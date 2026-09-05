import Foundation

public struct LearningCase: Codable, Sendable, Identifiable {
    public var id: UUID
    public var name: String
    public var path: String
    public var fileSHA256: String
    public var anatomyGroup: String
    public var reference: String
    public var structureIDs: [Int]
    public init(source: PhantomCase, url: URL, fileSHA256: String, anatomyGroup: String = "") {
        id = source.id; name = source.name; path = url.path; self.fileSHA256 = fileSHA256
        self.anatomyGroup = anatomyGroup; reference = source.generator
        structureIDs = source.structures.map(\.id).sorted()
    }
}

public struct DatasetPartition: Codable, Sendable {
    public var seed: Int
    public var trainPercent: Int
    public var validationPercent: Int
    public var assignments: [String: String]
    public var groups: [String: String]
    public static func make(cases: [LearningCase], seed: Int, train: Int = 70, validation: Int = 15) throws -> DatasetPartition {
        guard !cases.isEmpty, Set(cases.map(\.id)).count == cases.count,
              cases.allSatisfy({ !$0.anatomyGroup.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }),
              train >= 10, validation >= 10, train + validation <= 90 else {
            throw TPSError.invalid("Assign the original anatomy group to every case; choose nonzero train, validation and test fractions.")
        }
        let unique = Set(cases.map { $0.anatomyGroup.trimmingCharacters(in: .whitespacesAndNewlines) })
        guard unique.count >= 3 else { throw TPSError.invalid("At least three independent anatomy groups are required for a three-way split.") }
        // Sort before keyed hashing: selection order must not change the partition.
        let ordered = try unique.sorted().map { ($0, try Canonical.hash("\(seed):\($0)")) }.sorted { $0.1 < $1.1 }.map(\.0)
        let nTrain = min(max(1, Int((Double(ordered.count) * Double(train)/100).rounded())), ordered.count-2)
        let nVal = min(max(1, Int((Double(ordered.count) * Double(validation)/100).rounded())), ordered.count-nTrain-1)
        var groups: [String:String] = [:]
        for (i, group) in ordered.enumerated() { groups[group] = i < nTrain ? "train" : i < nTrain+nVal ? "validation" : "test" }
        return DatasetPartition(seed: seed, trainPercent: train, validationPercent: validation,
                                assignments: Dictionary(uniqueKeysWithValues: cases.map { ($0.id.uuidString, groups[$0.anatomyGroup.trimmingCharacters(in: .whitespacesAndNewlines)]!) }), groups: groups)
    }
}

/// Interpretable learned baseline. CT intensity + normalized voxel position;
/// it is not a neural network and is not a substitute for an anatomical contour model.
public struct GaussianContourModel: Codable, Sendable {
    public var labelIDs: [Int]
    public var means: [[Double]]
    public var variances: [[Double]]
    public var structures: [Structure]
    public var trainingSourceHashes: [String]
    public var featureContract = "CT clipped [-1000,2000]/1000; normalized voxel XYZ [-1,1]; diagonal Gaussian, equal class priors"
    static func features(_ source: PhantomCase, _ i: Int) -> [Double] {
        let d = source.ct.grid.dimensions
        return [Double(min(max(source.ct.values[i], -1000),2000))/1000,
                Double(i % d[0])/Double(d[0]-1)*2-1,
                Double((i/d[0]) % d[1])/Double(d[1]-1)*2-1,
                Double(i/(d[0]*d[1]))/Double(d[2]-1)*2-1]
    }
    public static func fit(_ sources: [PhantomCase], varianceFloor: Double) throws -> GaussianContourModel {
        guard let first = sources.first, varianceFloor.isFinite, varianceFloor > 0 else { throw TPSError.invalid("Training sources and positive variance floor required.") }
        let ids = [0] + first.structures.map(\.id).sorted()
        let names = Dictionary(uniqueKeysWithValues: first.structures.map { ($0.id,$0.name) })
        var counts = [Double](repeating: 0, count: ids.count)
        var sums = [[Double]](repeating: [Double](repeating: 0, count: 4), count: ids.count)
        var squares = sums
        var hashes: [String] = []
        for source in sources {
            try source.validate()
            guard Dictionary(uniqueKeysWithValues: source.structures.map { ($0.id,$0.name) }) == names else { throw TPSError.invalid("Training cases must use the same label dictionary.") }
            hashes.append(try Canonical.hash(source))
            let indices = Dictionary(uniqueKeysWithValues: ids.enumerated().map { ($0.element,$0.offset) })
            // Bounded, deterministic sampling for the first Mac CPU baseline.
            let step = max(1, source.ct.grid.count / 100_000)
            for i in stride(from: 0, to: source.ct.grid.count, by: step) {
                let k = indices[Int(source.truth.values[i])]!
                let values = features(source,i); counts[k] += 1
                for f in 0..<4 { sums[k][f] += values[f]; squares[k][f] += values[f]*values[f] }
            }
        }
        guard counts.allSatisfy({ $0 > 0 }) else { throw TPSError.invalid("A label is absent from sampled training data; review coverage or sampling before training.") }
        let means = sums.enumerated().map { k,row in row.map { $0/counts[k] } }
        let variances = squares.enumerated().map { k,row in row.enumerated().map { f,value in max(varianceFloor,value/counts[k]-means[k][f]*means[k][f]) } }
        return GaussianContourModel(labelIDs: ids, means: means, variances: variances, structures: first.structures, trainingSourceHashes: hashes)
    }
    public func predict(_ source: PhantomCase) throws -> Volume {
        try source.validate()
        guard labelIDs.count == means.count, means.count == variances.count, !labelIDs.isEmpty,
              means.allSatisfy({ $0.count == 4 && $0.allSatisfy(\.isFinite) }),
              variances.allSatisfy({ $0.count == 4 && $0.allSatisfy { $0.isFinite && $0 > 0 } }) else { throw TPSError.invalid("Invalid trained baseline parameters.") }
        let constants = variances.map { $0.map(log).reduce(0,+) }
        let inverse = variances.map { $0.map { 1/$0 } }
        var values = [Float](repeating: 0, count: source.ct.grid.count)
        for i in values.indices {
            let x = Self.features(source,i)
            var best = Double.infinity, chosen = 0
            for k in labelIDs.indices {
                var score = constants[k]
                for f in 0..<4 { let diff = x[f]-means[k][f]; score += diff*diff*inverse[k][f] }
                if score < best { best = score; chosen = labelIDs[k] }
            }
            values[i] = Float(chosen)
        }
        return Volume(grid: source.ct.grid, modality: .labels, units: "label", values: values)
    }
}

public struct LabelMetric: Codable, Sendable, Identifiable {
    public var id: Int
    public var name: String
    public var dice: Double?
    public var referenceCC: Double
    public var predictedCC: Double
    public var centroidErrorMM: Double?
}
public struct CaseEvaluation: Codable, Sendable, Identifiable {
    public var id: UUID
    public var name: String
    public var split: String
    public var metrics: [LabelMetric]
    public var meanDice: Double? {
        let values = metrics.compactMap(\.dice)
        return values.isEmpty ? nil : values.reduce(0,+)/Double(values.count)
    }
    public static func contours(source: PhantomCase, prediction: Volume, split: String) throws -> CaseEvaluation {
        try source.validate(); try prediction.validate()
        guard prediction.grid == source.truth.grid, prediction.modality == .labels else { throw TPSError.invalid("Evaluation requires labels on the exact reference grid.") }
        let ids = Set(source.structures.map(\.id)).union([0])
        guard prediction.values.allSatisfy({ ids.contains(Int($0)) }) else { throw TPSError.invalid("Prediction contains an unknown label.") }
        let cc = source.ct.grid.spacing.reduce(1,*) / 1000
        var truth: [Int:Int] = [:], predicted: [Int:Int] = [:], intersection: [Int:Int] = [:]
        var tSum: [Int:[Double]] = [:], pSum: [Int:[Double]] = [:]
        let d = source.ct.grid.dimensions
        for i in prediction.values.indices {
            let t = Int(source.truth.values[i]), p = Int(prediction.values[i])
            if t == 0 && p == 0 { continue }
            let xyz = source.ct.grid.position(i % d[0], (i/d[0]) % d[1], i/(d[0]*d[1]))
            if t != 0 { truth[t,default:0] += 1; var sum = tSum[t] ?? [0,0,0]; for k in 0..<3 { sum[k] += xyz[k] }; tSum[t] = sum }
            if p != 0 { predicted[p,default:0] += 1; var sum = pSum[p] ?? [0,0,0]; for k in 0..<3 { sum[k] += xyz[k] }; pSum[p] = sum }
            if t == p { intersection[t,default:0] += 1 }
        }
        var metrics: [LabelMetric] = []
        for structure in source.structures {
            let t = truth[structure.id,default:0], p = predicted[structure.id,default:0]
            var centroid: Double? = nil
            if t > 0 && p > 0 {
                var squared = 0.0
                for k in 0..<3 {
                    let diff = tSum[structure.id]![k]/Double(t) - pSum[structure.id]![k]/Double(p)
                    squared += diff*diff
                }
                centroid = sqrt(squared)
            }
            let dice: Double? = t+p == 0 ? nil : 2*Double(intersection[structure.id,default:0])/Double(t+p)
            metrics.append(LabelMetric(id: structure.id, name: structure.name, dice: dice, referenceCC: Double(t)*cc, predictedCC: Double(p)*cc, centroidErrorMM: centroid))
        }
        return CaseEvaluation(id: source.id, name: source.name, split: split, metrics: metrics)
    }
}

public struct LearningExperiment: Codable, Sendable {
    public var schemaVersion = 1
    public var id = UUID()
    public var createdAt = Date()
    public var cases: [LearningCase]
    public var partition: DatasetPartition
    public var model: GaussianContourModel
    public var selectedVarianceFloor: Double
    public var validation: [CaseEvaluation]
    public var test: [CaseEvaluation]? = nil
    public var clinicalUsePermitted = false
    public var method = "Gaussian CT+position contour baseline; validation-selected variance floor; background excluded; both-empty Dice omitted"
    public init(cases: [LearningCase], partition: DatasetPartition, model: GaussianContourModel, selectedVarianceFloor: Double, validation: [CaseEvaluation]) {
        self.cases = cases; self.partition = partition; self.model = model
        self.selectedVarianceFloor = selectedVarianceFloor; self.validation = validation
    }
}

public struct LearningReport: Codable, Sendable {
    public var schemaVersion = 1
    public var experimentID: UUID
    public var experimentHash: String
    public var method: String
    public var clinicalUsePermitted = false
    public var groupCounts: [String:Int]
    public var validation: [CaseEvaluation]
    public var test: [CaseEvaluation]?
    public init(experiment: LearningExperiment) throws {
        experimentID = experiment.id; experimentHash = try Canonical.hash(experiment); method = experiment.method
        groupCounts = experiment.partition.groups.values.reduce(into: [:]) { $0[$1,default:0] += 1 }
        validation = experiment.validation; test = experiment.test
    }
}
