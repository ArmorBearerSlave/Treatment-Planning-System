import { useCallback, useRef, useState } from 'react';
import { COMMAND_CATEGORIES, parseCommand } from '../services/nli/parser';
import { transcribeAudio } from '../services/nli/asr';
import { MicRecorder } from '../services/nli/recorder';
import type { AuditEntry, CompiledIntent, InputType, ParserContext } from '../services/nli/types';

// NLI-001..008 (spec/risks.yaml): typed text and user-initiated
// push-to-talk speech only (no background listening); every actionable
// request is compiled into an inspectable typed intent and shown as a
// structured read-back before any state-changing execution; speech
// transcripts get an explicit confirmation step of their own; nothing is
// ever executed directly from a spoken "yes" (no voice-only signature);
// every step is recorded in an in-memory audit ledger. Speech-to-text runs
// fully in-browser via a local Whisper model (WASM/ONNX) rather than the
// browser's built-in SpeechRecognition, which streams audio to a cloud
// service and fails outright without network access to it.

interface NliCommandBarProps {
  context: ParserContext;
  onExecute: (intent: CompiledIntent) => void;
}

type Stage =
  | { kind: 'idle' }
  | { kind: 'confirm_transcript'; rawInput: string; transcript: string }
  | { kind: 'confirm_intent'; intent: CompiledIntent }
  | { kind: 'clarification'; question: string };

function describeIntent(intent: CompiledIntent): string {
  const objects = intent.objects.join(', ');
  const params = Object.entries(intent.parameters)
    .map(([k, v]) => `${k}=${v}`)
    .join(', ');
  return `${intent.action} on [${objects}]${params ? ` (${params})` : ''}`;
}

export function NliCommandBar({ context, onExecute }: NliCommandBarProps) {
  const [text, setText] = useState('');
  const [stage, setStage] = useState<Stage>({ kind: 'idle' });
  const [listening, setListening] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [ledger, setLedger] = useState<AuditEntry[]>([]);
  const micRecorderRef = useRef<MicRecorder | null>(null);
  const speechSupported = typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia;

  const appendLedger = useCallback((entry: Omit<AuditEntry, 'id' | 'timestamp'>) => {
    setLedger((prev) => [
      { id: crypto.randomUUID(), timestamp: new Date().toISOString(), ...entry },
      ...prev,
    ]);
  }, []);

  const runParse = useCallback(
    (rawInput: string, confirmedTranscript: string, inputType: InputType) => {
      const result = parseCommand(confirmedTranscript, inputType, context);
      if (result.kind === 'clarification') {
        appendLedger({
          inputType,
          rawInput,
          confirmedTranscript,
          clarificationQuestion: result.question,
          confirmed: false,
          corrections: [],
        });
        setStage({ kind: 'clarification', question: result.question });
        return;
      }
      setStage({ kind: 'confirm_intent', intent: result.intent });
    },
    [context, appendLedger],
  );

  const onTextSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const raw = text.trim();
      if (!raw) return;
      setText('');
      runParse(raw, raw, 'text');
    },
    [text, runParse],
  );

  const startListening = useCallback(async () => {
    // Ignore a second mousedown/touchstart while already recording (e.g. a
    // stray repeat event) rather than leaking a second recorder instance.
    if (micRecorderRef.current) return;
    setSpeechError(null);
    const recorder = new MicRecorder();
    micRecorderRef.current = recorder;
    try {
      await recorder.start();
      setListening(true);
    } catch (err) {
      // getUserMedia rejects on denied/unavailable microphone permission --
      // surface it instead of silently reverting to "Hold to talk" with no
      // explanation, which is indistinguishable from "broken".
      micRecorderRef.current = null;
      setListening(false);
      setSpeechError(
        err instanceof Error && err.name === 'NotAllowedError'
          ? 'Microphone permission was denied. Allow microphone access for this site and try again.'
          : 'Could not access the microphone.',
      );
    }
  }, []);

  // Explicit user-initiated start/stop only -- never left running in the
  // background (NLI-001). Releasing the button stops recording immediately
  // and transcription (local Whisper inference) begins right away.
  const stopListening = useCallback(async () => {
    const recorder = micRecorderRef.current;
    if (!recorder) return;
    micRecorderRef.current = null;
    setListening(false);
    setTranscribing(true);
    try {
      const samples = await recorder.stop();
      if (samples.length === 0) {
        setSpeechError('No audio was captured. Hold the button, wait a moment, then speak.');
        return;
      }
      const transcript = await transcribeAudio(samples);
      if (!transcript) {
        setSpeechError('No speech was detected in the recording. Try again and speak clearly.');
        return;
      }
      setStage({ kind: 'confirm_transcript', rawInput: transcript, transcript });
    } catch (err) {
      // The first use of the local Whisper model downloads and compiles it,
      // which can fail (offline with nothing cached yet, WASM unsupported);
      // surface that distinctly from a plain "no speech" result.
      setSpeechError(err instanceof Error ? `Local transcription failed: ${err.message}` : 'Local transcription failed.');
    } finally {
      setTranscribing(false);
    }
  }, []);

  const confirmTranscript = useCallback(
    (editedTranscript: string) => {
      if (stage.kind !== 'confirm_transcript') return;
      runParse(stage.rawInput, editedTranscript, 'speech');
    },
    [stage, runParse],
  );

  const confirmIntent = useCallback(() => {
    if (stage.kind !== 'confirm_intent') return;
    const { intent } = stage;
    try {
      onExecute(intent);
      appendLedger({
        inputType: intent.provenance.inputType,
        rawInput: intent.provenance.rawInput,
        confirmedTranscript: intent.provenance.confirmedTranscript,
        compiledIntent: intent,
        preview: describeIntent(intent),
        confirmed: true,
        executionResult: 'executed',
        corrections: [],
      });
    } catch (err) {
      appendLedger({
        inputType: intent.provenance.inputType,
        rawInput: intent.provenance.rawInput,
        confirmedTranscript: intent.provenance.confirmedTranscript,
        compiledIntent: intent,
        preview: describeIntent(intent),
        confirmed: true,
        executionResult: 'error',
        errorMessage: err instanceof Error ? err.message : String(err),
        corrections: [],
      });
    }
    setStage({ kind: 'idle' });
  }, [stage, onExecute, appendLedger]);

  const cancelIntent = useCallback(() => {
    if (stage.kind !== 'confirm_intent') return;
    const { intent } = stage;
    appendLedger({
      inputType: intent.provenance.inputType,
      rawInput: intent.provenance.rawInput,
      confirmedTranscript: intent.provenance.confirmedTranscript,
      compiledIntent: intent,
      preview: describeIntent(intent),
      confirmed: false,
      executionResult: 'cancelled',
      corrections: [],
    });
    setStage({ kind: 'idle' });
  }, [stage, appendLedger]);

  return (
    <div style={{ fontFamily: 'sans-serif', fontSize: '0.85rem', border: '1px solid #444', borderRadius: 4, padding: '0.5rem' }}>
      <form onSubmit={onTextSubmit} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder='Type a command, e.g. "next slice" or "hide dose"'
          style={{ flex: 1 }}
        />
        <button type="submit">Send</button>
        {speechSupported && (
          <button
            type="button"
            disabled={transcribing}
            onMouseDown={startListening}
            onMouseUp={stopListening}
            onMouseLeave={stopListening}
            onTouchStart={startListening}
            onTouchEnd={stopListening}
          >
            {transcribing ? 'Transcribing locally...' : listening ? 'Listening... (release to stop)' : 'Hold to talk'}
          </button>
        )}
      </form>

      <details style={{ marginTop: '0.5rem' }}>
        <summary>Commands</summary>
        <ul style={{ paddingLeft: '1rem' }}>
          {COMMAND_CATEGORIES.map((category) => (
            <li key={category.label} style={{ marginBottom: '0.25rem' }}>
              {category.label}:{' '}
              {category.examples.map((example, i) => (
                <span key={example}>
                  {i > 0 && ', '}
                  <button
                    type="button"
                    onClick={() => setText(example)}
                    style={{ font: 'inherit', padding: '0 0.25rem' }}
                  >
                    {example}
                  </button>
                </span>
              ))}
            </li>
          ))}
        </ul>
      </details>

      {speechError && (
        <div style={{ marginTop: '0.5rem', color: '#c77' }}>
          {speechError}
          <button type="button" onClick={() => setSpeechError(null)} style={{ marginLeft: '0.5rem' }}>
            Dismiss
          </button>
        </div>
      )}

      {stage.kind === 'confirm_transcript' && (
        <TranscriptConfirm
          transcript={stage.transcript}
          onConfirm={confirmTranscript}
          onDiscard={() => setStage({ kind: 'idle' })}
        />
      )}

      {stage.kind === 'clarification' && (
        <div style={{ marginTop: '0.5rem', color: '#c77' }}>
          {stage.question}
          <button type="button" onClick={() => setStage({ kind: 'idle' })} style={{ marginLeft: '0.5rem' }}>
            Dismiss
          </button>
        </div>
      )}

      {stage.kind === 'confirm_intent' && (
        <IntentReadback intent={stage.intent} onConfirm={confirmIntent} onCancel={cancelIntent} />
      )}

      {ledger.length > 0 && (
        <details style={{ marginTop: '0.5rem' }}>
          <summary>Audit ledger ({ledger.length})</summary>
          <ul style={{ maxHeight: 160, overflowY: 'auto', paddingLeft: '1rem' }}>
            {ledger.map((entry) => (
              <li key={entry.id}>
                [{entry.timestamp}] {entry.inputType}: "{entry.rawInput}" -&gt;{' '}
                {entry.clarificationQuestion
                  ? `clarification requested`
                  : `${entry.executionResult ?? 'pending'}${entry.preview ? `: ${entry.preview}` : ''}`}
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}

function TranscriptConfirm({
  transcript,
  onConfirm,
  onDiscard,
}: {
  transcript: string;
  onConfirm: (edited: string) => void;
  onDiscard: () => void;
}) {
  const [edited, setEdited] = useState(transcript);
  return (
    <div style={{ marginTop: '0.5rem', border: '1px dashed #888', padding: '0.5rem' }}>
      <div>Confirm what you said before it is parsed into a command:</div>
      <input type="text" value={edited} onChange={(e) => setEdited(e.target.value)} style={{ width: '100%', marginTop: '0.25rem' }} />
      <div style={{ marginTop: '0.25rem' }}>
        <button type="button" onClick={() => onConfirm(edited)}>Use this transcript</button>
        <button type="button" onClick={onDiscard} style={{ marginLeft: '0.5rem' }}>Discard</button>
      </div>
    </div>
  );
}

function IntentReadback({
  intent,
  onConfirm,
  onCancel,
}: {
  intent: CompiledIntent;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <div style={{ marginTop: '0.5rem', border: '1px solid #6a6', padding: '0.5rem' }}>
      <div>
        <strong>This will:</strong> {describeIntent(intent)}
      </div>
      <div>Objects: {intent.objects.join(', ')}</div>
      <div>Preconditions: {intent.preconditions.join('; ') || 'none'}</div>
      <div>Expected outcome: {intent.expectedOutputs.join('; ')}</div>
      <div>Affected approval state: {intent.affectedApprovalState} (this prototype has no clinical approval workflow)</div>
      <div>Source: {intent.provenance.inputType} input "{intent.provenance.rawInput}"</div>
      <div style={{ marginTop: '0.25rem' }}>
        <button type="button" onClick={onConfirm}>Confirm</button>
        <button type="button" onClick={onCancel} style={{ marginLeft: '0.5rem' }}>Cancel</button>
      </div>
    </div>
  );
}
