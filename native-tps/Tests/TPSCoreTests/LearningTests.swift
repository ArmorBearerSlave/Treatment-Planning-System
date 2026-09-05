import XCTest
@testable import TPSCore

final class LearningTests: XCTestCase {
    func fixture(_ group: String) throws -> PhantomCase { try PhantomFactory.analytic(PhantomRecipe(anatomyID: group), size: 16) }
    func testPartitionKeepsVariantsTogetherAndIsOrderIndependent() throws {
        let sources = try ["a","a","b","c","d","e"].map(fixture)
        let cases = sources.map { LearningCase(source: $0, url: URL(fileURLWithPath: "/unused"), fileSHA256: "test", anatomyGroup: $0.recipe.anatomyID) }
        let split = try DatasetPartition.make(cases: cases, seed: 42)
        let reversed = try DatasetPartition.make(cases: cases.reversed(), seed: 42)
        XCTAssertEqual(split.assignments, reversed.assignments)
        XCTAssertEqual(split.assignments[cases[0].id.uuidString], split.assignments[cases[1].id.uuidString])
        XCTAssertEqual(Set(split.assignments.values), Set(["train","validation","test"]))
        let bytes = try Canonical.data(split)
        let restored = try JSONDecoder().decode(DatasetPartition.self, from: bytes)
        XCTAssertEqual(try Canonical.hash(split), try Canonical.hash(restored))
    }
    func testMissingGroupsAndTooFewIndependentAnatomiesRejected() throws {
        let source = try fixture("a")
        var entry = LearningCase(source: source, url: URL(fileURLWithPath: "/unused"), fileSHA256: "test")
        XCTAssertThrowsError(try DatasetPartition.make(cases: [entry], seed: 42))
        entry.anatomyGroup = "a"
        XCTAssertThrowsError(try DatasetPartition.make(cases: [entry], seed: 42))
    }
    func testExperimentHashSurvivesSaveAndReload() throws {
        let sources = try ["a","b","c"].map(fixture)
        let entries = sources.map { LearningCase(source: $0, url: URL(fileURLWithPath: "/unused"), fileSHA256: "test", anatomyGroup: $0.recipe.anatomyID) }
        let partition = try DatasetPartition.make(cases: entries, seed: 42)
        let model = try GaussianContourModel.fit([sources[0]], varianceFloor: 0.01)
        let result = LearningExperiment(cases: entries, partition: partition, model: model, selectedVarianceFloor: 0.01, validation: [])
        let restored = try JSONDecoder().decode(LearningExperiment.self, from: Canonical.data(result))
        XCTAssertEqual(try Canonical.hash(result), try Canonical.hash(restored))
    }
    func testPerfectContourMetricsAndWrongGrid() throws {
        let source = try fixture("a")
        let result = try CaseEvaluation.contours(source: source, prediction: source.truth, split: "test")
        XCTAssertEqual(result.meanDice, 1)
        XCTAssertTrue(result.metrics.allSatisfy { $0.predictedCC == $0.referenceCC })
        XCTAssertTrue(result.metrics.compactMap(\.centroidErrorMM).allSatisfy { $0 == 0 })
        var wrong = source.truth; wrong.grid.frameID = "wrong"
        XCTAssertThrowsError(try CaseEvaluation.contours(source: source, prediction: wrong, split: "test"))
    }
    func testLearnedPredictionDoesNotReadTargetLabels() throws {
        let source = try fixture("a")
        let model = try GaussianContourModel.fit([source], varianceFloor: 0.01)
        var changed = source; changed.truth.values = Array(repeating: 0, count: source.truth.values.count)
        XCTAssertEqual(try model.predict(source).values, try model.predict(changed).values)
        XCTAssertEqual(model.trainingSourceHashes, [try Canonical.hash(source)])
    }
    func testEmptyLabelsNotReportedAsPerfect() throws {
        var source = try fixture("a")
        source.truth.values = Array(repeating: 0, count: source.truth.values.count)
        let result = try CaseEvaluation.contours(source: source, prediction: source.truth, split: "test")
        XCTAssertNil(result.meanDice)
        XCTAssertTrue(result.metrics.allSatisfy { $0.dice == nil })
    }
}
