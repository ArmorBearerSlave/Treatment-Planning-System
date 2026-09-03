import type { CompiledIntent, InputType, ParseResult, ParserContext } from './types';

// Deterministic, regex/keyword parsing only (NLI-005) -- no ML/LLM
// inference in the loop, so behavior is inspectable and reproducible.
// Fixed-vocabulary commands are checked before free-text ROI name matching
// to avoid a structure name shadowing a command keyword.

const EVIDENCE = ['NLI-001', 'NLI-002', 'NLI-003', 'NLI-005'];

function baseIntent(
  action: CompiledIntent['action'],
  objects: string[],
  parameters: CompiledIntent['parameters'],
  units: string | undefined,
  preconditions: string[],
  expectedOutputs: string[],
  inputType: InputType,
  rawInput: string,
  confirmedTranscript: string,
): CompiledIntent {
  return {
    version: 1,
    action,
    objects,
    parameters,
    units,
    priority: 'normal',
    evidenceReferences: EVIDENCE,
    preconditions,
    expectedOutputs,
    affectedApprovalState: 'none',
    provenance: { inputType, rawInput, confirmedTranscript },
  };
}

function stripNegation(text: string): { negated: boolean; text: string } {
  const match = text.match(/^(don'?t|do not|never)\s+(.*)$/i);
  if (match) return { negated: true, text: match[2] };
  return { negated: false, text };
}

export function parseCommand(rawInput: string, inputType: InputType, context: ParserContext): ParseResult {
  const clarify = (question: string): ParseResult => ({ kind: 'clarification', rawInput, inputType, question });
  const intent = (i: CompiledIntent): ParseResult => ({ kind: 'intent', intent: i });

  const trimmed = rawInput.trim();
  if (trimmed.length === 0) {
    return clarify('No command was recognized in an empty input. What would you like to do?');
  }
  const { negated, text: withoutNegation } = stripNegation(trimmed);
  const text = withoutNegation.toLowerCase().replace(/\s+/g, ' ').trim();

  // --- slice navigation ---
  let m = text.match(/^(?:go to|jump to|goto)?\s*slice\s+(\d+)$/);
  if (m) {
    const requested = Number(m[1]);
    if (!Number.isInteger(requested) || requested < 1 || requested > context.totalSlices) {
      return clarify(
        `Slice ${m[1]} is outside the loaded range of 1-${context.totalSlices}. Which slice did you mean?`,
      );
    }
    return intent(
      baseIntent(
        'navigate_slice',
        ['CT_VOLUME'],
        { targetSliceIndex: requested - 1, targetSliceNumber: requested },
        'slice index',
        [`0 <= targetSliceIndex < ${context.totalSlices}`],
        [`viewport displays slice ${requested} of ${context.totalSlices}`],
        inputType,
        rawInput,
        trimmed,
      ),
    );
  }
  m = text.match(/^(?:next|forward)(?:\s+(\d+))?\s*slices?$/);
  if (m) {
    const count = m[1] ? Number(m[1]) : 1;
    return intent(
      baseIntent(
        'navigate_slice',
        ['CT_VOLUME'],
        { deltaSlices: count },
        'slice count',
        ['a CT volume is loaded'],
        [`viewport advances ${count} slice(s) forward`],
        inputType,
        rawInput,
        trimmed,
      ),
    );
  }
  m = text.match(/^(?:previous|prior|back)(?:\s+(\d+))?\s*slices?$/);
  if (m) {
    const count = m[1] ? Number(m[1]) : 1;
    return intent(
      baseIntent(
        'navigate_slice',
        ['CT_VOLUME'],
        { deltaSlices: -count },
        'slice count',
        ['a CT volume is loaded'],
        [`viewport moves ${count} slice(s) backward`],
        inputType,
        rawInput,
        trimmed,
      ),
    );
  }

  // --- dose visibility ---
  m = text.match(/^(show|display|hide|remove|toggle)\s+dose$/);
  if (m) {
    if (!context.doseLoaded) {
      return clarify('No RTDOSE overlay is loaded yet, so there is nothing to show or hide. Load one first?');
    }
    const verb = m[1];
    const visible = verb === 'toggle' ? 'toggle' : verb === 'show' || verb === 'display' ? !negated : negated;
    return intent(
      baseIntent(
        'toggle_dose_visibility',
        ['DOSE_VOLUME'],
        { visible },
        undefined,
        ['an RTDOSE volume is loaded'],
        [`RTDOSE color-wash overlay visibility is set to ${visible}`],
        inputType,
        rawInput,
        trimmed,
      ),
    );
  }

  // --- structure-set (whole-set) visibility ---
  m = text.match(/^(show|display|hide|remove|toggle)\s+(?:structures|contours)$/);
  if (m) {
    if (!context.structuresLoaded) {
      return clarify('No RTSTRUCT contours are loaded yet, so there is nothing to show or hide. Load one first?');
    }
    const verb = m[1];
    const visible = verb === 'toggle' ? 'toggle' : verb === 'show' || verb === 'display' ? !negated : negated;
    return intent(
      baseIntent(
        'toggle_structure_visibility',
        ['ALL_ROIS'],
        { visible },
        undefined,
        ['RTSTRUCT contours are loaded'],
        [`all ROI contour outlines visibility is set to ${visible}`],
        inputType,
        rawInput,
        trimmed,
      ),
    );
  }

  // --- named-ROI visibility (fallback, after fixed keywords are excluded) ---
  m = text.match(/^(show|display|hide|remove|toggle)\s+(.+)$/);
  if (m) {
    const verb = m[1];
    const nameFragment = m[2].trim();
    const matches = context.loadedRoiNames.filter((name) => name.toLowerCase().includes(nameFragment));
    if (matches.length === 0) {
      return clarify(
        context.loadedRoiNames.length > 0
          ? `"${nameFragment}" does not match any loaded ROI (${context.loadedRoiNames.join(', ')}). Which one did you mean?`
          : `"${nameFragment}" does not match any loaded ROI, and no RTSTRUCT is loaded yet.`,
      );
    }
    if (matches.length > 1) {
      return clarify(`"${nameFragment}" matches multiple ROIs (${matches.join(', ')}). Which one did you mean?`);
    }
    const roiName = matches[0];
    const visible = verb === 'toggle' ? 'toggle' : verb === 'show' || verb === 'display' ? !negated : negated;
    return intent(
      baseIntent(
        'toggle_structure_visibility',
        [roiName],
        { visible },
        undefined,
        [`ROI "${roiName}" is loaded`],
        [`ROI "${roiName}" contour visibility is set to ${visible}`],
        inputType,
        rawInput,
        trimmed,
      ),
    );
  }

  // --- reset view ---
  if (/^reset\s+(?:the\s+)?(?:view|camera)$/.test(text)) {
    return intent(
      baseIntent(
        'reset_view',
        ['VIEWPORT'],
        {},
        undefined,
        [],
        ['camera position, zoom, and pan reset to the default view'],
        inputType,
        rawInput,
        trimmed,
      ),
    );
  }

  // --- zoom ---
  m = text.match(/^zoom\s+(in|out)(?:\s+(\d+(?:\.\d+)?)x?)?$/);
  if (m) {
    const direction = m[1] as 'in' | 'out';
    const factor = m[2] ? Number(m[2]) : 1.5;
    return intent(
      baseIntent(
        'zoom',
        ['VIEWPORT'],
        { direction, factor },
        'zoom factor',
        [],
        [`viewport zooms ${direction} by a factor of ${factor}`],
        inputType,
        rawInput,
        trimmed,
      ),
    );
  }

  return clarify(
    `"${rawInput}" was not recognized as a supported command (slice navigation, show/hide dose, show/hide structures or a named ROI, reset view, zoom in/out). Could you rephrase it?`,
  );
}
