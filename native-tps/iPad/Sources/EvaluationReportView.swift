import SwiftUI
import TPSCore

struct EvaluationReportView: View {
    let report: LearningReport
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        NavigationStack {
            List {
                Section("Experiment") {
                    Text(report.experimentID.uuidString).font(.caption.monospaced())
                    Text(report.method)
                    Text("Research agreement with synthetic references; not clinical model approval.").foregroundStyle(.orange)
                    ForEach(["train","validation","test"], id: \.self) { split in
                        LabeledContent(split.capitalized, value: "\(report.groupCounts[split,default:0]) anatomy groups")
                    }
                }
                Section("Validation") { rows(report.validation) }
                Section("Held-out test") {
                    if let test = report.test { rows(test) }
                    else { Text("Not evaluated. Test references remain reserved on the Mac.") }
                }
            }.navigationTitle("Model evaluation")
                .toolbar { Button("Done") { dismiss() } }
        }
    }
    @ViewBuilder func rows(_ values: [CaseEvaluation]) -> some View {
        ForEach(values) { value in
            DisclosureGroup("\(value.name) · Dice \(value.meanDice?.formatted(.number.precision(.fractionLength(3))) ?? "n/a")") {
                ForEach(value.metrics) { metric in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(metric.name).font(.headline)
                        Text("Dice \(metric.dice?.formatted(.number.precision(.fractionLength(3))) ?? "n/a") · centroid error \(metric.centroidErrorMM?.formatted(.number.precision(.fractionLength(2))) ?? "n/a") mm")
                        Text("Predicted / reference: \(metric.predictedCC.formatted(.number.precision(.fractionLength(2)))) / \(metric.referenceCC.formatted(.number.precision(.fractionLength(2)))) cc").foregroundStyle(.secondary)
                    }
                }
            }
        }
    }
}
