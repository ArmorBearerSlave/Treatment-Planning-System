import Foundation
import Darwin
import CryptoKit
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
        if let flag = CommandLine.arguments.firstIndex(of: "--cerr-input"), CommandLine.arguments.count > flag+3 {
            let sourceURL = URL(fileURLWithPath: CommandLine.arguments[flag+1])
            let resultURL = URL(fileURLWithPath: CommandLine.arguments[flag+2])
            let folder = URL(fileURLWithPath: CommandLine.arguments[flag+3])
            guard !FileManager.default.fileExists(atPath: folder.path) else { throw TPSError.invalid("Use a new CERR job folder.") }
            let source = try JSONDecoder().decode(PhantomCase.self, from: Data(contentsOf: sourceURL))
            let result = try JSONDecoder().decode(MatRadResult.self, from: Data(contentsOf: resultURL))
            let request = try CERRRequest(source: source, dose: result.volume, doseDescription: "matRad geometry software fixture")
            try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
            try Canonical.data(source).write(to: folder.appendingPathComponent("source.json"))
            try Canonical.data(result.volume).write(to: folder.appendingPathComponent("dose.json"))
            try Canonical.data(request).write(to: folder.appendingPathComponent("request.json"))
            print("PASS: canonical CT, labels and dose frozen for CERR software verification.")
            return
        }
        if let flag = CommandLine.arguments.firstIndex(of: "--validate-cerr"), CommandLine.arguments.count > flag+1 {
            let folder = URL(fileURLWithPath: CommandLine.arguments[flag+1])
            let source = try JSONDecoder().decode(PhantomCase.self, from: Data(contentsOf: folder.appendingPathComponent("source.json")))
            let dose = try JSONDecoder().decode(Volume.self, from: Data(contentsOf: folder.appendingPathComponent("dose.json")))
            let request = try JSONDecoder().decode(CERRRequest.self, from: Data(contentsOf: folder.appendingPathComponent("request.json")))
            let report = try JSONDecoder().decode(CERRReport.self, from: Data(contentsOf: folder.appendingPathComponent("report.json")))
            let rows = try report.compare(source: source, dose: dose, request: request)
            for row in rows {
                print("\(row.cerr.name): n=\(row.cerr.sampleCount) ΔmeanGy=\(row.cerr.meanGy-row.nativeMeanGy) ΔD95Gy=\(row.cerr.d95Gy-row.nativeD95Gy) Δcc=\(row.cerr.volumeCC-row.nativeVolumeCC) maxSampleΔGy=\(row.cerr.maxSampleDifferenceGy)")
            }
            print("PASS: CERR provenance, structure coverage, sample counts and histogram volumes; native comparisons computed.")
            return
        }
        if let flag = CommandLine.arguments.firstIndex(of: "--validate-matrad"), CommandLine.arguments.count > flag+1 {
            let folder = URL(fileURLWithPath: CommandLine.arguments[flag+1])
            let source = try JSONDecoder().decode(PhantomCase.self, from: Data(contentsOf: folder.appendingPathComponent("source.json")))
            let request = try JSONDecoder().decode(MatRadRequest.self, from: Data(contentsOf: folder.appendingPathComponent("request.json")))
            let result = try JSONDecoder().decode(MatRadResult.self, from: Data(contentsOf: folder.appendingPathComponent("result.json")))
            let artifact = try result.artifact(source: source, request: request)
            try artifact.validate(for: source)
            let dvhs = try DVH.calculate(dose: result.volume, labels: source.truth, structures: source.structures)
            print("PASS: matRad source/request binding, converged optimizer, exact CT grid and physical course Gy. \(dvhs.count) DVHs computed.")
            return
        }
        if let flag = CommandLine.arguments.firstIndex(of: "--matrad-smoke-input"), CommandLine.arguments.count > flag+1 {
            let folder = URL(fileURLWithPath: CommandLine.arguments[flag+1])
            guard !FileManager.default.fileExists(atPath: folder.path) else { throw TPSError.invalid("Use a new smoke folder.") }
            var source = try PhantomFactory.analytic(PhantomRecipe(), size: 16)
            source.name = "MATRAD-GEOMETRY-FIXTURE"; source.mr = nil
            let oldCT = source.ct, oldLabels = source.truth
            let grid = Grid(dimensions: [12,14,10], spacing: [2,3,4], origin: [-11,-19.5,-18], frameID: source.ct.grid.frameID)
            var indices: [Int] = []
            for z in 0..<10 { for y in 0..<14 { for x in 0..<12 { indices.append(oldCT.grid.index(x,y,z)) } } }
            source.ct = Volume(grid: grid, modality: .ct, units: "HU", values: indices.map { oldCT.values[$0] })
            source.truth = Volume(grid: grid, modality: .labels, units: "label", values: indices.map { oldLabels.values[$0] })
            source.sourceNotes = ["reference":"Cropped analytic fixture with asymmetric spacing for adapter software verification only."]
            var settings = MatRadSettings(targetID: 2)
            settings.gantryAngles = [0]; settings.bixelWidthMM = 20; settings.fractions = 5
            let request = try MatRadRequest(source: source, settings: settings)
            try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
            try Canonical.data(source).write(to: folder.appendingPathComponent("source.json"))
            try Canonical.data(request).write(to: folder.appendingPathComponent("request.json"))
            print("PASS: asymmetric CT-only fixture prepared for matRad; five fractions, one generic photon beam.")
            return
        }
        if let flag = CommandLine.arguments.firstIndex(of: "--learning-smoke"), CommandLine.arguments.count > flag+1 {
            let directory = URL(fileURLWithPath: CommandLine.arguments[flag+1], isDirectory: true)
            guard !FileManager.default.fileExists(atPath: directory.path) else { throw TPSError.invalid("Choose a new smoke-test directory.") }
            try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
            var entries: [LearningCase] = [], sources: [UUID:PhantomCase] = [:]
            for index in 0..<6 {
                var source = try PhantomFactory.analytic(PhantomRecipe(anatomyID: "LEARNING-FIXTURE-\(index)", seed: index*13, bodyScale: 0.8+Double(index)*0.08), size: 16)
                source.mr = nil; source.sourceNotes = ["anatomyGroupID": "pipeline-fixture-\(index)", "reference": "Artificial split groups for software testing only; not evidence of independent anatomy generalization."]
                let path = directory.appendingPathComponent("fixture-\(index).json")
                let bytes = try Canonical.data(source)
                try bytes.write(to: path)
                let fileHash = SHA256.hash(data: bytes).map { String(format: "%02x",$0) }.joined()
                entries.append(LearningCase(source: source, url: path, fileSHA256: fileHash, anatomyGroup: "pipeline-fixture-\(index)"))
                sources[source.id] = source
            }
            let partition = try DatasetPartition.make(cases: entries, seed: 42)
            let training = entries.filter { partition.assignments[$0.id.uuidString] == "train" }.map { sources[$0.id]! }
            let model = try GaussianContourModel.fit(training, varianceFloor: 0.01)
            var validation: [CaseEvaluation] = []
            for split in ["validation"] {
                for entry in entries where partition.assignments[entry.id.uuidString] == split {
                    let source = sources[entry.id]!
                    validation.append(try CaseEvaluation.contours(source: source, prediction: model.predict(source), split: split))
                }
            }
            let experiment = LearningExperiment(cases: entries, partition: partition, model: model, selectedVarianceFloor: 0.01, validation: validation)
            try Canonical.data(experiment).write(to: directory.appendingPathComponent("experiment.json"))
            print("PASS: six artificial CT-only fixtures → grouped split → trained contour baseline → validation metrics. Test is reserved for app smoke check. Pipeline test only, no model performance claim.")
            return
        }
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
