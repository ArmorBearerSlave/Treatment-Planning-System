<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:863b484b-e576-4ac1-8523-3f82d6179201(nltps.roles.physics.structure)">
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
  <node concept="25R3W" id="1bNmcZ3oT8y">
    <property role="3F6X1D" value="1365532761382949410" />
    <property role="TrG5h" value="PhysicsTaskKindEnum" />
    <node concept="25R33" id="1bNmcZ3oT8$" role="25R1y">
      <property role="3tVfz5" value="7369436249373262236" />
      <property role="TrG5h" value="technical_plan_review" />
      <property role="1L1pqM" value="technical_plan_review" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8_" role="25R1y">
      <property role="3tVfz5" value="1830216097719825879" />
      <property role="TrG5h" value="machine_configuration_review" />
      <property role="1L1pqM" value="machine_configuration_review" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8A" role="25R1y">
      <property role="3tVfz5" value="9082035445237515036" />
      <property role="TrG5h" value="robustness_review" />
      <property role="1L1pqM" value="robustness_review" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8B" role="25R1y">
      <property role="3tVfz5" value="6822867354689283202" />
      <property role="TrG5h" value="dose_algorithm_review" />
      <property role="1L1pqM" value="dose_algorithm_review" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8C" role="25R1y">
      <property role="3tVfz5" value="4134350218723957317" />
      <property role="TrG5h" value="technical_release_review" />
      <property role="1L1pqM" value="technical_release_review" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8D" role="25R1y">
      <property role="3tVfz5" value="4849839426704181694" />
      <property role="TrG5h" value="independent_verification_request" />
      <property role="1L1pqM" value="independent_verification_request" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8E" role="25R1y">
      <property role="3tVfz5" value="5643286939044768812" />
      <property role="TrG5h" value="qa_safety_escalation" />
      <property role="1L1pqM" value="qa_safety_escalation" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3oT9b">
    <property role="EcuMT" value="1365532761382949451" />
    <property role="TrG5h" value="PhysicsView" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ3oT9e" role="1TKVEl">
      <property role="IQ2nx" value="1365532761382949454" />
      <property role="TrG5h" value="viewName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3oT9f" role="1TKVEi">
      <property role="IQ2ns" value="1365532761382949455" />
      <property role="20kJfa" value="subjects" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" to="vyi7:1bNmcZ2XUBl" resolve="SemanticTargetRef" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3oT9c">
    <property role="EcuMT" value="1365532761382949452" />
    <property role="TrG5h" value="PhysicsTask" />
    <ref role="1TJDcQ" to="vyi7:1bNmcZ2XUBw" resolve="RoleCommand" />
    <node concept="1TJgyi" id="1bNmcZ3oT9g" role="1TKVEl">
      <property role="IQ2nx" value="1365532761382949456" />
      <property role="TrG5h" value="taskKind" />
      <ref role="AX2Wp" node="1bNmcZ3oT8y" resolve="PhysicsTaskKindEnum" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3oT9d">
    <property role="EcuMT" value="1365532761382949453" />
    <property role="TrG5h" value="PhysicsProjection" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="vyi7:1bNmcZ2XUBk" resolve="RoleProjection" />
    <node concept="1TJgyj" id="1bNmcZ3oT9h" role="1TKVEi">
      <property role="IQ2ns" value="1365532761382949457" />
      <property role="20kJfa" value="views" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3oT9b" resolve="PhysicsView" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3oT9i" role="1TKVEi">
      <property role="IQ2ns" value="1365532761382949458" />
      <property role="20kJfa" value="tasks" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3oT9c" resolve="PhysicsTask" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3oT9j" role="1TKVEi">
      <property role="IQ2ns" value="1365532761382949459" />
      <property role="20kJfa" value="intendedRole" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" to="jb6s:1bNmcZ2XUAi" resolve="ProfessionalRole" />
    </node>
  </node>
</model>

