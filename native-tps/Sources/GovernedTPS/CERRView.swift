import SwiftUI
import AppKit
import CryptoKit
import TPSCore

private struct CERRJob: Codable, Sendable {
    var requestHash: String
    var bridgeHash: String
    var matlab: String
    var library: String
}

@MainActor final class CERRStore: ObservableObject {
    @Published var matlab = "/Applications/MATLAB_R2025b.app/bin/matlab"
    @Published var library = "/Users/ericbrass/Documents/medical-physics-mbse/CERR/CERR-master"
    @Published var savedJobPath = ""
    @Published var useReference = false
    @Published var binWidthGy = 0.1
    @Published var comparisons: [CERRComparison] = []
    @Published var reviewed = false
    @Published var busy = false
    @Published var status = "Select a synthetic CT and dose proposal in Workspace, or choose its simulation reference dose here."
    @Published var error: String?
    @Published var jobURL: URL?
    @Published var request: CERRRequest?
    @Published var result: CERRReport?
    @Published var preview = ""
    @Published var log = ""
    private var job: CERRJob?

    private var jobRoot: URL {
        FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("GovernedTPS/cerr-jobs", isDirectory: true)
    }
    func prepare(source: PhantomCase?, dose: Volume?, description: String) {
        guard !busy else { return }
        guard let source, let dose else { error = "Select a CT case and an available dose."; return }
        let width = binWidthGy, matlabPath = matlab, libraryPath = library, root = jobRoot
        busy = true; error = nil; status = "Freezing CT, labels and dose…"
        Task {
            defer { busy = false }
            do {
                let (request, url, job) = try await Task.detached {
                    let request = try CERRRequest(source: source, dose: dose, doseDescription: description, binWidthGy: width)
                    guard FileManager.default.isExecutableFile(atPath: matlabPath),
                          FileManager.default.fileExists(atPath: libraryPath + "/CERR_core/Importing/initializeCERR.m") else {
                        throw TPSError.invalid("Choose installed MATLAB and a CERR root containing CERR_core.")
                    }
                    let url = root.appendingPathComponent(request.id.uuidString, isDirectory: true)
                    try FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
                    try Canonical.data(source).write(to: url.appendingPathComponent("source.json"), options: .atomic)
                    try Canonical.data(dose).write(to: url.appendingPathComponent("dose.json"), options: .atomic)
                    try Canonical.data(request).write(to: url.appendingPathComponent("request.json"), options: .atomic)
                    let bridge = Data(CERRScript.source.utf8)
                    try bridge.write(to: url.appendingPathComponent("tps_cerr_analyze.m"), options: .atomic)
                    let job = CERRJob(requestHash: try Canonical.hash(request), bridgeHash: Self.hash(bridge), matlab: matlabPath, library: libraryPath)
                    try Canonical.data(job).write(to: url.appendingPathComponent("job.json"), options: .atomic)
                    return (request, url, job)
                }.value
                self.job = job; jobURL = url; self.request = request; result = nil; comparisons = []; reviewed = false
                preview = "CT: \(source.name)\nDose: \(description)\nMATLAB: \(matlabPath)\nCERR: \(libraryPath)\n" + String(decoding: try Canonical.data(request), as: UTF8.self)
                log = ""; status = "Prepared. Review the frozen inputs before analysis."
            } catch { self.error = error.localizedDescription; status = "Preparation stopped." }
        }
    }
    static nonisolated func hash(_ data: Data) -> String {
        SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
    }
    private func verify() throws -> (URL, CERRJob, CERRRequest) {
        guard let url = jobURL, let job, let request else { throw TPSError.invalid("Prepare or open a CERR job first.") }
        guard Self.hash(try Data(contentsOf: url.appendingPathComponent("request.json"))) == job.requestHash,
              try Canonical.hash(request) == job.requestHash,
              Self.hash(try Data(contentsOf: url.appendingPathComponent("source.json"))) == request.sourceHash,
              Self.hash(try Data(contentsOf: url.appendingPathComponent("dose.json"))) == request.doseHash,
              Self.hash(try Data(contentsOf: url.appendingPathComponent("tps_cerr_analyze.m"))) == job.bridgeHash else {
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
            busy = true; error = nil; reviewed = false; status = "CERR is sampling dose and computing histograms on this Mac."
            Task {
                defer { busy = false; refreshLog() }
                do {
                    let code = try await Task.detached {
                        let process = Process()
                        process.executableURL = URL(fileURLWithPath: job.matlab)
                        process.currentDirectoryURL = url
                        func quote(_ text: String) -> String { "'" + text.replacingOccurrences(of: "'", with: "''") + "'" }
                        process.arguments = ["-batch", "addpath(\(quote(url.path))); tps_cerr_analyze(\(quote(url.path)),\(quote(job.library)));" ]
                        let logURL = url.appendingPathComponent("matlab.log")
                        FileManager.default.createFile(atPath: logURL.path, contents: nil)
                        let handle = try FileHandle(forWritingTo: logURL)
                        defer { try? handle.close() }
                        process.standardOutput = handle; process.standardError = handle; process.standardInput = FileHandle.nullDevice
                        try process.run(); process.waitUntilExit()
                        try Data("\(process.terminationStatus)".utf8).write(to: url.appendingPathComponent("exit-code.txt"), options: .atomic)
                        return process.terminationStatus
                    }.value
                    guard code == 0 else { throw TPSError.invalid("MATLAB exited with code \(code). Inspect the log. No analysis has been accepted.") }
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
        let (url, job, request) = try verify()
        let resultURL = url.appendingPathComponent("report.json")
        guard (try resultURL.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0) <= 10_000_000 else { throw TPSError.invalid("Result exceeds 10 MB.") }
        let output = try JSONDecoder().decode(CERRReport.self, from: Data(contentsOf: resultURL))
        guard output.evidence["bridgeSHA256"] == job.bridgeHash else { throw TPSError.invalid("Report was produced by a different CERR bridge.") }
        let source = try JSONDecoder().decode(PhantomCase.self, from: Data(contentsOf: url.appendingPathComponent("source.json")))
        let dose = try JSONDecoder().decode(Volume.self, from: Data(contentsOf: url.appendingPathComponent("dose.json")))
        comparisons = try output.compare(source: source, dose: dose, request: request)
        result = output; status = "Report verified. Compare CERR with native voxel statistics below."
    }
    func openLatestJob() {
        do {
            let folders = try FileManager.default.contentsOfDirectory(at: jobRoot, includingPropertiesForKeys: nil)
            let manifests = folders.map { $0.appendingPathComponent("job.json") }.filter { FileManager.default.fileExists(atPath: $0.path) }
            guard let latest = try manifests.sorted(by: {
                (try $0.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate ?? .distantPast) >
                (try $1.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate ?? .distantPast)
            }).first else { throw TPSError.invalid("No saved CERR jobs on this Mac.") }
            savedJobPath = latest.path; openJob()
        } catch { self.error = error.localizedDescription }
    }
    func openJob() {
        guard !busy else { return }
        do {
            let path = (savedJobPath.trimmingCharacters(in: .whitespacesAndNewlines) as NSString).expandingTildeInPath
            guard !path.isEmpty else { throw TPSError.invalid("Enter a saved CERR job folder or job.json path.") }
            let file = URL(fileURLWithPath: path)
            let url = file.lastPathComponent == "job.json" ? file.deletingLastPathComponent() : file
            let job = try JSONDecoder().decode(CERRJob.self, from: Data(contentsOf: url.appendingPathComponent("job.json")))
            let request = try JSONDecoder().decode(CERRRequest.self, from: Data(contentsOf: url.appendingPathComponent("request.json")))
            self.job = job; self.request = request; jobURL = url; result = nil; comparisons = []; reviewed = false
            _ = try verify()
            error = nil
            preview = String(decoding: try Canonical.data(request), as: UTF8.self)
            refreshLog(); status = "Job reopened."
            if FileManager.default.fileExists(atPath: url.appendingPathComponent("report.json").path) { try loadResult() }
        } catch { self.error = error.localizedDescription }
    }
}

struct CERRView: View {
    @ObservedObject var analysis: CERRStore
    @EnvironmentObject var app: AppStore
    private var dose: Volume? {
        if analysis.useReference { return app.source?.simulation?.referenceDose }
        guard app.selectedArtifact?.operation == .predictDose else { return nil }
        return app.selectedArtifact?.volume
    }
    private var description: String {
        analysis.useReference ? "Simulation reference dose" : "Proposal: \(app.selectedArtifact?.modelID ?? "none") · \(app.selectedArtifact?.id.uuidString ?? "")"
    }
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                SectionIntro(eyebrow: "Independent analysis · MATLAB on this Mac", title: "CERR", detail: "Compare CERR dose-volume sampling with native voxel statistics for the same frozen CT, structures and dose.")
                Card(title: "Local runtime", subtitle: "Isolated jobs using the installed CERR library") {
                    TextField("MATLAB executable", text: $analysis.matlab)
                    TextField("CERR root folder", text: $analysis.library)
                }.disabled(analysis.busy)
                Card(title: app.source?.name ?? "Select a case in Workspace", subtitle: "CT and truth labels · dose in Gy · no resampling") {
                    Picker("Dose source", selection: $analysis.useReference) {
                        Text("Selected workspace dose proposal").tag(false)
                        Text("Case simulation reference dose").tag(true)
                    }
                    Text(description).font(.caption).textSelection(.enabled)
                    if dose == nil { Text("This dose source is unavailable. Select a dose proposal in Workspace or a case with a reference dose.").foregroundStyle(Theme.amber) }
                    HStack { Text("Histogram bin width, Gy"); TextField("Gy", value: $analysis.binWidthGy, format: .number).frame(width: 90) }
                    Button("Prepare CT + labels + dose") { analysis.prepare(source: app.source, dose: dose, description: description) }
                        .buttonStyle(.borderedProminent).disabled(dose == nil)
                }.disabled(analysis.busy)
                Card(title: "Frozen analysis job", subtitle: "Input hashes, MATLAB log, planC.mat and portable report.json") {
                    HStack {
                        Button("Open latest analysis") { analysis.openLatestJob() }.disabled(analysis.busy)
                        Button("Show analysis files") { if let url = analysis.jobURL { NSWorkspace.shared.open(url) } }.disabled(analysis.jobURL == nil)
                        Button("Refresh analysis log") { analysis.refreshLog() }
                        if analysis.busy { ProgressView().controlSize(.small) }
                    }
                    HStack {
                        TextField("Saved CERR job folder or job.json path", text: $analysis.savedJobPath)
                        Button("Open saved path") { analysis.openJob() }.disabled(analysis.busy)
                    }
                    Text(analysis.status).foregroundStyle(Theme.teal)
                    if !analysis.preview.isEmpty {
                        Text(analysis.preview).font(.caption.monospaced()).textSelection(.enabled)
                        Toggle("I reviewed the frozen research CT, dose source and histogram settings", isOn: $analysis.reviewed).disabled(analysis.busy)
                        Button("Run CERR analysis") { analysis.run() }.buttonStyle(.borderedProminent).disabled(!analysis.reviewed || analysis.busy)
                    }
                    if let report = analysis.result, let request = analysis.request, let url = analysis.jobURL {
                        Button("Record analysis in audit trail") { app.recordCERR(report, request: request, jobURL: url) }.disabled(app.busy)
                        Text("CERR minus native · Gy for dose, cc for volume. Differences are observations, not a clinical acceptance test.").font(.caption)
                        Grid(alignment: .leading, horizontalSpacing: 16, verticalSpacing: 10) {
                            GridRow { Text("Structure"); Text("CERR mean"); Text("Δ mean"); Text("Δ D95"); Text("Δ volume"); Text("Max sample Δ") }.bold()
                            ForEach(analysis.comparisons) { row in
                                GridRow {
                                    Text(row.cerr.name)
                                    Text(row.cerr.meanGy, format: .number.precision(.fractionLength(5)))
                                    Text(row.cerr.meanGy-row.nativeMeanGy, format: .number.precision(.fractionLength(6)))
                                    Text(row.cerr.d95Gy-row.nativeD95Gy, format: .number.precision(.fractionLength(6)))
                                    Text(row.cerr.volumeCC-row.nativeVolumeCC, format: .number.precision(.fractionLength(6)))
                                    Text(row.cerr.maxSampleDifferenceGy, format: .number.precision(.fractionLength(6)))
                                }
                            }
                        }.font(.caption.monospaced()).textSelection(.enabled)
                        Text(report.evidence["sampling"] ?? "").font(.caption).foregroundStyle(Theme.muted)
                    }
                    if !analysis.log.isEmpty { ScrollView { Text(analysis.log).font(.caption.monospaced()).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading) }.frame(height: 160) }
                    if let error = analysis.error { Text(error).foregroundStyle(Theme.amber).textSelection(.enabled) }
                }
                Text("This bridge produces an analysis planC from native synthetic CT and exact label masks. Patient DICOM import, polygon editing, radiomics and outcome models are not wired into this workflow. CERR analysis does not recalculate dose or authorize treatment.").font(.caption).foregroundStyle(Theme.amber)
            }.padding(28)
        }
    }
}
