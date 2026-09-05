// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "GovernedTPS",
    platforms: [.macOS(.v14)],
    products: [
        .library(name: "TPSCore", targets: ["TPSCore"]),
        .executable(name: "GovernedTPS", targets: ["GovernedTPS"]),
        .executable(name: "tps-check", targets: ["TPSCheck"])
    ],
    targets: [
        .target(name: "TPSCore"),
        .executableTarget(name: "GovernedTPS", dependencies: ["TPSCore"]),
        .executableTarget(name: "TPSCheck", dependencies: ["TPSCore"]),
        .testTarget(name: "TPSCoreTests", dependencies: ["TPSCore"])
    ]
)
