import XCTest
@testable import TPSCore

final class TPSCoreTests: XCTestCase {
    func source() throws -> PhantomCase { try PhantomFactory.analytic(PhantomRecipe(), size: 16) }
    func testPlaceholderMRProvenanceSurvivesRoundTripAndBlocksSCT() throws {
        var value = try source()
        value.sourceNotes = ["mr": "Synthetic zero placeholder", "xcatPlanSHA256": String(repeating: "a", count: 64)]
        value.mrIsPlaceholder = true
        let restored = try JSONDecoder().decode(PhantomCase.self, from: Canonical.data(value))
        XCTAssertEqual(restored.sourceNotes, value.sourceNotes)
        XCTAssertEqual(restored.mrIsPlaceholder, true)
        XCTAssertThrowsError(try restored.validateInput(for: .syntheticCT))
        XCTAssertNoThrow(try restored.validateInput(for: .contour))
        value.sourceNotes = nil; value.mrIsPlaceholder = nil
        value.mr.values = Array(repeating: 0, count: value.mr.values.count)
        XCTAssertThrowsError(try AnalyticInference.run(.syntheticCT, source: value))
    }
    func testGridRejectsOversizedAndDegenerateDimensions() {
        for dimensions in [[0,2,2], [Int.max,2,2], [512,512,512], [3,3]] {
            XCTAssertThrowsError(try Grid(dimensions: dimensions, spacing: [1,1,1], origin: [0,0,0], frameID: "test").validate())
        }
    }
    func testGridRejectsBadDirection() {
        XCTAssertThrowsError(try Grid(dimensions: [2,2,2], spacing: [1,1,1], origin: [0,0,0], direction: [1,0,0,0,1,0,0,0,-1], frameID: "test").validate())
    }
    func testLPSPositionWithRotatedBasis() throws {
        let grid = Grid(dimensions: [2,2,2], spacing: [2,3,4], origin: [10,20,30], direction: [0,-1,0,1,0,0,0,0,1], frameID: "test")
        try grid.validate(); XCTAssertEqual(grid.position(1,1,1), [7,22,34])
    }
    func testRejectsInvalidVoxelCountAndUnits() throws {
        var volume = try source().ct; volume.values.removeLast()
        XCTAssertThrowsError(try volume.validate())
        volume = try source().ct; volume.units = "Gy"
        XCTAssertThrowsError(try volume.validate())
    }
    func testRejectsNonfiniteVoxels() throws {
        var volume = try source().ct; volume.values[0] = .nan
        XCTAssertThrowsError(try volume.validate())
    }
    func testRejectsNegativeDose() throws {
        let item = try source(); var volume = try AnalyticInference.run(.predictDose, source: item).volume
        volume.values[0] = -1; XCTAssertThrowsError(try volume.validate())
    }
    func testRecipeIsReproducible() throws {
        let a = try source(), b = try source()
        XCTAssertEqual(a.ct.values, b.ct.values); XCTAssertEqual(a.mr.values, b.mr.values)
        XCTAssertNotEqual(a.id, b.id)
    }
    func testRecipeChangesVolume() throws {
        let a = try source(), b = try PhantomFactory.analytic(PhantomRecipe(seed: 3), size: 16)
        XCTAssertNotEqual(a.ct.values, b.ct.values)
    }
    func testSplitStaysWithAnatomyAcrossVariants() {
        XCTAssertEqual(PhantomRecipe(seed: 42).suggestedSplit, PhantomRecipe(seed: 99, motionPhase: 0.7).suggestedSplit)
    }
    func testCaseRejectsNonSyntheticAndUnknownTruthLabels() throws {
        var item = try source(); item.syntheticOnly = false
        XCTAssertThrowsError(try item.validate())
        item.syntheticOnly = true; item.truth.values[0] = 999
        XCTAssertThrowsError(try item.validate())
    }
    func testAllFixtureOutputsValidateAndAreIdentified() throws {
        let item = try source()
        for operation in [TPSOperation.contour, .predictDose, .syntheticCT] {
            let artifact = try AnalyticInference.run(operation, source: item)
            try artifact.validate(for: item); XCTAssertTrue(artifact.isDemo)
            XCTAssertEqual(artifact.volume.modality, operation.modality)
        }
    }
    func testContoursDoNotCopyGroundTruth() throws {
        let item = try source(), artifact = try AnalyticInference.run(.contour, source: item)
        XCTAssertNotEqual(artifact.volume.values, item.truth.values)
    }
    func testArtifactRejectsSpatialAndInputMismatch() throws {
        let item = try source(); var artifact = try AnalyticInference.run(.predictDose, source: item)
        artifact.volume.grid.origin[0] += 1
        XCTAssertThrowsError(try artifact.validate(for: item))
        artifact = try AnalyticInference.run(.predictDose, source: item); artifact.inputHash = "altered"
        XCTAssertThrowsError(try artifact.validate(for: item))
    }
    func testRejectsMismatchedResponseIdentity() throws {
        let item = try source(), artifact = try AnalyticInference.run(.contour, source: item)
        let request = try InferenceRequest(operation: .contour, modelID: artifact.modelID, modelVersion: artifact.modelVersion, source: item)
        XCTAssertThrowsError(try InferenceResponse(requestID: UUID(), artifact: artifact).validate(for: request))
        try InferenceResponse(requestID: request.requestID, artifact: artifact).validate(for: request)
    }
    func testDVHUsesVolumeAndCumulativeThresholds() throws {
        let grid = Grid(dimensions: [2,2,2], spacing: [10,10,10], origin: [0,0,0], frameID: "test")
        let dose = Volume(grid: grid, modality: .dose, units: "Gy", values: [10,10,20,20,30,30,40,40])
        let labels = Volume(grid: grid, modality: .labels, units: "label", values: Array(repeating: 1, count: 8))
        let dvh = try DVH.calculate(dose: dose, labels: labels, structures: [Structure(id: 1, name: "ROI", color: [1,0,0])])[0]
        XCTAssertEqual(dvh.meanGy, 25); XCTAssertEqual(dvh.volumeCC, 8); XCTAssertEqual(dvh.d95Gy, 10)
        XCTAssertEqual(dvh.points.first?.volumePercent, 100); XCTAssertEqual(dvh.points.last?.volumePercent, 25)
        for i in 1..<dvh.points.count { XCTAssertLessThanOrEqual(dvh.points[i].volumePercent, dvh.points[i-1].volumePercent) }
    }
    func testDVHRejectsSameShapeDifferentFrame() throws {
        let item = try source(); let dose = try AnalyticInference.run(.predictDose, source: item).volume
        var labels = item.truth; labels.grid.frameID = "other"
        XCTAssertThrowsError(try DVH.calculate(dose: dose, labels: labels, structures: item.structures))
    }
    func testRolePermissionsFailClosed() {
        XCTAssertThrowsError(try AgentPlan(summary: "Dose", operations: [.predictDose]).validate(for: .technologist))
        XCTAssertThrowsError(try AgentPlan(summary: "Duplicate", operations: [.inspect,.inspect]).validate(for: .physician))
        XCTAssertThrowsError(try JSONDecoder().decode(AgentPlan.self, from: Data("{\"summary\":\"x\",\"operations\":[\"approveTreatment\"]}".utf8)))
    }
    func testAgentCannotReview() throws {
        let item = try source(), artifact = try AnalyticInference.run(.contour, source: item)
        XCTAssertThrowsError(try ReviewRecord(artifact: artifact, reviewer: "Agent", note: "Self approved", decision: .acceptedForResearch, actorIsAgent: true))
    }
    func testResearchExportRequiresReview() throws {
        let item = try source(); var workspace = Workspace(); workspace.cases = [item]
        workspace.artifacts = [try AnalyticInference.run(.predictDose, source: item)]
        XCTAssertThrowsError(try workspace.researchExport(caseID: item.id))
        workspace.reviews = [try ReviewRecord(artifact: workspace.artifacts[0], reviewer: "Research operator", note: "Inspected synthetic output", decision: .acceptedForResearch)]
        let bundle = try workspace.researchExport(caseID: item.id)
        XCTAssertFalse(bundle.clinicalUsePermitted); XCTAssertEqual(bundle.artifacts.count, 1)
    }
    func testRejectionOverridesEarlierAcceptance() throws {
        let item = try source(); var workspace = Workspace(); workspace.cases = [item]
        let artifact = try AnalyticInference.run(.contour, source: item); workspace.artifacts = [artifact]
        for decision in [ReviewDecision.acceptedForResearch, .rejected] {
            workspace.reviews.append(try ReviewRecord(artifact: artifact, reviewer: "Operator", note: "New inspection evidence", decision: decision))
        }
        XCTAssertThrowsError(try workspace.researchExport(caseID: item.id))
    }
    func testEditedArtifactInvalidatesReview() throws {
        let item = try source(); var workspace = Workspace(); workspace.cases = [item]
        workspace.artifacts = [try AnalyticInference.run(.predictDose, source: item)]
        workspace.reviews = [try ReviewRecord(artifact: workspace.artifacts[0], reviewer: "Operator", note: "Inspected synthetic output", decision: .acceptedForResearch)]
        workspace.artifacts[0].volume.values[0] = 1
        XCTAssertThrowsError(try workspace.validate())
    }
    func testAuditDetectsEditedEvent() throws {
        var ledger = AuditLedger(); try ledger.append(actor: "test", action: "created", detail: "original")
        let text = String(decoding: try Canonical.data(ledger), as: UTF8.self).replacingOccurrences(of: "original", with: "modified")
        let tampered = try JSONDecoder().decode(AuditLedger.self, from: Data(text.utf8))
        XCTAssertThrowsError(try tampered.validate())
    }
    func testWorkspaceRoundTrip() throws {
        var workspace = Workspace(); workspace.cases = [try source()]
        try workspace.ledger.append(actor: "test", action: "created", detail: "fixture")
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString+".json")
        defer { try? FileManager.default.removeItem(at: url) }
        try WorkspaceFile.save(workspace, to: url)
        XCTAssertEqual(try Canonical.hash(WorkspaceFile.load(url)), try Canonical.hash(workspace))
    }
    func testEndpointsRejectPublicHostsCredentialsAndTricks() {
        for value in ["https://example.com", "http://127.0.0.1.evil.com", "file:///tmp/model", "http://user:pass@localhost", "http://localhost?token=x", "http://169.254.169.254"] {
            XCTAssertThrowsError(try LocalEndpoint.validate(value))
        }
        XCTAssertNoThrow(try LocalEndpoint.validate("http://192.168.1.2:8105"))
        XCTAssertNoThrow(try LocalAgentClient.loopback("http://127.0.0.1:11434"))
        XCTAssertThrowsError(try LocalAgentClient.loopback("http://192.168.1.2:11434"))
    }
    func testResearchBundleRejectsChangedIntendedUse() throws {
        let item = try source(); var workspace = Workspace(); workspace.cases = [item]
        let artifact = try AnalyticInference.run(.contour, source: item)
        workspace.artifacts = [artifact]
        workspace.reviews = [try ReviewRecord(artifact: artifact, reviewer: "Operator", note: "Synthetic integration inspection", decision: .acceptedForResearch)]
        var bundle = try workspace.researchExport(caseID: item.id)
        try bundle.validate()
        bundle.clinicalUsePermitted = true
        XCTAssertThrowsError(try bundle.validate())
    }
    func testResearchBundleRejectsChangedSourceHash() throws {
        let item = try source(); var workspace = Workspace(); workspace.cases = [item]
        let artifact = try AnalyticInference.run(.contour, source: item)
        workspace.artifacts = [artifact]
        workspace.reviews = [try ReviewRecord(artifact: artifact, reviewer: "Operator", note: "Synthetic integration inspection", decision: .acceptedForResearch)]
        var bundle = try workspace.researchExport(caseID: item.id)
        bundle.sourceHash = "changed"
        XCTAssertThrowsError(try bundle.validate())
    }
}
