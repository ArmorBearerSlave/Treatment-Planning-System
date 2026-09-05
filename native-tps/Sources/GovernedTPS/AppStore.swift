import SwiftUI
import AppKit
import UniformTypeIdentifiers
import TPSCore

enum Screen: String, CaseIterable, Identifiable {
    case workspace = "Workspace", agents = "Agent workbench", phantoms = "Phantom lab", models = "Local models", governance = "Review & evidence"
    var id: String { rawValue }
    var icon: String { switch self { case .workspace: "square.stack.3d.up"; case .agents: "point.3.connected.trianglepath.dotted"; case .phantoms: "figure.stand"; case .models: "cpu"; case .governance: "checkmark.shield" } }
}
enum InferenceMode: String, CaseIterable, Identifiable {
    case fixture = "Analytic fixture", coreML = "Core ML on this Mac"
    var id: String { rawValue }
}

@MainActor final class AppStore: ObservableObject {
    @Published var screen: Screen = .workspace
    @Published private(set) var workspace = Workspace()
    @Published var selectedCaseID: UUID?
    @Published var selectedArtifactID: UUID?
    @Published var busy = false
    @Published var activity = "Ready"
    @Published var error: String?
    @Published var slice = 32.0
    @Published var windowCenter = 40.0
    @Published var windowWidth = 500.0
    @Published var overlayOpacity = 0.55
    @Published var showTruth = true
    @Published var inferenceMode: InferenceMode = .fixture
    @Published var modelManifests: [TPSOperation: URL] = [:]
    @Published var ollamaEndpoint = "http://127.0.0.1:11434"
    @Published var ollamaModel = "qwen3-coder:30b"
    @Published var availableModels: [String] = []
    @Published var ollamaStatus = "Not checked"
    @Published var sparkEndpoint = ""
    @Published var role: AgentRole = .dosimetrist
    @Published var prompt = "Inspect the synthetic case, then generate contour and dose proposals for research review."
    @Published var proposal: AgentPlan?
    @Published var proposalCaseID: UUID?
    @Published var proposalRole: AgentRole?
    @Published var proposalModel = ""
    @Published var reviewer = ""
    @Published var reviewNote = ""
    @Published var recipe = PhantomRecipe()
    @Published var persistenceDescription = "Local workspace"
    private var workspaceURL: URL

    var source: PhantomCase? { workspace.cases.first { $0.id == selectedCaseID } }
    var artifacts: [Artifact] { workspace.artifacts.filter { $0.caseID == selectedCaseID } }
    var selectedArtifact: Artifact? { artifacts.first { $0.id == selectedArtifactID } }
    var pendingCount: Int { workspace.artifacts.filter { workspace.latestReview(for: $0) == nil }.count }
    var dvhs: [DVH] {
        guard let source, let selectedArtifact, selectedArtifact.operation == .predictDose else { return [] }
        return (try? DVH.calculate(dose: selectedArtifact.volume, labels: source.truth, structures: source.structures.filter { $0.id != 1 })) ?? []
    }

    init() {
        workspaceURL = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("GovernedTPS", isDirectory: true).appendingPathComponent("workspace.json")
        if FileManager.default.fileExists(atPath: workspaceURL.path) {
            do { workspace = try WorkspaceFile.load(workspaceURL); selectedCaseID = workspace.cases.last?.id; activity = "Restored local workspace" }
            catch { self.error = "Saved workspace could not be verified. It has not been overwritten. \(error.localizedDescription)" }
        }
    }
    private func commit(_ next: Workspace) throws {
        try FileManager.default.createDirectory(at: workspaceURL.deletingLastPathComponent(), withIntermediateDirectories: true)
        try WorkspaceFile.save(next, to: workspaceURL)
        workspace = next
        persistenceDescription = "Saved locally · \(Date().formatted(date: .omitted, time: .shortened))"
    }
    func perform(_ label: String, work: @escaping @MainActor () async throws -> Void) {
        guard !busy else { return }
        busy = true; activity = label
        Task {
            defer { busy = false }
            do { try await work(); activity = "Ready · \(label) complete" }
            catch { self.error = error.localizedDescription; activity = "Stopped · \(label)" }
        }
    }
    func createPhantom(remote: Bool = false) {
        let recipe = self.recipe
        perform(remote ? "Generating on DGX Spark" : "Building analytic phantom") { [self] in
            let result: PhantomCase
            if remote { result = try await ModelGateway.phantom(endpoint: sparkEndpoint, recipe: recipe) }
            else { result = try await Task.detached { try PhantomFactory.analytic(recipe) }.value }
            var next = workspace
            guard !next.cases.contains(where: { $0.id == result.id }) else { throw TPSError.invalid("Generator returned an existing case identifier.") }
            next.cases.append(result)
            try next.ledger.append(actor: "operator", action: "phantom.created", detail: "\(result.id) · \(result.generator) · \(try Canonical.hash(result))")
            try commit(next)
            selectedCaseID = result.id; selectedArtifactID = nil; slice = Double(result.ct.grid.dimensions[2]/2)
            proposal = nil; screen = .workspace
        }
    }
    func run(_ operation: TPSOperation) {
        guard let source else { return }
        let mode = inferenceMode, manifestURL = modelManifests[operation]
        perform(operation.title) { [self] in try await execute(operation, source: source, mode: mode, manifestURL: manifestURL, actor: "operator") }
    }
    private func execute(_ operation: TPSOperation, source: PhantomCase, mode: InferenceMode, manifestURL: URL?, actor: String) async throws {
        if operation == .inspect {
            try source.validate()
            var next = workspace
            try next.ledger.append(actor: actor, action: "case.inspected", detail: "\(source.id) · grid and provenance checks passed")
            try commit(next); return
        }
        var started = workspace
        try started.ledger.append(actor: actor, action: "inference.requested", detail: "\(source.id) · \(operation.rawValue) · \(mode.rawValue)")
        try commit(started)
        do {
            let artifact: Artifact
            if mode == .fixture {
                artifact = try await Task.detached { try AnalyticInference.run(operation, source: source) }.value
            } else {
                guard let manifestURL else { throw TPSError.invalid("Choose a local model manifest for \(operation.title) in Local models.") }
                artifact = try await CoreMLInference.run(manifestURL: manifestURL, operation: operation, source: source)
            }
            try artifact.validate(for: source)
            var next = workspace
            next.artifacts.append(artifact)
            try next.ledger.append(actor: actor, action: "artifact.proposed", detail: "\(artifact.id) · \(artifact.modelID) · \(try Canonical.hash(artifact))")
            try commit(next)
            selectedArtifactID = artifact.id
        } catch {
            var next = workspace
            try next.ledger.append(actor: actor, action: "inference.failed", detail: "\(operation.rawValue) · \(error.localizedDescription)")
            try commit(next)
            throw error
        }
    }
    func checkOllama() {
        perform("Checking local Ollama") { [self] in
            availableModels = try await LocalAgentClient.models(endpoint: ollamaEndpoint)
            if !availableModels.contains(ollamaModel), let fallback = ["qwen3-coder:30b", "qwen3.5:9b", "qwen3:4b"].first(where: { availableModels.contains($0) }) { ollamaModel = fallback }
            ollamaStatus = "Connected · \(availableModels.count) installed models"
        }
    }
    func propose() {
        guard let source else { return }
        let role = role, prompt = prompt, model = ollamaModel, endpoint = ollamaEndpoint
        proposal = nil
        perform("Compiling local agent proposal") { [self] in
            let result = try await LocalAgentClient.propose(endpoint: endpoint, model: model, role: role, prompt: prompt, source: source)
            var next = workspace
            try next.ledger.append(actor: "agent:\(role.rawValue)", action: "workflow.proposed",
                detail: "case=\(source.id) model=\(model) promptHash=\(try Canonical.hash(prompt)) plan=\(String(decoding: try Canonical.data(result), as: UTF8.self))")
            try commit(next)
            proposal = result; proposalCaseID = source.id; proposalRole = role; proposalModel = model
        }
    }
    func executeProposal() {
        guard let proposal, let source, proposalCaseID == source.id, proposalRole == role else { error = "The case or agent role changed. Compile a fresh proposal."; return }
        let role = role, mode = inferenceMode, manifests = modelManifests
        self.proposal = nil // One-shot execution; repeated clicks cannot replay a plan.
        perform("Executing confirmed workflow") { [self] in
            try proposal.validate(for: role)
            var next = workspace
            try next.ledger.append(actor: "operator", action: "workflow.confirmed", detail: "\(source.id) · \(role.rawValue) · \(try Canonical.hash(proposal))")
            try commit(next)
            for operation in proposal.operations {
                try await execute(operation, source: source, mode: mode, manifestURL: manifests[operation], actor: "agent:\(role.rawValue)")
            }
            screen = .workspace
        }
    }
    func review(_ decision: ReviewDecision) {
        guard let artifact = selectedArtifact else { return }
        do {
            let record = try ReviewRecord(artifact: artifact, reviewer: reviewer, note: reviewNote, decision: decision)
            var next = workspace
            next.reviews.append(record)
            try next.ledger.append(actor: "local-reviewer:\(reviewer)", action: "artifact.\(decision.rawValue)", detail: "\(artifact.id) · \(record.artifactHash) · \(reviewNote)")
            try commit(next); reviewNote = ""
        } catch { self.error = error.localizedDescription }
    }
    func chooseManifest(_ operation: TPSOperation) {
        let panel = NSOpenPanel(); panel.allowedContentTypes = [.json]; panel.message = "Select the model's TPS manifest JSON. The matching .mlmodel must be beside it."
        guard panel.runModal() == .OK, let url = panel.url else { return }
        do {
            let manifest = try CoreMLInference.manifest(at: url)
            guard manifest.operation == operation else { throw TPSError.invalid("Manifest is for a different operation.") }
            modelManifests[operation] = url
            activity = "Configured \(manifest.modelID) · checksum will be checked before inference"
        } catch { self.error = error.localizedDescription }
    }
    func importCase() {
        guard !busy else { return }
        let panel = NSOpenPanel(); panel.allowedContentTypes = [.json]
        panel.canChooseDirectories = false; panel.allowsMultipleSelection = false
        panel.prompt = "Import case"
        panel.message = "Choose the converted native case JSON on this Mac. Copy Spark output to this Mac first. DICOM folders and NPZ arrays require conversion."
        guard panel.runModal() == .OK, let url = panel.url else { return }
        let previous = workspace, destination = workspaceURL
        perform("Importing synthetic case") { [self] in
            let (next, source) = try await Task.detached(priority: .userInitiated) {
                let scoped = url.startAccessingSecurityScopedResource()
                defer { if scoped { url.stopAccessingSecurityScopedResource() } }
                let size = try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
                guard size <= 96_000_000 else { throw TPSError.invalid("Case file exceeds 96 MB.") }
                let source = try JSONDecoder().decode(PhantomCase.self, from: Data(contentsOf: url))
                try source.validate()
                if let existing = previous.cases.first(where: { $0.id == source.id }) {
                    guard try Canonical.hash(existing) == Canonical.hash(source) else {
                        throw TPSError.invalid("A different version of this case is already in the workspace. Use a new case identifier for revised data.")
                    }
                    return (previous, existing)
                }
                var next = previous; next.cases.append(source)
                try next.ledger.append(actor: "operator", action: "case.imported", detail: "\(source.id) · \(try Canonical.hash(source))")
                try FileManager.default.createDirectory(at: destination.deletingLastPathComponent(), withIntermediateDirectories: true)
                try WorkspaceFile.save(next, to: destination)
                return (next, source)
            }.value
            workspace = next; selectedCaseID = source.id; selectedArtifactID = nil; proposal = nil
            slice = Double(source.ct.grid.dimensions[2] / 2); screen = .workspace
            persistenceDescription = "Saved locally · \(Date().formatted(date: .omitted, time: .shortened))"
        }
    }
    func exportResearch() {
        guard let source else { return }
        do {
            let bundle = try workspace.researchExport(caseID: source.id)
            let panel = NSSavePanel(); panel.allowedContentTypes = [.json]; panel.nameFieldStringValue = "research-\(source.id.uuidString.prefix(8)).json"
            guard panel.runModal() == .OK, let url = panel.url else { return }
            try Canonical.data(bundle).write(to: url, options: .atomic)
            var next = workspace
            try next.ledger.append(actor: "operator", action: "research.exported", detail: "\(source.id) · \(try Canonical.hash(bundle))")
            try commit(next); activity = "Research bundle exported"
        } catch { self.error = error.localizedDescription }
    }
    func removePlaceholderMR() {
        guard let source else { return }
        let previous = workspace, destination = workspaceURL
        perform("Removing placeholder MR") { [self] in
            let next = try await Task.detached(priority: .userInitiated) {
                guard source.mr != nil,
                      source.mrIsPlaceholder == true || source.sourceNotes?["mr"]?.lowercased().contains("placeholder") == true else {
                    throw TPSError.invalid("The selected case has no explicitly identified placeholder MR.")
                }
                guard !previous.artifacts.contains(where: { $0.caseID == source.id }) else {
                    throw TPSError.invalid("This case has derived artifacts. Import a new CT-only revision to preserve their source provenance.")
                }
                var revised = source
                revised.mr = nil; revised.mrIsPlaceholder = nil
                revised.sourceNotes?["mr"] = "Not provided. CT-only case; placeholder removed."
                var next = previous
                guard let index = next.cases.firstIndex(where: { $0.id == source.id }) else { throw TPSError.invalid("Case is unavailable.") }
                next.cases[index] = revised
                try next.ledger.append(actor: "operator", action: "case.placeholderMR.removed",
                                      detail: "\(source.id) · previous=\(try Canonical.hash(source)) · revised=\(try Canonical.hash(revised))")
                try WorkspaceFile.save(next, to: destination)
                return next
            }.value
            workspace = next; proposal = nil
        }
    }
    func saveCopy() {
        let panel = NSSavePanel(); panel.allowedContentTypes = [.json]; panel.nameFieldStringValue = "governed-tps-workspace.json"
        guard panel.runModal() == .OK, let url = panel.url else { return }
        do { try WorkspaceFile.save(workspace, to: url) } catch { self.error = error.localizedDescription }
    }
}
