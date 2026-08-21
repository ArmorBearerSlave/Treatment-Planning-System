<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:07b10a47-b937-4aa9-ad53-c2e3280bb0f3(nltps.foundation.structure)">
  <persistence version="9" />
  <languages>
    <use id="c72da2b9-7cce-4447-8389-f407dc1158b7" name="jetbrains.mps.lang.structure" version="9" />
    <devkit ref="78434eb8-b0e5-444b-850d-e7c4ad2da9ab(jetbrains.mps.devkit.aspect.structure)" />
  </languages>
  <imports>
    <import index="tpck" ref="r:00000000-0000-4000-0000-011c89590288(jetbrains.mps.lang.core.structure)" />
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
        <property id="4628067390765956802" name="abstract" index="R5$K7" />
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
  <node concept="25R3W" id="1bNmcZ2iEqI">
    <property role="3F6X1D" value="1365532761364539054" />
    <property role="TrG5h" value="LifecycleStateEnum" />
    <node concept="25R33" id="1bNmcZ2iEqK" role="25R1y">
      <property role="3tVfz5" value="4681353882189179079" />
      <property role="TrG5h" value="draft" />
      <property role="1L1pqM" value="draft" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEqL" role="25R1y">
      <property role="3tVfz5" value="3973094265416042804" />
      <property role="TrG5h" value="proposed" />
      <property role="1L1pqM" value="proposed" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEqM" role="25R1y">
      <property role="3tVfz5" value="4242776863707717646" />
      <property role="TrG5h" value="reviewed" />
      <property role="1L1pqM" value="reviewed" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEqN" role="25R1y">
      <property role="3tVfz5" value="677575931061439266" />
      <property role="TrG5h" value="approved" />
      <property role="1L1pqM" value="approved" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEqO" role="25R1y">
      <property role="3tVfz5" value="3178812603523149326" />
      <property role="TrG5h" value="effective" />
      <property role="1L1pqM" value="effective" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEqP" role="25R1y">
      <property role="3tVfz5" value="1162831981239765066" />
      <property role="TrG5h" value="superseded" />
      <property role="1L1pqM" value="superseded" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEqQ" role="25R1y">
      <property role="3tVfz5" value="6743565606916228437" />
      <property role="TrG5h" value="retired" />
      <property role="1L1pqM" value="retired" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEqR" role="25R1y">
      <property role="3tVfz5" value="601031440706328587" />
      <property role="TrG5h" value="withdrawn" />
      <property role="1L1pqM" value="withdrawn" />
    </node>
  </node>
  <node concept="25R3W" id="1bNmcZ2iEqU">
    <property role="3F6X1D" value="1365532761364539066" />
    <property role="TrG5h" value="AuthorityClassEnum" />
    <node concept="25R33" id="1bNmcZ2iEqW" role="25R1y">
      <property role="3tVfz5" value="7448726309117037100" />
      <property role="TrG5h" value="patient_specific_authority" />
      <property role="1L1pqM" value="patient_specific_authority" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEqX" role="25R1y">
      <property role="3tVfz5" value="7928481952409679625" />
      <property role="TrG5h" value="protocol_authority" />
      <property role="1L1pqM" value="protocol_authority" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEqY" role="25R1y">
      <property role="3tVfz5" value="3357753120246553755" />
      <property role="TrG5h" value="institutional_standard" />
      <property role="1L1pqM" value="institutional_standard" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEqZ" role="25R1y">
      <property role="3tVfz5" value="5640683532820908225" />
      <property role="TrG5h" value="institutional_procedure" />
      <property role="1L1pqM" value="institutional_procedure" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEr0" role="25R1y">
      <property role="3tVfz5" value="1237717721994257205" />
      <property role="TrG5h" value="professional_guidance" />
      <property role="1L1pqM" value="professional_guidance" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEr1" role="25R1y">
      <property role="3tVfz5" value="736437823207140459" />
      <property role="TrG5h" value="technical_guidance" />
      <property role="1L1pqM" value="technical_guidance" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEr2" role="25R1y">
      <property role="3tVfz5" value="9039981131681300050" />
      <property role="TrG5h" value="authoritative_qa_record" />
      <property role="1L1pqM" value="authoritative_qa_record" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEr3" role="25R1y">
      <property role="3tVfz5" value="6350529443124676103" />
      <property role="TrG5h" value="commissioning_evidence" />
      <property role="1L1pqM" value="commissioning_evidence" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEr4" role="25R1y">
      <property role="3tVfz5" value="2117844453836069051" />
      <property role="TrG5h" value="peer_reviewed_evidence" />
      <property role="1L1pqM" value="peer_reviewed_evidence" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEr5" role="25R1y">
      <property role="3tVfz5" value="9210040616070742870" />
      <property role="TrG5h" value="retrieval_evidence" />
      <property role="1L1pqM" value="retrieval_evidence" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEr6" role="25R1y">
      <property role="3tVfz5" value="5208303270169744288" />
      <property role="TrG5h" value="derived_analytics" />
      <property role="1L1pqM" value="derived_analytics" />
    </node>
  </node>
  <node concept="25R3W" id="1bNmcZ2iEr9">
    <property role="3F6X1D" value="1365532761364539081" />
    <property role="TrG5h" value="DoseBasisEnum" />
    <node concept="25R33" id="1bNmcZ2iErb" role="25R1y">
      <property role="3tVfz5" value="6409524104647911995" />
      <property role="TrG5h" value="physical_absorbed" />
      <property role="1L1pqM" value="physical_absorbed" />
    </node>
    <node concept="25R33" id="1bNmcZ2iErc" role="25R1y">
      <property role="3tVfz5" value="8201615488398588038" />
      <property role="TrG5h" value="rbe_weighted" />
      <property role="1L1pqM" value="rbe_weighted" />
    </node>
    <node concept="25R33" id="1bNmcZ2iErd" role="25R1y">
      <property role="3tVfz5" value="3663538068258315607" />
      <property role="TrG5h" value="bed" />
      <property role="1L1pqM" value="bed" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEre" role="25R1y">
      <property role="3tVfz5" value="4407958052655350157" />
      <property role="TrG5h" value="eqd2" />
      <property role="1L1pqM" value="eqd2" />
    </node>
    <node concept="25R33" id="1bNmcZ2iErf" role="25R1y">
      <property role="3tVfz5" value="4907861132042141029" />
      <property role="TrG5h" value="not_applicable" />
      <property role="1L1pqM" value="not_applicable" />
    </node>
  </node>
  <node concept="25R3W" id="1bNmcZ2iEri">
    <property role="3F6X1D" value="1365532761364539090" />
    <property role="TrG5h" value="DimensionEnum" />
    <node concept="25R33" id="1bNmcZ2iErk" role="25R1y">
      <property role="3tVfz5" value="884811871472512723" />
      <property role="TrG5h" value="dose" />
      <property role="1L1pqM" value="dose" />
    </node>
    <node concept="25R33" id="1bNmcZ2iErl" role="25R1y">
      <property role="3tVfz5" value="1671410498033060285" />
      <property role="TrG5h" value="length" />
      <property role="1L1pqM" value="length" />
    </node>
    <node concept="25R33" id="1bNmcZ2iErm" role="25R1y">
      <property role="3tVfz5" value="8362596284469897237" />
      <property role="TrG5h" value="mass" />
      <property role="1L1pqM" value="mass" />
    </node>
    <node concept="25R33" id="1bNmcZ2iErn" role="25R1y">
      <property role="3tVfz5" value="4502557198292508536" />
      <property role="TrG5h" value="time" />
      <property role="1L1pqM" value="time" />
    </node>
    <node concept="25R33" id="1bNmcZ2iEro" role="25R1y">
      <property role="3tVfz5" value="7526866924574955561" />
      <property role="TrG5h" value="energy" />
      <property role="1L1pqM" value="energy" />
    </node>
    <node concept="25R33" id="1bNmcZ2iErp" role="25R1y">
      <property role="3tVfz5" value="5085909976535718247" />
      <property role="TrG5h" value="count" />
      <property role="1L1pqM" value="count" />
    </node>
    <node concept="25R33" id="1bNmcZ2iErq" role="25R1y">
      <property role="3tVfz5" value="3343266095071171905" />
      <property role="TrG5h" value="fraction" />
      <property role="1L1pqM" value="fraction" />
    </node>
    <node concept="25R33" id="1bNmcZ2iErr" role="25R1y">
      <property role="3tVfz5" value="8935336350171647324" />
      <property role="TrG5h" value="percentage" />
      <property role="1L1pqM" value="percentage" />
    </node>
    <node concept="25R33" id="1bNmcZ2iErs" role="25R1y">
      <property role="3tVfz5" value="2683103381032540552" />
      <property role="TrG5h" value="dimensionless" />
      <property role="1L1pqM" value="dimensionless" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2iEsv">
    <property role="EcuMT" value="1365532761364539167" />
    <property role="TrG5h" value="GovernedElement" />
    <property role="R5$K7" value="true" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyj" id="1bNmcZ2iEsG" role="1TKVEi">
      <property role="IQ2ns" value="1365532761364539180" />
      <property role="20kJfa" value="identifier" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ2iEsw" resolve="StableId" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2iEsH" role="1TKVEi">
      <property role="IQ2ns" value="1365532761364539181" />
      <property role="20kJfa" value="version" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ2iEsy" resolve="Version" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2iEsI" role="1TKVEi">
      <property role="IQ2ns" value="1365532761364539182" />
      <property role="20kJfa" value="aliases" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2iEsx" resolve="Alias" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2iEsJ" role="1TKVEi">
      <property role="IQ2ns" value="1365532761364539183" />
      <property role="20kJfa" value="provenance" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2iEsB" resolve="ProvenanceRef" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2iEsK" role="1TKVEi">
      <property role="IQ2ns" value="1365532761364539184" />
      <property role="20kJfa" value="lifecycleState" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ2iEsz" resolve="LifecycleState" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2iEsL" role="1TKVEi">
      <property role="IQ2ns" value="1365532761364539185" />
      <property role="20kJfa" value="authorityClass" />
      <ref role="20lvS9" node="1bNmcZ2iEs$" resolve="AuthorityClass" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2iEsw">
    <property role="EcuMT" value="1365532761364539168" />
    <property role="TrG5h" value="StableId" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2iEsM" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539186" />
      <property role="TrG5h" value="value" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEsN" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539187" />
      <property role="TrG5h" value="namespace" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2iEsx">
    <property role="EcuMT" value="1365532761364539169" />
    <property role="TrG5h" value="Alias" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2iEsO" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539188" />
      <property role="TrG5h" value="value" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEsP" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539189" />
      <property role="TrG5h" value="scheme" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEtH" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539245" />
      <property role="TrG5h" value="retired" />
      <ref role="AX2Wp" to="tpck:fKAQMTB" resolve="boolean" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2iEsy">
    <property role="EcuMT" value="1365532761364539170" />
    <property role="TrG5h" value="Version" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2iEsR" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539191" />
      <property role="TrG5h" value="value" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEsS" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539192" />
      <property role="TrG5h" value="effectiveDate" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEsT" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539193" />
      <property role="TrG5h" value="supersededDate" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2iEsz">
    <property role="EcuMT" value="1365532761364539171" />
    <property role="TrG5h" value="LifecycleState" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2iEsU" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539194" />
      <property role="TrG5h" value="state" />
      <ref role="AX2Wp" node="1bNmcZ2iEqI" resolve="LifecycleStateEnum" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEsV" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539195" />
      <property role="TrG5h" value="ordinal" />
      <ref role="AX2Wp" to="tpck:fKAQMTA" resolve="integer" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEsW" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539196" />
      <property role="TrG5h" value="terminal" />
      <ref role="AX2Wp" to="tpck:fKAQMTB" resolve="boolean" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2iEs$">
    <property role="EcuMT" value="1365532761364539172" />
    <property role="TrG5h" value="AuthorityClass" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2iEsX" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539197" />
      <property role="TrG5h" value="authority" />
      <ref role="AX2Wp" node="1bNmcZ2iEqU" resolve="AuthorityClassEnum" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEsY" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539198" />
      <property role="TrG5h" value="rank" />
      <ref role="AX2Wp" to="tpck:fKAQMTA" resolve="integer" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEsZ" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539199" />
      <property role="TrG5h" value="description" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2iEs_">
    <property role="EcuMT" value="1365532761364539173" />
    <property role="TrG5h" value="PhysicalQuantity" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2iEt0" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539200" />
      <property role="TrG5h" value="magnitude" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEt1" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539201" />
      <property role="TrG5h" value="doseBasis" />
      <ref role="AX2Wp" node="1bNmcZ2iEr9" resolve="DoseBasisEnum" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2iEt2" role="1TKVEi">
      <property role="IQ2ns" value="1365532761364539202" />
      <property role="20kJfa" value="unit" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ2iEsA" resolve="Unit" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2iEsA">
    <property role="EcuMT" value="1365532761364539174" />
    <property role="TrG5h" value="Unit" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2iEt3" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539203" />
      <property role="TrG5h" value="symbol" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEt4" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539204" />
      <property role="TrG5h" value="dimension" />
      <ref role="AX2Wp" node="1bNmcZ2iEri" resolve="DimensionEnum" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEt5" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539205" />
      <property role="TrG5h" value="doseBasis" />
      <ref role="AX2Wp" node="1bNmcZ2iEr9" resolve="DoseBasisEnum" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2iEsB">
    <property role="EcuMT" value="1365532761364539175" />
    <property role="TrG5h" value="ProvenanceRef" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2iEt6" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539206" />
      <property role="TrG5h" value="sourcePath" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEt7" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539207" />
      <property role="TrG5h" value="sourceLine" />
      <ref role="AX2Wp" to="tpck:fKAQMTA" resolve="integer" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEt8" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539208" />
      <property role="TrG5h" value="sha256" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2iEsC">
    <property role="EcuMT" value="1365532761364539176" />
    <property role="TrG5h" value="ExternalReference" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2iEt9" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539209" />
      <property role="TrG5h" value="title" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEta" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539210" />
      <property role="TrG5h" value="locator" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEtb" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539211" />
      <property role="TrG5h" value="edition" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEtc" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539212" />
      <property role="TrG5h" value="retrievedDate" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2iEtd" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539213" />
      <property role="TrG5h" value="integrityValue" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2iEsD">
    <property role="EcuMT" value="1365532761364539177" />
    <property role="TrG5h" value="AuthorityVocabulary" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2iEte" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539214" />
      <property role="TrG5h" value="name" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2iEtf" role="1TKVEi">
      <property role="IQ2ns" value="1365532761364539215" />
      <property role="20kJfa" value="classes" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2iEs$" resolve="AuthorityClass" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2iEsE">
    <property role="EcuMT" value="1365532761364539178" />
    <property role="TrG5h" value="UnitCatalog" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2iEtg" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539216" />
      <property role="TrG5h" value="name" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2iEth" role="1TKVEi">
      <property role="IQ2ns" value="1365532761364539217" />
      <property role="20kJfa" value="units" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2iEsA" resolve="Unit" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2iEsF">
    <property role="EcuMT" value="1365532761364539179" />
    <property role="TrG5h" value="LifecycleVocabulary" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="1bNmcZ2iEti" role="1TKVEl">
      <property role="IQ2nx" value="1365532761364539218" />
      <property role="TrG5h" value="name" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2iEtj" role="1TKVEi">
      <property role="IQ2ns" value="1365532761364539219" />
      <property role="20kJfa" value="states" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2iEsz" resolve="LifecycleState" />
    </node>
  </node>
</model>

