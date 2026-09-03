import { useCallback, useEffect, useRef, useState } from 'react';
import {
  RenderingEngine,
  Enums,
  getRenderingEngine,
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
} from '@cornerstonejs/tools';
import { ensureCornerstoneInitialized } from '../services/cornerstoneInit';

const RENDERING_ENGINE_ID = 'tps-rendering-engine';
const VIEWPORT_ID = 'tps-stack-viewport';
const TOOL_GROUP_ID = 'tps-tool-group';

export function DicomViewer() {
  const elementRef = useRef<HTMLDivElement>(null);
  const [ready, setReady] = useState(false);
  const [status, setStatus] = useState('Initializing Cornerstone3D...');

  useEffect(() => {
    let cancelled = false;

    async function setup() {
      await ensureCornerstoneInitialized();
      if (cancelled || !elementRef.current) return;

      const renderingEngine = new RenderingEngine(RENDERING_ENGINE_ID);
      const viewportInput: Types.PublicViewportInput = {
        viewportId: VIEWPORT_ID,
        type: Enums.ViewportType.STACK,
        element: elementRef.current,
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

      setStatus('Load a local DICOM series to begin.');
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

  const onFilesSelected = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setStatus(`Loading ${files.length} file(s)...`);

    // fileManager.add already returns a fully-scoped id, e.g. "dicomfile:0" --
    // do not wrap it in an extra "wadouri:" prefix, or parseImageId reads the
    // whole thing as a "wadouri" (i.e. XHR/http) scheme instead of a local file.
    const imageIds = Array.from(files).map((file) => wadouri.fileManager.add(file));

    const renderingEngine = getRenderingEngine(RENDERING_ENGINE_ID);
    const viewport = renderingEngine?.getViewport(VIEWPORT_ID) as
      | Types.IStackViewport
      | undefined;
    if (!viewport) return;

    await viewport.setStack(imageIds, 0);
    viewport.render();
    setStatus(`Loaded ${imageIds.length} image(s). Left-drag: window/level, middle-drag: pan, right-drag: zoom, wheel: scroll.`);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <input
        type="file"
        multiple
        accept=".dcm,application/dicom"
        disabled={!ready}
        onChange={(e) => onFilesSelected(e.target.files)}
      />
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
