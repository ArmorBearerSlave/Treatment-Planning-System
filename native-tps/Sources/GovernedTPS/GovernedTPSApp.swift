import SwiftUI

@main struct GovernedTPSApp: App {
    @StateObject private var store = AppStore()
    var body: some Scene {
        WindowGroup("Governed TPS") {
            RootView().environmentObject(store).preferredColorScheme(.dark)
                .frame(minWidth: 1180, minHeight: 780)
                .alert("Action could not complete", isPresented: Binding(get: { store.error != nil }, set: { if !$0 { store.error = nil } })) {
                    Button("OK") { store.error = nil }
                } message: { Text(store.error ?? "") }
        }
        .defaultSize(width: 1460, height: 920)
        .windowStyle(.hiddenTitleBar)
        .commands {
            CommandGroup(replacing: .newItem) {
                Button("New analytic phantom") { store.createPhantom() }.keyboardShortcut("n").disabled(store.busy)
                Button("Import synthetic case…") { store.importCase() }.keyboardShortcut("o").disabled(store.busy)
                Button("Save workspace copy…") { store.saveCopy() }.keyboardShortcut("s").disabled(store.busy)
            }
        }
    }
}

enum Theme {
    static let background = Color(red: 0.035, green: 0.060, blue: 0.087)
    static let surface = Color(red: 0.062, green: 0.098, blue: 0.135)
    static let raised = Color(red: 0.09, green: 0.14, blue: 0.18)
    static let teal = Color(red: 0.32, green: 0.88, blue: 0.75)
    static let amber = Color(red: 1, green: 0.72, blue: 0.38)
    static let muted = Color(red: 0.54, green: 0.64, blue: 0.72)
}

struct Card<Content: View>: View {
    var title: String
    var subtitle: String = ""
    @ViewBuilder var content: Content
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            if !title.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Text(title).font(.system(size: 15, weight: .semibold))
                    if !subtitle.isEmpty { Text(subtitle).font(.system(size: 11)).foregroundStyle(Theme.muted) }
                }
            }
            content
        }.padding(20).frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.surface, in: RoundedRectangle(cornerRadius: 14))
            .overlay(RoundedRectangle(cornerRadius: 14).stroke(.white.opacity(0.07)))
    }
}
struct Badge: View {
    var text: String
    var color: Color = Theme.teal
    var body: some View { Text(text.uppercased()).font(.system(size: 9, weight: .bold, design: .monospaced)).tracking(0.7).foregroundStyle(color).padding(.horizontal, 9).padding(.vertical, 5).background(color.opacity(0.1), in: Capsule()) }
}
struct SectionIntro: View {
    var eyebrow: String
    var title: String
    var detail: String
    var body: some View {
        VStack(alignment: .leading, spacing: 9) {
            Text(eyebrow.uppercased()).font(.system(size: 10, weight: .semibold, design: .monospaced)).tracking(2).foregroundStyle(Theme.teal)
            Text(title).font(.system(size: 29, weight: .semibold))
            Text(detail).font(.system(size: 13)).foregroundStyle(Theme.muted).fixedSize(horizontal: false, vertical: true)
        }.padding(.bottom, 6)
    }
}
