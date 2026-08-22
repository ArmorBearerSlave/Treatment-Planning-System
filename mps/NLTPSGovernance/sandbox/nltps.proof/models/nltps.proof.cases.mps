<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:098128cc-3125-4d66-a424-2542a6566f82(nltps.proof.cases)">
  <persistence version="9" />
  <languages>
    <use id="4709dc1d-8658-45c6-b6ee-185bd2ba1b14" name="nltps.governance" version="0" />
    <use id="87311da3-67f4-4168-a5e2-0a32e6781088" name="nltps.foundation" version="0" />
    <use id="dbcbafd2-9884-4f01-8836-da8cbf2c072f" name="nltps.clinicalintent" version="0" />
    <use id="12705dba-f436-4675-8d88-79a0f43738a5" name="nltps.roles.radonc" version="0" />
    <use id="5b19e2ff-ed83-482c-ba24-1b8dca166673" name="nltps.roles.physics" version="0" />
    <use id="32a5fe33-a49d-4203-b3e1-5054d68a5daf" name="nltps.roles.common" version="0" />
    <use id="08070d1a-4999-4bfd-a38c-2b1b3ffd9ef4" name="nltps.realization" version="0" />
  </languages>
  <imports />
  <registry>
    <language id="12705dba-f436-4675-8d88-79a0f43738a5" name="nltps.roles.radonc">
      <concept id="1365532761382949442" name="nltps.roles.radonc.structure.RadoncProjection" flags="ng" index="3h$cEd">
        <reference id="1365532761382949448" name="intendedRole" index="3h$cE7" />
        <child id="1365532761382949447" name="tasks" index="3h$cE8" />
        <child id="1365532761382949446" name="views" index="3h$cE9" />
      </concept>
      <concept id="1365532761382949441" name="nltps.roles.radonc.structure.RadoncTask" flags="ng" index="3h$cEe">
        <property id="1365532761382949445" name="taskKind" index="3h$cEa" />
      </concept>
      <concept id="1365532761382949440" name="nltps.roles.radonc.structure.RadoncView" flags="ng" index="3h$cEf">
        <property id="1365532761382949443" name="viewName" index="3h$cEc" />
        <child id="1365532761382949444" name="subjects" index="3h$cEb" />
      </concept>
    </language>
    <language id="87311da3-67f4-4168-a5e2-0a32e6781088" name="nltps.foundation">
      <concept id="1365532761364539167" name="nltps.foundation.structure.GovernedElement" flags="ng" index="3gIvZg">
        <reference id="1365532761364539184" name="lifecycleState" index="3gIvZZ" />
        <child id="1365532761364539181" name="version" index="3gIvZy" />
        <child id="1365532761364539180" name="identifier" index="3gIvZz" />
      </concept>
      <concept id="1365532761364539179" name="nltps.foundation.structure.LifecycleVocabulary" flags="ng" index="3gIvZ$">
        <property id="1365532761364539218" name="name" index="3gIvYt" />
        <child id="1365532761364539219" name="states" index="3gIvYs" />
      </concept>
      <concept id="1365532761364539178" name="nltps.foundation.structure.UnitCatalog" flags="ng" index="3gIvZ_">
        <property id="1365532761364539216" name="name" index="3gIvYv" />
        <child id="1365532761364539217" name="units" index="3gIvYu" />
      </concept>
      <concept id="1365532761364539176" name="nltps.foundation.structure.ExternalReference" flags="ng" index="3gIvZB">
        <property id="1365532761364539212" name="retrievedDate" index="3gIvY3" />
        <property id="1365532761364539210" name="locator" index="3gIvY5" />
        <property id="1365532761364539209" name="title" index="3gIvY6" />
      </concept>
      <concept id="1365532761364539174" name="nltps.foundation.structure.Unit" flags="ng" index="3gIvZD">
        <property id="1365532761364539205" name="doseBasis" index="3gIvYa" />
        <property id="1365532761364539204" name="dimension" index="3gIvYb" />
        <property id="1365532761364539203" name="symbol" index="3gIvYc" />
      </concept>
      <concept id="1365532761364539173" name="nltps.foundation.structure.PhysicalQuantity" flags="ng" index="3gIvZE">
        <property id="1365532761364539201" name="doseBasis" index="3gIvYe" />
        <property id="1365532761364539200" name="magnitude" index="3gIvYf" />
        <reference id="1365532761364539202" name="unit" index="3gIvYd" />
      </concept>
      <concept id="1365532761364539171" name="nltps.foundation.structure.LifecycleState" flags="ng" index="3gIvZG">
        <property id="1365532761364539196" name="terminal" index="3gIvZN" />
        <property id="1365532761364539195" name="ordinal" index="3gIvZO" />
        <property id="1365532761364539194" name="state" index="3gIvZP" />
      </concept>
      <concept id="1365532761364539170" name="nltps.foundation.structure.Version" flags="ng" index="3gIvZH">
        <property id="1365532761364539193" name="supersededDate" index="3gIvZQ" />
        <property id="1365532761364539192" name="effectiveDate" index="3gIvZR" />
        <property id="1365532761364539191" name="value" index="3gIvZS" />
      </concept>
      <concept id="1365532761364539168" name="nltps.foundation.structure.StableId" flags="ng" index="3gIvZJ">
        <property id="1365532761364539186" name="value" index="3gIvZX" />
      </concept>
    </language>
    <language id="4709dc1d-8658-45c6-b6ee-185bd2ba1b14" name="nltps.governance">
      <concept id="1365532761364587934" name="nltps.governance.structure.EmphasisEntry" flags="ng" index="3gI3Ph">
        <property id="1365532761364587940" name="emphasis" index="3gI3PF" />
      </concept>
      <concept id="1365532761364587933" name="nltps.governance.structure.VerificationMethodEntry" flags="ng" index="3gI3Pi">
        <property id="1365532761364587939" name="method" index="3gI3PG" />
      </concept>
      <concept id="1365532761364587951" name="nltps.governance.structure.RequirementOverride" flags="ng" index="3gI3Pw">
        <property id="1365532761364587983" name="rationale" index="3gI3O0" />
        <property id="1365532761364587985" name="overrideText" index="3gI3Ou" />
        <property id="1365532761364587984" name="approvalState" index="3gI3Ov" />
        <reference id="1365532761364587986" name="target" index="3gI3Ot" />
      </concept>
      <concept id="1365532761364587950" name="nltps.governance.structure.DerivedRequirement" flags="ng" index="3gI3Px">
        <property id="1365532761364587980" name="derivedIndex" index="3gI3O3" />
        <reference id="1365532761364587982" name="pattern" index="3gI3O1" />
        <reference id="1365532761364587981" name="parent" index="3gI3O2" />
      </concept>
      <concept id="1365532761364587949" name="nltps.governance.structure.RequirementPattern" flags="ng" index="3gI3Py">
        <property id="1365532761364587978" name="childCount" index="3gI3O5" />
        <property id="1365532761364587977" name="childSuffixTemplate" index="3gI3O6" />
        <property id="1365532761364587976" name="patternId" index="3gI3O7" />
        <child id="1365532761364587979" name="emphasis" index="3gI3O4" />
      </concept>
      <concept id="1365532761364587948" name="nltps.governance.structure.Requirement" flags="ng" index="3gI3Pz">
        <property id="1365532761364587972" name="category" index="3gI3Ob" />
        <property id="1365532761364587971" name="domain" index="3gI3Oc" />
        <property id="1365532761364587970" name="statement" index="3gI3Od" />
        <child id="1365532761364587973" name="verificationMethods" index="3gI3Oa" />
      </concept>
      <concept id="1365532761364587938" name="nltps.governance.structure.AllowedConceptEntry" flags="ng" index="3gI3PH">
        <property id="1365532761364587944" name="conceptName" index="3gI3PB" />
      </concept>
      <concept id="1365532761364587967" name="nltps.governance.structure.TraceGraph" flags="ng" index="3gI3PK">
        <property id="1365532761364588036" name="name" index="3gI3Vb" />
        <child id="1365532761364588038" name="links" index="3gI3V9" />
        <child id="1365532761364588037" name="relations" index="3gI3Va" />
      </concept>
      <concept id="1365532761364587965" name="nltps.governance.structure.RiskBaseline" flags="ng" index="3gI3PM">
        <property id="1365532761364588028" name="name" index="3gI3ON" />
        <child id="1365532761364588031" name="controls" index="3gI3OK" />
        <child id="1365532761364588029" name="hazards" index="3gI3OM" />
      </concept>
      <concept id="1365532761364587964" name="nltps.governance.structure.RequirementBaseline" flags="ng" index="3gI3PN">
        <property id="1365532761364588023" name="name" index="3gI3OS" />
        <child id="1365532761364588027" name="overrides" index="3gI3OO" />
        <child id="1365532761364588026" name="patterns" index="3gI3OP" />
        <child id="1365532761364588025" name="requirements" index="3gI3OQ" />
      </concept>
      <concept id="1365532761364587960" name="nltps.governance.structure.HazardRef" flags="ng" index="3gI3PR">
        <reference id="1365532761364588019" name="hazard" index="3gI3OW" />
      </concept>
      <concept id="1365532761364587959" name="nltps.governance.structure.TraceLink" flags="ng" index="3gI3PS">
        <property id="1365532761364588015" name="rationale" index="3gI3Ow" />
        <reference id="1365532761364588018" name="target" index="3gI3OX" />
        <reference id="1365532761364588017" name="source" index="3gI3OY" />
        <reference id="1365532761364588016" name="relation" index="3gI3OZ" />
      </concept>
      <concept id="1365532761364587958" name="nltps.governance.structure.TraceRelation" flags="ng" index="3gI3PT">
        <property id="1365532761364588012" name="targetCardinality" index="3gI3Oz" />
        <property id="1365532761364588011" name="sourceCardinality" index="3gI3O$" />
        <property id="1365532761364588010" name="relation" index="3gI3O_" />
        <child id="1365532761364588014" name="allowedTargetConcepts" index="3gI3Ox" />
        <child id="1365532761364588013" name="allowedSourceConcepts" index="3gI3Oy" />
      </concept>
      <concept id="1365532761364587954" name="nltps.governance.structure.RiskControl" flags="ng" index="3gI3PX">
        <property id="1365532761364587995" name="statement" index="3gI3Ok" />
        <property id="1365532761364587994" name="controlType" index="3gI3Ol" />
        <child id="1365532761364587996" name="mitigates" index="3gI3Oj" />
      </concept>
      <concept id="1365532761364587952" name="nltps.governance.structure.Hazard" flags="ng" index="3gI3PZ">
        <property id="1365532761364587990" name="harm" index="3gI3Op" />
        <property id="1365532761364587989" name="description" index="3gI3Oq" />
        <property id="1365532761364587988" name="hazardId" index="3gI3Or" />
      </concept>
    </language>
    <language id="5b19e2ff-ed83-482c-ba24-1b8dca166673" name="nltps.roles.physics">
      <concept id="1365532761382949453" name="nltps.roles.physics.structure.PhysicsProjection" flags="ng" index="3h$cE2">
        <reference id="1365532761382949459" name="intendedRole" index="3h$cEs" />
        <child id="1365532761382949458" name="tasks" index="3h$cEt" />
        <child id="1365532761382949457" name="views" index="3h$cEu" />
      </concept>
      <concept id="1365532761382949452" name="nltps.roles.physics.structure.PhysicsTask" flags="ng" index="3h$cE3">
        <property id="1365532761382949456" name="taskKind" index="3h$cEv" />
      </concept>
      <concept id="1365532761382949451" name="nltps.roles.physics.structure.PhysicsView" flags="ng" index="3h$cE4">
        <property id="1365532761382949454" name="viewName" index="3h$cE1" />
        <child id="1365532761382949455" name="subjects" index="3h$cE0" />
      </concept>
    </language>
    <language id="08070d1a-4999-4bfd-a38c-2b1b3ffd9ef4" name="nltps.realization">
      <concept id="1365532761387707800" name="nltps.realization.structure.VerificationBaseline" flags="ng" index="3hnRln">
        <property id="1365532761387707809" name="name" index="3hnRlI" />
        <child id="1365532761387707810" name="claims" index="3hnRlH" />
      </concept>
      <concept id="1365532761387707798" name="nltps.realization.structure.ArchitectureRealization" flags="ng" index="3hnRlp">
        <property id="1365532761387707802" name="name" index="3hnRll" />
        <child id="1365532761387707804" name="teams" index="3hnRlj" />
      </concept>
      <concept id="1365532761387707747" name="nltps.realization.structure.VerificationClaim" flags="ng" index="3hnRmG">
        <property id="1365532761387707755" name="verdict" index="3hnRm$" />
        <property id="1365532761387707754" name="claimName" index="3hnRm_" />
        <reference id="1365532761387707761" name="owningTeam" index="3hnRmY" />
        <reference id="1365532761387707760" name="verifies" index="3hnRmZ" />
      </concept>
      <concept id="1365532761387707706" name="nltps.realization.structure.Team" flags="ng" index="3hnRnP">
        <property id="1365532761387707715" name="accountableRole" index="3hnRmc" />
        <property id="1365532761387707714" name="teamName" index="3hnRmd" />
      </concept>
    </language>
    <language id="32a5fe33-a49d-4203-b3e1-5054d68a5daf" name="nltps.roles.common">
      <concept id="1365532761375877592" name="nltps.roles.common.structure.OperationalRoleRef" flags="ng" index="3g1f4n">
        <reference id="1365532761375877597" name="role" index="3g1f4i" />
      </concept>
      <concept id="1365532761375877591" name="nltps.roles.common.structure.WorkflowStateRef" flags="ng" index="3g1f4o">
        <reference id="1365532761375877596" name="state" index="3g1f4j" />
      </concept>
      <concept id="1365532761375877590" name="nltps.roles.common.structure.ActionRef" flags="ng" index="3g1f4p">
        <reference id="1365532761375877595" name="action" index="3g1f4k" />
      </concept>
      <concept id="1365532761375877589" name="nltps.roles.common.structure.SemanticTargetRef" flags="ng" index="3g1f4q">
        <reference id="1365532761375877594" name="target" index="3g1f4l" />
      </concept>
      <concept id="1365532761375877588" name="nltps.roles.common.structure.RoleProjection" flags="ng" index="3g1f4r">
        <property id="1365532761375877593" name="projectionName" index="3g1f4m" />
      </concept>
      <concept id="1365532761375877600" name="nltps.roles.common.structure.RoleCommand" flags="ng" index="3g1f4J">
        <property id="1365532761375877601" name="commandName" index="3g1f4I" />
        <child id="1365532761375877605" name="roles" index="3g1f4E" />
        <child id="1365532761375877604" name="states" index="3g1f4F" />
        <child id="1365532761375877603" name="actions" index="3g1f4G" />
        <child id="1365532761375877602" name="targets" index="3g1f4H" />
      </concept>
    </language>
    <language id="dbcbafd2-9884-4f01-8836-da8cbf2c072f" name="nltps.clinicalintent">
      <concept id="1365532761375877577" name="nltps.clinicalintent.structure.WorkflowDefinition" flags="ng" index="3g1f46">
        <property id="1365532761375877583" name="name" index="3g1f40" />
        <child id="1365532761375877585" name="transitions" index="3g1f4u" />
        <child id="1365532761375877584" name="states" index="3g1f4v" />
      </concept>
      <concept id="1365532761375877576" name="nltps.clinicalintent.structure.StateTransition" flags="ng" index="3g1f47">
        <property id="1365532761375877579" name="invalidationEffect" index="3g1f44" />
        <property id="1365532761375877578" name="guard" index="3g1f45" />
        <reference id="1365532761375877582" name="actorRole" index="3g1f41" />
        <reference id="1365532761375877581" name="target" index="3g1f42" />
        <reference id="1365532761375877580" name="source" index="3g1f43" />
      </concept>
      <concept id="1365532761375877519" name="nltps.clinicalintent.structure.CommissionedUseEnvelope" flags="ng" index="3g1f50">
        <property id="1365532761375877526" name="commissionedOn" index="3g1f5p" />
        <property id="1365532761375877525" name="scopeDescription" index="3g1f5q" />
        <property id="1365532761375877524" name="envelopeName" index="3g1f5r" />
      </concept>
      <concept id="1365532761375877523" name="nltps.clinicalintent.structure.OperationalRole" flags="ng" index="3g1f5s">
        <property id="1365532761375877535" name="description" index="3g1f5g" />
        <property id="1365532761375877534" name="functionName" index="3g1f5h" />
      </concept>
      <concept id="1365532761375877522" name="nltps.clinicalintent.structure.ProfessionalRole" flags="ng" index="3g1f5t">
        <property id="1365532761375877533" name="credentialBasis" index="3g1f5i" />
        <property id="1365532761375877532" name="title" index="3g1f5j" />
      </concept>
      <concept id="1365532761375877542" name="nltps.clinicalintent.structure.ReleaseProfile" flags="ng" index="3g1f5D">
        <property id="1365532761375877569" name="releaseState" index="3g1f4e" />
        <property id="1365532761375877568" name="intendedUse" index="3g1f4f" />
        <property id="1365532761375877567" name="name" index="3g1f5K" />
        <child id="1365532761375877571" name="commissionedUse" index="3g1f4c" />
        <child id="1365532761375877570" name="evidenceProfiles" index="3g1f4d" />
      </concept>
      <concept id="1365532761375877541" name="nltps.clinicalintent.structure.AuthorityPolicy" flags="ng" index="3g1f5E">
        <property id="1365532761375877562" name="institution" index="3g1f5P" />
        <property id="1365532761375877561" name="name" index="3g1f5Q" />
        <child id="1365532761375877566" name="actors" index="3g1f5L" />
        <child id="1365532761375877565" name="capabilities" index="3g1f5M" />
        <child id="1365532761375877564" name="operationalRoles" index="3g1f5N" />
        <child id="1365532761375877563" name="professionalRoles" index="3g1f5O" />
      </concept>
      <concept id="1365532761375877540" name="nltps.clinicalintent.structure.PlanIntentDefinition" flags="ng" index="3g1f5F">
        <property id="1365532761375877554" name="aiCreatable" index="3g1f5X" />
        <property id="1365532761375877553" name="name" index="3g1f5Y" />
        <child id="1365532761375877557" name="constraints" index="3g1f5U" />
        <child id="1365532761375877556" name="actions" index="3g1f5V" />
        <child id="1365532761375877555" name="objectTypes" index="3g1f5W" />
      </concept>
      <concept id="1365532761375877539" name="nltps.clinicalintent.structure.AuthorizedActor" flags="ng" index="3g1f5G">
        <property id="1365532761375877550" name="actorKind" index="3g1f5x" />
        <property id="1365532761375877549" name="principalId" index="3g1f5y" />
        <reference id="1365532761375877551" name="professionalRole" index="3g1f5w" />
        <reference id="1365532761375877552" name="operationalRole" index="3g1f5Z" />
      </concept>
      <concept id="1365532761375877538" name="nltps.clinicalintent.structure.RoleCapability" flags="ng" index="3g1f5H">
        <property id="1365532761375877543" name="requiresApproval" index="3g1f5C" />
        <reference id="1365532761375877547" name="targetScope" index="3g1f5$" />
        <reference id="1365532761375877546" name="allowedAction" index="3g1f5_" />
        <reference id="1365532761375877545" name="operationalRole" index="3g1f5A" />
        <reference id="1365532761375877544" name="professionalRole" index="3g1f5B" />
      </concept>
      <concept id="1365532761375877485" name="nltps.clinicalintent.structure.ConstraintDefinition" flags="ng" index="3g1f6y">
        <property id="1365532761375877491" name="comparison" index="3g1f6W" />
        <property id="1365532761375877490" name="constraintName" index="3g1f6X" />
        <child id="1365532761375877493" name="limit" index="3g1f6U" />
      </concept>
      <concept id="1365532761375877484" name="nltps.clinicalintent.structure.ActionDefinition" flags="ng" index="3g1f6z">
        <property id="1365532761375877487" name="autonomyLevel" index="3g1f6w" />
        <property id="1365532761375877486" name="actionName" index="3g1f6x" />
      </concept>
      <concept id="1365532761375877479" name="nltps.clinicalintent.structure.ClinicalObjectType" flags="ng" index="3g1f6C">
        <property id="1365532761375877480" name="typeName" index="3g1f6B" />
      </concept>
      <concept id="1365532761375877503" name="nltps.clinicalintent.structure.EvidenceProfile" flags="ng" index="3g1f6K">
        <property id="1365532761375877515" name="requiredTier" index="3g1f54" />
        <property id="1365532761375877514" name="profileName" index="3g1f55" />
        <child id="1365532761375877516" name="citations" index="3g1f53" />
      </concept>
      <concept id="1365532761375877502" name="nltps.clinicalintent.structure.WorkflowState" flags="ng" index="3g1f6L">
        <property id="1365532761375877513" name="terminal" index="3g1f56" />
        <property id="1365532761375877512" name="stateName" index="3g1f57" />
      </concept>
    </language>
  </registry>
  <node concept="3gIvZ$" id="1bNmcZ2uzo$">
    <property role="3gIvYt" value="ProofLifecycle" />
    <node concept="3gIvZG" id="1bNmcZ2uzo_" role="3gIvYs">
      <property role="3gIvZP" value="43RwCQfM2z7/draft" />
      <property role="3gIvZO" value="1" />
      <property role="3gIvZN" value="false" />
    </node>
    <node concept="3gIvZG" id="1bNmcZ2uzoA" role="3gIvYs">
      <property role="3gIvZP" value="_BeVwBhoGy/approved" />
      <property role="3gIvZO" value="4" />
      <property role="3gIvZN" value="false" />
    </node>
  </node>
  <node concept="3gIvZ_" id="1bNmcZ2uzoB">
    <property role="3gIvYv" value="ProofUnits" />
    <node concept="3gIvZD" id="1bNmcZ2uzoC" role="3gIvYu">
      <property role="3gIvYc" value="Gy" />
      <property role="3gIvYb" value="L7uVmcaIVj/dose" />
      <property role="3gIvYa" value="5zNd3rcPUCV/physical_absorbed" />
    </node>
    <node concept="3gIvZD" id="1bNmcZ2uzoD" role="3gIvYu">
      <property role="3gIvYc" value="Gy(RBE)" />
      <property role="3gIvYb" value="L7uVmcaIVj/dose" />
      <property role="3gIvYa" value="77hZtkElJy6/rbe_weighted" />
    </node>
    <node concept="3gIvZD" id="1bNmcZ2uzoE" role="3gIvYu">
      <property role="3gIvYc" value="mm" />
      <property role="3gIvYb" value="1sM2JSh7CAX/length" />
      <property role="3gIvYa" value="4gser9mknP_/not_applicable" />
    </node>
  </node>
  <node concept="3gI3PN" id="1bNmcZ2uzoF">
    <property role="3gI3OS" value="ProofRequirements" />
    <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
    <node concept="3gIvZJ" id="1bNmcZ2uzoI" role="3gIvZz">
      <property role="3gIvZX" value="BASE-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ2uzoJ" role="3gIvZy">
      <property role="3gIvZS" value="1.0" />
      <property role="3gIvZR" value="2024-02-29" />
    </node>
    <node concept="3gI3Pz" id="1bNmcZ2uzoK" role="3gI3OQ">
      <property role="3gI3Od" value="The system shall record an approval decision." />
      <property role="3gI3Oc" value="7Ri7H_AEJ6z/GOV" />
      <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ2uzoO" role="3gIvZz">
        <property role="3gIvZX" value="GOV-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ2uzoP" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
      <node concept="3gI3Pi" id="1bNmcZ2uzoQ" role="3gI3Oa">
        <property role="3gI3PG" value="1yA6SzRMnoc/I" />
      </node>
    </node>
    <node concept="3gI3Py" id="1bNmcZ2Kg1M" role="3gI3OP">
      <property role="3gI3O7" value="PAT-GOV-01" />
      <property role="3gI3O6" value="-{index}" />
      <property role="3gI3O5" value="3" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ2Kg1Q" role="3gIvZz">
        <property role="3gIvZX" value="PAT-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ2Kg1R" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
      <node concept="3gI3Ph" id="1bNmcZ2Kg1S" role="3gI3O4">
        <property role="3gI3PF" value="completeness" />
      </node>
    </node>
    <node concept="3gI3Px" id="1bNmcZ2Kg1T" role="3gI3OQ">
      <property role="3gI3Od" value="The system shall record the derived obligation." />
      <property role="3gI3Oc" value="7Ri7H_AEJ6z/GOV" />
      <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
      <property role="3gI3O3" value="1" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <ref role="3gI3O2" node="1bNmcZ2uzoK" />
      <ref role="3gI3O1" node="1bNmcZ2Kg1M" />
      <node concept="3gIvZJ" id="1bNmcZ2Kg1X" role="3gIvZz">
        <property role="3gIvZX" value="GOV-001-1" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ2Kg1Y" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
      <node concept="3gI3Pi" id="1bNmcZ2Kg1Z" role="3gI3Oa">
        <property role="3gI3PG" value="1yA6SzRMnoc/I" />
      </node>
    </node>
    <node concept="3gI3Pw" id="1bNmcZ2Kg20" role="3gI3OO">
      <property role="3gI3O0" value="The derived wording omits the monthly QA interval required by the operating programme." />
      <property role="3gI3Ov" value="5PrMha4qV75/pending_named_approval" />
      <property role="3gI3Ou" value="The system shall record the bespoke obligation." />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <ref role="3gI3Ot" node="1bNmcZ2Kg1T" />
      <node concept="3gIvZJ" id="1bNmcZ2Kg23" role="3gIvZz">
        <property role="3gIvZX" value="OVR-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ2Kg24" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
  </node>
  <node concept="3gI3PM" id="1bNmcZ2uzoX">
    <property role="3gI3ON" value="ProofRisk" />
    <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
    <node concept="3gIvZJ" id="1bNmcZ2uzp0" role="3gIvZz">
      <property role="3gIvZX" value="RISK-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ2uzp1" role="3gIvZy">
      <property role="3gIvZS" value="1.0" />
    </node>
    <node concept="3gI3PZ" id="1bNmcZ2uzp2" role="3gI3OM">
      <property role="3gI3Or" value="H-01" />
      <property role="3gI3Oq" value="Incorrect dose basis applied to a plan." />
      <property role="3gI3Op" value="Overdose or underdose to the patient." />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ2uzp5" role="3gIvZz">
        <property role="3gIvZX" value="HAZ-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ2uzp6" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
    <node concept="3gI3PX" id="1bNmcZ2uzp7" role="3gI3OK">
      <property role="3gI3Ol" value="KTCEeZFWZg/protective_measure" />
      <property role="3gI3Ok" value="The planning system shall display the dose basis on every dose constraint." />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ2uzpb" role="3gIvZz">
        <property role="3gIvZX" value="CTL-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ2uzpc" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
      <node concept="3gI3PR" id="1bNmcZ2uzpd" role="3gI3Oj">
        <ref role="3gI3OW" node="1bNmcZ2uzp2" />
      </node>
    </node>
  </node>
  <node concept="3gI3PK" id="1bNmcZ2wLsL">
    <property role="3gI3Vb" value="ProofTrace" />
    <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
    <node concept="3gIvZJ" id="1bNmcZ2wLsO" role="3gIvZz">
      <property role="3gIvZX" value="TRACE-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ2wLsP" role="3gIvZy">
      <property role="3gIvZS" value="1.0" />
    </node>
    <node concept="3gI3PT" id="1bNmcZ2wLsQ" role="3gI3Va">
      <property role="3gI3O_" value="1zIccLPMcY7/MITIGATES" />
      <property role="3gI3O$" value="1..n" />
      <property role="3gI3Oz" value="1..n" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ2wLsV" role="3gIvZz">
        <property role="3gIvZX" value="REL-MITIGATES" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ2wLsW" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
        <property role="3gIvZR" value="2026-08-20" />
      </node>
      <node concept="3gI3PH" id="1bNmcZ2wLsX" role="3gI3Oy">
        <property role="3gI3PB" value="RiskControl" />
      </node>
      <node concept="3gI3PH" id="1bNmcZ2wLsY" role="3gI3Ox">
        <property role="3gI3PB" value="Hazard" />
      </node>
    </node>
    <node concept="3gI3PS" id="1bNmcZ2wLsZ" role="3gI3V9">
      <property role="3gI3Ow" value="GOV-C-003 positive case: RiskControl MITIGATES Hazard is permitted." />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <ref role="3gI3OZ" node="1bNmcZ2wLsQ" />
      <ref role="3gI3OY" node="1bNmcZ2uzp7" />
      <ref role="3gI3OX" node="1bNmcZ2uzp2" />
      <node concept="3gIvZJ" id="1bNmcZ2wLt2" role="3gIvZz">
        <property role="3gIvZX" value="LNK-VALID" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ2wLt3" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
  </node>
  <node concept="3gI3PN" id="1bNmcZ2VTQo">
    <property role="3gI3OS" value="DateFacetProof" />
    <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
    <node concept="3gIvZJ" id="1bNmcZ2VTQr" role="3gIvZz">
      <property role="3gIvZX" value="BASE-DATE-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ2VTQs" role="3gIvZy">
      <property role="3gIvZS" value="1.0" />
      <property role="3gIvZR" value="2024-02-29" />
      <property role="3gIvZQ" value="2025-12-31" />
    </node>
  </node>
  <node concept="3g1f5F" id="1bNmcZ3ewyT">
    <property role="3g1f5Y" value="PlanIntentProof" />
    <property role="3g1f5X" value="false" />
    <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
    <node concept="3gIvZJ" id="1bNmcZ3ewyW" role="3gIvZz">
      <property role="3gIvZX" value="PID-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3ewyX" role="3gIvZy">
      <property role="3gIvZS" value="1.0" />
    </node>
    <node concept="3g1f6C" id="1bNmcZ3ewyY" role="3g1f5W">
      <property role="3g1f6B" value="PrescriptionIntent" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3ewz1" role="3gIvZz">
        <property role="3gIvZX" value="COT-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3ewz2" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
    <node concept="3g1f6C" id="1bNmcZ3ewz3" role="3g1f5W">
      <property role="3g1f6B" value="CandidatePlan" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3ewz6" role="3gIvZz">
        <property role="3gIvZX" value="COT-002" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3ewz7" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
    <node concept="3g1f6z" id="1bNmcZ3ewz8" role="3g1f5V">
      <property role="3g1f6x" value="authorizeRelease" />
      <property role="3g1f6w" value="OQMDNNNEg4/A4_authorize_or_deliver" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3ewzb" role="3gIvZz">
        <property role="3gIvZX" value="ACT-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3ewzc" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
    <node concept="3g1f6z" id="1bNmcZ3ewzd" role="3g1f5V">
      <property role="3g1f6x" value="draftPlan" />
      <property role="3g1f6w" value="7iWT5AvLSad/A1_draft" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3ewzg" role="3gIvZz">
        <property role="3gIvZX" value="ACT-002" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3ewzh" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
    <node concept="3g1f6y" id="1bNmcZ3ewzi" role="3g1f5U">
      <property role="3g1f6X" value="maxCordDose" />
      <property role="3g1f6W" value="3iyRqiiTyS4/le" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3ewzm" role="3gIvZz">
        <property role="3gIvZX" value="CON-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3ewzn" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
      <node concept="3gIvZE" id="1bNmcZ3ewzo" role="3g1f6U">
        <property role="3gIvYf" value="60.0" />
        <property role="3gIvYe" value="5zNd3rcPUCV/physical_absorbed" />
        <ref role="3gIvYd" node="1bNmcZ2uzoC" />
      </node>
    </node>
  </node>
  <node concept="3g1f5F" id="1bNmcZ3ewzX">
    <property role="3g1f5Y" value="NonAiCreatableIntentProof" />
    <property role="3g1f5X" value="false" />
    <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
    <node concept="3gIvZJ" id="1bNmcZ3ew$0" role="3gIvZz">
      <property role="3gIvZX" value="PID-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3ew$1" role="3gIvZy">
      <property role="3gIvZS" value="1.0" />
    </node>
    <node concept="3g1f6z" id="1bNmcZ3ew$2" role="3g1f5V">
      <property role="3g1f6x" value="authorizeDelivery" />
      <property role="3g1f6w" value="OQMDNNNEg4/A4_authorize_or_deliver" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3ew$5" role="3gIvZz">
        <property role="3gIvZX" value="ACT-003" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3ew$6" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
  </node>
  <node concept="3g1f46" id="1bNmcZ3ew$O">
    <property role="3g1f40" value="WorkflowProof" />
    <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
    <node concept="3gIvZJ" id="1bNmcZ3ew$R" role="3gIvZz">
      <property role="3gIvZX" value="WFD-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3ew$S" role="3gIvZy">
      <property role="3gIvZS" value="1.0" />
    </node>
    <node concept="3g1f6L" id="1bNmcZ3ew$T" role="3g1f4v">
      <property role="3g1f57" value="drafted" />
      <property role="3g1f56" value="false" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3ew$W" role="3gIvZz">
        <property role="3gIvZX" value="WFS-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3ew$X" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
    <node concept="3g1f6L" id="1bNmcZ3ew$Y" role="3g1f4v">
      <property role="3g1f57" value="approved" />
      <property role="3g1f56" value="true" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3ew_1" role="3gIvZz">
        <property role="3gIvZX" value="WFS-002" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3ew_2" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
    <node concept="3g1f47" id="1bNmcZ3ew_3" role="3g1f4u">
      <property role="3g1f45" value="the prescription intent carries an approved dose constraint set" />
      <property role="3g1f44" value="any later edit to the constraint set returns the object to drafted" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <ref role="3g1f43" node="1bNmcZ3ew$T" />
      <ref role="3g1f42" node="1bNmcZ3ew$Y" />
      <ref role="3g1f41" node="1bNmcZ3gpZB" />
      <node concept="3gIvZJ" id="1bNmcZ3ew_6" role="3gIvZz">
        <property role="3gIvZX" value="TRN-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3ew_7" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
  </node>
  <node concept="3g1f5E" id="1bNmcZ3gpZt">
    <property role="3g1f5Q" value="AuthorityProof" />
    <property role="3g1f5P" value="Stage A governance mirror" />
    <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
    <node concept="3gIvZJ" id="1bNmcZ3gpZw" role="3gIvZz">
      <property role="3gIvZX" value="POL-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3gpZx" role="3gIvZy">
      <property role="3gIvZS" value="1.0" />
    </node>
    <node concept="3g1f5t" id="1bNmcZ3gpZy" role="3g1f5O">
      <property role="3g1f5j" value="Radiation Oncologist" />
      <property role="3g1f5i" value="board certification" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3gpZ_" role="3gIvZz">
        <property role="3gIvZX" value="PRO-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3gpZA" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
    <node concept="3g1f5s" id="1bNmcZ3gpZB" role="3g1f5N">
      <property role="3g1f5h" value="approveTreatmentPlan" />
      <property role="3g1f5g" value="authorizes release of a prescription intent" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3gpZE" role="3gIvZz">
        <property role="3gIvZX" value="OPR-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3gpZF" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
    <node concept="3g1f5H" id="1bNmcZ3gpZG" role="3g1f5M">
      <property role="3g1f5C" value="true" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <ref role="3g1f5B" node="1bNmcZ3gpZy" />
      <ref role="3g1f5A" node="1bNmcZ3gpZB" />
      <ref role="3g1f5_" node="1bNmcZ3ewz8" />
      <ref role="3g1f5$" node="1bNmcZ3ewyY" />
      <node concept="3gIvZJ" id="1bNmcZ3gpZJ" role="3gIvZz">
        <property role="3gIvZX" value="CAP-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3gpZK" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
    <node concept="3g1f5G" id="1bNmcZ3gpZL" role="3g1f5L">
      <property role="3g1f5y" value="radiation.oncologist.on.record" />
      <property role="3g1f5x" value="183owDga$eg/HUMAN" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <ref role="3g1f5w" node="1bNmcZ3gpZy" />
      <ref role="3g1f5Z" node="1bNmcZ3gpZB" />
      <node concept="3gIvZJ" id="1bNmcZ3gpZO" role="3gIvZz">
        <property role="3gIvZX" value="ACR-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3gpZP" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
    <node concept="3g1f5t" id="1bNmcZ3xMSR" role="3g1f5O">
      <property role="3g1f5j" value="Medical Physicist" />
      <property role="3g1f5i" value="board certification in medical physics" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3xMSU" role="3gIvZz">
        <property role="3gIvZX" value="PRO-002" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3xMSV" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
  </node>
  <node concept="3g1f5D" id="1bNmcZ3gpZZ">
    <property role="3g1f5K" value="ReleaseProof" />
    <property role="3g1f4f" value="Stage A governance mirror" />
    <property role="3g1f4e" value="draft" />
    <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
    <node concept="3gIvZJ" id="1bNmcZ3gq02" role="3gIvZz">
      <property role="3gIvZX" value="REL-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3gq03" role="3gIvZy">
      <property role="3gIvZS" value="1.0" />
    </node>
    <node concept="3g1f6K" id="1bNmcZ3gq04" role="3g1f4d">
      <property role="3g1f55" value="primaryEvidence" />
      <property role="3g1f54" value="2Up8EKRKlMr/institutional_standard" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3gq07" role="3gIvZz">
        <property role="3gIvZX" value="EVP-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3gq08" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
      <node concept="3gIvZB" id="1bNmcZ3gq09" role="3g1f53">
        <property role="3gIvY6" value="AAPM TG-263" />
        <property role="3gIvY5" value="https://www.aapm.org/pubs/reports/RPT_263.pdf" />
        <property role="3gIvY3" value="2024-02-29" />
      </node>
    </node>
    <node concept="3g1f50" id="1bNmcZ3gq0_" role="3g1f4c">
      <property role="3g1f5r" value="stageAMirror" />
      <property role="3g1f5q" value="structural representation only; no clinical use" />
      <property role="3g1f5p" value="2026-08-20" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3gq0C" role="3gIvZz">
        <property role="3gIvZX" value="CUE-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3gq0D" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
  </node>
  <node concept="3h$cEd" id="1bNmcZ3xMT5">
    <property role="3g1f4m" value="RadoncClinicalReview" />
    <ref role="3h$cE7" node="1bNmcZ3gpZy" />
    <node concept="3h$cEf" id="1bNmcZ3xMT6" role="3h$cE9">
      <property role="3h$cEc" value="candidatePlanClinicalReview" />
      <node concept="3g1f4q" id="1bNmcZ3xMT7" role="3h$cEb">
        <ref role="3g1f4l" node="1bNmcZ3ewz3" />
      </node>
    </node>
    <node concept="3h$cEe" id="1bNmcZ3xMT8" role="3h$cE8">
      <property role="3g1f4I" value="approveCandidatePlan" />
      <property role="3h$cEa" value="70q02MNHk8Y/clinical_approval" />
      <node concept="3g1f4q" id="1bNmcZ3xMT9" role="3g1f4H">
        <ref role="3g1f4l" node="1bNmcZ3ewz3" />
      </node>
      <node concept="3g1f4p" id="1bNmcZ3xMTa" role="3g1f4G">
        <ref role="3g1f4k" node="1bNmcZ3ewz8" />
      </node>
      <node concept="3g1f4o" id="1bNmcZ3xMTb" role="3g1f4F">
        <ref role="3g1f4j" node="1bNmcZ3ew$Y" />
      </node>
      <node concept="3g1f4n" id="1bNmcZ3xMTc" role="3g1f4E">
        <ref role="3g1f4i" node="1bNmcZ3gpZB" />
      </node>
    </node>
  </node>
  <node concept="3h$cE2" id="1bNmcZ3xMTv">
    <property role="3g1f4m" value="PhysicsTechnicalReview" />
    <ref role="3h$cEs" node="1bNmcZ3xMSR" />
    <node concept="3h$cE4" id="1bNmcZ3xMTw" role="3h$cEu">
      <property role="3h$cE1" value="candidatePlanTechnicalReview" />
      <node concept="3g1f4q" id="1bNmcZ3xMTx" role="3h$cE0">
        <ref role="3g1f4l" node="1bNmcZ3ewz3" />
      </node>
    </node>
    <node concept="3h$cE3" id="1bNmcZ3xMTy" role="3h$cEt">
      <property role="3g1f4I" value="reviewCandidatePlanTechnically" />
      <property role="3h$cEv" value="6p5vN_eLW6s/technical_plan_review" />
      <node concept="3g1f4q" id="1bNmcZ3xMTz" role="3g1f4H">
        <ref role="3g1f4l" node="1bNmcZ3ewz3" />
      </node>
      <node concept="3g1f4p" id="1bNmcZ3xMT$" role="3g1f4G">
        <ref role="3g1f4k" node="1bNmcZ3ewzd" />
      </node>
    </node>
  </node>
  <node concept="3hnRlp" id="1bNmcZ3JGzj">
    <property role="3hnRll" value="RealizationProof" />
    <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
    <node concept="3gIvZJ" id="1bNmcZ3JGzm" role="3gIvZz">
      <property role="3gIvZX" value="ARC-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGzn" role="3gIvZy">
      <property role="3gIvZS" value="1.0" />
    </node>
    <node concept="3hnRnP" id="1bNmcZ3JGzo" role="3hnRlj">
      <property role="3hnRmd" value="Verification and Validation" />
      <property role="3hnRmc" value="Qualified Medical Physicist" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <node concept="3gIvZJ" id="1bNmcZ3JGzr" role="3gIvZz">
        <property role="3gIvZX" value="TEAM-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JGzs" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
  </node>
  <node concept="3hnRln" id="1bNmcZ3JGzA">
    <property role="3hnRlI" value="VerificationProof" />
    <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
    <node concept="3gIvZJ" id="1bNmcZ3JGzD" role="3gIvZz">
      <property role="3gIvZX" value="VBL-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGzE" role="3gIvZy">
      <property role="3gIvZS" value="1.0" />
    </node>
    <node concept="3hnRmG" id="1bNmcZ3JGzF" role="3hnRlH">
      <property role="3hnRm_" value="approvalDecisionRecorded" />
      <property role="3hnRm$" value="1RV1HIhZ_9S/not_assessed" />
      <ref role="3gIvZZ" node="1bNmcZ2uzo_" />
      <ref role="3hnRmZ" node="1bNmcZ2uzoK" />
      <ref role="3hnRmY" node="1bNmcZ3JGzo" />
      <node concept="3gIvZJ" id="1bNmcZ3JGzI" role="3gIvZz">
        <property role="3gIvZX" value="VCL-001" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JGzJ" role="3gIvZy">
        <property role="3gIvZS" value="1.0" />
      </node>
    </node>
  </node>
  <node concept="3gIvZ$" id="1bNmcZ3JG$g">
    <property role="3gIvYt" value="StageAMirrorLifecycle" />
    <node concept="3gIvZG" id="1bNmcZ3JG$h" role="3gIvYs">
      <property role="3gIvZP" value="3szh2WtgW$O/proposed" />
      <property role="3gIvZO" value="1" />
      <property role="3gIvZN" value="false" />
    </node>
  </node>
</model>

