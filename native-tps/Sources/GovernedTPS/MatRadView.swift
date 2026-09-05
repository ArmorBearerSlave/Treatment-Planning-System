import SwiftUI
import AppKit
import CryptoKit
import TPSCore

private struct MatRadJob: Codable, Sendable {
    var requestHash: String
    var bridgeHash: String
    var matlab: String
    var library: String
}

@MainActor final class MatRadStore: ObservableObject {
    @Published var matlab = "/Applications/MATLAB_R2025b.app/bin/matlab"
    @Published var library = "/Users/ericbrass/Documents/GitHub/matRad"
    @Published var targetID = 0
    @Published var dose = 2.0
    @Published var fractions = 1
    @Published var targetPenalty = 100.0
    @Published var angles = "0, 90, 180, 270"
    @Published var bixelWidth = 10.0
    @Published var organs: [MatRadObjective] = []
    @Published var reviewed = false
    @Published var busy = false
    @Published var status = "Select a synthetic CT case in Workspace, then choose its target here."
    @Published var error: String?
    @Published var jobURL: URL?
    @Published var request: MatRadRequest?
    @Published var result: MatRadResult?
    @Published var preview = ""
    @Published var log = ""
    private var job: MatRadJob?
    private var objectiveCaseID: UUID?

    private var jobRoot: URL {
        FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("GovernedTPS/matrad-jobs", isDirectory: true)
    }
    func resetObjectives(source: PhantomCase?) {
        objectiveCaseID = source?.id
        targetID = 0; organs = source?.structures.map { MatRadObjective(id: $0.id) } ?? []
    }
    func syncObjectives(source: PhantomCase?) {
        if objectiveCaseID != source?.id { resetObjectives(source: source) }
    }
    func prepare(source: PhantomCase?) {
        guard !busy else { return }
        guard let source else { error = "Choose a source CT in Workspace."; return }
        var settings = MatRadSettings(targetID: targetID)
        settings.targetGy = dose; settings.fractions = fractions; settings.targetPenalty = targetPenalty
        let parts = angles.split(separator: ",", omittingEmptySubsequences: false).map { $0.trimmingCharacters(in: .whitespaces) }
        let numbers = parts.compactMap(Double.init)
        guard numbers.count == parts.count else { error = "Angles must be a comma-separated list of numbers."; return }
        settings.gantryAngles = numbers; settings.bixelWidthMM = bixelWidth
        settings.organs = organs.filter { $0.id != targetID }
        let frozenSettings = settings, matlabPath = matlab, libraryPath = library, root = jobRoot
        busy = true; error = nil; status = "Validating and copying the CT snapshot…"
        Task {
            defer { busy = false }
            do {
                let (request, url, job) = try await Task.detached {
                    let request = try MatRadRequest(source: source, settings: frozenSettings)
                    guard FileManager.default.isExecutableFile(atPath: matlabPath),
                          FileManager.default.fileExists(atPath: libraryPath + "/matRad_rc.m") else {
                        throw TPSError.invalid("Choose an installed MATLAB executable and a matRad root containing matRad_rc.m.")
                    }
                    let url = root.appendingPathComponent(request.id.uuidString, isDirectory: true)
                    try FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
                    try Canonical.data(source).write(to: url.appendingPathComponent("source.json"), options: .atomic)
                    try Canonical.data(request).write(to: url.appendingPathComponent("request.json"), options: .atomic)
                    let bridge = Data(MatRadScript.source.utf8)
                    try bridge.write(to: url.appendingPathComponent("tps_matrad_run.m"), options: .atomic)
                    let job = MatRadJob(requestHash: try Canonical.hash(request), bridgeHash: Self.hash(bridge), matlab: matlabPath, library: libraryPath)
                    try Canonical.data(job).write(to: url.appendingPathComponent("job.json"), options: .atomic)
                    return (request, url, job)
                }.value
                self.job = job; jobURL = url; self.request = request; result = nil; reviewed = false
                preview = "Source: \(source.name)\nMATLAB: \(matlabPath)\nmatRad: \(libraryPath)\n" + String(decoding: try Canonical.data(request), as: UTF8.self)
                log = ""; status = "Prepared. Review frozen parameters before starting MATLAB."
            } catch { self.error = error.localizedDescription; status = "Preparation stopped." }
        }
    }
    static nonisolated func hash(_ data: Data) -> String {
        SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
    }
    private func verify() throws -> (URL, MatRadJob, MatRadRequest) {
        guard let url = jobURL, let job, let request else { throw TPSError.invalid("Prepare or open a matRad job first.") }
        guard Self.hash(try Data(contentsOf: url.appendingPathComponent("request.json"))) == job.requestHash,
              try Canonical.hash(request) == job.requestHash,
              Self.hash(try Data(contentsOf: url.appendingPathComponent("source.json"))) == request.sourceHash,
              Self.hash(try Data(contentsOf: url.appendingPathComponent("tps_matrad_run.m"))) == job.bridgeHash else {
            throw TPSError.invalid("The frozen request, source or bridge changed. Prepare a new job.")
        }
        return (url, job, request)
    }
    func run() {
        guard reviewed, !busy else { return }
        do {
            let (url, job, _) = try verify()
            let marker = url.appendingPathComponent("submitted.txt")
            guard !FileManager.default.fileExists(atPath: marker.path) else { throw TPSError.invalid("Job already submitted. Load its result or prepare a new job.") }
            try Data(Date().description.utf8).write(to: marker, options: .withoutOverwriting)
            busy = true; error = nil; reviewed = false; status = "MATLAB is calculating dose and optimizing fluence on this Mac."
            Task {
                defer { busy = false; refreshLog() }
                do {
                    let code = try await Task.detached {
                        let process = Process()
                        process.executableURL = URL(fileURLWithPath: job.matlab)
                        process.currentDirectoryURL = url
                        func quote(_ text: String) -> String { "'" + text.replacingOccurrences(of: "'", with: "''") + "'" }
                        process.arguments = ["-batch", "addpath(\(quote(url.path))); tps_matrad_run(\(quote(url.path)),\(quote(job.library)));" ]
                        let logURL = url.appendingPathComponent("matlab.log")
                        FileManager.default.createFile(atPath: logURL.path, contents: nil)
                        let handle = try FileHandle(forWritingTo: logURL)
                        defer { try? handle.close() }
                        process.standardOutput = handle; process.standardError = handle; process.standardInput = FileHandle.nullDevice
                        try process.run(); process.waitUntilExit()
                        try Data("\(process.terminationStatus)".utf8).write(to: url.appendingPathComponent("exit-code.txt"), options: .atomic)
                        return process.terminationStatus
                    }.value
                    guard code == 0 else { throw TPSError.invalid("MATLAB exited with code \(code). Inspect the log. No dose has been imported.") }
                    try loadResult()
                } catch { self.error = error.localizedDescription; status = "Run stopped; job files preserved." }
            }
        } catch { self.error = error.localizedDescription }
    }
    func refreshLog() {
        guard let url = jobURL?.appendingPathComponent("matlab.log"), let handle = try? FileHandle(forReadingFrom: url) else { return }
        defer { try? handle.close() }
        do {
            let length = try handle.seekToEnd(); try handle.seek(toOffset: length > 24000 ? length-24000 : 0)
            log = String(decoding: try handle.readToEnd() ?? Data(), as: UTF8.self)
        } catch { self.error = error.localizedDescription }
    }
    func loadResult() throws {
        let (url, _, request) = try verify()
        let resultURL = url.appendingPathComponent("result.json")
        guard (try resultURL.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0) <= 160_000_000 else { throw TPSError.invalid("Result exceeds 160 MB.") }
        let output = try JSONDecoder().decode(MatRadResult.self, from: Data(contentsOf: resultURL))
        let source = try JSONDecoder().decode(PhantomCase.self, from: Data(contentsOf: url.appendingPathComponent("source.json")))
        _ = try output.artifact(source: source, request: request)
        result = output; status = "Optimization result verified. Import as a proposal for workspace review."
    }
    func openJob() {
        let panel = NSOpenPanel(); panel.canChooseFiles = false; panel.canChooseDirectories = true
        panel.message = "Choose a desktop matRad job folder containing job.json and request.json."
        guard panel.runModal() == .OK, let url = panel.url else { return }
        do {
            let job = try JSONDecoder().decode(MatRadJob.self, from: Data(contentsOf: url.appendingPathComponent("job.json")))
            let request = try JSONDecoder().decode(MatRadRequest.self, from: Data(contentsOf: url.appendingPathComponent("request.json")))
            self.job = job; self.request = request; jobURL = url; result = nil; reviewed = false
            _ = try verify()
            preview = String(decoding: try Canonical.data(request), as: UTF8.self)
            refreshLog(); status = "Job reopened."
            if FileManager.default.fileExists(atPath: url.appendingPathComponent("result.json").path) { try loadResult() }
        } catch { self.error = error.localizedDescription }
    }
}

struct MatRadView: View {
    @ObservedObject var planning: MatRadStore
    @EnvironmentObject var app: AppStore
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                SectionIntro(eyebrow: "Inverse planning · MATLAB on this Mac", title: "matRad", detail: "Calculate photon dose and optimize fluence against explicit objectives, then inspect the result in the CT workspace.")
                Card(title: "Local runtime", subtitle: "Uses the installed matRad library and MATLAB license") {
                    TextField("MATLAB executable", text: $planning.matlab)
                    TextField("matRad root folder", text: $planning.library)
                }.disabled(planning.busy)
                Card(title: app.source?.name ?? "Select a case in Workspace", subtitle: "Generic photon machine · physical course dose · nominal geometry · no sequencing") {
                    Picker("Target label", selection: $planning.targetID) {
                        Text("Choose target").tag(0)
                        ForEach(app.source?.structures ?? []) { Text($0.name).tag($0.id) }
                    }
                    HStack {
                        Text("Target course Gy"); TextField("Gy", value: $planning.dose, format: .number).frame(width: 65)
                        Stepper("\(planning.fractions) fractions", value: $planning.fractions, in: 1...50)
                        Text("Target penalty"); TextField("Weight", value: $planning.targetPenalty, format: .number).frame(width: 70)
                    }
                    TextField("Gantry angles in degrees, comma separated", text: $planning.angles)
                    HStack { Text("Bixel width, mm"); TextField("mm", value: $planning.bixelWidth, format: .number).frame(width: 75) }
                    Text("Organ objectives: squared overdose above each course-dose ceiling. A zero penalty disables that objective. These initial research values are not prescribed constraints.").font(.caption).foregroundStyle(Theme.muted)
                    ForEach(planning.organs.indices, id: \.self) { index in
                        if planning.organs[index].id != planning.targetID {
                            HStack {
                                Text(app.source?.structures.first(where: { $0.id == planning.organs[index].id })?.name ?? "Label \(planning.organs[index].id)").frame(width: 160, alignment: .leading)
                                Text("Ceiling Gy"); TextField("Gy", value: $planning.organs[index].ceilingGy, format: .number).frame(width: 70)
                                Text("Penalty"); TextField("Weight", value: $planning.organs[index].penalty, format: .number).frame(width: 70)
                            }
                        }
                    }
                    Button("Prepare selected CT + objectives") { planning.prepare(source: app.source) }.buttonStyle(.borderedProminent)
                }.disabled(planning.busy)
                Card(title: "Frozen planning job", subtitle: "Preparation binds the source CT and labels, objectives and adapter to hashes") {
                    HStack {
                        Button("Open job…") { planning.openJob() }.disabled(planning.busy)
                        Button("Show job files") { if let url = planning.jobURL { NSWorkspace.shared.open(url) } }.disabled(planning.jobURL == nil)
                        Button("Refresh log") { planning.refreshLog() }
                        if planning.busy { ProgressView().controlSize(.small) }
                    }
                    Text(planning.status).foregroundStyle(Theme.teal)
                    if !planning.preview.isEmpty {
                        Text(planning.preview).font(.caption.monospaced()).textSelection(.enabled)
                        Toggle("I reviewed the frozen research objectives, generic machine and CT/label geometry", isOn: $planning.reviewed).disabled(planning.busy)
                        Button("Run dose calculation + optimization") { planning.run() }.disabled(!planning.reviewed || planning.busy).buttonStyle(.borderedProminent)
                    }
                    if let output = planning.result, let request = planning.request {
                        Text("Physical course dose · peak \(Double(output.volume.values.max() ?? 0).formatted()) Gy · \(output.evidence["optimizer"] ?? "")")
                        Text(output.evidence["optimizerInfo"] ?? "").font(.caption.monospaced()).textSelection(.enabled)
                        Button("Import dose proposal into Workspace") { app.importMatRad(output, request: request, jobURL: planning.jobURL) }.disabled(app.busy)
                    }
                    if !planning.log.isEmpty { ScrollView { Text(planning.log).font(.caption.monospaced()).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading) }.frame(height: 260) }
                    if let error = planning.error { Text(error).foregroundStyle(Theme.amber).textSelection(.enabled) }
                }
                Text("matRad returns a research plan proposal, not a trained inference result or OpenTOPAS reference. Generic machine and default HU calibration are uncommissioned. CT axes are preserved; oblique grids are rejected. No MR or biological effect is generated.").font(.caption).foregroundStyle(Theme.amber)
            }.padding(28)
        }
        .onAppear { planning.syncObjectives(source: app.source) }
        .onChange(of: app.selectedCaseID) { _, _ in planning.resetObjectives(source: app.source) }
    }
}
