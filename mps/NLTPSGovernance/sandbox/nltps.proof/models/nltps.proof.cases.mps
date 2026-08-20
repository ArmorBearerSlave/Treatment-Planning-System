<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:098128cc-3125-4d66-a424-2542a6566f82(nltps.proof.cases)">
  <persistence version="9" />
  <languages>
    <use id="4709dc1d-8658-45c6-b6ee-185bd2ba1b14" name="nltps.governance" version="0" />
    <use id="87311da3-67f4-4168-a5e2-0a32e6781088" name="nltps.foundation" version="0" />
  </languages>
  <imports />
  <registry>
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
      <concept id="1365532761364539174" name="nltps.foundation.structure.Unit" flags="ng" index="3gIvZD">
        <property id="1365532761364539205" name="doseBasis" index="3gIvYa" />
        <property id="1365532761364539204" name="dimension" index="3gIvYb" />
        <property id="1365532761364539203" name="symbol" index="3gIvYc" />
      </concept>
      <concept id="1365532761364539171" name="nltps.foundation.structure.LifecycleState" flags="ng" index="3gIvZG">
        <property id="1365532761364539196" name="terminal" index="3gIvZN" />
        <property id="1365532761364539195" name="ordinal" index="3gIvZO" />
        <property id="1365532761364539194" name="state" index="3gIvZP" />
      </concept>
      <concept id="1365532761364539170" name="nltps.foundation.structure.Version" flags="ng" index="3gIvZH">
        <property id="1365532761364539191" name="value" index="3gIvZS" />
      </concept>
      <concept id="1365532761364539168" name="nltps.foundation.structure.StableId" flags="ng" index="3gIvZJ">
        <property id="1365532761364539186" name="value" index="3gIvZX" />
      </concept>
    </language>
    <language id="4709dc1d-8658-45c6-b6ee-185bd2ba1b14" name="nltps.governance">
      <concept id="1365532761364587933" name="nltps.governance.structure.VerificationMethodEntry" flags="ng" index="3gI3Pi">
        <property id="1365532761364587939" name="method" index="3gI3PG" />
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
</model>

