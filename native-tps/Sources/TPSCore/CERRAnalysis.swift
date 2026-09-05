import Foundation

public struct CERRRequest: Codable, Sendable {
    public var schemaVersion = 1
    public var id = UUID()
    public var sourceHash: String
    public var doseHash: String
    public var doseDescription: String
    public var binWidthGy: Double
    public init(source: PhantomCase, dose: Volume, doseDescription: String, binWidthGy: Double = 0.1) throws {
        sourceHash = try Canonical.hash(source); doseHash = try Canonical.hash(dose)
        self.doseDescription = doseDescription; self.binWidthGy = binWidthGy
        try validate(source: source, dose: dose)
    }
    public func validate(source: PhantomCase, dose: Volume) throws {
        try source.validate(); try dose.validate()
        guard schemaVersion == 1, source.syntheticOnly, source.ct.grid.direction == [1,0,0,0,1,0,0,0,1],
              source.ct.grid.dimensions.allSatisfy({ $0 >= 2 }), source.ct.grid.count <= 4_000_000,
              dose.grid == source.ct.grid, dose.modality == .dose, dose.units == "Gy",
              binWidthGy.isFinite, binWidthGy > 0, Double(dose.values.max() ?? 0)/binWidthGy <= 5000,
              !doseDescription.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
              sourceHash == (try Canonical.hash(source)), doseHash == (try Canonical.hash(dose)) else {
            throw TPSError.invalid("CERR needs a bound synthetic CT, aligned Gy dose, axis-aligned grid (2+ voxels per axis, at most four million voxels), and at most 5000 histogram bins.")
        }
    }
}

public struct CERRRecord: Codable, Sendable, Identifiable {
    public var id: Int
    public var name: String
    public var sampleCount: Int
    public var volumeCC: Double
    public var meanGy: Double
    public var d95Gy: Double
    public var maxSampleDifferenceGy: Double
    public var binCentersGy: [Double]
    public var differentialVolumeCC: [Double]
}
public struct CERRComparison: Sendable, Identifiable {
    public var id: Int { cerr.id }
    public var cerr: CERRRecord
    public var nativeMeanGy: Double
    public var nativeD95Gy: Double
    public var nativeVolumeCC: Double
}
public struct CERRReport: Codable, Sendable {
    public var schemaVersion: Int
    public var requestID: UUID
    public var requestHash: String
    public var sourceHash: String
    public var doseHash: String
    public var clinicalReleaseAllowed: Bool
    public var records: [CERRRecord]
    public var evidence: [String: String]
    public func compare(source: PhantomCase, dose: Volume, request: CERRRequest) throws -> [CERRComparison] {
        try request.validate(source: source, dose: dose)
        guard schemaVersion == 1, requestID == request.id, requestHash == (try Canonical.hash(request)),
              sourceHash == request.sourceHash, doseHash == request.doseHash, !clinicalReleaseAllowed,
              ["getDVHSHA256", "doseHistSHA256", "bridgeSHA256"].allSatisfy({ key in
                  guard let value = evidence[key] else { return false }
                  return value.count == 64 && value.allSatisfy({ "0123456789abcdef".contains($0) })
              }) else { throw TPSError.invalid("CERR report provenance does not match this frozen analysis.") }
        var values: [Int: [Double]] = [:]
        for i in dose.values.indices { values[Int(source.truth.values[i]), default: []].append(Double(dose.values[i])) }
        let structures = source.structures.filter { !(values[$0.id] ?? []).isEmpty }
        guard Set(records.map(\.id)) == Set(structures.map(\.id)), records.count == structures.count else {
            throw TPSError.invalid("CERR report has missing or duplicate structures.")
        }
        let voxelCC = source.ct.grid.spacing.reduce(1, *) / 1000
        return try structures.map { structure in
            let samples = values[structure.id]!.sorted(), record = records.first { $0.id == structure.id }!
            let cc = Double(samples.count) * voxelCC
            let tolerance = max(1e-7, cc * 1e-6)
            guard record.name == structure.name, record.sampleCount == samples.count,
                  [record.volumeCC, record.meanGy, record.d95Gy, record.maxSampleDifferenceGy].allSatisfy({ $0.isFinite && $0 >= 0 }),
                  abs(record.volumeCC - cc) <= tolerance,
                  !record.binCentersGy.isEmpty, record.binCentersGy.count <= 5001,
                  record.binCentersGy.count == record.differentialVolumeCC.count,
                  record.differentialVolumeCC.allSatisfy({ $0.isFinite && $0 >= 0 }),
                  record.binCentersGy.enumerated().allSatisfy({ i, bin in bin.isFinite && abs(bin - (Double(i)+0.5)*request.binWidthGy) < 1e-7 }),
                  abs(record.differentialVolumeCC.reduce(0,+) - cc) <= tolerance else {
                throw TPSError.invalid("CERR returned invalid samples, histogram or volume for \(structure.name).")
            }
            return CERRComparison(cerr: record, nativeMeanGy: samples.reduce(0,+)/Double(samples.count),
                                  nativeD95Gy: samples[max(0, Int(ceil(0.05*Double(samples.count)))-1)], nativeVolumeCC: cc)
        }
    }
}
