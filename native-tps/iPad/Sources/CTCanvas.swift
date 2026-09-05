import SwiftUI
import PencilKit
import TPSCore

struct CTCanvas: View {
    @ObservedObject var store: TabletStore
    let source: PhantomCase
    @State private var zoom = 1.0
    var body: some View {
        GeometryReader { geometry in
            let axes = planeAxes(store.axis)
            let ratio = Double(source.ct.grid.dimensions[axes.1]) * source.ct.grid.spacing[axes.1] / (Double(source.ct.grid.dimensions[axes.0]) * source.ct.grid.spacing[axes.0])
            let width = min(geometry.size.width, geometry.size.height / ratio)
            ZStack {
                Color.black
                ZStack {
                    if let image = renderSlice(source, axis: store.axis, slice: Int(store.slice), center: store.windowCenter, width: store.windowWidth, overlay: store.overlay) {
                        Image(uiImage: image).resizable().interpolation(.none)
                    }
                    PencilSurface(drawing: $store.drawing, enabled: store.markup, fingerInk: store.fingerInk, changed: { store.stashDrawing() })
                        .id(store.key)
                        .allowsHitTesting(store.markup)
                }
                .frame(width: 1024, height: 1024 * ratio)
                .scaleEffect(width / 1024 * zoom)
                .frame(width: width, height: width * ratio)
                .clipped()
                .gesture(MagnifyGesture().onChanged { if !store.markup { zoom = min(max($0.magnification, 1), 3) } }.onEnded { _ in zoom = 1 })
            }
            .clipShape(RoundedRectangle(cornerRadius: 24))
            .overlay(alignment: .topLeading) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("\(["YZ", "XZ", "XY"][store.axis]) VOXEL PLANE").font(.caption.monospaced().bold())
                    Text("Slice \(Int(store.slice) + 1) / \(source.ct.grid.dimensions[store.axis]) · CT / HU").font(.caption)
                }.padding(18).foregroundStyle(.white).allowsHitTesting(false)
            }
            .overlay(alignment: .bottomLeading) {
                Text(store.markup ? "PENCIL MARKUP · observation only" : "Pinch to inspect · release to reset")
                    .font(.caption.monospaced()).padding(14).foregroundStyle(.mint).allowsHitTesting(false)
            }
        }
        .accessibilityLabel("CT slice viewer, \(["YZ", "XZ", "XY"][store.axis]) plane, slice \(Int(store.slice)+1)")
        .onChange(of: store.markup) { _, _ in zoom = 1 }
    }
}

func planeAxes(_ axis: Int) -> (Int, Int) { axis == 2 ? (0,1) : axis == 1 ? (0,2) : (1,2) }

func renderSlice(_ source: PhantomCase, axis: Int, slice: Int, center: Double, width: Double, overlay: String) -> UIImage? {
    let axes = planeAxes(axis), d = source.ct.grid.dimensions
    let w = d[axes.0], h = d[axes.1]
    var pixels = [UInt8](repeating: 255, count: w*h*4)
    let colors = Dictionary(uniqueKeysWithValues: source.structures.map { ($0.id, $0.color) })
    let dose = source.simulation?.referenceDose
    for y in 0..<h { for x in 0..<w {
        var p = [0,0,0]; p[axis] = min(max(slice, 0),d[axis]-1); p[axes.0] = x; p[axes.1] = y
        let i = source.ct.grid.index(p[0],p[1],p[2]), j = (y*w+x)*4
        let gray = min(max((Double(source.ct.values[i])-center+width/2)/width, 0),1)
        var color = [gray,gray,gray]
        if overlay == "Labels", let rgb = colors[Int(source.truth.values[i])] {
            color = zip(color,rgb).map { $0*0.65 + $1*0.35 }
        }
        if overlay == "Dose", let dose {
            // Fixed Gy scale: no per-slice renormalization.
            let level = min(Double(dose.values[i])/80,1)
            if level > 0.02 { color = zip(color,[level,0.3,1-level]).map { $0*0.6+$1*0.4 } }
        }
        for k in 0..<3 { pixels[j+k] = UInt8(min(max(color[k]*255,0),255)) }
    } }
    guard let provider = CGDataProvider(data: Data(pixels) as CFData), let image = CGImage(width: w, height: h, bitsPerComponent: 8, bitsPerPixel: 32, bytesPerRow: w*4, space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.last.rawValue), provider: provider, decode: nil, shouldInterpolate: false, intent: .defaultIntent) else { return nil }
    return UIImage(cgImage: image)
}

struct PencilSurface: UIViewRepresentable {
    @Binding var drawing: PKDrawing
    var enabled: Bool
    var fingerInk: Bool
    var changed: () -> Void
    func makeCoordinator() -> Coordinator { Coordinator(self) }
    func makeUIView(context: Context) -> PKCanvasView {
        let view = PKCanvasView()
        view.backgroundColor = .clear; view.isOpaque = false; view.isScrollEnabled = false
        view.tool = PKInkingTool(.pen, color: .systemMint, width: 3)
        view.delegate = context.coordinator
        return view
    }
    func updateUIView(_ view: PKCanvasView, context: Context) {
        context.coordinator.parent = self
        context.coordinator.updating = true
        if view.drawing != drawing { view.drawing = drawing }
        view.isUserInteractionEnabled = enabled
        view.drawingPolicy = fingerInk ? .anyInput : .pencilOnly
        context.coordinator.updating = false
    }
    class Coordinator: NSObject, PKCanvasViewDelegate {
        var parent: PencilSurface
        var updating = false
        init(_ parent: PencilSurface) { self.parent = parent }
        func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
            guard !updating else { return }
            parent.drawing = canvasView.drawing
            parent.changed()
        }
    }
}
