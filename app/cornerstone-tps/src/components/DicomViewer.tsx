import { useCallback, useEffect, useRef, useState } from 'react';
import {
  RenderingEngine,
  Enums,
  getRenderingEngine,
  volumeLoader,
  setVolumesForViewports,
  addVolumesToViewports,
  imageLoader,
  metaData,
  utilities,
  geometryLoader,
  type Types,
} from '@cornerstonejs/core';
import { wadouri } from '@cornerstonejs/dicom-image-loader';
import {
  ToolGroupManager,
  Enums as ToolsEnums,
  PanTool,
  WindowLevelTool,
  ZoomTool,
  StackScrollTool,
  segmentation,
} from '@cornerstonejs/tools';
import { ensureCornerstoneInitialized } from '../services/cornerstoneInit';

const RENDERING_ENGINE_ID = 'tps-rendering-engine';
const VIEWPORT_ID = 'tps-volume-viewport';
const TOOL_GROUP_ID = 'tps-tool-group';
const CT_VOLUME_ID = 'cornerstoneStreamingImageVolume:CT_VOLUME';
const DOSE_VOLUME_ID = 'cornerstoneStreamingImageVolume:DOSE_VOLUME';
const RTSTRUCT_SEGMENTATION_ID = 'RTSTRUCT_SEGMENTATION';

// wadouri's metaData.metaDataProvider (the bridge into core's generic
// metaData registry, which volumes read geometry through) reads from
// dataSetCacheManager -- a different, older store than the NATURALIZED
// cache that loadAndCacheImages/loadImageFromNaturalizedMetadata populates.
// Volume creation needs both populated.
async function primeDataSetCache(imageIds: string[]) {
  const uniqueUrls = new Set(imageIds.map((id) => wadouri.parseImageId(id).url));
  await Promise.all(
    Array.from(uniqueUrls).map((url) => wadouri.dataSetCacheManager.load(url, wadouri.loadFileRequest, url)),
  );
}

export function DicomViewer() {
  const elementRef = useRef<HTMLDivElement>(null);
  const [ready, setReady] = useState(false);
  const [ctLoaded, setCtLoaded] = useState(false);
  const [status, setStatus] = useState('Initializing Cornerstone3D...');

  useEffect(() => {
    let cancelled = false;

    async function setup() {
      await ensureCornerstoneInitialized();
      if (cancelled || !elementRef.current) return;

      const renderingEngine = new RenderingEngine(RENDERING_ENGINE_ID);
      const viewportInput: Types.PublicViewportInput = {
        viewportId: VIEWPORT_ID,
        type: Enums.ViewportType.ORTHOGRAPHIC,
        element: elementRef.current,
        defaultOptions: { orientation: Enums.OrientationAxis.AXIAL },
      };
      renderingEngine.enableElement(viewportInput);

      let toolGroup = ToolGroupManager.getToolGroup(TOOL_GROUP_ID);
      if (!toolGroup) {
        toolGroup = ToolGroupManager.createToolGroup(TOOL_GROUP_ID);
      }
      if (toolGroup) {
        toolGroup.addTool(WindowLevelTool.toolName);
        toolGroup.addTool(PanTool.toolName);
        toolGroup.addTool(ZoomTool.toolName);
        toolGroup.addTool(StackScrollTool.toolName);

        toolGroup.setToolActive(WindowLevelTool.toolName, {
          bindings: [{ mouseButton: ToolsEnums.MouseBindings.Primary }],
        });
        toolGroup.setToolActive(PanTool.toolName, {
          bindings: [{ mouseButton: ToolsEnums.MouseBindings.Auxiliary }],
        });
        toolGroup.setToolActive(ZoomTool.toolName, {
          bindings: [{ mouseButton: ToolsEnums.MouseBindings.Secondary }],
        });
        toolGroup.setToolActive(StackScrollTool.toolName, {
          bindings: [{ mouseButton: ToolsEnums.MouseBindings.Wheel }],
        });

        toolGroup.addViewport(VIEWPORT_ID, RENDERING_ENGINE_ID);
      }

      setStatus('Load a local CT series to begin.');
      setReady(true);
    }

    setup();

    return () => {
      cancelled = true;
      const engine = getRenderingEngine(RENDERING_ENGINE_ID);
      engine?.destroy();
      ToolGroupManager.destroyToolGroup(TOOL_GROUP_ID);
    };
  }, []);

  const onCtFilesSelected = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setStatus(`Loading ${files.length} CT file(s)...`);

    // fileManager.add already returns a fully-scoped id, e.g. "dicomfile:0" --
    // do not wrap it in an extra "wadouri:" prefix, or parseImageId reads the
    // whole thing as a "wadouri" (i.e. XHR/http) scheme instead of a local file.
    const imageIds = Array.from(files).map((file) => wadouri.fileManager.add(file));

    const renderingEngine = getRenderingEngine(RENDERING_ENGINE_ID);
    if (!renderingEngine) return;

    // Volume creation needs each image's metadata (dimensions, spacing,
    // orientation) synchronously up front. Local wadouri files have no
    // metadata until their header is actually parsed, which only happens as
    // a side effect of loading the image -- so every image must be loaded
    // once here before the volume loader can compute the volume's geometry.
    await Promise.all(imageLoader.loadAndCacheImages(imageIds));
    await primeDataSetCache(imageIds);

    const volume = await volumeLoader.createAndCacheVolume(CT_VOLUME_ID, { imageIds });
    volume.load();
    await setVolumesForViewports(renderingEngine, [{ volumeId: CT_VOLUME_ID }], [VIEWPORT_ID]);
    const viewport = renderingEngine.getViewport(VIEWPORT_ID) as Types.IVolumeViewport;
    // Cornerstone3D's default volume opacity is a flat 1.0 across the whole
    // range. In the joint multi-volume raycast this saturates ray alpha at
    // the very first sample, so a later-added overlay volume (e.g. RTDOSE)
    // never contributes any visible color no matter its own opacity. Scaling
    // down the existing (correctly auto-windowed) opacity function in place
    // -- rather than replacing voiRange/colormap outright, which broke the
    // color mapping for this dataset's non-standard intensity range --
    // leaves room for the dose overlay without changing how the CT looks.
    // getActor() expects the actor's own UID, not the volumeId, so look it
    // up by referencedId from the actor list instead.
    const ctActor = viewport.getActors().find((a) => a.referencedId === CT_VOLUME_ID)?.actor;
    if (ctActor) utilities.colormap.updateOpacity(ctActor, 0.8);
    viewport.resetCamera();
    renderingEngine.render();

    setCtLoaded(true);
    setStatus(`Loaded ${imageIds.length} CT image(s). Left-drag: window/level, middle-drag: pan, right-drag: zoom, wheel: scroll.`);
  }, []);

  const onDoseFileSelected = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    setStatus('Loading RTDOSE...');

    const baseId = wadouri.fileManager.add(file);
    // RTDOSE is a single multi-frame file. Frame numbers in a wadouri
    // imageId are 1-based (parseImageId subtracts 1 internally), so frame=1
    // is the first frame -- one imageId per frame, all sharing the same
    // underlying file/fileManager index.
    const dataSet = await wadouri.dataSetCacheManager.load(baseId, wadouri.loadFileRequest, baseId)
      .catch(() => null);
    const frameCount = dataSet ? dataSet.intString('x00280008') : null;
    const numberOfFrames = frameCount ?? 1;
    const doseGridScaling = dataSet ? parseFloat(dataSet.string('x3004000e') || '1') : 1;

    const imageIds = Array.from({ length: numberOfFrames }, (_, i) => `${baseId}?frame=${i + 1}`);

    // RTDOSE stores one ImagePositionPatient for the whole multi-frame
    // dataset, with each frame's actual position given by an offset along
    // the slice normal in GridFrameOffsetVector -- wadouri's own metadata
    // provider does not compute this, so every frame reports the identical
    // position, and the volume loader cannot tell the 96 frames apart in Z.
    // A higher-priority provider overrides imagePlaneModule for these
    // imageIds specifically, leaving everything else (CT) untouched.
    if (dataSet) {
      const basePosition = dataSet.string('x00200032')?.split('\\').map(Number) ?? [0, 0, 0];
      const orientation = dataSet.string('x00200037')?.split('\\').map(Number) ?? [1, 0, 0, 0, 1, 0];
      const rowCosines: [number, number, number] = [orientation[0], orientation[1], orientation[2]];
      const colCosines: [number, number, number] = [orientation[3], orientation[4], orientation[5]];
      const normal: [number, number, number] = [
        rowCosines[1] * colCosines[2] - rowCosines[2] * colCosines[1],
        rowCosines[2] * colCosines[0] - rowCosines[0] * colCosines[2],
        rowCosines[0] * colCosines[1] - rowCosines[1] * colCosines[0],
      ];
      const frameOffsets = (dataSet.string('x3004000c')?.split('\\').map(Number)) ?? imageIds.map((_, i) => i);
      const rows = dataSet.uint16('x00280010');
      const columns = dataSet.uint16('x00280011');
      const pixelSpacing = dataSet.string('x00280030')?.split('\\').map(Number) ?? [1, 1];
      const frameOfReferenceUID = dataSet.string('x00200052');
      const sliceThickness = parseFloat(dataSet.string('x00180050') || '0') || undefined;

      const doseImageIdSet = new Set(imageIds);
      metaData.addProvider((type: string, imageId: string) => {
        if (type !== 'imagePlaneModule' || !doseImageIdSet.has(imageId)) return undefined;
        const frameIndex = Number(imageId.split('?frame=')[1]) - 1;
        const offset = frameOffsets[frameIndex] ?? frameIndex;
        const imagePositionPatient: [number, number, number] = [
          basePosition[0] + normal[0] * offset,
          basePosition[1] + normal[1] * offset,
          basePosition[2] + normal[2] * offset,
        ];
        return {
          frameOfReferenceUID,
          rows,
          columns,
          imageOrientationPatient: orientation,
          rowCosines,
          columnCosines: colCosines,
          imagePositionPatient,
          sliceThickness,
          pixelSpacing,
          rowPixelSpacing: pixelSpacing[0],
          columnPixelSpacing: pixelSpacing[1],
        };
      }, 1);
    }

    const renderingEngine = getRenderingEngine(RENDERING_ENGINE_ID);
    if (!renderingEngine) return;

    await Promise.all(imageLoader.loadAndCacheImages(imageIds));
    await primeDataSetCache(imageIds);

    const doseVolume = await volumeLoader.createAndCacheVolume(DOSE_VOLUME_ID, { imageIds });
    doseVolume.load();
    // addVolumesToViewports defaults a secondary volume's actor to invisible.
    await addVolumesToViewports(
      renderingEngine,
      [{ volumeId: DOSE_VOLUME_ID, visibility: true }],
      [VIEWPORT_ID],
    );

    const viewport = renderingEngine.getViewport(VIEWPORT_ID) as Types.IVolumeViewport;
    // Verified via direct voxelManager inspection: cornerstone's image
    // loader already applies DoseGridScaling when decoding pixel data, so
    // volume voxel values are already in Gy (max sampled ~70, matching the
    // expected ~80 Gy plan max) -- NOT raw unscaled integers. An earlier
    // version of this code converted maxDoseGy back to "raw" units
    // (dividing by doseGridScaling, ~4.89 billion) and used that for the
    // opacity/voiRange domain, which put every real voxel value into the
    // flat opacity=0 region of the transfer function, making the whole
    // overlay invisible despite every other setting being correct.
    const maxDoseGy = 80;
    // A flat colormap.opacity number does not get rescaled to the volume's
    // actual value range the way the color transfer function does -- it
    // was observed applying only across a tiny sliver of the range, making
    // every real voxel invisible. opacityMapping takes explicit
    // (value, opacity) points, which must be given in the same units as
    // voiRange (Gy, here).
    viewport.setProperties(
      {
        colormap: {
          name: 'dose-rainbow',
          opacityMapping: [
            { value: 0, opacity: 0 },
            { value: maxDoseGy * 0.1, opacity: 0 },
            { value: maxDoseGy * 0.15, opacity: 0.5 },
            { value: maxDoseGy, opacity: 0.7 },
          ],
        },
        voiRange: { lower: 0, upper: maxDoseGy },
      },
      DOSE_VOLUME_ID,
    );
    viewport.render();

    setStatus(`Loaded RTDOSE (${numberOfFrames} frames, scaling ${doseGridScaling.toExponential(3)} Gy/unit) as a color-wash overlay.`);
  }, []);

  const onRtstructFileSelected = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    setStatus('Loading RTSTRUCT...');

    const fileId = wadouri.fileManager.add(file);
    const dataSet = await wadouri.dataSetCacheManager.load(fileId, wadouri.loadFileRequest, fileId);

    const roiNames = new Map<number, string>();
    for (const item of dataSet.elements['x30060020']?.items ?? []) {
      const ds = item.dataSet;
      if (!ds) continue;
      roiNames.set(ds.intString('x30060022') ?? -1, ds.string('x30060026') ?? '');
    }
    const frameOfReferenceUID = dataSet.string('x00200052') ?? '';

    // One geometryId (contour set) per ROI, each carrying its own
    // segmentIndex/color -- referenced together by a single segmentation.
    const geometryIds: string[] = [];
    const segmentColors: Array<{ segmentIndex: number; color: Types.Point3 }> = [];
    let segmentIndex = 1;
    for (const item of dataSet.elements['x30060039']?.items ?? []) {
      const ds = item.dataSet;
      if (!ds) continue;
      const referencedRoiNumber = ds.intString('x30060084') ?? -1;
      const colorStr = ds.string('x3006002a');
      const rgb = colorStr?.split('\\').map(Number);
      const color: Types.Point3 = rgb && rgb.length === 3 ? [rgb[0], rgb[1], rgb[2]] : [255, 255, 0];

      const contourData: Types.ContourData[] = [];
      for (const contourItem of ds.elements['x30060040']?.items ?? []) {
        const cds = contourItem.dataSet;
        if (!cds) continue;
        const dataStr = cds.string('x30060050');
        if (!dataStr) continue;
        const nums = dataStr.split('\\').map(Number);
        const points: Types.Point3[] = [];
        for (let i = 0; i + 2 < nums.length; i += 3) points.push([nums[i], nums[i + 1], nums[i + 2]]);
        if (points.length > 0) {
          contourData.push({ points, type: Enums.ContourType.CLOSED_PLANAR, color, segmentIndex });
        }
      }
      if (contourData.length === 0) continue;

      const geometryId = `rtstruct-roi-${referencedRoiNumber}`;
      geometryLoader.createAndCacheGeometry(geometryId, {
        type: Enums.GeometryType.CONTOUR,
        geometryData: { id: geometryId, data: contourData, frameOfReferenceUID, color },
      });
      geometryIds.push(geometryId);
      segmentColors.push({ segmentIndex, color });
      segmentIndex += 1;
    }

    segmentation.addSegmentations([
      {
        segmentationId: RTSTRUCT_SEGMENTATION_ID,
        representation: { type: ToolsEnums.SegmentationRepresentations.Contour, data: { geometryIds } },
      },
    ]);
    segmentation.addContourRepresentationToViewport(VIEWPORT_ID, [
      { segmentationId: RTSTRUCT_SEGMENTATION_ID },
    ]);
    // addContourRepresentationToViewport builds the geometry-derived
    // annotations asynchronously; the per-segment color LUT entries it
    // creates don't exist yet if set immediately afterwards.
    await new Promise((resolve) => setTimeout(resolve, 0));
    // Outline only (no fill) so the CT/dose underneath stays visible, and
    // each ROI keeps its own DICOM-authored color rather than a shared
    // default (contour geometry's own `color` field is cosmetic metadata
    // only -- rendering reads a separate per-segment color LUT).
    segmentation.config.style.setStyle(
      { type: ToolsEnums.SegmentationRepresentations.Contour },
      { renderFill: false, outlineWidth: 2 },
    );
    for (const { segmentIndex: idx, color } of segmentColors) {
      segmentation.config.color.setSegmentIndexColor(VIEWPORT_ID, RTSTRUCT_SEGMENTATION_ID, idx, [
        color[0],
        color[1],
        color[2],
        255,
      ]);
    }

    setStatus(`Loaded RTSTRUCT with ${geometryIds.length} ROI contour(s).`);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <label style={{ fontFamily: 'sans-serif', fontSize: '0.85rem' }}>
          CT series:{' '}
          <input
            type="file"
            multiple
            accept=".dcm,application/dicom"
            disabled={!ready}
            onChange={(e) => onCtFilesSelected(e.target.files)}
          />
        </label>
        <label style={{ fontFamily: 'sans-serif', fontSize: '0.85rem' }}>
          RTDOSE:{' '}
          <input
            type="file"
            accept=".dcm,application/dicom"
            disabled={!ready || !ctLoaded}
            onChange={(e) => onDoseFileSelected(e.target.files)}
          />
        </label>
        <label style={{ fontFamily: 'sans-serif', fontSize: '0.85rem' }}>
          RTSTRUCT:{' '}
          <input
            type="file"
            accept=".dcm,application/dicom"
            disabled={!ready || !ctLoaded}
            onChange={(e) => onRtstructFileSelected(e.target.files)}
          />
        </label>
      </div>
      <p style={{ fontFamily: 'sans-serif', fontSize: '0.9rem' }}>{status}</p>
      <div
        ref={elementRef}
        style={{
          width: '512px',
          height: '512px',
          backgroundColor: '#000',
        }}
      />
    </div>
  );
}
