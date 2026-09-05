import Foundation

public struct MatRadObjective: Codable, Sendable, Identifiable {
    public var id: Int
    public var ceilingGy: Double
    public var penalty: Double
    public init(id: Int, ceilingGy: Double = 0, penalty: Double = 1) {
        self.id = id; self.ceilingGy = ceilingGy; self.penalty = penalty
    }
}

public struct MatRadSettings: Codable, Sendable {
    public var targetID: Int
    public var targetGy: Double = 2
    public var fractions: Int = 1
    public var targetPenalty: Double = 100
    public var gantryAngles: [Double] = [0, 90, 180, 270]
    public var bixelWidthMM: Double = 10
    public var organs: [MatRadObjective] = []
    public init(targetID: Int) { self.targetID = targetID }
    public func validate(for source: PhantomCase) throws {
        try source.validate()
        guard source.syntheticOnly, source.ct.grid.direction == [1,0,0,0,1,0,0,0,1] else {
            throw TPSError.invalid("matRad currently requires synthetic CT on an axis-aligned LPS grid. Oblique grids must be explicitly converted first.")
        }
        guard source.ct.grid.count <= 4_000_000, source.structures.contains(where: { $0.id == targetID }),
              source.truth.values.contains(Float(targetID)), targetGy.isFinite, (0.01...100).contains(targetGy),
              (1...50).contains(fractions), targetPenalty.isFinite, (0.01...10000).contains(targetPenalty),
              !gantryAngles.isEmpty, gantryAngles.count <= 9, gantryAngles.allSatisfy({ $0.isFinite && (0..<360).contains($0) }),
              Set(gantryAngles).count == gantryAngles.count,
              bixelWidthMM.isFinite, (5...30).contains(bixelWidthMM) else {
            throw TPSError.invalid("Check target, dose, fractions, angles and bixel width. Limit: four million CT voxels and nine beams.")
        }
        let allowed = Set(source.structures.map(\.id)).subtracting([targetID])
        guard Set(organs.map(\.id)).count == organs.count,
              organs.allSatisfy({ allowed.contains($0.id) && $0.ceilingGy.isFinite && (0...100).contains($0.ceilingGy) && $0.penalty.isFinite && (0...10000).contains($0.penalty) }) else {
            throw TPSError.invalid("Invalid organ objective or duplicate structure ID.")
        }
    }
}

public struct MatRadRequest: Codable, Sendable {
    public var schemaVersion = 1
    public var id = UUID()
    public var sourceHash: String
    public var settings: MatRadSettings
    public init(source: PhantomCase, settings: MatRadSettings) throws {
        try settings.validate(for: source)
        self.sourceHash = try Canonical.hash(source); self.settings = settings
    }
}

public struct MatRadResult: Codable, Sendable {
    public var schemaVersion: Int
    public var requestID: UUID
    public var requestHash: String
    public var sourceHash: String
    public var clinicalReleaseAllowed: Bool
    public var doseBasis: String
    public var volume: Volume
    public var evidence: [String: String]
    public func artifact(source: PhantomCase, request: MatRadRequest) throws -> Artifact {
        try request.settings.validate(for: source)
        guard schemaVersion == 1, request.schemaVersion == 1, requestID == request.id, requestHash == (try Canonical.hash(request)),
              sourceHash == request.sourceHash, sourceHash == (try Canonical.hash(source)),
              !clinicalReleaseAllowed, evidence["optimizerConverged"] == "true", doseBasis == "physical-course-Gy", volume.grid == source.ct.grid,
              volume.modality == .dose, let version = evidence["matRadVersion"], !version.isEmpty else {
            throw TPSError.invalid("matRad result does not match the frozen request, source CT, or dose convention.")
        }
        try volume.validate()
        guard volume.values.contains(where: { $0 > 0 }) else { throw TPSError.invalid("matRad returned an all-zero dose.") }
        var artifact = Artifact(caseID: source.id, inputHash: sourceHash, operation: .predictDose,
                        modelID: "matRad/Generic-photons/\(requestID)", modelVersion: try Canonical.hash(self),
                        isDemo: false, volume: volume)
        artifact.planningEvidence = evidence
        artifact.planningEvidence?["doseBasis"] = doseBasis
        artifact.planningEvidence?["requestJSON"] = String(decoding: try Canonical.data(request), as: UTF8.self)
        artifact.planningEvidence?["requestHash"] = requestHash
        return artifact
    }
}
