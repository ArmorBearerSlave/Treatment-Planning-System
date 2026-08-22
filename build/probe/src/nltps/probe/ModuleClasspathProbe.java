package nltps.probe;

import jetbrains.mps.classloading.ClassLoaderManager;
import jetbrains.mps.classloading.MPSModuleClassLoader;
import jetbrains.mps.classloading.ModuleClassLoader;
import jetbrains.mps.lang.test.launcher.LaunchTestWorker;
import jetbrains.mps.project.AbstractModule;
import jetbrains.mps.project.facets.JavaModuleFacet;
import jetbrains.mps.smodel.MPSModuleRepository;
import jetbrains.mps.tool.common.Script;
import jetbrains.mps.vfs.IFile;
import org.jetbrains.mps.openapi.language.SLanguage;
import org.jetbrains.mps.openapi.module.SDependency;
import org.jetbrains.mps.openapi.module.SModule;
import org.jetbrains.mps.openapi.module.SModuleFacet;

import java.io.File;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * An instrumented execution of the failing launchtests path -- not a reconstruction of it.
 *
 * <p>Three earlier sketches of this diagnostic each reconstructed some part of the system
 * under observation, and each difference was invisible until the one above it was removed:
 * a CoreWorker base (different environment), a generic mps.run-worker invocation (different
 * module population path), and a probe that re-attempted the failing class load itself
 * (different call). This one differs from the failing run in one respect only: the worker
 * class. Everything else -- Script, project, testmodules, plugins, IdeaEnvironment with
 * test mode, LibraryInitializer and ModulesMiner registration, TestDiscoveryContributor --
 * is inherited by calling super.work().
 *
 * <p>Emission is gated on reproduction. WorkerBase.myErrors is protected, so this subclass
 * can require that the exact failure was recorded before printing a single reading. A probe
 * that runs cleanly and localises nothing has failed whatever its exit code; a probe that
 * localises something without first reproducing the failure has also failed, because its
 * readings would then describe some other execution.
 *
 * <p>Rethrowing is mandatory. LaunchTestWorker's work() ends in finally{failBuild()}, and
 * WorkerBase.failBuild throws BuildFailureException when myErrors is non-empty and
 * failOnError is set; workFromMain turns that into exit code -13. A probe that swallowed it
 * would convert the reproduced defect into a successful build -- the same false green this
 * whole item exists to detect, manufactured by the instrument built to detect it.
 *
 * <p>This class diagnoses MPS-MAT-008. It is not part of the controlled build, and the
 * production test target does not reference it.
 */
public final class ModuleClasspathProbe extends LaunchTestWorker {

  /** The class TestDiscoveryContributor.visitTestRoot fails to load in the run under study. */
  private static final String TARGET_FQN =
      "nltps.modeltests.headless.REA_C_002_evidence_required_for_assessed_verdict_Test";

  /** Both must appear in one recorded error. The FQN alone would let an unrelated failure
      that merely names the same class open the gate. */
  private static final String TARGET_FAILURE = "java.lang.ClassNotFoundException";

  /** The solution launchtests registers, and whose classloader fails to produce the class. */
  private static final String MODULE_NAME = "nltps.modeltests";

  public ModuleClasspathProbe(Script whatToDo) {
    super(whatToDo);
  }

  @Override
  public void work() {
    // Bootstrap control. These are not readings about the defect; they are evidence that
    // the instrument entered the production path at all, and that the environment it
    // inherited is the one the failing run used rather than a lighter one.
    say("BOOTSTRAP_ENTERED=true");
    say("WORKER_CLASS=" + getClass().getName());
    say("WORKER_SUPERCLASS=" + getClass().getSuperclass().getName());
    say("ENVIRONMENT_CLASS="
        + (myEnvironment == null ? "null" : myEnvironment.getClass().getName()));
    say("TARGET_FQN=" + TARGET_FQN);
    int declared = 0;
    for (File testModule : myWhatToDo.getModules()) {
      declared++;
      say("TEST_MODULE=" + testModule.getAbsolutePath() + " exists=" + testModule.isFile());
    }
    say("TEST_MODULE_COUNT=" + declared);

    RuntimeException thrown = null;
    try {
      super.work();
    } catch (RuntimeException ex) {
      thrown = ex;
    }
    say("SUPER_WORK_THREW=" + (thrown != null));
    say("ERRORS_RECORDED=" + myErrors.size());

    // Configuration state, emitted unconditionally and labelled CONFIG_ so it cannot be
    // read as a diagnosis. The gate below governs claims about the failure under study;
    // this is an inventory of what the worker's repository actually contains, which is
    // true or false independently of any failure. It is emitted here because the gate
    // cannot fire on a failure that surfaces through the JUnit report rather than through
    // myErrors -- and a probe that stays silent about a question it can answer is the
    // first acceptance edge, not the second.
    inventory();

    if (!reproducedExactTargetFailure()) {
      say("PROBE_REPRODUCED=false");
      say("NO_READINGS_EMITTED=the observed run is not the run under study");
      if (thrown != null) {
        throw thrown;
      }
      return;
    }

    say("PROBE_REPRODUCED=true");
    measure();

    if (thrown != null) {
      throw thrown;
    }
  }

  /**
   * Every module the worker's repository holds, by deployment status.
   *
   * <p>Enumerating the whole repository rather than resolving the one module currently
   * wanted. The repair sequence foundation, governance, clinicalintent, realization,
   * MPS.OpenAPI has the shape of a wrong lever: each fix reveals the next absence. If the
   * platform modules are missing as a class that is one finding, not five, and supplying
   * them one at a time would be treating a population mechanism as a list.
   */
  private void inventory() {
    MPSModuleRepository repository = getPlatform().findComponent(MPSModuleRepository.class);
    ClassLoaderManager clm = getPlatform().findComponent(ClassLoaderManager.class);
    if (repository == null || clm == null) {
      say("CONFIG_UNAVAILABLE repository=" + repository + " classLoaderManager=" + clm);
      return;
    }
    repository.getModelAccess().runReadAction(() -> {
      Map<String, Integer> byStatus = new TreeMap<String, Integer>();
      List<String> notDeployed = new ArrayList<String>();
      List<String> watched = new ArrayList<String>();
      int total = 0;
      for (SModule candidate : repository.getModules()) {
        total++;
        String candidateName = String.valueOf(candidate.getModuleName());
        String status = String.valueOf(clm.getStatus(candidate));
        Integer seen = byStatus.get(status);
        byStatus.put(status, seen == null ? 1 : seen + 1);
        if (!("DEPLOYED".equals(status))) {
          notDeployed.add(candidateName + "=" + status);
        }
        if (candidateName.startsWith("nltps.") || candidateName.startsWith("MPS.")
            || candidateName.startsWith("jetbrains.mps.lang.test")
            || "JDK".equals(candidateName) || "Annotations".equals(candidateName)) {
          watched.add(candidateName + "=" + status);
        }
      }
      say("CONFIG_REPOSITORY_MODULE_COUNT=" + total);
      say("CONFIG_STATUS_HISTOGRAM=" + byStatus);
      say("CONFIG_WATCHED=" + watched);
      say("CONFIG_NOT_DEPLOYED_COUNT=" + notDeployed.size());
      for (String entry : notDeployed) {
        say("CONFIG_NOT_DEPLOYED=" + entry);
      }
    });
  }

  /**
   * Readings, taken only after the gate. The environment is still alive here: WorkerBase
   * .workFromMain flushes and disposes it in a finally around work(), so catching inside
   * this override leaves the repository, the module and its classloader intact.
   *
   * <p>Each reading is taken through the same accessor the failing code used.
   * TestDiscoveryContributor obtains its loader as ClassLoaderManager.getClassLoader(module)
   * and calls loadClass on it; asking a different loader a similar question would produce a
   * number that describes something else.
   */
  private void measure() {
    MPSModuleRepository repository = getPlatform().findComponent(MPSModuleRepository.class);
    ClassLoaderManager clm = getPlatform().findComponent(ClassLoaderManager.class);
    if (repository == null || clm == null) {
      say("MEASURE_ABORTED repository=" + repository + " classLoaderManager=" + clm);
      return;
    }
    repository.getModelAccess().runReadAction(() -> readInsideReadAction(repository, clm));
  }

  private void readInsideReadAction(MPSModuleRepository repository, ClassLoaderManager clm) {
    SModule module = null;
    for (SModule candidate : repository.getModules()) {
      if (MODULE_NAME.equals(candidate.getModuleName())) {
        module = candidate;
        break;
      }
    }
    if (module == null) {
      say("MODULE_RESOLVED=false name=" + MODULE_NAME);
      return;
    }
    say("MODULE_RESOLVED=true");
    say("MODULE_REF=" + module.getModuleReference());
    say("MODULE_CLASS=" + module.getClass().getName());

    // The branch that would explain everything: getClassLoader returns a system-delegating
    // fallback, not a ModuleClassLoader, when the module's deployment status is not valid.
    try {
      say("MODULE_DEPLOYMENT_STATUS=" + clm.getStatus(module));
    } catch (RuntimeException ex) {
      say("MODULE_DEPLOYMENT_STATUS_UNAVAILABLE=" + ex);
    }

    if (module instanceof AbstractModule) {
      AbstractModule am = (AbstractModule) module;
      say("MODULE_PACKAGED=" + am.isPackaged());
      IFile descriptor = am.getDescriptorFile();
      say("MODULE_DESCRIPTOR=" + (descriptor == null ? "null" : descriptor.getPath()));
      IFile output = am.getOutputPath();
      say("MODULE_OUTPUT_PATH=" + (output == null ? "null" : output.getPath()));
      if (output != null) {
        File physical = new File(output.getPath(), TARGET_FQN.replace('.', '/') + ".class");
        say("PHYSICAL_CLASS=" + physical.getAbsolutePath() + " exists=" + physical.isFile()
            + " bytes=" + (physical.isFile() ? physical.length() : -1));
      }
    } else {
      say("MODULE_NOT_ABSTRACTMODULE=" + module.getClass().getName());
    }

    // The facet step. getOutputPath() above is the *generator* output (source_gen); the
    // compiled classes live under the java facet's classesGen, which is a different accessor
    // and the one that answers whether the class was ever produced.
    StringBuilder facets = new StringBuilder();
    for (SModuleFacet facet : module.getFacets()) {
      if (facets.length() > 0) {
        facets.append(", ");
      }
      facets.append(facet.getFacetType());
    }
    say("MODULE_FACETS=" + facets);

    JavaModuleFacet java = module.getFacet(JavaModuleFacet.class);
    if (java == null) {
      say("JAVA_FACET=absent");
    } else {
      say("JAVA_FACET_COMPILE=" + java.getCompile());
      say("JAVA_FACET_LOAD_CLASSES=" + java.getLoadClasses()
          + " classesAvailable=" + java.getLoadClasses().classesAvailable());
      IFile classesGen = java.getClassesGen();
      say("JAVA_FACET_CLASSES_GEN=" + (classesGen == null ? "null" : classesGen.getPath()));
      if (classesGen != null) {
        File compiled = new File(classesGen.getPath(), TARGET_FQN.replace('.', '/') + ".class");
        say("COMPILED_CLASS=" + compiled.getAbsolutePath() + " exists=" + compiled.isFile()
            + " bytes=" + (compiled.isFile() ? compiled.length() : -1));
      }
    }

    // NOT_IN_REPO reads "The module does not belong to any repository (or depends on such
    // module)". The module itself resolved out of the repository, so the parenthetical is
    // the half worth testing: an unresolved dependency propagates the status.
    int declared = 0;
    int unresolved = 0;
    for (SDependency dependency : module.getDeclaredDependencies()) {
      declared++;
      SModule target = dependency.getTarget();
      if (target == null) {
        unresolved++;
      }
      say("DEPENDENCY=" + dependency.getTargetModule()
          + " scope=" + dependency.getScope()
          + " resolved=" + (target != null)
          + " status=" + (target == null ? "n/a" : String.valueOf(clm.getStatus(target))));
    }
    say("DEPENDENCIES_DECLARED=" + declared + " UNRESOLVED=" + unresolved);

    for (SLanguage language : module.getUsedLanguages()) {
      say("USED_LANGUAGE=" + language);
    }

    MPSModuleClassLoader loader = clm.getClassLoader(module);
    say("CLASSLOADER_CLASS=" + loader.getClass().getName());
    say("CLASSLOADER_IS_MODULE_CLASSLOADER=" + (loader instanceof ModuleClassLoader));
    say("CLASSLOADER_TOSTRING=" + loader);
    say("CLASSLOADER_DISPOSED=" + loader.isDisposed());

    String resourceName = TARGET_FQN.replace('.', '/') + ".class";
    if (loader instanceof ModuleClassLoader) {
      URL own = ((ModuleClassLoader) loader).getOwnResource(resourceName);
      say("OWN_RESOURCE=" + own);
    } else {
      say("OWN_RESOURCE=n/a the loader is not a ModuleClassLoader");
    }

    try {
      Class<?> c = loader.loadOwnClass(TARGET_FQN);
      say("LOAD_OWN_CLASS=OK " + c.getName());
    } catch (Throwable ex) {
      say("LOAD_OWN_CLASS=FAIL " + describe(ex));
    }

    try {
      Class<?> c = loader.loadClass(TARGET_FQN);
      say("LOAD_CLASS=OK " + c.getName());
    } catch (Throwable ex) {
      say("LOAD_CLASS=FAIL " + describe(ex));
    }
  }

  /** Full cause chain. A top-level exception name alone has repeatedly been the wrong half. */
  private static String describe(Throwable ex) {
    StringBuilder sb = new StringBuilder();
    for (Throwable t = ex; t != null; t = t.getCause()) {
      if (sb.length() > 0) {
        sb.append(" <- caused by ");
      }
      sb.append(t.getClass().getName()).append(": ").append(t.getMessage());
      if (t.getCause() == t) {
        break;
      }
    }
    return sb.toString();
  }

  /**
   * True only if one recorded error carries both the exact class name and the class-loading
   * failure. WorkerBase.error(String,Throwable) appends the formatted stack trace to the
   * text before recording it, so a reproduced run stores both in the same entry.
   */
  private boolean reproducedExactTargetFailure() {
    for (String recorded : myErrors) {
      if (recorded.contains(TARGET_FQN) && recorded.contains(TARGET_FAILURE)) {
        return true;
      }
    }
    return false;
  }

  private static void say(String line) {
    System.out.println("[PROBE] " + line);
  }

  public static void main(String[] args) {
    new ModuleClasspathProbe(Script.fromDumpInFile(new File(args[0]))).workFromMain();
  }
}
