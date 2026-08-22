package nltps.probe;

import jetbrains.mps.build.ant.junit.LaunchTestTask;
import org.apache.tools.ant.BuildException;

import java.io.File;
import java.util.LinkedHashSet;
import java.util.Set;

/**
 * The production &lt;launchtests&gt; task with exactly one observable difference: one extra
 * jar on the forked JVM's classpath.
 *
 * <p>Why a subclass rather than a flag. MpsLoadTask builds the forked process classpath
 * from two sources -- whatever {@code calculateClassPath(boolean)} returns, plus the Ant
 * JVM's own {@code java.class.path} minus JDK and filtered entries. Ant's {@code -lib}
 * option adds jars to <em>Ant's classloader</em>, which is neither of those. A probe
 * launched that way could fail to load for a reason that has nothing to do with the defect
 * under investigation, and the failure would look like a finding.
 *
 * <p>What this preserves by not reimplementing it: LaunchTestTask.init (openPackages,
 * failOnError, fork), the two IDEA jvm args set in its constructor, the mps-testing
 * launcher-support jar its own calculateClassPath adds, filterClasspathEntry's exclusion
 * of incompatible JUnit 3 and 4 jars, finalizeScriptSettings' transfer of test modules
 * into the Script, the stream handler, and the LaunchTestWorker default that the probe
 * then overrides through the inherited public setWorker.
 *
 * <p>This class exists only to diagnose MPS-MAT-008 and is not part of the controlled
 * build. The production target does not reference it.
 */
public final class ProbeLaunchTestTask extends LaunchTestTask {

  private File myProbeJar;

  public void setProbeJar(File probeJar) {
    myProbeJar = probeJar;
  }

  @Override
  protected Set<File> calculateClassPath(boolean fork) {
    if (myProbeJar == null || !myProbeJar.isFile()) {
      // Refused rather than reported. A probe whose own class is absent from the fork
      // classpath fails with a ClassNotFoundException that is indistinguishable in shape
      // from the defect it was built to observe.
      throw new BuildException("probeJar missing or not a file: " + myProbeJar);
    }
    LinkedHashSet<File> cp = new LinkedHashSet<>(super.calculateClassPath(fork));
    cp.add(myProbeJar);
    return cp;
  }
}
