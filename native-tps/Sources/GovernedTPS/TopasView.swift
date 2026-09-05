import SwiftUI
import AppKit
import TPSCore

@MainActor final class TopasStore: ObservableObject {
    @Published var host = "spark-wired"
    @Published var source = "/home/armorbearer/nl-tps-autoseg/dosepred-mc/batch/VCT-PROSTATE-001"
    @Published var files = "fieldA.txt, fieldB.txt, xcat_materials_4tier.txt, combined_atn_1.bin"
    @Published var macros = "fieldA.txt, fieldB.txt"
    @Published var jobID = UserDefaults.standard.string(forKey: "topas.jobID") ?? ""
    @Published var state = "Not connected"
    @Published var details = ""
    @Published var parameters = ""
    @Published var log = ""
    @Published var reviewed = false
    @Published var busy = false
    @Published var error: String?
    private var manifestHash = ""
    private var preparedHost = ""
    private var preparedID = ""

    var currentJob: Bool { host == preparedHost && jobID == preparedID }
    var canSubmit: Bool { currentJob && reviewed && state == "prepared" }

    func request(_ action: String) {
        var request: [String: String] = ["action": action, "id": jobID]
        if action == "submit" {
            guard reviewed, host == preparedHost, jobID == preparedID, state == "prepared" else { return }
            request["manifestSHA256"] = manifestHash
        }
        var payload: [String: Any] = request
        if action == "prepare" {
            payload["source"] = source
            payload["files"] = files.split(separator: ",").map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            payload["macros"] = macros.split(separator: ",").map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            payload["worker"] = TopasBridge.source.data(using: .utf8)!.base64EncodedString()
        }
        do {
            let data = try JSONSerialization.data(withJSONObject: payload)
            let target = host
            busy = true; error = nil
            Task {
                defer { busy = false }
                do {
                    let response = try await Task.detached { try TopasBridge.call(host: target, payload: data) }.value
                    guard let result = try JSONSerialization.jsonObject(with: response) as? [String: Any] else { throw TPSError.invalid("Invalid Spark response") }
                    if action == "probe" {
                        details = String(data: try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys]), encoding: .utf8) ?? ""
                        state = "Connection checked"
                    } else {
                        jobID = result["id"] as? String ?? jobID
                        UserDefaults.standard.set(jobID, forKey: "topas.jobID")
                        state = result["state"] as? String ?? "Unknown"
                        log = result["log"] as? String ?? "No log yet"
                        manifestHash = result["manifestSHA256"] as? String ?? ""
                        preparedHost = target; preparedID = jobID; reviewed = false
                        let texts = result["parameters"] as? [String: String] ?? [:]
                        parameters = texts.keys.sorted().map { "// \($0)\n\(texts[$0]!)" }.joined(separator: "\n\n")
                        var evidence = result; evidence.removeValue(forKey: "log"); evidence.removeValue(forKey: "parameters")
                        details = String(data: try JSONSerialization.data(withJSONObject: evidence, options: [.prettyPrinted, .sortedKeys]), encoding: .utf8) ?? ""
                    }
                } catch { self.error = error.localizedDescription }
            }
        } catch { self.error = error.localizedDescription }
    }

    func download() {
        guard currentJob else { return }
        let panel = NSSavePanel(); panel.nameFieldStringValue = "topas-\(jobID).tar.gz"
        guard panel.runModal() == .OK, let url = panel.url else { return }
        let target = host
        do {
            let data = try JSONSerialization.data(withJSONObject: ["action": "fetch", "id": jobID])
            busy = true; error = nil
            Task {
                defer { busy = false }
                do {
                    let result = try await Task.detached { try TopasBridge.call(host: target, payload: data) }.value
                    try result.write(to: url, options: .atomic)
                    NSWorkspace.shared.activateFileViewerSelecting([url])
                } catch { self.error = error.localizedDescription }
            }
        } catch { self.error = error.localizedDescription }
    }
}

struct TopasView: View {
    @ObservedObject var simulation: TopasStore
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                SectionIntro(eyebrow: "Monte Carlo transport · DGX Spark", title: "OpenTOPAS", detail: "Prepare a private input snapshot, inspect its parameters, then submit a persistent simulation job.")
                Card(title: "Spark connection", subtitle: "Uses your Mac's SSH configuration and existing key authentication") {
                    TextField("SSH host alias", text: $simulation.host)
                    HStack {
                        Button("Check connection") { simulation.request("probe") }
                        Text(simulation.state).foregroundStyle(Theme.teal)
                        if simulation.busy { ProgressView().controlSize(.small) }
                    }
                }
                Card(title: "Prepare simulation", subtitle: "Copy only explicitly listed inputs into a new desktop-managed folder on Spark") {
                    TextField("Remote prepared input folder", text: $simulation.source)
                    TextField("Input filenames, comma separated", text: $simulation.files)
                    TextField("Ordered macro filenames, comma separated", text: $simulation.macros)
                    Button("Prepare input snapshot") { simulation.request("prepare") }.buttonStyle(.borderedProminent)
                    Text("The existing case-001 fields are exploratory transport inputs. Preparation does not run them. Use relative input paths; includes and data files must be listed.").font(.caption).foregroundStyle(Theme.muted)
                }
                Card(title: "Job & parameter review", subtitle: "Jobs continue on Spark when this app closes; restore a job by ID and refresh") {
                    TextField("Job UUID", text: $simulation.jobID)
                    HStack {
                        Button("Refresh job") { simulation.request("status") }.disabled(UUID(uuidString: simulation.jobID) == nil)
                        Button("Download results…") { simulation.download() }.disabled(!simulation.currentJob || !["completed", "failed", "interrupted"].contains(simulation.state))
                    }
                    if !simulation.parameters.isEmpty {
                        ScrollView { Text(simulation.parameters).font(.system(size: 11, design: .monospaced)).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading) }.frame(height: 240)
                        Toggle("I reviewed the snapshot parameters, histories, scoring and geometry for this research run", isOn: $simulation.reviewed)
                        Button("Submit reviewed simulation") { simulation.request("submit") }.buttonStyle(.borderedProminent)
                            .disabled(!simulation.canSubmit)
                    }
                }
                if !simulation.details.isEmpty {
                    Card(title: "Provenance", subtitle: "SHA-256 binds inputs, launcher, engine binary and worker; runtime dependencies are not frozen") {
                        ScrollView { Text(simulation.details).font(.system(size: 11, design: .monospaced)).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading) }.frame(height: 240)
                    }
                }
                if !simulation.log.isEmpty {
                    Card(title: "Transport log", subtitle: "Last 24 KB · refresh to update") {
                        ScrollView { Text(simulation.log).font(.system(size: 11, design: .monospaced)).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading) }.frame(height: 280)
                    }
                }
                Text("Results include raw scorer files and provenance. A successful process exit does not establish calibrated dose or CT alignment. Convert and validate a native CT case before importing it into the workspace. nBio scoring depends on the installed engine and reviewed macro; no biology results are fabricated.").font(.caption).foregroundStyle(Theme.amber)
                if let error = simulation.error { Text(error).foregroundStyle(Theme.amber).textSelection(.enabled) }
            }.padding(28).disabled(simulation.busy)
        }
    }
}

// The embedded bridge is generated from scripts/topas_jobs.py by generate_topas_bridge.py.
enum TopasBridge {
    static func call(host: String, payload: Data) throws -> Data {
        guard !host.isEmpty, host.first != "-", host.range(of: #"^[A-Za-z0-9_.@-]+$"#, options: .regularExpression) != nil else {
            throw TPSError.invalid("Use a configured SSH alias or hostname.")
        }
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: directory) }
        let output = directory.appendingPathComponent("stdout"), errors = directory.appendingPathComponent("stderr")
        FileManager.default.createFile(atPath: output.path, contents: nil)
        FileManager.default.createFile(atPath: errors.path, contents: nil)
        let out = try FileHandle(forWritingTo: output), err = try FileHandle(forWritingTo: errors)
        defer { try? out.close(); try? err.close() }
        let process = Process(), input = Pipe()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/ssh")
        let quoted = "'" + source.replacingOccurrences(of: "'", with: "'\\''") + "'"
        process.arguments = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=10", "-o", "ServerAliveCountMax=2", host, "python3 -c " + quoted]
        process.standardInput = input; process.standardOutput = out; process.standardError = err
        try process.run()
        try input.fileHandleForWriting.write(contentsOf: payload)
        try input.fileHandleForWriting.close()
        let watchdog = DispatchSource.makeTimerSource(queue: .global())
        watchdog.schedule(deadline: .now() + 120)
        watchdog.setEventHandler { if process.isRunning { process.terminate() } }
        watchdog.resume()
        defer { watchdog.cancel() }
        process.waitUntilExit()
        guard process.terminationStatus == 0 else {
            throw TPSError.invalid(String(data: try Data(contentsOf: errors), encoding: .utf8) ?? "SSH command failed")
        }
        return try Data(contentsOf: output)
    }
}
