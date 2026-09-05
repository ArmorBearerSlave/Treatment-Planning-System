import Foundation
import Darwin
import TPSCore

@main struct TPSCheck {
    static func main() async {
        do { try await run() }
        catch {
            FileHandle.standardError.write(Data("FAIL: \(error.localizedDescription)\n".utf8))
            exit(EXIT_FAILURE)
        }
    }
    static func run() async throws {
        if let flag = CommandLine.arguments.firstIndex(of: "--validate-case"), CommandLine.arguments.count > flag+1 {
            let url = URL(fileURLWithPath: CommandLine.arguments[flag+1])
            guard (try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0) <= 96_000_000 else { throw TPSError.invalid("Case exceeds 96 MB.") }
            let source = try JSONDecoder().decode(PhantomCase.self, from: Data(contentsOf: url))
            try source.validate()
            print("PASS: \(source.name), \(source.ct.grid.count) voxels; MR present: \(source.mr != nil); native case contract verified.")
            print("This checks encoded data consistency, not source calibration or independent spatial registration.")
            return
        }
        if let flag = CommandLine.arguments.firstIndex(of: "--validate-bundle"), CommandLine.arguments.count > flag+1 {
            let url = URL(fileURLWithPath: CommandLine.arguments[flag+1])
            guard (try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0) <= 256_000_000 else { throw TPSError.invalid("Bundle exceeds 256 MB.") }
            let bundle = try JSONDecoder().decode(ResearchBundle.self, from: Data(contentsOf: url))
            try bundle.validate()
            print("PASS: native research bundle hashes, review binding, geometry and audit chain verified.")
            return
        }
        let source = try PhantomFactory.analytic(PhantomRecipe(), size: 32)
        if let flag = CommandLine.arguments.firstIndex(of: "--coreml-fixture"), CommandLine.arguments.count > flag+1 {
            let url = URL(fileURLWithPath: CommandLine.arguments[flag+1])
            let result = try await CoreMLInference.run(manifestURL: url, operation: .syntheticCT, source: source)
            let maximumError = zip(result.volume.values, source.mr!.values).map { abs($0 - $1) }.max() ?? 0
            // ANE/GPU may round to Float16 internally even with Float32 IO.
            // Accept only exact or IEEE Float16-rounded identity values, not arbitrary error.
            var preservesOrder = true
            for (actual, expected) in zip(result.volume.values, source.mr!.values) {
                let rounded = Float(Float16(expected))
                let exactMatch = abs(actual - expected) < Float(0.0001)
                let roundedMatch = abs(actual - rounded) < Float(0.0001)
                if !exactMatch && !roundedMatch { preservesOrder = false; break }
            }
            guard result.isDemo, preservesOrder else {
                throw TPSError.invalid("Core ML identity fixture: maximum error \(maximumError), fixture flag \(result.isDemo).")
            }
            print("PASS: real Core ML compilation/prediction preserve [1,1,Z,Y,X] ordering with exact-or-Float16-rounded identity values; max error \(maximumError). Fixture provenance verified.")
        }
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
