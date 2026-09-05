import XCTest
@testable import TPSCore

final class MatRadTests: XCTestCase {
    func source() throws -> PhantomCase { try PhantomFactory.analytic(PhantomRecipe(), size: 16) }
    func result(_ source: PhantomCase, _ request: MatRadRequest) throws -> MatRadResult {
        MatRadResult(schemaVersion: 1, requestID: request.id, requestHash: try Canonical.hash(request), sourceHash: request.sourceHash,
                     clinicalReleaseAllowed: false, doseBasis: "physical-course-Gy",
                     volume: Volume(grid: source.ct.grid, modality: .dose, units: "Gy", values: Array(repeating: 2, count: source.ct.grid.count)),
                     evidence: ["matRadVersion":"test", "optimizerConverged":"true"])
    }
    func testValidProposalAndStableRoundTrip() throws {
        let source = try source(), request = try MatRadRequest(source: self.source(), settings: MatRadSettings(targetID: 2))
        // Bind to the actual source (the fixture factory creates fresh case IDs).
        let bound = try MatRadRequest(source: source, settings: request.settings)
        let decoded = try JSONDecoder().decode(MatRadRequest.self, from: Canonical.data(bound))
        XCTAssertEqual(try Canonical.hash(bound), try Canonical.hash(decoded))
        let output = try result(source, bound)
        let artifact = try output.artifact(source: source, request: bound)
        try artifact.validate(for: source)
        XCTAssertEqual(artifact.operation, .predictDose)
        XCTAssertTrue(artifact.modelID.hasPrefix("matRad/"))
        let restored = try JSONDecoder().decode(Artifact.self, from: Canonical.data(artifact))
        XCTAssertEqual(restored.planningEvidence?["doseBasis"], "physical-course-Gy")
        XCTAssertEqual(restored.planningEvidence?["requestHash"], try Canonical.hash(bound))
    }
    func testObliqueAndInvalidObjectivesRejected() throws {
        var source = try source()
        var settings = MatRadSettings(targetID: 2)
        settings.gantryAngles = [0,0]
        XCTAssertThrowsError(try settings.validate(for: source))
        settings.gantryAngles = [0]; settings.organs = [MatRadObjective(id: 2)]
        XCTAssertThrowsError(try settings.validate(for: source))
        settings.organs = []; settings.targetGy = .nan
        XCTAssertThrowsError(try settings.validate(for: source))
        settings.targetGy = 2
        source.ct.grid.direction = [0,-1,0,1,0,0,0,0,1]
        source.truth.grid = source.ct.grid
        source.mr = nil
        XCTAssertThrowsError(try settings.validate(for: source))
    }
    func testWrongCaseAndChangedRequestRejected() throws {
        let source = try source(), request = try MatRadRequest(source: self.source(), settings: MatRadSettings(targetID: 2))
        let output = try result(source, request)
        XCTAssertThrowsError(try output.artifact(source: source, request: request))
        var bound = try MatRadRequest(source: source, settings: MatRadSettings(targetID: 2))
        let valid = try result(source, bound)
        bound.settings.fractions = 2
        XCTAssertThrowsError(try valid.artifact(source: source, request: bound))
    }
    func testWrongGridUnitsAndNonconvergenceRejected() throws {
        let source = try source()
        let request = try MatRadRequest(source: source, settings: MatRadSettings(targetID: 2))
        var output = try result(source, request)
        output.volume.grid.origin[0] += 1
        XCTAssertThrowsError(try output.artifact(source: source, request: request))
        output = try result(source, request); output.doseBasis = "per-fraction"
        XCTAssertThrowsError(try output.artifact(source: source, request: request))
        output = try result(source, request); output.evidence["optimizerConverged"] = "false"
        XCTAssertThrowsError(try output.artifact(source: source, request: request))
        output = try result(source, request); output.clinicalReleaseAllowed = true
        XCTAssertThrowsError(try output.artifact(source: source, request: request))
        output = try result(source, request); output.volume.values[0] = -1
        XCTAssertThrowsError(try output.artifact(source: source, request: request))
    }
}
