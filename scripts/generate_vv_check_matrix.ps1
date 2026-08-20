param(
    [string]$OutputPath = "overleaf\NL_TPS_Verification_Validation_Check_Matrix.tex",
    [switch]$Check
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$riskPath = Join-Path $repoRoot "overleaf\NL_TPS_Risk_and_Mitigation_Register.tex"
$mqaPath = Join-Path $repoRoot "overleaf\NL_TPS_Monthly_QA_Integration_Profile.tex"
$tracePath = Join-Path $repoRoot "mps\import\traceability.json"
$resolvedOutput = Join-Path $repoRoot $OutputPath

if (-not (Test-Path -LiteralPath $tracePath)) { throw "Missing materialized trace graph: $tracePath" }
$traceDocument = Get-Content -LiteralPath $tracePath -Raw | ConvertFrom-Json
$hazardsByEntity = @{}
foreach ($traceRecord in $traceDocument.records) {
    $hazardsByEntity[$traceRecord.id] = @($traceRecord.hazards)
}

$domainOrder = @("GOV", "SAF", "NLI", "EVD", "CLN", "PLN", "REV", "DAT", "AIM", "HFE", "SEC", "OPS", "VAL", "ACC")
$domainTitles = @{
    GOV = "Governance, intended use, and scope"
    SAF = "Safety boundaries and human authority"
    NLI = "Natural-language and voice interaction"
    EVD = "Evidence and literature governance"
    CLN = "Clinical context, imaging, registration, and contours"
    PLN = "Treatment-plan generation and calculation"
    REV = "Plan review, selection, QA, and transfer"
    DAT = "Data, interoperability, provenance, and audit"
    AIM = "AI and inference-model lifecycle"
    HFE = "Human factors, usability, and competency"
    SEC = "Privacy, cybersecurity, and secure development"
    OPS = "Clinical operations, monitoring, and resilience"
    VAL = "Verification, commissioning, release, and change control"
    ACC = "Accreditation-profile and clinical-quality governance"
}
$domainFocus = @{
    GOV = "scope, authority, separation of duties, effective configuration, change, and release"
    SAF = "patient and object context, prohibited authority, deterministic hard stops, approval state, and fail-closed behavior"
    NLI = "ambiguity, negation, numbers, units, laterality, transcript correction, typed intent, read-back, and cancellation"
    EVD = "source authority, applicability, version, effective date, conflict, exception, citation, and no-applicable-rule behavior"
    CLN = "patient identity, study and frame references, geometry, registration, contours, uncertainty, edit lineage, and review state"
    PLN = "prescription, intent, objectives, constraints, machine and technique, optimization, dose, uncertainty, and robustness"
    REV = "candidate identity, comparison basis, selection, approval, independent QA, transfer eligibility, acknowledgment, and reconciliation"
    DAT = "canonical identity, version, units, coordinates, integrity, lineage, audit, retention, DICOM semantics, and reconciliation"
    AIM = "model identity, intended-use scope, inputs, outputs, uncertainty, abstention, subgroup performance, drift, and change"
    HFE = "critical tasks, persistent context, warning comprehension, use error, workload, accessibility, training, and recovery"
    SEC = "identity, authorization, privacy, integrity, secrets, egress, malicious input, supply chain, detection, and response"
    OPS = "atomic jobs, availability, health, alerts, partial failure, degraded operation, backup, restore, recovery, and reconciliation"
    VAL = "bidirectional trace, reference and challenge cases, expected results, anomaly closure, independence, regression, and release evidence"
    ACC = "source-profile applicability, human accreditation authority, QMP ownership, evidence integrity, deficiencies, CAPA, and claim limitation"
}
$domainScenario = @{
    GOV = "governed scope, change, approval, and release scenario"
    SAF = "safety-critical clinical workflow with wrong-context and prohibited-action challenges"
    NLI = "typed and push-to-talk workflow containing realistic ambiguity and critical tokens"
    EVD = "clinical evidence selection and computable-rule workflow with conflict, expiry, and missing-rule cases"
    CLN = "representative imaging, registration, contouring, and anatomy-review case"
    PLN = "representative treatment-planning case spanning intent, candidates, dose, and robustness"
    REV = "multidisciplinary plan comparison, approval, QA, transfer, and reconciliation workflow"
    DAT = "clinical-object lifecycle and round-trip data exchange workflow"
    AIM = "model-supported clinical draft workflow including abstention, failure, and monitoring cases"
    HFE = "representative critical-task usability scenario with interruptions and recovery"
    SEC = "threat, privacy, access-control, and incident-response scenario"
    OPS = "production-like load, dependency failure, degraded-mode, and recovery scenario"
    VAL = "controlled reference-case, anomaly, regression, and release-decision scenario"
    ACC = "QMP-led quality and accreditation-evidence workflow without system-generated compliance claims"
}

function Get-EntityType([string]$id) {
    if ($id -match '^SIR-') { return 'SIR' }
    if ($id -match '^IF-') { return 'HLIR' }
    if ($id -match '^C-') { return 'CORE-COMP' }
    if ($id -match '^IC-') { return 'IF-COMP' }
    if ($id -match '^(FC|NFC|OC)-') { return 'CAT-COMP' }
    if ($id -match '-[0-9]{2}$') { return 'SUB' }
    return 'HLR'
}

function Get-Domain([string]$id, [string]$type) {
    $tokens = $id -split '-'
    if ($type -in @('HLR', 'SUB')) { return $tokens[0] }
    if ($type -in @('HLIR', 'SIR')) { return $tokens[1] }
    return 'COMP'
}

function Get-Methods([string]$evidence) {
    $latex = 'I\slash\allowbreak{}T'
    if ($evidence -match 'V\\&V\s+([^;]+)') { $latex = $Matches[1].Trim() }
    $plain = $latex -replace '\\slash\\allowbreak\{\}', '/' -replace '\\&', '&'
    $names = foreach ($code in ($plain -split '/')) {
        switch ($code.Trim()) {
            'I' { 'controlled inspection' }
            'T' { 'objective testing' }
            'A' { 'documented analysis' }
            'D' { 'witnessed demonstration' }
            'HFE' { 'representative-user human-factors evaluation' }
            default { if ($code.Trim()) { $code.Trim() } }
        }
    }
    [pscustomobject]@{ Latex = $latex; Phrase = ($names -join ', ') }
}

function Get-Owner([string]$evidence) {
    if ($evidence -match '(T-[A-Z]+)') { return $Matches[1] }
    return 'T-VV'
}

function Get-ComponentFocus([string]$id) {
    switch -Regex ($id) {
        '(IAM|SEC|PRIV|AUTH)' { return $domainFocus.SEC }
        '(SAFE|STATE|GUARD)' { return $domainFocus.SAF }
        '(VOICE|NLI|INTENT|UX|HFE)' { return "$($domainFocus.NLI); $($domainFocus.HFE)" }
        '(EVID|RULE|LIT)' { return $domainFocus.EVD }
        '(CASE|CTX|IMG|REG|SEG|CONTOUR)' { return $domainFocus.CLN }
        '(PLAN|DOSE|ROB|OPT)' { return $domainFocus.PLN }
        '(REV|QA|TRANSFER)' { return $domainFocus.REV }
        '(DICOM|TPS|IHE|ROUTE|SCH|SEM|TRX|INT)' { return "$($domainFocus.DAT); producer-consumer compatibility and route behavior" }
        '(MODEL|MGW|MREG|MVAL|AI)' { return $domainFocus.AIM }
        '(DATA|OBJ|TERM|PROV|AUD|STORE)' { return $domainFocus.DAT }
        '(JOB|OPS|MON|RES|REC|INC|BACKUP)' { return $domainFocus.OPS }
        '(VV|TEST|VVP)' { return $domainFocus.VAL }
        '(ACC|QMS|GOV|CFG|RLS|REQ|ARCH|OWN|CAP)' { return "$($domainFocus.GOV); $($domainFocus.ACC)" }
        default { return 'contract completeness, configuration, inputs, outputs, safe failure, monitoring, recovery, and traceability' }
    }
}

function Get-CheckClass([string]$type) {
    switch ($type) {
        'HLR' { 'VVC-HLR' }
        'SUB' { 'VVC-SUB' }
        'HLIR' { 'VVC-HLIR' }
        'SIR' { 'VVC-SIR' }
        'CORE-COMP' { 'VVC-COMP' }
        'IF-COMP' { 'VVC-ICOMP' }
        'CAT-COMP' { 'VVC-CCOMP' }
        'MQA-REQ' { 'VVC-MQA-R' }
        'MQA-SUB' { 'VVC-MQA-S' }
        'MQA-COMP' { 'VVC-MQA-C' }
    }
}

function Get-VerificationText($record) {
    $methods = Get-Methods $record.Evidence
    $focus = if ($record.Domain -eq 'COMP') { Get-ComponentFocus $record.Id } else { $domainFocus[$record.Domain] }
    switch ($record.Type) {
        'HLR' { return "Close direct-child coverage, then use $($methods.Phrase) to verify the parent outcome under the approved baseline. Challenge $focus and every linked risk control." }
        'SUB' { return "Use $($methods.Phrase) to execute the exact normative statement through every allocated component. Include positive, negative, boundary, stale, incompatible, failure, recovery, and audit cases applicable to $focus." }
        'HLIR' { return "Use $($methods.Phrase) to inspect producer and consumer contracts and execute the integrated route across every assigned interface family. Challenge $focus, partial results, and reconciliation." }
        'SIR' { return "Use $($methods.Phrase) to verify the assigned realization package at producer, boundary, consumer, audit, and reconciliation points. Challenge $focus and unsafe exception paths." }
        default { return "Use $($methods.Phrase) to verify the component responsibility, executable contract, safe failure state, monitoring, rollback or recovery, and all allocated requirement paths. Fault-inject conditions involving $focus." }
    }
}

function Get-ValidationText($record) {
    if ($record.Domain -eq 'COMP') {
        return 'Integrate the commissioned component in representative clinical and operational workflows; authorized users and operators confirm workflow fit, understandable state, human authority, safe failure, supportability, and recovery.'
    }
    $scenario = $domainScenario[$record.Domain]
    switch ($record.Type) {
        'HLR' { return "Representative authorized roles execute an end-to-end $scenario in the intended-use environment and confirm clinical suitability, human authority, comprehensibility, and recovery." }
        'SUB' { return "Demonstrate this child within a representative $scenario and confirm that its output supports the parent outcome without unintended state, authority, or workflow effects." }
        'HLIR' { return "Commission a representative site-, version-, machine-, and route-specific $scenario; producer, consumer, clinical owner, security, operations, and T-VV confirm fitness." }
        'SIR' { return "Validate the package contribution within its parent route during a representative $scenario, including expected failure, user response, support, and recovery." }
    }
}

function Get-AcceptanceText($record) {
    $specific = switch ($record.Type) {
        'HLR' { 'All three detailed-child and three HLIR checks pass, and the direct parent outcome is observed end to end.' }
        'SUB' { 'The exact expected result is obtained for every mandatory case and every allocated component path is covered.' }
        'HLIR' { 'All three SIR checks and every assigned interface-family profile pass paired producer-consumer and site-route acceptance.' }
        'SIR' { 'The realization package is complete; producer, boundary, consumer, audit, failure, and recovery results match the approved contract.' }
        default { 'Every allocated requirement path, contract, unit, integration, fault, monitoring, and recovery check assigned to the component passes.' }
    }
    return "$specific Configuration and data hashes, expected and actual results, logs, audit, anomaly dispositions, and approvals are retained; PASS is prohibited with an unresolved release blocker."
}

function New-Record([string]$id, [string]$trace, [string]$evidence, [string]$band) {
    $type = Get-EntityType $id
    [pscustomobject]@{
        Id = $id
        Trace = $trace
        Evidence = $evidence
        Band = $band
        Type = $type
        Domain = Get-Domain $id $type
        Hazards = @($hazardsByEntity[$id])
    }
}

$domainPattern = '(?:GOV|SAF|NLI|EVD|CLN|PLN|REV|DAT|AIM|HFE|SEC|OPS|VAL|ACC)'
$entityPattern = "^(?<id>(?:$domainPattern-[0-9]{3}(?:-[0-9]{2})?|IF-$domainPattern-[0-9]{3}-[0-9]{2}|SIR-$domainPattern-[0-9]{3}-[0-9]{2}-[0-9]{2}|C-[A-Z0-9-]+-[0-9]{2}|IC-[A-Z0-9-]+-[0-9]{2}|(?:FC|NFC|OC)-[A-Z0-9-]+-[0-9]{2}))\s&"
$records = [System.Collections.Generic.List[object]]::new()

foreach ($line in Get-Content -LiteralPath $riskPath) {
    if ($line -notmatch $entityPattern) { continue }
    $parts = $line -split ' & ', 7
    if ($parts.Count -ne 7) { throw "Cannot parse risk row: $line" }
    $band = ($parts[6] -replace '\s*\\\\\s*$', '').Trim()
    $records.Add((New-Record $Matches.id $parts[1].Trim() $parts[5].Trim() $band))
}

if ($records.Count -ne 2088) { throw "Expected 2,088 risk-baseline entities; found $($records.Count)." }
if (($records.Id | Sort-Object -Unique).Count -ne 2088) { throw 'Duplicate risk-baseline entity IDs found.' }
foreach ($record in $records) {
    if ($record.Hazards.Count -eq 0) { throw "No hazard allocation for $($record.Id)." }
}

$mqaFocus = @{
    '001' = 'source allowlisting, read-only acquisition, integrity, atomic import, and reconciliation'
    '002' = 'canonical identity, version, units, machine and configuration scope, and lifecycle state'
    '003' = 'approved protocol and tolerance applicability, effective time, uncertainty, and no-rule behavior'
    '004' = 'bidirectional provenance from source through calculation, review, approval, and readiness effect'
    '005' = 'missing, incomplete, unreadable, unsupported, conflicting, and protocol-era evidence'
    '006' = 'separation of source results from analytics, simulation, models, retrieval, and readiness adjudication'
    '007' = 'QMP authority, approval identity, separation of duties, expiry, and return to service'
    '008' = 'deviation, containment, investigation, CAPA, retest, effectiveness review, and closure'
    '009' = 'signed minimal readiness state, scope, invalidation, hold, expiry, and fail-closed consumption'
    '010' = 'typed machine-QA query and draft workflow intents, read-back, confirmation, and prohibited authority'
    '011' = 'commissioned DICOM and TPS association, UID and frame identity, round trip, and reconciliation'
    '012' = 'threat analysis, privacy, acceptance, commissioning, regression, recovery, monitoring, and release'
}
$mqaOwner = @{
    '001' = 'T-DATA/T-OPS'
    '002' = 'T-DATA'
    '003' = 'QMP/T-EVD'
    '004' = 'T-DATA/T-VV'
    '005' = 'QMP/T-OPS'
    '006' = 'T-SYS/T-VV'
    '007' = 'QMP/T-GOV'
    '008' = 'QMP/T-GOV'
    '009' = 'QMP/T-SYS'
    '010' = 'T-NLI/T-UX'
    '011' = 'T-INT/QMP'
    '012' = 'T-VV/QMP'
}

$mqaRecords = [System.Collections.Generic.List[object]]::new()
foreach ($line in Get-Content -LiteralPath $mqaPath) {
    if ($line -match '^(MQA-[0-9]{3}-[0-9]{2}) & ') {
        $parts = $line -split ' & ', 3
        $id = $Matches[1]
        $parent = ($id -split '-')[1]
        $child = ($id -split '-')[2]
        $method = switch ($child) { '01' { 'I\slash\allowbreak{}A' } '02' { 'T\slash\allowbreak{}D' } default { 'T\slash\allowbreak{}A' } }
        $mqaRecords.Add([pscustomobject]@{ Id=$id; Type='MQA-SUB'; Domain='MQA'; Evidence="V\&V $method"; Methods=$method; Owner=$mqaOwner[$parent]; Band='Gate'; Focus=$mqaFocus[$parent] })
        continue
    }
    if ($line -match '^(MQA-[0-9]{3}) & ') {
        $parts = $line -split ' & ', 4
        $id = $Matches[1]
        $parent = ($id -split '-')[1]
        $method = (($parts[3] -replace '\s*\\\\\s*$', '').Trim())
        $mqaRecords.Add([pscustomobject]@{ Id=$id; Type='MQA-REQ'; Domain='MQA'; Evidence="V\&V $method"; Methods=$method; Owner=$mqaOwner[$parent]; Band='Gate'; Focus=$mqaFocus[$parent] })
        continue
    }
    if ($line -match '^(MQA-A[0-9]{2}) & ') {
        $parts = $line -split ' & ', 4
        $id = $Matches[1]
        $mqaRecords.Add([pscustomobject]@{ Id=$id; Type='MQA-COMP'; Domain='MQA'; Evidence='V\&V I\slash\allowbreak{}T\slash\allowbreak{}D'; Methods='I\slash\allowbreak{}T\slash\allowbreak{}D'; Owner='T-VV/QMP'; Band='Gate'; Focus='machine-QA evidence, governance, readiness, language interaction, external association, and safe lifecycle behavior' })
    }
}

if ($mqaRecords.Count -ne 56) { throw "Expected 56 MQA entities; found $($mqaRecords.Count)." }
if (($mqaRecords.Id | Sort-Object -Unique).Count -ne 56) { throw 'Duplicate MQA entity IDs found.' }

$sb = [System.Text.StringBuilder]::new()
function Add-Line([string]$text = '') { [void]$sb.AppendLine($text) }

Add-Line '\documentclass[11pt,letterpaper]{article}'
Add-Line '\usepackage{nl_tps_common}'
Add-Line '\hypersetup{pdftitle={NL-TPS Verification and Validation Check Matrix},pdfsubject={NL-TPS controlled documentation}}'
Add-Line '\makeatletter'
Add-Line '\renewcommand{\@pnumwidth}{3.0em}'
Add-Line '\renewcommand{\@tocrmarg}{4.0em}'
Add-Line '\makeatother'
Add-Line '\begin{document}'
Add-Line '\NLSetPageStyle{NL-TPS VERIFICATION AND VALIDATION CHECK MATRIX}{2,144 Planned Checks Across Requirements, Interfaces, Components, and Machine QA}'
Add-Line '\NLTitleBlock{VERIFICATION AND VALIDATION SPECIFICATION}{Verification and Validation Check Matrix}{Natural-Language Treatment Planning System (NL-TPS)}{\begin{minipage}{0.95\textwidth}'
Add-Line '\NLMeta{Source baseline}{Controlled NL-TPS suite v0.1 including MQA-PKG-01}'
Add-Line '\NLMeta{Document version}{0.2 - Hazard-linked proposed baseline}'
Add-Line '\NLMeta{Date}{19 August 2026}'
Add-Line '\NLMeta{Status}{Discussion Draft - Planned checks, not executed results}'
Add-Line '\NLMeta{Coverage}{2,144 unique checks: 1,952 requirement or interface checks and 192 component or subassembly checks}'
Add-Line '\NLMeta{Hazard trace}{Every check carries one or more hazard IDs from \texttt{mps/import/traceability.json}}'
Add-Line '\end{minipage}}{This document specifies required checks. It does not claim that verification, validation, commissioning, clinical evaluation, acceptance, or release has occurred. A check becomes PASS only after controlled execution, attributable review, anomaly disposition, and approval by the required independent and clinical authorities.}'
Add-Line ''
Add-Line '\tableofcontents'
Add-Line '\clearpage'
Add-Line '\ifdefined\NLTPSCombinedDocument\else\pagenumbering{arabic}\fi'
Add-Line ''
Add-Line '\NLFrontMatterSection{Document control}'
Add-Line '\begin{small}'
Add-Line '\begin{longtable}{@{}L{0.20\textwidth}L{0.72\textwidth}@{}}'
Add-Line '\toprule'
Add-Line '\rowcolor{NLTableHeader}\textbf{Field} & \textbf{Value} \\'
Add-Line '\midrule'
Add-Line '\endfirsthead'
Add-Line '\toprule'
Add-Line '\rowcolor{NLTableHeader}\textbf{Field} & \textbf{Value} \\'
Add-Line '\midrule'
Add-Line '\endhead'
Add-Line '\midrule'
Add-Line '\multicolumn{2}{r}{\scriptsize Continued on next page} \\'
Add-Line '\endfoot'
Add-Line '\bottomrule'
Add-Line '\endlastfoot'
Add-Line 'Document owner & NL-TPS Program; verification authority assigned to T-VV; clinical validation authority remains with approved clinical governance, qualified medical physicists, radiation oncologists, dosimetrists, and other authorized specialists. \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'Source entities & 2,088 unique entities in the controlled risk baseline plus 56 MQA-PKG-01 realization entities. Categorized F/NF/O requirement IDs remain aliases to canonical source IDs and do not create duplicate checks. \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'Check status & All rows are PLANNED and UNEXECUTED until an approved protocol, environment, expected result, actual result, anomaly record, reviewer, and disposition are linked. \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'Change authority & Clinical governance, QMP technical authority, quality management, systems engineering, security/privacy, interface control, operations, affected specialty teams, and independent V\&V. \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'Supersession & None \\'
Add-Line '\end{longtable}'
Add-Line '\end{small}'
Add-Line ''
Add-Line '\NLFrontMatterSection{Executive summary}'
Add-Line 'This specification assigns one uniquely identified V\&V check to every controlled high-level requirement, detailed sub-requirement, high-level interface requirement, sub-interface requirement, component responsibility, and MQA-PKG-01 realization entity. Each row defines the minimum direct verification action, its validation contribution, objective acceptance evidence, accountable owner, inherited method, risk gate, initial status, and hazards materialized from \texttt{spec/allocations.yaml}.'
Add-Line ''
Add-Line '\begin{nlnotice}{NO INFERRED PASS OR CLINICAL AUTHORITY}'
Add-Line 'Trace completeness is not verification, a successful verification is not clinical validation, and validation is not authorization to treat. No model, retrieval system, dashboard, document generator, or automated service may mark a check PASS, accept an anomaly or residual risk, commission a route, approve a plan, declare machine readiness, or authorize clinical release.'
Add-Line '\end{nlnotice}'
Add-Line ''
Add-Line '\section{Purpose, scope, and governing principles}'
Add-Line 'Verification asks whether the specified requirement, interface, or component responsibility was implemented correctly against its controlled definition. Validation asks whether the integrated result supports the approved intended use safely and effectively for representative users, patients, workflows, sites, modalities, machines, and environments. Both are required where applicable; neither may be replaced by document review alone when executable behavior or human interaction is involved.'
Add-Line ''
Add-Line 'The matrix uses the suite''s existing evidence hierarchy and applicable institutional interpretations of AAPM task-group and medical-physics practice guidance, ISO 14971 risk controls, IEC 62304 lifecycle controls, IEC 62366-1 usability engineering, DICOM PS3 conformance, IHE-RO profiles, approved commissioning evidence, and disease-site literature. Source editions, applicability, local policy, tolerances, expected values, datasets, and acceptance thresholds shall be configuration-controlled in each executed protocol rather than inferred from this matrix.'
Add-Line ''
Add-Line '\section{Coverage and roll-up architecture}'
Add-Line '\begin{small}'
Add-Line '\begin{longtable}{@{}L{0.42\textwidth}L{0.12\textwidth}L{0.26\textwidth}L{0.12\textwidth}@{}}'
Add-Line '\toprule'
Add-Line '\rowcolor{NLTableHeader}\textbf{Entity set} & \textbf{Checks} & \textbf{Check class} & \textbf{Initial status} \\'
Add-Line '\midrule'
Add-Line '\endfirsthead'
Add-Line '\toprule'
Add-Line '\rowcolor{NLTableHeader}\textbf{Entity set} & \textbf{Checks} & \textbf{Check class} & \textbf{Initial status} \\'
Add-Line '\midrule'
Add-Line '\endhead'
Add-Line '\midrule'
Add-Line '\multicolumn{4}{r}{\scriptsize Continued on next page} \\'
Add-Line '\endfoot'
Add-Line '\bottomrule'
Add-Line '\endlastfoot'
Add-Line 'System high-level requirements & 119 & VVC-HLR & Planned \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'Detailed sub-requirements & 357 & VVC-SUB & Planned \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'High-level interface requirements & 357 & VVC-HLIR & Planned \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'Sub-interface requirements & 1,071 & VVC-SIR & Planned \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'Core component responsibilities & 45 & VVC-COMP & Planned \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'Interface component responsibilities & 61 & VVC-ICOMP & Planned \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'F/NF/O category component responsibilities & 78 & VVC-CCOMP & Planned \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'MQA realization requirements & 12 & VVC-MQA-R & Planned \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'MQA sub-requirements & 36 & VVC-MQA-S & Planned \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'MQA package subassemblies & 8 & VVC-MQA-C & Planned \\'
Add-Line '\addlinespace[2pt]'
Add-Line '\textbf{TOTAL} & \textbf{2,144} & \textbf{One check per unique entity} & \textbf{Planned} \\'
Add-Line '\end{longtable}'
Add-Line '\end{small}'
Add-Line ''
Add-Line 'A parent check does not pass by arithmetic alone. Every child must pass, but the parent must also demonstrate its emergent end-to-end outcome. An HLR therefore requires its three detailed children, three HLIRs, their SIRs and allocated components, plus direct system validation. An HLIR requires all three SIRs and every assigned interface-family profile. A component requires direct contract, unit, integration, fault, monitoring, recovery, allocation-coverage, and representative-workflow evidence.'
Add-Line ''
Add-Line '\section{Methods, independence, and execution record}'
Add-Line '\begin{small}'
Add-Line '\begin{longtable}{@{}L{0.10\textwidth}L{0.24\textwidth}L{0.58\textwidth}@{}}'
Add-Line '\toprule'
Add-Line '\rowcolor{NLTableHeader}\textbf{Code} & \textbf{Method} & \textbf{Minimum evidence} \\'
Add-Line '\midrule'
Add-Line '\endfirsthead'
Add-Line '\toprule'
Add-Line '\rowcolor{NLTableHeader}\textbf{Code} & \textbf{Method} & \textbf{Minimum evidence} \\'
Add-Line '\midrule'
Add-Line '\endhead'
Add-Line '\midrule'
Add-Line '\multicolumn{3}{r}{\scriptsize Continued on next page} \\'
Add-Line '\endfoot'
Add-Line '\bottomrule'
Add-Line '\endlastfoot'
Add-Line 'I & Inspection & Approved requirement, design, code or configuration review; bidirectional trace; signature; checklist; version and integrity evidence. \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'T & Test & Controlled inputs, expected outputs, actual outputs, tolerances and sources, positive/negative/boundary/failure cases, logs, repeatability, and anomaly disposition. \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'A & Analysis & Reproducible calculation, coverage, uncertainty, statistical or hazard analysis with locked data, assumptions, software, reviewer, and conclusion. \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'D & Demonstration & Witnessed execution of the approved workflow in the controlled environment with attributable observations and outcome. \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'HFE & Human-factors evaluation & Representative users, critical tasks, use-related hazards, environments, interruptions, workload, comprehension, recovery, observations, and acceptance decision. \\'
Add-Line '\end{longtable}'
Add-Line '\end{small}'
Add-Line ''
Add-Line 'Every executed check record shall include: immutable check and entity IDs; parent and allocation trace; approved protocol and revision; risk controls and hazard links; site, system, interface, machine, modality, technique, operating mode, software, model, evidence, and configuration versions; data manifest and hashes; preconditions; expected result and tolerance source; actual result; raw evidence and logs; deviations and anomalies; tester; independent reviewer; clinical/QMP validator where applicable; date and environment; pass/fail/blocked disposition; residual-risk decision; regression triggers; and release linkage.'
Add-Line ''
Add-Line '\section{Pass, fail, block, and change rules}'
Add-Line '\begin{itemize}'
Add-Line '\item \textbf{PASS} requires every mandatory expected result to be met and every required artifact and approval to be present. A partial pass, average pass, model confidence, or undocumented expert judgment is not PASS.'
Add-Line '\item \textbf{FAIL} records any unmet expected result, unsafe or unexplained behavior, missing mandatory evidence, or unapproved variance. Failed tests are preserved; they are never overwritten by a retest.'
Add-Line '\item \textbf{BLOCKED} records a test that cannot validly execute because an approved prerequisite, environment, reference, authority, source, configuration, or dependency is unavailable or inconsistent. BLOCKED is not PASS.'
Add-Line '\item Every anomaly shall identify affected requirements, components, hazards, patients or records if any, containment, correction, retest, regression scope, root cause, CAPA when applicable, and authorized closure.'
Add-Line '\item Any change to intended use, requirement, risk control, source evidence, tolerance, interface, vendor/version, machine, model, data distribution, workflow, security control, dependency, monitoring threshold, or recovery behavior triggers documented impact analysis and risk-based regression.'
Add-Line '\item Sampling of entity IDs is prohibited. Statistical sampling within a parameter space is permitted only when the approved protocol defines the population, rationale, power or coverage basis, boundaries, rare and adverse cases, and residual uncertainty.'
Add-Line '\end{itemize}'

function Add-MatrixHeader {
    Add-Line '\begin{scriptsize}'
    Add-Line '\begin{longtable}{@{}L{0.16\textwidth}L{0.24\textwidth}L{0.19\textwidth}L{0.225\textwidth}L{0.08\textwidth}@{}}'
    Add-Line '\toprule'
    Add-Line '\rowcolor{NLTableHeader}\textbf{Check / entity} & \textbf{Verification check} & \textbf{Validation check} & \textbf{Acceptance evidence} & \textbf{Owner / method / gate} \\'
    Add-Line '\midrule'
    Add-Line '\endfirsthead'
    Add-Line '\toprule'
    Add-Line '\rowcolor{NLTableHeader}\textbf{Check / entity} & \textbf{Verification check} & \textbf{Validation check} & \textbf{Acceptance evidence} & \textbf{Owner / method / gate} \\'
    Add-Line '\midrule'
    Add-Line '\endhead'
    Add-Line '\midrule'
    Add-Line '\multicolumn{5}{r}{\scriptsize Continued on next page} \\'
    Add-Line '\endfoot'
    Add-Line '\bottomrule'
    Add-Line '\endlastfoot'
}

function Add-MatrixFooter {
    Add-Line '\end{longtable}'
    Add-Line '\end{scriptsize}'
}

function Add-RecordRow($record) {
    $checkClass = Get-CheckClass $record.Type
    $methods = Get-Methods $record.Evidence
    $owner = Get-Owner $record.Evidence
    $verification = Get-VerificationText $record
    $validation = Get-ValidationText $record
    $acceptance = Get-AcceptanceText $record
    $hazardText = ($record.Hazards -join ', ')
    Add-Line "\textbf{$checkClass}\\\texttt{$($record.Id)}\\Hazards: $hazardText & $verification & $validation & $acceptance & $owner; $($methods.Latex); $($record.Band); Planned \\"
    Add-Line '\addlinespace[2pt]'
}

$setSections = @(
    @{ Type='HLR'; Title='System high-level requirement V\&V checks'; Intro='Each HLR check verifies the parent outcome in addition to child closure and validates the integrated clinical or operational result.' },
    @{ Type='SUB'; Title='Detailed sub-requirement V\&V checks'; Intro='Each detailed child receives a direct executable or inspectable check through its allocated components; source and F/NF/O alias IDs share one result.' },
    @{ Type='HLIR'; Title='High-level interface requirement V\&V checks'; Intro='Each HLIR check covers the paired producer-consumer contract, integrated route, assigned interface families, and all three SIR children.' },
    @{ Type='SIR'; Title='Sub-interface requirement V\&V checks'; Intro='Each SIR check verifies its assigned realization package at every relevant boundary and validates its contribution within the parent route.' }
)

foreach ($set in $setSections) {
    Add-Line "\section{$($set.Title)}"
    Add-Line $set.Intro
    foreach ($domain in $domainOrder) {
        $domainRecords = @($records | Where-Object { $_.Type -eq $set.Type -and $_.Domain -eq $domain })
        if ($domainRecords.Count -eq 0) { continue }
        Add-Line "\subsection{$($domainTitles[$domain]) ($domain) - $($domainRecords.Count) checks}"
        Add-MatrixHeader
        foreach ($record in $domainRecords) { Add-RecordRow $record }
        Add-MatrixFooter
    }
}

$componentSections = @(
    @{ Type='CORE-COMP'; Title='Core component V\&V checks'; Intro='One direct check is assigned to each of the 45 core component responsibilities.' },
    @{ Type='IF-COMP'; Title='Interface component V\&V checks'; Intro='One direct check is assigned to each of the 61 interface component responsibilities.' },
    @{ Type='CAT-COMP'; Title='F/NF/O category component V\&V checks'; Intro='One direct check is assigned to each of the 78 category-scoped component responsibilities.' }
)
foreach ($set in $componentSections) {
    $componentRecords = @($records | Where-Object { $_.Type -eq $set.Type })
    Add-Line "\section{$($set.Title)}"
    Add-Line $set.Intro
    Add-MatrixHeader
    foreach ($record in $componentRecords) { Add-RecordRow $record }
    Add-MatrixFooter
}

function Add-MqaRow($record) {
    $methods = Get-Methods $record.Evidence
    $checkClass = Get-CheckClass $record.Type
    $verification = switch ($record.Type) {
        'MQA-REQ' { "Close all three MQA child checks, then use $($methods.Phrase) to verify the complete realization outcome. Challenge $($record.Focus) without allowing analytics or AI to adjudicate readiness." }
        'MQA-SUB' { "Use $($methods.Phrase) to execute the exact MQA child obligation through its allocated components. Include source, boundary, missing, stale, wrong-context, failure, recovery, provenance, and audit cases applicable to $($record.Focus)." }
        default { "Use $($methods.Phrase) to verify the subassembly responsibility, contracts, allocations, safe state, monitoring, failure response, recovery, and trace coverage for $($record.Focus)." }
    }
    $validation = 'A QMP-led representative Daily, Monthly, Annual, commissioning, maintenance, discrepancy, and return-to-service workflow confirms fitness, comprehensibility, human authority, safe failure, and integration with the NL-TPS and commissioned external routes.'
    $acceptance = switch ($record.Type) {
        'MQA-REQ' { 'All three direct MQA child checks and the parent end-to-end outcome pass.' }
        'MQA-SUB' { 'The direct expected result and every allocated component path pass.' }
        default { 'All allocated MQA requirement paths, contracts, unit, integration, fault, monitoring, recovery, and QMP workflow checks pass.' }
    }
    $acceptance += ' Source hashes, configuration, expected and actual results, audit, anomalies, QMP review, T-VV review, and release decision are retained; no unresolved readiness or release blocker remains.'
    $hazardText = (@($hazardsByEntity[$record.Id]) -join ', ')
    if (-not $hazardText) { throw "No hazard allocation for $($record.Id)." }
    Add-Line "\textbf{$checkClass}\\\texttt{$($record.Id)}\\Hazards: $hazardText & $verification & $validation & $acceptance & $($record.Owner); $($record.Methods); Gate; Planned \\"
    Add-Line '\addlinespace[2pt]'
}

Add-Line '\section{Machine-QA realization V\&V checks}'
Add-Line 'These 56 checks supplement the 2,088-entity controlled baseline and trace MQA-PKG-01 into the same independent V\&V and clinical-governance process. They do not create automated machine-readiness or return-to-service authority.'
foreach ($mqaType in @('MQA-REQ','MQA-SUB','MQA-COMP')) {
    $subset = @($mqaRecords | Where-Object Type -eq $mqaType)
    $title = switch ($mqaType) { 'MQA-REQ' { 'MQA realization requirements' } 'MQA-SUB' { 'MQA sub-requirements' } default { 'MQA package subassemblies' } }
    Add-Line "\subsection{$title - $($subset.Count) checks}"
    Add-MatrixHeader
    foreach ($record in $subset) { Add-MqaRow $record }
    Add-MatrixFooter
}

Add-Line '\section{Execution sequence and release gates}'
Add-Line '\begin{enumerate}'
Add-Line '\item Freeze the applicable requirements, risks, architecture, interfaces, component allocations, evidence, site, machines, models, data, software, and configuration manifest.'
Add-Line '\item Approve check procedures, expected results, tolerance sources, datasets, environments, independence assignments, clinical validation protocols, and anomaly rules before execution.'
Add-Line '\item Execute component and SIR checks first; preserve raw evidence and failed attempts. Resolve or formally block affected higher-level checks.'
Add-Line '\item Execute sub-requirement and HLIR integration checks, including negative, boundary, concurrency, interoperability, failure, recovery, security, and human-factors cases.'
Add-Line '\item Execute HLR and MQA parent validation using representative team-of-teams workflows in the intended environment; do not infer parent PASS solely from child counts.'
Add-Line '\item Complete coverage analysis, anomaly and CAPA closure, residual-risk review, regression, site acceptance, QMP and clinical approvals, and independent T-VV release recommendation.'
Add-Line '\item Clinical governance issues or withholds the scoped release. Production monitoring and post-release evidence feed change impact and regression.'
Add-Line '\end{enumerate}'
Add-Line ''
Add-Line '\section{Structural completeness audit}'
Add-Line '\begin{small}'
Add-Line '\begin{longtable}{@{}L{0.40\textwidth}L{0.14\textwidth}L{0.14\textwidth}L{0.16\textwidth}L{0.08\textwidth}@{}}'
Add-Line '\toprule'
Add-Line '\rowcolor{NLTableHeader}\textbf{Audit item} & \textbf{Expected} & \textbf{Generated} & \textbf{Exceptions} & \textbf{Status} \\'
Add-Line '\midrule'
Add-Line '\endfirsthead'
Add-Line '\toprule'
Add-Line '\rowcolor{NLTableHeader}\textbf{Audit item} & \textbf{Expected} & \textbf{Generated} & \textbf{Exceptions} & \textbf{Status} \\'
Add-Line '\midrule'
Add-Line '\endhead'
Add-Line '\midrule'
Add-Line '\multicolumn{5}{r}{\scriptsize Continued on next page} \\'
Add-Line '\endfoot'
Add-Line '\bottomrule'
Add-Line '\endlastfoot'
Add-Line 'Controlled risk-baseline entity checks & 2,088 & 2,088 & 0 & Pass \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'MQA-PKG-01 supplemental checks & 56 & 56 & 0 & Pass \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'Unique check-to-entity pairs & 2,144 & 2,144 & 0 duplicates & Pass \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'Categorized F/NF/O alias duplication & 0 & 0 & Aliases retained in source trace & Pass \\'
Add-Line '\addlinespace[2pt]'
Add-Line 'Executed-result claims & 0 & 0 & All checks remain Planned & Pass \\'
Add-Line '\end{longtable}'
Add-Line '\end{small}'
Add-Line ''
Add-Line '\section{Definition of done}'
Add-Line 'This V\&V specification is realized only when each of the 2,144 checks has an approved executable procedure or controlled inspection/analysis record, complete trace, locked environment and evidence, expected and actual results, anomaly disposition, independent review, and applicable clinical/QMP validation. A release package shall prove complete bidirectional trace from ConOps through requirements, interfaces, components, risks, checks, results, anomalies, monitoring, and the exact scoped release decision. Until then, the matrix is a plan and no row is PASS.'
Add-Line ''
Add-Line '\end{document}'

# StringBuilder.AppendLine emits Environment.NewLine, which is CRLF on Windows and
# LF on Linux. The repository pins LF through .gitattributes and the -Check
# comparison below is byte-exact, so an unnormalized build made the check pass on CI
# and fail on every Windows workstation. Normalizing here makes the generated text
# canonical LF independent of the host; the comparison stays byte-exact.
$rendered = $sb.ToString().Replace("`r`n", "`n")
$generatedCheckRows = ([regex]::Matches($rendered, '\\textbf\{VVC-')).Count
if ($generatedCheckRows -ne 2144) { throw "Expected 2,144 generated check rows; found $generatedCheckRows." }
$generatedHazardRows = ([regex]::Matches($rendered, '\\\\Hazards: H-')).Count
if ($generatedHazardRows -ne 2144) { throw "Expected 2,144 hazard-linked check rows; found $generatedHazardRows." }

if ($Check) {
    if (-not (Test-Path -LiteralPath $resolvedOutput)) { throw "Generated document is missing: $resolvedOutput" }
    $existing = [System.IO.File]::ReadAllText($resolvedOutput)
    if ($existing -cne $rendered) { throw "V&V generated-document drift detected: $resolvedOutput" }
    Write-Output "PASS: V&V generated document matches $resolvedOutput"
}
else {
    $encoding = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($resolvedOutput, $rendered, $encoding)
    Write-Output "Generated $resolvedOutput"
}
Write-Output "Risk-baseline checks: $($records.Count)"
Write-Output "MQA checks: $($mqaRecords.Count)"
Write-Output "Total checks: $generatedCheckRows"
