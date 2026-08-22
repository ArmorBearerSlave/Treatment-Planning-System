<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:2f7d0a13-7a5d-496c-9157-cfd83631b510(nltps.modeltests.headless@tests)">
  <persistence version="9" />
  <languages>
    <use id="8585453e-6bfb-4d80-98de-b16074f1d86c" name="jetbrains.mps.lang.test" version="6" />
    <use id="08070d1a-4999-4bfd-a38c-2b1b3ffd9ef4" name="nltps.realization" version="0" />
    <use id="87311da3-67f4-4168-a5e2-0a32e6781088" name="nltps.foundation" version="0" />
    <use id="f3061a53-9226-4cc5-a443-f952ceaf5816" name="jetbrains.mps.baseLanguage" version="12" />
  </languages>
  <imports>
    <import index="pb3e" ref="r:098128cc-3125-4d66-a424-2542a6566f82(nltps.proof.cases)" />
  </imports>
  <registry>
    <language id="8585453e-6bfb-4d80-98de-b16074f1d86c" name="jetbrains.mps.lang.test">
      <concept id="1216913645126" name="jetbrains.mps.lang.test.structure.NodesTestCase" flags="lg" index="1lH9Xt">
        <property id="2616911529524314943" name="accessMode" index="3DII0k" />
        <child id="1217501822150" name="nodesToCheck" index="1SKRRt" />
        <child id="1217501895093" name="testMethods" index="1SL9yI" />
      </concept>
      <concept id="1216989428737" name="jetbrains.mps.lang.test.structure.TestNode" flags="ng" index="1qefOq">
        <child id="1216989461394" name="nodeToCheck" index="1qenE9" />
      </concept>
      <concept id="1225978065297" name="jetbrains.mps.lang.test.structure.SimpleNodeTest" flags="ng" index="1LZb2c" />
    </language>
    <language id="f3061a53-9226-4cc5-a443-f952ceaf5816" name="jetbrains.mps.baseLanguage">
      <concept id="1068580123132" name="jetbrains.mps.baseLanguage.structure.BaseMethodDeclaration" flags="ng" index="3clF44">
        <child id="1068580123133" name="returnType" index="3clF45" />
        <child id="1068580123135" name="body" index="3clF47" />
      </concept>
      <concept id="1068580123136" name="jetbrains.mps.baseLanguage.structure.StatementList" flags="sn" stub="5293379017992965193" index="3clFbS" />
      <concept id="1068581517677" name="jetbrains.mps.baseLanguage.structure.VoidType" flags="in" index="3cqZAl" />
    </language>
    <language id="87311da3-67f4-4168-a5e2-0a32e6781088" name="nltps.foundation">
      <concept id="1365532761364539167" name="nltps.foundation.structure.GovernedElement" flags="ng" index="3gIvZg">
        <reference id="1365532761364539184" name="lifecycleState" index="3gIvZZ" />
        <child id="1365532761364539181" name="version" index="3gIvZy" />
        <child id="1365532761364539180" name="identifier" index="3gIvZz" />
      </concept>
      <concept id="1365532761364539170" name="nltps.foundation.structure.Version" flags="ng" index="3gIvZH">
        <property id="1365532761364539191" name="value" index="3gIvZS" />
      </concept>
      <concept id="1365532761364539168" name="nltps.foundation.structure.StableId" flags="ng" index="3gIvZJ">
        <property id="1365532761364539186" name="value" index="3gIvZX" />
      </concept>
    </language>
    <language id="08070d1a-4999-4bfd-a38c-2b1b3ffd9ef4" name="nltps.realization">
      <concept id="1365532761387707747" name="nltps.realization.structure.VerificationClaim" flags="ng" index="3hnRmG">
        <property id="1365532761387707755" name="verdict" index="3hnRm$" />
        <property id="1365532761387707754" name="claimName" index="3hnRm_" />
        <reference id="1365532761387707761" name="owningTeam" index="3hnRmY" />
        <reference id="1365532761387707760" name="verifies" index="3hnRmZ" />
      </concept>
    </language>
    <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
      <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ngI" index="TrEIO">
        <property id="1169194664001" name="name" index="TrG5h" />
      </concept>
    </language>
  </registry>
  <node concept="1lH9Xt" id="1bNmcZ3WSdB">
    <property role="3DII0k" value="2hh8MJdVwqX/command" />
    <property role="TrG5h" value="REA_C_002_evidence_required_for_assessed_verdict" />
    <node concept="1qefOq" id="1bNmcZ3WSdC" role="1SKRRt">
      <node concept="3hnRmG" id="1bNmcZ3WSdE" role="1qenE9">
        <property role="3hnRm_" value="headlessSentinelClaim" />
        <property role="3hnRm$" value="1HxEvIlveq9/passed" />
        <ref role="3gIvZZ" to="pb3e:1bNmcZ2uzo_" />
        <ref role="3hnRmZ" to="pb3e:1bNmcZ2uzoK" />
        <ref role="3hnRmY" to="pb3e:1bNmcZ3JGzo" />
        <node concept="3gIvZJ" id="1bNmcZ3WSdH" role="3gIvZz">
          <property role="3gIvZX" value="HEADLESSSENTINEL" />
        </node>
        <node concept="3gIvZH" id="1bNmcZ3WSdI" role="3gIvZy">
          <property role="3gIvZS" value="0.2" />
        </node>
      </node>
    </node>
    <node concept="1LZb2c" id="1bNmcZ3WSdO" role="1SL9yI">
      <property role="TrG5h" value="testAssessedClaimWithoutEvidenceIsRejected" />
      <node concept="3cqZAl" id="1bNmcZ3WSdR" role="3clF45" />
      <node concept="3clFbS" id="1bNmcZ3WSdS" role="3clF47" />
    </node>
  </node>
</model>

