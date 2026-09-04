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
import { NliCommandBar } from './NliCommandBar';
import type { CompiledIntent } from '../services/nli/types';

const RENDERING_ENGINE_ID = 'tps-rendering-engine';
const VIEWPORT_ID = 'tps-volume-viewport';
const TOOL_GROUP_ID = 'tps-tool-group';
const CT_VOLUME_ID = 'cornerstoneStreamingImageVolume:CT_VOLUME';
const DOSE_VOLUME_ID = 'cornerstoneStreamingImageVolume:DOSE_VOLUME';
const RTSTRUCT_SEGMENTATION_ID = 'RTSTRUCT_SEGMENTATION';
const AUTOSEG_SEGMENTATION_ID = 'AUTOSEG_SEGMENTATION';
const DOSEPRED_VOLUME_ID = 'DOSEPRED_VOLUME';
// Technical feasibility spike only: an unreviewed TotalSegmentator proposal
// service running on the DGX Spark, not a validated NL-TPS component.
const AUTOSEG_SERVICE_URL = 'http://192.168.1.165:8100/segment';
// Technical feasibility spike only: a 3D U-Net trained on 10 synthetic
// cases, not a validated dose-prediction model.
const DOSEPRED_SERVICE_URL = 'http://192.168.1.165:8101/predict_dose';

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
  const [doseLoaded, setDoseLoaded] = useState(false);
  const [structuresLoaded, setStructuresLoaded] = useState(false);
  const [loadedRoiNames, setLoadedRoiNames] = useState<string[]>([]);
  const [totalSlices, setTotalSlices] = useState(0);
  const [autoSegStatus, setAutoSegStatus] = useState<'idle' | 'running' | 'error'>('idle');
  const [autoSegLoaded, setAutoSegLoaded] = useState(false);
  const [dosePredStatus, setDosePredStatus] = useState<'idle' | 'running' | 'error'>('idle');
  const [dosePredLoaded, setDosePredLoaded] = useState(false);
  const roiNameToSegmentIndexRef = useRef<Map<string, number>>(new Map());
  const ctFilesRef = useRef<File[]>([]);
  const rtstructFileRef = useRef<File | null>(null);
  const ctFrameOfReferenceUidRef = useRef('');

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
    ctFilesRef.current = Array.from(files);

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
    ctFrameOfReferenceUidRef.current = metaData.get('imagePlaneModule', imageIds[0])?.frameOfReferenceUID ?? '';

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
    setTotalSlices(viewport.getNumberOfSlices());
    setStatus(`Loaded ${imageIds.length} CT image(s). Left-drag: window/level, middle-drag: pan, right-drag: zoom, wheel: scroll.`);
  }, []);

  const executeIntent = useCallback((intent: CompiledIntent) => {
    const renderingEngine = getRenderingEngine(RENDERING_ENGINE_ID);
    if (!renderingEngine) throw new Error('Viewer is not initialized.');
    const viewport = renderingEngine.getViewport(VIEWPORT_ID) as Types.IVolumeViewport;
    const contourSpecifier = { segmentationId: RTSTRUCT_SEGMENTATION_ID, type: ToolsEnums.SegmentationRepresentations.Contour };

    switch (intent.action) {
      case 'navigate_slice': {
        const { targetSliceIndex, deltaSlices } = intent.parameters;
        if (typeof targetSliceIndex === 'number') {
          viewport.scroll(targetSliceIndex - viewport.getSliceIndex());
        } else if (typeof deltaSlices === 'number') {
          viewport.scroll(deltaSlices);
        }
        renderingEngine.render();
        break;
      }
      case 'toggle_dose_visibility': {
        const doseActor = viewport.getActors().find((a) => a.referencedId === DOSE_VOLUME_ID)?.actor as
          | { getVisibility(): boolean; setVisibility(visible: boolean): void }
          | undefined;
        if (!doseActor) throw new Error('RTDOSE volume actor not found.');
        const requested = intent.parameters.visible;
        const nextVisible = requested === 'toggle' ? !doseActor.getVisibility() : Boolean(requested);
        doseActor.setVisibility(nextVisible);
        renderingEngine.render();
        break;
      }
      case 'toggle_structure_visibility': {
        const requested = intent.parameters.visible;
        const target = intent.objects[0];
        if (target === 'ALL_ROIS') {
          const current = segmentation.config.visibility.getSegmentationRepresentationVisibility(VIEWPORT_ID, contourSpecifier) ?? true;
          const nextVisible = requested === 'toggle' ? !current : Boolean(requested);
          segmentation.config.visibility.setSegmentationRepresentationVisibility(VIEWPORT_ID, contourSpecifier, nextVisible);
        } else {
          const segmentIndex = roiNameToSegmentIndexRef.current.get(target);
          if (segmentIndex === undefined) throw new Error(`Unknown ROI "${target}".`);
          const current = segmentation.config.visibility.getSegmentIndexVisibility(VIEWPORT_ID, contourSpecifier, segmentIndex);
          const nextVisible = requested === 'toggle' ? !current : Boolean(requested);
          segmentation.config.visibility.setSegmentIndexVisibility(VIEWPORT_ID, contourSpecifier, segmentIndex, nextVisible);
        }
        renderingEngine.render();
        break;
      }
      case 'reset_view': {
        viewport.resetCamera();
        renderingEngine.render();
        break;
      }
      case 'zoom': {
        const { direction, factor } = intent.parameters;
        const camera = viewport.getCamera();
        const scale = typeof factor === 'number' ? factor : 1.5;
        const parallelScale = camera.parallelScale ?? 1;
        const nextScale = direction === 'in' ? parallelScale / scale : parallelScale * scale;
        viewport.setCamera({ parallelScale: nextScale });
        renderingEngine.render();
        break;
      }
    }
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

    setDoseLoaded(true);
    setStatus(`Loaded RTDOSE (${numberOfFrames} frames, scaling ${doseGridScaling.toExponential(3)} Gy/unit) as a color-wash overlay.`);
  }, []);

  const onRtstructFileSelected = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    rtstructFileRef.current = files[0];
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
    const segmentColors: Array<{ segmentIndex: number; color: Types.Point3; name: string }> = [];
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
      segmentColors.push({ segmentIndex, color, name: roiNames.get(referencedRoiNumber) ?? `ROI ${referencedRoiNumber}` });
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

    roiNameToSegmentIndexRef.current = new Map(segmentColors.map(({ name, segmentIndex: idx }) => [name, idx]));
    setLoadedRoiNames(segmentColors.map(({ name }) => name));
    setStructuresLoaded(true);
    setStatus(`Loaded RTSTRUCT with ${geometryIds.length} ROI contour(s).`);
  }, []);

  const onLoadNativeTrainingContours = useCallback(async () => {
    if (!ctLoaded) return;
    const response = await fetch('/sample-data/VCT-PROSTATE-001/RT/RTSTRUCT_XCAT_LABELS.dcm');
    if (!response.ok) throw new Error(`native training RTSTRUCT returned HTTP ${response.status}`);
    const blob = await response.blob();
    const transfer = new DataTransfer();
    transfer.items.add(new File([blob], 'RTSTRUCT_XCAT_LABELS.dcm', { type: 'application/dicom' }));
    await onRtstructFileSelected(transfer.files);
  }, [ctLoaded, onRtstructFileSelected]);

  const onRunAutoSegmentation = useCallback(async () => {
    if (ctFilesRef.current.length === 0) return;
    setAutoSegStatus('running');
    setStatus('Running AI auto-segmentation (TotalSegmentator, unverified proposal, ~1-2 min)...');
    try {
      const formData = new FormData();
      for (const file of ctFilesRef.current) formData.append('files', file, file.name);
      const response = await fetch(AUTOSEG_SERVICE_URL, { method: 'POST', body: formData });
      if (!response.ok) throw new Error(`auto-segmentation service returned HTTP ${response.status}`);
      const result = (await response.json()) as {
        rois: Array<{ name: string; color: [number, number, number]; contours: Types.Point3[][] }>;
        model: string;
        unverified: boolean;
      };

      const renderingEngine = getRenderingEngine(RENDERING_ENGINE_ID);
      if (!renderingEngine) throw new Error('viewer is not initialized');

      const geometryIds: string[] = [];
      const segmentColors: Array<{ segmentIndex: number; color: Types.Point3 }> = [];
      let segmentIndex = 1;
      for (const roi of result.rois) {
        const contourData: Types.ContourData[] = roi.contours.map((points) => ({
          points,
          type: Enums.ContourType.CLOSED_PLANAR,
          color: roi.color,
          segmentIndex,
        }));
        const geometryId = `autoseg-roi-${roi.name}`;
        geometryLoader.createAndCacheGeometry(geometryId, {
          type: Enums.GeometryType.CONTOUR,
          geometryData: {
            id: geometryId,
            data: contourData,
            frameOfReferenceUID: ctFrameOfReferenceUidRef.current,
            color: roi.color,
            segmentIndex,
          },
        });
        geometryIds.push(geometryId);
        segmentColors.push({ segmentIndex, color: roi.color });
        segmentIndex += 1;
      }

      if (geometryIds.length === 0) {
        setAutoSegStatus('idle');
        setStatus('Auto-segmentation returned no structures above the noise threshold.');
        return;
      }

      // Allow a clean re-run: discard any previous AI proposal first.
      try {
        segmentation.removeSegmentation(AUTOSEG_SEGMENTATION_ID);
      } catch {
        // nothing to remove on the first run
      }

      segmentation.addSegmentations([
        {
          segmentationId: AUTOSEG_SEGMENTATION_ID,
          representation: {
            type: ToolsEnums.SegmentationRepresentations.Contour,
            data: { geometryIds, annotationUIDsMap: new Map() },
          },
        },
      ]);
      segmentation.addContourRepresentationToViewport(VIEWPORT_ID, [{ segmentationId: AUTOSEG_SEGMENTATION_ID }]);
      await new Promise((resolve) => setTimeout(resolve, 0));
      // Dashed outline (vs. the real RTSTRUCT's solid outline) so this
      // unreviewed AI proposal can never be visually mistaken for a
      // clinician-authored contour.
      segmentation.config.style.setStyle(
        { segmentationId: AUTOSEG_SEGMENTATION_ID, type: ToolsEnums.SegmentationRepresentations.Contour },
        { renderFill: false, outlineWidth: 2, outlineDash: '4,4' },
      );
      for (const { segmentIndex: idx, color } of segmentColors) {
        segmentation.config.color.setSegmentIndexColor(VIEWPORT_ID, AUTOSEG_SEGMENTATION_ID, idx, [
          color[0],
          color[1],
          color[2],
          255,
        ]);
      }

      renderingEngine.render();
      setAutoSegStatus('idle');
      setAutoSegLoaded(true);
      setStatus(
        `AI auto-segmentation proposed ${result.rois.length} structure(s) via ${result.model} -- ` +
          'UNVERIFIED, shown with a dashed outline. Review before relying on it for anything.',
      );
    } catch (err) {
      setAutoSegStatus('error');
      setStatus(`Auto-segmentation failed: ${err instanceof Error ? err.message : String(err)}`);
    }
  }, []);

  const onDiscardAutoSegmentation = useCallback(() => {
    segmentation.removeSegmentation(AUTOSEG_SEGMENTATION_ID);
    const renderingEngine = getRenderingEngine(RENDERING_ENGINE_ID);
    renderingEngine?.render();
    setAutoSegLoaded(false);
    setStatus('Discarded the AI auto-segmentation proposal.');
  }, []);

  const onRunDosePrediction = useCallback(async () => {
    if (ctFilesRef.current.length === 0 || !rtstructFileRef.current) return;
    setDosePredStatus('running');
    setStatus('Running AI dose prediction (3D U-Net trained on 10 synthetic cases, unverified)...');
    try {
      const formData = new FormData();
      for (const file of ctFilesRef.current) formData.append('ct_files', file, file.name);
      formData.append('rtstruct_file', rtstructFileRef.current, rtstructFileRef.current.name);
      const response = await fetch(DOSEPRED_SERVICE_URL, { method: 'POST', body: formData });
      if (!response.ok) throw new Error(`dose-prediction service returned HTTP ${response.status}`);
      const buffer = await response.arrayBuffer();
      const predictedDose = new Float32Array(buffer);

      const renderingEngine = getRenderingEngine(RENDERING_ENGINE_ID);
      if (!renderingEngine) throw new Error('viewer is not initialized');
      if (predictedDose.length !== totalSlices * 180 * 180) {
        throw new Error(
          `predicted dose has ${predictedDose.length} voxels, expected ${totalSlices * 180 * 180}`,
        );
      }

      // Same voxel dimensions/spacing/orientation as the loaded CT, just
      // filled with predicted values instead of streamed from DICOM.
      const doseVolume = volumeLoader.createAndCacheDerivedVolume(CT_VOLUME_ID, {
        volumeId: DOSEPRED_VOLUME_ID,
        targetBuffer: { type: 'Float32Array' },
      });
      if (!doseVolume.voxelManager) throw new Error('derived volume has no voxel manager');
      // setScalarData() only updates the volume-level cache; the actual
      // per-slice image voxel managers used for rendering must be updated
      // via setCompleteScalarDataArray, otherwise the actor renders all zeros.
      doseVolume.voxelManager.setCompleteScalarDataArray?.(predictedDose);

      let maxDoseGy = 0;
      for (let i = 0; i < predictedDose.length; i++) {
        if (predictedDose[i] > maxDoseGy) maxDoseGy = predictedDose[i];
      }
      if (maxDoseGy <= 0) maxDoseGy = 80;
      await addVolumesToViewports(
        renderingEngine,
        [{ volumeId: DOSEPRED_VOLUME_ID, visibility: true }],
        [VIEWPORT_ID],
      );
      const viewport = renderingEngine.getViewport(VIEWPORT_ID) as Types.IVolumeViewport;
      viewport.setProperties(
        {
          colormap: {
            name: 'dosepred-magenta',
            opacityMapping: [
              { value: 0, opacity: 0 },
              { value: maxDoseGy * 0.1, opacity: 0 },
              { value: maxDoseGy * 0.15, opacity: 0.5 },
              { value: maxDoseGy, opacity: 0.7 },
            ],
          },
          voiRange: { lower: 0, upper: maxDoseGy },
        },
        DOSEPRED_VOLUME_ID,
      );
      renderingEngine.render();
      setDosePredStatus('idle');
      setDosePredLoaded(true);
      setStatus(
        'AI dose prediction rendered (magenta/orange colormap) -- UNVERIFIED, a feasibility spike ' +
          'trained on only 10 synthetic cases. Review before relying on it for anything.',
      );
    } catch (err) {
      setDosePredStatus('error');
      setStatus(`Dose prediction failed: ${err instanceof Error ? err.message : String(err)}`);
    }
  }, [totalSlices]);

  const onDiscardDosePrediction = useCallback(() => {
    const renderingEngine = getRenderingEngine(RENDERING_ENGINE_ID);
    const viewport = renderingEngine?.getViewport(VIEWPORT_ID) as Types.IVolumeViewport | undefined;
    const actorUid = viewport?.getActors().find((a) => a.referencedId === DOSEPRED_VOLUME_ID)?.uid;
    if (actorUid) viewport?.removeVolumeActors([actorUid], true);
    setDosePredLoaded(false);
    setStatus('Discarded the AI dose prediction.');
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
        <button type="button" disabled={!ctLoaded} onClick={onLoadNativeTrainingContours}>
          Load native XCAT training contours
        </button>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <button
          type="button"
          disabled={!ctLoaded || autoSegStatus === 'running'}
          onClick={onRunAutoSegmentation}
        >
          {autoSegStatus === 'running' ? 'Running AI auto-segmentation...' : 'Run AI auto-segmentation (unverified)'}
        </button>
        {autoSegLoaded && (
          <button type="button" onClick={onDiscardAutoSegmentation}>
            Discard AI proposal
          </button>
        )}
        <button
          type="button"
          disabled={!ctLoaded || !structuresLoaded || dosePredStatus === 'running'}
          onClick={onRunDosePrediction}
        >
          {dosePredStatus === 'running' ? 'Running AI dose prediction...' : 'Run AI dose prediction (unverified)'}
        </button>
        {dosePredLoaded && (
          <button type="button" onClick={onDiscardDosePrediction}>
            Discard AI dose prediction
          </button>
        )}
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
      {ctLoaded && (
        <NliCommandBar
          context={{ loadedRoiNames, doseLoaded, structuresLoaded, currentSliceIndex: 0, totalSlices }}
          onExecute={executeIntent}
        />
      )}
    </div>
  );
}
