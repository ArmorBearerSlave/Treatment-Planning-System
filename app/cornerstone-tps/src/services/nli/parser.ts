import type { CompiledIntent, InputType, ParseResult, ParserContext } from './types';

// Deterministic, regex/keyword parsing only (NLI-005) -- no ML/LLM
// inference in the loop, so behavior is inspectable and reproducible.
// Fixed-vocabulary commands are checked before free-text ROI name matching
// to avoid a structure name shadowing a command keyword.

const EVIDENCE = ['NLI-001', 'NLI-002', 'NLI-003', 'NLI-005'];

// Matches "structures"/"contours" optionally prefixed with the DICOM object
// name ("RTSTRUCT contours", "rt struct structures"), "structure/contour
// set" alone, "RTSTRUCT" alone, and an optional trailing ", whole set".
const STRUCTURES_NOUN =
  '(?:(?:rt\\s*struct(?:ure)?s?\\s+)?(?:structures|contours)|structure set|contour set|rt\\s*struct(?:ure)?s?)(?:,?\\s*whole set)?';
const STRUCTURES_NOUN_RE = new RegExp(`^(?:the\\s+)?${STRUCTURES_NOUN}$`);
const VERB_STRUCTURES_RE = new RegExp(`^(show|display|hide|remove|toggle)\\s+(?:the\\s+)?${STRUCTURES_NOUN}$`);

// Matches "dose"/"rtdose" alone or followed by "overlay" ("RTDOSE overlay",
// "dose overlay") -- bare "overlay" alone is deliberately NOT matched here,
// since it's ambiguous with a structure/contour overlay.
const DOSE_NOUN = '(?:(?:rt\\s*dose|dose)\\s+overlay|rt\\s*dose|dose)';
const DOSE_NOUN_RE = new RegExp(`^(?:the\\s+)?${DOSE_NOUN}$`);
const VERB_DOSE_RE = new RegExp(`^(show|display|hide|remove|toggle)\\s+(?:the\\s+)?${DOSE_NOUN}$`);

// Single source of truth for the command menu shown in the UI, the "help"
// command's response, and the catch-all "not recognized" message -- so
// none of the three can silently drift out of sync with each other.
export interface CommandCategory {
  label: string;
  examples: string[];
}

export const COMMAND_CATEGORIES: CommandCategory[] = [
  { label: 'Slice navigation', examples: ['go to slice 45', 'next slice', 'previous 3 slices'] },
  { label: 'RTDOSE overlay', examples: ['show dose', 'hide dose', 'toggle dose', 'dose'] },
  { label: 'RTSTRUCT contours (whole set)', examples: ['show structures', 'hide structures', 'structures'] },
  { label: 'A named ROI', examples: ['hide the prostate', 'show BODY', 'prostate'] },
  { label: 'Camera', examples: ['reset view', 'zoom in', 'zoom out 2'] },
  { label: 'Help', examples: ['help', 'what can I say?'] },
];

const COMMAND_HELP = 'Supported commands: ' + COMMAND_CATEGORIES.map(describeCategory).join('; ') + '.';

function describeCategory(category: CommandCategory): string {
  return `${category.label} (${category.examples.map((e) => `"${e}"`).join(', ')})`;
}


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
  // Speech transcripts routinely include trailing sentence punctuation,
  // filler words a typed command wouldn't ("please"), and hyphens where a
  // typed command would have a space ("RT-struck" for "RT struct") --
  // strip/normalize those before matching so they don't block an otherwise
  // well-formed command. This is still plain normalization, not fuzzy/ML
  // matching (NLI-005): anything not covered below still falls through to
  // a clarification request rather than being guessed at.
  const text = withoutNegation
    .toLowerCase()
    .replace(/[.!?]+$/g, '')
    .replace(/\bplease\b/g, '')
    .replace(/-/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  if (/^(?:help|commands?|what commands?(?: can i (?:say|use))?|what can i say)$/.test(text)) {
    return clarify(COMMAND_HELP);
  }

  // --- slice navigation ---
  let m = text.match(/^(?:go to|jump to|goto)?\s*(?:the\s+)?slice\s+(\d+)$/);
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
  m = text.match(VERB_DOSE_RE);
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
  m = text.match(VERB_STRUCTURES_RE);
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

  // --- bare noun, no verb: "dose" or "structures" alone default to toggle,
  // a well-defined action rather than a guessed show/hide direction.
  if (DOSE_NOUN_RE.test(text)) {
    if (!context.doseLoaded) {
      return clarify('No RTDOSE overlay is loaded yet, so there is nothing to show or hide. Load one first?');
    }
    return intent(
      baseIntent(
        'toggle_dose_visibility',
        ['DOSE_VOLUME'],
        { visible: 'toggle' },
        undefined,
        ['an RTDOSE volume is loaded'],
        ['RTDOSE color-wash overlay visibility is toggled'],
        inputType,
        rawInput,
        trimmed,
      ),
    );
  }
  if (STRUCTURES_NOUN_RE.test(text)) {
    if (!context.structuresLoaded) {
      return clarify('No RTSTRUCT contours are loaded yet, so there is nothing to show or hide. Load one first?');
    }
    return intent(
      baseIntent(
        'toggle_structure_visibility',
        ['ALL_ROIS'],
        { visible: 'toggle' },
        undefined,
        ['RTSTRUCT contours are loaded'],
        ['all ROI contour outlines visibility is toggled'],
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
    const nameFragment = m[2].trim().replace(/^(?:the|a)\s+/, '');
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

  // --- bare ROI name, no verb (e.g. just "prostate" or "body"): also
  // toggle, the same well-defined default as bare "dose"/"structures"
  // above. Require at least 3 characters so a stray short word doesn't
  // spuriously substring-match an ROI name.
  {
    const nameFragment = text.replace(/^(?:the|a)\s+/, '');
    if (nameFragment.length >= 3 && context.loadedRoiNames.length > 0) {
      const matches = context.loadedRoiNames.filter((name) => name.toLowerCase().includes(nameFragment));
      if (matches.length === 1) {
        const roiName = matches[0];
        return intent(
          baseIntent(
            'toggle_structure_visibility',
            [roiName],
            { visible: 'toggle' },
            undefined,
            [`ROI "${roiName}" is loaded`],
            [`ROI "${roiName}" contour visibility is toggled`],
            inputType,
            rawInput,
            trimmed,
          ),
        );
      }
      if (matches.length > 1) {
        return clarify(`"${nameFragment}" matches multiple ROIs (${matches.join(', ')}). Which one did you mean?`);
      }
    }
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
    `"${rawInput}" was not recognized as a supported command. ${COMMAND_HELP}`,
  );
}
