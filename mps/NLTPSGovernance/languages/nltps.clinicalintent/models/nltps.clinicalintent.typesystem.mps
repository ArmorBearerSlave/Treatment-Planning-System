<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:ca8dbc2e-1ece-4d45-ae95-292ad0508b55(nltps.clinicalintent.typesystem)">
  <persistence version="9" />
  <languages>
    <use id="7a5dda62-9140-4668-ab76-d5ed1746f2b2" name="jetbrains.mps.lang.typesystem" version="5" />
    <use id="f3061a53-9226-4cc5-a443-f952ceaf5816" name="jetbrains.mps.baseLanguage" version="12" />
    <use id="83888646-71ce-4f1c-9c53-c54016f6ad4f" name="jetbrains.mps.baseLanguage.collections" version="2" />
    <use id="7866978e-a0f0-4cc7-81bc-4d213d9375e1" name="jetbrains.mps.lang.smodel" version="19" />
    <devkit ref="00000000-0000-4000-0000-1de82b3a4936(jetbrains.mps.devkit.aspect.typesystem)" />
  </languages>
  <imports>
    <import index="jb6s" ref="r:4741d84b-80d0-4a09-848d-cb03c7811725(nltps.clinicalintent.structure)" />
    <import index="5q6" ref="r:07b10a47-b937-4aa9-ad53-c2e3280bb0f3(nltps.foundation.structure)" />
    <import index="wyt6" ref="6354ebe7-c22a-4a0f-ac54-50b52ab9b065/java:java.lang(JDK/)" />
  </imports>
  <registry>
    <language id="f3061a53-9226-4cc5-a443-f952ceaf5816" name="jetbrains.mps.baseLanguage">
      <concept id="1202948039474" name="jetbrains.mps.baseLanguage.structure.InstanceMethodCallOperation" flags="nn" index="liA8E" />
      <concept id="1154032098014" name="jetbrains.mps.baseLanguage.structure.AbstractLoopStatement" flags="nn" index="2LF5Ji">
        <child id="1154032183016" name="body" index="2LFqv$" />
      </concept>
      <concept id="1197027756228" name="jetbrains.mps.baseLanguage.structure.DotExpression" flags="nn" index="2OqwBi">
        <child id="1197027771414" name="operand" index="2Oq$k0" />
        <child id="1197027833540" name="operation" index="2OqNvi" />
      </concept>
      <concept id="1070475926800" name="jetbrains.mps.baseLanguage.structure.StringLiteral" flags="nn" index="Xl_RD">
        <property id="1070475926801" name="value" index="Xl_RC" />
      </concept>
      <concept id="1070534058343" name="jetbrains.mps.baseLanguage.structure.NullLiteral" flags="nn" index="10Nm6u" />
      <concept id="1068580123152" name="jetbrains.mps.baseLanguage.structure.EqualsExpression" flags="nn" index="3clFbC" />
      <concept id="1068580123159" name="jetbrains.mps.baseLanguage.structure.IfStatement" flags="nn" index="3clFbJ">
        <child id="1068580123160" name="condition" index="3clFbw" />
        <child id="1068580123161" name="ifTrue" index="3clFbx" />
      </concept>
      <concept id="1068580123136" name="jetbrains.mps.baseLanguage.structure.StatementList" flags="sn" stub="5293379017992965193" index="3clFbS">
        <child id="1068581517665" name="statement" index="3cqZAp" />
      </concept>
      <concept id="1068581242875" name="jetbrains.mps.baseLanguage.structure.PlusExpression" flags="nn" index="3cpWs3" />
      <concept id="1079359253375" name="jetbrains.mps.baseLanguage.structure.ParenthesizedExpression" flags="nn" index="1eOMI4">
        <child id="1079359253376" name="expression" index="1eOMHV" />
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
      <concept id="1073239437375" name="jetbrains.mps.baseLanguage.structure.NotEqualsExpression" flags="nn" index="3y3z36" />
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
      <concept id="1138056143562" name="jetbrains.mps.lang.smodel.structure.SLinkAccess" flags="nn" index="3TrEf2">
        <reference id="1138056516764" name="link" index="3Tt5mk" />
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
      <concept id="1153943597977" name="jetbrains.mps.baseLanguage.collections.structure.ForEachStatement" flags="nn" index="2Gpval">
        <child id="1153944400369" name="variable" index="2Gsz3X" />
        <child id="1153944424730" name="inputSequence" index="2GsD0m" />
      </concept>
      <concept id="1153944193378" name="jetbrains.mps.baseLanguage.collections.structure.ForEachVariable" flags="nr" index="2GrKxI" />
      <concept id="1153944233411" name="jetbrains.mps.baseLanguage.collections.structure.ForEachVariableReference" flags="nn" index="2GrUjf">
        <reference id="1153944258490" name="variable" index="2Gs0qQ" />
      </concept>
      <concept id="1165530316231" name="jetbrains.mps.baseLanguage.collections.structure.IsEmptyOperation" flags="nn" index="1v1jN8" />
    </language>
  </registry>
  <node concept="18kY7G" id="1bNmcZ3aehC">
    <property role="TrG5h" value="CLI_C_001_ai_creatable_excludes_A4" />
    <node concept="1YaCAy" id="1bNmcZ3aehF" role="1YuTPh">
      <property role="TrG5h" value="pid" />
      <ref role="1YaFvo" to="jb6s:1bNmcZ2XUA$" resolve="PlanIntentDefinition" />
    </node>
    <node concept="3clFbS" id="1bNmcZ3aehG" role="18ibNy">
      <node concept="2Gpval" id="1bNmcZ3aehH" role="3cqZAp">
        <node concept="2GrKxI" id="1bNmcZ3aehL" role="2Gsz3X">
          <property role="TrG5h" value="act" />
        </node>
        <node concept="2OqwBi" id="1bNmcZ3aehM" role="2GsD0m">
          <node concept="1YBJjd" id="1bNmcZ3aehP" role="2Oq$k0">
            <ref role="1YBMHb" node="1bNmcZ3aehF" resolve="pid" />
          </node>
          <node concept="3Tsc0h" id="1bNmcZ3aehQ" role="2OqNvi">
            <ref role="3TtcxE" to="jb6s:1bNmcZ2XUAO" resolve="actions" />
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ3aehR" role="2LFqv$">
          <node concept="3clFbJ" id="1bNmcZ3aehS" role="3cqZAp">
            <node concept="1Wc70l" id="1bNmcZ3aehV" role="3clFbw">
              <node concept="2OqwBi" id="1bNmcZ3aehY" role="3uHU7B">
                <node concept="1YBJjd" id="1bNmcZ3aei1" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ3aehF" resolve="pid" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ3aei2" role="2OqNvi">
                  <ref role="3TsBF5" to="jb6s:1bNmcZ2XUAM" resolve="aiCreatable" />
                </node>
              </node>
              <node concept="2OqwBi" id="1bNmcZ3aei3" role="3uHU7w">
                <node concept="2OqwBi" id="1bNmcZ3aei6" role="2Oq$k0">
                  <node concept="2OqwBi" id="1bNmcZ3aei9" role="2Oq$k0">
                    <node concept="2GrUjf" id="1bNmcZ3aeic" role="2Oq$k0">
                      <ref role="2Gs0qQ" node="1bNmcZ3aehL" resolve="act" />
                    </node>
                    <node concept="3TrcHB" id="1bNmcZ3aeid" role="2OqNvi">
                      <ref role="3TsBF5" to="jb6s:1bNmcZ2XU_J" resolve="autonomyLevel" />
                    </node>
                  </node>
                  <node concept="24Tkf9" id="1bNmcZ3aeie" role="2OqNvi" />
                </node>
                <node concept="liA8E" id="1bNmcZ3aeif" role="2OqNvi">
                  <ref role="37wK5l" to="wyt6:~String.equals(java.lang.Object)" resolve="equals" />
                  <node concept="Xl_RD" id="1bNmcZ3aeig" role="37wK5m">
                    <property role="Xl_RC" value="A4_authorize_or_deliver" />
                  </node>
                </node>
              </node>
            </node>
            <node concept="3clFbS" id="1bNmcZ3aeih" role="3clFbx">
              <node concept="2MkqsV" id="1bNmcZ3aeii" role="3cqZAp">
                <node concept="Xl_RD" id="1bNmcZ3aeil" role="2MkJ7o">
                  <property role="Xl_RC" value="CLI-C-001: an AI-creatable PlanIntentDefinition may not contain an ActionDefinition at autonomy level A4_authorize_or_deliver" />
                </node>
                <node concept="2GrUjf" id="1bNmcZ3aeim" role="1urrMF">
                  <ref role="2Gs0qQ" node="1bNmcZ3aehL" resolve="act" />
                </node>
              </node>
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="18kY7G" id="1bNmcZ3ae_o">
    <property role="TrG5h" value="CLI_C_002_no_patient_identifying_name" />
    <node concept="1YaCAy" id="1bNmcZ3ae_r" role="1YuTPh">
      <property role="TrG5h" value="pid" />
      <ref role="1YaFvo" to="jb6s:1bNmcZ2XUA$" resolve="PlanIntentDefinition" />
    </node>
    <node concept="3clFbS" id="1bNmcZ3ae_s" role="18ibNy">
      <node concept="3clFbJ" id="1bNmcZ3ae_t" role="3cqZAp">
        <node concept="1Wc70l" id="1bNmcZ3ae_w" role="3clFbw">
          <node concept="1Wc70l" id="1bNmcZ3ae_z" role="3uHU7B">
            <node concept="3y3z36" id="1bNmcZ3ae_A" role="3uHU7B">
              <node concept="2OqwBi" id="1bNmcZ3ae_D" role="3uHU7B">
                <node concept="1YBJjd" id="1bNmcZ3ae_G" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ3ae_r" resolve="pid" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ3ae_H" role="2OqNvi">
                  <ref role="3TsBF5" to="jb6s:1bNmcZ2XUAL" resolve="name" />
                </node>
              </node>
              <node concept="10Nm6u" id="1bNmcZ3ae_I" role="3uHU7w" />
            </node>
            <node concept="3fqX7Q" id="1bNmcZ3ae_J" role="3uHU7w">
              <node concept="2OqwBi" id="1bNmcZ3ae_L" role="3fr31v">
                <node concept="2OqwBi" id="1bNmcZ3ae_O" role="2Oq$k0">
                  <node concept="1YBJjd" id="1bNmcZ3ae_R" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ3ae_r" resolve="pid" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ3ae_S" role="2OqNvi">
                    <ref role="3TsBF5" to="jb6s:1bNmcZ2XUAL" resolve="name" />
                  </node>
                </node>
                <node concept="liA8E" id="1bNmcZ3ae_T" role="2OqNvi">
                  <ref role="37wK5l" to="wyt6:~String.isEmpty()" resolve="isEmpty" />
                </node>
              </node>
            </node>
          </node>
          <node concept="2OqwBi" id="1bNmcZ3ae_U" role="3uHU7w">
            <node concept="2OqwBi" id="1bNmcZ3ae_X" role="2Oq$k0">
              <node concept="1YBJjd" id="1bNmcZ3aeA0" role="2Oq$k0">
                <ref role="1YBMHb" node="1bNmcZ3ae_r" resolve="pid" />
              </node>
              <node concept="3TrcHB" id="1bNmcZ3aeA1" role="2OqNvi">
                <ref role="3TsBF5" to="jb6s:1bNmcZ2XUAL" resolve="name" />
              </node>
            </node>
            <node concept="liA8E" id="1bNmcZ3aeA2" role="2OqNvi">
              <ref role="37wK5l" to="wyt6:~String.matches(java.lang.String)" resolve="matches" />
              <node concept="Xl_RD" id="1bNmcZ3aeA3" role="37wK5m">
                <property role="Xl_RC" value="(?i).*(mrn|patient).*" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ3aeA4" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ3aeA5" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ3aeA8" role="2MkJ7o">
              <property role="Xl_RC" value="CLI-C-002: a PlanIntentDefinition name may not carry patient-identifying content; Stage A governance models are non-clinical mirrors" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ3aeA9" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ3ae_r" resolve="pid" />
            </node>
          </node>
        </node>
      </node>
      <node concept="3clFbJ" id="1bNmcZ3aeAa" role="3cqZAp">
        <node concept="1Wc70l" id="1bNmcZ3aeAd" role="3clFbw">
          <node concept="1Wc70l" id="1bNmcZ3aeAg" role="3uHU7B">
            <node concept="3y3z36" id="1bNmcZ3aeAj" role="3uHU7B">
              <node concept="2OqwBi" id="1bNmcZ3aeAm" role="3uHU7B">
                <node concept="1YBJjd" id="1bNmcZ3aeAp" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ3ae_r" resolve="pid" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ3aeAq" role="2OqNvi">
                  <ref role="3TsBF5" to="jb6s:1bNmcZ2XUAL" resolve="name" />
                </node>
              </node>
              <node concept="10Nm6u" id="1bNmcZ3aeAr" role="3uHU7w" />
            </node>
            <node concept="3fqX7Q" id="1bNmcZ3aeAs" role="3uHU7w">
              <node concept="2OqwBi" id="1bNmcZ3aeAu" role="3fr31v">
                <node concept="2OqwBi" id="1bNmcZ3aeAx" role="2Oq$k0">
                  <node concept="1YBJjd" id="1bNmcZ3aeA$" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ3ae_r" resolve="pid" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ3aeA_" role="2OqNvi">
                    <ref role="3TsBF5" to="jb6s:1bNmcZ2XUAL" resolve="name" />
                  </node>
                </node>
                <node concept="liA8E" id="1bNmcZ3aeAA" role="2OqNvi">
                  <ref role="37wK5l" to="wyt6:~String.isEmpty()" resolve="isEmpty" />
                </node>
              </node>
            </node>
          </node>
          <node concept="2OqwBi" id="1bNmcZ3aeAB" role="3uHU7w">
            <node concept="2OqwBi" id="1bNmcZ3aeAE" role="2Oq$k0">
              <node concept="1YBJjd" id="1bNmcZ3aeAH" role="2Oq$k0">
                <ref role="1YBMHb" node="1bNmcZ3ae_r" resolve="pid" />
              </node>
              <node concept="3TrcHB" id="1bNmcZ3aeAI" role="2OqNvi">
                <ref role="3TsBF5" to="jb6s:1bNmcZ2XUAL" resolve="name" />
              </node>
            </node>
            <node concept="liA8E" id="1bNmcZ3aeAJ" role="2OqNvi">
              <ref role="37wK5l" to="wyt6:~String.matches(java.lang.String)" resolve="matches" />
              <node concept="Xl_RD" id="1bNmcZ3aeAK" role="37wK5m">
                <property role="Xl_RC" value=".*[0-9]{6,}.*" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ3aeAL" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ3aeAM" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ3aeAP" role="2MkJ7o">
              <property role="Xl_RC" value="CLI-C-002: a PlanIntentDefinition name may not carry a record-number-shaped digit run; Stage A governance models are non-clinical mirrors" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ3aeAQ" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ3ae_r" resolve="pid" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="18kY7G" id="1bNmcZ3aeEw">
    <property role="TrG5h" value="CLI_C_005_A4_requires_human_actor" />
    <node concept="1YaCAy" id="1bNmcZ3aeEz" role="1YuTPh">
      <property role="TrG5h" value="pol" />
      <ref role="1YaFvo" to="jb6s:1bNmcZ2XUA_" resolve="AuthorityPolicy" />
    </node>
    <node concept="3clFbS" id="1bNmcZ3aeE$" role="18ibNy">
      <node concept="2Gpval" id="1bNmcZ3aeE_" role="3cqZAp">
        <node concept="2GrKxI" id="1bNmcZ3aeED" role="2Gsz3X">
          <property role="TrG5h" value="actor" />
        </node>
        <node concept="2OqwBi" id="1bNmcZ3aeEE" role="2GsD0m">
          <node concept="1YBJjd" id="1bNmcZ3aeEH" role="2Oq$k0">
            <ref role="1YBMHb" node="1bNmcZ3aeEz" resolve="pol" />
          </node>
          <node concept="3Tsc0h" id="1bNmcZ3aeEI" role="2OqNvi">
            <ref role="3TtcxE" to="jb6s:1bNmcZ2XUAY" resolve="actors" />
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ3aeEJ" role="2LFqv$">
          <node concept="2Gpval" id="1bNmcZ3aeEK" role="3cqZAp">
            <node concept="2GrKxI" id="1bNmcZ3aeEO" role="2Gsz3X">
              <property role="TrG5h" value="cap" />
            </node>
            <node concept="2OqwBi" id="1bNmcZ3aeEP" role="2GsD0m">
              <node concept="1YBJjd" id="1bNmcZ3aeES" role="2Oq$k0">
                <ref role="1YBMHb" node="1bNmcZ3aeEz" resolve="pol" />
              </node>
              <node concept="3Tsc0h" id="1bNmcZ3aeET" role="2OqNvi">
                <ref role="3TtcxE" to="jb6s:1bNmcZ2XUAX" resolve="capabilities" />
              </node>
            </node>
            <node concept="3clFbS" id="1bNmcZ3aeEU" role="2LFqv$">
              <node concept="3clFbJ" id="1bNmcZ3aeEV" role="3cqZAp">
                <node concept="1Wc70l" id="1bNmcZ3aeEY" role="3clFbw">
                  <node concept="1Wc70l" id="1bNmcZ3aeF1" role="3uHU7B">
                    <node concept="1Wc70l" id="1bNmcZ3aeF4" role="3uHU7B">
                      <node concept="1Wc70l" id="1bNmcZ3aeF7" role="3uHU7B">
                        <node concept="3clFbC" id="1bNmcZ3aeFa" role="3uHU7B">
                          <node concept="2OqwBi" id="1bNmcZ3aeFd" role="3uHU7B">
                            <node concept="2GrUjf" id="1bNmcZ3aeFg" role="2Oq$k0">
                              <ref role="2Gs0qQ" node="1bNmcZ3aeEO" resolve="cap" />
                            </node>
                            <node concept="3TrEf2" id="1bNmcZ3aeFh" role="2OqNvi">
                              <ref role="3Tt5mk" to="jb6s:1bNmcZ2XUAC" resolve="professionalRole" />
                            </node>
                          </node>
                          <node concept="2OqwBi" id="1bNmcZ3aeFi" role="3uHU7w">
                            <node concept="2GrUjf" id="1bNmcZ3aeFl" role="2Oq$k0">
                              <ref role="2Gs0qQ" node="1bNmcZ3aeED" resolve="actor" />
                            </node>
                            <node concept="3TrEf2" id="1bNmcZ3aeFm" role="2OqNvi">
                              <ref role="3Tt5mk" to="jb6s:1bNmcZ2XUAJ" resolve="professionalRole" />
                            </node>
                          </node>
                        </node>
                        <node concept="3clFbC" id="1bNmcZ3aeFn" role="3uHU7w">
                          <node concept="2OqwBi" id="1bNmcZ3aeFq" role="3uHU7B">
                            <node concept="2GrUjf" id="1bNmcZ3aeFt" role="2Oq$k0">
                              <ref role="2Gs0qQ" node="1bNmcZ3aeEO" resolve="cap" />
                            </node>
                            <node concept="3TrEf2" id="1bNmcZ3aeFu" role="2OqNvi">
                              <ref role="3Tt5mk" to="jb6s:1bNmcZ2XUAD" resolve="operationalRole" />
                            </node>
                          </node>
                          <node concept="2OqwBi" id="1bNmcZ3aeFv" role="3uHU7w">
                            <node concept="2GrUjf" id="1bNmcZ3aeFy" role="2Oq$k0">
                              <ref role="2Gs0qQ" node="1bNmcZ3aeED" resolve="actor" />
                            </node>
                            <node concept="3TrEf2" id="1bNmcZ3aeFz" role="2OqNvi">
                              <ref role="3Tt5mk" to="jb6s:1bNmcZ2XUAK" resolve="operationalRole" />
                            </node>
                          </node>
                        </node>
                      </node>
                      <node concept="3y3z36" id="1bNmcZ3aeF$" role="3uHU7w">
                        <node concept="2OqwBi" id="1bNmcZ3aeFB" role="3uHU7B">
                          <node concept="2GrUjf" id="1bNmcZ3aeFE" role="2Oq$k0">
                            <ref role="2Gs0qQ" node="1bNmcZ3aeEO" resolve="cap" />
                          </node>
                          <node concept="3TrEf2" id="1bNmcZ3aeFF" role="2OqNvi">
                            <ref role="3Tt5mk" to="jb6s:1bNmcZ2XUAE" resolve="allowedAction" />
                          </node>
                        </node>
                        <node concept="10Nm6u" id="1bNmcZ3aeFG" role="3uHU7w" />
                      </node>
                    </node>
                    <node concept="2OqwBi" id="1bNmcZ3aeFH" role="3uHU7w">
                      <node concept="2OqwBi" id="1bNmcZ3aeFK" role="2Oq$k0">
                        <node concept="2OqwBi" id="1bNmcZ3aeFN" role="2Oq$k0">
                          <node concept="2OqwBi" id="1bNmcZ3aeFQ" role="2Oq$k0">
                            <node concept="2GrUjf" id="1bNmcZ3aeFT" role="2Oq$k0">
                              <ref role="2Gs0qQ" node="1bNmcZ3aeEO" resolve="cap" />
                            </node>
                            <node concept="3TrEf2" id="1bNmcZ3aeFU" role="2OqNvi">
                              <ref role="3Tt5mk" to="jb6s:1bNmcZ2XUAE" resolve="allowedAction" />
                            </node>
                          </node>
                          <node concept="3TrcHB" id="1bNmcZ3aeFV" role="2OqNvi">
                            <ref role="3TsBF5" to="jb6s:1bNmcZ2XU_J" resolve="autonomyLevel" />
                          </node>
                        </node>
                        <node concept="24Tkf9" id="1bNmcZ3aeFW" role="2OqNvi" />
                      </node>
                      <node concept="liA8E" id="1bNmcZ3aeFX" role="2OqNvi">
                        <ref role="37wK5l" to="wyt6:~String.equals(java.lang.Object)" resolve="equals" />
                        <node concept="Xl_RD" id="1bNmcZ3aeFY" role="37wK5m">
                          <property role="Xl_RC" value="A4_authorize_or_deliver" />
                        </node>
                      </node>
                    </node>
                  </node>
                  <node concept="3fqX7Q" id="1bNmcZ3aeFZ" role="3uHU7w">
                    <node concept="2OqwBi" id="1bNmcZ3aeG1" role="3fr31v">
                      <node concept="2OqwBi" id="1bNmcZ3aeG4" role="2Oq$k0">
                        <node concept="2OqwBi" id="1bNmcZ3aeG7" role="2Oq$k0">
                          <node concept="2GrUjf" id="1bNmcZ3aeGa" role="2Oq$k0">
                            <ref role="2Gs0qQ" node="1bNmcZ3aeED" resolve="actor" />
                          </node>
                          <node concept="3TrcHB" id="1bNmcZ3aeGb" role="2OqNvi">
                            <ref role="3TsBF5" to="jb6s:1bNmcZ2XUAI" resolve="actorKind" />
                          </node>
                        </node>
                        <node concept="24Tkf9" id="1bNmcZ3aeGc" role="2OqNvi" />
                      </node>
                      <node concept="liA8E" id="1bNmcZ3aeGd" role="2OqNvi">
                        <ref role="37wK5l" to="wyt6:~String.equals(java.lang.Object)" resolve="equals" />
                        <node concept="Xl_RD" id="1bNmcZ3aeGe" role="37wK5m">
                          <property role="Xl_RC" value="HUMAN" />
                        </node>
                      </node>
                    </node>
                  </node>
                </node>
                <node concept="3clFbS" id="1bNmcZ3aeGf" role="3clFbx">
                  <node concept="2MkqsV" id="1bNmcZ3aeGg" role="3cqZAp">
                    <node concept="3cpWs3" id="1bNmcZ3aeGj" role="2MkJ7o">
                      <node concept="Xl_RD" id="1bNmcZ3aeGm" role="3uHU7B">
                        <property role="Xl_RC" value="CLI-C-005 (realizes GOV-C-007): an action at autonomy level A4_authorize_or_deliver may be satisfied only by an AuthorizedActor whose actorKind is HUMAN; this actor is " />
                      </node>
                      <node concept="2OqwBi" id="1bNmcZ3aeGn" role="3uHU7w">
                        <node concept="2OqwBi" id="1bNmcZ3aeGq" role="2Oq$k0">
                          <node concept="2GrUjf" id="1bNmcZ3aeGt" role="2Oq$k0">
                            <ref role="2Gs0qQ" node="1bNmcZ3aeED" resolve="actor" />
                          </node>
                          <node concept="3TrcHB" id="1bNmcZ3aeGu" role="2OqNvi">
                            <ref role="3TsBF5" to="jb6s:1bNmcZ2XUAI" resolve="actorKind" />
                          </node>
                        </node>
                        <node concept="24Tkf9" id="1bNmcZ3aeGv" role="2OqNvi" />
                      </node>
                    </node>
                    <node concept="2GrUjf" id="1bNmcZ3aeGw" role="1urrMF">
                      <ref role="2Gs0qQ" node="1bNmcZ3aeED" resolve="actor" />
                    </node>
                  </node>
                </node>
              </node>
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="18kY7G" id="1bNmcZ3af8A">
    <property role="TrG5h" value="CLI_C_006_transition_facets_explicit" />
    <node concept="1YaCAy" id="1bNmcZ3ew_h" role="1YuTPh">
      <property role="TrG5h" value="st" />
      <ref role="1YaFvo" to="jb6s:1bNmcZ2XUB8" resolve="StateTransition" />
    </node>
    <node concept="3clFbS" id="1bNmcZ3ew_i" role="18ibNy">
      <node concept="3clFbJ" id="1bNmcZ3ew_j" role="3cqZAp">
        <node concept="3fqX7Q" id="1bNmcZ3ew_m" role="3clFbw">
          <node concept="1eOMI4" id="1bNmcZ3ew_o" role="3fr31v">
            <node concept="1Wc70l" id="1bNmcZ3ew_q" role="1eOMHV">
              <node concept="3y3z36" id="1bNmcZ3ew_t" role="3uHU7B">
                <node concept="2OqwBi" id="1bNmcZ3ew_w" role="3uHU7B">
                  <node concept="1YBJjd" id="1bNmcZ3ew_z" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ3ew_h" resolve="st" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ3ew_$" role="2OqNvi">
                    <ref role="3TsBF5" to="jb6s:1bNmcZ2XUBa" resolve="guard" />
                  </node>
                </node>
                <node concept="10Nm6u" id="1bNmcZ3ew__" role="3uHU7w" />
              </node>
              <node concept="3fqX7Q" id="1bNmcZ3ew_A" role="3uHU7w">
                <node concept="2OqwBi" id="1bNmcZ3ew_C" role="3fr31v">
                  <node concept="2OqwBi" id="1bNmcZ3ew_F" role="2Oq$k0">
                    <node concept="1YBJjd" id="1bNmcZ3ew_I" role="2Oq$k0">
                      <ref role="1YBMHb" node="1bNmcZ3ew_h" resolve="st" />
                    </node>
                    <node concept="3TrcHB" id="1bNmcZ3ew_J" role="2OqNvi">
                      <ref role="3TsBF5" to="jb6s:1bNmcZ2XUBa" resolve="guard" />
                    </node>
                  </node>
                  <node concept="liA8E" id="1bNmcZ3ew_K" role="2OqNvi">
                    <ref role="37wK5l" to="wyt6:~String.isEmpty()" resolve="isEmpty" />
                  </node>
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ3ew_L" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ3ew_M" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ3ew_P" role="2MkJ7o">
              <property role="Xl_RC" value="CLI-C-006: a StateTransition must declare its guard explicitly; an implied guard is not a transition condition the model may express" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ3ew_Q" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ3ew_h" resolve="st" />
            </node>
          </node>
        </node>
      </node>
      <node concept="3clFbJ" id="1bNmcZ3ew_R" role="3cqZAp">
        <node concept="3fqX7Q" id="1bNmcZ3ew_U" role="3clFbw">
          <node concept="1eOMI4" id="1bNmcZ3ew_W" role="3fr31v">
            <node concept="1Wc70l" id="1bNmcZ3ew_Y" role="1eOMHV">
              <node concept="3y3z36" id="1bNmcZ3ewA1" role="3uHU7B">
                <node concept="2OqwBi" id="1bNmcZ3ewA4" role="3uHU7B">
                  <node concept="1YBJjd" id="1bNmcZ3ewA7" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ3ew_h" resolve="st" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ3ewA8" role="2OqNvi">
                    <ref role="3TsBF5" to="jb6s:1bNmcZ2XUBb" resolve="invalidationEffect" />
                  </node>
                </node>
                <node concept="10Nm6u" id="1bNmcZ3ewA9" role="3uHU7w" />
              </node>
              <node concept="3fqX7Q" id="1bNmcZ3ewAa" role="3uHU7w">
                <node concept="2OqwBi" id="1bNmcZ3ewAc" role="3fr31v">
                  <node concept="2OqwBi" id="1bNmcZ3ewAf" role="2Oq$k0">
                    <node concept="1YBJjd" id="1bNmcZ3ewAi" role="2Oq$k0">
                      <ref role="1YBMHb" node="1bNmcZ3ew_h" resolve="st" />
                    </node>
                    <node concept="3TrcHB" id="1bNmcZ3ewAj" role="2OqNvi">
                      <ref role="3TsBF5" to="jb6s:1bNmcZ2XUBb" resolve="invalidationEffect" />
                    </node>
                  </node>
                  <node concept="liA8E" id="1bNmcZ3ewAk" role="2OqNvi">
                    <ref role="37wK5l" to="wyt6:~String.isEmpty()" resolve="isEmpty" />
                  </node>
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ3ewAl" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ3ewAm" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ3ewAp" role="2MkJ7o">
              <property role="Xl_RC" value="CLI-C-006: a StateTransition must declare its invalidation effect explicitly" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ3ewAq" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ3ew_h" resolve="st" />
            </node>
          </node>
        </node>
      </node>
      <node concept="3clFbJ" id="1bNmcZ3ewAr" role="3cqZAp">
        <node concept="3clFbC" id="1bNmcZ3ewAu" role="3clFbw">
          <node concept="2OqwBi" id="1bNmcZ3ewAx" role="3uHU7B">
            <node concept="1YBJjd" id="1bNmcZ3ewA$" role="2Oq$k0">
              <ref role="1YBMHb" node="1bNmcZ3ew_h" resolve="st" />
            </node>
            <node concept="3TrEf2" id="1bNmcZ3ewA_" role="2OqNvi">
              <ref role="3Tt5mk" to="jb6s:1bNmcZ2XUBc" resolve="source" />
            </node>
          </node>
          <node concept="10Nm6u" id="1bNmcZ3ewAA" role="3uHU7w" />
        </node>
        <node concept="3clFbS" id="1bNmcZ3ewAB" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ3ewAC" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ3ewAF" role="2MkJ7o">
              <property role="Xl_RC" value="CLI-C-006: a StateTransition must declare its source state explicitly" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ3ewAG" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ3ew_h" resolve="st" />
            </node>
          </node>
        </node>
      </node>
      <node concept="3clFbJ" id="1bNmcZ3ewAH" role="3cqZAp">
        <node concept="3clFbC" id="1bNmcZ3ewAK" role="3clFbw">
          <node concept="2OqwBi" id="1bNmcZ3ewAN" role="3uHU7B">
            <node concept="1YBJjd" id="1bNmcZ3ewAQ" role="2Oq$k0">
              <ref role="1YBMHb" node="1bNmcZ3ew_h" resolve="st" />
            </node>
            <node concept="3TrEf2" id="1bNmcZ3ewAR" role="2OqNvi">
              <ref role="3Tt5mk" to="jb6s:1bNmcZ2XUBd" resolve="target" />
            </node>
          </node>
          <node concept="10Nm6u" id="1bNmcZ3ewAS" role="3uHU7w" />
        </node>
        <node concept="3clFbS" id="1bNmcZ3ewAT" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ3ewAU" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ3ewAX" role="2MkJ7o">
              <property role="Xl_RC" value="CLI-C-006: a StateTransition must declare its target state explicitly" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ3ewAY" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ3ew_h" resolve="st" />
            </node>
          </node>
        </node>
      </node>
      <node concept="3clFbJ" id="1bNmcZ3ewAZ" role="3cqZAp">
        <node concept="3clFbC" id="1bNmcZ3ewB2" role="3clFbw">
          <node concept="2OqwBi" id="1bNmcZ3ewB5" role="3uHU7B">
            <node concept="1YBJjd" id="1bNmcZ3ewB8" role="2Oq$k0">
              <ref role="1YBMHb" node="1bNmcZ3ew_h" resolve="st" />
            </node>
            <node concept="3TrEf2" id="1bNmcZ3ewB9" role="2OqNvi">
              <ref role="3Tt5mk" to="jb6s:1bNmcZ2XUBe" resolve="actorRole" />
            </node>
          </node>
          <node concept="10Nm6u" id="1bNmcZ3ewBa" role="3uHU7w" />
        </node>
        <node concept="3clFbS" id="1bNmcZ3ewBb" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ3ewBc" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ3ewBf" role="2MkJ7o">
              <property role="Xl_RC" value="CLI-C-006: a StateTransition must declare the operational role that performs it explicitly" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ3ewBg" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ3ew_h" resolve="st" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="18kY7G" id="1bNmcZ3afbM">
    <property role="TrG5h" value="CLI_C_007_release_binds_commissioned_use" />
    <node concept="1YaCAy" id="1bNmcZ3afbP" role="1YuTPh">
      <property role="TrG5h" value="rp" />
      <ref role="1YaFvo" to="jb6s:1bNmcZ2XUAA" resolve="ReleaseProfile" />
    </node>
    <node concept="3clFbS" id="1bNmcZ3afbQ" role="18ibNy">
      <node concept="3clFbJ" id="1bNmcZ3afbR" role="3cqZAp">
        <node concept="1Wc70l" id="1bNmcZ3afbU" role="3clFbw">
          <node concept="1Wc70l" id="1bNmcZ3afbX" role="3uHU7B">
            <node concept="3y3z36" id="1bNmcZ3afc0" role="3uHU7B">
              <node concept="2OqwBi" id="1bNmcZ3afc3" role="3uHU7B">
                <node concept="1YBJjd" id="1bNmcZ3afc6" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ3afbP" resolve="rp" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ3afc7" role="2OqNvi">
                  <ref role="3TsBF5" to="jb6s:1bNmcZ2XUB0" resolve="intendedUse" />
                </node>
              </node>
              <node concept="10Nm6u" id="1bNmcZ3afc8" role="3uHU7w" />
            </node>
            <node concept="3fqX7Q" id="1bNmcZ3afc9" role="3uHU7w">
              <node concept="2OqwBi" id="1bNmcZ3afcb" role="3fr31v">
                <node concept="2OqwBi" id="1bNmcZ3afce" role="2Oq$k0">
                  <node concept="1YBJjd" id="1bNmcZ3afch" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ3afbP" resolve="rp" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ3afci" role="2OqNvi">
                    <ref role="3TsBF5" to="jb6s:1bNmcZ2XUB0" resolve="intendedUse" />
                  </node>
                </node>
                <node concept="liA8E" id="1bNmcZ3afcj" role="2OqNvi">
                  <ref role="37wK5l" to="wyt6:~String.isEmpty()" resolve="isEmpty" />
                </node>
              </node>
            </node>
          </node>
          <node concept="2OqwBi" id="1bNmcZ3afck" role="3uHU7w">
            <node concept="2OqwBi" id="1bNmcZ3afcn" role="2Oq$k0">
              <node concept="1YBJjd" id="1bNmcZ3afcq" role="2Oq$k0">
                <ref role="1YBMHb" node="1bNmcZ3afbP" resolve="rp" />
              </node>
              <node concept="3Tsc0h" id="1bNmcZ3afcr" role="2OqNvi">
                <ref role="3TtcxE" to="jb6s:1bNmcZ2XUB3" resolve="commissionedUse" />
              </node>
            </node>
            <node concept="1v1jN8" id="1bNmcZ3afcs" role="2OqNvi" />
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ3afct" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ3afcu" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ3afcx" role="2MkJ7o">
              <property role="Xl_RC" value="CLI-C-007: a ReleaseProfile that states an intended use must bind at least one CommissionedUseEnvelope; intended use outside the commissioned scope is not a release decision the model may express" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ3afcy" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ3afbP" resolve="rp" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
</model>

