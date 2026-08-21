<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:856c8b9b-af0a-43e7-a94c-e5b667f02d38(nltps.foundation.typesystem)">
  <persistence version="9" />
  <languages>
    <use id="7a5dda62-9140-4668-ab76-d5ed1746f2b2" name="jetbrains.mps.lang.typesystem" version="5" />
    <use id="f3061a53-9226-4cc5-a443-f952ceaf5816" name="jetbrains.mps.baseLanguage" version="12" />
    <use id="7866978e-a0f0-4cc7-81bc-4d213d9375e1" name="jetbrains.mps.lang.smodel" version="19" />
    <use id="af65afd8-f0dd-4942-87d9-63a55f2a9db1" name="jetbrains.mps.lang.behavior" version="2" />
    <use id="83888646-71ce-4f1c-9c53-c54016f6ad4f" name="jetbrains.mps.baseLanguage.collections" version="2" />
    <use id="fd392034-7849-419d-9071-12563d152375" name="jetbrains.mps.baseLanguage.closures" version="0" />
    <devkit ref="00000000-0000-4000-0000-1de82b3a4936(jetbrains.mps.devkit.aspect.typesystem)" />
  </languages>
  <imports>
    <import index="5q6" ref="r:07b10a47-b937-4aa9-ad53-c2e3280bb0f3(nltps.foundation.structure)" />
    <import index="wyt6" ref="6354ebe7-c22a-4a0f-ac54-50b52ab9b065/java:java.lang(JDK/)" />
    <import index="vdre" ref="r:1cfb31f6-8af2-41dd-91f1-d89c69640fdd(nltps.foundation.behavior)" />
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
      <concept id="1081236700937" name="jetbrains.mps.baseLanguage.structure.StaticMethodCall" flags="nn" index="2YIFZM">
        <reference id="1144433194310" name="classConcept" index="1Pybhc" />
      </concept>
      <concept id="1070534058343" name="jetbrains.mps.baseLanguage.structure.NullLiteral" flags="nn" index="10Nm6u" />
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
      <concept id="1068580320020" name="jetbrains.mps.baseLanguage.structure.IntegerConstant" flags="nn" index="3cmrfG">
        <property id="1068580320021" name="value" index="3cmrfH" />
      </concept>
      <concept id="1081506762703" name="jetbrains.mps.baseLanguage.structure.GreaterThanExpression" flags="nn" index="3eOSWO" />
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
      <concept id="1966870290083281362" name="jetbrains.mps.lang.smodel.structure.EnumMember_NameOperation" flags="ng" index="24Tkf9" />
      <concept id="1177026924588" name="jetbrains.mps.lang.smodel.structure.RefConcept_Reference" flags="nn" index="chp4Y">
        <reference id="1177026940964" name="conceptDeclaration" index="cht4Q" />
      </concept>
      <concept id="1143234257716" name="jetbrains.mps.lang.smodel.structure.Node_GetModelOperation" flags="nn" index="I4A8Y" />
      <concept id="1171323947159" name="jetbrains.mps.lang.smodel.structure.Model_NodesOperation" flags="nn" index="2SmgA7">
        <child id="1758937410080001570" name="conceptArgument" index="1dBWTz" />
      </concept>
      <concept id="1138055754698" name="jetbrains.mps.lang.smodel.structure.SNodeType" flags="in" index="3Tqbb2">
        <reference id="1138405853777" name="concept" index="ehGHo" />
      </concept>
      <concept id="1138056022639" name="jetbrains.mps.lang.smodel.structure.SPropertyAccess" flags="nn" index="3TrcHB">
        <reference id="1138056395725" name="property" index="3TsBF5" />
      </concept>
      <concept id="1138056143562" name="jetbrains.mps.lang.smodel.structure.SLinkAccess" flags="nn" index="3TrEf2">
        <reference id="1138056516764" name="link" index="3Tt5mk" />
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
      <concept id="1162935959151" name="jetbrains.mps.baseLanguage.collections.structure.GetSizeOperation" flags="nn" index="34oBXx" />
      <concept id="1202120902084" name="jetbrains.mps.baseLanguage.collections.structure.WhereOperation" flags="nn" index="3zZkjj" />
    </language>
  </registry>
  <node concept="18kY7G" id="1bNmcZ2CHuG">
    <property role="TrG5h" value="FND_REPR_version_dates" />
    <node concept="1YaCAy" id="1bNmcZ2Vqml" role="1YuTPh">
      <property role="TrG5h" value="ver" />
      <ref role="1YaFvo" to="5q6:1bNmcZ2iEsy" resolve="Version" />
    </node>
    <node concept="3clFbS" id="1bNmcZ2Vqmm" role="18ibNy">
      <node concept="3clFbJ" id="1bNmcZ2Vqmn" role="3cqZAp">
        <node concept="1Wc70l" id="1bNmcZ2Vqmq" role="3clFbw">
          <node concept="1Wc70l" id="1bNmcZ2Vqmt" role="3uHU7B">
            <node concept="3y3z36" id="1bNmcZ2Vqmw" role="3uHU7B">
              <node concept="2OqwBi" id="1bNmcZ2Vqmz" role="3uHU7B">
                <node concept="1YBJjd" id="1bNmcZ2VqmA" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2VqmB" role="2OqNvi">
                  <ref role="3TsBF5" to="5q6:1bNmcZ2iEsS" resolve="effectiveDate" />
                </node>
              </node>
              <node concept="10Nm6u" id="1bNmcZ2VqmC" role="3uHU7w" />
            </node>
            <node concept="3fqX7Q" id="1bNmcZ2VqmD" role="3uHU7w">
              <node concept="2OqwBi" id="1bNmcZ2VqmF" role="3fr31v">
                <node concept="2OqwBi" id="1bNmcZ2VqmI" role="2Oq$k0">
                  <node concept="1YBJjd" id="1bNmcZ2VqmL" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ2VqmM" role="2OqNvi">
                    <ref role="3TsBF5" to="5q6:1bNmcZ2iEsS" resolve="effectiveDate" />
                  </node>
                </node>
                <node concept="liA8E" id="1bNmcZ2VqmN" role="2OqNvi">
                  <ref role="37wK5l" to="wyt6:~String.isEmpty()" resolve="isEmpty" />
                </node>
              </node>
            </node>
          </node>
          <node concept="3fqX7Q" id="1bNmcZ2VqmO" role="3uHU7w">
            <node concept="2OqwBi" id="1bNmcZ2VqmQ" role="3fr31v">
              <node concept="2OqwBi" id="1bNmcZ2VqmT" role="2Oq$k0">
                <node concept="1YBJjd" id="1bNmcZ2VqmW" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2VqmX" role="2OqNvi">
                  <ref role="3TsBF5" to="5q6:1bNmcZ2iEsS" resolve="effectiveDate" />
                </node>
              </node>
              <node concept="liA8E" id="1bNmcZ2VqmY" role="2OqNvi">
                <ref role="37wK5l" to="wyt6:~String.matches(java.lang.String)" resolve="matches" />
                <node concept="Xl_RD" id="1bNmcZ2VqmZ" role="37wK5m">
                  <property role="Xl_RC" value="^[0-9]{4}-[0-9]{2}-[0-9]{2}$" />
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ2Vqn0" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ2Vqn1" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ2Vqn4" role="2MkJ7o">
              <property role="Xl_RC" value="property_facet_policy date lexical: effectiveDate must use the YYYY-MM-DD form" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ2Vqn5" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
            </node>
          </node>
        </node>
      </node>
      <node concept="3clFbJ" id="1bNmcZ2Vqn6" role="3cqZAp">
        <node concept="1Wc70l" id="1bNmcZ2Vqn9" role="3clFbw">
          <node concept="1Wc70l" id="1bNmcZ2Vqnc" role="3uHU7B">
            <node concept="1Wc70l" id="1bNmcZ2Vqnf" role="3uHU7B">
              <node concept="3y3z36" id="1bNmcZ2Vqni" role="3uHU7B">
                <node concept="2OqwBi" id="1bNmcZ2Vqnl" role="3uHU7B">
                  <node concept="1YBJjd" id="1bNmcZ2Vqno" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ2Vqnp" role="2OqNvi">
                    <ref role="3TsBF5" to="5q6:1bNmcZ2iEsS" resolve="effectiveDate" />
                  </node>
                </node>
                <node concept="10Nm6u" id="1bNmcZ2Vqnq" role="3uHU7w" />
              </node>
              <node concept="3fqX7Q" id="1bNmcZ2Vqnr" role="3uHU7w">
                <node concept="2OqwBi" id="1bNmcZ2Vqnt" role="3fr31v">
                  <node concept="2OqwBi" id="1bNmcZ2Vqnw" role="2Oq$k0">
                    <node concept="1YBJjd" id="1bNmcZ2Vqnz" role="2Oq$k0">
                      <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                    </node>
                    <node concept="3TrcHB" id="1bNmcZ2Vqn$" role="2OqNvi">
                      <ref role="3TsBF5" to="5q6:1bNmcZ2iEsS" resolve="effectiveDate" />
                    </node>
                  </node>
                  <node concept="liA8E" id="1bNmcZ2Vqn_" role="2OqNvi">
                    <ref role="37wK5l" to="wyt6:~String.isEmpty()" resolve="isEmpty" />
                  </node>
                </node>
              </node>
            </node>
            <node concept="2OqwBi" id="1bNmcZ2VqnA" role="3uHU7w">
              <node concept="2OqwBi" id="1bNmcZ2VqnD" role="2Oq$k0">
                <node concept="1YBJjd" id="1bNmcZ2VqnG" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2VqnH" role="2OqNvi">
                  <ref role="3TsBF5" to="5q6:1bNmcZ2iEsS" resolve="effectiveDate" />
                </node>
              </node>
              <node concept="liA8E" id="1bNmcZ2VqnI" role="2OqNvi">
                <ref role="37wK5l" to="wyt6:~String.matches(java.lang.String)" resolve="matches" />
                <node concept="Xl_RD" id="1bNmcZ2VqnJ" role="37wK5m">
                  <property role="Xl_RC" value="^[0-9]{4}-[0-9]{2}-[0-9]{2}$" />
                </node>
              </node>
            </node>
          </node>
          <node concept="3fqX7Q" id="1bNmcZ2VqnK" role="3uHU7w">
            <node concept="2YIFZM" id="1bNmcZ2VqnM" role="3fr31v">
              <ref role="1Pybhc" to="vdre:1bNmcZ2VoXx" resolve="CalendarDates" />
              <ref role="37wK5l" to="vdre:1bNmcZ2VoX$" resolve="isValidCalendarDate" />
              <node concept="2OqwBi" id="1bNmcZ2VqnN" role="37wK5m">
                <node concept="1YBJjd" id="1bNmcZ2VqnQ" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2VqnR" role="2OqNvi">
                  <ref role="3TsBF5" to="5q6:1bNmcZ2iEsS" resolve="effectiveDate" />
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ2VqnS" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ2VqnT" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ2VqnW" role="2MkJ7o">
              <property role="Xl_RC" value="property_facet_policy date calendar: effectiveDate is not a valid calendar date" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ2VqnX" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
            </node>
          </node>
        </node>
      </node>
      <node concept="3clFbJ" id="1bNmcZ2VqnY" role="3cqZAp">
        <node concept="1Wc70l" id="1bNmcZ2Vqo1" role="3clFbw">
          <node concept="1Wc70l" id="1bNmcZ2Vqo4" role="3uHU7B">
            <node concept="3y3z36" id="1bNmcZ2Vqo7" role="3uHU7B">
              <node concept="2OqwBi" id="1bNmcZ2Vqoa" role="3uHU7B">
                <node concept="1YBJjd" id="1bNmcZ2Vqod" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2Vqoe" role="2OqNvi">
                  <ref role="3TsBF5" to="5q6:1bNmcZ2iEsT" resolve="supersededDate" />
                </node>
              </node>
              <node concept="10Nm6u" id="1bNmcZ2Vqof" role="3uHU7w" />
            </node>
            <node concept="3fqX7Q" id="1bNmcZ2Vqog" role="3uHU7w">
              <node concept="2OqwBi" id="1bNmcZ2Vqoi" role="3fr31v">
                <node concept="2OqwBi" id="1bNmcZ2Vqol" role="2Oq$k0">
                  <node concept="1YBJjd" id="1bNmcZ2Vqoo" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ2Vqop" role="2OqNvi">
                    <ref role="3TsBF5" to="5q6:1bNmcZ2iEsT" resolve="supersededDate" />
                  </node>
                </node>
                <node concept="liA8E" id="1bNmcZ2Vqoq" role="2OqNvi">
                  <ref role="37wK5l" to="wyt6:~String.isEmpty()" resolve="isEmpty" />
                </node>
              </node>
            </node>
          </node>
          <node concept="3fqX7Q" id="1bNmcZ2Vqor" role="3uHU7w">
            <node concept="2OqwBi" id="1bNmcZ2Vqot" role="3fr31v">
              <node concept="2OqwBi" id="1bNmcZ2Vqow" role="2Oq$k0">
                <node concept="1YBJjd" id="1bNmcZ2Vqoz" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2Vqo$" role="2OqNvi">
                  <ref role="3TsBF5" to="5q6:1bNmcZ2iEsT" resolve="supersededDate" />
                </node>
              </node>
              <node concept="liA8E" id="1bNmcZ2Vqo_" role="2OqNvi">
                <ref role="37wK5l" to="wyt6:~String.matches(java.lang.String)" resolve="matches" />
                <node concept="Xl_RD" id="1bNmcZ2VqoA" role="37wK5m">
                  <property role="Xl_RC" value="^[0-9]{4}-[0-9]{2}-[0-9]{2}$" />
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ2VqoB" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ2VqoC" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ2VqoF" role="2MkJ7o">
              <property role="Xl_RC" value="property_facet_policy date lexical: supersededDate must use the YYYY-MM-DD form" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ2VqoG" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
            </node>
          </node>
        </node>
      </node>
      <node concept="3clFbJ" id="1bNmcZ2VqoH" role="3cqZAp">
        <node concept="1Wc70l" id="1bNmcZ2VqoK" role="3clFbw">
          <node concept="1Wc70l" id="1bNmcZ2VqoN" role="3uHU7B">
            <node concept="1Wc70l" id="1bNmcZ2VqoQ" role="3uHU7B">
              <node concept="3y3z36" id="1bNmcZ2VqoT" role="3uHU7B">
                <node concept="2OqwBi" id="1bNmcZ2VqoW" role="3uHU7B">
                  <node concept="1YBJjd" id="1bNmcZ2VqoZ" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ2Vqp0" role="2OqNvi">
                    <ref role="3TsBF5" to="5q6:1bNmcZ2iEsT" resolve="supersededDate" />
                  </node>
                </node>
                <node concept="10Nm6u" id="1bNmcZ2Vqp1" role="3uHU7w" />
              </node>
              <node concept="3fqX7Q" id="1bNmcZ2Vqp2" role="3uHU7w">
                <node concept="2OqwBi" id="1bNmcZ2Vqp4" role="3fr31v">
                  <node concept="2OqwBi" id="1bNmcZ2Vqp7" role="2Oq$k0">
                    <node concept="1YBJjd" id="1bNmcZ2Vqpa" role="2Oq$k0">
                      <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                    </node>
                    <node concept="3TrcHB" id="1bNmcZ2Vqpb" role="2OqNvi">
                      <ref role="3TsBF5" to="5q6:1bNmcZ2iEsT" resolve="supersededDate" />
                    </node>
                  </node>
                  <node concept="liA8E" id="1bNmcZ2Vqpc" role="2OqNvi">
                    <ref role="37wK5l" to="wyt6:~String.isEmpty()" resolve="isEmpty" />
                  </node>
                </node>
              </node>
            </node>
            <node concept="2OqwBi" id="1bNmcZ2Vqpd" role="3uHU7w">
              <node concept="2OqwBi" id="1bNmcZ2Vqpg" role="2Oq$k0">
                <node concept="1YBJjd" id="1bNmcZ2Vqpj" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2Vqpk" role="2OqNvi">
                  <ref role="3TsBF5" to="5q6:1bNmcZ2iEsT" resolve="supersededDate" />
                </node>
              </node>
              <node concept="liA8E" id="1bNmcZ2Vqpl" role="2OqNvi">
                <ref role="37wK5l" to="wyt6:~String.matches(java.lang.String)" resolve="matches" />
                <node concept="Xl_RD" id="1bNmcZ2Vqpm" role="37wK5m">
                  <property role="Xl_RC" value="^[0-9]{4}-[0-9]{2}-[0-9]{2}$" />
                </node>
              </node>
            </node>
          </node>
          <node concept="3fqX7Q" id="1bNmcZ2Vqpn" role="3uHU7w">
            <node concept="2YIFZM" id="1bNmcZ2Vqpp" role="3fr31v">
              <ref role="1Pybhc" to="vdre:1bNmcZ2VoXx" resolve="CalendarDates" />
              <ref role="37wK5l" to="vdre:1bNmcZ2VoX$" resolve="isValidCalendarDate" />
              <node concept="2OqwBi" id="1bNmcZ2Vqpq" role="37wK5m">
                <node concept="1YBJjd" id="1bNmcZ2Vqpt" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2Vqpu" role="2OqNvi">
                  <ref role="3TsBF5" to="5q6:1bNmcZ2iEsT" resolve="supersededDate" />
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ2Vqpv" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ2Vqpw" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ2Vqpz" role="2MkJ7o">
              <property role="Xl_RC" value="property_facet_policy date calendar: supersededDate is not a valid calendar date" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ2Vqp$" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ2Vqml" resolve="ver" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="18kY7G" id="1bNmcZ2CHHz">
    <property role="TrG5h" value="FND_REPR_magnitude_numeric" />
    <node concept="1YaCAy" id="1bNmcZ2QTOe" role="1YuTPh">
      <property role="TrG5h" value="pq" />
      <ref role="1YaFvo" to="5q6:1bNmcZ2iEs_" resolve="PhysicalQuantity" />
    </node>
    <node concept="3clFbS" id="1bNmcZ2QTOf" role="18ibNy">
      <node concept="3clFbJ" id="1bNmcZ2QTOg" role="3cqZAp">
        <node concept="3fqX7Q" id="1bNmcZ2QTOj" role="3clFbw">
          <node concept="2OqwBi" id="1bNmcZ2QTOl" role="3fr31v">
            <node concept="2OqwBi" id="1bNmcZ2QTOo" role="2Oq$k0">
              <node concept="1YBJjd" id="1bNmcZ2QTOr" role="2Oq$k0">
                <ref role="1YBMHb" node="1bNmcZ2QTOe" resolve="pq" />
              </node>
              <node concept="3TrcHB" id="1bNmcZ2QTOs" role="2OqNvi">
                <ref role="3TsBF5" to="5q6:1bNmcZ2iEt0" resolve="magnitude" />
              </node>
            </node>
            <node concept="liA8E" id="1bNmcZ2QTOt" role="2OqNvi">
              <ref role="37wK5l" to="wyt6:~String.matches(java.lang.String)" resolve="matches" />
              <node concept="Xl_RD" id="1bNmcZ2QTOu" role="37wK5m">
                <property role="Xl_RC" value="^-?[0-9]+([.][0-9]+)?$" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ2QTOv" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ2QTOw" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ2QTOz" role="2MkJ7o">
              <property role="Xl_RC" value="property_facet_policy real: magnitude is logically numeric and must be a deterministic numeric literal" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ2QTO$" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ2QTOe" resolve="pq" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="18kY7G" id="1bNmcZ2CHIM">
    <property role="TrG5h" value="FND_C_003_unit_dimension" />
    <node concept="1YaCAy" id="1bNmcZ2DbZ9" role="1YuTPh">
      <property role="TrG5h" value="pq" />
      <ref role="1YaFvo" to="5q6:1bNmcZ2iEs_" resolve="PhysicalQuantity" />
    </node>
    <node concept="3clFbS" id="1bNmcZ2DbZa" role="18ibNy">
      <node concept="3clFbJ" id="1bNmcZ2DbZb" role="3cqZAp">
        <node concept="1Wc70l" id="1bNmcZ2DbZe" role="3clFbw">
          <node concept="3fqX7Q" id="1bNmcZ2DbZh" role="3uHU7B">
            <node concept="2OqwBi" id="1bNmcZ2DbZj" role="3fr31v">
              <node concept="2OqwBi" id="1bNmcZ2DbZm" role="2Oq$k0">
                <node concept="2OqwBi" id="1bNmcZ2DbZp" role="2Oq$k0">
                  <node concept="1YBJjd" id="1bNmcZ2DbZs" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ2DbZ9" resolve="pq" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ2DbZt" role="2OqNvi">
                    <ref role="3TsBF5" to="5q6:1bNmcZ2iEt1" resolve="doseBasis" />
                  </node>
                </node>
                <node concept="24Tkf9" id="1bNmcZ2DbZu" role="2OqNvi" />
              </node>
              <node concept="liA8E" id="1bNmcZ2DbZv" role="2OqNvi">
                <ref role="37wK5l" to="wyt6:~String.equals(java.lang.Object)" resolve="equals" />
                <node concept="Xl_RD" id="1bNmcZ2DbZw" role="37wK5m">
                  <property role="Xl_RC" value="not_applicable" />
                </node>
              </node>
            </node>
          </node>
          <node concept="3fqX7Q" id="1bNmcZ2DbZx" role="3uHU7w">
            <node concept="2OqwBi" id="1bNmcZ2DbZz" role="3fr31v">
              <node concept="2OqwBi" id="1bNmcZ2DbZA" role="2Oq$k0">
                <node concept="2OqwBi" id="1bNmcZ2DbZD" role="2Oq$k0">
                  <node concept="2OqwBi" id="1bNmcZ2DbZG" role="2Oq$k0">
                    <node concept="1YBJjd" id="1bNmcZ2DbZJ" role="2Oq$k0">
                      <ref role="1YBMHb" node="1bNmcZ2DbZ9" resolve="pq" />
                    </node>
                    <node concept="3TrEf2" id="1bNmcZ2DbZK" role="2OqNvi">
                      <ref role="3Tt5mk" to="5q6:1bNmcZ2iEt2" resolve="unit" />
                    </node>
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ2DbZL" role="2OqNvi">
                    <ref role="3TsBF5" to="5q6:1bNmcZ2iEt4" resolve="dimension" />
                  </node>
                </node>
                <node concept="24Tkf9" id="1bNmcZ2DbZM" role="2OqNvi" />
              </node>
              <node concept="liA8E" id="1bNmcZ2DbZN" role="2OqNvi">
                <ref role="37wK5l" to="wyt6:~String.equals(java.lang.Object)" resolve="equals" />
                <node concept="Xl_RD" id="1bNmcZ2DbZO" role="37wK5m">
                  <property role="Xl_RC" value="dose" />
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ2DbZP" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ2DbZQ" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ2DbZT" role="2MkJ7o">
              <property role="Xl_RC" value="FND-C-003: a dose-bearing PhysicalQuantity must reference a unit of dimension dose" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ2DbZU" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ2DbZ9" resolve="pq" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="18kY7G" id="1bNmcZ2CHJQ">
    <property role="TrG5h" value="FND_C_004_dose_basis" />
    <node concept="1YaCAy" id="1bNmcZ2Dc1G" role="1YuTPh">
      <property role="TrG5h" value="pq" />
      <ref role="1YaFvo" to="5q6:1bNmcZ2iEs_" resolve="PhysicalQuantity" />
    </node>
    <node concept="3clFbS" id="1bNmcZ2Dc1H" role="18ibNy">
      <node concept="3clFbJ" id="1bNmcZ2Dc1I" role="3cqZAp">
        <node concept="1Wc70l" id="1bNmcZ2Dc1L" role="3clFbw">
          <node concept="1Wc70l" id="1bNmcZ2Dc1O" role="3uHU7B">
            <node concept="3fqX7Q" id="1bNmcZ2Dc1R" role="3uHU7B">
              <node concept="2OqwBi" id="1bNmcZ2Dc1T" role="3fr31v">
                <node concept="2OqwBi" id="1bNmcZ2Dc1W" role="2Oq$k0">
                  <node concept="2OqwBi" id="1bNmcZ2Dc1Z" role="2Oq$k0">
                    <node concept="1YBJjd" id="1bNmcZ2Dc22" role="2Oq$k0">
                      <ref role="1YBMHb" node="1bNmcZ2Dc1G" resolve="pq" />
                    </node>
                    <node concept="3TrcHB" id="1bNmcZ2Dc23" role="2OqNvi">
                      <ref role="3TsBF5" to="5q6:1bNmcZ2iEt1" resolve="doseBasis" />
                    </node>
                  </node>
                  <node concept="24Tkf9" id="1bNmcZ2Dc24" role="2OqNvi" />
                </node>
                <node concept="liA8E" id="1bNmcZ2Dc25" role="2OqNvi">
                  <ref role="37wK5l" to="wyt6:~String.equals(java.lang.Object)" resolve="equals" />
                  <node concept="Xl_RD" id="1bNmcZ2Dc26" role="37wK5m">
                    <property role="Xl_RC" value="not_applicable" />
                  </node>
                </node>
              </node>
            </node>
            <node concept="3fqX7Q" id="1bNmcZ2Dc27" role="3uHU7w">
              <node concept="2OqwBi" id="1bNmcZ2Dc29" role="3fr31v">
                <node concept="2OqwBi" id="1bNmcZ2Dc2c" role="2Oq$k0">
                  <node concept="2OqwBi" id="1bNmcZ2Dc2f" role="2Oq$k0">
                    <node concept="2OqwBi" id="1bNmcZ2Dc2i" role="2Oq$k0">
                      <node concept="1YBJjd" id="1bNmcZ2Dc2l" role="2Oq$k0">
                        <ref role="1YBMHb" node="1bNmcZ2Dc1G" resolve="pq" />
                      </node>
                      <node concept="3TrEf2" id="1bNmcZ2Dc2m" role="2OqNvi">
                        <ref role="3Tt5mk" to="5q6:1bNmcZ2iEt2" resolve="unit" />
                      </node>
                    </node>
                    <node concept="3TrcHB" id="1bNmcZ2Dc2n" role="2OqNvi">
                      <ref role="3TsBF5" to="5q6:1bNmcZ2iEt5" resolve="doseBasis" />
                    </node>
                  </node>
                  <node concept="24Tkf9" id="1bNmcZ2Dc2o" role="2OqNvi" />
                </node>
                <node concept="liA8E" id="1bNmcZ2Dc2p" role="2OqNvi">
                  <ref role="37wK5l" to="wyt6:~String.equals(java.lang.Object)" resolve="equals" />
                  <node concept="Xl_RD" id="1bNmcZ2Dc2q" role="37wK5m">
                    <property role="Xl_RC" value="not_applicable" />
                  </node>
                </node>
              </node>
            </node>
          </node>
          <node concept="3fqX7Q" id="1bNmcZ2Dc2r" role="3uHU7w">
            <node concept="2OqwBi" id="1bNmcZ2Dc2t" role="3fr31v">
              <node concept="2OqwBi" id="1bNmcZ2Dc2w" role="2Oq$k0">
                <node concept="2OqwBi" id="1bNmcZ2Dc2z" role="2Oq$k0">
                  <node concept="1YBJjd" id="1bNmcZ2Dc2A" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ2Dc1G" resolve="pq" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ2Dc2B" role="2OqNvi">
                    <ref role="3TsBF5" to="5q6:1bNmcZ2iEt1" resolve="doseBasis" />
                  </node>
                </node>
                <node concept="24Tkf9" id="1bNmcZ2Dc2C" role="2OqNvi" />
              </node>
              <node concept="liA8E" id="1bNmcZ2Dc2D" role="2OqNvi">
                <ref role="37wK5l" to="wyt6:~String.equals(java.lang.Object)" resolve="equals" />
                <node concept="2OqwBi" id="1bNmcZ2Dc2E" role="37wK5m">
                  <node concept="2OqwBi" id="1bNmcZ2Dc2H" role="2Oq$k0">
                    <node concept="2OqwBi" id="1bNmcZ2Dc2K" role="2Oq$k0">
                      <node concept="1YBJjd" id="1bNmcZ2Dc2N" role="2Oq$k0">
                        <ref role="1YBMHb" node="1bNmcZ2Dc1G" resolve="pq" />
                      </node>
                      <node concept="3TrEf2" id="1bNmcZ2Dc2O" role="2OqNvi">
                        <ref role="3Tt5mk" to="5q6:1bNmcZ2iEt2" resolve="unit" />
                      </node>
                    </node>
                    <node concept="3TrcHB" id="1bNmcZ2Dc2P" role="2OqNvi">
                      <ref role="3TsBF5" to="5q6:1bNmcZ2iEt5" resolve="doseBasis" />
                    </node>
                  </node>
                  <node concept="24Tkf9" id="1bNmcZ2Dc2Q" role="2OqNvi" />
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ2Dc2R" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ2Dc2S" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ2Dc2V" role="2MkJ7o">
              <property role="Xl_RC" value="FND-C-004: physical_absorbed and rbe_weighted dose are not interchangeable; quantity and unit dose bases differ" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ2Dc2W" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ2Dc1G" resolve="pq" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="18kY7G" id="1bNmcZ2Kg33">
    <property role="TrG5h" value="FND_C_001_stableid_unique" />
    <node concept="1YaCAy" id="1bNmcZ2Kg36" role="1YuTPh">
      <property role="TrG5h" value="sid" />
      <ref role="1YaFvo" to="5q6:1bNmcZ2iEsw" resolve="StableId" />
    </node>
    <node concept="3clFbS" id="1bNmcZ2Kg37" role="18ibNy">
      <node concept="3clFbJ" id="1bNmcZ2Kg38" role="3cqZAp">
        <node concept="3eOSWO" id="1bNmcZ2Kg3b" role="3clFbw">
          <node concept="2OqwBi" id="1bNmcZ2Kg3e" role="3uHU7B">
            <node concept="2OqwBi" id="1bNmcZ2Kg3h" role="2Oq$k0">
              <node concept="2OqwBi" id="1bNmcZ2Kg3k" role="2Oq$k0">
                <node concept="2OqwBi" id="1bNmcZ2Kg3n" role="2Oq$k0">
                  <node concept="1YBJjd" id="1bNmcZ2Kg3q" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ2Kg36" resolve="sid" />
                  </node>
                  <node concept="I4A8Y" id="1bNmcZ2Kg3r" role="2OqNvi" />
                </node>
                <node concept="2SmgA7" id="1bNmcZ2Kg3s" role="2OqNvi">
                  <node concept="chp4Y" id="1bNmcZ2Kg3t" role="1dBWTz">
                    <ref role="cht4Q" to="5q6:1bNmcZ2iEsw" resolve="StableId" />
                  </node>
                </node>
              </node>
              <node concept="3zZkjj" id="1bNmcZ2Kg3u" role="2OqNvi">
                <node concept="1bVj0M" id="1bNmcZ2Kg3z" role="23t8la">
                  <node concept="37vLTG" id="1bNmcZ2Kg3_" role="1bW2Oz">
                    <property role="TrG5h" value="it" />
                    <node concept="3Tqbb2" id="1bNmcZ2Kg3B" role="1tU5fm">
                      <ref role="ehGHo" to="5q6:1bNmcZ2iEsw" resolve="StableId" />
                    </node>
                  </node>
                  <node concept="3clFbS" id="1bNmcZ2Kg3C" role="1bW5cS">
                    <node concept="3clFbF" id="1bNmcZ2Kg3D" role="3cqZAp">
                      <node concept="2OqwBi" id="1bNmcZ2Kg3F" role="3clFbG">
                        <node concept="2OqwBi" id="1bNmcZ2Kg3I" role="2Oq$k0">
                          <node concept="37vLTw" id="1bNmcZ2Kg3L" role="2Oq$k0">
                            <ref role="3cqZAo" node="1bNmcZ2Kg3_" resolve="it" />
                          </node>
                          <node concept="3TrcHB" id="1bNmcZ2Kg3M" role="2OqNvi">
                            <ref role="3TsBF5" to="5q6:1bNmcZ2iEsM" resolve="value" />
                          </node>
                        </node>
                        <node concept="liA8E" id="1bNmcZ2Kg3N" role="2OqNvi">
                          <ref role="37wK5l" to="wyt6:~String.equals(java.lang.Object)" resolve="equals" />
                          <node concept="2OqwBi" id="1bNmcZ2Kg3O" role="37wK5m">
                            <node concept="1YBJjd" id="1bNmcZ2Kg3R" role="2Oq$k0">
                              <ref role="1YBMHb" node="1bNmcZ2Kg36" resolve="sid" />
                            </node>
                            <node concept="3TrcHB" id="1bNmcZ2Kg3S" role="2OqNvi">
                              <ref role="3TsBF5" to="5q6:1bNmcZ2iEsM" resolve="value" />
                            </node>
                          </node>
                        </node>
                      </node>
                    </node>
                  </node>
                </node>
              </node>
            </node>
            <node concept="34oBXx" id="1bNmcZ2Kg3T" role="2OqNvi" />
          </node>
          <node concept="3cmrfG" id="1bNmcZ2Kg3U" role="3uHU7w">
            <property role="3cmrfH" value="1" />
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ2Kg3V" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ2Kg3W" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ2Kg3Z" role="2MkJ7o">
              <property role="Xl_RC" value="FND-C-001: stable identifiers must be unique within a baseline" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ2Kg40" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ2Kg36" resolve="sid" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
  <node concept="18kY7G" id="1bNmcZ2VqTA">
    <property role="TrG5h" value="FND_REPR_externalreference_date" />
    <node concept="1YaCAy" id="1bNmcZ2VqTD" role="1YuTPh">
      <property role="TrG5h" value="ext" />
      <ref role="1YaFvo" to="5q6:1bNmcZ2iEsC" resolve="ExternalReference" />
    </node>
    <node concept="3clFbS" id="1bNmcZ2VqTE" role="18ibNy">
      <node concept="3clFbJ" id="1bNmcZ2VqTF" role="3cqZAp">
        <node concept="1Wc70l" id="1bNmcZ2VqTI" role="3clFbw">
          <node concept="1Wc70l" id="1bNmcZ2VqTL" role="3uHU7B">
            <node concept="3y3z36" id="1bNmcZ2VqTO" role="3uHU7B">
              <node concept="2OqwBi" id="1bNmcZ2VqTR" role="3uHU7B">
                <node concept="1YBJjd" id="1bNmcZ2VqTU" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ2VqTD" resolve="ext" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2VqTV" role="2OqNvi">
                  <ref role="3TsBF5" to="5q6:1bNmcZ2iEtc" resolve="retrievedDate" />
                </node>
              </node>
              <node concept="10Nm6u" id="1bNmcZ2VqTW" role="3uHU7w" />
            </node>
            <node concept="3fqX7Q" id="1bNmcZ2VqTX" role="3uHU7w">
              <node concept="2OqwBi" id="1bNmcZ2VqTZ" role="3fr31v">
                <node concept="2OqwBi" id="1bNmcZ2VqU2" role="2Oq$k0">
                  <node concept="1YBJjd" id="1bNmcZ2VqU5" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ2VqTD" resolve="ext" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ2VqU6" role="2OqNvi">
                    <ref role="3TsBF5" to="5q6:1bNmcZ2iEtc" resolve="retrievedDate" />
                  </node>
                </node>
                <node concept="liA8E" id="1bNmcZ2VqU7" role="2OqNvi">
                  <ref role="37wK5l" to="wyt6:~String.isEmpty()" resolve="isEmpty" />
                </node>
              </node>
            </node>
          </node>
          <node concept="3fqX7Q" id="1bNmcZ2VqU8" role="3uHU7w">
            <node concept="2OqwBi" id="1bNmcZ2VqUa" role="3fr31v">
              <node concept="2OqwBi" id="1bNmcZ2VqUd" role="2Oq$k0">
                <node concept="1YBJjd" id="1bNmcZ2VqUg" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ2VqTD" resolve="ext" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2VqUh" role="2OqNvi">
                  <ref role="3TsBF5" to="5q6:1bNmcZ2iEtc" resolve="retrievedDate" />
                </node>
              </node>
              <node concept="liA8E" id="1bNmcZ2VqUi" role="2OqNvi">
                <ref role="37wK5l" to="wyt6:~String.matches(java.lang.String)" resolve="matches" />
                <node concept="Xl_RD" id="1bNmcZ2VqUj" role="37wK5m">
                  <property role="Xl_RC" value="^[0-9]{4}-[0-9]{2}-[0-9]{2}$" />
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ2VqUk" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ2VqUl" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ2VqUo" role="2MkJ7o">
              <property role="Xl_RC" value="property_facet_policy date lexical: retrievedDate must use the YYYY-MM-DD form" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ2VqUp" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ2VqTD" resolve="ext" />
            </node>
          </node>
        </node>
      </node>
      <node concept="3clFbJ" id="1bNmcZ2VqUq" role="3cqZAp">
        <node concept="1Wc70l" id="1bNmcZ2VqUt" role="3clFbw">
          <node concept="1Wc70l" id="1bNmcZ2VqUw" role="3uHU7B">
            <node concept="1Wc70l" id="1bNmcZ2VqUz" role="3uHU7B">
              <node concept="3y3z36" id="1bNmcZ2VqUA" role="3uHU7B">
                <node concept="2OqwBi" id="1bNmcZ2VqUD" role="3uHU7B">
                  <node concept="1YBJjd" id="1bNmcZ2VqUG" role="2Oq$k0">
                    <ref role="1YBMHb" node="1bNmcZ2VqTD" resolve="ext" />
                  </node>
                  <node concept="3TrcHB" id="1bNmcZ2VqUH" role="2OqNvi">
                    <ref role="3TsBF5" to="5q6:1bNmcZ2iEtc" resolve="retrievedDate" />
                  </node>
                </node>
                <node concept="10Nm6u" id="1bNmcZ2VqUI" role="3uHU7w" />
              </node>
              <node concept="3fqX7Q" id="1bNmcZ2VqUJ" role="3uHU7w">
                <node concept="2OqwBi" id="1bNmcZ2VqUL" role="3fr31v">
                  <node concept="2OqwBi" id="1bNmcZ2VqUO" role="2Oq$k0">
                    <node concept="1YBJjd" id="1bNmcZ2VqUR" role="2Oq$k0">
                      <ref role="1YBMHb" node="1bNmcZ2VqTD" resolve="ext" />
                    </node>
                    <node concept="3TrcHB" id="1bNmcZ2VqUS" role="2OqNvi">
                      <ref role="3TsBF5" to="5q6:1bNmcZ2iEtc" resolve="retrievedDate" />
                    </node>
                  </node>
                  <node concept="liA8E" id="1bNmcZ2VqUT" role="2OqNvi">
                    <ref role="37wK5l" to="wyt6:~String.isEmpty()" resolve="isEmpty" />
                  </node>
                </node>
              </node>
            </node>
            <node concept="2OqwBi" id="1bNmcZ2VqUU" role="3uHU7w">
              <node concept="2OqwBi" id="1bNmcZ2VqUX" role="2Oq$k0">
                <node concept="1YBJjd" id="1bNmcZ2VqV0" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ2VqTD" resolve="ext" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2VqV1" role="2OqNvi">
                  <ref role="3TsBF5" to="5q6:1bNmcZ2iEtc" resolve="retrievedDate" />
                </node>
              </node>
              <node concept="liA8E" id="1bNmcZ2VqV2" role="2OqNvi">
                <ref role="37wK5l" to="wyt6:~String.matches(java.lang.String)" resolve="matches" />
                <node concept="Xl_RD" id="1bNmcZ2VqV3" role="37wK5m">
                  <property role="Xl_RC" value="^[0-9]{4}-[0-9]{2}-[0-9]{2}$" />
                </node>
              </node>
            </node>
          </node>
          <node concept="3fqX7Q" id="1bNmcZ2VqV4" role="3uHU7w">
            <node concept="2YIFZM" id="1bNmcZ2VqV6" role="3fr31v">
              <ref role="1Pybhc" to="vdre:1bNmcZ2VoXx" resolve="CalendarDates" />
              <ref role="37wK5l" to="vdre:1bNmcZ2VoX$" resolve="isValidCalendarDate" />
              <node concept="2OqwBi" id="1bNmcZ2VqV7" role="37wK5m">
                <node concept="1YBJjd" id="1bNmcZ2VqVa" role="2Oq$k0">
                  <ref role="1YBMHb" node="1bNmcZ2VqTD" resolve="ext" />
                </node>
                <node concept="3TrcHB" id="1bNmcZ2VqVb" role="2OqNvi">
                  <ref role="3TsBF5" to="5q6:1bNmcZ2iEtc" resolve="retrievedDate" />
                </node>
              </node>
            </node>
          </node>
        </node>
        <node concept="3clFbS" id="1bNmcZ2VqVc" role="3clFbx">
          <node concept="2MkqsV" id="1bNmcZ2VqVd" role="3cqZAp">
            <node concept="Xl_RD" id="1bNmcZ2VqVg" role="2MkJ7o">
              <property role="Xl_RC" value="property_facet_policy date calendar: retrievedDate is not a valid calendar date" />
            </node>
            <node concept="1YBJjd" id="1bNmcZ2VqVh" role="1urrMF">
              <ref role="1YBMHb" node="1bNmcZ2VqTD" resolve="ext" />
            </node>
          </node>
        </node>
      </node>
    </node>
  </node>
</model>

