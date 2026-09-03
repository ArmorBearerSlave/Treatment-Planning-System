import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    // These codec packages ship UMD/CJS-only glue files with no native ESM
    // export. dicom-image-loader's decode worker imports them eagerly (all
    // four, regardless of which transfer syntax is actually in use), and a
    // native `type: module` Worker cannot link a file with no `export`
    // statement -- it fails silently with a sanitized, message-less error
    // and the worker just closes. Forcing esbuild to pre-bundle (and thus
    // ESM-ify) these subpaths fixes it.
    include: [
      '@cornerstonejs/codec-openjpeg/decodewasmjs',
      '@cornerstonejs/codec-openjph/wasmjs',
      '@cornerstonejs/codec-libjpeg-turbo-8bit/decodewasmjs',
      '@cornerstonejs/codec-charls/decodewasmjs',
    ],
  },
})
