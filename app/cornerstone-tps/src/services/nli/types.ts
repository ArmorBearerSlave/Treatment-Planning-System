// Typed intent schema for the viewer's natural-language command interface,
// scoped to NLI-001..008 (spec/risks.yaml). This prototype has no patient
// record, prescription, or signature workflow -- "affected approval state"
// is always 'none' rather than a fabricated clinical concept, and
// "evidenceReferences" cite the requirement IDs this command pattern is
// built against, not clinical evidence (none exists here).

export type IntentAction =
  | 'navigate_slice'
  | 'toggle_dose_visibility'
  | 'toggle_structure_visibility'
  | 'reset_view'
  | 'zoom';

export type InputType = 'text' | 'speech';

export interface CompiledIntent {
  version: 1;
  action: IntentAction;
  /** Clinical/viewer objects this intent targets, e.g. ["DOSE_VOLUME"] or an ROI name. */
  objects: string[];
  parameters: Record<string, number | string | boolean>;
  units?: string;
  priority: 'normal';
  evidenceReferences: string[];
  preconditions: string[];
  expectedOutputs: string[];
  affectedApprovalState: 'none';
  provenance: {
    inputType: InputType;
    rawInput: string;
    confirmedTranscript: string;
  };
}

export type ParseResult =
  | { kind: 'intent'; intent: CompiledIntent }
  | { kind: 'clarification'; rawInput: string; inputType: InputType; question: string };

export interface ParserContext {
  loadedRoiNames: string[];
  doseLoaded: boolean;
  structuresLoaded: boolean;
  currentSliceIndex: number;
  totalSlices: number;
}

export interface AuditEntry {
  id: string;
  timestamp: string;
  inputType: InputType;
  rawInput: string;
  confirmedTranscript: string;
  clarificationQuestion?: string;
  compiledIntent?: CompiledIntent;
  preview?: string;
  confirmed: boolean;
  executionResult?: 'executed' | 'cancelled' | 'error';
  errorMessage?: string;
  corrections: string[];
}
