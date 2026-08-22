<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:6aeac6c0-4966-4224-b0f1-a0cd5adc504c(nltps.realization.structure)">
  <persistence version="9" />
  <languages>
    <devkit ref="78434eb8-b0e5-444b-850d-e7c4ad2da9ab(jetbrains.mps.devkit.aspect.structure)" />
  </languages>
  <imports>
    <import index="5q6" ref="r:07b10a47-b937-4aa9-ad53-c2e3280bb0f3(nltps.foundation.structure)" />
    <import index="ol33" ref="r:e3f43cc2-9854-4561-9b2a-13d5891c34c9(nltps.governance.structure)" />
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
  <node concept="25R3W" id="1bNmcZ3F2NR">
    <property role="3F6X1D" value="1365532761387707639" />
    <property role="TrG5h" value="VerificationVerdictEnum" />
    <node concept="25R33" id="1bNmcZ3F2NT" role="25R1y">
      <property role="3tVfz5" value="2160327986371252856" />
      <property role="TrG5h" value="not_assessed" />
      <property role="1L1pqM" value="not_assessed" />
    </node>
    <node concept="25R33" id="1bNmcZ3F2NU" role="25R1y">
      <property role="3tVfz5" value="1973045009774864009" />
      <property role="TrG5h" value="passed" />
      <property role="1L1pqM" value="passed" />
    </node>
    <node concept="25R33" id="1bNmcZ3F2NV" role="25R1y">
      <property role="3tVfz5" value="5328828441919888048" />
      <property role="TrG5h" value="failed" />
      <property role="1L1pqM" value="failed" />
    </node>
    <node concept="25R33" id="1bNmcZ3F2NW" role="25R1y">
      <property role="3tVfz5" value="6101733620987369413" />
      <property role="TrG5h" value="blocked" />
      <property role="1L1pqM" value="blocked" />
    </node>
  </node>
  <node concept="25R3W" id="1bNmcZ3F2O8">
    <property role="3F6X1D" value="1365532761387707656" />
    <property role="TrG5h" value="EvidenceKindEnum" />
    <node concept="25R33" id="1bNmcZ3F2Oa" role="25R1y">
      <property role="3tVfz5" value="7477145779645558883" />
      <property role="TrG5h" value="executable_result" />
      <property role="1L1pqM" value="executable_result" />
    </node>
    <node concept="25R33" id="1bNmcZ3F2Ob" role="25R1y">
      <property role="3tVfz5" value="2004525961659099700" />
      <property role="TrG5h" value="manual_record" />
      <property role="1L1pqM" value="manual_record" />
    </node>
    <node concept="25R33" id="1bNmcZ3F2Oc" role="25R1y">
      <property role="3tVfz5" value="8812085971939243480" />
      <property role="TrG5h" value="inspection_note" />
      <property role="1L1pqM" value="inspection_note" />
    </node>
    <node concept="25R33" id="1bNmcZ3F2Od" role="25R1y">
      <property role="3tVfz5" value="729872057208568272" />
      <property role="TrG5h" value="analysis_report" />
      <property role="1L1pqM" value="analysis_report" />
    </node>
  </node>
  <node concept="25R3W" id="1bNmcZ3F2Op">
    <property role="3F6X1D" value="1365532761387707673" />
    <property role="TrG5h" value="DataDirectionEnum" />
    <node concept="25R33" id="1bNmcZ3F2Or" role="25R1y">
      <property role="3tVfz5" value="4780794098497546900" />
      <property role="TrG5h" value="read" />
      <property role="1L1pqM" value="read" />
    </node>
    <node concept="25R33" id="1bNmcZ3F2Os" role="25R1y">
      <property role="3tVfz5" value="4643681081019618305" />
      <property role="TrG5h" value="write" />
      <property role="1L1pqM" value="write" />
    </node>
    <node concept="25R33" id="1bNmcZ3F2Ot" role="25R1y">
      <property role="3tVfz5" value="3937039880864672682" />
      <property role="TrG5h" value="read_write" />
      <property role="1L1pqM" value="read_write" />
    </node>
  </node>
  <node concept="25R3W" id="1bNmcZ3F2OD">
    <property role="3F6X1D" value="1365532761387707689" />
    <property role="TrG5h" value="TrustZoneEnum" />
    <node concept="25R33" id="1bNmcZ3F2OF" role="25R1y">
      <property role="3tVfz5" value="5095602192084007604" />
      <property role="TrG5h" value="clinical_network" />
      <property role="1L1pqM" value="clinical_network" />
    </node>
    <node concept="25R33" id="1bNmcZ3F2OG" role="25R1y">
      <property role="3tVfz5" value="8279989909729208621" />
      <property role="TrG5h" value="segmented_research" />
      <property role="1L1pqM" value="segmented_research" />
    </node>
    <node concept="25R33" id="1bNmcZ3F2OH" role="25R1y">
      <property role="3tVfz5" value="2225550049616910641" />
      <property role="TrG5h" value="vendor_managed" />
      <property role="1L1pqM" value="vendor_managed" />
    </node>
    <node concept="25R33" id="1bNmcZ3F2OI" role="25R1y">
      <property role="3tVfz5" value="3432838068210285305" />
      <property role="TrG5h" value="public" />
      <property role="1L1pqM" value="public" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2OU">
    <property role="EcuMT" value="1365532761387707706" />
    <property role="TrG5h" value="Team" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2P2" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707714" />
      <property role="TrG5h" value="teamName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2P3" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707715" />
      <property role="TrG5h" value="accountableRole" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2OV">
    <property role="EcuMT" value="1365532761387707707" />
    <property role="TrG5h" value="ConfigurationBaseline" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2P4" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707716" />
      <property role="TrG5h" value="baselineName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2P5" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707717" />
      <property role="TrG5h" value="configurationHash" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2OW">
    <property role="EcuMT" value="1365532761387707708" />
    <property role="TrG5h" value="AcceptanceCriterion" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2P6" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707718" />
      <property role="TrG5h" value="criterionText" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2P7" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707719" />
      <property role="TrG5h" value="measurable" />
      <ref role="AX2Wp" to="tpck:fKAQMTB" resolve="boolean" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2OX">
    <property role="EcuMT" value="1365532761387707709" />
    <property role="TrG5h" value="ExecutableSuiteRef" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2P8" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707720" />
      <property role="TrG5h" value="suiteId" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2P9" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707721" />
      <property role="TrG5h" value="toolchain" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2OY">
    <property role="EcuMT" value="1365532761387707710" />
    <property role="TrG5h" value="ManualEvidenceRef" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2Pa" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707722" />
      <property role="TrG5h" value="evidenceId" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2Pb" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707723" />
      <property role="TrG5h" value="recordLocation" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2Pc" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707724" />
      <property role="TrG5h" value="recordedByRole" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2OZ">
    <property role="EcuMT" value="1365532761387707711" />
    <property role="TrG5h" value="EvidenceRequirement" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2Pd" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707725" />
      <property role="TrG5h" value="requirementText" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2Pe" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707726" />
      <property role="TrG5h" value="evidenceKind" />
      <ref role="AX2Wp" node="1bNmcZ3F2O8" resolve="EvidenceKindEnum" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2P0">
    <property role="EcuMT" value="1365532761387707712" />
    <property role="TrG5h" value="AdapterCapability" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2Pf" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707727" />
      <property role="TrG5h" value="capabilityName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2Pg" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707728" />
      <property role="TrG5h" value="direction" />
      <ref role="AX2Wp" node="1bNmcZ3F2Op" resolve="DataDirectionEnum" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2Ph" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707729" />
      <property role="TrG5h" value="trustZone" />
      <ref role="AX2Wp" node="1bNmcZ3F2OD" resolve="TrustZoneEnum" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2Pi" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707730" />
      <property role="TrG5h" value="destination" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2Pj" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707731" />
      <property role="TrG5h" value="commissionedProfile" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2P1">
    <property role="EcuMT" value="1365532761387707713" />
    <property role="TrG5h" value="ImportedHLR" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="ol33:1bNmcZ2iQmG" resolve="Requirement" />
    <node concept="1TJgyi" id="1bNmcZ3F2Pk" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707732" />
      <property role="TrG5h" value="bundleId" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2Pl" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707733" />
      <property role="TrG5h" value="authoritative" />
      <ref role="AX2Wp" to="tpck:fKAQMTB" resolve="boolean" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2Px">
    <property role="EcuMT" value="1365532761387707745" />
    <property role="TrG5h" value="Component" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2P$" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707748" />
      <property role="TrG5h" value="componentName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2P_" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707749" />
      <property role="TrG5h" value="responsibility" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2PA" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707750" />
      <property role="20kJfa" value="owningTeam" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ3F2OU" resolve="Team" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2Py">
    <property role="EcuMT" value="1365532761387707746" />
    <property role="TrG5h" value="ExternalSystem" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2PB" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707751" />
      <property role="TrG5h" value="systemName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2PC" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707752" />
      <property role="TrG5h" value="vendor" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2PD" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707753" />
      <property role="20kJfa" value="capabilities" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3F2P0" resolve="AdapterCapability" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2Pz">
    <property role="EcuMT" value="1365532761387707747" />
    <property role="TrG5h" value="VerificationClaim" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2PE" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707754" />
      <property role="TrG5h" value="claimName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2PF" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707755" />
      <property role="TrG5h" value="verdict" />
      <ref role="AX2Wp" node="1bNmcZ3F2NR" resolve="VerificationVerdictEnum" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2PG" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707756" />
      <property role="20kJfa" value="criteria" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3F2OW" resolve="AcceptanceCriterion" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2PH" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707757" />
      <property role="20kJfa" value="executableSuites" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3F2OX" resolve="ExecutableSuiteRef" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2PI" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707758" />
      <property role="20kJfa" value="manualEvidence" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3F2OY" resolve="ManualEvidenceRef" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2PJ" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707759" />
      <property role="20kJfa" value="evidenceRequirements" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3F2OZ" resolve="EvidenceRequirement" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2PK" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707760" />
      <property role="20kJfa" value="verifies" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" to="ol33:1bNmcZ2iQmG" resolve="Requirement" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2PL" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707761" />
      <property role="20kJfa" value="owningTeam" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ3F2OU" resolve="Team" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2PM" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707762" />
      <property role="20kJfa" value="atConfiguration" />
      <ref role="20lvS9" node="1bNmcZ3F2OV" resolve="ConfigurationBaseline" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2PY">
    <property role="EcuMT" value="1365532761387707774" />
    <property role="TrG5h" value="Allocation" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2Q1" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707777" />
      <property role="TrG5h" value="rationale" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2Q2" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707778" />
      <property role="20kJfa" value="allocatedRequirement" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" to="ol33:1bNmcZ2iQmG" resolve="Requirement" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2Q3" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707779" />
      <property role="20kJfa" value="component" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ3F2Px" resolve="Component" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2Q4" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707780" />
      <property role="20kJfa" value="owningTeam" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ3F2OU" resolve="Team" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2PZ">
    <property role="EcuMT" value="1365532761387707775" />
    <property role="TrG5h" value="InterfaceContract" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2Q5" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707781" />
      <property role="TrG5h" value="contractName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ3F2Q6" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707782" />
      <property role="TrG5h" value="synchronous" />
      <ref role="AX2Wp" to="tpck:fKAQMTB" resolve="boolean" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2Q7" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707783" />
      <property role="20kJfa" value="provider" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ3F2Px" resolve="Component" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2Q8" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707784" />
      <property role="20kJfa" value="consumer" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ3F2Px" resolve="Component" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2Q0">
    <property role="EcuMT" value="1365532761387707776" />
    <property role="TrG5h" value="InterfaceFamily" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2Q9" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707785" />
      <property role="TrG5h" value="familyName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2Qa" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707786" />
      <property role="20kJfa" value="contracts" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3F2PZ" resolve="InterfaceContract" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2Qm">
    <property role="EcuMT" value="1365532761387707798" />
    <property role="TrG5h" value="ArchitectureRealization" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2Qq" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707802" />
      <property role="TrG5h" value="name" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2Qr" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707803" />
      <property role="20kJfa" value="components" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3F2Px" resolve="Component" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2Qs" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707804" />
      <property role="20kJfa" value="teams" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3F2OU" resolve="Team" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2Qt" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707805" />
      <property role="20kJfa" value="allocations" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3F2PY" resolve="Allocation" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2Qu" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707806" />
      <property role="20kJfa" value="configurations" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3F2OV" resolve="ConfigurationBaseline" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2Qn">
    <property role="EcuMT" value="1365532761387707799" />
    <property role="TrG5h" value="InterfaceCatalog" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2Qv" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707807" />
      <property role="TrG5h" value="name" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2Qw" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707808" />
      <property role="20kJfa" value="families" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3F2Q0" resolve="InterfaceFamily" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2Qo">
    <property role="EcuMT" value="1365532761387707800" />
    <property role="TrG5h" value="VerificationBaseline" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2Qx" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707809" />
      <property role="TrG5h" value="name" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2Qy" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707810" />
      <property role="20kJfa" value="claims" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3F2Pz" resolve="VerificationClaim" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ3F2Qp">
    <property role="EcuMT" value="1365532761387707801" />
    <property role="TrG5h" value="AdapterCatalog" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ3F2Qz" role="1TKVEl">
      <property role="IQ2nx" value="1365532761387707811" />
      <property role="TrG5h" value="name" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ3F2Q$" role="1TKVEi">
      <property role="IQ2ns" value="1365532761387707812" />
      <property role="20kJfa" value="systems" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ3F2Py" resolve="ExternalSystem" />
    </node>
  </node>
</model>

