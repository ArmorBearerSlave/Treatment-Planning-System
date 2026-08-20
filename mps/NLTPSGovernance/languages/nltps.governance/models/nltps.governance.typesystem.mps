<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:430deb07-cfa5-41b1-81b1-8b959ab409e8(nltps.governance.typesystem)">
  <persistence version="9" />
  <languages>
    <use id="7a5dda62-9140-4668-ab76-d5ed1746f2b2" name="jetbrains.mps.lang.typesystem" version="5" />
    <use id="f3061a53-9226-4cc5-a443-f952ceaf5816" name="jetbrains.mps.baseLanguage" version="12" />
    <use id="7866978e-a0f0-4cc7-81bc-4d213d9375e1" name="jetbrains.mps.lang.smodel" version="19" />
    <use id="83888646-71ce-4f1c-9c53-c54016f6ad4f" name="jetbrains.mps.baseLanguage.collections" version="2" />
    <use id="fd392034-7849-419d-9071-12563d152375" name="jetbrains.mps.baseLanguage.closures" version="0" />
    <devkit ref="00000000-0000-4000-0000-1de82b3a4936(jetbrains.mps.devkit.aspect.typesystem)" />
  </languages>
  <imports>
    <import index="ol33" ref="r:e3f43cc2-9854-4561-9b2a-13d5891c34c9(nltps.governance.structure)" />
    <import index="tpck" ref="r:00000000-0000-4000-0000-011c89590288(jetbrains.mps.lang.core.structure)" />
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
      <concept id="1068498886296" name="jetbrains.mps.baseLanguage.structure.VariableReference" flags="nn" index="37vLTw">
        <reference id="1068581517664" name="variableDeclaration" index="3cqZAo" />
      </concept>
      <concept id="1068498886292" name="jetbrains.mps.baseLanguage.structure.ParameterDeclaration" flags="ir" index="37vLTG" />
      <concept id="4972933694980447171" name="jetbrains.mps.baseLanguage.structure.BaseVariableDeclaration" flags="ng" index="19Szcq">
        <child id="5680397130376446158" name="type" index="1tU5fm" />
      </concept>
      <concept id="1068580123155" name="jetbrains.mps.baseLanguage.structure.ExpressionStatement" flags="nn" index="3clFbF">
        <child id="1068580123156" name="expression" index="3clFbG" />
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
    </language>
    <language id="fd392034-7849-419d-9071-12563d152375" name="jetbrains.mps.baseLanguage.closures">
      <concept id="1199569711397" name="jetbrains.mps.baseLanguage.closures.structure.ClosureLiteral" flags="nn" index="1bVj0M">
        <child id="1199569906740" name="parameter" index="1bW2Oz" />
        <child id="1199569916463" name="body" index="1bW5cS" />
      </concept>
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
      <concept id="7453996997717780434" name="jetbrains.mps.lang.smodel.structure.Node_GetSConceptOperation" flags="nn" index="2yIwOk" />
      <concept id="8866923313515890008" name="jetbrains.mps.lang.smodel.structure.AsNodeOperation" flags="nn" index="FGMqu" />
      <concept id="1138055754698" name="jetbrains.mps.lang.smodel.structure.SNodeType" flags="in" index="3Tqbb2">
        <reference id="1138405853777" name="concept" index="ehGHo" />
      </concept>
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
      <concept id="1204796164442" name="jetbrains.mps.baseLanguage.collections.structure.InternalSequenceOperation" flags="nn" index="23sCx2">
        <child id="1204796294226" name="closure" index="23t8la" />
      </concept>
      <concept id="540871147943773365" name="jetbrains.mps.baseLanguage.collections.structure.SingleArgumentSequenceOperation" flags="nn" index="25WWJ4">
        <child id="540871147943773366" name="argument" index="25WWJ7" />
      </concept>
      <concept id="1202128969694" name="jetbrains.mps.baseLanguage.collections.structure.SelectOperation" flags="nn" index="3$u5V9" />
      <concept id="1172254888721" name="jetbrains.mps.baseLanguage.collections.structure.ContainsOperation" flags="nn" index="3JPx81" />
    </language>
  </registry>
  <node concept="18kY7G" id="1bNmcZ2uzrV">
    <property role="TrG5h" value="GOV_C_002_tracelink_relation_validity" />
    <node concept="1YaCAy" id="1bNmcZ2u$kn" role="1YuTPh">
      <property role="TrG5h" value="link" />
      <ref role="1YaFvo" to="ol33:1bNmcZ2iQmR" resolve="TraceLink" />
    </node>
    <node concept="3clFbS" id="1bNmcZ2u$ko" role="18ibNy">
      <node concept="3clFbJ" id="1bNmcZ2u$kp" role="3cqZAp">
        <node concept="3fqX7Q" id="1bNmcZ2u$ks" role="3clFbw">
          <node concept="2OqwBi" id="1bNmcZ2u$ku" role="3fr31v">
            <node concept="2OqwBi" id="1bNmcZ2u$kx" role="2Oq$k0">
              <node concept="2OqwBi" id="1bNmcZ2u$k$" role="2Oq$k0">
                <node concept="2OqwBi" id="1bNmcZ2u$kB" role="2Oq$k0">
                  <node concept="1YBJjd" id="1bNmcZ2u$kE" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ2u$kn" resolve="link" />
                  </node>
                  <node concept="3TrEf2" id="1bNmcZ2u$kF" role="2OqNvi">
                    <ref role="3Tt5mk" to="ol33:1bNmcZ2iQnK" />
                  </node>
                </node>
                <node concept="3Tsc0h" id="1bNmcZ2u$kG" role="2OqNvi">
                  <ref role="3TtcxE" to="ol33:1bNmcZ2iQnH" />
                </node>
              </node>
              <node concept="3$u5V9" id="1bNmcZ2u$kH" role="2OqNvi">
                <node concept="1bVj0M" id="1bNmcZ2u$kM" role="23t8la">
                  <node concept="37vLTG" id="1bNmcZ2u$kO" role="1bW2Oz">
                    <property role="TrG5h" value="it" />
                    <node concept="3Tqbb2" id="1bNmcZ2u$kQ" role="1tU5fm">
                      <ref role="ehGHo" to="ol33:1bNmcZ2iQmy" resolve="AllowedConceptEntry" />
                    </node>
                  </node>
                  <node concept="3clFbS" id="1bNmcZ2u$kR" role="1bW5cS">
                    <node concept="3clFbF" id="1bNmcZ2u$kS" role="3cqZAp">
                      <node concept="2OqwBi" id="1bNmcZ2u$kU" role="3clFbG">
                        <node concept="37vLTw" id="1bNmcZ2u$kX" role="2Oq$k0">
                          <ref role="3cqZAo" node="1bNmcZ2u$kO" resolve="it" />
                        </node>
                        <node concept="3TrcHB" id="1bNmcZ2u$kY" role="2OqNvi">
                          <ref role="3TsBF5" to="ol33:1bNmcZ2iQmC" resolve="conceptName" />
                        </node>
                      </node>
                    </node>
                  </node>
                </node>
              </node>
            </node>
            <node concept="3JPx81" id="1bNmcZ2u$kZ" role="2OqNvi">
              <node concept="2OqwBi" id="1bNmcZ2u$l1" role="25WWJ7">
                <node concept="2OqwBi" id="1bNmcZ2u$l4" role="2Oq$k0">
                  <node concept="2OqwBi" id="1bNmcZ2u$l7" role="2Oq$k0">
                    <node concept="2OqwBi" id="1bNmcZ2u$la" role="2Oq$k0">
                      <node concept="1YBJjd" id="1bNmcZ2u$ld" role="2Oq$k0">
                        <ref role="1YBMHb" node="1bNmcZ2u$kn" resolve="link" />
                      </node>
                      <node concept="3TrEf2" id="1bNmcZ2u$le" role="2OqNvi">
                        <ref role="3Tt5mk" to="ol33:1bNmcZ2iQnL" />
                      </node>
                    </node>
                    <node concept="2yIwOk" id="1bNmcZ2u$lf" role="2OqNvi" />
                  </node>
                  <node concept="FGMqu" id="1bNmcZ2u$lg" role="2OqNvi" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2u$lh" role="2OqNvi">
                  <ref role="3TsBF5" to="tpck:h0TrG11" resolve="name" />
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ2u$li" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ2u$lj" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ2u$lm" role="2MkJ7o">
              <property role="Xl_RC" value="GOV-C-002: TraceLink source concept is not permitted by the referenced TraceRelation" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ2u$ln" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ2u$kn" resolve="link" />
            </node>
          </node>
        </node>
      </node>
      <node concept="3clFbJ" id="1bNmcZ2u$lo" role="3cqZAp">
        <node concept="3fqX7Q" id="1bNmcZ2u$lr" role="3clFbw">
          <node concept="2OqwBi" id="1bNmcZ2u$lt" role="3fr31v">
            <node concept="2OqwBi" id="1bNmcZ2u$lw" role="2Oq$k0">
              <node concept="2OqwBi" id="1bNmcZ2u$lz" role="2Oq$k0">
                <node concept="2OqwBi" id="1bNmcZ2u$lA" role="2Oq$k0">
                  <node concept="1YBJjd" id="1bNmcZ2u$lD" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ2u$kn" resolve="link" />
                  </node>
                  <node concept="3TrEf2" id="1bNmcZ2u$lE" role="2OqNvi">
                    <ref role="3Tt5mk" to="ol33:1bNmcZ2iQnK" />
                  </node>
                </node>
                <node concept="3Tsc0h" id="1bNmcZ2u$lF" role="2OqNvi">
                  <ref role="3TtcxE" to="ol33:1bNmcZ2iQnI" />
                </node>
              </node>
              <node concept="3$u5V9" id="1bNmcZ2u$lG" role="2OqNvi">
                <node concept="1bVj0M" id="1bNmcZ2u$lL" role="23t8la">
                  <node concept="37vLTG" id="1bNmcZ2u$lN" role="1bW2Oz">
                    <property role="TrG5h" value="it" />
                    <node concept="3Tqbb2" id="1bNmcZ2u$lP" role="1tU5fm">
                      <ref role="ehGHo" to="ol33:1bNmcZ2iQmy" resolve="AllowedConceptEntry" />
                    </node>
                  </node>
                  <node concept="3clFbS" id="1bNmcZ2u$lQ" role="1bW5cS">
                    <node concept="3clFbF" id="1bNmcZ2u$lR" role="3cqZAp">
                      <node concept="2OqwBi" id="1bNmcZ2u$lT" role="3clFbG">
                        <node concept="37vLTw" id="1bNmcZ2u$lW" role="2Oq$k0">
                          <ref role="3cqZAo" node="1bNmcZ2u$lN" resolve="it" />
                        </node>
                        <node concept="3TrcHB" id="1bNmcZ2u$lX" role="2OqNvi">
                          <ref role="3TsBF5" to="ol33:1bNmcZ2iQmC" resolve="conceptName" />
                        </node>
                      </node>
                    </node>
                  </node>
                </node>
              </node>
            </node>
            <node concept="3JPx81" id="1bNmcZ2u$lY" role="2OqNvi">
              <node concept="2OqwBi" id="1bNmcZ2u$m0" role="25WWJ7">
                <node concept="2OqwBi" id="1bNmcZ2u$m3" role="2Oq$k0">
                  <node concept="2OqwBi" id="1bNmcZ2u$m6" role="2Oq$k0">
                    <node concept="2OqwBi" id="1bNmcZ2u$m9" role="2Oq$k0">
                      <node concept="1YBJjd" id="1bNmcZ2u$mc" role="2Oq$k0">
                        <ref role="1YBMHb" node="1bNmcZ2u$kn" resolve="link" />
                      </node>
                      <node concept="3TrEf2" id="1bNmcZ2u$md" role="2OqNvi">
                        <ref role="3Tt5mk" to="ol33:1bNmcZ2iQnM" />
                      </node>
                    </node>
                    <node concept="2yIwOk" id="1bNmcZ2u$me" role="2OqNvi" />
                  </node>
                  <node concept="FGMqu" id="1bNmcZ2u$mf" role="2OqNvi" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2u$mg" role="2OqNvi">
                  <ref role="3TsBF5" to="tpck:h0TrG11" resolve="name" />
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ2u$mh" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ2u$mi" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ2u$ml" role="2MkJ7o">
              <property role="Xl_RC" value="GOV-C-002/GOV-C-004: TraceLink target concept is not permitted by the referenced TraceRelation" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ2u$mm" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ2u$kn" resolve="link" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="18kY7G" id="1bNmcZ2wLte">
    <property role="TrG5h" value="GOV_C_001_requirement_shall" />
    <node concept="1YaCAy" id="1bNmcZ2wLth" role="1YuTPh">
      <property role="TrG5h" value="req" />
      <ref role="1YaFvo" to="ol33:1bNmcZ2iQmG" resolve="Requirement" />
    </node>
    <node concept="3clFbS" id="1bNmcZ2wLti" role="18ibNy">
      <node concept="3clFbJ" id="1bNmcZ2wLtj" role="3cqZAp">
        <node concept="3fqX7Q" id="1bNmcZ2wLtm" role="3clFbw">
          <node concept="2OqwBi" id="1bNmcZ2wLto" role="3fr31v">
            <node concept="2OqwBi" id="1bNmcZ2wLtr" role="2Oq$k0">
              <node concept="1YBJjd" id="1bNmcZ2wLtu" role="2Oq$k0">
                <ref role="1YBMHb" node="1bNmcZ2wLth" resolve="req" />
              </node>
              <node concept="3TrcHB" id="1bNmcZ2wLtv" role="2OqNvi">
                <ref role="3TsBF5" to="ol33:1bNmcZ2iQn2" resolve="statement" />
              </node>
            </node>
            <node concept="liA8E" id="1bNmcZ2wLtw" role="2OqNvi">
              <ref role="37wK5l" to="wyt6:~String.contains(java.lang.CharSequence)" resolve="contains" />
              <node concept="Xl_RD" id="1bNmcZ2wLtx" role="37wK5m">
                <property role="Xl_RC" value="shall" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ2wLty" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ2wLtz" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ2wLtA" role="2MkJ7o">
              <property role="Xl_RC" value="GOV-C-001: a normative requirement statement must contain the word shall" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ2wLtB" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ2wLth" resolve="req" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
</model>

