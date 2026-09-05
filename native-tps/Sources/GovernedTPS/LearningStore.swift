import SwiftUI
import AppKit
import CryptoKit
import TPSCore

@MainActor final class LearningStore: ObservableObject {
    @Published var cases: [LearningCase] = []
    @Published var partition: DatasetPartition?
    @Published var experiment: LearningExperiment?
    @Published var seed = 42
    @Published var trainPercent = 70
    @Published var validationPercent = 15
    @Published var busy = false
    @Published var status = "Select the completed native training cohort when it arrives from DGX."
    @Published var error: String?
    @Published var resultURL: URL?
    @Published var referenceConfirmed = false
    private var datasetURL: URL?

    static nonisolated func hash(_ data: Data) -> String { SHA256.hash(data: data).map { String(format: "%02x",$0) }.joined() }
    static nonisolated func load(_ entry: LearningCase) throws -> PhantomCase {
        let url = URL(fileURLWithPath: entry.path)
        guard (try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0) <= 96_000_000 else { throw TPSError.invalid("Case exceeds 96 MB.") }
        let bytes = try Data(contentsOf: url)
        guard hash(bytes) == entry.fileSHA256 else { throw TPSError.invalid("Dataset file changed after selection: \(entry.name). Start a new dataset snapshot.") }
        let source = try JSONDecoder().decode(PhantomCase.self, from: bytes)
        try source.validate()
        guard source.id == entry.id else { throw TPSError.invalid("Case identity changed.") }
        return source
    }
    func chooseDataset() {
        let panel = NSOpenPanel(); panel.canChooseDirectories = true; panel.canChooseFiles = false
        panel.message = "Choose a completed native-case cohort folder with anatomy-groups.json. Raw DICOM requires validated CT/label/dose conversion."
        guard panel.runModal() == .OK, let folder = panel.url else { return }
        run("Checking dataset files and target provenance") { [self] in
            let entries = try await Task.detached {
                let files = try FileManager.default.contentsOfDirectory(at: folder, includingPropertiesForKeys: [.fileSizeKey]).filter { $0.pathExtension == "json" }.sorted { $0.path < $1.path }
                var groups: [String:String] = [:]
                let mapping = folder.appendingPathComponent("anatomy-groups.json")
                if FileManager.default.fileExists(atPath: mapping.path) {
                    struct Mapping: Decodable { var schemaVersion: Int; var groups: [String:String] }
                    let value = try JSONDecoder().decode(Mapping.self, from: Data(contentsOf: mapping))
                    guard value.schemaVersion == 1 else { throw TPSError.invalid("Unsupported anatomy mapping.") }
                    groups = value.groups
                }
                var entries: [LearningCase] = []
                for url in files {
                    let name = url.lastPathComponent
                    if ["anatomy-groups.json", "transfer-manifest.json", "dataset.json"].contains(name) { continue }
                    guard (try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0) <= 96_000_000 else { throw TPSError.invalid("Oversized file: \(name)") }
                    let bytes = try Data(contentsOf: url)
                    guard let object = try JSONSerialization.jsonObject(with: bytes) as? [String:Any], object["ct"] != nil, object["truth"] != nil else { continue }
                    let source = try JSONDecoder().decode(PhantomCase.self, from: bytes); try source.validate()
                    let group = groups[source.id.uuidString] ?? groups[source.name] ?? source.sourceNotes?["anatomyGroupID"] ?? ""
                    entries.append(LearningCase(source: source, url: url, fileSHA256: Self.hash(bytes), anatomyGroup: group))
                }
                guard !entries.isEmpty else { throw TPSError.invalid("No native CT + label cases found. DICOM proxy RTSTRUCT/RTDOSE are not automatically accepted as native ground truth. Complete conversion and the anatomy-group manifest on DGX first.") }
                guard Set(entries.map(\.id)).count == entries.count else { throw TPSError.invalid("Duplicate case IDs in cohort.") }
                return entries
            }.value
            cases = entries; datasetURL = folder; partition = nil; experiment = nil; resultURL = nil; referenceConfirmed = false
            status = "\(entries.count) cases indexed. Verify targets and original anatomy groups before freezing the split."
        }
    }
    func freeze() {
        do {
            guard referenceConfirmed else { throw TPSError.invalid("Inspect reference provenance and confirm its suitability for this research experiment.") }
            partition = try DatasetPartition.make(cases: cases, seed: seed, train: trainPercent, validation: validationPercent)
            status = "Split frozen in this experiment. Test references remain unused until final evaluation."
        } catch { self.error = error.localizedDescription }
    }
    func openExperiment() {
        let panel = NSOpenPanel(); panel.canChooseFiles = true; panel.canChooseDirectories = false; panel.allowedContentTypes = [.json]
        panel.message = "Open a saved learning experiment. Source files must remain at their recorded paths."
        guard panel.runModal() == .OK, let url = panel.url else { return }
        run("Verifying saved experiment") { [self] in
            let saved = try await Task.detached {
                guard (try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0) <= 16_000_000 else { throw TPSError.invalid("Experiment exceeds 16 MB.") }
                let saved = try JSONDecoder().decode(LearningExperiment.self, from: Data(contentsOf: url))
                guard saved.schemaVersion == 1, !saved.clinicalUsePermitted else { throw TPSError.invalid("Only research experiments are supported.") }
                let rebuilt = try DatasetPartition.make(cases: saved.cases, seed: saved.partition.seed, train: saved.partition.trainPercent, validation: saved.partition.validationPercent)
                guard try Canonical.hash(rebuilt) == Canonical.hash(saved.partition) else { throw TPSError.invalid("Saved partition is inconsistent with its dataset and seed.") }
                let hashes = try saved.cases.filter { rebuilt.assignments[$0.id.uuidString] == "train" }.map { try Canonical.hash(Self.load($0)) }
                guard hashes == saved.model.trainingSourceHashes else { throw TPSError.invalid("Training source binding failed.") }
                return saved
            }.value
            cases = saved.cases; partition = saved.partition; experiment = saved; resultURL = url
            seed = saved.partition.seed; trainPercent = saved.partition.trainPercent; validationPercent = saved.partition.validationPercent
            referenceConfirmed = true; status = "Saved experiment restored; source and split bindings verified."
        }
    }
    func train() {
        guard let partition, experiment == nil else { return }
        let entries = cases
        let panel = NSSavePanel(); panel.nameFieldStringValue = "contour-experiment-\(UUID().uuidString.prefix(8)).json"
        panel.message = "Save the frozen dataset, trained baseline and validation results."
        guard panel.runModal() == .OK, let output = panel.url else { return }
        run("Training Gaussian contour baseline on this Mac; selecting on validation only") { [self] in
            let result = try await Task.detached(priority: .userInitiated) {
                guard !FileManager.default.fileExists(atPath: output.path) else { throw TPSError.invalid("Choose a new experiment file; previous runs are not overwritten.") }
                let training = try entries.filter { partition.assignments[$0.id.uuidString] == "train" }.map(Self.load)
                let validation = try entries.filter { partition.assignments[$0.id.uuidString] == "validation" }.map(Self.load)
                let dictionary = training.first?.structures.map { "\($0.id):\($0.name)" }.sorted()
                guard validation.allSatisfy({ $0.structures.map { "\($0.id):\($0.name)" }.sorted() == dictionary }) else { throw TPSError.invalid("Validation label dictionary differs from training.") }
                var best: (GaussianContourModel, Double, [CaseEvaluation], Double)?
                for floor in [0.0025, 0.01, 0.04] {
                    let model = try GaussianContourModel.fit(training, varianceFloor: floor)
                    let scores = try validation.map { try CaseEvaluation.contours(source: $0, prediction: model.predict($0), split: "validation") }
                    let means = scores.compactMap(\.meanDice)
                    guard !means.isEmpty else { throw TPSError.invalid("Validation contains no scorable foreground labels.") }
                    let score = means.reduce(0,+)/Double(means.count)
                    if best == nil || score > best!.3 { best = (model,floor,scores,score) }
                }
                let result = LearningExperiment(cases: entries, partition: partition, model: best!.0, selectedVarianceFloor: best!.1, validation: best!.2)
                try Canonical.data(result).write(to: output, options: .atomic)
                return result
            }.value
            experiment = result; resultURL = output
            status = "Baseline trained and validation selection saved. Test set has not been evaluated."
        }
    }
    func test() {
        guard let current = experiment, current.test == nil, let output = resultURL else { return }
        run("Evaluating frozen model on held-out anatomy groups") { [self] in
            let result = try await Task.detached(priority: .userInitiated) {
                let saved = try JSONDecoder().decode(LearningExperiment.self, from: Data(contentsOf: output))
                guard try Canonical.hash(saved) == Canonical.hash(current) else { throw TPSError.invalid("Experiment changed on disk; test evaluation stopped.") }
                let targets = try current.cases.filter { current.partition.assignments[$0.id.uuidString] == "test" }.map(Self.load)
                let dictionary = current.model.structures.map { "\($0.id):\($0.name)" }.sorted()
                guard targets.allSatisfy({ $0.structures.map { "\($0.id):\($0.name)" }.sorted() == dictionary }) else { throw TPSError.invalid("Test label dictionary differs from training.") }
                var result = current
                result.test = try targets.map { try CaseEvaluation.contours(source: $0, prediction: current.model.predict($0), split: "test") }
                try Canonical.data(result).write(to: output, options: .atomic)
                return result
            }.value
            experiment = result; status = "Final test evaluation saved. Start a new documented experiment for further model changes."
        }
    }
    func exportReport() {
        guard let result = experiment else { return }
        let panel = NSSavePanel(); panel.nameFieldStringValue = "evaluation-report.json"
        guard panel.runModal() == .OK, let url = panel.url else { return }
        do {
            let report = try LearningReport(experiment: result)
            try Canonical.data(report).write(to: url, options: .atomic)
        } catch { self.error = error.localizedDescription }
    }
    func run(_ label: String, work: @escaping @MainActor () async throws -> Void) {
        guard !busy else { return }; busy = true; status = label
        Task { defer { busy = false }; do { try await work() } catch { self.error = error.localizedDescription; status = "Stopped · \(label)" } }
    }
}
