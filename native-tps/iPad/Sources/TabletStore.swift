import SwiftUI
import PencilKit
import UniformTypeIdentifiers
import TPSCore

@MainActor final class TabletStore: ObservableObject {
    @Published var source: PhantomCase?
    @Published var review: TabletReview?
    @Published var busy = false
    @Published var status = "Ready for a case"
    @Published var error: String?
    @Published var axis = 2
    @Published var slice = 0.0
    @Published var windowCenter = 40.0
    @Published var windowWidth = 500.0
    @Published var overlay = "Labels"
    @Published var drawing = PKDrawing()
    @Published var markup = false
    @Published var fingerInk = false
    private var saveTask: Task<Void, Never>?
    private let directory = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    var key: String { "\(axis):\(Int(slice))" }
    var sourceURL: URL { directory.appendingPathComponent("active-case.json") }
    var reviewURL: URL { directory.appendingPathComponent("tablet-review.json") }

    func restore() async {
        guard source == nil, !busy else { return }
        if FileManager.default.fileExists(atPath: sourceURL.path) { await load(sourceURL, restoring: true) }
    }
    func load(_ url: URL, restoring: Bool = false) async {
        guard !busy else { return }
        busy = true; status = "Validating CT and provenance…"
        defer { busy = false }
        let destination = sourceURL, notes = reviewURL
        do {
            try saveNow()
            let (value, packet) = try await Task.detached(priority: .userInitiated) {
                let access = url.startAccessingSecurityScopedResource()
                defer { if access { url.stopAccessingSecurityScopedResource() } }
                guard (try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0) <= 96_000_000 else { throw TPSError.invalid("Native case limit is 96 MB.") }
                let bytes = try Data(contentsOf: url)
                let value = try JSONDecoder().decode(PhantomCase.self, from: bytes)
                try value.validate()
                let hash = try Canonical.hash(value)
                var packet = TabletReview(sourceHash: hash, caseID: value.id, caseName: value.name)
                if FileManager.default.fileExists(atPath: notes.path) {
                    let saved = try JSONDecoder().decode(TabletReview.self, from: Data(contentsOf: notes))
                    if saved.sourceHash == hash { try saved.validate(source: value); packet = saved }
                    else if !restoring {
                        let archive = notes.deletingLastPathComponent().appendingPathComponent("review-\(saved.caseID)-\(UUID()).json")
                        try Data(contentsOf: notes).write(to: archive, options: .atomic)
                    }
                }
                if !restoring { try bytes.write(to: destination, options: [.atomic, .completeFileProtection]) }
                return (value, packet)
            }.value
            source = value; review = packet; axis = 2; slice = Double(value.ct.grid.dimensions[2] / 2)
            markup = false; loadDrawing(); try saveNow(); status = "Available offline · CT verified"
        } catch { self.error = error.localizedDescription; status = "Import stopped" }
    }
    func demo() async {
        guard !busy else { return }
        busy = true; status = "Preparing CT demonstration…"
        do {
            let value = try await Task.detached { () -> PhantomCase in
                var result = try PhantomFactory.analytic(PhantomRecipe(anatomyID: "TABLET-DEMO"), size: 64)
                result.mr = nil
                return result
            }.value
            let url = FileManager.default.temporaryDirectory.appendingPathComponent("tablet-demo.json")
            try await Task.detached { try Canonical.data(value).write(to: url, options: .atomic) }.value
            busy = false; await load(url)
        } catch { self.error = error.localizedDescription; busy = false }
    }
    func move(axis: Int? = nil, slice: Double? = nil) {
        stashDrawing()
        if let axis { self.axis = axis; self.slice = Double((source?.ct.grid.dimensions[axis] ?? 2) / 2) }
        if let slice { self.slice = slice }
        loadDrawing()
    }
    func stashDrawing() {
        guard review != nil else { return }
        if drawing.strokes.isEmpty { review?.drawings.removeValue(forKey: key) }
        else { review?.drawings[key] = drawing.dataRepresentation() }
        scheduleSave()
    }
    private func loadDrawing() {
        if let bytes = review?.drawings[key] { drawing = (try? PKDrawing(data: bytes)) ?? PKDrawing() }
        else { drawing = PKDrawing() }
    }
    func scheduleSave() {
        review?.updatedAt = Date()
        saveTask?.cancel()
        saveTask = Task {
            do { try await Task.sleep(for: .milliseconds(400)); try saveNow() }
            catch is CancellationError {} catch { self.error = error.localizedDescription }
        }
    }
    func saveNow() throws {
        saveTask?.cancel()
        guard let review else { return }
        try Canonical.data(review).write(to: reviewURL, options: [.atomic, .completeFileProtection])
    }
    func export() throws -> ReviewDocument {
        stashDrawing(); try saveNow()
        guard let review, let source else { throw TPSError.invalid("Import a case first.") }
        try review.validate(source: source)
        return ReviewDocument(data: try Canonical.data(review))
    }
}

struct ReviewDocument: FileDocument {
    static var readableContentTypes: [UTType] { [.json] }
    var data: Data
    init(data: Data) { self.data = data }
    init(configuration: ReadConfiguration) throws { data = configuration.file.regularFileContents ?? Data() }
    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper { FileWrapper(regularFileWithContents: data) }
}
