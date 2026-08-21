<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:03c59dbb-02a2-4640-9787-a2fad5bd196e(nltps.roles.common.structure)">
  <persistence version="9" />
  <languages>
    <devkit ref="78434eb8-b0e5-444b-850d-e7c4ad2da9ab(jetbrains.mps.devkit.aspect.structure)" />
  </languages>
  <imports>
    <import index="5q6" ref="r:07b10a47-b937-4aa9-ad53-c2e3280bb0f3(nltps.foundation.structure)" />
    <import index="jb6s" ref="r:4741d84b-80d0-4a09-848d-cb03c7811725(nltps.clinicalintent.structure)" />
    <import index="tpck" ref="r:00000000-0000-4000-0000-011c89590288(jetbrains.mps.lang.core.structure)" implicit="true" />
  </imports>
  <registry>
    <language id="c72da2b9-7cce-4447-8389-f407dc1158b7" name="jetbrains.mps.lang.structure">
      <concept id="1169125787135" name="jetbrains.mps.lang.structure.structure.AbstractConceptDeclaration" flags="ig" index="PkWjJ">
        <property id="6714410169261853888" name="conceptId" index="EcuMT" />
        <property id="4628067390765956802" name="abstract" index="R5$K7" />
        <child id="1071489727083" name="linkDeclaration" index="1TKVEi" />
        <child id="1071489727084" name="propertyDeclaration" index="1TKVEl" />
      </concept>
      <concept id="1071489090640" name="jetbrains.mps.lang.structure.structure.ConceptDeclaration" flags="ig" index="1TIwiD">
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
  <node concept="1TIwiD" id="1bNmcZ2XUBk">
    <property role="EcuMT" value="1365532761375877588" />
    <property role="TrG5h" value="RoleProjection" />
    <property role="R5$K7" value="true" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2XUBp" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877593" />
      <property role="TrG5h" value="projectionName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUBl">
    <property role="EcuMT" value="1365532761375877589" />
    <property role="TrG5h" value="SemanticTargetRef" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyj" id="1bNmcZ2XUBq" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877594" />
      <property role="20kJfa" value="target" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUBm">
    <property role="EcuMT" value="1365532761375877590" />
    <property role="TrG5h" value="ActionRef" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyj" id="1bNmcZ2XUBr" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877595" />
      <property role="20kJfa" value="action" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" to="jb6s:1bNmcZ2XU_G" resolve="ActionDefinition" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUBn">
    <property role="EcuMT" value="1365532761375877591" />
    <property role="TrG5h" value="WorkflowStateRef" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyj" id="1bNmcZ2XUBs" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877596" />
      <property role="20kJfa" value="state" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" to="jb6s:1bNmcZ2XU_Y" resolve="WorkflowState" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUBo">
    <property role="EcuMT" value="1365532761375877592" />
    <property role="TrG5h" value="OperationalRoleRef" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyj" id="1bNmcZ2XUBt" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877597" />
      <property role="20kJfa" value="role" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" to="jb6s:1bNmcZ2XUAj" resolve="OperationalRole" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUBw">
    <property role="EcuMT" value="1365532761375877600" />
    <property role="TrG5h" value="RoleCommand" />
    <property role="R5$K7" value="true" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2XUBx" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877601" />
      <property role="TrG5h" value="commandName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUBy" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877602" />
      <property role="20kJfa" value="targets" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XUBl" resolve="SemanticTargetRef" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUBz" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877603" />
      <property role="20kJfa" value="actions" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XUBm" resolve="ActionRef" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUB$" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877604" />
      <property role="20kJfa" value="states" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XUBn" resolve="WorkflowStateRef" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUB_" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877605" />
      <property role="20kJfa" value="roles" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XUBo" resolve="OperationalRoleRef" />
    </node>
  </node>
</model>

