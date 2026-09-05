import Foundation
import TPSCore

/// Portable observations, not treatment approval or edited segmentation.
struct TabletReview: Codable, Sendable {
    var schemaVersion = 1
    var sourceHash: String
    var caseID: UUID
    var caseName: String
    var clinicalUsePermitted = false
    var intendedUse = "synthetic-research-review"
    var reviewer = ""
    var note = ""
    var checked: Set<String> = []
    var drawings: [String: Data] = [:]
    var updatedAt = Date()
    var coordinateContract = "Voxel planes; axis:slice keys, zero-based indices. Pencil canvas width 1024; height follows physical slice aspect ratio. X/Y increase right/down in displayed plane. Markup is not a segmentation."
    static let checklist = ["CT geometry inspected", "Organ boundaries inspected", "Dose provenance inspected"]
    func validate(source: PhantomCase) throws {
        guard schemaVersion == 1, caseID == source.id, sourceHash == (try Canonical.hash(source)),
              !clinicalUsePermitted, intendedUse == "synthetic-research-review",
              checked.isSubset(of: Set(Self.checklist)) else { throw TPSError.invalid("Review is not bound to this research case.") }
        for (key, data) in drawings {
            let parts = key.split(separator: ":").compactMap { Int($0) }
            guard parts.count == 2, (0...2).contains(parts[0]), (0..<source.ct.grid.dimensions[parts[0]]).contains(parts[1]), data.count <= 8_000_000 else {
                throw TPSError.invalid("Invalid slice markup.")
            }
        }
    }
}
