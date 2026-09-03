import { pipeline, type AutomaticSpeechRecognitionPipeline } from '@huggingface/transformers';

// In-browser Whisper via WebAssembly/ONNX -- no network round-trip per
// utterance and no server component, unlike the browser's built-in
// SpeechRecognition (which streams audio to a cloud service and fails with
// a "network" error offline). The model weights download once from the HF
// hub CDN and are cached by the browser afterwards.
const MODEL_ID = 'Xenova/whisper-tiny.en';

let pipelinePromise: Promise<AutomaticSpeechRecognitionPipeline> | null = null;

export function loadAsrPipeline(onProgress?: (loaded: number, total: number) => void) {
  if (!pipelinePromise) {
    pipelinePromise = pipeline('automatic-speech-recognition', MODEL_ID, {
      // The default "auto" quantized ONNX export for this model is missing
      // scale tensors for this onnxruntime-web version (session creation
      // fails with "Missing required scale ... DequantizeLinear"). fp32 is
      // the full-precision export, which every ONNX Runtime build supports.
      dtype: 'fp32',
      progress_callback: (progress: { status: string; loaded?: number; total?: number }) => {
        if (progress.status === 'progress' && progress.total) {
          onProgress?.(progress.loaded ?? 0, progress.total);
        }
      },
    });
  }
  return pipelinePromise;
}

export async function transcribeAudio(audioSamples: Float32Array): Promise<string> {
  const transcriber = await loadAsrPipeline();
  const result = await transcriber(audioSamples);
  const output = Array.isArray(result) ? result[0] : result;
  return (output?.text ?? '').trim();
}
