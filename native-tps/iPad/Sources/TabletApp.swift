import SwiftUI
import TPSCore

@main struct GovernedTPSiPadApp: App {
    @StateObject private var store = TabletStore()
    var body: some Scene {
        WindowGroup { TabletRoot(store: store).preferredColorScheme(.dark) }
    }
}

struct TabletRoot: View {
    @ObservedObject var store: TabletStore
    @Environment(\.scenePhase) var scenePhase
    @State private var importing = false
    @State private var exporting = false
    @State private var document: ReviewDocument?
    @State private var tab = "Images"
    private let navy = Color(red: 0.035, green: 0.065, blue: 0.10)
    var body: some View {
        NavigationStack {
            VStack(spacing: 18) {
                header
                if let source = store.source {
                    Picker("Workspace", selection: $tab) {
                        Label("Images", systemImage: "square.stack.3d.up").tag("Images")
                        Label("Review", systemImage: "checklist").tag("Review")
                        Label("Handoff", systemImage: "square.and.arrow.up").tag("Handoff")
                    }.pickerStyle(.segmented)
                    if tab == "Images" { imageWorkspace(source) }
                    else if tab == "Review" { reviewWorkspace(source) }
                    else { handoffWorkspace(source) }
                } else { welcome }
                HStack {
                    if store.busy { ProgressView() }
                    Text(store.status).font(.caption)
                    Spacer()
                    Label("Research only", systemImage: "lock.shield").font(.caption)
                }.foregroundStyle(.secondary)
            }.padding(22).background(navy)
            .toolbar(.hidden, for: .navigationBar)
            .fileImporter(isPresented: $importing, allowedContentTypes: [.json]) { result in
                switch result {
                case .success(let url): Task { await store.load(url) }
                case .failure(let error): store.error = error.localizedDescription
                }
            }
            .fileExporter(isPresented: $exporting, document: document, contentType: .json, defaultFilename: "tablet-review-\(store.source?.name ?? "case")") { result in
                if case .failure(let error) = result { store.error = error.localizedDescription }
            }
            .alert("Action could not complete", isPresented: Binding(get: { store.error != nil }, set: { if !$0 { store.error = nil } })) {
                Button("OK") { store.error = nil }
            } message: { Text(store.error ?? "") }
            .task { await store.restore() }
            .onChange(of: scenePhase) { _, phase in
                if phase != .active { do { store.stashDrawing(); try store.saveNow() } catch { store.error = error.localizedDescription } }
            }
        }.tint(.mint)
    }
    var header: some View {
        HStack {
            Image(systemName: "scope").font(.largeTitle).foregroundStyle(.mint)
            VStack(alignment: .leading, spacing: 3) {
                Text("TPS  /  FIELD REVIEW").font(.caption.monospaced().bold()).tracking(2)
                Text(store.source?.name ?? "A closer look. Anywhere.").font(.title2.bold()).lineLimit(1)
            }
            Spacer()
            Button { importing = true } label: { Label("Import CT case", systemImage: "square.and.arrow.down") }
                .buttonStyle(.bordered).controlSize(.large).disabled(store.busy)
        }
    }
    var welcome: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 28) {
                Image(systemName: "hand.draw").font(.system(size: 65, weight: .ultraLight)).foregroundStyle(.mint).padding(.top, 45)
                Text("Bring the case.\nLeave room for the conversation.").font(.system(size: 42, weight: .semibold, design: .rounded))
                Text("CT review designed for your hands, your Pencil, and the space beyond the workstation.").font(.title3).foregroundStyle(.secondary)
                feature("Mark what matters", "Draw directly on a CT slice with Apple Pencil. Every mark stays attached to its source and slice.", "pencil.tip.crop.circle")
                feature("Review without a connection", "Carry one synthetic case offline, inspect labels and transport dose, and keep your observations on the iPad.", "wifi.slash")
                feature("Return a focused handoff", "Export slice markup, your checklist and notes, bound to the original case hash.", "arrow.up.doc")
                Button("Explore a CT demonstration") { Task { await store.demo() } }.buttonStyle(.borderedProminent).controlSize(.large).disabled(store.busy)
                Text("Import native case JSON through Files. Demonstration anatomy is analytic, not XCAT2. AI inference remains on the Mac; phantom generation remains on DGX Spark.").font(.footnote).foregroundStyle(.secondary)
            }.frame(maxWidth: 850, alignment: .leading).frame(maxWidth: .infinity)
        }
    }
    func feature(_ title: String, _ detail: String, _ icon: String) -> some View {
        HStack(alignment: .top, spacing: 16) {
            Image(systemName: icon).font(.title2).foregroundStyle(.mint).frame(width: 32)
            VStack(alignment: .leading, spacing: 5) { Text(title).font(.headline); Text(detail).foregroundStyle(.secondary) }
        }
    }
    func imageWorkspace(_ source: PhantomCase) -> some View {
        VStack(spacing: 14) {
            HStack {
                Picker("Voxel plane", selection: Binding(get: { store.axis }, set: { store.move(axis: $0) })) {
                    Text("XY").tag(2); Text("XZ").tag(1); Text("YZ").tag(0)
                }.pickerStyle(.segmented).frame(maxWidth: 260)
                Spacer()
                Picker("Overlay", selection: $store.overlay) {
                    Text("CT").tag("CT"); Text("Labels").tag("Labels")
                    if source.simulation != nil { Text("Dose").tag("Dose") }
                }.pickerStyle(.segmented).frame(maxWidth: 300)
            }
            CTCanvas(store: store, source: source).frame(minHeight: 250)
            HStack {
                Button { store.move(slice: max(store.slice-1,0)) } label: { Image(systemName: "chevron.left").frame(width: 32,height: 32) }
                Slider(value: Binding(get: { store.slice }, set: { store.move(slice: $0) }), in: 0...Double(source.ct.grid.dimensions[store.axis]-1), step: 1).accessibilityLabel("CT slice")
                Button { store.move(slice: min(store.slice+1,Double(source.ct.grid.dimensions[store.axis]-1))) } label: { Image(systemName: "chevron.right").frame(width: 32,height: 32) }
            }
            ViewThatFits(in: .horizontal) {
                HStack { inkTools; Spacer(); windows }
                VStack { inkTools; windows }
            }
            if store.overlay == "Dose" { Text("Transport reference dose · fixed scale 0–80 Gy · \(source.simulation?.normalization ?? "")").font(.caption).foregroundStyle(.secondary).lineLimit(3) }
            else { Text("Voxel planes preserve stored geometry. Markup is a review observation, not an edited contour or treatment approval.").font(.caption).foregroundStyle(.secondary) }
        }.disabled(store.busy)
    }
    var inkTools: some View {
        HStack {
            Toggle(isOn: $store.markup) { Label("Mark up", systemImage: "pencil.tip") }.toggleStyle(.button)
            if store.markup {
                Toggle("Finger ink", isOn: $store.fingerInk).toggleStyle(.button)
                Button("Undo stroke") {
                    var strokes = store.drawing.strokes
                    if !strokes.isEmpty { strokes.removeLast(); store.drawing = .init(strokes: strokes); store.stashDrawing() }
                }.disabled(store.drawing.strokes.isEmpty)
            }
        }.buttonStyle(.bordered).controlSize(.large)
    }
    var windows: some View {
        HStack {
            Text("Window").font(.caption).foregroundStyle(.secondary)
            Button("Soft tissue") { store.windowCenter = 40; store.windowWidth = 500 }
            Button("Bone") { store.windowCenter = 400; store.windowWidth = 1800 }
        }.buttonStyle(.bordered).controlSize(.large)
    }
    func reviewWorkspace(_ source: PhantomCase) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                Text("A review you can carry.").font(.largeTitle.bold())
                Text("Record observations during a case discussion. Checkmarks document your inspection; they do not approve a plan.").foregroundStyle(.secondary)
                ForEach(TabletReview.checklist, id: \.self) { item in
                    Toggle(item, isOn: Binding(get: { store.review?.checked.contains(item) ?? false }, set: { checked in
                        if checked { store.review?.checked.insert(item) } else { store.review?.checked.remove(item) }; store.scheduleSave()
                    })).padding(18).background(.white.opacity(0.05), in: RoundedRectangle(cornerRadius: 16))
                    .disabled(item == "Dose provenance inspected" && source.simulation == nil)
                }
                TextField("Reviewer name (local attribution)", text: Binding(get: { store.review?.reviewer ?? "" }, set: { store.review?.reviewer = $0; store.scheduleSave() })).textFieldStyle(.roundedBorder)
                Text("Observations").font(.headline)
                TextEditor(text: Binding(get: { store.review?.note ?? "" }, set: { store.review?.note = $0; store.scheduleSave() })).frame(minHeight: 160).padding(8).background(.white.opacity(0.05), in: RoundedRectangle(cornerRadius: 14))
                Text("\(store.review?.drawings.count ?? 0) slices with Pencil markup · saved on this iPad").foregroundStyle(.mint)
                Text(source.generator).font(.footnote).foregroundStyle(.secondary)
            }.frame(maxWidth: 850).frame(maxWidth: .infinity)
        }.disabled(store.busy)
    }
    func handoffWorkspace(_ source: PhantomCase) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                Image(systemName: "arrow.up.doc").font(.system(size: 55, weight: .light)).foregroundStyle(.mint)
                Text("Return the observations.").font(.largeTitle.bold())
                Text("Export a compact review JSON through Files, then share it from Files using AirDrop or your chosen destination.").font(.title3)
                feature("Bound to this case", "Includes source hash, case identifier, slice coordinates, Pencil data, checklist and notes. CT voxels are not duplicated.", "link")
                feature("Keep the compute where it belongs", "Mac: image models and local LLMs. DGX Spark: XCAT2 and OpenTOPAS/nBio. iPad: touch review and observations.", "desktopcomputer")
                Button("Export review handoff") {
                    do { document = try store.export(); exporting = true } catch { store.error = error.localizedDescription }
                }.buttonStyle(.borderedProminent).controlSize(.large)
                Text("Desktop ingestion of this new tablet-review format is a next integration step. This export is not a signed approval, RTSTRUCT or treatment plan.").font(.footnote).foregroundStyle(.secondary)
            }.frame(maxWidth: 850, alignment: .leading).frame(maxWidth: .infinity).padding(.top, 30)
        }.disabled(store.busy)
    }
}
