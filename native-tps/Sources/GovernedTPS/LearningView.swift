import SwiftUI
import TPSCore

struct LearningView: View {
    @ObservedObject var lab: LearningStore
    @EnvironmentObject var app: AppStore
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                SectionIntro(eyebrow: "Known references → measured performance", title: "Dataset & learning", detail: "Train on this Mac. Select on validation. Report once on held-out anatomy groups.")
                HStack {
                    Button("Select native cohort…") { lab.chooseDataset() }.buttonStyle(.borderedProminent)
                    Button("Open experiment…") { lab.openExperiment() }.buttonStyle(.bordered)
                    if lab.busy { ProgressView().controlSize(.small) }
                    Text(lab.status).font(.callout).foregroundStyle(Theme.muted)
                }.disabled(lab.busy)
                Card(title: "Reference contract", subtitle: "The completed training cohort is still being generated on DGX") {
                    Text("Use CT with verified native organ labels for contour training. Dose learning requires transport dose with histories, normalization and scorer provenance. Analytic proxy targets must remain explicitly identified. No MR is required for CT contouring.")
                    Text("First executable model: an interpretable Gaussian CT + position contour baseline. It learns from training labels; it is not nnU-Net or a commissioned contour model.").foregroundStyle(Theme.amber)
                }
                if !lab.cases.isEmpty {
                    Card(title: "Anatomy groups", subtitle: "All energy, motion, lesion and reconstruction variants of one source anatomy stay together") {
                        ForEach(lab.cases.indices, id: \.self) { index in
                            HStack {
                                Text(lab.cases[index].name).frame(width: 190, alignment: .leading)
                                TextField("Original anatomy ID, e.g. male_pt108", text: $lab.cases[index].anatomyGroup)
                                    .disabled(lab.partition != nil || lab.busy)
                                Text(lab.partition?.assignments[lab.cases[index].id.uuidString] ?? "unassigned").font(.caption.monospaced()).frame(width: 85)
                            }
                        }
                        Text("Do not use a generated patient ID as the anatomy group unless it actually represents a distinct source anatomy. Mapping can be supplied in anatomy-groups.json.").font(.caption).foregroundStyle(Theme.muted)
                    }
                    Card(title: "Freeze the experiment", subtitle: "Fractions apply to anatomy groups; actual case counts depend on variant counts") {
                        HStack {
                            Stepper("Train \(lab.trainPercent)%", value: $lab.trainPercent, in: 10...80, step: 5)
                            Stepper("Validation \(lab.validationPercent)%", value: $lab.validationPercent, in: 10...40, step: 5)
                            Text("Test \(100-lab.trainPercent-lab.validationPercent)%")
                            TextField("Seed", value: $lab.seed, format: .number).frame(width: 80)
                        }.disabled(lab.partition != nil || lab.busy)
                        Toggle("I have checked reference provenance and original anatomy grouping for this research experiment", isOn: $lab.referenceConfirmed).disabled(lab.partition != nil || lab.busy)
                        HStack {
                            Button("1. Freeze split") { lab.freeze() }.disabled(lab.partition != nil || !lab.referenceConfirmed)
                            Button("2. Train + validate") { lab.train() }.disabled(lab.partition == nil || lab.experiment != nil)
                            Button("3. Evaluate test") { lab.test() }.disabled(lab.experiment == nil || lab.experiment?.test != nil)
                        }.buttonStyle(.borderedProminent).disabled(lab.busy)
                        if let partition = lab.partition {
                            HStack { ForEach(["train","validation","test"], id: \.self) { split in
                                Text("\(split.capitalized): \(partition.groups.values.filter { $0 == split }.count) groups / \(partition.assignments.values.filter { $0 == split }.count) cases")
                            } }.font(.caption.monospaced()).foregroundStyle(Theme.teal)
                        }
                    }
                }
                if let result = lab.experiment {
                    Card(title: "Measured against source labels", subtitle: "Dice excludes background; empty/empty labels are omitted. Centroid error is in LPS millimetres.") {
                        Text("Selected variance floor: \(result.selectedVarianceFloor.formatted()) · Model selection used validation only.")
                        ForEach(result.validation + (result.test ?? [])) { row in
                            VStack(alignment: .leading) {
                                Text("\(row.name) · \(row.split) · mean Dice \(row.meanDice?.formatted(.number.precision(.fractionLength(3))) ?? "n/a")").font(.headline)
                                ForEach(row.metrics) { metric in
                                    Text("\(metric.name): Dice \(metric.dice?.formatted(.number.precision(.fractionLength(3))) ?? "n/a") · volume \(metric.predictedCC.formatted(.number.precision(.fractionLength(2)))) / \(metric.referenceCC.formatted(.number.precision(.fractionLength(2)))) cc · centroid error \(metric.centroidErrorMM?.formatted(.number.precision(.fractionLength(2))) ?? "n/a") mm")
                                        .font(.caption).foregroundStyle(Theme.muted)
                                }
                            }.padding(.vertical, 6)
                        }
                        HStack {
                            Button("Export report for iPad…") { lab.exportReport() }
                            Button("Predict workspace case") { app.runLearned(result) }.disabled(app.source == nil || app.busy)
                        }.buttonStyle(.bordered).disabled(lab.busy)
                        if let url = lab.resultURL { Text(url.path).font(.caption.monospaced()).textSelection(.enabled) }
                        Text("These metrics measure agreement with this synthetic reference. They do not establish performance on real patient data. Test-set reuse across new experiments is not technically prevented; document it and reserve a new independent test cohort for final claims.").font(.caption).foregroundStyle(Theme.amber)
                    }
                }
            }.padding(26)
        }.alert("Dataset action stopped", isPresented: Binding(get: { lab.error != nil }, set: { if !$0 { lab.error = nil } })) {
            Button("OK") { lab.error = nil }
        } message: { Text(lab.error ?? "") }
    }
}
