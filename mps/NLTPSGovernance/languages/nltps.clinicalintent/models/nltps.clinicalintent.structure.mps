<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:4741d84b-80d0-4a09-848d-cb03c7811725(nltps.clinicalintent.structure)">
  <persistence version="9" />
  <languages>
    <devkit ref="78434eb8-b0e5-444b-850d-e7c4ad2da9ab(jetbrains.mps.devkit.aspect.structure)" />
  </languages>
  <imports>
    <import index="ol33" ref="r:e3f43cc2-9854-4561-9b2a-13d5891c34c9(nltps.governance.structure)" />
    <import index="5q6" ref="r:07b10a47-b937-4aa9-ad53-c2e3280bb0f3(nltps.foundation.structure)" implicit="true" />
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
  <node concept="25R3W" id="1bNmcZ2XU_c">
    <property role="3F6X1D" value="1365532761375877452" />
    <property role="TrG5h" value="AutonomyLevelEnum" />
    <node concept="25R33" id="1bNmcZ2XU_e" role="25R1y">
      <property role="3tVfz5" value="6749285000948932786" />
      <property role="TrG5h" value="A0_inform" />
      <property role="1L1pqM" value="A0_inform" />
    </node>
    <node concept="25R33" id="1bNmcZ2XU_f" role="25R1y">
      <property role="3tVfz5" value="8411849277605118605" />
      <property role="TrG5h" value="A1_draft" />
      <property role="1L1pqM" value="A1_draft" />
    </node>
    <node concept="25R33" id="1bNmcZ2XU_g" role="25R1y">
      <property role="3tVfz5" value="8802936983869323210" />
      <property role="TrG5h" value="A2_sandbox_execute" />
      <property role="1L1pqM" value="A2_sandbox_execute" />
    </node>
    <node concept="25R33" id="1bNmcZ2XU_h" role="25R1y">
      <property role="3tVfz5" value="5348815439146947361" />
      <property role="TrG5h" value="A3_clinical_candidate" />
      <property role="1L1pqM" value="A3_clinical_candidate" />
    </node>
    <node concept="25R33" id="1bNmcZ2XU_i" role="25R1y">
      <property role="3tVfz5" value="952171146689553412" />
      <property role="TrG5h" value="A4_authorize_or_deliver" />
      <property role="1L1pqM" value="A4_authorize_or_deliver" />
    </node>
  </node>
  <node concept="25R3W" id="1bNmcZ2XU_l">
    <property role="3F6X1D" value="1365532761375877461" />
    <property role="TrG5h" value="ActorKindEnum" />
    <node concept="25R33" id="1bNmcZ2XU_n" role="25R1y">
      <property role="3tVfz5" value="1297988914046976912" />
      <property role="TrG5h" value="HUMAN" />
      <property role="1L1pqM" value="HUMAN" />
    </node>
    <node concept="25R33" id="1bNmcZ2XU_o" role="25R1y">
      <property role="3tVfz5" value="1395389743501678967" />
      <property role="TrG5h" value="SERVICE_ACCOUNT" />
      <property role="1L1pqM" value="SERVICE_ACCOUNT" />
    </node>
    <node concept="25R33" id="1bNmcZ2XU_p" role="25R1y">
      <property role="3tVfz5" value="7755301726373670665" />
      <property role="TrG5h" value="AUTOMATED_AGENT" />
      <property role="1L1pqM" value="AUTOMATED_AGENT" />
    </node>
    <node concept="25R33" id="1bNmcZ2XU_q" role="25R1y">
      <property role="3tVfz5" value="3370589103545085898" />
      <property role="TrG5h" value="GENERATOR" />
      <property role="1L1pqM" value="GENERATOR" />
    </node>
    <node concept="25R33" id="1bNmcZ2XU_r" role="25R1y">
      <property role="3tVfz5" value="4903568655703951445" />
      <property role="TrG5h" value="MODEL_NODE" />
      <property role="1L1pqM" value="MODEL_NODE" />
    </node>
  </node>
  <node concept="25R3W" id="1bNmcZ2XU_u">
    <property role="3F6X1D" value="1365532761375877470" />
    <property role="TrG5h" value="ComparisonOperatorEnum" />
    <node concept="25R33" id="1bNmcZ2XU_w" role="25R1y">
      <property role="3tVfz5" value="1124697316962857772" />
      <property role="TrG5h" value="lt" />
      <property role="1L1pqM" value="lt" />
    </node>
    <node concept="25R33" id="1bNmcZ2XU_x" role="25R1y">
      <property role="3tVfz5" value="3792837535108312580" />
      <property role="TrG5h" value="le" />
      <property role="1L1pqM" value="le" />
    </node>
    <node concept="25R33" id="1bNmcZ2XU_y" role="25R1y">
      <property role="3tVfz5" value="4399751441507831857" />
      <property role="TrG5h" value="gt" />
      <property role="1L1pqM" value="gt" />
    </node>
    <node concept="25R33" id="1bNmcZ2XU_z" role="25R1y">
      <property role="3tVfz5" value="3990939331416061237" />
      <property role="TrG5h" value="ge" />
      <property role="1L1pqM" value="ge" />
    </node>
    <node concept="25R33" id="1bNmcZ2XU_$" role="25R1y">
      <property role="3tVfz5" value="2348493728328713877" />
      <property role="TrG5h" value="eq" />
      <property role="1L1pqM" value="eq" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XU_B">
    <property role="EcuMT" value="1365532761375877479" />
    <property role="TrG5h" value="ClinicalObjectType" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XU_C" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877480" />
      <property role="TrG5h" value="typeName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XU_D" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877481" />
      <property role="TrG5h" value="description" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XU_G">
    <property role="EcuMT" value="1365532761375877484" />
    <property role="TrG5h" value="ActionDefinition" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XU_I" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877486" />
      <property role="TrG5h" value="actionName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XU_J" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877487" />
      <property role="TrG5h" value="autonomyLevel" />
      <ref role="AX2Wp" node="1bNmcZ2XU_c" resolve="AutonomyLevelEnum" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XU_K" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877488" />
      <property role="TrG5h" value="description" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XU_L" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877489" />
      <property role="20kJfa" value="appliesTo" />
      <ref role="20lvS9" node="1bNmcZ2XU_B" resolve="ClinicalObjectType" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XU_H">
    <property role="EcuMT" value="1365532761375877485" />
    <property role="TrG5h" value="ConstraintDefinition" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XU_M" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877490" />
      <property role="TrG5h" value="constraintName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XU_N" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877491" />
      <property role="TrG5h" value="comparison" />
      <ref role="AX2Wp" node="1bNmcZ2XU_u" resolve="ComparisonOperatorEnum" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XU_O" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877492" />
      <property role="TrG5h" value="structure" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XU_P" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877493" />
      <property role="20kJfa" value="limit" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" to="5q6:1bNmcZ2iEs_" resolve="PhysicalQuantity" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XU_V">
    <property role="EcuMT" value="1365532761375877499" />
    <property role="TrG5h" value="RobustnessScenarioDefinition" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUA0" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877504" />
      <property role="TrG5h" value="scenarioName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUA1" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877505" />
      <property role="TrG5h" value="perturbation" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUA2" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877506" />
      <property role="TrG5h" value="magnitudeDescription" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XU_W">
    <property role="EcuMT" value="1365532761375877500" />
    <property role="TrG5h" value="OperatingMode" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUA3" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877507" />
      <property role="TrG5h" value="modeName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUA4" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877508" />
      <property role="TrG5h" value="description" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XU_X">
    <property role="EcuMT" value="1365532761375877501" />
    <property role="TrG5h" value="ComputableRule" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUA5" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877509" />
      <property role="TrG5h" value="ruleName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUA6" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877510" />
      <property role="TrG5h" value="expression" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUA7" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877511" />
      <property role="TrG5h" value="evaluable" />
      <ref role="AX2Wp" to="tpck:fKAQMTB" resolve="boolean" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XU_Y">
    <property role="EcuMT" value="1365532761375877502" />
    <property role="TrG5h" value="WorkflowState" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUA8" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877512" />
      <property role="TrG5h" value="stateName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUA9" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877513" />
      <property role="TrG5h" value="terminal" />
      <ref role="AX2Wp" to="tpck:fKAQMTB" resolve="boolean" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XU_Z">
    <property role="EcuMT" value="1365532761375877503" />
    <property role="TrG5h" value="EvidenceProfile" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUAa" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877514" />
      <property role="TrG5h" value="profileName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUAb" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877515" />
      <property role="TrG5h" value="requiredTier" />
      <ref role="AX2Wp" to="5q6:1bNmcZ2iEqU" resolve="AuthorityClassEnum" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAc" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877516" />
      <property role="20kJfa" value="citations" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" to="5q6:1bNmcZ2iEsC" resolve="ExternalReference" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUAf">
    <property role="EcuMT" value="1365532761375877519" />
    <property role="TrG5h" value="CommissionedUseEnvelope" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUAk" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877524" />
      <property role="TrG5h" value="envelopeName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUAl" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877525" />
      <property role="TrG5h" value="scopeDescription" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUAm" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877526" />
      <property role="TrG5h" value="commissionedOn" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUAg">
    <property role="EcuMT" value="1365532761375877520" />
    <property role="TrG5h" value="ModelProfile" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUAn" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877527" />
      <property role="TrG5h" value="modelName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUAo" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877528" />
      <property role="TrG5h" value="modelVersion" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUAp" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877529" />
      <property role="TrG5h" value="validated" />
      <ref role="AX2Wp" to="tpck:fKAQMTB" resolve="boolean" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUAh">
    <property role="EcuMT" value="1365532761375877521" />
    <property role="TrG5h" value="MachineProfile" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUAq" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877530" />
      <property role="TrG5h" value="machineName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUAr" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877531" />
      <property role="TrG5h" value="configuration" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUAi">
    <property role="EcuMT" value="1365532761375877522" />
    <property role="TrG5h" value="ProfessionalRole" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUAs" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877532" />
      <property role="TrG5h" value="title" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUAt" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877533" />
      <property role="TrG5h" value="credentialBasis" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUAj">
    <property role="EcuMT" value="1365532761375877523" />
    <property role="TrG5h" value="OperationalRole" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUAu" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877534" />
      <property role="TrG5h" value="functionName" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUAv" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877535" />
      <property role="TrG5h" value="description" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUAy">
    <property role="EcuMT" value="1365532761375877538" />
    <property role="TrG5h" value="RoleCapability" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUAB" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877543" />
      <property role="TrG5h" value="requiresApproval" />
      <ref role="AX2Wp" to="tpck:fKAQMTB" resolve="boolean" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAC" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877544" />
      <property role="20kJfa" value="professionalRole" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ2XUAi" resolve="ProfessionalRole" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAD" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877545" />
      <property role="20kJfa" value="operationalRole" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ2XUAj" resolve="OperationalRole" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAE" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877546" />
      <property role="20kJfa" value="allowedAction" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ2XU_G" resolve="ActionDefinition" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAF" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877547" />
      <property role="20kJfa" value="targetScope" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ2XU_B" resolve="ClinicalObjectType" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAG" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877548" />
      <property role="20kJfa" value="workflowState" />
      <ref role="20lvS9" node="1bNmcZ2XU_Y" resolve="WorkflowState" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUAz">
    <property role="EcuMT" value="1365532761375877539" />
    <property role="TrG5h" value="AuthorizedActor" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUAH" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877549" />
      <property role="TrG5h" value="principalId" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUAI" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877550" />
      <property role="TrG5h" value="actorKind" />
      <ref role="AX2Wp" node="1bNmcZ2XU_l" resolve="ActorKindEnum" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAJ" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877551" />
      <property role="20kJfa" value="professionalRole" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ2XUAi" resolve="ProfessionalRole" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAK" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877552" />
      <property role="20kJfa" value="operationalRole" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ2XUAj" resolve="OperationalRole" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUA$">
    <property role="EcuMT" value="1365532761375877540" />
    <property role="TrG5h" value="PlanIntentDefinition" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUAL" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877553" />
      <property role="TrG5h" value="name" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUAM" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877554" />
      <property role="TrG5h" value="aiCreatable" />
      <ref role="AX2Wp" to="tpck:fKAQMTB" resolve="boolean" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAN" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877555" />
      <property role="20kJfa" value="objectTypes" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XU_B" resolve="ClinicalObjectType" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAO" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877556" />
      <property role="20kJfa" value="actions" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XU_G" resolve="ActionDefinition" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAP" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877557" />
      <property role="20kJfa" value="constraints" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XU_H" resolve="ConstraintDefinition" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAQ" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877558" />
      <property role="20kJfa" value="robustnessScenarios" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XU_V" resolve="RobustnessScenarioDefinition" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAR" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877559" />
      <property role="20kJfa" value="operatingModes" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XU_W" resolve="OperatingMode" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAS" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877560" />
      <property role="20kJfa" value="computableRules" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XU_X" resolve="ComputableRule" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUA_">
    <property role="EcuMT" value="1365532761375877541" />
    <property role="TrG5h" value="AuthorityPolicy" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUAT" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877561" />
      <property role="TrG5h" value="name" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUAU" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877562" />
      <property role="TrG5h" value="institution" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAV" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877563" />
      <property role="20kJfa" value="professionalRoles" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XUAi" resolve="ProfessionalRole" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAW" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877564" />
      <property role="20kJfa" value="operationalRoles" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XUAj" resolve="OperationalRole" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAX" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877565" />
      <property role="20kJfa" value="capabilities" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XUAy" resolve="RoleCapability" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUAY" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877566" />
      <property role="20kJfa" value="actors" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XUAz" resolve="AuthorizedActor" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUAA">
    <property role="EcuMT" value="1365532761375877542" />
    <property role="TrG5h" value="ReleaseProfile" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUAZ" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877567" />
      <property role="TrG5h" value="name" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUB0" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877568" />
      <property role="TrG5h" value="intendedUse" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUB1" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877569" />
      <property role="TrG5h" value="releaseState" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUB2" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877570" />
      <property role="20kJfa" value="evidenceProfiles" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XU_Z" resolve="EvidenceProfile" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUB3" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877571" />
      <property role="20kJfa" value="commissionedUse" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XUAf" resolve="CommissionedUseEnvelope" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUB4" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877572" />
      <property role="20kJfa" value="modelProfiles" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XUAg" resolve="ModelProfile" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUB5" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877573" />
      <property role="20kJfa" value="machineProfiles" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XUAh" resolve="MachineProfile" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUB8">
    <property role="EcuMT" value="1365532761375877576" />
    <property role="TrG5h" value="StateTransition" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUBa" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877578" />
      <property role="TrG5h" value="guard" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="1bNmcZ2XUBb" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877579" />
      <property role="TrG5h" value="invalidationEffect" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUBc" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877580" />
      <property role="20kJfa" value="source" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ2XU_Y" resolve="WorkflowState" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUBd" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877581" />
      <property role="20kJfa" value="target" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ2XU_Y" resolve="WorkflowState" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUBe" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877582" />
      <property role="20kJfa" value="actorRole" />
      <property role="20lbJX" value="fLJekj4/_1" />
      <ref role="20lvS9" node="1bNmcZ2XUAj" resolve="OperationalRole" />
    </node>
  </node>
  <node concept="1TIwiD" id="1bNmcZ2XUB9">
    <property role="EcuMT" value="1365532761375877577" />
    <property role="TrG5h" value="WorkflowDefinition" />
    <property role="19KtqR" value="true" />
    <ref role="1TJDcQ" to="5q6:1bNmcZ2iEsv" resolve="GovernedElement" />
    <node concept="1TJgyi" id="1bNmcZ2XUBf" role="1TKVEl">
      <property role="IQ2nx" value="1365532761375877583" />
      <property role="TrG5h" value="name" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUBg" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877584" />
      <property role="20kJfa" value="states" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XU_Y" resolve="WorkflowState" />
    </node>
    <node concept="1TJgyj" id="1bNmcZ2XUBh" role="1TKVEi">
      <property role="IQ2ns" value="1365532761375877585" />
      <property role="20kJfa" value="transitions" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="1bNmcZ2XUB8" resolve="StateTransition" />
    </node>
  </node>
</model>

