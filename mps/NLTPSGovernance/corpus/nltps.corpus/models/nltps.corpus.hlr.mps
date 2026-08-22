<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:42669edd-f887-4e0e-a7a4-d7a2958f0e96(nltps.corpus.hlr)">
  <persistence version="9" />
  <languages>
    <use id="08070d1a-4999-4bfd-a38c-2b1b3ffd9ef4" name="nltps.realization" version="0" />
    <use id="4709dc1d-8658-45c6-b6ee-185bd2ba1b14" name="nltps.governance" version="0" />
    <use id="87311da3-67f4-4168-a5e2-0a32e6781088" name="nltps.foundation" version="0" />
  </languages>
  <imports />
  <registry>
    <language id="87311da3-67f4-4168-a5e2-0a32e6781088" name="nltps.foundation">
      <concept id="1365532761364539167" name="nltps.foundation.structure.GovernedElement" flags="ng" index="3gIvZg">
        <reference id="1365532761364539184" name="lifecycleState" index="3gIvZZ" />
        <child id="1365532761364539183" name="provenance" index="3gIvZw" />
        <child id="1365532761364539182" name="aliases" index="3gIvZx" />
        <child id="1365532761364539181" name="version" index="3gIvZy" />
        <child id="1365532761364539180" name="identifier" index="3gIvZz" />
      </concept>
      <concept id="1365532761364539179" name="nltps.foundation.structure.LifecycleVocabulary" flags="ng" index="3gIvZ$">
        <property id="1365532761364539218" name="name" index="3gIvYt" />
        <child id="1365532761364539219" name="states" index="3gIvYs" />
      </concept>
      <concept id="1365532761364539175" name="nltps.foundation.structure.ProvenanceRef" flags="ng" index="3gIvZC">
        <property id="1365532761364539208" name="sha256" index="3gIvY7" />
        <property id="1365532761364539207" name="sourceLine" index="3gIvY8" />
        <property id="1365532761364539206" name="sourcePath" index="3gIvY9" />
      </concept>
      <concept id="1365532761364539171" name="nltps.foundation.structure.LifecycleState" flags="ng" index="3gIvZG">
        <property id="1365532761364539196" name="terminal" index="3gIvZN" />
        <property id="1365532761364539195" name="ordinal" index="3gIvZO" />
        <property id="1365532761364539194" name="state" index="3gIvZP" />
      </concept>
      <concept id="1365532761364539170" name="nltps.foundation.structure.Version" flags="ng" index="3gIvZH">
        <property id="1365532761364539191" name="value" index="3gIvZS" />
      </concept>
      <concept id="1365532761364539169" name="nltps.foundation.structure.Alias" flags="ng" index="3gIvZI">
        <property id="1365532761364539245" name="retired" index="3gIvYy" />
        <property id="1365532761364539189" name="scheme" index="3gIvZU" />
        <property id="1365532761364539188" name="value" index="3gIvZV" />
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
        <child id="1365532761364587974" name="hazards" index="3gI3O9" />
        <child id="1365532761364587973" name="verificationMethods" index="3gI3Oa" />
      </concept>
      <concept id="1365532761364587965" name="nltps.governance.structure.RiskBaseline" flags="ng" index="3gI3PM">
        <property id="1365532761364588028" name="name" index="3gI3ON" />
        <child id="1365532761364588029" name="hazards" index="3gI3OM" />
      </concept>
      <concept id="1365532761364587960" name="nltps.governance.structure.HazardRef" flags="ng" index="3gI3PR">
        <reference id="1365532761364588019" name="hazard" index="3gI3OW" />
      </concept>
      <concept id="1365532761364587952" name="nltps.governance.structure.Hazard" flags="ng" index="3gI3PZ">
        <property id="1365532761364587990" name="harm" index="3gI3Op" />
        <property id="1365532761364587989" name="description" index="3gI3Oq" />
        <property id="1365532761364587988" name="hazardId" index="3gI3Or" />
      </concept>
    </language>
    <language id="08070d1a-4999-4bfd-a38c-2b1b3ffd9ef4" name="nltps.realization">
      <concept id="1365532761387707713" name="nltps.realization.structure.ImportedHLR" flags="ng" index="3hnRme">
        <property id="1365532761388928862" name="sourceHazardText" index="3hjpuh" />
        <property id="1365532761387707733" name="authoritative" index="3hnRmq" />
        <property id="1365532761387707732" name="bundleId" index="3hnRmr" />
      </concept>
    </language>
  </registry>
  <node concept="3gIvZ$" id="1bNmcZ3JG$Q">
    <property role="3gIvYt" value="StageAMirrorLifecycle" />
    <node concept="3gIvZG" id="1bNmcZ3JG$R" role="3gIvYs">
      <property role="3gIvZP" value="3szh2WtgW$O/proposed" />
      <property role="3gIvZO" value="1" />
      <property role="3gIvZN" value="false" />
    </node>
  </node>
  <node concept="3gI3PM" id="1bNmcZ3JG_1">
    <property role="3gI3ON" value="StageAMirrorHazards" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JG_4" role="3gIvZz">
      <property role="3gIvZX" value="RISK-MIRROR" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JG_5" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JG_6" role="3gI3OM">
      <property role="3gI3Or" value="H-01" />
      <property role="3gI3Oq" value="Wrong patient, course, study, frame of reference, or plan version is selected or associated." />
      <property role="3gI3Op" value="Planning or a state-changing action may be applied to the wrong anatomy, prescription, or clinical object." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JG_9" role="3gIvZz">
        <property role="3gIvZX" value="H01" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JG_a" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JG_b" role="3gI3OM">
      <property role="3gI3Or" value="H-02" />
      <property role="3gI3Oq" value="Speech or language processing misinterprets negation, number, unit, laterality, object, priority, or an ambiguous instruction." />
      <property role="3gI3Op" value="The typed intent may request an unintended planning action or parameter." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JG_e" role="3gIvZz">
        <property role="3gIvZX" value="H02" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JG_f" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JG_g" role="3gI3OM">
      <property role="3gI3Or" value="H-03" />
      <property role="3gI3Oq" value="A clinical recommendation, evidence item, or dose constraint is hallucinated, outdated, conflicted, or inapplicable." />
      <property role="3gI3Op" value="A candidate or review may be represented as evidence-based when its rule does not apply." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JG_j" role="3gIvZz">
        <property role="3gIvZX" value="H03" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JG_k" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JG_l" role="3gI3OM">
      <property role="3gI3Or" value="H-04" />
      <property role="3gI3Oq" value="A prescription, trial protocol, or authenticated physician intent is altered, overridden, or represented incorrectly." />
      <property role="3gI3Op" value="Planning may proceed against intent that was not authorized by the responsible clinician." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JG_o" role="3gIvZz">
        <property role="3gIvZX" value="H04" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JG_p" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JG_q" role="3gI3OM">
      <property role="3gI3Or" value="H-05" />
      <property role="3gI3Oq" value="A contour is missing, mislabeled, geometrically implausible, truncated, or clinically incorrect." />
      <property role="3gI3Op" value="Optimization or dose evaluation may use incorrect target or organ-at-risk anatomy." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JG_t" role="3gIvZz">
        <property role="3gIvZX" value="H05" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JG_u" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JG_v" role="3gI3OM">
      <property role="3gI3Or" value="H-06" />
      <property role="3gI3Oq" value="A rigid or deformable registration is unsuitable and propagates incorrect anatomy, geometry, or accumulated dose." />
      <property role="3gI3Op" value="Contours or dose may be interpreted in the wrong spatial relationship." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JG_y" role="3gIvZz">
        <property role="3gIvZX" value="H06" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JG_z" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JG_$" role="3gI3OM">
      <property role="3gI3Or" value="H-07" />
      <property role="3gI3Oq" value="Dose basis, biological model, fractionation, BED or EQD2 basis, units, or structure definition is mismatched." />
      <property role="3gI3Op" value="Dose objectives or comparisons may be numerically valid but clinically incommensurate." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JG_B" role="3gIvZz">
        <property role="3gIvZX" value="H07" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JG_C" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JG_D" role="3gI3OM">
      <property role="3gI3Or" value="H-08" />
      <property role="3gI3Oq" value="A dose calculation, optimizer, machine model, or technique is used outside its commissioned envelope." />
      <property role="3gI3Op" value="A candidate may contain unverified dose or machine behavior and appear clinically usable." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JG_G" role="3gIvZz">
        <property role="3gIvZX" value="H08" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JG_H" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JG_I" role="3gI3OM">
      <property role="3gI3Or" value="H-09" />
      <property role="3gI3Oq" value="Proton range, setup, motion, or interplay uncertainty is omitted, incomplete, or misconfigured." />
      <property role="3gI3Op" value="A proton candidate may appear robust while clinically important uncertainty is not evaluated." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JG_L" role="3gIvZz">
        <property role="3gIvZX" value="H09" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JG_M" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JG_N" role="3gI3OM">
      <property role="3gI3Or" value="H-10" />
      <property role="3gI3Oq" value="Candidate plans share a hidden systematic defect, lack meaningful diversity, or are infeasible or undeliverable." />
      <property role="3gI3Op" value="Reviewers may select among alternatives that do not represent safe or deliverable choices." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JG_Q" role="3gIvZz">
        <property role="3gIvZX" value="H10" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JG_R" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JG_S" role="3gI3OM">
      <property role="3gI3Or" value="H-11" />
      <property role="3gI3Oq" value="Optimization silently relaxes a hard constraint or changes a clinical priority." />
      <property role="3gI3Op" value="A candidate may violate the approved planning intent without a visible decision trail." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JG_V" role="3gIvZz">
        <property role="3gIvZX" value="H11" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JG_W" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JG_X" role="3gI3OM">
      <property role="3gI3Or" value="H-12" />
      <property role="3gI3Oq" value="DICOM or another external transfer corrupts, omits, transforms, duplicates, or misassociates plan data." />
      <property role="3gI3Op" value="Wrong or incomplete clinical objects may enter a TPS, PACS, OIS, QA, review, or treatment workflow." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JGA0" role="3gIvZz">
        <property role="3gIvZX" value="H12" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JGA1" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JGA2" role="3gI3OM">
      <property role="3gI3Or" value="H-13" />
      <property role="3gI3Oq" value="AI output weakens independent professional review through shared logic, data, automation bias, or false representation of authority." />
      <property role="3gI3Op" value="A reviewer may accept an unsuitable result or fail to exercise required independent judgment." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JGA5" role="3gIvZz">
        <property role="3gIvZX" value="H13" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JGA6" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JGA7" role="3gI3OM">
      <property role="3gI3Or" value="H-14" />
      <property role="3gI3Oq" value="Unauthorized access, prompt injection, malicious content, compromised software or model, or protected-health-information leakage occurs." />
      <property role="3gI3Op" value="Clinical data, system integrity, authority, or availability may be compromised." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JGAa" role="3gIvZz">
        <property role="3gIvZX" value="H14" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JGAb" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JGAc" role="3gI3OM">
      <property role="3gI3Or" value="H-15" />
      <property role="3gI3Oq" value="Evidence, software, or model becomes stale, drifts, fails a subgroup, or degrades without detection." />
      <property role="3gI3Op" value="A previously acceptable output may become unreliable while remaining available to users." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JGAf" role="3gIvZz">
        <property role="3gIvZX" value="H15" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JGAg" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JGAh" role="3gI3OM">
      <property role="3gI3Or" value="H-16" />
      <property role="3gI3Oq" value="An outage, timeout, retry, partial result, or failed dependency leaves incomplete work that appears valid." />
      <property role="3gI3Op" value="A partial or degraded artifact may be promoted, reviewed, transferred, or relied upon as complete." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JGAk" role="3gIvZz">
        <property role="3gIvZX" value="H16" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JGAl" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JGAm" role="3gI3OM">
      <property role="3gI3Or" value="H-17" />
      <property role="3gI3Oq" value="A post-approval edit or dependency change invalidates contours, dose, QA, approval, or transfer status without detection." />
      <property role="3gI3Op" value="Downstream evidence may remain apparently current after its basis has changed." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JGAp" role="3gIvZz">
        <property role="3gIvZX" value="H17" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JGAq" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
    <node concept="3gI3PZ" id="1bNmcZ3JGAr" role="3gI3OM">
      <property role="3gI3Or" value="H-18" />
      <property role="3gI3Oq" value="Users over-trust fluent explanations, under-trust valid alerts, or misunderstand system limits and state." />
      <property role="3gI3Op" value="Human decisions may be biased by presentation rather than clinical evidence and professional judgment." />
      <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
      <node concept="3gIvZJ" id="1bNmcZ3JGAu" role="3gIvZz">
        <property role="3gIvZX" value="H18" />
      </node>
      <node concept="3gIvZH" id="1bNmcZ3JGAv" role="3gIvZy">
        <property role="3gIvZS" value="0.2" />
      </node>
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGAD">
    <property role="3gI3Od" value="The NL-TPS shall operate as a human-supervised treatment-planning support system and shall not be represented as a substitute for the professional judgment of radiation oncologists, medical dosimetrists, qualified medical physicists, or other authorized clinical staff." />
    <property role="3gI3Oc" value="7Ri7H_AEJ6z/GOV" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="SCP; PRN; AUTH" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGAH" role="3gIvZz">
      <property role="3gIvZX" value="GOV-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGAI" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGAJ" role="3gIvZx">
      <property role="3gIvZV" value="HOR-GOV-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGAK" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGAL" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGAM" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="170" />
      <property role="3gIvY7" value="913189cef6c9b17d7b8c8bbd78d200a8605fd082041fa5d2206f2f8d0ba78448" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGAN" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGAO">
    <property role="3gI3Od" value="The NL-TPS shall restrict clinical operation to the institution-approved intended use, patient population, disease sites, modalities, machines, techniques, and tasks defined in the active release authorization." />
    <property role="3gI3Oc" value="7Ri7H_AEJ6z/GOV" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="SCP; MODE; ROAD" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGAS" role="3gIvZz">
      <property role="3gIvZX" value="GOV-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGAT" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGAU" role="3gIvZx">
      <property role="3gIvZV" value="HOR-GOV-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGAV" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGAW" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGAX" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="172" />
      <property role="3gIvY7" value="1ada340cdacdb2250ccf2c90a9732f26db5208b820eca71f58c82e287481e957" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGAY" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGAZ">
    <property role="3gI3Od" value="The NL-TPS shall block clinical execution for an unsupported or out-of-scope workflow until that workflow has completed separate risk assessment, commissioning, validation, and governance approval." />
    <property role="3gI3Oc" value="7Ri7H_AEJ6z/GOV" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="SCP; HAZ; ROAD" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGB3" role="3gIvZz">
      <property role="3gIvZX" value="GOV-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGB4" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGB5" role="3gIvZx">
      <property role="3gIvZV" value="HOR-GOV-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGB6" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGB7" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGB8" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="174" />
      <property role="3gIvY7" value="a025e846d1d072d9243a88d7681bdcee7334aa2a262a340e944e05417b635a5b" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGB9" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGBa">
    <property role="3gI3Od" value="The NL-TPS shall provide segregated training\slash\allowbreak{}research, commissioning, shadow, clinical-draft, clinical-approved, and degraded\slash\allowbreak{}read-only operating modes with mode-specific permissions and destinations." />
    <property role="3gI3Oc" value="7Ri7H_AEJ6z/GOV" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODE; ARCH" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGBe" role="3gIvZz">
      <property role="3gIvZX" value="GOV-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGBf" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGBg" role="3gIvZx">
      <property role="3gIvZV" value="HOR-GOV-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGBh" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGBi" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGBj" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="176" />
      <property role="3gIvY7" value="b4bd0b68d001c290e883378557ae1446c217dccff936a68eda4a4c290450a901" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGBk" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGBl">
    <property role="3gI3Od" value="The NL-TPS shall enforce institution-approved role authority and separation-of-duties rules for radiation oncologists, dosimetrists, medical physicists, therapists, informatics staff, quality staff, and system developers." />
    <property role="3gI3Oc" value="7Ri7H_AEJ6z/GOV" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="AUTH; MODE; QMS" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGBp" role="3gIvZz">
      <property role="3gIvZX" value="GOV-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGBq" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGBr" role="3gIvZx">
      <property role="3gIvZV" value="HOR-GOV-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGBs" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGBt" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGBu" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="178" />
      <property role="3gIvY7" value="c64d996558b5189ca1f7748b325529a578225546d729f2a9eb98e3718e6a8ad3" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGBv" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGBw">
    <property role="3gI3Od" value="The NL-TPS shall maintain the intended-use statement, approved scope, risk controls, release status, configuration baseline, and applicable regulatory and quality-system records as controlled artifacts." />
    <property role="3gI3Oc" value="7Ri7H_AEJ6z/GOV" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="SCP; QMS; ROAD" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGB$" role="3gIvZz">
      <property role="3gIvZX" value="GOV-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGB_" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGBA" role="3gIvZx">
      <property role="3gIvZV" value="HOR-GOV-006" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGBB" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGBC" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGBD" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="180" />
      <property role="3gIvY7" value="55e508ba514dc8ad0fafddbce8f889c9237e46cacb1fa3ce9a3532c886f54f5e" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGBE" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGBF">
    <property role="3gI3Od" value="The NL-TPS shall require clinical-governance approval for changes to deployment scope, accepted residual risk, evidence policy, model release, monitoring thresholds, or clinical workflow authority." />
    <property role="3gI3Oc" value="7Ri7H_AEJ6z/GOV" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="AUTH; QMS; ROAD" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGBJ" role="3gIvZz">
      <property role="3gIvZX" value="GOV-007" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGBK" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGBL" role="3gIvZx">
      <property role="3gIvZV" value="HOR-GOV-007" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGBM" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGBN" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGBO" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="182" />
      <property role="3gIvY7" value="92f9ddbb00e5c7bac2ff4519122d9c2ec87e2abfed8a0e296ae9ac46f7fd211c" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGBP" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGBQ">
    <property role="3gI3Od" value="The NL-TPS shall prevent any AI or automated service from prescribing treatment, signing or approving a prescription or plan, waiving required QA, releasing a plan for treatment, or commanding treatment delivery." />
    <property role="3gI3Oc" value="7AEoSD3Crid/SAF" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="PRN; AUTH; MODE; TLR; H-04" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGBU" role="3gIvZz">
      <property role="3gIvZX" value="SAF-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGBV" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGBW" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SAF-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGBX" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGBY" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGBZ" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="205" />
      <property role="3gIvY7" value="d1f84cda12d28778e7f99f46fdf01d645588134f48f7470c0435b894fe66a134" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGC0" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGC1" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_l" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGC2">
    <property role="3gI3Od" value="The NL-TPS shall bind every clinical action to an authenticated user and role and to a confirmed patient, course, study, frame of reference, plan version, operating mode, and destination." />
    <property role="3gI3Oc" value="7AEoSD3Crid/SAF" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="WF; ARCH; TLR; H-01" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGC6" role="3gIvZz">
      <property role="3gIvZX" value="SAF-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGC7" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGC8" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SAF-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGC9" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGCa" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGCb" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="207" />
      <property role="3gIvY7" value="73b6cf8c4eafca38b76466783317e6fe3971c15969b75ca73e801eef68f84323" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGCc" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGCd" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_6" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGCe">
    <property role="3gI3Od" value="The NL-TPS shall require confirmation of at least two patient identifiers before a state-changing clinical action is executed." />
    <property role="3gI3Oc" value="7AEoSD3Crid/SAF" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="HAZ; H-01" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGCi" role="3gIvZz">
      <property role="3gIvZX" value="SAF-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGCj" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGCk" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SAF-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGCl" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGCm" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGCn" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="209" />
      <property role="3gIvY7" value="4c4d4c2be103c952c2090b4c965f0f2b26f565921d30814d3afc1971418701e0" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGCo" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGCp" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_6" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGCq">
    <property role="3gI3Od" value="The NL-TPS shall fail closed when a safety-critical field, permission, dependency, context assertion, evidence rule, or commissioned-use condition is missing, ambiguous, inconsistent, expired, or unsupported." />
    <property role="3gI3Oc" value="7AEoSD3Crid/SAF" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="PRN; WF; TLR; H-01,H-03,H-08" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGCu" role="3gIvZz">
      <property role="3gIvZX" value="SAF-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGCv" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGCw" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SAF-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGCx" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGCy" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGCz" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="211" />
      <property role="3gIvY7" value="34cbaabd3f7915a26ae041e0b7ac9a823476709a1636dbbfd2a7899c38e8aedb" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGC$" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGC_" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_6" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGCA" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_g" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGCB" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_D" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGCC">
    <property role="3gI3Od" value="The NL-TPS shall keep automated contours, objectives, transformations, calculations, and candidate plans in a visibly unsigned draft or sandbox state until all required reviews and approvals are complete." />
    <property role="3gI3Oc" value="7AEoSD3Crid/SAF" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODE; WF; TLR; H-16" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGCG" role="3gIvZz">
      <property role="3gIvZX" value="SAF-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGCH" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGCI" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SAF-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGCJ" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGCK" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGCL" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="213" />
      <property role="3gIvY7" value="d2b28eaf72c0a7071f5e469eba7d76bba8f1b1f3ecf7b637355b7b59196026b1" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGCM" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGCN" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAh" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGCO">
    <property role="3gI3Od" value="The NL-TPS shall provide a structured preview, explicit confirmation, cancellation, and rollback for reversible state-changing actions before those actions can affect a clinical candidate." />
    <property role="3gI3Oc" value="7AEoSD3Crid/SAF" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODE; WF; PRN" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGCS" role="3gIvZz">
      <property role="3gIvZX" value="SAF-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGCT" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGCU" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SAF-006" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGCV" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGCW" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGCX" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="215" />
      <property role="3gIvY7" value="909cf5636be79a996b6197995e802a06f4fc23f12a9aa609c093bd410928f22a" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGCY" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGCZ">
    <property role="3gI3Od" value="The NL-TPS shall invalidate affected downstream approvals, QA evidence, and transfer status whenever an approved dependency changes." />
    <property role="3gI3Oc" value="7AEoSD3Crid/SAF" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="INFO; TLR; H-17" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGD3" role="3gIvZz">
      <property role="3gIvZX" value="SAF-007" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGD4" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGD5" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SAF-007" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGD6" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGD7" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGD8" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="217" />
      <property role="3gIvY7" value="000e35b63d9ed28ec812349d778144234bf7cc29619a7682162e2060c9ab05d3" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGD9" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGDa" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAm" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGDb">
    <property role="3gI3Od" value="The NL-TPS shall implement role authorization, state transitions, context assertions, hard stops, approval invalidation, and export policy in a deterministic safety kernel that is independently testable from generative models." />
    <property role="3gI3Oc" value="7AEoSD3Crid/SAF" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="ARCH; PRN; HAZ" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGDf" role="3gIvZz">
      <property role="3gIvZX" value="SAF-008" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGDg" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGDh" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SAF-008" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGDi" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGDj" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGDk" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="219" />
      <property role="3gIvY7" value="47ed6b039fa029d54ffe2bab97fcf46b227d899d0ecc95dba6c468d15845ad48" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGDl" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGDm">
    <property role="3gI3Od" value="The NL-TPS shall preserve institutionally required independent review, dose or MU verification, data-transfer verification, patient-specific QA, and physics checks without allowing AI output to satisfy incompatible approval roles." />
    <property role="3gI3Oc" value="7AEoSD3Crid/SAF" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="PRN; AUTH; VV; TLR; H-13" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGDq" role="3gIvZz">
      <property role="3gIvZX" value="SAF-009" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGDr" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGDs" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SAF-009" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGDt" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGDu" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGDv" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="221" />
      <property role="3gIvY7" value="adc2105c57031c015fb1b1e872a0b9cd72c252da297027e2c5c1747631856537" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGDw" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGDx" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA2" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGDy">
    <property role="3gI3Od" value="The NL-TPS shall identify degraded operation and failed dependencies explicitly and shall not use an unannounced fallback that changes clinical behavior, calculation, evidence, model, or destination." />
    <property role="3gI3Oc" value="7AEoSD3Crid/SAF" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="PRN; OPS; H-16" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGDA" role="3gIvZz">
      <property role="3gIvZX" value="SAF-010" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGDB" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGDC" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SAF-010" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGDD" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGDE" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGDF" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="223" />
      <property role="3gIvY7" value="3319ee4b9364afabca5277a23acf2ea89a40f212f074bdda963a7aa0263fb1d7" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGDG" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGDH" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAh" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGDI">
    <property role="3gI3Od" value="The NL-TPS shall accept typed text and user-initiated push-to-talk speech while prohibiting background listening and voice-only clinical signatures." />
    <property role="3gI3Oc" value="27NqjWjzO3o/NLI" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="WF; NLI; H-02" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGDM" role="3gIvZz">
      <property role="3gIvZX" value="NLI-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGDN" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGDO" role="3gIvZx">
      <property role="3gIvZV" value="HFR-NLI-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGDP" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGDQ" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGDR" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="246" />
      <property role="3gIvY7" value="773830b8d221331600ccf8dd8468c9628ce3e1fb9b92cd826b422c0b0217178a" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGDS" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGDT" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_b" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGDU">
    <property role="3gI3Od" value="The NL-TPS shall compile each actionable natural-language request into a versioned, inspectable, typed intent before executing a state-changing action." />
    <property role="3gI3Oc" value="27NqjWjzO3o/NLI" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="WF; NLI; TLR; H-02" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGDY" role="3gIvZz">
      <property role="3gIvZX" value="NLI-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGDZ" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGE0" role="3gIvZx">
      <property role="3gIvZV" value="HFR-NLI-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGE1" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGE2" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGE3" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="248" />
      <property role="3gIvY7" value="f19a645b7d698901bf30c83bad0352291c9cbe9cb707dde0ae11f0003f86af7a" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGE4" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGE5" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_b" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGE6">
    <property role="3gI3Od" value="The typed intent shall identify the clinical objects, requested action, parameters, units, priorities, evidence references, preconditions, expected outputs, and affected approval state." />
    <property role="3gI3Oc" value="27NqjWjzO3o/NLI" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="WF; NLI; ARCH" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGEa" role="3gIvZz">
      <property role="3gIvZX" value="NLI-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGEb" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGEc" role="3gIvZx">
      <property role="3gIvZV" value="HFR-NLI-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGEd" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGEe" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGEf" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="250" />
      <property role="3gIvY7" value="3f6de2f33a858152bb5ec9f487a8603402d6bb0fc8bcddd8d61f4c94ad167f42" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGEg" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGEq">
    <property role="3gI3Od" value="The NL-TPS shall distinguish verified patient facts, signed clinical intent, user preferences, evidence-derived rules, system assumptions, and unresolved questions in the compiled intent and user interface." />
    <property role="3gI3Oc" value="27NqjWjzO3o/NLI" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="ARCH; INFO; HFE" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGEu" role="3gIvZz">
      <property role="3gIvZX" value="NLI-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGEv" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGEw" role="3gIvZx">
      <property role="3gIvZV" value="HFR-NLI-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGEx" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGEy" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGEz" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="252" />
      <property role="3gIvY7" value="01f0210a67053f309b50d29a88e06671fa86ed4588b76c2c5d042d75661bf482" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGE$" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGE_">
    <property role="3gI3Od" value="The NL-TPS shall use deterministic validation for safety-critical numbers, units, dose basis, fractionation, negation, laterality, structure identity, and clinical-object references." />
    <property role="3gI3Oc" value="27NqjWjzO3o/NLI" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="NLI; HAZ; H-02,H-07" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGED" role="3gIvZz">
      <property role="3gIvZX" value="NLI-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGEE" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGEF" role="3gIvZx">
      <property role="3gIvZV" value="HFR-NLI-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGEG" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGEH" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGEI" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="254" />
      <property role="3gIvY7" value="15d1605ab5d8e6815367281f26828fc0a59ed8e0b6c711a7ed03eff1848ab77e" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGEJ" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGEK" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_b" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGEL" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_$" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGEM">
    <property role="3gI3Od" value="The NL-TPS shall display a structured read-back of what will change, the affected patient and object, assumptions, evidence, expected effect, expected runtime, and cancellation or rollback method before consequential execution." />
    <property role="3gI3Oc" value="27NqjWjzO3o/NLI" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="WF; NLI; TLR" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGEQ" role="3gIvZz">
      <property role="3gIvZX" value="NLI-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGER" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGES" role="3gIvZx">
      <property role="3gIvZV" value="HFR-NLI-006" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGET" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGEU" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGEV" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="256" />
      <property role="3gIvY7" value="e35a9edb06d372a849875b862f48ea897dc4df3eed212311ec427aee0587c992" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGEW" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGEX">
    <property role="3gI3Od" value="The NL-TPS shall require explicit confirmation of speech transcripts containing safety-critical numbers, units, negation, laterality, prescription elements, or clinical-object names." />
    <property role="3gI3Oc" value="27NqjWjzO3o/NLI" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="NLI; TLR; H-02" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGF1" role="3gIvZz">
      <property role="3gIvZX" value="NLI-007" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGF2" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGF3" role="3gIvZx">
      <property role="3gIvZV" value="HFR-NLI-007" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGF4" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGF5" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGF6" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="258" />
      <property role="3gIvY7" value="d9af174bcc8e902bf7cd8c9e750923a91419e8b01ea878812e6dedac985b82cc" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGF7" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGF8" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_b" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGF9">
    <property role="3gI3Od" value="The NL-TPS shall record the original user input or confirmed transcript, compiled intent, clarifications, assumptions, preview, confirmations, execution result, and user corrections in the audit ledger." />
    <property role="3gI3Oc" value="27NqjWjzO3o/NLI" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="WF; INFO; TLR" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGFd" role="3gIvZz">
      <property role="3gIvZX" value="NLI-008" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGFe" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGFf" role="3gIvZx">
      <property role="3gIvZV" value="HFR-NLI-008" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGFg" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGFh" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGFi" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="260" />
      <property role="3gIvY7" value="dbbf19e787a9a20faa103b78a9e9493e11ab84d4c87b24b6bb7721450dd708bf" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGFj" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGFk">
    <property role="3gI3Od" value="The NL-TPS shall use only an institution-approved, closed evidence service for patient-specific clinical rules and shall not derive such rules from unrestricted internet retrieval in clinical mode." />
    <property role="3gI3Oc" value="1jxv_X1CUqj/EVD" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="EVD; ARCH; TLR; H-03" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGFo" role="3gIvZz">
      <property role="3gIvZX" value="EVD-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGFp" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGFq" role="3gIvZx">
      <property role="3gIvZV" value="HFR-EVD-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGFr" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGFs" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGFt" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="283" />
      <property role="3gIvY7" value="19899074e3f5bf19a6a231eb6ca1e9bd99d0b5f21bb70161e4ae598713b5f1e1" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGFu" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGFv" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_g" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGFw">
    <property role="3gI3Od" value="The NL-TPS shall attach the source title, version or date, exact location, population, applicability, limitations, institutional approval status, effective date, and review date to each active evidence-derived rule." />
    <property role="3gI3Oc" value="1jxv_X1CUqj/EVD" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="EVD; TLR; H-03" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGF$" role="3gIvZz">
      <property role="3gIvZX" value="EVD-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGF_" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGFA" role="3gIvZx">
      <property role="3gIvZV" value="HFR-EVD-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGFB" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGFC" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGFD" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="285" />
      <property role="3gIvY7" value="df0afc00cfa87a7351ccb860eef5caa741e1a122a62401abcb7493b6263d9407" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGFE" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGFF" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_g" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGFG">
    <property role="3gI3Od" value="The NL-TPS shall apply the approved authority order of patient-specific signed intent, applicable trial protocol, institutional standard, professional guidance, and supporting peer-reviewed evidence." />
    <property role="3gI3Oc" value="1jxv_X1CUqj/EVD" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="EVD; H-03,H-04" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGFK" role="3gIvZz">
      <property role="3gIvZX" value="EVD-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGFL" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGFM" role="3gIvZx">
      <property role="3gIvZV" value="HFR-EVD-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGFN" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGFO" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGFP" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="287" />
      <property role="3gIvY7" value="082911eac6ccee0f8fa68627ed518ece49452187978ba423173139108bc60ec1" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGFQ" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGFR" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_g" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGFS" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_l" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGFT">
    <property role="3gI3Od" value="The NL-TPS shall treat the signed prescription and physician-approved case intent as the highest patient-specific authority and shall stop when a lower-tier rule conflicts with that authority." />
    <property role="3gI3Oc" value="1jxv_X1CUqj/EVD" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="EVD; H-04" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGFX" role="3gIvZz">
      <property role="3gIvZX" value="EVD-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGFY" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGFZ" role="3gIvZx">
      <property role="3gIvZV" value="HFR-EVD-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGG0" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGG1" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGG2" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="289" />
      <property role="3gIvY7" value="2ace6125bc098c95fcd32a4de625163a2cd3e74d5917b6fcba684210c699b948" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGG3" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGG4" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_l" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGG5">
    <property role="3gI3Od" value="The NL-TPS shall block or escalate conflicting, expired, retired, superseded, or inapplicable evidence rather than silently selecting or blending a clinical rule." />
    <property role="3gI3Oc" value="1jxv_X1CUqj/EVD" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="EVD; TLR; H-03" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGG9" role="3gIvZz">
      <property role="3gIvZX" value="EVD-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGGa" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGGb" role="3gIvZx">
      <property role="3gIvZV" value="HFR-EVD-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGGc" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGGd" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGGe" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="291" />
      <property role="3gIvY7" value="a2bd66cf144a5a99d0af93c52d9252295eebd41c374d92f322ae6b987beddf4f" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGGf" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGGg" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_g" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGGh">
    <property role="3gI3Od" value="The evidence service shall represent each computable rule with explicit structure definition, units, comparator, dose quantity and basis, population, exclusions, rule type, tolerance, and conflict policy." />
    <property role="3gI3Oc" value="1jxv_X1CUqj/EVD" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="EVD; INFO; H-07" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGGl" role="3gIvZz">
      <property role="3gIvZX" value="EVD-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGGm" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGGn" role="3gIvZx">
      <property role="3gIvZV" value="HFR-EVD-006" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGGo" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGGp" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGGq" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="293" />
      <property role="3gIvY7" value="b5b3ca4a685c5e776de637992ad6a745d4a7bcd28d91a60c76496645e9b6c833" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGGr" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGGs" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_$" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGGt">
    <property role="3gI3Od" value="The NL-TPS shall support controlled evidence proposal, independent clinical review, approval, publication, periodic review, retirement, emergency suspension, and rollback." />
    <property role="3gI3Oc" value="1jxv_X1CUqj/EVD" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="EVD; QMS; OPS; H-15" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGGx" role="3gIvZz">
      <property role="3gIvZX" value="EVD-007" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGGy" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGGz" role="3gIvZx">
      <property role="3gIvZV" value="HFR-EVD-007" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGG$" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGG_" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGGA" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="295" />
      <property role="3gIvY7" value="dbc499da48dd119ad65229762fa9fd159f36620b158e43d3cec5a79867650c54" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGGB" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGGC" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAc" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGGD">
    <property role="3gI3Od" value="The NL-TPS shall provide a no-source or no-applicable-rule response and require human resolution when a verified clinical rule cannot be produced." />
    <property role="3gI3Oc" value="1jxv_X1CUqj/EVD" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="EVD; PRN; H-03" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGGH" role="3gIvZz">
      <property role="3gIvZX" value="EVD-008" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGGI" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGGJ" role="3gIvZx">
      <property role="3gIvZV" value="HFR-EVD-008" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGGK" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGGL" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGGM" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="297" />
      <property role="3gIvY7" value="ba0064bf8ce608c7d2ec3bf3e743bb986557aa3601e9da431607ed0350a0b28e" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGGN" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGGO" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_g" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGGP">
    <property role="3gI3Od" value="The NL-TPS disease-site assistant shall map verified case facts to candidate workflows or templates, identify missing material information, and require clinician confirmation without autonomously diagnosing or staging disease." />
    <property role="3gI3Oc" value="2XmFPP8Pk_A/CLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; MODEL" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGGT" role="3gIvZz">
      <property role="3gIvZX" value="CLN-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGGU" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGGV" role="3gIvZx">
      <property role="3gIvZV" value="HFR-CLN-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGGW" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGGX" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGGY" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="320" />
      <property role="3gIvY7" value="778730f154d66d1c909f045245f32a7e2d883cb6f81f1ad42785eadd8ab7886a" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGGZ" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGH0">
    <property role="3gI3Od" value="The NL-TPS shall acquire and bind the approved image studies, frame of reference, registrations, structure sets, prior-treatment information, and signed clinical intent required for the active planning task." />
    <property role="3gI3Oc" value="2XmFPP8Pk_A/CLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="WF; INFO; H-01" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGH4" role="3gIvZz">
      <property role="3gIvZX" value="CLN-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGH5" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGH6" role="3gIvZx">
      <property role="3gIvZV" value="HFR-CLN-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGH7" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGH8" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGH9" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="322" />
      <property role="3gIvY7" value="d3dff2f9ec1970fabd90365f6d6ca06303ca1530d47ee82323e4ab0df12934fb" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGHa" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGHb" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_6" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGHc">
    <property role="3gI3Od" value="The NL-TPS shall permit rigid or deformable registration and derived dose accumulation only through commissioned methods with registration-specific visualization, quality review, uncertainty documentation, and approval." />
    <property role="3gI3Oc" value="2XmFPP8Pk_A/CLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; VV; H-06" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGHg" role="3gIvZz">
      <property role="3gIvZX" value="CLN-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGHh" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGHi" role="3gIvZx">
      <property role="3gIvZV" value="HFR-CLN-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGHj" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGHk" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGHl" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="324" />
      <property role="3gIvY7" value="3e58eba4256b02ad0f417c9740aa8f90402a772990ab57e76a5c316f93fd9355" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGHm" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGHn" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_v" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGHo">
    <property role="3gI3Od" value="The NL-TPS shall invoke contouring models only for approved anatomy, imaging conditions, structures, populations, and use cases and shall retain all model-generated contours as drafts pending review." />
    <property role="3gI3Oc" value="2XmFPP8Pk_A/CLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; MODEL; H-05" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGHs" role="3gIvZz">
      <property role="3gIvZX" value="CLN-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGHt" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGHu" role="3gIvZx">
      <property role="3gIvZV" value="HFR-CLN-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGHv" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGHw" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGHx" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="326" />
      <property role="3gIvY7" value="bab9346587081c4e0a71df9b98bd6e44c544e506bee0cf5002cbcfd113fd0c92" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGHy" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGHz" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_q" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGH$">
    <property role="3gI3Od" value="The NL-TPS shall display contour-model uncertainty, input anomalies, and out-of-distribution status and shall abstain or route to manual contouring when the commissioned use envelope is not satisfied." />
    <property role="3gI3Oc" value="2XmFPP8Pk_A/CLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODEL; VV; H-05,H-15" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGHC" role="3gIvZz">
      <property role="3gIvZX" value="CLN-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGHD" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGHE" role="3gIvZx">
      <property role="3gIvZV" value="HFR-CLN-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGHF" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGHG" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGHH" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="328" />
      <property role="3gIvY7" value="efc0e5fd5712c980c2d55b2c791fb2db1cff7ad51264d2980e3454f1d3496c49" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGHI" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGHJ" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_q" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGHK" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAc" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGHL">
    <property role="3gI3Od" value="The NL-TPS shall validate structure identity, nomenclature mapping, laterality, presence, completeness, topology, image coverage, and geometric plausibility before a contour set can become a clinical candidate." />
    <property role="3gI3Oc" value="2XmFPP8Pk_A/CLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; INFO; H-05" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGHP" role="3gIvZz">
      <property role="3gIvZX" value="CLN-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGHQ" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGHR" role="3gIvZx">
      <property role="3gIvZV" value="HFR-CLN-006" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGHS" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGHT" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGHU" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="330" />
      <property role="3gIvY7" value="3f95f737d98b860799d12d1cc825d74a492b11ee6eba3383b0c785c4d3f1c483" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGHV" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGHW" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_q" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGHX">
    <property role="3gI3Od" value="The NL-TPS shall preserve each contour's input study, frame of reference, model and version, configuration, naming map, confidence information, edits, reviewer, approval state, and lineage." />
    <property role="3gI3Oc" value="2XmFPP8Pk_A/CLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="INFO; TLR; H-05" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGI1" role="3gIvZz">
      <property role="3gIvZX" value="CLN-007" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGI2" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGI3" role="3gIvZx">
      <property role="3gIvZV" value="HFR-CLN-007" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGI4" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGI5" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGI6" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="332" />
      <property role="3gIvY7" value="332e18ef617aa5c3c492d354ec958b4b35069a31a03000524e6086a577cb6ef4" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGI7" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGI8" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_q" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGIi">
    <property role="3gI3Od" value="The NL-TPS shall provide slice, surface, difference, and clinically relevant error-review views and shall capture the location and extent of user edits." />
    <property role="3gI3Oc" value="2XmFPP8Pk_A/CLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; VV; HFE" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGIm" role="3gIvZz">
      <property role="3gIvZX" value="CLN-008" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGIn" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGIo" role="3gIvZx">
      <property role="3gIvZV" value="HFR-CLN-008" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGIp" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGIq" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGIr" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="334" />
      <property role="3gIvY7" value="3abf796afc7d168d58ddfe190312cf42248d61b51ea30d4ce1fe2552e94792b6" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGIs" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGIt">
    <property role="3gI3Od" value="The NL-TPS shall require radiation-oncologist approval for clinical target contours and shall enforce institution-approved approval roles for organs at risk and other derived structures." />
    <property role="3gI3Oc" value="2XmFPP8Pk_A/CLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="AUTH; UC; TLR; H-05" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGIx" role="3gIvZz">
      <property role="3gIvZX" value="CLN-009" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGIy" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGIz" role="3gIvZx">
      <property role="3gIvZV" value="HFR-CLN-009" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGI$" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGI_" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGIA" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="336" />
      <property role="3gIvY7" value="07a264b4f21afb4f54116a14ded56f0e7e7cf8c5d55689cd54046e213343152e" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGIB" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGIC" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_q" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGID">
    <property role="3gI3Od" value="The NL-TPS shall create a versioned structured planning intent from the signed prescription, approved anatomy, patient-specific instructions, applicable protocol, institutional planning standard, and confirmed user priorities." />
    <property role="3gI3Oc" value="4TI5pucg$nj/PLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="WF; UC; INFO" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGIH" role="3gIvZz">
      <property role="3gIvZX" value="PLN-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGII" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGIJ" role="3gIvZx">
      <property role="3gIvZV" value="HFR-PLN-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGIK" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGIL" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGIM" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="359" />
      <property role="3gIvY7" value="d6be3b7d57fd4db9960a08d2b4ec3164c4f02b13b10a9e10d73e11275a634ffc" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGIN" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGIO">
    <property role="3gI3Od" value="The NL-TPS shall generate or modify candidate plans only through commissioned planning, optimization, robustness, and dose-calculation services operating within the validated machine, technique, and algorithm envelope." />
    <property role="3gI3Oc" value="4TI5pucg$nj/PLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; ARCH; TLR; H-08" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGIS" role="3gIvZz">
      <property role="3gIvZX" value="PLN-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGIT" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGIU" role="3gIvZx">
      <property role="3gIvZV" value="HFR-PLN-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGIV" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGIW" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGIX" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="361" />
      <property role="3gIvY7" value="8fd76ca7b54dd137854ceeb35700430607af722f01916758c23ea39e3195982b" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGIY" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGIZ" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_D" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGJ0">
    <property role="3gI3Od" value="The NL-TPS shall prevent language, speech, disease-site, or generative models from directly calculating clinical dose or substituting for a commissioned dose engine." />
    <property role="3gI3Oc" value="4TI5pucg$nj/PLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="PRN; MODEL; H-08" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGJ4" role="3gIvZz">
      <property role="3gIvZX" value="PLN-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGJ5" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGJ6" role="3gIvZx">
      <property role="3gIvZV" value="HFR-PLN-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGJ7" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGJ8" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGJ9" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="363" />
      <property role="3gIvY7" value="12ac967713cbfd47e3a6c8b7ea398957f2f0b05813e14e9c997610f7b8169432" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGJa" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGJb" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_D" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGJc">
    <property role="3gI3Od" value="The structured planning intent shall distinguish hard constraints, planning goals, optimization objectives, preferences, and reporting-only metrics." />
    <property role="3gI3Oc" value="4TI5pucg$nj/PLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; EVD; TLR; H-11" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGJg" role="3gIvZz">
      <property role="3gIvZX" value="PLN-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGJh" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGJi" role="3gIvZx">
      <property role="3gIvZV" value="HFR-PLN-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGJj" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGJk" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGJl" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="365" />
      <property role="3gIvY7" value="cd0f6c8b96f60705e6bc4e2bd68361a5b8cd691b8315309f9b23df6439f5d135" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGJm" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGJn" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_S" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGJo">
    <property role="3gI3Od" value="The NL-TPS shall prevent silent relaxation of a hard constraint and shall require an authorized explicit action, documented rationale, and pre\slash\allowbreak{}post difference review for any permitted relaxation." />
    <property role="3gI3Oc" value="4TI5pucg$nj/PLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; TLR; H-11" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGJs" role="3gIvZz">
      <property role="3gIvZX" value="PLN-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGJt" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGJu" role="3gIvZx">
      <property role="3gIvZV" value="HFR-PLN-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGJv" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGJw" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGJx" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="367" />
      <property role="3gIvY7" value="475a5bed3613667c95fdfdf2ac087629db68eacd64eafcd3be900cba6156ca5d" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGJy" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGJz" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_S" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGJ$">
    <property role="3gI3Od" value="The NL-TPS shall generate the number of candidate plans requested by an authorized user when feasible and shall identify when the requested candidate set cannot be produced." />
    <property role="3gI3Oc" value="4TI5pucg$nj/PLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; MOE" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGJC" role="3gIvZz">
      <property role="3gIvZX" value="PLN-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGJD" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGJE" role="3gIvZx">
      <property role="3gIvZV" value="HFR-PLN-006" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGJF" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGJG" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGJH" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="369" />
      <property role="3gIvY7" value="21711cc0dbf205bfe86445b67b1e5c4f8a2215d5e4adc186ec0506649847da62" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGJI" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGJJ">
    <property role="3gI3Od" value="The NL-TPS shall document the planning strategy, parameter variation, objective tradeoff, beam or modality variation, or other method used to create meaningful candidate diversity." />
    <property role="3gI3Oc" value="4TI5pucg$nj/PLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; TLR; H-10" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGJN" role="3gIvZz">
      <property role="3gIvZX" value="PLN-007" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGJO" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGJP" role="3gIvZx">
      <property role="3gIvZV" value="HFR-PLN-007" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGJQ" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGJR" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGJS" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="371" />
      <property role="3gIvY7" value="de463c551101cc6287af8af9a82db72d1e4bf5bd215a965da7bee75652970029" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGJT" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGJU" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_N" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGJV">
    <property role="3gI3Od" value="The NL-TPS shall identify infeasible candidates and candidates dominated by another candidate under the declared evaluation criteria." />
    <property role="3gI3Oc" value="4TI5pucg$nj/PLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; TLR; H-10" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGJZ" role="3gIvZz">
      <property role="3gIvZX" value="PLN-008" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGK0" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGK1" role="3gIvZx">
      <property role="3gIvZV" value="HFR-PLN-008" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGK2" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGK3" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGK4" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="373" />
      <property role="3gIvY7" value="c4e80f8b2e446d95afeaa7de20760cc874499230ad803debe66dbf02e2ed6d58" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGK5" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGK6" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_N" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGK7">
    <property role="3gI3Od" value="The NL-TPS shall attest at runtime to the active machine model, energy or beam type, technique, dose algorithm, grid, optimizer, biological model if used, and approved configuration before plan calculation." />
    <property role="3gI3Oc" value="4TI5pucg$nj/PLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="INFO; MODEL; H-08" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGKb" role="3gIvZz">
      <property role="3gIvZX" value="PLN-009" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGKc" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGKd" role="3gIvZx">
      <property role="3gIvZV" value="HFR-PLN-009" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGKe" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGKf" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGKg" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="375" />
      <property role="3gIvY7" value="6746cc109f8cf9205b99cc4d4c0385e167cec8f8f195cb6388bfe244d55dcb3b" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGKh" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGKi" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_D" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGKj">
    <property role="3gI3Od" value="The NL-TPS shall represent physical dose, RBE-weighted dose, fractionation, normalization, BED or EQD2 when approved, and proton-specific assumptions explicitly and without implicit conversion." />
    <property role="3gI3Oc" value="4TI5pucg$nj/PLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="EVD; INFO; H-07,H-09" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGKn" role="3gIvZz">
      <property role="3gIvZX" value="PLN-010" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGKo" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGKp" role="3gIvZx">
      <property role="3gIvZV" value="HFR-PLN-010" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGKq" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGKr" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGKs" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="377" />
      <property role="3gIvY7" value="49240366f357d64ad8598905223581ef88b19ccdf7013c43ef3e5df111cba475" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGKt" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGKu" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_$" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGKv" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_I" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGKw">
    <property role="3gI3Od" value="The NL-TPS shall apply and record the institution-approved setup, range, motion, interplay, and other robustness scenarios required for the active technique before candidate eligibility." />
    <property role="3gI3Oc" value="4TI5pucg$nj/PLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; VV; H-09" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGK$" role="3gIvZz">
      <property role="3gIvZX" value="PLN-011" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGK_" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGKA" role="3gIvZx">
      <property role="3gIvZV" value="HFR-PLN-011" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGKB" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGKC" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGKD" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="379" />
      <property role="3gIvY7" value="b745cf092b67d4a4797fe1265a22d1021648c78682ddc3fe311e51d5c8864e2c" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGKE" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGKF" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_I" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGKG">
    <property role="3gI3Od" value="The NL-TPS shall preserve candidate-plan identity, parent intent, parameters, calculation outputs, warnings, configuration, evaluation results, and lineage through iterative refinement." />
    <property role="3gI3Oc" value="4TI5pucg$nj/PLN" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="INFO; ARCH; H-17" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGKK" role="3gIvZz">
      <property role="3gIvZX" value="PLN-012" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGKL" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGKM" role="3gIvZx">
      <property role="3gIvZV" value="HFR-PLN-012" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGKN" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGKO" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGKP" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="381" />
      <property role="3gIvY7" value="b3685c121928e3299676fb9c5daa4cfbf2afeace910e4e006352ca9b0faa3881" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGKQ" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGKR" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAm" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGKS">
    <property role="3gI3Od" value="The NL-TPS shall present candidate plans in a consistent comparison workspace showing absolute values and differences without changing metric definitions or display scales between candidates." />
    <property role="3gI3Oc" value="26fKV4gKT$1/REV" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; HFE; MOE" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGKW" role="3gIvZz">
      <property role="3gIvZX" value="REV-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGKX" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGKY" role="3gIvZx">
      <property role="3gIvZV" value="HFR-REV-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGKZ" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGL0" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGL1" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="404" />
      <property role="3gIvY7" value="93e06c36b07c0e5a72165ddcc625f4fe31da2274f92b9d2707c25f3166c6f0a0" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGL2" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGL3">
    <property role="3gI3Od" value="The comparison workspace shall display target coverage, organ-at-risk results, constraint status, spatial dose, hotspots and coldspots, robustness, uncertainty, complexity, deliverability, and provenance before plan selection." />
    <property role="3gI3Oc" value="26fKV4gKT$1/REV" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; TLR; H-10" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGL7" role="3gIvZz">
      <property role="3gIvZX" value="REV-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGL8" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGL9" role="3gIvZx">
      <property role="3gIvZV" value="HFR-REV-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGLa" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGLb" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGLc" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="406" />
      <property role="3gIvY7" value="8c9b81f829b1fc75e450dc2d60ffd9cbf7fcafa55d5b24419b9ac0685f530f50" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGLd" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGLe" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_N" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGLf">
    <property role="3gI3Od" value="The NL-TPS shall expose the declared tradeoffs and shall not select or recommend a winning plan solely through an opaque composite score." />
    <property role="3gI3Oc" value="26fKV4gKT$1/REV" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="UC; PRN; H-10,H-18" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGLj" role="3gIvZz">
      <property role="3gIvZX" value="REV-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGLk" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGLl" role="3gIvZx">
      <property role="3gIvZV" value="HFR-REV-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGLm" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGLn" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGLo" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="408" />
      <property role="3gIvY7" value="7de6d5c3dafd1e7fe68249cf260efbb5c08e61451f36b501dae60fb89342992d" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGLp" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGLq" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_N" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGLr" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAr" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGLs">
    <property role="3gI3Od" value="The NL-TPS shall record the selected plan, rejected alternatives, review comments, deviations, tradeoff rationale, and role-specific decisions." />
    <property role="3gI3Oc" value="26fKV4gKT$1/REV" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="INFO; MOE" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGLw" role="3gIvZz">
      <property role="3gIvZX" value="REV-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGLx" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGLy" role="3gIvZx">
      <property role="3gIvZV" value="HFR-REV-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGLz" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGL$" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGL_" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="410" />
      <property role="3gIvY7" value="21baac7a179f04d4fb2fbf673c325aa94a4ced803620636725439cc5d0881cea" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGLA" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGLB">
    <property role="3gI3Od" value="The NL-TPS shall enforce radiation-oncologist clinical plan approval and qualified-medical-physicist technical review before a candidate can enter the approved state." />
    <property role="3gI3Oc" value="26fKV4gKT$1/REV" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="AUTH; MODE; HAZ" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGLF" role="3gIvZz">
      <property role="3gIvZX" value="REV-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGLG" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGLH" role="3gIvZx">
      <property role="3gIvZV" value="HFR-REV-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGLI" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGLJ" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGLK" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="412" />
      <property role="3gIvY7" value="86dacb6b6ee533fadfdf1c52d86cebf59b8af15c758eecbfb9066e4510799c8f" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGLL" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGLM">
    <property role="3gI3Od" value="The NL-TPS shall route the approved candidate through the institutionally required independent dose or MU verification, patient-specific QA, transfer QA, and other technique-specific checks." />
    <property role="3gI3Oc" value="26fKV4gKT$1/REV" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="VV; TLR; H-13" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGLQ" role="3gIvZz">
      <property role="3gIvZX" value="REV-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGLR" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGLS" role="3gIvZx">
      <property role="3gIvZV" value="HFR-REV-006" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGLT" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGLU" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGLV" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="414" />
      <property role="3gIvY7" value="46510237e22e079d6d4f0d955688b211b2fe5841f97334829a42b97c22f0e738" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGLW" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGLX" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA2" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGM7">
    <property role="3gI3Od" value="The NL-TPS shall authorize export only after all required approvals and QA states are current and shall verify source-to-destination identity, content, geometry, and status after transfer." />
    <property role="3gI3Oc" value="26fKV4gKT$1/REV" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="WF; INFO; H-12,H-17" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGMb" role="3gIvZz">
      <property role="3gIvZX" value="REV-007" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGMc" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGMd" role="3gIvZx">
      <property role="3gIvZV" value="HFR-REV-007" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGMe" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGMf" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGMg" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="416" />
      <property role="3gIvY7" value="ff41879bc7a970afb05a9099c3f8fb6862a87a4c88b7db1e415ebb335aec61cf" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGMh" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGMi" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_X" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGMj" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAm" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGMk">
    <property role="3gI3Od" value="The NL-TPS shall make approved clinical objects immutable or version-controlled and shall require re-review of every affected downstream object after a change." />
    <property role="3gI3Oc" value="26fKV4gKT$1/REV" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODE; INFO; H-17" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGMo" role="3gIvZz">
      <property role="3gIvZX" value="REV-008" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGMp" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGMq" role="3gIvZx">
      <property role="3gIvZV" value="HFR-REV-008" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGMr" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGMs" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGMt" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="418" />
      <property role="3gIvY7" value="13a1622a5e499d7389a4d1049c7271fd9211c59bb4675227363055a8834a0e61" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGMu" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGMv" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAm" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGMw">
    <property role="3gI3Od" value="The NL-TPS shall document the independence assumptions, shared inputs, shared dependencies, ownership boundaries, and common-cause failure risks of each automated verification path." />
    <property role="3gI3Oc" value="26fKV4gKT$1/REV" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="PRN; VV; TLR; H-13" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGM$" role="3gIvZz">
      <property role="3gIvZX" value="REV-009" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGM_" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGMA" role="3gIvZx">
      <property role="3gIvZV" value="HFR-REV-009" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGMB" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGMC" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGMD" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="420" />
      <property role="3gIvY7" value="d535d79b03411e32d47d73790a525af1efca93c7c21cc64075d7609c1ccd5766" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGME" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGMF" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA2" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGMG">
    <property role="3gI3Od" value="The NL-TPS shall assign a unique identity, version, lifecycle state, owner, and source linkage to each clinical context, prescription intent, anatomy set, evidence package, planning strategy, candidate plan, review decision, QA record, and transfer record." />
    <property role="3gI3Oc" value="3Kk0BFVo$cd/DAT" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="INFO; ARCH" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGMK" role="3gIvZz">
      <property role="3gIvZX" value="DAT-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGML" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGMM" role="3gIvZx">
      <property role="3gIvZV" value="HFR-DAT-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGMN" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGMO" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGMP" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="443" />
      <property role="3gIvY7" value="60414507f7b24e74ad9ab1bf77704807db6b4319e1cbcb65f63db77edc6e7f2f" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGMQ" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGMR">
    <property role="3gI3Od" value="The NL-TPS shall maintain a dependency and provenance graph that traces every derived object to its inputs, transformations, software, model, evidence, configuration, user actions, and approvals." />
    <property role="3gI3Oc" value="3Kk0BFVo$cd/DAT" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="INFO; TLR; H-17" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGMV" role="3gIvZz">
      <property role="3gIvZX" value="DAT-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGMW" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGMX" role="3gIvZx">
      <property role="3gIvZV" value="HFR-DAT-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGMY" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGMZ" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGN0" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="445" />
      <property role="3gIvY7" value="8e21c2a3efe011a0a4479d47d9a75d77d34f296a61a7789b25be1d1376e23ed6" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGN1" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGN2" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAm" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGN3">
    <property role="3gI3Od" value="The NL-TPS shall validate and preserve explicit units, coordinate systems, dose quantity and basis, structure definitions, and rounding behavior at storage, calculation, display, and interface boundaries." />
    <property role="3gI3Oc" value="3Kk0BFVo$cd/DAT" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="INFO; H-07,H-12" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGN7" role="3gIvZz">
      <property role="3gIvZX" value="DAT-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGN8" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGN9" role="3gIvZx">
      <property role="3gIvZV" value="HFR-DAT-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGNa" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGNb" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGNc" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="447" />
      <property role="3gIvY7" value="432649d76f0ad38cfb2cc9192a85b52f4fb8af7d7f14df287683edee0fb0cc2f" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGNd" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGNe" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_$" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGNf" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_X" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGNg">
    <property role="3gI3Od" value="The NL-TPS shall validate DICOM patient and study identities, SOP Instance UIDs, references, frame-of-reference UIDs, required attributes, coordinate transformations, units, and destination fidelity for every clinical transfer." />
    <property role="3gI3Oc" value="3Kk0BFVo$cd/DAT" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="ARCH; TLR; H-01,H-12" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGNk" role="3gIvZz">
      <property role="3gIvZX" value="DAT-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGNl" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGNm" role="3gIvZx">
      <property role="3gIvZV" value="HFR-DAT-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGNn" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGNo" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGNp" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="449" />
      <property role="3gIvY7" value="c3df10b346af872e7694416275ab5afa0c028f28b3c36a58b304465023acd9b6" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGNq" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGNr" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_6" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGNs" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_X" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGNt">
    <property role="3gI3Od" value="The NL-TPS shall support the approved DICOM objects and transactions required for images, registrations, segmentations or structures, RT Plan, RT Ion Plan, RT Dose, treatment records, and related provenance in the active deployment." />
    <property role="3gI3Oc" value="3Kk0BFVo$cd/DAT" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="ARCH; QMS" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGNx" role="3gIvZz">
      <property role="3gIvZX" value="DAT-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGNy" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGNz" role="3gIvZx">
      <property role="3gIvZV" value="HFR-DAT-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGN$" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGN_" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGNA" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="451" />
      <property role="3gIvY7" value="74c5b2450e0a5b8ae16b176afa5fe5eec3d7a678dfed38c64410139aa00ec5b8" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGNB" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGNC">
    <property role="3gI3Od" value="The NL-TPS shall use approved IHE-RO profiles and FHIR or CodeX radiation-therapy exchanges where implemented and shall document conformance and known limitations." />
    <property role="3gI3Oc" value="3Kk0BFVo$cd/DAT" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="ARCH; QMS" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGNG" role="3gIvZz">
      <property role="3gIvZX" value="DAT-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGNH" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGNI" role="3gIvZx">
      <property role="3gIvZV" value="HFR-DAT-006" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGNJ" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGNK" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGNL" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="453" />
      <property role="3gIvY7" value="37a5de282ed9e17b674f9c2747f10613bdd0eecacaab4d880455b47434d4e43f" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGNM" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGNN">
    <property role="3gI3Od" value="The NL-TPS shall reject incomplete, ambiguous, inconsistent, orphaned, or partially transferred clinical data rather than promoting it to a valid state." />
    <property role="3gI3Oc" value="3Kk0BFVo$cd/DAT" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="INFO; H-12,H-16" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGNR" role="3gIvZz">
      <property role="3gIvZX" value="DAT-007" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGNS" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGNT" role="3gIvZx">
      <property role="3gIvZV" value="HFR-DAT-007" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGNU" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGNV" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="455" />
      <property role="3gIvY7" value="6bb35b11a4d2e8e069540196187a51e5ec351dd885d2aca177e75e51e347e05c" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGNW" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGNX" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_X" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGNY" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAh" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGNZ">
    <property role="3gI3Od" value="The NL-TPS shall maintain a tamper-evident, time-synchronized audit ledger of commands, context, inputs, versions, evidence, outputs, warnings, edits, approvals, QA, exports, failures, overrides, and reconciliation events." />
    <property role="3gI3Oc" value="3Kk0BFVo$cd/DAT" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="INFO; TLR; H-14" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGO3" role="3gIvZz">
      <property role="3gIvZX" value="DAT-008" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGO4" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGO5" role="3gIvZx">
      <property role="3gIvZV" value="HFR-DAT-008" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGO6" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGO7" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGO8" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="457" />
      <property role="3gIvY7" value="c3ad17309d63eb4a34f3a3deba30d6896158247915c27a74fe4de55965aacde2" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGO9" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGOa" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA7" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGOb">
    <property role="3gI3Od" value="The NL-TPS shall use integrity hashes or equivalent controls to detect unauthorized modification of clinical objects, evidence packages, software artifacts, model artifacts, audit records, and transferred data." />
    <property role="3gI3Oc" value="3Kk0BFVo$cd/DAT" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="INFO; SEC; H-12,H-14" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGOf" role="3gIvZz">
      <property role="3gIvZX" value="DAT-009" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGOg" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGOh" role="3gIvZx">
      <property role="3gIvZV" value="HFR-DAT-009" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGOi" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGOj" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGOk" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="459" />
      <property role="3gIvY7" value="0897bfa788eb1423eab9bb6de8aa3f7d24d748dde817db43db5d1b2c5f117c81" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGOl" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGOm" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_X" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGOn" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA7" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGOo">
    <property role="3gI3Od" value="The NL-TPS shall identify the authoritative system of record and retention, legal-record, export, archival, and reconciliation policy for each clinical object type." />
    <property role="3gI3Oc" value="3Kk0BFVo$cd/DAT" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="INFO; DEC" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGOs" role="3gIvZz">
      <property role="3gIvZX" value="DAT-010" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGOt" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGOu" role="3gIvZx">
      <property role="3gIvZV" value="HFR-DAT-010" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGOv" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGOw" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGOx" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="461" />
      <property role="3gIvY7" value="904709ac27de185c6717e53fd60d12cb37ff005a3d81a27f8129c625580d2a74" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGOy" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGOz">
    <property role="3gI3Od" value="The NL-TPS shall invoke only institution-approved, locked model versions registered for the active task and clinical operating mode." />
    <property role="3gI3Oc" value="48OUvMX9qWT/AIM" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODEL; TLR; H-15" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGOB" role="3gIvZz">
      <property role="3gIvZX" value="AIM-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGOC" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGOD" role="3gIvZx">
      <property role="3gIvZV" value="HFR-AIM-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGOE" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGOF" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGOG" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="484" />
      <property role="3gIvY7" value="5d71dbb6e1dc20f83b2bd89769c69c918ba6969e9f422fcb360f45a3868bc5e0" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGOH" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGOI" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAc" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGOJ">
    <property role="3gI3Od" value="The model gateway shall verify that the active case satisfies the model's intended use, input contract, population, imaging or data conditions, required preprocessing, and resource limits before inference." />
    <property role="3gI3Oc" value="48OUvMX9qWT/AIM" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="ARCH; MODEL; TLR" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGON" role="3gIvZz">
      <property role="3gIvZX" value="AIM-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGOO" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGOP" role="3gIvZx">
      <property role="3gIvZV" value="HFR-AIM-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGOQ" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGOR" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGOS" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="486" />
      <property role="3gIvY7" value="0cc0cc1ff63aad8322a2e1502fd96623fdd53f726afe8ff1a320088578ae182c" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGOT" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGOU">
    <property role="3gI3Od" value="Each clinical model shall implement a defined abstention, rejection, or manual-review response for unsupported, anomalous, incomplete, or out-of-distribution input." />
    <property role="3gI3Oc" value="48OUvMX9qWT/AIM" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODEL; TLR; H-05,H-15" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGOY" role="3gIvZz">
      <property role="3gIvZX" value="AIM-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGOZ" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGP0" role="3gIvZx">
      <property role="3gIvZV" value="HFR-AIM-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGP1" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGP2" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGP3" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="488" />
      <property role="3gIvY7" value="9f1abb516294017cde0bbff1f0aba88a23bb3eab37e9d3f5d0816541a95da533" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGP4" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGP5" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_q" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGP6" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAc" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGP7">
    <property role="3gI3Od" value="The NL-TPS shall prohibit production model-weight updates and unapproved behavioral learning from routine patient cases, user edits, prompts, or outcomes." />
    <property role="3gI3Oc" value="48OUvMX9qWT/AIM" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODEL; TLR; H-15" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGPb" role="3gIvZz">
      <property role="3gIvZX" value="AIM-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGPc" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGPd" role="3gIvZx">
      <property role="3gIvZV" value="HFR-AIM-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGPe" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGPf" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGPg" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="490" />
      <property role="3gIvY7" value="c9a90cb500de8c878819acf0819c224302a50f5e5b1321b7a5a1f25517d809a3" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGPh" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGPi" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAc" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGPj">
    <property role="3gI3Od" value="The NL-TPS shall maintain a model and dependency registry containing version, intended use, owner, supplier, training and evaluation provenance, limitations, approved configuration, signed artifacts, and software bill of materials." />
    <property role="3gI3Oc" value="48OUvMX9qWT/AIM" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODEL; SEC; QMS" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGPn" role="3gIvZz">
      <property role="3gIvZX" value="AIM-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGPo" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGPp" role="3gIvZx">
      <property role="3gIvZV" value="HFR-AIM-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGPq" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGPr" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGPs" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="492" />
      <property role="3gIvY7" value="366aa20c4a466477982199ece4112e25f8b1c12a6c502c203d7126a84dfc34e6" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGPt" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGPu">
    <property role="3gI3Od" value="Clinical model evaluation shall use separated development, tuning, internal test, external test, and site-acceptance data with documented overlap controls." />
    <property role="3gI3Oc" value="48OUvMX9qWT/AIM" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODEL; VV" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGPy" role="3gIvZz">
      <property role="3gIvZX" value="AIM-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGPz" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGP$" role="3gIvZx">
      <property role="3gIvZV" value="HFR-AIM-006" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGP_" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGPA" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGPB" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="494" />
      <property role="3gIvY7" value="a4be18799e7722c6211a30aac6e08e7085b920c19d147062018f5e3fb0a1408b" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGPC" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGPD">
    <property role="3gI3Od" value="The NL-TPS shall evaluate and display clinically relevant overall and subgroup performance, calibration, failure detection, uncertainty, edit burden, and known limitations for each approved model use." />
    <property role="3gI3Oc" value="48OUvMX9qWT/AIM" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODEL; VV; MOE" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGPH" role="3gIvZz">
      <property role="3gIvZX" value="AIM-007" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGPI" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGPJ" role="3gIvZx">
      <property role="3gIvZV" value="HFR-AIM-007" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGPK" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGPL" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGPM" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="496" />
      <property role="3gIvY7" value="065f86423c78032f2cd4a70bb6f240382698bc4801ecab0908b3838ed8b99ee3" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGPN" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGPX">
    <property role="3gI3Od" value="Changes to model weights, prompts that alter clinical behavior, retrieval configuration, clinical rules, preprocessing, dependencies, or runtime infrastructure shall undergo impact assessment, regression testing, approval, versioning, and rollback planning." />
    <property role="3gI3Oc" value="48OUvMX9qWT/AIM" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODEL; QMS; ROAD; H-15" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGQ1" role="3gIvZz">
      <property role="3gIvZX" value="AIM-008" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGQ2" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGQ3" role="3gIvZx">
      <property role="3gIvZV" value="HFR-AIM-008" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGQ4" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGQ5" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGQ6" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="498" />
      <property role="3gIvY7" value="65392d9e13ec6504d1f6908c0d509c15e9d032471840aefc7659df54b0d9d515" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGQ7" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGQ8" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAc" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGQ9">
    <property role="3gI3Od" value="The NL-TPS shall continuously display the active patient, course, study, plan, operating mode, approval state, and unsaved or unverified changes during clinical work." />
    <property role="3gI3Oc" value="30s52f96x9I/HFE" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="HFE; H-01,H-17" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGQd" role="3gIvZz">
      <property role="3gIvZX" value="HFE-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGQe" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGQf" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-HFE-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGQg" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGQh" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGQi" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="521" />
      <property role="3gIvY7" value="23a6f29cb9cec1dc50da1ba44f5804200d92e1c670266f5d534ac52e17cab42a" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGQj" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGQk" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_6" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGQl" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAm" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGQm">
    <property role="3gI3Od" value="The user interface shall visually distinguish verified patient facts, signed intent, approved evidence, model suggestions, user preferences, assumptions, warnings, and unresolved questions." />
    <property role="3gI3Oc" value="30s52f96x9I/HFE" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="NLI; HFE; H-18" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGQq" role="3gIvZz">
      <property role="3gIvZX" value="HFE-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGQr" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGQs" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-HFE-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGQt" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGQu" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGQv" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="523" />
      <property role="3gIvY7" value="3de2a15ea85daf96af7d997e09d8b655cd20358c12fa3a8723c3ceea2f1b5167" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGQw" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGQx" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAr" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGQy">
    <property role="3gI3Od" value="Warnings shall identify the hazard, affected object, required action, and escalation path and shall not rely on color alone." />
    <property role="3gI3Oc" value="30s52f96x9I/HFE" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="HFE; H-18" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGQA" role="3gIvZz">
      <property role="3gIvZX" value="HFE-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGQB" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGQC" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-HFE-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGQD" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGQE" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGQF" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="525" />
      <property role="3gIvY7" value="f9c10f4982bb4c3bd0ae73f8afe18ec618f0dc29d48e5840b74268cc038eb40a" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGQG" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGQH" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAr" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGQI">
    <property role="3gI3Od" value="Confirmation burden shall be proportional to clinical risk, and the NL-TPS shall monitor alert burden, overrides, workarounds, and critical-warning comprehension." />
    <property role="3gI3Oc" value="30s52f96x9I/HFE" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="WF; HFE; OPS; H-18" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGQM" role="3gIvZz">
      <property role="3gIvZX" value="HFE-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGQN" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGQO" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-HFE-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGQP" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGQQ" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGQR" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="527" />
      <property role="3gIvY7" value="437a69b208ff106393a5f4708684a68f22a77b163a9aa54dd959d633bfda3a0b" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGQS" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGQT" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAr" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGQU">
    <property role="3gI3Od" value="The NL-TPS shall complete formative and summative human-factors validation with representative intended users, critical tasks, environments, interruptions, handoffs, and recovery scenarios before clinical release." />
    <property role="3gI3Oc" value="30s52f96x9I/HFE" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="VV; HFE; TLR" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGQY" role="3gIvZz">
      <property role="3gIvZX" value="HFE-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGQZ" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGR0" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-HFE-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGR1" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGR2" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGR3" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="529" />
      <property role="3gIvY7" value="505ec841c6f17667c56e4e2f56b1076eee90b6c9a9291bcb1bb2ca65cb38e597" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGR4" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGR5">
    <property role="3gI3Od" value="The NL-TPS shall require role-specific training, demonstrated competency, and current authorization before a user can perform clinical functions assigned to that role." />
    <property role="3gI3Oc" value="30s52f96x9I/HFE" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="AUTH; HFE; ROAD" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGR9" role="3gIvZz">
      <property role="3gIvZX" value="HFE-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGRa" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGRb" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-HFE-006" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGRc" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGRd" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGRe" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="531" />
      <property role="3gIvY7" value="fb5335600acdd6fe2eb3fc25fc95ac6365297b16e5d5b09c2707f4fb8d55a980" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGRf" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGRg">
    <property role="3gI3Od" value="The NL-TPS shall enforce unique user identity, multi-factor authentication, least privilege, role and context authorization, session controls, and periodic access review." />
    <property role="3gI3Oc" value="nnKKnLMBvH/SEC" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="SEC; TLR; H-14" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGRk" role="3gIvZz">
      <property role="3gIvZX" value="SEC-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGRl" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGRm" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SEC-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGRn" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGRo" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGRp" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="554" />
      <property role="3gIvY7" value="18e8c8af2ce266c846cc9ea46b75641e680f7f914bf4eb9362d6d4389904488e" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGRq" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGRr" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA7" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGRs">
    <property role="3gI3Od" value="The NL-TPS shall protect data and services through approved encryption, network segmentation, managed secrets, secure configuration, endpoint controls, and least-privilege service identities." />
    <property role="3gI3Oc" value="nnKKnLMBvH/SEC" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="SEC; TLR; H-14" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGRw" role="3gIvZz">
      <property role="3gIvZX" value="SEC-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGRx" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGRy" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SEC-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGRz" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGR$" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGR_" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="556" />
      <property role="3gIvY7" value="5981136029329a5efe3509486c544c2a9dc0afcf16f5dc72c0f6c8c132713d4b" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGRA" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGRB" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA7" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGRC">
    <property role="3gI3Od" value="The NL-TPS shall prevent protected health information, images, prompts, transcripts, or outputs from being sent to an unapproved connector, model service, tenant, destination, or external tool." />
    <property role="3gI3Oc" value="nnKKnLMBvH/SEC" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="SEC; H-14" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGRG" role="3gIvZz">
      <property role="3gIvZX" value="SEC-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGRH" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGRI" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SEC-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGRJ" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGRK" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGRL" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="558" />
      <property role="3gIvY7" value="c3bf904598037b8dd1f8297b29a383f802615a14b7bc136d367393e6bbd46cec" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGRM" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGRN" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA7" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGRO">
    <property role="3gI3Od" value="The NL-TPS shall treat retrieved text, uploaded documents, DICOM metadata, user content, and model output as untrusted input and shall isolate instructions embedded in that content from system authority." />
    <property role="3gI3Oc" value="nnKKnLMBvH/SEC" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="SEC; H-14" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGRS" role="3gIvZz">
      <property role="3gIvZX" value="SEC-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGRT" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGRU" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SEC-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGRV" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGRW" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGRX" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="560" />
      <property role="3gIvY7" value="11f8fdc59553893e81bb48cf850d39bd45ca9be47993fc08f6d61c5129983701" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGRY" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGRZ" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA7" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGS0">
    <property role="3gI3Od" value="The NL-TPS shall verify the identity, integrity, signature, provenance, and approved status of software, model, evidence, configuration, and dependency artifacts before clinical use." />
    <property role="3gI3Oc" value="nnKKnLMBvH/SEC" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODEL; SEC; H-14,H-15" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGS4" role="3gIvZz">
      <property role="3gIvZX" value="SEC-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGS5" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGS6" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SEC-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGS7" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGS8" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGS9" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="562" />
      <property role="3gIvY7" value="9b82fc1b145b3f6af80f1b9058a77823ff8df4360dfe7f88506ca3961b1a5033" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGSa" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGSb" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA7" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGSc" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAc" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGSd">
    <property role="3gI3Od" value="The NL-TPS development and maintenance process shall include threat modeling, secure coding, code review, software bill of materials, vulnerability scanning, penetration testing, patch governance, and supplier-risk controls." />
    <property role="3gI3Oc" value="nnKKnLMBvH/SEC" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="SEC; QMS" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGSh" role="3gIvZz">
      <property role="3gIvZX" value="SEC-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGSi" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGSj" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SEC-006" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGSk" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGSl" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGSm" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="564" />
      <property role="3gIvY7" value="887753aa50e5ffbcefca18abb168d33eb4e67b1d8a4f969ed70233d2d6e5c251" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGSn" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGSo">
    <property role="3gI3Od" value="The NL-TPS shall centrally record and detect unauthorized access, anomalous export, integrity failure, malicious input, model or evidence compromise, secrets exposure, and suspected PHI leakage." />
    <property role="3gI3Oc" value="nnKKnLMBvH/SEC" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="SEC; OPS; H-14" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGSs" role="3gIvZz">
      <property role="3gIvZX" value="SEC-007" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGSt" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGSu" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SEC-007" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGSv" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGSw" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGSx" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="566" />
      <property role="3gIvY7" value="c174d2ac0aea9090ede5490307e7118f472c9f979d6788f9b90a48d20de40c8e" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGSy" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGSz" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA7" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGS$">
    <property role="3gI3Od" value="The NL-TPS shall support tested clinical and cybersecurity incident containment, evidence preservation, patient-impact assessment, communication, reporting, recovery, and corrective and preventive action." />
    <property role="3gI3Oc" value="nnKKnLMBvH/SEC" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="SEC; OPS; H-14" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGSC" role="3gIvZz">
      <property role="3gIvZX" value="SEC-008" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGSD" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGSE" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-SEC-008" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGSF" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGSG" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGSH" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="568" />
      <property role="3gIvY7" value="a5b7d1285c7ff2bdd18ff33579968fe9a97aa998150a897f39fa6c10825eb8c6" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGSI" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGSJ" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA7" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGSK">
    <property role="3gI3Od" value="The NL-TPS shall monitor predefined safety, model, evidence, workflow, technical, subgroup, reliability, and security signals against approved action thresholds." />
    <property role="3gI3Oc" value="4SyqJ5bQEO_/OPS" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="OPS; MOE; TLR; H-15" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGSO" role="3gIvZz">
      <property role="3gIvZX" value="OPS-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGSP" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGSQ" role="3gIvZx">
      <property role="3gIvZV" value="HOR-OPS-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGSR" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGSS" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGST" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="591" />
      <property role="3gIvY7" value="51fb342684e37b0cfe7b19cde6bb1b03c38146c686dd7d9587efa7a31ca796f9" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGSU" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGSV" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAc" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGSW">
    <property role="3gI3Od" value="The NL-TPS shall use atomic job states and shall prevent a timed-out, failed, canceled, partial, or unreconciled result from appearing complete or eligible for promotion." />
    <property role="3gI3Oc" value="4SyqJ5bQEO_/OPS" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="OPS; H-16" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGT0" role="3gIvZz">
      <property role="3gIvZX" value="OPS-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGT1" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGT2" role="3gIvZx">
      <property role="3gIvZV" value="HOR-OPS-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGT3" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGT4" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="593" />
      <property role="3gIvY7" value="866511645cfe2a3adb112c2d2b6a140c1f3596b93159c25cc47d5f5c401ca9c2" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGT5" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGT6" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAh" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGT7">
    <property role="3gI3Od" value="The NL-TPS shall support rapid suspension of a model, evidence rule, connector, workflow, disease site, or complete clinical service and rollback to an approved known-good configuration." />
    <property role="3gI3Oc" value="4SyqJ5bQEO_/OPS" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="OPS; TLR; H-15,H-16" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGTb" role="3gIvZz">
      <property role="3gIvZX" value="OPS-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGTc" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGTd" role="3gIvZx">
      <property role="3gIvZV" value="HOR-OPS-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGTe" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGTf" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGTg" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="595" />
      <property role="3gIvY7" value="55fbdc8af590eee434d66747469ea5e3e66e06f80c298874dba67c321cec35b1" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGTh" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGTi" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAc" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGTj" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAh" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGTk">
    <property role="3gI3Od" value="The NL-TPS shall provide an explicit degraded or read-only mode and an institution-approved downtime procedure that prohibits new clinical execution while preserving access to completed work and audit records as authorized." />
    <property role="3gI3Oc" value="4SyqJ5bQEO_/OPS" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODE; OPS; TLR" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGTo" role="3gIvZz">
      <property role="3gIvZX" value="OPS-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGTp" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGTq" role="3gIvZx">
      <property role="3gIvZV" value="HOR-OPS-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGTr" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGTs" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGTt" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="597" />
      <property role="3gIvY7" value="1544eb9481ceef13e73be9198351561298ca9667d170cb02dd45cdde2c3174b0" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGTu" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGTv">
    <property role="3gI3Od" value="The NL-TPS shall maintain validated backups and shall perform staged restoration, object and destination reconciliation, approval-state verification, regression testing, and documented recovery exercises." />
    <property role="3gI3Oc" value="4SyqJ5bQEO_/OPS" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="SEC; OPS" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGTz" role="3gIvZz">
      <property role="3gIvZX" value="OPS-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGT$" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGT_" role="3gIvZx">
      <property role="3gIvZV" value="HOR-OPS-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGTA" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGTB" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGTC" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="599" />
      <property role="3gIvY7" value="0827d161739a7a960aade8b3bc9be09aa890d7bf79882b8040a6c4bfa61b1d92" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGTD" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGTN">
    <property role="3gI3Od" value="The NL-TPS shall support reporting, triage, investigation, patient-impact assessment, evidence preservation, trend analysis, and corrective and preventive action for incidents, near misses, unsafe workarounds, and QA discrepancies." />
    <property role="3gI3Oc" value="4SyqJ5bQEO_/OPS" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="OPS; QMS" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGTR" role="3gIvZz">
      <property role="3gIvZX" value="OPS-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGTS" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGTT" role="3gIvZx">
      <property role="3gIvZV" value="HOR-OPS-006" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGTU" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGTV" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGTW" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="601" />
      <property role="3gIvY7" value="6e71b6d1d8351b2283b6d6e75b3ae97e0b1d37068afc1daa97b3ab7dc3839f5d" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGTX" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGTY">
    <property role="3gI3Od" value="The NL-TPS shall define, approve, monitor, and periodically review clinical service levels and action thresholds for availability, latency, recovery, data retention, reliability, safety, model performance, evidence currency, and security." />
    <property role="3gI3Oc" value="4SyqJ5bQEO_/OPS" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="OPS; MOE; DEC" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGU2" role="3gIvZz">
      <property role="3gIvZX" value="OPS-007" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGU3" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGU4" role="3gIvZx">
      <property role="3gIvZV" value="HOR-OPS-007" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGU5" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGU6" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGU7" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="603" />
      <property role="3gIvY7" value="ebab08d0a519acdb60679aedb9f2ac4e0e1c99ce12a60e9f5e2e7213f029394a" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGU8" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGU9">
    <property role="3gI3Od" value="The program shall trace each stakeholder need, hazard, risk control, and high-level requirement to allocated design, implementation, verification method, test result, anomaly disposition, and release decision." />
    <property role="3gI3Oc" value="3AUG9$YiR$1/VAL" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="HAZ; VV; QMS" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGUd" role="3gIvZz">
      <property role="3gIvZX" value="VAL-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGUe" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGUf" role="3gIvZx">
      <property role="3gIvZV" value="HOR-VAL-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGUg" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGUh" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGUi" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="626" />
      <property role="3gIvY7" value="a6226bc236cb1b6a05415acd2592dea31e9eaf00ae8887677549e89c8abf4ce8" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGUj" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGUk">
    <property role="3gI3Od" value="The integrated NL-TPS shall pass site-specific acceptance, commissioning, end-to-end, regression, shadow-mode, and governance release criteria before clinical use." />
    <property role="3gI3Oc" value="3AUG9$YiR$1/VAL" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="VV; ROAD; TLR" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGUo" role="3gIvZz">
      <property role="3gIvZX" value="VAL-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGUp" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGUq" role="3gIvZx">
      <property role="3gIvZV" value="HOR-VAL-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGUr" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGUs" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGUt" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="628" />
      <property role="3gIvY7" value="614095cf550f86364dcb83f8095af61015667732d9e37243a44ff9d9322696ad" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGUu" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGUv">
    <property role="3gI3Od" value="Verification shall include locked reference cases and challenge cases for language and voice, evidence computation, segmentation, registration, planning, dose, robustness, interoperability, security, recovery, and audit integrity." />
    <property role="3gI3Oc" value="3AUG9$YiR$1/VAL" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="VV; HAZ" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGUz" role="3gIvZz">
      <property role="3gIvZX" value="VAL-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGU$" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGU_" role="3gIvZx">
      <property role="3gIvZV" value="HOR-VAL-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGUA" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGUB" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGUC" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="630" />
      <property role="3gIvY7" value="bc96baa23c2ae297e515039c7978744c754380130a9499d29f33ac91b5a9b3c9" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGUD" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGUE">
    <property role="3gI3Od" value="End-to-end verification shall exercise normal, boundary, rare but foreseeable, wrong-context, partial-failure, timeout, rollback, post-approval change, and recovery scenarios through the official clinical interfaces." />
    <property role="3gI3Oc" value="3AUG9$YiR$1/VAL" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="HAZ; VV; OPS" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGUI" role="3gIvZz">
      <property role="3gIvZX" value="VAL-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGUJ" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGUK" role="3gIvZx">
      <property role="3gIvZV" value="HOR-VAL-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGUL" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGUM" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGUN" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="632" />
      <property role="3gIvY7" value="14a11cc686e5321cf21bb711bef3735258ab7339afcf50d8d8fb2231c8dd3112" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGUO" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGUP">
    <property role="3gI3Od" value="Clinical model validation shall include task-specific technical performance, clinically significant error, dose impact where relevant, edit burden, failure detection, subgroup performance, and human-team effect." />
    <property role="3gI3Oc" value="3AUG9$YiR$1/VAL" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="MODEL; VV; MOE" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGUT" role="3gIvZz">
      <property role="3gIvZX" value="VAL-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGUU" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGUV" role="3gIvZx">
      <property role="3gIvZV" value="HOR-VAL-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGUW" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGUX" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGUY" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="634" />
      <property role="3gIvY7" value="812e6c072856c800181957ef622ab7ae7cb849a3ed1ce69c6f80111730abc03c" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGUZ" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGV0">
    <property role="3gI3Od" value="Clinical evaluation shall progress through retrospective, shadow, and controlled limited-clinical stages with predefined endpoints, independent adjudication, and applicable research, ethics, quality, and regulatory authorization." />
    <property role="3gI3Oc" value="3AUG9$YiR$1/VAL" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="VV; ROAD; DEC" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGV4" role="3gIvZz">
      <property role="3gIvZX" value="VAL-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGV5" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGV6" role="3gIvZx">
      <property role="3gIvZV" value="HOR-VAL-006" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGV7" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGV8" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGV9" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="636" />
      <property role="3gIvY7" value="73ffbf120359c0a25b39fdc39bd845a0af2623e56fd84574257c6fe11b55feab" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGVa" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGVb">
    <property role="3gI3Od" value="The NL-TPS shall prevent progression through each release gate until its predefined safety, quality, subgroup, usability, reliability, cybersecurity, and governance evidence is complete and approved." />
    <property role="3gI3Oc" value="3AUG9$YiR$1/VAL" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="ROAD; MOE" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGVf" role="3gIvZz">
      <property role="3gIvZX" value="VAL-007" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGVg" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGVh" role="3gIvZx">
      <property role="3gIvZV" value="HOR-VAL-007" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGVi" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGVj" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGVk" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="638" />
      <property role="3gIvY7" value="8d36ef15579e5c38c8a531b72175f4f917df522a223bc44d3ad5ba231c369153" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGVl" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGVm">
    <property role="3gI3Od" value="Each expansion to a new disease site, model, modality, machine, technique, institution, adaptive workflow, interface, or evidence package shall receive documented change-impact assessment, commissioning, human-factors assessment, regression testing, and monitoring approval." />
    <property role="3gI3Oc" value="3AUG9$YiR$1/VAL" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="QMS; ROAD" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGVq" role="3gIvZz">
      <property role="3gIvZX" value="VAL-008" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGVr" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGVs" role="3gIvZx">
      <property role="3gIvZV" value="HOR-VAL-008" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGVt" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGVu" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGVv" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="640" />
      <property role="3gIvY7" value="619ba4631443ba496cc12d35849b61be5460fee813d0b9437bdd249bc88b28e6" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGVw" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGVx">
    <property role="3gI3Od" value="The NL-TPS shall not enter or remain in clinical service with an unresolved critical anomaly, unacceptable residual risk, failed release threshold, unverified risk control, or unreconciled safety-critical change." />
    <property role="3gI3Oc" value="3AUG9$YiR$1/VAL" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="HAZ; VV; QMS; ROAD" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGV_" role="3gIvZz">
      <property role="3gIvZX" value="VAL-009" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGVA" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGVB" role="3gIvZx">
      <property role="3gIvZV" value="HOR-VAL-009" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGVC" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGVD" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGVE" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="642" />
      <property role="3gIvY7" value="0b2d5d265ba777686c62b8b7a68127ac2b07deb0d845284da88c090466f52624" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGVF" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGVG">
    <property role="3gI3Od" value="The NL-TPS shall maintain separately versioned ACR ROPA, ASTRO APEx, technical-guidance, institutional, and modality-specific profiles with explicit authority, applicability, effective status, and supersession." />
    <property role="3gI3Oc" value="37$DxU4q_wQ/ACC" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="ACR; APEx; EVD; QMS" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGVK" role="3gIvZz">
      <property role="3gIvZX" value="ACC-001" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGVL" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGVM" role="3gIvZx">
      <property role="3gIvZV" value="HFR-ACC-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGVN" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGVO" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGVP" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="665" />
      <property role="3gIvY7" value="346d18c8907212ff34ed189ab5c5c7bf5008f31592b0d768877c8b654ef4eb5b" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGVQ" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGVR">
    <property role="3gI3Od" value="The NL-TPS shall require authorized human approval of every profile applicability decision, distinguish product-enforceable, workflow-supporting, evidence-only, organizational, and not-applicable controls, and shall not represent readiness status as accreditation or compliance." />
    <property role="3gI3Oc" value="37$DxU4q_wQ/ACC" />
    <property role="3gI3Ob" value="6Yvm3GjCY99/cross_cutting_safety_and_assurance_constraint" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="ACR; APEx; AUTH; H-18" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGVV" role="3gIvZz">
      <property role="3gIvZX" value="ACC-002" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGVW" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGVX" role="3gIvZx">
      <property role="3gIvZV" value="HNFR-ACC-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGVY" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGVZ" role="3gI3Oa">
      <property role="3gI3PG" value="3ymaDPnVYHy/HFE" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGW0" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="667" />
      <property role="3gIvY7" value="0b07c8e1e89739e6715320180e9eeebdc1bd275a1e766de3356a1126d5ab378d" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGW1" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGW2" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAr" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGW3">
    <property role="3gI3Od" value="The NL-TPS shall maintain atomic bidirectional traceability from each applicable source element through requirements, risks, interfaces, components, tests, evidence, deficiencies, approvals, releases, and supersession." />
    <property role="3gI3Oc" value="37$DxU4q_wQ/ACC" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="ACR; APEx; TLR; QMS" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGW7" role="3gIvZz">
      <property role="3gIvZX" value="ACC-003" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGW8" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGW9" role="3gIvZx">
      <property role="3gIvZV" value="HFR-ACC-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGWa" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGWb" role="3gI3Oa">
      <property role="3gI3PG" value="2pBNHL3$JL8/A" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGWc" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="669" />
      <property role="3gIvY7" value="1b3a31463a8e6b6f32352e3fef483f8cac65ce1c149626cc2b1644c7d78ae5f9" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGWd" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGWe">
    <property role="3gI3Od" value="The NL-TPS shall validate the completeness, consistency, signature, effective time, and authoritative source of required patient-evaluation status, prior-treatment information, simulation directive, planning directive, prescription, consent status, planning documentation, and transfer verification before the associated clinical transition." />
    <property role="3gI3Oc" value="37$DxU4q_wQ/ACC" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="APEx 1--3,14; ROPA; H-01,H-04,H-12" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGWi" role="3gIvZz">
      <property role="3gIvZX" value="ACC-004" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGWj" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGWk" role="3gIvZx">
      <property role="3gIvZV" value="HFR-ACC-003" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGWl" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGWm" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGWn" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="671" />
      <property role="3gIvY7" value="23afb1acd06420ab5190a6df47a793d8638c8cf6ceffe8ff93efa820e3d937d9" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGWo" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGWp" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_6" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGWq" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_l" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGWr" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_X" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGWs">
    <property role="3gI3Od" value="The NL-TPS shall enforce institution-approved prerequisites and schedules for patient identity verification, timeout evidence, pretreatment and replan physics checks, independent dose or MU verification, patient-specific QA, periodic chart review, end-of-treatment review, and affected-approval invalidation." />
    <property role="3gI3Oc" value="37$DxU4q_wQ/ACC" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="APEx 3; ROPA QA; H-13,H-17" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGWw" role="3gIvZz">
      <property role="3gIvZX" value="ACC-005" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGWx" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGWy" role="3gIvZx">
      <property role="3gIvZV" value="HFR-ACC-004" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGWz" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGW$" role="3gI3Oa">
      <property role="3gI3PG" value="6h_ZhumnKbU/D" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGW_" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="673" />
      <property role="3gIvY7" value="5a8c1384c8bee23489bcf6489dea9200dfdb85b0d5cdb46fbe876b40dca9b339" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGWA" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGWB" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA2" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGWC" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAm" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGWD">
    <property role="3gI3Od" value="The NL-TPS shall require QMP-owned acceptance, commissioning, limitation documentation, periodic TPS QA, postservice and upgrade assessment, annual and change-triggered end-to-end testing, and return-to-service authorization for the TPS and all clinically used support software, scripts, models, and interfaces." />
    <property role="3gI3Oc" value="37$DxU4q_wQ/ACC" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="APEx 11--12; ACR--AAPM TPS; H-08,H-15" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGWH" role="3gIvZz">
      <property role="3gIvZX" value="ACC-006" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGWI" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGWJ" role="3gIvZx">
      <property role="3gIvZV" value="HOR-ACC-001" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGWK" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGWL" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGWM" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="675" />
      <property role="3gIvY7" value="e5cb9063049b1a05c94990e414b206fae41676ca3c00b01615d1649cf1a16d85" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGWN" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGWO" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_D" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGWP" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGAc" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGWQ">
    <property role="3gI3Od" value="The NL-TPS shall maintain attributable, time-ordered, privacy-controlled evidence for credentials, competency, SOPs, staffing plans, safety events, CQI, peer review, patient education and follow-up status, deficiencies, CAPA, and survey preparation without replacing the responsible professional or facility process." />
    <property role="3gI3Oc" value="37$DxU4q_wQ/ACC" />
    <property role="3gI3Ob" value="jMIUTB_omE/operational" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="APEx 4--10,13--14; ROPA; H-14" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGWU" role="3gIvZz">
      <property role="3gIvZX" value="ACC-007" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGWV" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGWW" role="3gIvZx">
      <property role="3gIvZV" value="HOR-ACC-002" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGWX" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGWY" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGWZ" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="677" />
      <property role="3gIvY7" value="0e55ad6bfee12cc18beb0f4f3b4dc8fd4ea5fb78cc82a7ed30b8699565071fee" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGX0" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGX1" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA7" />
    </node>
  </node>
  <node concept="3hnRme" id="1bNmcZ3JGX2">
    <property role="3gI3Od" value="The NL-TPS shall apply proton-specific planning, dose, robustness, calibration, patient-specific QA, independent verification, beamline, readiness, and periodic-review controls only to the commissioned proton scope and delivery mode identified by the active release profile." />
    <property role="3gI3Oc" value="37$DxU4q_wQ/ACC" />
    <property role="3gI3Ob" value="1Pg7pL_yGnB/functional" />
    <property role="3hnRmr" value="NLTPS-HLR-MIRROR-0.2" />
    <property role="3hnRmq" value="false" />
    <property role="3hjpuh" value="ACR--AAPM PBT; PLN; VAL; H-09,H-13" />
    <ref role="3gIvZZ" node="1bNmcZ3JG$R" />
    <node concept="3gIvZJ" id="1bNmcZ3JGX6" role="3gIvZz">
      <property role="3gIvZX" value="ACC-008" />
    </node>
    <node concept="3gIvZH" id="1bNmcZ3JGX7" role="3gIvZy">
      <property role="3gIvZS" value="0.2" />
    </node>
    <node concept="3gIvZI" id="1bNmcZ3JGX8" role="3gIvZx">
      <property role="3gIvZV" value="HFR-ACC-005" />
      <property role="3gIvZU" value="F/SA/O category ID" />
      <property role="3gIvYy" value="false" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGX9" role="3gI3Oa">
      <property role="3gI3PG" value="1yA6SzRMnoc/I" />
    </node>
    <node concept="3gI3Pi" id="1bNmcZ3JGXa" role="3gI3Oa">
      <property role="3gI3PG" value="24m8Ybx32Ky/T" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGXb" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY8" value="679" />
      <property role="3gIvY7" value="038eece31171baf55715df6b61bca713cdcfe768479e72085685fe0f24ea0376" />
    </node>
    <node concept="3gIvZC" id="1bNmcZ3JGXc" role="3gIvZw">
      <property role="3gIvY9" value="overleaf/NL_TPS_High_Level_Requirements.tex" />
      <property role="3gIvY7" value="c3e7697f1e5bf3f9ec6298666b1a9db8655fd85c23569a6106c5747b6cc00bb4" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGXd" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JG_I" />
    </node>
    <node concept="3gI3PR" id="1bNmcZ3JGXe" role="3gI3O9">
      <ref role="3gI3OW" node="1bNmcZ3JGA2" />
    </node>
  </node>
</model>

