import SwiftUI
import AppKit
import TPSCore

struct WorkstationView: View {
    @EnvironmentObject var store: AppStore
    var body: some View {
        if let source = store.source {
            HStack(alignment: .top, spacing: 18) {
                ScrollView {
                    VStack(alignment: .leading, spacing: 18) {
                        HStack {
                            SectionIntro(eyebrow: "Image & inference workspace", title: source.name,
                                detail: "\(source.ct.grid.dimensions.map(String.init).joined(separator: " × ")) voxels  ·  \(source.ct.grid.spacing[0].formatted(.number.precision(.fractionLength(1)))) mm  ·  LPS coordinates")
                            Spacer()
                            Badge(text: "Synthetic")
                        }
                        HStack(spacing: 12) {
                            SlicePanel(source: source, artifact: store.selectedArtifact, axis: 2, slice: Int(store.slice), label: "AXIAL", center: store.windowCenter, width: store.windowWidth, opacity: store.overlayOpacity, showTruth: store.showTruth)
                            SlicePanel(source: source, artifact: store.selectedArtifact, axis: 1, slice: source.ct.grid.dimensions[1]/2, label: "CORONAL", center: store.windowCenter, width: store.windowWidth, opacity: store.overlayOpacity, showTruth: store.showTruth)
                            SlicePanel(source: source, artifact: store.selectedArtifact, axis: 0, slice: source.ct.grid.dimensions[0]/2, label: "SAGITTAL", center: store.windowCenter, width: store.windowWidth, opacity: store.overlayOpacity, showTruth: store.showTruth)
                        }
                        HStack {
                            Text("AXIAL SLICE").font(.system(size: 9, weight: .semibold, design: .monospaced)).foregroundStyle(Theme.muted)
                            Slider(value: $store.slice, in: 0...Double(source.ct.grid.dimensions[2]-1), step: 1)
                            Text("\(Int(store.slice)+1) / \(source.ct.grid.dimensions[2])").font(.system(size: 11, design: .monospaced)).frame(width: 66)
                        }
                        if let artifact = store.selectedArtifact {
                            HStack {
                                Image(systemName: "sparkles").foregroundStyle(Theme.amber)
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(artifact.operation.title+" · "+(artifact.isDemo ? "analytic fixture" : "local Core ML")).font(.system(size: 12, weight: .medium))
                                    Text("\(artifact.modelID) · \(store.workspace.latestReview(for: artifact)?.decision.rawValue ?? "Awaiting human research review")").font(.system(size: 10)).foregroundStyle(Theme.muted)
                                }
                                Spacer()
                                Button("Review result") { store.screen = .governance }.buttonStyle(.bordered)
                            }.padding(14).background(Theme.amber.opacity(0.07), in: RoundedRectangle(cornerRadius: 10))
                        }
                        if !store.dvhs.isEmpty { DVHChart(curves: store.dvhs) }
                        else {
                            Card(title: "Dose-volume analysis", subtitle: "Select a predicted dose result to calculate a cumulative DVH.") {
                                Text("Metrics are computed from the displayed dose grid and phantom truth labels. They are descriptive research measurements, not planning constraints or pass/fail criteria.")
                                    .font(.system(size: 12)).foregroundStyle(Theme.muted).lineSpacing(4)
                            }
                        }
                        HStack(spacing: 12) {
                            Card(title: "Geometry", subtitle: "Preserved across every result") {
                                Label("Exact grid + frame checks", systemImage: "checkmark.circle").font(.system(size: 12)).foregroundStyle(Theme.teal)
                                Text("No implicit resampling").font(.system(size: 11)).foregroundStyle(Theme.muted)
                            }
                            Card(title: "Source provenance", subtitle: "Generator identity") {
                                Text(source.generator).font(.system(size: 12))
                                if source.mr == nil {
                                    Text("CT only · no MR acquisition").font(.system(size: 12)).foregroundStyle(Theme.muted)
                                } else if let note = source.sourceNotes?["mr"] {
                                    Text("MR: \(note)").font(.system(size: 12)).foregroundStyle(.orange)
                                }
                                Text("nBio profile: \(source.recipe.nBioProfile)").font(.system(size: 11)).foregroundStyle(Theme.muted)
                            }
                        }
                    }.padding(24)
                }
                inspector(source).frame(width: 250).padding(.vertical, 24).padding(.trailing, 22)
            }
        } else {
            VStack(spacing: 24) {
                Image(systemName: "viewfinder.circle").font(.system(size: 70, weight: .ultraLight)).foregroundStyle(Theme.teal)
                Text("A governed space to build.").font(.system(size: 32, weight: .semibold))
                Text("Start with a reproducible synthetic phantom. Explore image-model outputs,\ninspect their provenance, and record a research review.")
                    .font(.system(size: 14)).foregroundStyle(Theme.muted).multilineTextAlignment(.center).lineSpacing(6)
                HStack(spacing: 14) {
                    Button("Create analytic phantom") { store.createPhantom() }.buttonStyle(.borderedProminent)
                    Button("Import synthetic case…") { store.importCase() }.buttonStyle(.bordered)
                }.controlSize(.large).disabled(store.busy)
                Text("XCAT2 / OpenTOPAS-nBio generation connects separately to your DGX Spark.").font(.system(size: 11)).foregroundStyle(Theme.muted)
            }.frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }
    func inspector(_ source: PhantomCase) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                VStack(alignment: .leading, spacing: 10) {
                    Text("CASE LIBRARY").font(.system(size: 10, weight: .bold)).tracking(1).foregroundStyle(Theme.muted)
                    Picker("Case", selection: $store.selectedCaseID) {
                        ForEach(store.workspace.cases) { item in Text(item.name).tag(Optional(item.id)) }
                    }.labelsHidden().disabled(store.busy)
                    .onChange(of: store.selectedCaseID) { _, _ in store.selectedArtifactID = nil; store.proposal = nil; store.slice = Double((store.source?.ct.grid.dimensions[2] ?? 64)/2) }
                }
                Divider()
                VStack(alignment: .leading, spacing: 12) {
                    Text("MODEL PREDICT").font(.system(size: 10, weight: .bold)).tracking(1).foregroundStyle(Theme.muted)
                    Picker("Execution", selection: $store.inferenceMode) { ForEach(InferenceMode.allCases) { Text($0.rawValue).tag($0) } }.labelsHidden().disabled(store.busy)
                    ForEach([TPSOperation.contour, .predictDose, .syntheticCT]) { operation in
                        Button { store.run(operation) } label: {
                            HStack { Image(systemName: operation == .contour ? "lasso" : operation == .predictDose ? "waveform.path" : "square.3.layers.3d"); Text(operation.title); Spacer(); Image(systemName: "arrow.up.right") }
                                .font(.system(size: 12)).padding(10).frame(maxWidth: .infinity)
                        }.buttonStyle(.bordered).disabled(store.busy || (operation == .syntheticCT && source.mr == nil))
                    }
                    Text(store.inferenceMode == .fixture ? "Fixture mode tests the pipeline. It does not run a trained AI model." : "Requires a checksum-pinned local model manifest.")
                        .font(.system(size: 11)).foregroundStyle(Theme.amber).lineSpacing(3)
                }
                Divider()
                VStack(alignment: .leading, spacing: 12) {
                    Text("DISPLAY").font(.system(size: 10, weight: .bold)).tracking(1).foregroundStyle(Theme.muted)
                    Toggle("Phantom truth outlines", isOn: $store.showTruth).font(.system(size: 11))
                    Text("Window width · \(Int(store.windowWidth)) HU").font(.system(size: 11)).foregroundStyle(Theme.muted)
                    Slider(value: $store.windowWidth, in: 100...2000)
                    Text("Window center · \(Int(store.windowCenter)) HU").font(.system(size: 11)).foregroundStyle(Theme.muted)
                    Slider(value: $store.windowCenter, in: -500...700)
                    Text("Proposal opacity").font(.system(size: 11)).foregroundStyle(Theme.muted)
                    Slider(value: $store.overlayOpacity, in: 0...1)
                }
                Divider()
                VStack(alignment: .leading, spacing: 10) {
                    Text("RESULTS / \(store.artifacts.count)").font(.system(size: 10, weight: .bold)).tracking(1).foregroundStyle(Theme.muted)
                    Button("Source CT only") { store.selectedArtifactID = nil }.font(.system(size: 11)).buttonStyle(.plain)
                    ForEach(store.artifacts.reversed()) { artifact in
                        Button { store.selectedArtifactID = artifact.id } label: {
                            HStack {
                                Circle().fill(store.workspace.latestReview(for: artifact)?.decision == .acceptedForResearch ? Theme.teal : Theme.amber).frame(width: 5, height: 5)
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(artifact.operation.title).font(.system(size: 11, weight: .medium))
                                    Text(artifact.isDemo ? "Analytic fixture" : artifact.modelID).font(.system(size: 9)).foregroundStyle(Theme.muted)
                                }
                                Spacer()
                            }.padding(10).background(store.selectedArtifactID == artifact.id ? Theme.raised : .clear, in: RoundedRectangle(cornerRadius: 8))
                        }.buttonStyle(.plain)
                    }
                }
            }
        }
    }
}

struct SlicePanel: View {
    let source: PhantomCase
    let artifact: Artifact?
    let axis: Int
    let slice: Int
    let label: String
    let center: Double
    let width: Double
    let opacity: Double
    let showTruth: Bool
    var body: some View {
        VStack(spacing: 0) {
            HStack { Text(isAxisAligned ? label : "VOXEL PLANE \(axis)"); Spacer(); Text(isAxisAligned ? "LPS" : "OBLIQUE").foregroundStyle(Theme.teal) }.font(.system(size: 9, weight: .medium, design: .monospaced)).tracking(1).padding(12)
            ZStack {
                if let image = render() { Image(decorative: image, scale: 1).resizable().interpolation(.none).aspectRatio(physicalAspect, contentMode: .fit) }
                if isAxisAligned {
                    VStack { Text(axis == 2 ? "A" : "S"); Spacer(); Text(axis == 2 ? "P" : "I") }.font(.system(size: 9, design: .monospaced)).foregroundStyle(Theme.teal).padding(6)
                    HStack { Text(axis == 0 ? "A" : "R"); Spacer(); Text(axis == 0 ? "P" : "L") }.font(.system(size: 9, design: .monospaced)).foregroundStyle(Theme.teal).padding(6)
                }
            }.aspectRatio(1, contentMode: .fit).padding(4)
            HStack { Text("\(slice + 1)"); Spacer(); Text(artifact?.operation == .syntheticCT ? "SCT PROPOSAL" : "CT / HU") }.font(.system(size: 8, design: .monospaced)).foregroundStyle(Theme.muted).padding(12)
        }.background(.black.opacity(0.55), in: RoundedRectangle(cornerRadius: 12)).overlay(RoundedRectangle(cornerRadius: 12).stroke(.white.opacity(0.08)))
    }
    var plane: (Int, Int) { axis == 2 ? (0,1) : axis == 1 ? (0,2) : (1,2) }
    var isAxisAligned: Bool { source.ct.grid.direction == [1,0,0,0,1,0,0,0,1] }
    var physicalAspect: Double { Double(source.ct.grid.dimensions[plane.0])*source.ct.grid.spacing[plane.0] / (Double(source.ct.grid.dimensions[plane.1])*source.ct.grid.spacing[plane.1]) }
    func render() -> CGImage? {
        let grid = source.ct.grid, w = grid.dimensions[plane.0], h = grid.dimensions[plane.1]
        var bytes = [UInt8](repeating: 255, count: w*h*4)
        let doseMax = max(artifact?.volume.values.max() ?? 1, 0.001)
        let dictionary = Dictionary(uniqueKeysWithValues: source.structures.map { ($0.id, $0.color) })
        let proposedDictionary = Dictionary(uniqueKeysWithValues: (artifact?.structures ?? []).map { ($0.id, $0.color) })
        func coordinates(_ x: Int, _ y: Int) -> [Int] {
            var result = [0,0,0]; result[axis] = min(max(slice,0),grid.dimensions[axis]-1)
            result[plane.0] = x; result[plane.1] = axis == 2 ? y : h-1-y
            return result
        }
        for y in 0..<h { for x in 0..<w {
            let p = coordinates(x,y), i = grid.index(p[0],p[1],p[2]), b = (y*w+x)*4
            let voxel = artifact?.operation == .syntheticCT ? artifact!.volume.values[i] : source.ct.values[i]
            let gray = min(max((Double(voxel)-center)/width+0.5,0),1)
            var rgb = [gray,gray,gray]
            if let artifact, artifact.operation == .predictDose {
                let t = Double(artifact.volume.values[i]/doseMax)
                if t > 0.04 {
                    let color = [min(1,t*2), max(0,1-abs(t-0.55)*2), max(0,1-t*2)]
                    let alpha = opacity * min(1,t*3)
                    rgb = (0..<3).map { rgb[$0]*(1-alpha)+color[$0]*alpha }
                }
            }
            if showTruth {
                let truthID = Int(source.truth.values[i])
                if truthID > 1, let color = dictionary[truthID] {
                    let neighbor = coordinates(min(x+1,w-1), min(y+1,h-1))
                    if source.truth.values[grid.index(neighbor[0],neighbor[1],neighbor[2])] != source.truth.values[i] { rgb = color }
                }
            }
            if let artifact, artifact.operation == .contour, let color = proposedDictionary[Int(artifact.volume.values[i])], (x+y)%4 < 2 {
                let q = coordinates(min(x+1,w-1),min(y+1,h-1))
                if artifact.volume.values[grid.index(q[0],q[1],q[2])] != artifact.volume.values[i] {
                    rgb = (0..<3).map { rgb[$0]*(1-opacity)+color[$0]*opacity }
                }
            }
            for channel in 0..<3 { bytes[b+channel] = UInt8(min(max(rgb[channel]*255,0),255)) }
        } }
        guard let provider = CGDataProvider(data: Data(bytes) as CFData) else { return nil }
        return CGImage(width: w, height: h, bitsPerComponent: 8, bitsPerPixel: 32, bytesPerRow: w*4,
            space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.last.rawValue), provider: provider, decode: nil, shouldInterpolate: false, intent: .defaultIntent)
    }
}

struct DVHChart: View {
    let curves: [DVH]
    var body: some View {
        Card(title: "Dose-volume histogram", subtitle: "Cumulative · phantom truth structures · research measurements") {
            HStack(alignment: .top, spacing: 16) {
                VStack {
                    Canvas { context, size in
                        let maximum = curves.flatMap(\.points).map(\.dose).max() ?? 1
                        for tick in 0...4 {
                            let y = size.height * Double(tick)/4
                            var line = Path(); line.move(to: CGPoint(x: 0,y: y)); line.addLine(to: CGPoint(x: size.width,y: y))
                            context.stroke(line, with: .color(.white.opacity(0.07)), style: StrokeStyle(lineWidth: 1, dash: [3,4]))
                        }
                        for curve in curves {
                            var path = Path()
                            for (index, point) in curve.points.enumerated() {
                                let p = CGPoint(x: point.dose/maximum*size.width, y: (1-point.volumePercent/100)*size.height)
                                if index == 0 { path.move(to: p) } else { path.addLine(to: p) }
                            }
                            context.stroke(path, with: .color(Color(red: curve.color[0],green: curve.color[1],blue: curve.color[2])), lineWidth: 2)
                        }
                    }.frame(height: 160)
                    HStack { Text("0 Gy"); Spacer(); Text("Dose (Gy)"); Spacer(); Text("\((curves.first?.points.last?.dose ?? 0).formatted(.number.precision(.fractionLength(1)))) Gy") }.font(.system(size: 9, design: .monospaced)).foregroundStyle(Theme.muted)
                }
                VStack(alignment: .leading, spacing: 12) {
                    Text("MEAN / D95 (Gy)").font(.system(size: 8, design: .monospaced)).foregroundStyle(Theme.muted)
                    ForEach(curves) { curve in
                        VStack(alignment: .leading, spacing: 4) {
                            Text(curve.name).font(.system(size: 10, weight: .medium)).foregroundStyle(Color(red: curve.color[0],green: curve.color[1],blue: curve.color[2]))
                            Text("\(curve.meanGy.formatted(.number.precision(.fractionLength(1)))) / \(curve.d95Gy.formatted(.number.precision(.fractionLength(1))))").font(.system(size: 10, design: .monospaced))
                        }
                    }
                }.frame(width: 130, alignment: .leading)
            }
        }
    }
}
