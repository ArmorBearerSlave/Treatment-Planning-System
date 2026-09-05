import XCTest
@testable import TPSCore

final class CERRTests: XCTestCase {
    func fixture() throws -> (PhantomCase, Volume, CERRRequest, CERRReport) {
        var source = try PhantomFactory.analytic(PhantomRecipe(), size: 16); source.mr = nil
        let dose = Volume(grid: source.ct.grid, modality: .dose, units: "Gy", values: Array(repeating: 2, count: source.ct.grid.count))
        let request = try CERRRequest(source: source, dose: dose, doseDescription: "Constant dose software fixture", binWidthGy: 1)
        let records = source.structures.compactMap { structure -> CERRRecord? in
            let n = source.truth.values.filter { $0 == Float(structure.id) }.count
            guard n > 0 else { return nil }
            let cc = Double(n)*source.ct.grid.spacing.reduce(1,*)/1000
            return CERRRecord(id: structure.id, name: structure.name, sampleCount: n, volumeCC: cc, meanGy: 2, d95Gy: 2, maxSampleDifferenceGy: 0, binCentersGy: [0.5,1.5,2.5], differentialVolumeCC: [0,0,cc])
        }
        let evidence = Dictionary(uniqueKeysWithValues: ["getDVHSHA256", "doseHistSHA256", "bridgeSHA256"].map { ($0, String(repeating: "a", count: 64)) })
        let report = CERRReport(schemaVersion: 1, requestID: request.id, requestHash: try Canonical.hash(request), sourceHash: request.sourceHash, doseHash: request.doseHash, clinicalReleaseAllowed: false, records: records, evidence: evidence)
        return (source,dose,request,report)
    }
    func testConstantDoseComparisonAndRoundTrip() throws {
        let (source,dose,request,report) = try fixture()
        let decoded = try JSONDecoder().decode(CERRReport.self, from: Canonical.data(report))
        let rows = try decoded.compare(source: source, dose: dose, request: request)
        XCTAssertFalse(rows.isEmpty)
        for row in rows { XCTAssertEqual(row.nativeMeanGy,2); XCTAssertEqual(row.nativeD95Gy,2); XCTAssertEqual(row.nativeVolumeCC,row.cerr.volumeCC,accuracy:1e-9) }
    }
    func testChangedDoseRequestAndReleaseRejected() throws {
        let (source,dose,request,report) = try fixture()
        var altered = dose; altered.values[0] = 3
        XCTAssertThrowsError(try report.compare(source: source,dose: altered,request: request))
        var changed = request; changed.binWidthGy = 0.5
        XCTAssertThrowsError(try report.compare(source: source,dose: dose,request: changed))
        var released = report; released.clinicalReleaseAllowed = true
        XCTAssertThrowsError(try released.compare(source: source,dose: dose,request: request))
    }
    func testMissingStructureInvalidHistogramAndVolumeRejected() throws {
        let (source,dose,request,report) = try fixture()
        var bad = report; bad.records.removeLast()
        XCTAssertThrowsError(try bad.compare(source: source,dose: dose,request: request))
        bad = report; bad.records.append(bad.records[0])
        XCTAssertThrowsError(try bad.compare(source: source,dose: dose,request: request))
        bad = report; bad.records[0].differentialVolumeCC = [0,0,0]
        XCTAssertThrowsError(try bad.compare(source: source,dose: dose,request: request))
        bad = report; bad.records[0].meanGy = .nan
        XCTAssertThrowsError(try bad.compare(source: source,dose: dose,request: request))
        bad = report; bad.records[0].sampleCount += 1
        XCTAssertThrowsError(try bad.compare(source: source,dose: dose,request: request))
    }
    func testGridUnitsAndBinLimits() throws {
        let (source,dose,_,_) = try fixture()
        var bad = dose; bad.grid.origin[0] += 1
        XCTAssertThrowsError(try CERRRequest(source:source,dose:bad,doseDescription:"test"))
        bad = dose; bad.units = "cGy"
        XCTAssertThrowsError(try CERRRequest(source:source,dose:bad,doseDescription:"test"))
        XCTAssertThrowsError(try CERRRequest(source:source,dose:dose,doseDescription:"test",binWidthGy:0.00001))
        XCTAssertThrowsError(try CERRRequest(source:source,dose:dose,doseDescription:"test",binWidthGy:.nan))
    }
}
