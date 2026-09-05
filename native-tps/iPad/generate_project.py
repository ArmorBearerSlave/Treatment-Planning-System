"""Generate a dependency-free Xcode project around the local Swift package core."""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parent
project = root / "GovernedTPSiPad.xcodeproj"
project.mkdir(exist_ok=True)
objects = []

def uid(name):
    return hashlib.sha256(name.encode()).hexdigest()[:24].upper()

def obj(name, body):
    objects.append(f"\t\t{uid(name)} = {{ {body} }};")
    return uid(name)

def refs(names):
    return ", ".join(uid(n) for n in names) + ","

app_files = sorted((root / "Sources").glob("*.swift"))
test_files = sorted((root / "Tests").glob("*.swift")) + [root / "Sources/ReviewModel.swift"]
for p in dict.fromkeys(app_files + test_files):
    rel = p.relative_to(root).as_posix()
    obj(rel, f'isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = "{rel}"; sourceTree = "<group>";')
    obj(rel + ":build", f'isa = PBXBuildFile; fileRef = {uid(rel)};')

obj("appProduct", 'isa = PBXFileReference; explicitFileType = wrapper.application; path = GovernedTPSiPad.app; sourceTree = BUILT_PRODUCTS_DIR;')
obj("testProduct", 'isa = PBXFileReference; explicitFileType = wrapper.cfbundle; path = TPSCoreTests.xctest; sourceTree = BUILT_PRODUCTS_DIR;')
obj("products", f'isa = PBXGroup; children = ({refs(["appProduct", "testProduct"])}); name = Products; sourceTree = "<group>";')
obj("mainGroup", f'isa = PBXGroup; children = ({refs([p.relative_to(root).as_posix() for p in app_files + test_files] + ["products"])}); sourceTree = "<group>";')
obj("package", 'isa = XCLocalSwiftPackageReference; relativePath = ..;')
for target, files, product, product_type in [
    ("app", app_files, "appProduct", "com.apple.product-type.application"),
    ("tests", test_files, "testProduct", "com.apple.product-type.bundle.unit-test"),
]:
    obj(target+"Core", f'isa = XCSwiftPackageProductDependency; package = {uid("package")}; productName = TPSCore;')
    obj(target+"CoreBuild", f'isa = PBXBuildFile; productRef = {uid(target+"Core")};')
    obj(target+"Sources", f'isa = PBXSourcesBuildPhase; buildActionMask = 2147483647; files = ({refs([p.relative_to(root).as_posix()+":build" for p in files])}); runOnlyForDeploymentPostprocessing = 0;')
    obj(target+"Frameworks", f'isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = ({refs([target+"CoreBuild"])}); runOnlyForDeploymentPostprocessing = 0;')
    obj(target+"Resources", 'isa = PBXResourcesBuildPhase; buildActionMask = 2147483647; files = (); runOnlyForDeploymentPostprocessing = 0;')
    for config in ["Debug", "Release"]:
        settings = 'CODE_SIGN_STYLE = Automatic; GENERATE_INFOPLIST_FILE = YES; IPHONEOS_DEPLOYMENT_TARGET = 17.0; TARGETED_DEVICE_FAMILY = 2; SUPPORTED_PLATFORMS = "iphoneos iphonesimulator"; SUPPORTS_MACCATALYST = NO; SWIFT_VERSION = 6.0; ONLY_ACTIVE_ARCH = YES; PRODUCT_NAME = "$(TARGET_NAME)";'
        settings += ' SWIFT_OPTIMIZATION_LEVEL = "'+ ('-Onone' if config == 'Debug' else '-O') +'";'
        if target == "app":
            settings += ' PRODUCT_BUNDLE_IDENTIFIER = org.gcpl.native.ipad; INFOPLIST_KEY_UILaunchScreen_Generation = YES; INFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES; INFOPLIST_KEY_UISupportedInterfaceOrientations = "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";'
        else:
            settings += ' PRODUCT_BUNDLE_IDENTIFIER = org.gcpl.native.ipad.tests;'
        obj(target+config, f'isa = XCBuildConfiguration; buildSettings = {{ {settings} }}; name = {config};')
    obj(target+"Configs", f'isa = XCConfigurationList; buildConfigurations = ({refs([target+"Debug",target+"Release"])}); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release;')
    name = "GovernedTPSiPad" if target == "app" else "TPSCoreTests"
    obj(target, f'isa = PBXNativeTarget; buildConfigurationList = {uid(target+"Configs")}; buildPhases = ({refs([target+"Sources",target+"Frameworks",target+"Resources"])}); buildRules = (); dependencies = (); name = {name}; packageProductDependencies = ({refs([target+"Core"])}); productName = {name}; productReference = {uid(product)}; productType = "{product_type}";')
for config in ["Debug", "Release"]:
    obj("project"+config, f'isa = XCBuildConfiguration; buildSettings = {{ SDKROOT = iphoneos; CLANG_ENABLE_MODULES = YES; }}; name = {config};')
obj("projectConfigs", f'isa = XCConfigurationList; buildConfigurations = ({refs(["projectDebug","projectRelease"])}); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release;')
obj("project", f'isa = PBXProject; attributes = {{ LastUpgradeCheck = 2630; }}; buildConfigurationList = {uid("projectConfigs")}; compatibilityVersion = "Xcode 14.0"; developmentRegion = en; hasScannedForEncodings = 0; knownRegions = (en, Base); mainGroup = {uid("mainGroup")}; packageReferences = ({refs(["package"])}); productRefGroup = {uid("products")}; projectDirPath = ""; projectRoot = ""; targets = ({refs(["app","tests"])});')
(project / "project.pbxproj").write_text('// !$*UTF8*$!\n{\n\tarchiveVersion = 1;\n\tclasses = {};\n\tobjectVersion = 56;\n\tobjects = {\n'+'\n'.join(objects)+'\n\t};\n\trootObject = '+uid("project")+';\n}\n')
scheme_dir = project / "xcshareddata/xcschemes"
scheme_dir.mkdir(parents=True, exist_ok=True)
def build_ref(target, name):
    return f'<BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{uid(target)}" BuildableName="{name}" BlueprintName="{name.split(".")[0]}" ReferencedContainer="container:GovernedTPSiPad.xcodeproj"/>'
(scheme_dir / "GovernedTPSiPad.xcscheme").write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion="2630" version="1.3">
 <BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES"><BuildActionEntries><BuildActionEntry buildForTesting="YES" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES">{build_ref("app", "GovernedTPSiPad.app")}</BuildActionEntry></BuildActionEntries></BuildAction>
 <TestAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" shouldUseLaunchSchemeArgsEnv="YES"><Testables><TestableReference skipped="NO">{build_ref("tests", "TPSCoreTests.xctest")}</TestableReference></Testables></TestAction>
 <LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" allowLocationSimulation="YES"><BuildableProductRunnable runnableDebuggingMode="0">{build_ref("app", "GovernedTPSiPad.app")}</BuildableProductRunnable></LaunchAction>
 <ProfileAction buildConfiguration="Release" shouldUseLaunchSchemeArgsEnv="YES" savedToolIdentifier="" useCustomWorkingDirectory="NO" debugDocumentVersioning="YES"><BuildableProductRunnable runnableDebuggingMode="0">{build_ref("app", "GovernedTPSiPad.app")}</BuildableProductRunnable></ProfileAction>
 <AnalyzeAction buildConfiguration="Debug"/><ArchiveAction buildConfiguration="Release" revealArchiveInOrganizer="YES"/>
</Scheme>
''')
print("Generated GovernedTPSiPad.xcodeproj")
