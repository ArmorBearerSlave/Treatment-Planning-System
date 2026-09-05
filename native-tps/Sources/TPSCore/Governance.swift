import Foundation

public enum TPSOperation: String, Codable, CaseIterable, Sendable, Identifiable {
    case contour, predictDose, syntheticCT, inspect
    public var id: String { rawValue }
    public var title: String {
        switch self { case .contour: "Contouring"; case .predictDose: "Dose prediction"; case .syntheticCT: "Synthetic CT"; case .inspect: "Inspect case" }
    }
    public var modality: Modality { switch self { case .contour: .labels; case .predictDose: .dose; case .syntheticCT: .ct; case .inspect: .ct } }
}
public enum AgentRole: String, Codable, CaseIterable, Sendable, Identifiable {
    case physician, physicist, dosimetrist, technologist
    public var id: String { rawValue }
    public var title: String {
        switch self { case .physician: "Physician assistant"; case .physicist: "Physics assistant"; case .dosimetrist: "Dosimetry assistant"; case .technologist: "Imaging assistant" }
    }
    public var scope: String {
        switch self {
        case .physician: "Anatomy inspection and contour proposals"
        case .physicist: "Dose and geometry investigation"
        case .dosimetrist: "Contours and predicted dose proposals"
        case .technologist: "Image inspection and synthetic CT proposals"
        }
    }
    public var allowed: Set<TPSOperation> {
        switch self {
        case .physician: [.inspect, .contour]
        case .physicist: [.inspect, .predictDose, .syntheticCT]
        case .dosimetrist: [.inspect, .contour, .predictDose]
        case .technologist: [.inspect, .syntheticCT]
        }
    }
}

public struct AgentPlan: Codable, Sendable {
    public var summary: String
    public var operations: [TPSOperation]
    public init(summary: String, operations: [TPSOperation]) { self.summary = summary; self.operations = operations }
    public func validate(for role: AgentRole) throws {
        guard !summary.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty, summary.count <= 2000,
              !operations.isEmpty, operations.count <= 4, Set(operations).count == operations.count,
              operations.allSatisfy({ role.allowed.contains($0) }) else {
            throw TPSError.invalid("Agent proposal exceeds the role's allowed operations or schema bounds.")
        }
    }
}

public struct Artifact: Codable, Sendable, Identifiable {
    public var id: UUID
    public var caseID: UUID
    public var inputHash: String
    public var operation: TPSOperation
    public var modelID: String
    public var modelVersion: String
    public var isDemo: Bool
    public var volume: Volume
    public var structures: [Structure]
    public var createdAt: Date
    public init(caseID: UUID, inputHash: String, operation: TPSOperation, modelID: String,
                modelVersion: String, isDemo: Bool, volume: Volume, structures: [Structure] = []) {
        self.id = UUID(); self.caseID = caseID; self.inputHash = inputHash; self.operation = operation
        self.modelID = modelID; self.modelVersion = modelVersion; self.isDemo = isDemo
        self.volume = volume; self.structures = structures; self.createdAt = Date()
    }
    public func validate(for source: PhantomCase) throws {
        try volume.validate()
        guard operation != .inspect, caseID == source.id, inputHash == (try Canonical.hash(source)),
              volume.grid == source.ct.grid, volume.modality == operation.modality,
              !modelID.isEmpty, !modelVersion.isEmpty else {
            throw TPSError.invalid("Result provenance, modality, or spatial geometry does not match its source case.")
        }
        if operation == .contour {
            guard !structures.isEmpty, Set(structures.map(\.id)).count == structures.count,
                  structures.allSatisfy({ $0.id > 0 && !$0.name.isEmpty && $0.color.count == 3 && $0.color.allSatisfy { $0.isFinite && (0...1).contains($0) } }) else {
                throw TPSError.invalid("Result has an invalid structure dictionary.")
            }
            let allowed = Set(structures.map(\.id)).union([0])
            guard volume.values.allSatisfy({ allowed.contains(Int($0)) }) else { throw TPSError.invalid("Result contains an unknown label.") }
        }
    }
}

public enum ReviewDecision: String, Codable, Sendable { case acceptedForResearch, rejected }
public struct ReviewRecord: Codable, Sendable, Identifiable {
    public var id: UUID
    public var artifactID: UUID
    public var artifactHash: String
    public var reviewer: String
    public var note: String
    public var decision: ReviewDecision
    public var date: Date
    public init(artifact: Artifact, reviewer: String, note: String, decision: ReviewDecision, actorIsAgent: Bool = false) throws {
        guard !actorIsAgent else { throw TPSError.invalid("Agents cannot record human review decisions.") }
        guard reviewer.trimmingCharacters(in: .whitespacesAndNewlines).count >= 2,
              note.trimmingCharacters(in: .whitespacesAndNewlines).count >= 8 else {
            throw TPSError.invalid("Enter a reviewer name and a meaningful review note (at least 8 characters).")
        }
        self.id = UUID(); self.artifactID = artifact.id; self.artifactHash = try Canonical.hash(artifact)
        self.reviewer = reviewer; self.note = note; self.decision = decision; self.date = Date()
    }
}

public struct AuditEvent: Codable, Sendable, Identifiable {
    public var id: UUID
    public var sequence: Int
    public var timestamp: Date
    public var actor: String
    public var action: String
    public var detail: String
    public var previousHash: String
    public var hash: String
    fileprivate var unsigned: AuditEvent { var copy = self; copy.hash = ""; return copy }
}
public struct AuditLedger: Codable, Sendable {
    public private(set) var events: [AuditEvent] = []
    public init() {}
    public mutating func append(actor: String, action: String, detail: String) throws {
        var event = AuditEvent(id: UUID(), sequence: events.count, timestamp: Date(), actor: actor,
            action: action, detail: detail, previousHash: events.last?.hash ?? "GENESIS", hash: "")
        event.hash = try Canonical.hash(event.unsigned)
        events.append(event)
    }
    public func validate() throws {
        var previous = "GENESIS"
        for (i, event) in events.enumerated() {
            guard event.sequence == i, event.previousHash == previous, event.hash == (try Canonical.hash(event.unsigned)) else {
                throw TPSError.invalid("Audit chain integrity failed at event \(i).")
            }
            previous = event.hash
        }
    }
}

public struct Workspace: Codable, Sendable {
    public var schemaVersion = 1
    public var cases: [PhantomCase] = []
    public var artifacts: [Artifact] = []
    public var reviews: [ReviewRecord] = []
    public var ledger = AuditLedger()
    public init() {}
    public func latestReview(for artifact: Artifact) -> ReviewRecord? {
        reviews.last { $0.artifactID == artifact.id && $0.artifactHash == (try? Canonical.hash(artifact)) }
    }
    public func validate() throws {
        guard schemaVersion == 1, Set(cases.map(\.id)).count == cases.count,
              Set(artifacts.map(\.id)).count == artifacts.count else { throw TPSError.invalid("Invalid workspace version or duplicate identity.") }
        try ledger.validate()
        for source in cases { try source.validate() }
        for artifact in artifacts {
            guard let source = cases.first(where: { $0.id == artifact.caseID }) else { throw TPSError.invalid("Orphan result.") }
            try artifact.validate(for: source)
        }
        for review in reviews {
            guard let artifact = artifacts.first(where: { $0.id == review.artifactID }),
                  review.artifactHash == (try Canonical.hash(artifact)),
                  review.reviewer.trimmingCharacters(in: .whitespacesAndNewlines).count >= 2,
                  review.note.trimmingCharacters(in: .whitespacesAndNewlines).count >= 8 else {
                throw TPSError.invalid("Review no longer matches its artifact or lacks reviewer evidence.")
            }
        }
    }
    public func researchExport(caseID: UUID) throws -> ResearchBundle {
        try validate()
        guard let source = cases.first(where: { $0.id == caseID }) else { throw TPSError.invalid("Select a case.") }
        let eligible = artifacts.filter { $0.caseID == caseID && latestReview(for: $0)?.decision == .acceptedForResearch }
        guard !eligible.isEmpty else { throw TPSError.invalid("Research export requires an accepted result with a current review.") }
        return ResearchBundle(schemaVersion: 1, intendedUse: "synthetic-research-only", clinicalUsePermitted: false,
                              source: source, artifacts: eligible,
                              reviews: eligible.compactMap { latestReview(for: $0) }, audit: ledger,
                              split: source.recipe.suggestedSplit, sourceHash: try Canonical.hash(source))
    }
}
public struct ResearchBundle: Codable, Sendable {
    public var schemaVersion: Int
    public var intendedUse: String
    public var clinicalUsePermitted: Bool
    public var source: PhantomCase
    public var artifacts: [Artifact]
    public var reviews: [ReviewRecord]
    public var audit: AuditLedger
    public var split: String
    public var sourceHash: String
    public func validate() throws {
        guard schemaVersion == 1, intendedUse == "synthetic-research-only", !clinicalUsePermitted,
              sourceHash == (try Canonical.hash(source)), split == source.recipe.suggestedSplit, !artifacts.isEmpty else {
            throw TPSError.invalid("Invalid research bundle identity, split or intended use.")
        }
        var workspace = Workspace()
        workspace.cases = [source]; workspace.artifacts = artifacts; workspace.reviews = reviews; workspace.ledger = audit
        try workspace.validate()
        guard artifacts.allSatisfy({ workspace.latestReview(for: $0)?.decision == .acceptedForResearch }) else {
            throw TPSError.invalid("Research bundle contains an output without a current acceptance.")
        }
    }
}

public enum WorkspaceFile {
    public static func load(_ url: URL) throws -> Workspace {
        let size = try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
        guard size <= 256_000_000 else { throw TPSError.invalid("Workspace exceeds the 256 MB prototype limit.") }
        let result = try JSONDecoder().decode(Workspace.self, from: Data(contentsOf: url))
        try result.validate(); return result
    }
    public static func save(_ workspace: Workspace, to url: URL) throws {
        try workspace.validate()
        try Canonical.data(workspace).write(to: url, options: .atomic)
    }
}
