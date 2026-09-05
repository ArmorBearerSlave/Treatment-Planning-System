import SwiftUI
import TPSCore

struct RootView: View {
    @StateObject private var cerr = CERRStore()
    @StateObject private var matrad = MatRadStore()
    @StateObject private var topas = TopasStore()
    @StateObject private var learning = LearningStore()
    @EnvironmentObject var store: AppStore
    var body: some View {
        HStack(spacing: 0) {
            sidebar.frame(width: 210)
            VStack(spacing: 0) {
                topBar
                Group {
                    switch store.screen {
                    case .cerr: CERRView(analysis: cerr)
                    case .matrad: MatRadView(planning: matrad)
                    case .topas: TopasView(simulation: topas)
                    case .learning: LearningView(lab: learning)
                    case .workspace: WorkstationView()
                    case .agents: AgentWorkbench()
                    case .phantoms: PhantomLab()
                    case .models: ModelLibrary()
                    case .governance: GovernanceView()
                    }
                }.frame(maxWidth: .infinity, maxHeight: .infinity)
                HStack(spacing: 8) {
                    if store.busy { ProgressView().controlSize(.mini) } else { Circle().fill(Theme.teal).frame(width: 5, height: 5) }
                    Text(store.activity).lineLimit(1)
                    Spacer()
                    Text(store.persistenceDescription)
                    Text("MACOS / NATIVE").foregroundStyle(Theme.teal)
                }.font(.system(size: 10, design: .monospaced)).foregroundStyle(Theme.muted).padding(.horizontal, 24).padding(.vertical, 12)
                .background(Theme.surface.opacity(0.7))
            }
        }.background(Theme.background).tint(Theme.teal)
    }
    var sidebar: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack(spacing: 10) {
                Image(systemName: "scope").font(.system(size: 27, weight: .light)).foregroundStyle(Theme.teal)
                VStack(alignment: .leading, spacing: 3) {
                    Text("GOVERNED").font(.system(size: 11, weight: .bold)).tracking(2)
                    Text("TPS / RESEARCH").font(.system(size: 9, design: .monospaced)).tracking(1).foregroundStyle(Theme.muted)
                }
            }.padding(.top, 42).padding(.bottom, 40).padding(.leading, 20)
            Text("WORKSTATION").font(.system(size: 9, weight: .medium)).tracking(1.5).foregroundStyle(Theme.muted).padding(.leading, 22).padding(.bottom, 14)
            ForEach(Screen.allCases) { screen in
                Button { store.screen = screen } label: {
                    HStack(spacing: 11) {
                        Image(systemName: screen.icon).frame(width: 20)
                        Text(screen.rawValue).font(.system(size: 12, weight: store.screen == screen ? .semibold : .regular))
                        Spacer()
                        if screen == .governance && store.pendingCount > 0 { Text("\(store.pendingCount)").font(.system(size: 10, weight: .bold)).foregroundStyle(Theme.amber) }
                    }.padding(.horizontal, 13).padding(.vertical, 13)
                    .foregroundStyle(store.screen == screen ? Theme.teal : Theme.muted)
                    .background(store.screen == screen ? Theme.teal.opacity(0.09) : .clear, in: RoundedRectangle(cornerRadius: 8))
                }.buttonStyle(.plain).padding(.horizontal, 10).padding(.bottom, 3)
            }
            Spacer()
            VStack(alignment: .leading, spacing: 12) {
                Image(systemName: "lock.shield").foregroundStyle(Theme.teal)
                Text("Propose. Inspect. Review.").font(.system(size: 12, weight: .medium))
                Text("AI outputs remain proposals. Research acceptance never authorizes treatment delivery.").font(.system(size: 11)).foregroundStyle(Theme.muted).lineSpacing(4)
                Badge(text: "Synthetic data only", color: Theme.amber)
            }.padding(16).background(Theme.raised.opacity(0.45), in: RoundedRectangle(cornerRadius: 12)).padding(12)
            Text("ISOLATED NATIVE WORKSPACE  /  0.1").font(.system(size: 8, design: .monospaced)).foregroundStyle(Theme.muted).padding(18)
        }.background(Theme.surface.opacity(0.6))
    }
    var topBar: some View {
        HStack(spacing: 14) {
            Text("Research environment").font(.system(size: 12, weight: .medium))
            Image(systemName: "chevron.right").font(.system(size: 9)).foregroundStyle(Theme.muted)
            Text(store.screen.rawValue).font(.system(size: 12)).foregroundStyle(Theme.muted)
            Spacer()
            Button { store.importCase() } label: {
                Label("Import case…", systemImage: "square.and.arrow.down")
            }.buttonStyle(.bordered).disabled(store.busy)
                .help("Import a converted native case JSON from this Mac (⌘O)")
            Badge(text: "Inference · this Mac")
            Badge(text: "Clinical release unavailable", color: Theme.amber)
        }.padding(.horizontal, 26).padding(.top, 25).padding(.bottom, 20)
        .overlay(alignment: .bottom) { Rectangle().fill(.white.opacity(0.06)).frame(height: 1) }
    }
}
