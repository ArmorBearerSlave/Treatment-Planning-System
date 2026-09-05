import Foundation
import TPSCore

@main struct TPSCheck {
    static func main() async throws {
        let source = try PhantomFactory.analytic(PhantomRecipe(), size: 32)
        var workspace = Workspace(); workspace.cases.append(source)
        try workspace.ledger.append(actor: "integration-check", action: "case.created", detail: source.id.uuidString)
        for operation in [TPSOperation.contour, .predictDose, .syntheticCT] {
            let artifact = try AnalyticInference.run(operation, source: source)
            workspace.artifacts.append(artifact)
            workspace.reviews.append(try ReviewRecord(artifact: artifact, reviewer: "Integration test operator",
                note: "Synthetic integration check only, not independent clinical review.", decision: .acceptedForResearch))
            try workspace.ledger.append(actor: "integration-check", action: "fixture.reviewed", detail: artifact.id.uuidString)
        }
        try workspace.validate()
        let export = try workspace.researchExport(caseID: source.id)
        let dose = workspace.artifacts.first { $0.operation == .predictDose }!
        let dvh = try DVH.calculate(dose: dose.volume, labels: source.truth, structures: source.structures)
        if let flag = CommandLine.arguments.firstIndex(of: "--llm-model"), CommandLine.arguments.count > flag+1 {
            let model = CommandLine.arguments[flag+1]
            let plan = try await LocalAgentClient.propose(endpoint: "http://127.0.0.1:11434", model: model,
                role: .dosimetrist, prompt: "Inspect this synthetic case and propose contours. Do not predict dose.", source: source)
            guard !plan.operations.contains(.predictDose) else { throw TPSError.invalid("Live model failed the negation smoke check.") }
            print("PASS: live local LLM \(model) → \(plan.operations.map(\.rawValue).joined(separator: ", ")); no dose action proposed.")
        }
        if CommandLine.arguments.count > 1 && !CommandLine.arguments[1].hasPrefix("--") {
            let directory = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
            try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
            try Canonical.data(source).write(to: directory.appendingPathComponent("synthetic-case.json"), options: .atomic)
            try Canonical.data(export).write(to: directory.appendingPathComponent("research-bundle.json"), options: .atomic)
            try WorkspaceFile.save(workspace, to: directory.appendingPathComponent("workspace.json"))
            _ = try WorkspaceFile.load(directory.appendingPathComponent("workspace.json"))
        }
        print("PASS: phantom → three fixture outputs → research reviews → export → \(dvh.count) DVHs; audit verified.")
        print("No trained-model, XCAT2/nBio, clinical or generalization claim. Physical memory: \(ProcessInfo.processInfo.physicalMemory / 1_073_741_824) GiB.")
    }
}
