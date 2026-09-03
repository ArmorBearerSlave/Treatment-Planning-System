import { init as coreInit } from '@cornerstonejs/core';
import { init as dicomImageLoaderInit } from '@cornerstonejs/dicom-image-loader';
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

      const { PanTool, WindowLevelTool, ZoomTool, StackScrollTool, addTool } = cornerstoneTools;
      addTool(PanTool);
      addTool(WindowLevelTool);
      addTool(ZoomTool);
      addTool(StackScrollTool);
    })();
  }
  return initPromise;
}
