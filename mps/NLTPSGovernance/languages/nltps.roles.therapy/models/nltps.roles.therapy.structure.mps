<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:efe6b658-71a4-41ab-9bb5-1bf2f66e4a84(nltps.roles.therapy.structure)">
  <persistence version="9" />
  <languages>
    <devkit ref="78434eb8-b0e5-444b-850d-e7c4ad2da9ab(jetbrains.mps.devkit.aspect.structure)" />
  </languages>
  <imports>
    <import index="vyi7" ref="r:03c59dbb-02a2-4640-9787-a2fad5bd196e(nltps.roles.common.structure)" />
    <import index="jb6s" ref="r:4741d84b-80d0-4a09-848d-cb03c7811725(nltps.clinicalintent.structure)" />
    <import index="tpck" ref="r:00000000-0000-4000-0000-011c89590288(jetbrains.mps.lang.core.structure)" implicit="true" />
  </imports>
  <registry>
    <language id="c72da2b9-7cce-4447-8389-f407dc1158b7" name="jetbrains.mps.lang.structure">
      <concept id="3348158742936976480" name="jetbrains.mps.lang.structure.structure.EnumerationMemberDeclaration" flags="ng" index="25R33">
        <property id="1421157252384165432" name="memberId" index="3tVfz5" />
        <property id="672037151186491528" name="presentation" index="1L1pqM" />
      </concept>
      <concept id="3348158742936976479" name="jetbrains.mps.lang.structure.structure.EnumerationDeclaration" flags="ng" index="25R3W">
        <child id="3348158742936976577" name="members" index="25R1y" />
      </concept>
      <concept id="1082978164218" name="jetbrains.mps.lang.structure.structure.DataTypeDeclaration" flags="ng" index="AxPO6">
        <property id="7791109065626895363" name="datatypeId" index="3F6X1D" />
      </concept>
      <concept id="1169125787135" name="jetbrains.mps.lang.structure.structure.AbstractConceptDeclaration" flags="ig" index="PkWjJ">
        <property id="6714410169261853888" name="conceptId" index="EcuMT" />
        <child id="1071489727083" name="linkDeclaration" index="1TKVEi" />
        <child id="1071489727084" name="propertyDeclaration" index="1TKVEl" />
      </concept>
      <concept id="1071489090640" name="jetbrains.mps.lang.structure.structure.ConceptDeclaration" flags="ig" index="1TIwiD">
        <property id="1096454100552" name="rootable" index="19KtqR" />
        <reference id="1071489389519" name="extends" index="1TJDcQ" />
      </concept>
      <concept id="1071489288299" name="jetbrains.mps.lang.structure.structure.PropertyDeclaration" flags="ig" index="1TJgyi">
        <property id="241647608299431129" name="propertyId" index="IQ2nx" />
        <reference id="1082985295845" name="dataType" index="AX2Wp" />
      </concept>
      <concept id="1071489288298" name="jetbrains.mps.lang.structure.structure.LinkDeclaration" flags="ig" index="1TJgyj">
        <property id="1071599776563" name="role" index="20kJfa" />
        <property id="1071599893252" name="sourceCardinality" index="20lbJX" />
        <property id="1071599937831" name="metaClass" index="20lmBu" />
        <property id="241647608299431140" name="linkId" index="IQ2ns" />
        <reference id="1071599976176" name="target" index="20lvS9" />
      </concept>
    </language>
    <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
      <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ngI" index="TrEIO">
        <property id="1169194664001" name="name" index="TrG5h" />
      </concept>
    </language>
  </registry>
  <node concept="25R3W" id="1bNmcZ3oT8R">
    <property role="3F6X1D" value="1365532761382949431" />
    <property role="TrG5h" value="TherapyTaskKindEnum" />
    <node concept="25R33" id="1bNmcZ3oT8T" role="25R1y">
      <property role="3tVfz5" value="91299862882101780" />
      <property role="TrG5h" value="treatment_setup_review" />
      <property role="1L1pqM" value="treatment_setup_review" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8U" role="25R1y">
      <property role="3tVfz5" value="7113978123113204969" />
      <property role="TrG5h" value="treatment_parameter_verification" />
      <property role="1L1pqM" value="treatment_parameter_verification" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8V" role="25R1y">
      <property role="3tVfz5" value="6580780051430500725" />
      <property role="TrG5h" value="transfer_verification" />
      <property role="1L1pqM" value="transfer_verification" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8W" role="25R1y">
      <property role="3tVfz5" value="5888639794504707569" />
      <property role="TrG5h" value="delivery_readiness_recording" />
      <property role="1L1pqM" value="delivery_readiness_recording" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8X" role="25R1y">
      <property role="3tVfz5" value="1892920179410043949" />
      <property role="TrG5h" value="setup_conflict_escalation" />
      <property role="1L1pqM" value="setup_conflict_escalation" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3oT9x">
    <property role="EcuMT" value="1365532761382949473" />
    <property role="TrG5h" value="TherapyView" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ3oT9$" role="1TKVEl">
      <property role="IQ2nx" value="1365532761382949476" />
      <property role="TrG5h" value="viewName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3oT9_" role="1TKVEi">
      <property role="IQ2ns" value="1365532761382949477" />
      <property role="20kJfa" value="subjects" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" to="vyi7:1bNmcZ2XUBl" resolve="SemanticTargetRef" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3oT9y">
    <property role="EcuMT" value="1365532761382949474" />
    <property role="TrG5h" value="TherapyTask" />
    <ref role="1TJDcQ" to="vyi7:1bNmcZ2XUBw" resolve="RoleCommand" />
    <node concept="1TJgyi" id="1bNmcZ3oT9A" role="1TKVEl">
      <property role="IQ2nx" value="1365532761382949478" />
      <property role="TrG5h" value="taskKind" />
      <ref role="AX2Wp" node="1bNmcZ3oT8R" resolve="TherapyTaskKindEnum" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3oT9z">
    <property role="EcuMT" value="1365532761382949475" />
    <property role="TrG5h" value="TherapyProjection" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="vyi7:1bNmcZ2XUBk" resolve="RoleProjection" />
    <node concept="1TJgyj" id="1bNmcZ3oT9B" role="1TKVEi">
      <property role="IQ2ns" value="1365532761382949479" />
      <property role="20kJfa" value="views" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3oT9x" resolve="TherapyView" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3oT9C" role="1TKVEi">
      <property role="IQ2ns" value="1365532761382949480" />
      <property role="20kJfa" value="tasks" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3oT9y" resolve="TherapyTask" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3oT9D" role="1TKVEi">
      <property role="IQ2ns" value="1365532761382949481" />
      <property role="20kJfa" value="intendedRole" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" to="jb6s:1bNmcZ2XUAi" resolve="ProfessionalRole" />
    </node>
  </node>
</model>

