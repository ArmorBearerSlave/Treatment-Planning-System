import Foundation
import CryptoKit

public enum TPSError: Error, LocalizedError, Equatable {
    case invalid(String)
    public var errorDescription: String? { if case .invalid(let text) = self { return text }; return nil }
}

public enum Canonical {
    public static func data<T: Encodable>(_ value: T) throws -> Data {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys, .withoutEscapingSlashes]
        return try encoder.encode(value)
    }
    public static func hash<T: Encodable>(_ value: T) throws -> String {
        SHA256.hash(data: try data(value)).map { String(format: "%02x", $0) }.joined()
    }
}

/// X is the fastest varying index. Direction is row-major, mapping voxel XYZ to LPS mm.
public struct Grid: Codable, Equatable, Sendable {
    public var dimensions: [Int]
    public var spacing: [Double]
    public var origin: [Double]
    public var direction: [Double]
    public var frameID: String
    public init(dimensions: [Int], spacing: [Double], origin: [Double],
                direction: [Double] = [1,0,0,0,1,0,0,0,1], frameID: String) {
        self.dimensions = dimensions; self.spacing = spacing; self.origin = origin
        self.direction = direction; self.frameID = frameID
    }
    public var count: Int { dimensions.reduce(1, *) }
    public func validate() throws {
        guard dimensions.count == 3, dimensions.allSatisfy({ (2...512).contains($0) }),
              dimensions.reduce(1, *) <= 8_388_608,
              spacing.count == 3, spacing.allSatisfy({ $0.isFinite && $0 > 0 && $0 <= 100 }),
              origin.count == 3, origin.allSatisfy(\.isFinite),
              direction.count == 9, direction.allSatisfy(\.isFinite), !frameID.isEmpty else {
            throw TPSError.invalid("Invalid grid: dimensions, spacing, origin, direction or frame identifier.")
        }
        for a in 0..<3 {
            for b in 0..<3 {
                var dot = 0.0
                for row in 0..<3 { dot += direction[row*3+a] * direction[row*3+b] }
                guard abs(dot - (a == b ? 1 : 0)) < 1e-5 else {
                    throw TPSError.invalid("Grid directions must form an orthonormal basis.")
                }
            }
        }
        let d = direction
        let determinant = d[0]*(d[4]*d[8]-d[5]*d[7]) - d[1]*(d[3]*d[8]-d[5]*d[6]) + d[2]*(d[3]*d[7]-d[4]*d[6])
        guard abs(determinant - 1) < 1e-5 else { throw TPSError.invalid("Grid basis must be right-handed.") }
    }
    public func index(_ x: Int, _ y: Int, _ z: Int) -> Int { (z*dimensions[1]+y)*dimensions[0]+x }
    public func position(_ x: Int, _ y: Int, _ z: Int) -> [Double] {
        let v = [Double(x)*spacing[0], Double(y)*spacing[1], Double(z)*spacing[2]]
        var result = origin
        for row in 0..<3 { for col in 0..<3 { result[row] += direction[row*3+col] * v[col] } }
        return result
    }
}

public enum Modality: String, Codable, Sendable { case ct, mr, dose, labels }
public struct Volume: Codable, Sendable {
    public var grid: Grid
    public var modality: Modality
    public var units: String
    public var values: [Float]
    public init(grid: Grid, modality: Modality, units: String, values: [Float]) {
        self.grid = grid; self.modality = modality; self.units = units; self.values = values
    }
    public func validate() throws {
        try grid.validate()
        guard values.count == grid.count, values.allSatisfy(\.isFinite) else {
            throw TPSError.invalid("Voxel count mismatch or non-finite voxel value.")
        }
        let expected: [Modality: String] = [.ct: "HU", .mr: "a.u.", .dose: "Gy", .labels: "label"]
        guard units == expected[modality] else { throw TPSError.invalid("Units do not match modality.") }
        if modality == .dose && values.contains(where: { $0 < 0 }) { throw TPSError.invalid("Negative dose is invalid.") }
        if modality == .labels && values.contains(where: { $0 < 0 || $0 > 65535 || $0.rounded() != $0 }) {
            throw TPSError.invalid("Label maps require non-negative integer labels.")
        }
    }
}

public struct Structure: Codable, Sendable, Identifiable {
    public var id: Int
    public var name: String
    public var color: [Double]
    public init(id: Int, name: String, color: [Double]) { self.id = id; self.name = name; self.color = color }
}

public struct DVHPoint: Codable, Sendable { public var dose: Double; public var volumePercent: Double }
public struct DVH: Codable, Sendable, Identifiable {
    public var id: Int
    public var name: String
    public var color: [Double]
    public var volumeCC: Double
    public var meanGy: Double
    public var d95Gy: Double
    public var points: [DVHPoint]
    public static func calculate(dose: Volume, labels: Volume, structures: [Structure]) throws -> [DVH] {
        try dose.validate(); try labels.validate()
        guard dose.modality == .dose, labels.modality == .labels, dose.grid == labels.grid else {
            throw TPSError.invalid("DVH requires dose and labels on the exact same spatial grid and frame.")
        }
        let maximum = max(Double(dose.values.max() ?? 0), 1)
        return structures.compactMap { structure in
            let samples = dose.values.indices.filter { Int(labels.values[$0]) == structure.id }.map { dose.values[$0] }.sorted()
            guard !samples.isEmpty else { return nil }
            let points = (0...80).map { bin -> DVHPoint in
                let threshold = maximum * Double(bin) / 80
                var low = 0, high = samples.count
                while low < high { let mid = (low+high)/2; if Double(samples[mid]) < threshold { low = mid+1 } else { high = mid } }
                return DVHPoint(dose: threshold, volumePercent: 100 * Double(samples.count-low)/Double(samples.count))
            }
            let index = max(0, Int(ceil(0.05 * Double(samples.count))) - 1)
            return DVH(id: structure.id, name: structure.name, color: structure.color,
                       volumeCC: Double(samples.count)*dose.grid.spacing.reduce(1, *)/1000,
                       meanGy: samples.reduce(0) { $0+Double($1) }/Double(samples.count),
                       d95Gy: Double(samples[index]), points: points)
        }
    }
}
