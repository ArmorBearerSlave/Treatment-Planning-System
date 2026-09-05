import Foundation

public struct PhantomRecipe: Codable, Sendable {
    public var anatomyID: String
    public var seed: Int
    public var bodyScale: Double
    public var targetRadiusMM: Double
    public var motionPhase: Double
    public var nBioProfile: String
    public init(anatomyID: String = "ANATOMY-001", seed: Int = 42, bodyScale: Double = 1,
                targetRadiusMM: Double = 18, motionPhase: Double = 0, nBioProfile: String = "unbound") {
        self.anatomyID = anatomyID; self.seed = seed; self.bodyScale = bodyScale
        self.targetRadiusMM = targetRadiusMM; self.motionPhase = motionPhase; self.nBioProfile = nBioProfile
    }
    public func validate() throws {
        guard !anatomyID.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
              anatomyID.count <= 100, (0...1_000_000).contains(seed),
              bodyScale.isFinite, (0.7...1.3).contains(bodyScale),
              targetRadiusMM.isFinite, (8...30).contains(targetRadiusMM),
              motionPhase.isFinite, (0...1).contains(motionPhase), !nBioProfile.isEmpty else {
            throw TPSError.invalid("Phantom recipe is outside supported bounds.")
        }
    }
    /// All variants of one anatomy remain in one split. This is a suggested research split, not approval.
    public var suggestedSplit: String {
        let hash = (try? Canonical.hash(anatomyID)) ?? "00"
        let bucket = Int(hash.prefix(4), radix: 16)! % 10
        return bucket < 8 ? "train" : bucket == 8 ? "validation" : "test"
    }
}

public struct PhantomCase: Codable, Sendable, Identifiable {
    public var schemaVersion: Int
    public var id: UUID
    public var name: String
    public var generator: String
    public var generatorVersion: String
    public var syntheticOnly: Bool
    public var recipe: PhantomRecipe
    public var ct: Volume
    public var mr: Volume?
    public var truth: Volume
    public var structures: [Structure]
    public var simulation: SimulationEvidence? = nil
    public var sourceNotes: [String: String]? = nil
    public var mrIsPlaceholder: Bool? = nil
    public func validateInput(for operation: TPSOperation) throws {
        try validate()
        let note = sourceNotes?["mr"]?.lowercased() ?? ""
        if operation == .syntheticCT && (mr == nil || mrIsPlaceholder == true || note.contains("placeholder") || mr?.values.allSatisfy({ $0 == 0 }) == true) {
            throw TPSError.invalid("Synthetic CT requires meaningful MR input. This case has no usable MR channel.")
        }
    }
    public func validate() throws {
        guard schemaVersion == 1, syntheticOnly, !generator.isEmpty, !generatorVersion.isEmpty else {
            throw TPSError.invalid("Only version 1 synthetic research cases with generator provenance are supported.")
        }
        try recipe.validate(); try ct.validate(); try truth.validate()
        guard ct.modality == .ct, truth.modality == .labels,
              ct.grid == truth.grid else { throw TPSError.invalid("Case modalities or grids disagree.") }
        if let mr {
            try mr.validate()
            guard mr.modality == .mr, ct.grid == mr.grid else { throw TPSError.invalid("MR modality or grid disagrees with CT.") }
        }
        guard Set(structures.map(\.id)).count == structures.count, !structures.isEmpty,
              structures.allSatisfy({ $0.id > 0 && !$0.name.isEmpty && $0.color.count == 3 && $0.color.allSatisfy { $0.isFinite && (0...1).contains($0) } }) else {
            throw TPSError.invalid("Invalid structure dictionary.")
        }
        let ids = Set(structures.map(\.id)).union([0])
        guard truth.values.allSatisfy({ ids.contains(Int($0)) }) else { throw TPSError.invalid("Unknown truth label.") }
        if let simulation { try simulation.validate(grid: ct.grid) }
    }
}

/// Separate physical transport truth and biological scorer measurements from AI predictions.
public struct SimulationEvidence: Codable, Sendable {
    public var transportEngine: String
    public var transportVersion: String
    public var nBioVersion: String
    public var parameterFileSHA256: String
    public var histories: Int
    public var normalization: String
    public var referenceDose: Volume
    public var observations: [BiologyObservation]
    public func validate(grid: Grid) throws {
        guard !transportEngine.isEmpty, !transportVersion.isEmpty, !nBioVersion.isEmpty,
              parameterFileSHA256.count == 64, parameterFileSHA256.allSatisfy(\.isHexDigit),
              histories > 0, !normalization.isEmpty,
              referenceDose.modality == .dose, referenceDose.grid == grid else {
            throw TPSError.invalid("Simulation evidence needs engine versions, parameter hash, histories, normalization and aligned dose.")
        }
        try referenceDose.validate()
        for observation in observations {
            guard !observation.scorer.isEmpty, !observation.region.isEmpty, !observation.units.isEmpty,
                  observation.value.isFinite, observation.standardError.isFinite, observation.standardError >= 0 else {
                throw TPSError.invalid("Biological observations require scorer, region, units and finite uncertainty.")
            }
        }
    }
}
public struct BiologyObservation: Codable, Sendable {
    public var scorer: String
    public var region: String
    public var value: Double
    public var units: String
    public var standardError: Double
}

public enum PhantomFactory {
    /// Analytic pelvis fixture; deliberately neither XCAT2 nor nBio output.
    public static func analytic(_ recipe: PhantomRecipe, size: Int = 64) throws -> PhantomCase {
        try recipe.validate()
        guard (16...128).contains(size) else { throw TPSError.invalid("Fixture size must be 16–128.") }
        let id = UUID()
        let step = 320.0 / Double(size)
        let grid = Grid(dimensions: [size,size,size], spacing: [step,step,step], origin: [-160,-160,-160], frameID: id.uuidString)
        var ct = [Float](repeating: -1000, count: grid.count)
        var mr = [Float](repeating: 0, count: grid.count)
        var labels = [Float](repeating: 0, count: grid.count)
        let phase = sin(recipe.motionPhase * 2 * .pi) * 7
        let variation = Double(recipe.seed % 17) - 8
        for z in 0..<size { for y in 0..<size { for x in 0..<size {
            let p = grid.position(x,y,z), px = p[0], py = p[1], pz = p[2]
            let i = grid.index(x,y,z)
            let body = pow(px/(125*recipe.bodyScale),2)+pow(py/(100*recipe.bodyScale),2)
            guard body < 1 && abs(pz) < 145 else { continue }
            var label: Float = 1
            var hu: Float = body > 0.8 ? -90 : 35
            var signal: Float = body > 0.8 ? 90 : 125
            if pow((abs(px)-76)/20,2)+pow((py-8)/24,2)+pow((pz+20)/90,2) < 1 { label = px < 0 ? 5 : 6; hu = 850; signal = 10 }
            if pow(px/29,2)+pow((py+26-phase)/32,2)+pow((pz-22)/38,2) < 1 { label = 3; hu = 10; signal = 220 }
            if pow(px/17,2)+pow((py-40)/18,2) < 1 && abs(pz) < 85 { label = 4; hu = 25; signal = 155 }
            if pow((px-variation)/recipe.targetRadiusMM,2)+pow((py-phase)/recipe.targetRadiusMM,2)+pow(pz/(recipe.targetRadiusMM*1.3),2) < 1 { label = 2; hu = 65; signal = 180 }
            let texture = Float(sin(Double(x*13+y*7+z*3+recipe.seed))*3)
            ct[i] = hu+texture; mr[i] = signal+texture; labels[i] = label
        } } }
        let result = PhantomCase(schemaVersion: 1, id: id, name: recipe.anatomyID,
            generator: "Analytic pelvis fixture (not XCAT2/nBio)", generatorVersion: "1.0", syntheticOnly: true, recipe: recipe,
            ct: Volume(grid: grid, modality: .ct, units: "HU", values: ct),
            mr: Volume(grid: grid, modality: .mr, units: "a.u.", values: mr),
            truth: Volume(grid: grid, modality: .labels, units: "label", values: labels),
            structures: [Structure(id: 1, name: "Soft tissue", color: [0.4,0.65,0.65]),
                         Structure(id: 2, name: "Target proxy", color: [1,0.4,0.43]),
                         Structure(id: 3, name: "Bladder proxy", color: [0.95,0.72,0.3]),
                         Structure(id: 4, name: "Rectum proxy", color: [0.5,0.55,1]),
                         Structure(id: 5, name: "Right bone proxy", color: [0.3,0.8,0.7]),
                         Structure(id: 6, name: "Left bone proxy", color: [0.4,0.7,0.95])])
        try result.validate()
        return result
    }
}
