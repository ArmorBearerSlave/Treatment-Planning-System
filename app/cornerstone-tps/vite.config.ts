import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    // xmlbuilder2 (pulled in by @kitware/vtk.js, a @cornerstonejs/core
    // dependency, for DICOM SEG/RT export utilities nothing here calls)
    // needs Node's EventEmitter, which Vite externalizes by default in
    // browser builds. The `events` npm package is a browser-compatible
    // polyfill with the same API; aliasing the bare specifier to it is the
    // standard fix for this class of "externalized for browser" crash.
    alias: {
      events: 'events',
    },
  },
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
      // @kitware/vtk.js (a dependency of @cornerstonejs/core) bundles an XML
      // writer (used only by DICOM SEG/RT export utilities nothing here
      // calls) that depends on this CJS package. Forcing it through
      // esbuild's CJS-to-ESM interop here avoids two different failures:
      // raw-served CJS missing named exports, and an eager top-level class
      // evaluation that crashes without that interop shim.
      'xmlbuilder2',
    ],
  },
})
