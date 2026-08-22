<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:b5932721-da09-43aa-899b-0b0afcaf35de(nltps.realization.typesystem)">
  <persistence version="9" />
  <languages>
    <use id="7a5dda62-9140-4668-ab76-d5ed1746f2b2" name="jetbrains.mps.lang.typesystem" version="5" />
    <use id="f3061a53-9226-4cc5-a443-f952ceaf5816" name="jetbrains.mps.baseLanguage" version="12" />
    <use id="7866978e-a0f0-4cc7-81bc-4d213d9375e1" name="jetbrains.mps.lang.smodel" version="19" />
    <use id="83888646-71ce-4f1c-9c53-c54016f6ad4f" name="jetbrains.mps.baseLanguage.collections" version="2" />
    <devkit ref="00000000-0000-4000-0000-1de82b3a4936(jetbrains.mps.devkit.aspect.typesystem)" />
  </languages>
  <imports>
    <import index="x4dh" ref="r:6aeac6c0-4966-4224-b0f1-a0cd5adc504c(nltps.realization.structure)" />
    <import index="wyt6" ref="6354ebe7-c22a-4a0f-ac54-50b52ab9b065/java:java.lang(JDK/)" />
  </imports>
  <registry>
    <language id="f3061a53-9226-4cc5-a443-f952ceaf5816" name="jetbrains.mps.baseLanguage">
      <concept id="1202948039474" name="jetbrains.mps.baseLanguage.structure.InstanceMethodCallOperation" flags="nn" index="liA8E" />
      <concept id="1197027756228" name="jetbrains.mps.baseLanguage.structure.DotExpression" flags="nn" index="2OqwBi">
        <child id="1197027771414" name="operand" index="2Oq$k0" />
        <child id="1197027833540" name="operation" index="2OqNvi" />
      </concept>
      <concept id="1070475926800" name="jetbrains.mps.baseLanguage.structure.StringLiteral" flags="nn" index="Xl_RD">
        <property id="1070475926801" name="value" index="Xl_RC" />
      </concept>
      <concept id="1068580123159" name="jetbrains.mps.baseLanguage.structure.IfStatement" flags="nn" index="3clFbJ">
        <child id="1068580123160" name="condition" index="3clFbw" />
        <child id="1068580123161" name="ifTrue" index="3clFbx" />
      </concept>
      <concept id="1068580123136" name="jetbrains.mps.baseLanguage.structure.StatementList" flags="sn" stub="5293379017992965193" index="3clFbS">
        <child id="1068581517665" name="statement" index="3cqZAp" />
      </concept>
      <concept id="1081516740877" name="jetbrains.mps.baseLanguage.structure.NotExpression" flags="nn" index="3fqX7Q">
        <child id="1081516765348" name="expression" index="3fr31v" />
      </concept>
      <concept id="1204053956946" name="jetbrains.mps.baseLanguage.structure.IMethodCall" flags="ngI" index="1ndlxa">
        <reference id="1068499141037" name="baseMethodDeclaration" index="37wK5l" />
        <child id="1068499141038" name="actualArgument" index="37wK5m" />
      </concept>
      <concept id="1081773326031" name="jetbrains.mps.baseLanguage.structure.BinaryOperation" flags="nn" index="3uHJSO">
        <child id="1081773367579" name="rightExpression" index="3uHU7w" />
        <child id="1081773367580" name="leftExpression" index="3uHU7B" />
      </concept>
      <concept id="1080120340718" name="jetbrains.mps.baseLanguage.structure.AndExpression" flags="nn" index="1Wc70l" />
    </language>
    <language id="7a5dda62-9140-4668-ab76-d5ed1746f2b2" name="jetbrains.mps.lang.typesystem">
      <concept id="1175517767210" name="jetbrains.mps.lang.typesystem.structure.ReportErrorStatement" flags="nn" index="2MkqsV">
        <child id="1175517851849" name="errorString" index="2MkJ7o" />
      </concept>
      <concept id="1195213580585" name="jetbrains.mps.lang.typesystem.structure.AbstractCheckingRule" flags="ig" index="18hYwZ">
        <child id="1195213635060" name="body" index="18ibNy" />
      </concept>
      <concept id="1195214364922" name="jetbrains.mps.lang.typesystem.structure.NonTypesystemRule" flags="ig" index="18kY7G" />
      <concept id="3937244445246642777" name="jetbrains.mps.lang.typesystem.structure.AbstractReportStatement" flags="ng" index="1urrMJ">
        <child id="3937244445246642781" name="nodeToReport" index="1urrMF" />
      </concept>
      <concept id="1174642788531" name="jetbrains.mps.lang.typesystem.structure.ConceptReference" flags="ig" index="1YaCAy">
        <reference id="1174642800329" name="concept" index="1YaFvo" />
      </concept>
      <concept id="1174648085619" name="jetbrains.mps.lang.typesystem.structure.AbstractRule" flags="ng" index="1YuPPy">
        <child id="1174648101952" name="applicableNode" index="1YuTPh" />
      </concept>
      <concept id="1174650418652" name="jetbrains.mps.lang.typesystem.structure.ApplicableNodeReference" flags="nn" index="1YBJjd">
        <reference id="1174650432090" name="applicableNode" index="1YBMHb" />
      </concept>
    </language>
    <language id="7866978e-a0f0-4cc7-81bc-4d213d9375e1" name="jetbrains.mps.lang.smodel">
      <concept id="1966870290083281362" name="jetbrains.mps.lang.smodel.structure.EnumMember_NameOperation" flags="ng" index="24Tkf9" />
      <concept id="1138056022639" name="jetbrains.mps.lang.smodel.structure.SPropertyAccess" flags="nn" index="3TrcHB">
        <reference id="1138056395725" name="property" index="3TsBF5" />
      </concept>
      <concept id="1138056282393" name="jetbrains.mps.lang.smodel.structure.SLinkListAccess" flags="nn" index="3Tsc0h">
        <reference id="1138056546658" name="link" index="3TtcxE" />
      </concept>
    </language>
    <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
      <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ngI" index="TrEIO">
        <property id="1169194664001" name="name" index="TrG5h" />
      </concept>
    </language>
    <language id="83888646-71ce-4f1c-9c53-c54016f6ad4f" name="jetbrains.mps.baseLanguage.collections">
      <concept id="1165530316231" name="jetbrains.mps.baseLanguage.collections.structure.IsEmptyOperation" flags="nn" index="1v1jN8" />
    </language>
  </registry>
  <node concept="18kY7G" id="1bNmcZ3JHXD">
    <property role="TrG5h" value="REA_C_002_verification_claim_binds_evidence" />
    <node concept="1YaCAy" id="1bNmcZ3JHXG" role="1YuTPh">
      <property role="TrG5h" value="claim" />
      <ref role="1YaFvo" to="x4dh:1bNmcZ3F2Pz" resolve="VerificationClaim" />
    </node>
    <node concept="3clFbS" id="1bNmcZ3TkxY" role="18ibNy">
      <node concept="3clFbJ" id="1bNmcZ3TkxZ" role="3cqZAp">
        <node concept="1Wc70l" id="1bNmcZ3Tky2" role="3clFbw">
          <node concept="1Wc70l" id="1bNmcZ3Tky5" role="3uHU7B">
            <node concept="3fqX7Q" id="1bNmcZ3Tky8" role="3uHU7B">
              <node concept="2OqwBi" id="1bNmcZ3Tkya" role="3fr31v">
                <node concept="2OqwBi" id="1bNmcZ3Tkyd" role="2Oq$k0">
                  <node concept="2OqwBi" id="1bNmcZ3Tkyg" role="2Oq$k0">
                    <node concept="1YBJjd" id="1bNmcZ3Tkyj" role="2Oq$k0">
                      <ref role="1YBMHb" node="1bNmcZ3JHXG" resolve="claim" />
                    </node>
                    <node concept="3TrcHB" id="1bNmcZ3Tkyk" role="2OqNvi">
                      <ref role="3TsBF5" to="x4dh:1bNmcZ3F2PF" resolve="verdict" />
                    </node>
                  </node>
                  <node concept="24Tkf9" id="1bNmcZ3Tkyl" role="2OqNvi" />
                </node>
                <node concept="liA8E" id="1bNmcZ3Tkym" role="2OqNvi">
                  <ref role="37wK5l" to="wyt6:~String.equals(java.lang.Object)" resolve="equals" />
                  <node concept="Xl_RD" id="1bNmcZ3Tkyn" role="37wK5m">
                    <property role="Xl_RC" value="not_assessed" />
                  </node>
                </node>
              </node>
            </node>
            <node concept="2OqwBi" id="1bNmcZ3Tkyo" role="3uHU7w">
              <node concept="2OqwBi" id="1bNmcZ3Tkyr" role="2Oq$k0">
                <node concept="1YBJjd" id="1bNmcZ3Tkyu" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ3JHXG" resolve="claim" />
                </node>
                <node concept="3Tsc0h" id="1bNmcZ3Tkyv" role="2OqNvi">
                  <ref role="3TtcxE" to="x4dh:1bNmcZ3F2PH" />
                </node>
              </node>
              <node concept="1v1jN8" id="1bNmcZ3Tkyw" role="2OqNvi" />
            </node>
          </node>
          <node concept="2OqwBi" id="1bNmcZ3Tkyx" role="3uHU7w">
            <node concept="2OqwBi" id="1bNmcZ3Tky$" role="2Oq$k0">
              <node concept="1YBJjd" id="1bNmcZ3TkyB" role="2Oq$k0">
                <ref role="1YBMHb" node="1bNmcZ3JHXG" resolve="claim" />
              </node>
              <node concept="3Tsc0h" id="1bNmcZ3TkyC" role="2OqNvi">
                <ref role="3TtcxE" to="x4dh:1bNmcZ3F2PI" />
              </node>
            </node>
            <node concept="1v1jN8" id="1bNmcZ3TkyD" role="2OqNvi" />
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ3TkyE" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ3TkyF" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ3TkyI" role="2MkJ7o">
              <property role="Xl_RC" value="REA-C-002: a VerificationClaim whose verdict is an assessed result must bind at least one ExecutableSuiteRef or at least one ManualEvidenceRef; an assessed claim supported by neither asserts a result nothing can be traced to. A claim whose verdict is not_assessed may carry no evidence, but must not satisfy a verification, approval, promotion or release prerequisite." />
            </node>
            <node concept="1YBJjd" id="1bNmcZ3TkyJ" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ3JHXG" resolve="claim" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="18kY7G" id="1bNmcZ3JHXH">
    <property role="TrG5h" value="REA_C_003_passed_verdict_requires_evidence" />
    <node concept="1YaCAy" id="1bNmcZ3JHXK" role="1YuTPh">
      <property role="TrG5h" value="claim" />
      <ref role="1YaFvo" to="x4dh:1bNmcZ3F2Pz" resolve="VerificationClaim" />
    </node>
    <node concept="3clFbS" id="1bNmcZ3JHZa" role="18ibNy">
      <node concept="3clFbJ" id="1bNmcZ3JHZb" role="3cqZAp">
        <node concept="1Wc70l" id="1bNmcZ3JHZe" role="3clFbw">
          <node concept="1Wc70l" id="1bNmcZ3JHZh" role="3uHU7B">
            <node concept="2OqwBi" id="1bNmcZ3JHZk" role="3uHU7B">
              <node concept="2OqwBi" id="1bNmcZ3JHZn" role="2Oq$k0">
                <node concept="2OqwBi" id="1bNmcZ3JHZq" role="2Oq$k0">
                  <node concept="1YBJjd" id="1bNmcZ3JHZt" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ3JHXK" resolve="claim" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ3JHZu" role="2OqNvi">
                    <ref role="3TsBF5" to="x4dh:1bNmcZ3F2PF" resolve="verdict" />
                  </node>
                </node>
                <node concept="24Tkf9" id="1bNmcZ3JHZv" role="2OqNvi" />
              </node>
              <node concept="liA8E" id="1bNmcZ3JHZw" role="2OqNvi">
                <ref role="37wK5l" to="wyt6:~String.equals(java.lang.Object)" resolve="equals" />
                <node concept="Xl_RD" id="1bNmcZ3JHZx" role="37wK5m">
                  <property role="Xl_RC" value="passed" />
                </node>
              </node>
            </node>
            <node concept="2OqwBi" id="1bNmcZ3JHZ$" role="3uHU7w">
              <node concept="2OqwBi" id="1bNmcZ3JHZB" role="2Oq$k0">
                <node concept="1YBJjd" id="1bNmcZ3JHZE" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ3JHXK" resolve="claim" />
                </node>
                <node concept="3Tsc0h" id="1bNmcZ3JHZF" role="2OqNvi">
                  <ref role="3TtcxE" to="x4dh:1bNmcZ3F2PH" resolve="executableSuites" />
                </node>
              </node>
              <node concept="1v1jN8" id="1bNmcZ3JHZG" role="2OqNvi" />
            </node>
          </node>
          <node concept="2OqwBi" id="1bNmcZ3JHZH" role="3uHU7w">
            <node concept="2OqwBi" id="1bNmcZ3JHZK" role="2Oq$k0">
              <node concept="1YBJjd" id="1bNmcZ3JHZN" role="2Oq$k0">
                <ref role="1YBMHb" node="1bNmcZ3JHXK" resolve="claim" />
              </node>
              <node concept="3Tsc0h" id="1bNmcZ3JHZO" role="2OqNvi">
                <ref role="3TtcxE" to="x4dh:1bNmcZ3F2PI" resolve="manualEvidence" />
              </node>
            </node>
            <node concept="1v1jN8" id="1bNmcZ3JHZP" role="2OqNvi" />
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ3JHZQ" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ3JHZR" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ3JHZU" role="2MkJ7o">
              <property role="Xl_RC" value="REA-C-003: a verdict is stated, never inferred; a VerificationClaim whose verdict is passed must bind evidence, and no verdict is computed from the records beneath it" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ3JHZV" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ3JHXK" resolve="claim" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
</model>

