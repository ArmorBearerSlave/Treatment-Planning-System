import SwiftUI
import TPSCore

struct AgentWorkbench: View {
    @EnvironmentObject var store: AppStore
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                SectionIntro(eyebrow: "Local intelligence / bounded actions", title: "Your research team, orchestrated.",
                    detail: "Role-scoped agents compile a workflow. You inspect the plan before execution; every result enters the review queue.")
                HStack(alignment: .top, spacing: 12) {
                    ForEach(AgentRole.allCases) { role in
                        Button { store.role = role; store.proposal = nil } label: {
                            VStack(alignment: .leading, spacing: 12) {
                                Image(systemName: role == .physician ? "stethoscope" : role == .physicist ? "atom" : role == .dosimetrist ? "waveform.path" : "viewfinder").font(.system(size: 23)).foregroundStyle(store.role == role ? Theme.teal : Theme.muted)
                                Text(role.title).font(.system(size: 13, weight: .semibold))
                                Text(role.scope).font(.system(size: 11)).foregroundStyle(Theme.muted).frame(height: 38, alignment: .top)
                            }.padding(18).frame(maxWidth: .infinity, alignment: .leading)
                            .background(store.role == role ? Theme.teal.opacity(0.08) : Theme.surface, in: RoundedRectangle(cornerRadius: 12))
                            .overlay(RoundedRectangle(cornerRadius: 12).stroke(store.role == role ? Theme.teal.opacity(0.5) : .white.opacity(0.06)))
                        }.buttonStyle(.plain).disabled(store.busy)
                    }
                }
                HStack(alignment: .top, spacing: 18) {
                    Card(title: "Describe the work", subtitle: "Selected case: \(store.source?.name ?? "Create a case in Workspace first")") {
                        TextEditor(text: $store.prompt).font(.system(size: 14)).scrollContentBackground(.hidden).padding(8).frame(height: 160).background(Theme.background, in: RoundedRectangle(cornerRadius: 8)).disabled(store.busy)
                        HStack {
                            Badge(text: store.ollamaModel)
                            Spacer()
                            Button("Compile with local LLM") { store.propose() }.buttonStyle(.borderedProminent).disabled(store.busy || store.source == nil)
                        }
                        Text("Only case identity and the typed request are sent to Ollama on this Mac. Image arrays stay out of the language-model prompt.")
                            .font(.system(size: 11)).foregroundStyle(Theme.muted)
                    }
                    Card(title: "Execution contract", subtitle: "Enforced by the application") {
                        ForEach(["Typed, allowlisted operations", "Role scope checked after generation", "Operator confirms the proposed workflow", "Model results carry source hashes", "Agents cannot record human reviews"], id: \.self) { item in
                            Label(item, systemImage: "checkmark.shield").font(.system(size: 12)).foregroundStyle(Theme.muted)
                        }
                        Text("These agents assist professional workflows. Professional identity, institutional signatures, and clinical release are not implemented.")
                            .font(.system(size: 11)).foregroundStyle(Theme.amber).lineSpacing(3)
                    }.frame(width: 310)
                }
                if let plan = store.proposal {
                    Card(title: "Proposed workflow", subtitle: "\(store.proposalModel) · no actions executed yet") {
                        Text(plan.summary).font(.system(size: 14)).lineSpacing(5)
                        HStack(spacing: 12) {
                            ForEach(Array(plan.operations.enumerated()), id: \.offset) { index, operation in
                                HStack { Text("0\(index+1)").foregroundStyle(Theme.teal); Text(operation.title) }.font(.system(size: 12, weight: .medium)).padding(12).background(Theme.raised, in: RoundedRectangle(cornerRadius: 8))
                            }
                        }
                        HStack {
                            Picker("Inference", selection: $store.inferenceMode) { ForEach(InferenceMode.allCases) { Text($0.rawValue).tag($0) } }.frame(width: 330)
                            Spacer()
                            Button("Discard proposal") { store.proposal = nil }.buttonStyle(.bordered)
                            Button("Confirm & execute") { store.executeProposal() }.buttonStyle(.borderedProminent)
                        }.disabled(store.busy)
                    }
                }
            }.padding(28)
        }
    }
}

struct PhantomLab: View {
    @EnvironmentObject var store: AppStore
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                SectionIntro(eyebrow: "Synthetic data / reproducible lineage", title: "Build the data behind the models.",
                    detail: "Define an anatomy family and a reproducible recipe. XCAT2 and OpenTOPAS/nBio run on the DGX Spark through the phantom adapter.")
                HStack(alignment: .top, spacing: 18) {
                    Card(title: "Phantom recipe", subtitle: "All variants of one anatomy share the same dataset split.") {
                        TextField("Anatomy family ID", text: $store.recipe.anatomyID).textFieldStyle(.roundedBorder)
                        Stepper("Seed: \(store.recipe.seed)", value: $store.recipe.seed, in: 0...1_000_000)
                        parameter("Body scale", value: $store.recipe.bodyScale, range: 0.7...1.3, unit: "×")
                        parameter("Target proxy radius", value: $store.recipe.targetRadiusMM, range: 8...30, unit: "mm")
                        parameter("Motion phase", value: $store.recipe.motionPhase, range: 0...1, unit: "cycle")
                        TextField("nBio profile ID (unbound until connected)", text: $store.recipe.nBioProfile).textFieldStyle(.roundedBorder)
                        HStack { Text("Suggested split").foregroundStyle(Theme.muted); Spacer(); Badge(text: store.recipe.suggestedSplit) }.font(.system(size: 12))
                        Button("Generate analytic test phantom") { store.createPhantom() }.buttonStyle(.borderedProminent)
                        Text("The built-in fixture creates CT, MR-signal and disjoint label volumes. It is not XCAT2, radiation transport, or nBio biology. The nBio profile is lineage metadata until a real adapter is connected.")
                            .font(.system(size: 11)).foregroundStyle(Theme.amber).lineSpacing(3)
                    }.disabled(store.busy)
                    VStack(spacing: 18) {
                        Card(title: "DGX Spark generator", subtitle: "XCAT2 → OpenTOPAS / nBio → synthetic case") {
                            TextField("http://<Spark LAN IP>:<adapter port>", text: $store.sparkEndpoint).textFieldStyle(.roundedBorder)
                            Button("Request phantom from Spark") { store.createPhantom(remote: true) }.buttonStyle(.bordered).disabled(store.sparkEndpoint.isEmpty || store.busy)
                            Text("Adapter endpoint: POST /v1/phantoms. The Spark's actual installation paths and job commands must be supplied in the adapter; this app does not invent or execute remote shell commands.")
                                .font(.system(size: 11)).foregroundStyle(Theme.muted).lineSpacing(4)
                        }
                        Card(title: "Training-data handoff", subtitle: "Lineage and evidence travel with the volume") {
                            ForEach(["Generator version + recipe + random seed", "Anatomy-level split assignment", "CT, MR and truth labels on one LPS grid", "Reviewed outputs remain distinct from truth", "Source digest and research review records"], id: \.self) { line in
                                Label(line, systemImage: "arrow.turn.down.right").font(.system(size: 12)).foregroundStyle(Theme.muted)
                            }
                            Button("Export reviewed research bundle…") { store.exportResearch() }.buttonStyle(.bordered).disabled(store.source == nil || store.busy)
                            Text("Analytic dose is not a physical dose training target. A separate dataset acceptance process must select valid labels and transport-derived targets.").font(.system(size: 11)).foregroundStyle(Theme.amber)
                        }
                    }
                }
                Card(title: "Generated case library", subtitle: "\(store.workspace.cases.count) local synthetic cases") {
                    if store.workspace.cases.isEmpty { Text("No phantoms generated yet.").foregroundStyle(Theme.muted) }
                    ForEach(store.workspace.cases) { source in
                        HStack {
                            VStack(alignment: .leading, spacing: 4) { Text(source.name).font(.system(size: 13, weight: .medium)); Text("Seed \(source.recipe.seed) · \(source.generator)").font(.system(size: 10)).foregroundStyle(Theme.muted) }
                            Spacer(); Badge(text: source.recipe.suggestedSplit)
                            Button("Open") { store.selectedCaseID = source.id; store.selectedArtifactID = nil; store.screen = .workspace }.disabled(store.busy)
                        }.padding(.vertical, 6)
                    }
                }
            }.padding(28)
        }
    }
    func parameter(_ title: String, value: Binding<Double>, range: ClosedRange<Double>, unit: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack { Text(title); Spacer(); Text("\(value.wrappedValue.formatted(.number.precision(.fractionLength(2)))) \(unit)").foregroundStyle(Theme.teal).monospacedDigit() }.font(.system(size: 12))
            Slider(value: value, in: range)
        }
    }
}

struct ModelLibrary: View {
    @EnvironmentObject var store: AppStore
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                SectionIntro(eyebrow: "Model registry / on-device inference", title: "Local by design. Explicit by version.",
                    detail: "Ollama handles language orchestration. Core ML runs compatible image-model exports on this Mac. No trained weights ship with the app.")
                HStack(alignment: .top, spacing: 18) {
                    Card(title: "Local language runtime", subtitle: store.ollamaStatus) {
                        TextField("Ollama URL", text: $store.ollamaEndpoint).textFieldStyle(.roundedBorder)
                        TextField("Installed model tag", text: $store.ollamaModel).textFieldStyle(.roundedBorder)
                        Button("Check installed models") { store.checkOllama() }.buttonStyle(.bordered).disabled(store.busy)
                        ForEach(store.availableModels, id: \.self) { model in Button(model) { store.ollamaModel = model }.font(.system(size: 11, design: .monospaced)).buttonStyle(.plain).foregroundStyle(Theme.teal) }
                        Text("Models are never downloaded automatically. Choose a locally installed, non-cloud tag.").font(.system(size: 11)).foregroundStyle(Theme.muted)
                    }
                    Card(title: "Selected language-model family", subtitle: "Candidate selection · evaluate on your workflow before promotion") {
                        modelRow("Qwen3 Coder · 30B", detail: "Default on this 128 GiB Mac. Already installed; used for bounded tool/workflow orchestration, not clinical reasoning. qwen3-coder:30b.", badge: "LOCAL DEFAULT")
                        modelRow("Qwen3 · 4B", detail: "Already installed. Lower-memory routing and short-workflow fallback. qwen3:4b.", badge: "FAST FALLBACK")
                        modelRow("Qwen3.5 · 9B / 35B-A3B", detail: "Upgrade candidates, not installed by this app. Compare schema adherence, task accuracy and latency before promotion.", badge: "EVALUATE")
                    }
                }
                HStack(alignment: .top, spacing: 14) {
                    ForEach([TPSOperation.contour, .predictDose, .syntheticCT]) { operation in
                        Card(title: operation.title, subtitle: store.modelManifests[operation] == nil ? "No local model configured" : "Manifest selected · verified at run") {
                            Image(systemName: operation == .contour ? "lasso" : operation == .predictDose ? "waveform.path" : "square.3.layers.3d").font(.system(size: 28)).foregroundStyle(Theme.teal)
                            Text(operation == .contour ? "Candidate: task-specific nnU-Net / TotalSegmentator-derived export. Requires an explicit Core ML conversion and label map." : operation == .predictDose ? "Candidate: CT + structures conditioned 3D U-Net. Requires your trained, evaluated weights and declared output units." : "Candidate: paired MR→CT 3D regression model. Requires acquisition-specific training and preserved HU calibration.")
                                .font(.system(size: 12)).foregroundStyle(Theme.muted).lineSpacing(4).frame(minHeight: 95, alignment: .top)
                            if let path = store.modelManifests[operation] { Text(path.lastPathComponent).font(.system(size: 10, design: .monospaced)).lineLimit(1) }
                            Button("Choose model manifest…") { store.chooseManifest(operation) }.buttonStyle(.bordered).disabled(store.busy)
                            Badge(text: "Unvalidated research", color: Theme.amber)
                        }
                    }
                }
                Card(title: "Promotion requires evidence", subtitle: "A selected file is not a validated model") {
                    Text("This build verifies checksums, modality, shape, units, input lineage and response bounds. It does not establish accuracy, clinical suitability, commissioning, independence of QA, or a release authorization. Model packages must be adapted to the documented tensor contract.")
                        .font(.system(size: 12)).foregroundStyle(Theme.muted).lineSpacing(4)
                }
            }.padding(28)
        }
    }
    func modelRow(_ name: String, detail: String, badge: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack { Text(name).font(.system(size: 13, weight: .semibold)); Spacer(); Badge(text: badge) }
            Text(detail).font(.system(size: 11)).foregroundStyle(Theme.muted)
        }
    }
}

struct GovernanceView: View {
    @EnvironmentObject var store: AppStore
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                SectionIntro(eyebrow: "Review / provenance / evidence", title: "Make every decision inspectable.",
                    detail: "Research reviews bind to the exact artifact hash. Names below are local operator attestations, not authenticated institutional signatures.")
                HStack(alignment: .top, spacing: 18) {
                    Card(title: "Review queue", subtitle: "\(store.pendingCount) unreviewed results across the workspace") {
                        if store.workspace.artifacts.isEmpty { Text("Generate an inference result to begin review.").foregroundStyle(Theme.muted).font(.system(size: 12)) }
                        ForEach(store.workspace.artifacts.reversed()) { artifact in
                            Button {
                                store.selectedCaseID = artifact.caseID; store.selectedArtifactID = artifact.id
                            } label: {
                                HStack {
                                    VStack(alignment: .leading, spacing: 5) {
                                        Text(artifact.operation.title).font(.system(size: 13, weight: .medium))
                                        Text("\(artifact.modelID) · \(artifact.id.uuidString.prefix(8))").font(.system(size: 10)).foregroundStyle(Theme.muted)
                                    }
                                    Spacer()
                                    Badge(text: store.workspace.latestReview(for: artifact)?.decision == .acceptedForResearch ? "Accepted / research" : store.workspace.latestReview(for: artifact)?.decision == .rejected ? "Rejected" : "Pending", color: store.workspace.latestReview(for: artifact)?.decision == .acceptedForResearch ? Theme.teal : Theme.amber)
                                }.padding(12).background(store.selectedArtifactID == artifact.id ? Theme.raised : .clear, in: RoundedRectangle(cornerRadius: 8))
                            }.buttonStyle(.plain).disabled(store.busy)
                        }
                    }
                    Card(title: "Record research review", subtitle: store.selectedArtifact?.operation.title ?? "Select a result") {
                        if let artifact = store.selectedArtifact {
                            Text(artifact.modelID).font(.system(size: 11, design: .monospaced)).foregroundStyle(Theme.teal)
                            Button("Inspect in volume viewer") { store.screen = .workspace }.buttonStyle(.bordered)
                            TextField("Reviewer name", text: $store.reviewer).textFieldStyle(.roundedBorder)
                            TextEditor(text: $store.reviewNote).font(.system(size: 12)).scrollContentBackground(.hidden).padding(8).frame(height: 90).background(Theme.background, in: RoundedRectangle(cornerRadius: 8))
                            Text("Record what you inspected and any limitations. Minimum 8 characters.").font(.system(size: 10)).foregroundStyle(Theme.muted)
                            HStack {
                                Button("Reject") { store.review(.rejected) }.buttonStyle(.bordered)
                                Button("Accept for research") { store.review(.acceptedForResearch) }.buttonStyle(.borderedProminent)
                            }.disabled(store.busy || store.reviewer.trimmingCharacters(in: .whitespacesAndNewlines).count < 2 || store.reviewNote.trimmingCharacters(in: .whitespacesAndNewlines).count < 8)
                            Button("Export reviewed research bundle…") { store.exportResearch() }.buttonStyle(.bordered).disabled(store.busy)
                        } else { Text("AI proposals remain separate from source data until explicitly reviewed.").font(.system(size: 12)).foregroundStyle(Theme.muted) }
                    }.frame(width: 350)
                }
                Card(title: "Audit trail", subtitle: "Hash-linked local events · \(store.workspace.ledger.events.count) records · not an externally anchored or signed ledger") {
                    HStack {
                        Label("Chain verified on load and save", systemImage: "link").foregroundStyle(Theme.teal)
                        Spacer()
                        Button("Save workspace copy…") { store.saveCopy() }.buttonStyle(.bordered).disabled(store.busy)
                    }.font(.system(size: 11))
                    ForEach(store.workspace.ledger.events.reversed()) { event in
                        HStack(alignment: .top, spacing: 16) {
                            Text(String(format: "%03d", event.sequence)).foregroundStyle(Theme.teal).frame(width: 30)
                            VStack(alignment: .leading, spacing: 5) {
                                HStack { Text(event.action).fontWeight(.semibold); Text(event.actor).foregroundStyle(Theme.muted); Spacer(); Text(event.timestamp.formatted(date: .omitted, time: .standard)).foregroundStyle(Theme.muted) }
                                Text(event.detail).foregroundStyle(Theme.muted).lineLimit(3).textSelection(.enabled)
                                Text("SHA256 \(event.hash.prefix(24))…").font(.system(size: 9, design: .monospaced)).foregroundStyle(Theme.teal.opacity(0.7))
                            }
                        }.font(.system(size: 11)).padding(.vertical, 8)
                    }
                }
            }.padding(28)
        }
    }
}
