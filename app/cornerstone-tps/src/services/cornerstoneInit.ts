import {
  init as coreInit,
  volumeLoader,
  metaData,
  cornerstoneStreamingImageVolumeLoader,
  utilities,
} from '@cornerstonejs/core';
import { init as dicomImageLoaderInit, wadouri } from '@cornerstonejs/dicom-image-loader';
import * as cornerstoneTools from '@cornerstonejs/tools';

let initPromise: Promise<void> | null = null;

/**
 * Memoized on the in-flight promise, not just a boolean: React StrictMode
 * double-invokes effects, so two concurrent callers must share one
 * initialization instead of both racing past a not-yet-true flag and
 * double-registering the decode worker pool.
 */
export function ensureCornerstoneInitialized(): Promise<void> {
  if (!initPromise) {
    initPromise = (async () => {
      await coreInit();
      dicomImageLoaderInit({ maxWebWorkers: 1 });
      cornerstoneTools.init();
      // Use core's own built-in streaming volume loader, not the separate
      // @cornerstonejs/streaming-image-volume-loader package: that package
      // is still on the pre-5.x release line (requires core ^1.86.0) and
      // npm nests an incompatible old copy of core under it, which has its
      // own disconnected metaData registry that never sees providers
      // registered against the top-level core instance.
      volumeLoader.registerVolumeLoader(
        'cornerstoneStreamingImageVolume',
        cornerstoneStreamingImageVolumeLoader as unknown as Parameters<typeof volumeLoader.registerVolumeLoader>[1],
      );
      // Bridges the loader's own NATURALIZED metadata store to core's
      // generic metaData provider registry -- volumes read standard modules
      // (imagePixelModule, imagePlaneModule, ...) through the latter, which
      // has nothing in it for wadouri imageIds until this is registered.
      metaData.addProvider(wadouri.metaData.metaDataProvider);

      // Colormaps are not pre-registered by core.init() -- and importing
      // VTK.js's own preset-list module pulls in an unrelated XML-builder
      // dependency chain that crashes when evaluated in the browser (it
      // uses Node's EventEmitter, which Vite correctly refuses to polyfill).
      // A small hand-defined dose color-wash gradient avoids that entirely.
      utilities.colormap.registerColormap({
        ColorSpace: 'RGB',
        Name: 'dose-rainbow',
        RGBPoints: [
          0.0, 0.0, 0.0, 0.6,
          0.25, 0.0, 0.8, 0.8,
          0.5, 0.0, 0.8, 0.0,
          0.75, 1.0, 1.0, 0.0,
          1.0, 1.0, 0.0, 0.0,
        ],
      });
      // Visually distinct from 'dose-rainbow' (real RTDOSE) so an AI-
      // predicted dose overlay can never be confused with it at a glance.
      utilities.colormap.registerColormap({
        ColorSpace: 'RGB',
        Name: 'dosepred-magenta',
        RGBPoints: [
          0.0, 0.1, 0.0, 0.2,
          0.25, 0.3, 0.0, 0.5,
          0.5, 0.6, 0.0, 0.6,
          0.75, 0.9, 0.2, 0.5,
          1.0, 1.0, 0.6, 0.2,
        ],
      });

      const { PanTool, WindowLevelTool, ZoomTool, StackScrollTool, addTool } = cornerstoneTools;
      addTool(PanTool);
      addTool(WindowLevelTool);
      addTool(ZoomTool);
      addTool(StackScrollTool);
    })();
  }
  return initPromise;
}
