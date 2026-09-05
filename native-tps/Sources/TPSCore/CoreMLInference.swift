import Foundation
import CoreML
import CryptoKit

/// Deliberately narrow versioned tensor contract; adapters must export models to this contract.
public struct LocalModelManifest: Codable, Sendable {
    public var schemaVersion: Int
    public var modelID: String
    public var version: String
    public var operation: TPSOperation
    public var modelFile: String
    public var modelSHA256: String
    public var dimensions: [Int]
    public var inputOffset: Float
    public var inputScale: Float
    public var inputClip: [Float]
    public var outputScale: Float
    public var outputOffset: Float
    public var structures: [Structure]
    public var intendedUse: String
    public var isFixture: Bool? = nil
    public func validate() throws {
        guard schemaVersion == 1, operation != .inspect, !modelID.isEmpty, !version.isEmpty,
              intendedUse == "synthetic-research-only", modelFile.hasSuffix(".mlmodel"),
              !modelFile.contains("/"), !modelFile.contains("\\"), !modelFile.hasPrefix("."),
              modelSHA256.count == 64, modelSHA256.allSatisfy(\.isHexDigit),
              dimensions.count == 3, dimensions.allSatisfy({ (2...256).contains($0) }),
              dimensions.reduce(1, *) <= 8_388_608,
              inputOffset.isFinite, inputScale.isFinite, inputScale > 0,
              inputClip.count == 2, inputClip.allSatisfy(\.isFinite), inputClip[0] < inputClip[1],
              outputScale.isFinite, outputScale > 0, outputOffset.isFinite else { throw TPSError.invalid("Invalid local model manifest.") }
    }
}

public enum CoreMLInference {
    public static func manifest(at url: URL) throws -> LocalModelManifest {
        let data = try Data(contentsOf: url)
        guard data.count <= 1_000_000 else { throw TPSError.invalid("Model manifest is too large.") }
        let manifest = try JSONDecoder().decode(LocalModelManifest.self, from: data)
        try manifest.validate(); return manifest
    }
    public static func run(manifestURL: URL, operation: TPSOperation, source: PhantomCase) async throws -> Artifact {
        try source.validateInput(for: operation)
        let manifest = try self.manifest(at: manifestURL)
        guard manifest.operation == operation, manifest.dimensions == source.ct.grid.dimensions else {
            throw TPSError.invalid("Model operation or fixed input dimensions do not match this case. Resampling is not implicit.")
        }
        let directory = manifestURL.deletingLastPathComponent().resolvingSymlinksInPath()
        let modelURL = directory.appendingPathComponent(manifest.modelFile).resolvingSymlinksInPath()
        guard modelURL.deletingLastPathComponent() == directory else { throw TPSError.invalid("Model must be inside its manifest directory.") }
        // Compile the exact bytes that were hashed, even if the source file changes during a run.
        let staging = FileManager.default.temporaryDirectory.appendingPathComponent("tps-model-"+UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: staging, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: staging) }
        let snapshot = staging.appendingPathComponent("verified.mlmodel")
        guard FileManager.default.createFile(atPath: snapshot.path, contents: nil) else { throw TPSError.invalid("Could not snapshot the local model.") }
        let outputHandle = try FileHandle(forWritingTo: snapshot)
        defer { try? outputHandle.close() }
        let handle = try FileHandle(forReadingFrom: modelURL)
        defer { try? handle.close() }
        var hasher = SHA256()
        while let chunk = try handle.read(upToCount: 1_048_576), !chunk.isEmpty {
            hasher.update(data: chunk); try outputHandle.write(contentsOf: chunk)
        }
        try outputHandle.synchronize()
        let digest = hasher.finalize().map { String(format: "%02x", $0) }.joined()
        guard digest == manifest.modelSHA256.lowercased() else { throw TPSError.invalid("Local model checksum mismatch.") }
        let compiled = try await MLModel.compileModel(at: snapshot)
        defer { try? FileManager.default.removeItem(at: compiled) }
        let configuration = MLModelConfiguration()
        configuration.computeUnits = .all
        let model = try MLModel(contentsOf: compiled, configuration: configuration)
        let d = source.ct.grid.dimensions
        let shape = [1,1,d[2],d[1],d[0]].map { NSNumber(value: $0) }
        let input = try MLMultiArray(shape: shape, dataType: .float32)
        let sourceVolume = operation == .syntheticCT ? source.mr : source.ct
        for i in sourceVolume.values.indices {
            input[i] = NSNumber(value: (min(max(sourceVolume.values[i], manifest.inputClip[0]), manifest.inputClip[1]) + manifest.inputOffset) * manifest.inputScale)
        }
        var features: [String: MLFeatureValue] = ["image": MLFeatureValue(multiArray: input)]
        if operation == .predictDose {
            let labels = try MLMultiArray(shape: shape, dataType: .float32)
            for i in source.truth.values.indices { labels[i] = NSNumber(value: source.truth.values[i]) }
            features["structures"] = MLFeatureValue(multiArray: labels)
        }
        guard Set(model.modelDescription.inputDescriptionsByName.keys) == Set(features.keys),
              model.modelDescription.outputDescriptionsByName["output"] != nil else {
            throw TPSError.invalid("Core ML model must use the documented image/structures → output tensor contract.")
        }
        let result = try await model.prediction(from: MLDictionaryFeatureProvider(dictionary: features))
        guard let output = result.featureValue(for: "output")?.multiArrayValue,
              output.shape == shape else { throw TPSError.invalid("Model output must have shape [1,1,Z,Y,X] on the unchanged source grid.") }
        let values = (0..<output.count).map { output[$0].floatValue * manifest.outputScale + manifest.outputOffset }
        let artifact = Artifact(caseID: source.id, inputHash: try Canonical.hash(source), operation: operation,
            modelID: manifest.modelID, modelVersion: manifest.version+"@"+digest,
            isDemo: manifest.isFixture ?? false, volume: Volume(grid: source.ct.grid, modality: operation.modality,
                units: operation == .contour ? "label" : operation == .predictDose ? "Gy" : "HU", values: values), structures: manifest.structures)
        try artifact.validate(for: source); return artifact
    }
}
