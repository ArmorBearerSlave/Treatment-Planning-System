// Captures microphone audio only while explicitly recording (push-to-talk),
// then resamples it to the 16kHz mono PCM Float32Array Whisper expects.
// Captures raw PCM directly via a ScriptProcessorNode rather than
// MediaRecorder + AudioContext.decodeAudioData -- WebM/Opus decode support
// is inconsistent across browsers (observed failing in at least one
// Chromium-based embedded browser), so this avoids an encode/decode round
// trip entirely.
function resampleTo16kHz(input: Float32Array, inputSampleRate: number): Float32Array {
  const targetRate = 16000;
  if (inputSampleRate === targetRate) return input;
  const ratio = inputSampleRate / targetRate;
  const outputLength = Math.floor(input.length / ratio);
  const output = new Float32Array(outputLength);
  for (let i = 0; i < outputLength; i++) {
    const srcIndex = i * ratio;
    const i0 = Math.floor(srcIndex);
    const i1 = Math.min(i0 + 1, input.length - 1);
    const frac = srcIndex - i0;
    output[i] = input[i0] * (1 - frac) + input[i1] * frac;
  }
  return output;
}

export class MicRecorder {
  private stream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private source: MediaStreamAudioSourceNode | null = null;
  private processor: ScriptProcessorNode | null = null;
  private silentGain: GainNode | null = null;
  private chunks: Float32Array[] = [];

  async start(): Promise<void> {
    this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.audioContext = new AudioContext();
    this.source = this.audioContext.createMediaStreamSource(this.stream);
    this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
    this.chunks = [];
    this.processor.onaudioprocess = (event) => {
      this.chunks.push(new Float32Array(event.inputBuffer.getChannelData(0)));
    };
    // ScriptProcessorNode only fires onaudioprocess while connected into a
    // graph that reaches the destination; route through a zero-gain node so
    // nothing is actually played back (no mic monitoring/feedback).
    this.silentGain = this.audioContext.createGain();
    this.silentGain.gain.value = 0;
    this.source.connect(this.processor);
    this.processor.connect(this.silentGain);
    this.silentGain.connect(this.audioContext.destination);
  }

  /** Resolves with 16kHz mono PCM once recording has stopped. */
  async stop(): Promise<Float32Array> {
    if (!this.audioContext) return new Float32Array(0);
    const nativeSampleRate = this.audioContext.sampleRate;
    this.processor?.disconnect();
    this.source?.disconnect();
    this.silentGain?.disconnect();
    this.stream?.getTracks().forEach((track) => track.stop());
    await this.audioContext.close();
    this.audioContext = null;
    this.source = null;
    this.processor = null;
    this.silentGain = null;
    this.stream = null;

    const totalLength = this.chunks.reduce((sum, chunk) => sum + chunk.length, 0);
    const merged = new Float32Array(totalLength);
    let offset = 0;
    for (const chunk of this.chunks) {
      merged.set(chunk, offset);
      offset += chunk.length;
    }
    this.chunks = [];

    return resampleTo16kHz(merged, nativeSampleRate);
  }

  /** Discards in-progress recording (e.g. the user cancelled). */
  cancel(): void {
    this.processor?.disconnect();
    this.source?.disconnect();
    this.silentGain?.disconnect();
    this.stream?.getTracks().forEach((track) => track.stop());
    void this.audioContext?.close();
    this.audioContext = null;
    this.source = null;
    this.processor = null;
    this.silentGain = null;
    this.stream = null;
    this.chunks = [];
  }
}
