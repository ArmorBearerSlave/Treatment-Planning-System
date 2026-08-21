<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:8dd9f206-c3d2-4005-9eac-68f587875029(nltps.roles.dosimetry.structure)">
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
  <node concept="25R3W" id="1bNmcZ3oT8H">
    <property role="3F6X1D" value="1365532761382949421" />
    <property role="TrG5h" value="DosimetryTaskKindEnum" />
    <node concept="25R33" id="1bNmcZ3oT8J" role="25R1y">
      <property role="3tVfz5" value="8910323401053931979" />
      <property role="TrG5h" value="planning_strategy_authoring" />
      <property role="1L1pqM" value="planning_strategy_authoring" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8K" role="25R1y">
      <property role="3tVfz5" value="3655319352912883426" />
      <property role="TrG5h" value="optimization_objective_setting" />
      <property role="1L1pqM" value="optimization_objective_setting" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8L" role="25R1y">
      <property role="3tVfz5" value="3577933709063267848" />
      <property role="TrG5h" value="candidate_generation" />
      <property role="1L1pqM" value="candidate_generation" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8M" role="25R1y">
      <property role="3tVfz5" value="2789160113220141019" />
      <property role="TrG5h" value="candidate_refinement" />
      <property role="1L1pqM" value="candidate_refinement" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8N" role="25R1y">
      <property role="3tVfz5" value="1527454587906381556" />
      <property role="TrG5h" value="tradeoff_documentation" />
      <property role="1L1pqM" value="tradeoff_documentation" />
    </node>
    <node concept="25R33" id="1bNmcZ3oT8O" role="25R1y">
      <property role="3tVfz5" value="5296115660642080677" />
      <property role="TrG5h" value="physics_review_request" />
      <property role="1L1pqM" value="physics_review_request" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3oT9m">
    <property role="EcuMT" value="1365532761382949462" />
    <property role="TrG5h" value="DosimetryView" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ3oT9p" role="1TKVEl">
      <property role="IQ2nx" value="1365532761382949465" />
      <property role="TrG5h" value="viewName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3oT9q" role="1TKVEi">
      <property role="IQ2ns" value="1365532761382949466" />
      <property role="20kJfa" value="subjects" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" to="vyi7:1bNmcZ2XUBl" resolve="SemanticTargetRef" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3oT9n">
    <property role="EcuMT" value="1365532761382949463" />
    <property role="TrG5h" value="DosimetryTask" />
    <ref role="1TJDcQ" to="vyi7:1bNmcZ2XUBw" resolve="RoleCommand" />
    <node concept="1TJgyi" id="1bNmcZ3oT9r" role="1TKVEl">
      <property role="IQ2nx" value="1365532761382949467" />
      <property role="TrG5h" value="taskKind" />
      <ref role="AX2Wp" node="1bNmcZ3oT8H" resolve="DosimetryTaskKindEnum" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3oT9o">
    <property role="EcuMT" value="1365532761382949464" />
    <property role="TrG5h" value="DosimetryProjection" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="vyi7:1bNmcZ2XUBk" resolve="RoleProjection" />
    <node concept="1TJgyj" id="1bNmcZ3oT9s" role="1TKVEi">
      <property role="IQ2ns" value="1365532761382949468" />
      <property role="20kJfa" value="views" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3oT9m" resolve="DosimetryView" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3oT9t" role="1TKVEi">
      <property role="IQ2ns" value="1365532761382949469" />
      <property role="20kJfa" value="tasks" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3oT9n" resolve="DosimetryTask" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3oT9u" role="1TKVEi">
      <property role="IQ2ns" value="1365532761382949470" />
      <property role="20kJfa" value="intendedRole" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" to="jb6s:1bNmcZ2XUAi" resolve="ProfessionalRole" />
    </node>
  </node>
</model>

