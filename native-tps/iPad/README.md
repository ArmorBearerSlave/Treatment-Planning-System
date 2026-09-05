# Governed TPS for iPad — field review prototype

Open `GovernedTPSiPad.xcodeproj`, select the GovernedTPSiPad scheme and an iPad
simulator. Deployment target: iPadOS 17+. Physical installation needs your Apple
Development team and a provisioned device. No model downloads or cloud services.

## Why iPad

| iPad capability implemented | Advantage for case review |
| --- | --- |
| Apple Pencil markup, with optional finger ink | Point out a boundary directly on the image during a discussion |
| Large slice controls and three voxel planes | Inspect CT without a mouse or keyboard |
| Hold-to-zoom pinch inspection | Examine a region, then return to the unmodified markup coordinate frame |
| Offline active case and saved notes | Carry a research case away from the workstation |
| Slice-bound markup and review checklist | Capture observations in context rather than in a separate document |
| Compact review JSON through Files | Hand off observations without sending the full CT again |

Desktop remains the place for image inference, local LLMs and detailed planning
work. Spark remains the place for XCAT2 and OpenTOPAS/nBio. This initial iPad app
makes no network requests and does not start inference or simulation jobs.

## Try it

1. Run on an iPad simulator or provisioned iPad.
2. Choose **Explore a CT demonstration**, or **Import CT case** for a native JSON
   transferred into Files. CT-only case 001 is already on the Mac under
   `../data/spark-cases/VCT-PROSTATE-001.json`; transfer it to the iPad using Files
   or AirDrop. Desktop workspace JSON and raw DICOM/NPZ are not case inputs.
3. Choose XY/XZ/YZ, scrub slices, toggle CT/labels/transport dose, and use window
   presets. Planes follow voxel axes, not an assumed anatomical orientation.
4. Enable **Mark up**. Apple Pencil is the default input; **Finger ink** enables
   touch/simulator drawing. **Undo stroke** removes the last stroke on that slice.
5. Add a reviewer name, observations and checklist on **Review**.
6. **Handoff → Export review handoff** saves a JSON through Files. Use Files to
   share it. The current desktop app does not yet ingest this new review format.

## Data and governance

Imports validate the shared TPSCore case contract, support absent MR, and retain
source notes. One active case is stored in the app's Documents folder, with
complete file protection. Importing another case archives the previous review
JSON there. The input limit remains 96 MB; large cohorts need a future case cache.
Source images are immutable in this app. Pencil strokes are **observations**, not
segmentation edits, RTSTRUCT, contour predictions or treatment approval.

Review JSON contains a canonical native source hash, case ID, local reviewer
name, checklist, notes and PencilKit drawing blobs keyed `axis:slice` (zero-based).
Canvas width is fixed at 1024; height follows the physical aspect ratio of that
slice. Strokes are preserved through resizing. Plane pixel axes increase right
and down. The exported source hash must be checked before overlaying marks on
another system. Review files contain no CT arrays. Local names/hashes are not
authenticated signatures. Checking every box does not authorize treatment.

Dose overlay uses a fixed 0–80 Gy color range. Inspect the source normalization
text; this is not an independent dose verification. Imported labels are viewed,
not corrected. A demo has CT/truth only and no transport dose.

## Validation and remaining work

- iPad simulator build passed (iOS 18.5, iPad Pro 11-inch M4).
- Two simulator tests passed: source binding, invalid slice and clinical-flag rejection.
- Simulator UI smoke check: CT demonstration renders; slice navigation works;
  finger/Pencil mode exposes markup; Review reports one saved marked slice.
- Physical Pencil latency, palm rejection, device memory pressure and real-device
  file sharing require hardware verification.
- Next: desktop review ingestion, multi-case cache, authenticated Mac job handoff,
  collaboration and richer contour editing with spatial validation.

Apple references: [PencilKit drawing policy](https://developer.apple.com/documentation/pencilkit/pkcanvasviewdrawingpolicy)
and [SwiftUI file importer](https://developer.apple.com/documentation/swiftui/view/fileimporter(ispresented:allowedcontenttypes:oncompletion:)).

Regenerate the project with `python3 generate_project.py` after adding sources.
This project shares TPSCore through the parent Swift package and is separate
from the desktop Xcode target and existing repository web application.
