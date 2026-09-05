import XCTest
import TPSCore

final class TabletReviewTests: XCTestCase {
    func testReviewCannotMoveToAnotherCase() throws {
        let a = try PhantomFactory.analytic(PhantomRecipe(), size: 16)
        let b = try PhantomFactory.analytic(PhantomRecipe(), size: 16)
        let review = TabletReview(sourceHash: try Canonical.hash(a), caseID: a.id, caseName: a.name)
        XCTAssertNoThrow(try review.validate(source: a))
        XCTAssertThrowsError(try review.validate(source: b))
    }
    func testRejectsInvalidMarkupSliceAndClinicalFlag() throws {
        let source = try PhantomFactory.analytic(PhantomRecipe(), size: 16)
        var review = TabletReview(sourceHash: try Canonical.hash(source), caseID: source.id, caseName: source.name)
        review.drawings["2:16"] = Data([0])
        XCTAssertThrowsError(try review.validate(source: source))
        review.drawings = [:]; review.clinicalUsePermitted = true
        XCTAssertThrowsError(try review.validate(source: source))
    }
}
