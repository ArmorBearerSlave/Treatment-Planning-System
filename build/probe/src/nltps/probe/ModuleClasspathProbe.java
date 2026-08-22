package nltps.probe;

import jetbrains.mps.lang.test.launcher.LaunchTestWorker;
import jetbrains.mps.tool.common.Script;

import java.io.File;

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

    if (!reproducedExactTargetFailure()) {
      say("PROBE_REPRODUCED=false");
      say("NO_READINGS_EMITTED=the observed run is not the run under study");
      if (thrown != null) {
        throw thrown;
      }
      return;
    }

    say("PROBE_REPRODUCED=true");
    say("READINGS=0 stage-1 bootstrap control only; measurement not implemented yet");

    if (thrown != null) {
      throw thrown;
    }
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
