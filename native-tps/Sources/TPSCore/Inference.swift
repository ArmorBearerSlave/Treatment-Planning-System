import Foundation

public enum AnalyticInference {
    public static func run(_ operation: TPSOperation, source: PhantomCase) throws -> Artifact {
        try source.validateInput(for: operation)
        guard operation != .inspect else { throw TPSError.invalid("Inspection does not produce an inference artifact.") }
        var values = [Float](repeating: 0, count: source.ct.grid.count)
        switch operation {
        case .contour:
            // Intensity-based body/bone fixture; never copies phantom truth as predicted contours.
            values = source.ct.values.map { $0 < -300 ? 0 : $0 > 400 ? 2 : 1 }
        case .syntheticCT:
            // Deliberately crude MR signal mapping, for integration tests only.
            guard let mr = source.mr else { throw TPSError.invalid("Synthetic CT requires MR input.") }
            values = mr.values.map { signal in signal < 2 ? -1000 : signal < 25 ? 700 : signal < 105 ? -80 : 40 }
        case .predictDose:
            let grid = source.ct.grid
            for z in 0..<grid.dimensions[2] { for y in 0..<grid.dimensions[1] { for x in 0..<grid.dimensions[0] {
                let i = grid.index(x,y,z), p = grid.position(x,y,z)
                if source.ct.values[i] > -300 {
                    // Unit-labelled analytic field, no beam transport, machine model or prescription.
                    values[i] = Float(50 * exp(-(p[0]*p[0]/1800+p[1]*p[1]/1400+p[2]*p[2]/2300)))
                }
            } } }
        case .inspect: break
        }
        let structures = operation == .contour ? [Structure(id: 1, name: "Body intensity proxy", color: [0.3,0.8,0.7]), Structure(id: 2, name: "Bone intensity proxy", color: [0.9,0.7,0.3])] : []
        let result = Artifact(caseID: source.id, inputHash: try Canonical.hash(source), operation: operation,
            modelID: "analytic-fixture/\(operation.rawValue)", modelVersion: "1.0", isDemo: true,
            volume: Volume(grid: source.ct.grid, modality: operation.modality,
                           units: operation == .predictDose ? "Gy" : operation == .contour ? "label" : "HU", values: values), structures: structures)
        try result.validate(for: source)
        return result
    }
}

public struct InferenceRequest: Codable, Sendable {
    public var schemaVersion = 1
    public var requestID: UUID
    public var operation: TPSOperation
    public var modelID: String
    public var modelVersion: String
    public var source: PhantomCase
    public var inputHash: String
    public init(operation: TPSOperation, modelID: String, modelVersion: String, source: PhantomCase) throws {
        self.requestID = UUID(); self.operation = operation; self.modelID = modelID; self.modelVersion = modelVersion
        self.source = source; self.inputHash = try Canonical.hash(source)
    }
}
public struct InferenceResponse: Codable, Sendable {
    public var schemaVersion: Int
    public var requestID: UUID
    public var artifact: Artifact
    public init(schemaVersion: Int = 1, requestID: UUID, artifact: Artifact) { self.schemaVersion = schemaVersion; self.requestID = requestID; self.artifact = artifact }
    public func validate(for request: InferenceRequest) throws {
        guard schemaVersion == 1, requestID == request.requestID,
              artifact.operation == request.operation, artifact.modelID == request.modelID,
              artifact.modelVersion == request.modelVersion else { throw TPSError.invalid("Inference response identity or model version mismatch.") }
        try artifact.validate(for: request.source)
    }
}

/// Endpoint strings are explicitly configured by the operator. Cloud names and redirects are rejected.
public enum LocalEndpoint {
    public static func validate(_ text: String) throws -> URL {
        guard let url = URL(string: text), ["http", "https"].contains(url.scheme),
              let host = url.host?.lowercased(), url.user == nil, url.password == nil,
              url.query == nil, url.fragment == nil else { throw TPSError.invalid("Enter a local HTTP(S) endpoint without credentials or query parameters.") }
        let parts = host.split(separator: ".", omittingEmptySubsequences: false)
        let octets = parts.compactMap { Int($0) }
        let ipv4 = parts.count == 4 && octets.count == 4 && parts.allSatisfy { !$0.isEmpty && $0.allSatisfy(\.isNumber) } && octets.allSatisfy { (0...255).contains($0) }
        let privateIP = ipv4 && (octets[0] == 10 || octets[0] == 127 || (octets[0] == 192 && octets[1] == 168) || (octets[0] == 172 && (16...31).contains(octets[1])))
        guard privateIP || host == "localhost" || host == "[::1]" || host == "::1" else {
            throw TPSError.invalid("Use localhost or a private LAN IPv4 address. Public and DNS-based endpoints are disabled.")
        }
        return url
    }
}

private final class NoRedirect: NSObject, URLSessionTaskDelegate, Sendable {
    func urlSession(_ session: URLSession, task: URLSessionTask, willPerformHTTPRedirection response: HTTPURLResponse,
                    newRequest request: URLRequest, completionHandler: @escaping @Sendable (URLRequest?) -> Void) { completionHandler(nil) }
}

public enum LocalHTTP {
    public static func request(_ request: URLRequest, maximumBytes: Int = 96_000_000) async throws -> Data {
        _ = try LocalEndpoint.validate(request.url?.absoluteString ?? "")
        let config = URLSessionConfiguration.ephemeral
        config.timeoutIntervalForRequest = 180; config.timeoutIntervalForResource = 240
        config.httpCookieStorage = nil; config.urlCache = nil
        let session = URLSession(configuration: config, delegate: NoRedirect(), delegateQueue: nil)
        defer { session.invalidateAndCancel() }
        let (bytes, response) = try await session.bytes(for: request)
        guard let http = response as? HTTPURLResponse else { throw TPSError.invalid("Service returned a non-HTTP response.") }
        guard response.expectedContentLength <= maximumBytes else { throw TPSError.invalid("Service response exceeds size limit.") }
        var data = Data()
        for try await byte in bytes {
            guard data.count < maximumBytes else { throw TPSError.invalid("Service response exceeds size limit.") }
            data.append(byte)
        }
        guard (200..<300).contains(http.statusCode) else {
            let object = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any]
            let detail = (object?["error"] as? String).map { String($0.prefix(400)) } ?? "Check the service and model configuration."
            throw TPSError.invalid("Local service returned HTTP \(http.statusCode): \(detail)")
        }
        return data
    }
}

public enum ModelGateway {
    public static func infer(endpoint: String, request: InferenceRequest) async throws -> Artifact {
        try request.source.validateInput(for: request.operation)
        var http = URLRequest(url: try LocalEndpoint.validate(endpoint).appendingPathComponent("v1/infer"))
        http.httpMethod = "POST"; http.setValue("application/json", forHTTPHeaderField: "Content-Type")
        http.httpBody = try Canonical.data(request)
        let response = try JSONDecoder().decode(InferenceResponse.self, from: await LocalHTTP.request(http))
        try response.validate(for: request); return response.artifact
    }
    public static func phantom(endpoint: String, recipe: PhantomRecipe) async throws -> PhantomCase {
        try recipe.validate()
        var http = URLRequest(url: try LocalEndpoint.validate(endpoint).appendingPathComponent("v1/phantoms"))
        http.httpMethod = "POST"; http.setValue("application/json", forHTTPHeaderField: "Content-Type")
        http.httpBody = try Canonical.data(recipe)
        let result = try JSONDecoder().decode(PhantomCase.self, from: await LocalHTTP.request(http))
        try result.validate()
        guard try Canonical.hash(result.recipe) == Canonical.hash(recipe) else { throw TPSError.invalid("Phantom response does not match the requested recipe.") }
        return result
    }
}
