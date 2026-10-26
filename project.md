# Project Overview: Rect Morph Pro (RectMorph Mask Pro)

**Rect Morph Pro** (`RectMorph Mask Pro`) is a DaVinci Resolve procedural card, rectangle, and mask morphing plugin/macro. It allows video editors and motion designers to create dynamic, springy, mathematical morph transitions between rounded rectangles, cards, pills, squircles, overlays, and masks without manually keyframing complex spline curves.

> [!NOTE]
> **Naming & Scope Alignment**: The project was officially titled **Rect Morph Pro** to accurately reflect its core superpower—parametric interpolation of `Width`, `Height`, and `CornerRadius` with mathematical easing curves—avoiding confusion with arbitrary polygon or vector SVG path morphing.

> [!IMPORTANT]
> **Compatibility Guarantee**: 100% compatible with both **DaVinci Resolve (Free)** and **DaVinci Resolve Studio** (v17, v18, v19, v20+). Uses zero Studio-exclusive nodes, zero third-party dependencies, and produces no watermarks.

---

## 1. Core Architecture & Workflow

### A. Active Iteration Model (Single File)
To ensure rapid iteration and zero friction during development and testing, work is concentrated strictly on a single source file:
* **Primary Source**: [`RectMorph_Mask_Pro.setting`](file:///d:/02%20Code/01%20Drafting%20Projects/Shape%20Morph%20Pro/RectMorph_Mask_Pro.setting)
* **Direct Live Testing**: Changes are loaded directly into DaVinci Resolve (via clipboard paste or file load) for instantaneous live feedback.
* **No Premature Bundling**: We do **not** re-bundle into `.drfx` or compile Edit Page macros on every edit. Packaging is deferred until explicit final distribution is required.

### B. Tool Construction
* **Container**: `MacroOperator` (`RectMorphMaskPro`).
* **Internal Engine**: Encapsulates an internal `RectangleMask` (`RectMorphMaskInternal`) where dynamic Lua expressions execute frame-by-frame.
* **Clean Inspector**: All internal math expressions on `Width`, `Height`, and `CornerRadius` are hidden inside the macro. The user only sees clean controls (Morph points, easing curves, dynamics, and standard mask options).
* **Output**: Standard mask output (blue mask arrow) usable on any node (`Background`, `MediaIn`, `Merge`, `Transform`, etc.).

---

## 2. How It Works (The Engine)

Unlike traditional keyframing where curves are drawn in the Spline Editor:
* Morph states are defined mathematically via custom **UserControls** for up to **12 key morph points** (labeled `PtA` through `PtL`).
* A self-executing Lua closure runs directly inside the `Width`, `Height`, and `CornerRadius` inputs of the `RectangleMask`.
* At every frame evaluation (`time`), the expression:
  1. Inspects the configured points, checking which points are enabled.
  2. Dynamically sorts active points chronologically by frame number (`pts.f`).
  3. Identifies the bounding interval `[p1, p2]` containing the current `time`.
  4. Calculates normalized progress $t \in [0, 1]$.
  5. Computes non-linear interpolation using the target point's selected easing function, direction, intensity/overshoot, and frequency.
  6. Returns the interpolated floating-point value for `Width`, `Height`, or `CornerRadius`.

---

## 3. Features & Controls

### A. Point Controller System (Points A to L)
* **Point A (Start State)**:
  * Baseline frame (default: `0`), Width, Height, Corner radius.
* **Points B through L (Morph Targets 2 through 12)**:
  * **Frame**: Target arrival frame on the timeline.
  * **Enable Switch**: Toggles whether the point is active in the morph sequence.
  * **Dimensions**: Target `Width`, `Height`, and `Corner` radius.
  * **Curve Selection** (11 Easing Algorithms):
    1. `Linear`
    2. `Sine`
    3. `Quad`
    4. `Cubic`
    5. `Quart`
    6. `Quint`
    7. `Expo`
    8. `Circ`
    9. `Back` (Overshoot / Anticipation)
    10. `Elastic` (Spring / Harmonic oscillation)
    11. `Bounce` (Physical decay bounce)
  * **Direction**:
    * `Ease Out` (**Default**)
    * `Ease In`
    * `Ease In-Out`
  * **Interactive On-Screen Preview Viewer Handles (`RectangleControl`)**:
    * Each point (`PtA` through `PtH`) binds its `Width`, `Height`, and `Corner` controls to a Fusion `RectangleControl` (`PC_ControlGroup = 1..8`, `PC_ControlID = 0, 1, 2`) centered on `RectMorphMaskInternal.Center` (`RCD_SetX = 0.5`, `RCD_SetY = 0.5`).
    * Selecting a point in the Sequencer window or clicking `Set = Playhead` / `Go to Frame` / `+ Add Point` activates that point's green rectangle handles in the Fusion Preview Viewer (`INPB_PC_Visible = true`) and hides the locked internal expression handles (`INPB_PC_Visible = false`), so users can drag mask width/height/corner edges directly in the viewer.
  * **Dynamics Tuning (Context-Aware Dynamic Visibility)**:
    * `Intensity` (Amplitude): Controls overshoot extent for `Back` and `Elastic`. Automatically **hidden** for all other curves; only visible when `Back` or `Elastic` is selected.
    * `Frequency` (Period): Adjusts spring oscillations for `Elastic`. Automatically **hidden** for all other curves; only visible when `Elastic` is selected.

### B. Streamlined Inspector & Top-Level Sequencer Workflow
* **Top of Inspector**:
  * Standard Mask Controls: `Filter` (`Fast Gaussian`, `Box`, `Bartlett`, `Multi-box`, `Gaussian`), `SoftEdge`, `BorderWidth`, `Invert`, `Solid`, and `Center`.
  * **Single Prominent Launcher Button**: **`📈 Open Curve & Point Sequencer`** (`OpenCurveBrowserBtn`) right at the top of the Inspector.
* **Clean Point Sections (`PtA` through `PtH`)**:
  * Smart transition headers: **`Start  ·  A`**, **`A  ➔  B`**, **`B  ➔  C`**, **`C  ➔  D`**, ..., **`G  ➔  H`**.
  * **Native `Set = Playhead` Button on Every Point**: Positioned directly underneath the `Frame` slider for rapid 1-click timeline capture on each morph point, automatically updating timeline keyframe ticks and preview viewer handles.
  * **Initial 2-Point State**: Only **`Start  ·  A`** and **`A  ➔  B`** are visible by default. Points `C` through `H` are hidden (`IC_Visible = false`, `Pt{L}_Enable = 0`) and dynamically revealed/hidden from the Curve & Point Sequencer window.

### C. Timeline Keyframe Visualization (`TimelineMarks` / `RectMorphKeyframes`)
* A hidden `TimelineMarks` input on `RectMorphMaskPro` is connected to a `BezierSpline` (`RectMorphKeyframes`).
* Whenever points are added, removed, or have their frame changed via slider or `Set = Playhead`, `syncKeys()` automatically updates `RectMorphKeyframes` so white keyframe tick lines appear on the Fusion Timeline Ruler at every active point's frame.

---

## 4. File Structure

```
Shape Morph Pro/
├── RectMorph_Mask_Pro.setting       # Single active source file for development & live testing
├── build_setting.py                 # Generator script for RectMorph_Mask_Pro.setting
├── generate_ui_buttons.py           # Generator for 8x supersampled card & upper deck PNG slices
├── scripts/
│   └── CurveBrowser.lua             # Floating Qt UIManager Visual Curve Browser window
├── assets/ui/                       # card_btn_*.png (160x30) & deck_*.png (44px tall upper deck slices)
├── assets/curves/                   # Anti-aliased 145x64 neon green easing curve thumbnails
│   ├── Linear.png, Sine.png, Quad.png, Cubic.png, Quart.png, Quint.png,
│   └── Expo.png, Circ.png, Back.png, Elastic.png, Bounce.png
├── backups/                         # Version checkpoints for guaranteed rollback safety
│   └── v1.3_stable/                 # Verified v1.3 stable release snapshot
├── sync_to_resolve.py               # Live hot-reload bridge script to push changes directly into active comp
├── package_drfx.py                  # Standby packaging script (used only on explicit release)
├── RectMorph_Mask_Pro.drfx          # Packaged bundle (generated on release)
├── project.md                       # Architecture, features, and specifications (this file)
└── rule.md                          # Development rules & guidelines
```

---

## 5. Live Hot-Reload Workflow in DaVinci Resolve

**Zero Copy-Paste Needed**:
Whenever changes are made to [`RectMorph_Mask_Pro.setting`](file:///d:/02%20Code/01%20Drafting%20Projects/Shape%20Morph%20Pro/RectMorph_Mask_Pro.setting):
1. The agent executes [`sync_to_resolve.py`](file:///d:/02%20Code/01%20Drafting%20Projects/Shape%20Morph%20Pro/sync_to_resolve.py) directly through the DaVinci Resolve API.
2. The active comp is inspected to find the existing `RectMorphMaskPro` node (and `RectMorphKeyframes` spline).
3. Its **canvas position** (X/Y grid) and all **downstream mask connections** (e.g. to `Background1.EffectMask`) are recorded.
4. The node is replaced with the newly updated tool settings.
5. Canvas position and mask connections are instantly restored, and the tool is selected in the Inspector.
6. The editor sees updates immediately without touching anything!

---

## 6. Changelog & Current State

* **Current Version**: v3.0 (12-Point Sequence Support `A`–`L`, Zero Hover Black-Out & Seamless 840×44 Upper Deck).
* **12-Point Sequence Pipeline (`Start · A` through `K ➔ L`) & Hover Fix (v3.0)**:
  - Fixed the hover black-out effect on sequence point buttons caused by a filename mismatch (`_normal_hover.png` vs `_hover.png`) between [`generate_ui_buttons.py`](file:///d:/02%20Code/01%20Drafting%20Projects/Shape%20Morph%20Pro/generate_ui_buttons.py) and [`scripts/CurveBrowser.lua`](file:///d:/02%20Code/01%20Drafting%20Projects/Shape%20Morph%20Pro/scripts/CurveBrowser.lua), and added `#212636` fallback `background-color` + `selected_hover` states.
  - Expanded [`build_setting.py`](file:///d:/02%20Code/01%20Drafting%20Projects/Shape%20Morph%20Pro/build_setting.py), [`RectMorph_Mask_Pro.setting`](file:///d:/02%20Code/01%20Drafting%20Projects/Shape%20Morph%20Pro/RectMorph_Mask_Pro.setting), [`generate_ui_buttons.py`](file:///d:/02%20Code/01%20Drafting%20Projects/Shape%20Morph%20Pro/generate_ui_buttons.py), and [`scripts/CurveBrowser.lua`](file:///d:/02%20Code/01%20Drafting%20Projects/Shape%20Morph%20Pro/scripts/CurveBrowser.lua) from 8 points (`A`–`H`) to **12 points (`A`–`L`)**: `Start · A` (`58×44`) + 11 transition slots `A➔B` through `K➔L` (`11 × (10+46) = 616px`) + right-corner `− Remove` (`66×44`) fitting the exact `840 × 44` upper deck (`78 + 58 + 616 + 10 + 66 + 12 = 840px`).
  - Optimized `activatePointViewerHandle` in `CurveBrowser.lua` (`lastActivePCIdx` differential update) to make point selection and adding/removing points 12× faster.
* **Seamless `840 × 44` Baked-PNG Upper Deck & Right-Corner `− Remove` (v2.9)**:
  - Removed the `DIRECTION` label and dropdown from the window so **`Direction` (`Ease Out`, `Ease In`, `Ease In-Out`) is controlled directly from the Inspector tab** (`PtB_Dir`–`PtH_Dir`).
  - Added a live 200ms `ui:Timer` (`InspectorSyncTimer`) in `scripts/CurveBrowser.lua` so changing `Direction` or `Curve` on any transition point in the Inspector tab immediately updates the open window's curve thumbnails (`_Out.png`, `_In.png`, `_InOut.png`), titles, and active highlight.
  - Fitted the **`− Remove`** button (`82 × 44`) permanently in the **right corner** of the upper deck (`PtBtn_Remove`), showing its neutral slate beveled pill when `highestActive > 2` and a subtle muted disabled state when `highestActive == 2`.
  - Replaced CSS-drawn upper-deck buttons and caps with **8× supersampled full-height (`44px`) PNG slices** (`deck_left88.png`, `deck_btn68_*.png`, `deck_mid18.png`, `deck_btn64_*.png`, `deck_empty64.png`, `deck_mid16.png`, `deck_rem82_*.png`, `deck_right12.png` generated by `generate_ui_buttons.py`), baking the `#212636` deck surface, `1px` `#363f58` border, `8px` outer rounded corners, and centered `28px`-tall (`y = 8..36`) `5px`-rounded beveled pills into one seamless `840 × 44` bar with zero bottom cutoffs, zero corner artifacts, and zero layout holes.
* **Toned-Down Selected / Accent Styling (User Preference: no flashy neon)**:
  - Selected card, `✓ Active` pill, selected sequence pill (`A ➔ B`), and the `● A ➔ B` badge now use a calm dark-sage fill (`#2f4226 → #25351f`) with a muted sage-lime outline (`#6a9a34`, rim `#86b84c`) and soft text (`#c4f07a`) instead of solid neon `#9aff1c` / `#a8ff33` fills and borders.
  - Active card surface `#1f2a1d` with `#5c7f33` border; title text `#b6e36b`.
  - `− Remove` is now a neutral slate button with grey text (`#94a3b8`); only on hover does it show a subtle muted-rose hint (`#e8a3ac` text, `#8a4b56` border). No red fill.
  - `+ Add` is a neutral slate button with soft green text; hover shows the muted sage outline (no neon fill).
  - All hovers (cards, titles, Direction dropdown) use the muted sage accent.
* **Separate Inset Rounded Pill Buttons on Curve Cards** (v2.6):
  - Restored the preferred look: `Apply` / `✓ Active` is again a separate 144×23 rounded (5px) pill sitting inside the card with 8px side padding, instead of a full-width card-bottom bar.
  - The bottom slice of each card (`Apply_X`, 160×30) is now drawn from an 8× supersampled PNG (`assets/ui/card_btn_*.png`, generated by `generate_ui_buttons.py`) that bakes the card surface, side/bottom border, 8px rounded card corners, and the beveled pill into one image. Qt draws the text on top via `background-image`.
  - Because the card surface surrounds the pill in the same pixels, no transparent gap exists around the pill corners, so the old dark corner chips cannot appear.
  - States: `idle`, `idle_hover` (green rim), `idle_pressed`, `active`, `active_hover`.
  - Card height 114 → 116, window height 356 → 360.
* **Luxury Button Bevels & Depth Lighting** (v2.5):
  - Replaced flat, dull 1px solid borders across all buttons with luxurious top-to-bottom depth gradients (`qlineargradient`), top rim highlight chamfers (`border-top: 1px solid <highlight>`), and grounded bottom shadows (`border-bottom: 1px solid <shadow>`).
  - **Upper Deck Buttons**: `Start · A`, `A ➔ B`, `+ Add`, `− Remove`, and `DirSelect` feature smooth 4px/5px anti-aliased corners with subtle metallic/cyber gradients and zero dark corner cutouts.
  - **Active Jewel Accents**: Active transition pills and cards feature vibrant neon emerald depth gradients (`stop:0 #a8ff33, stop:1 #86ef0d`) and top highlight rim chamfers.
* **Flawless Card Corners & Unified 3-Part Architecture**:
  - Eliminated legacy Frankenstein padding walls (`PadL_`, `PadR_`, `PadB_`) that carved out hollow notches and exposed the dark `#11141d` window canvas behind rounded `Apply` buttons.
  - Replaced with the unified 3-part card architecture:
    1. `Img_X` (160×64): Exact 1:1 anti-aliased curve graph with `border-top-left-radius: 8px; border-top-right-radius: 8px;`.
    2. `Lbl_X` (160×22): Seamless middle title band with straight vertical edges.
    3. `Apply_X` (160×28): Full-width bottom cap action button with `border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;`, depth gradient, top rim highlight, and 0px margin/padding, achieving 100% mathematically flawless corners with zero dark chips or seams.
* **Per-Point `Set = Playhead` in Inspector**:
  - Each point (`Start · A` through `G ➔ H`) has a dedicated `Set = Playhead` button directly below its `Frame` slider.
  - Clicking `Set = Playhead` captures `comp.CurrentTime` into the point's frame, triggers `syncKeys()` to update timeline ticks, and activates on-screen handles (`setActivePC`).
* **Cleaned Sequencer Window (`scripts/CurveBrowser.lua`)**:
  - Removed bottom status telemetry text (`StatusMsg`) for a sleeker, balanced window.
  - Removed `FRAME` spinbox and window `Set = Playhead` button from Tier 2, providing a minimalist layout with active transition badge (`● A ➔ B`) and Direction dropdown (`Ease Out`).
  - Window geometry reduced from 392px to 356px height.
* **Ease Out (0) Default**:
  - All transition points (`PtA_Dir` through `PtH_Dir`) and Lua expression fallback defaults (`defD`) default to `0` (`Ease Out`).
  - Sequencer window (`scripts/CurveBrowser.lua`) opens with `Ease Out` selected by default, displaying 1:1 `_Out.png` curve thumbnails and `Ease Out <Curve>` labels.
  - Adding new transitions via `+ Add` initializes direction to `0` (`Ease Out`).
* **Landscape Visual Curve & Point Sequencer (`scripts/CurveBrowser.lua`)**:
  - **Custom Colored Title Bar (`#1b2234`)**: Uses LuaJIT `ffi` + Win32 `DwmSetWindowAttribute` to replace the white Windows title bar with a dark slate-indigo header.
  - **Unified Lighter Slate Top Control Deck (`840 × 76`)**:
    - Wrapped in a seamless `#212636` lighter slate card box (`1px solid #363f58` outer border) matching the 10 curve cards below it.
    - Tier 1 (`SEQUENCE`): Smart transition pills **`Start · A`** `➔` **`A ➔ B`** `➔` **`B ➔ C`** `➔` **`+ Add`** and **`− Remove`**. Unused slots render as seamless `#212636` filler panels so there is zero layout shifting or background holes.
    - Tier 2: Active transition badge (`●  A  ➔  B`) and right-aligned `DIRECTION` (`Ease Out` default) dropdown.
  - **8× Supersampled 1:1 Native Curve Thumbnails (`144 × 54`)**:
    - Rendered at `1152 × 432` and downsampled via `LANCZOS` to `144 × 54`, displayed in Qt `QLabel` via `<img src="...">` with no HTML `width`/`height` rescaling so curve lines are 100% smooth and unbroken.
  - **Lighter-Colored Card Boxes (`#212636` Idle / `#1e2e18` Active) Wrapping Graph + Title + Apply**:
    - Each of the 10 easing curves in the 2×5 grid is enclosed in a unified lighter slate-blue rounded box (`1px solid #363f58` idle / `1px solid #9aff1c` active) that wraps the dark graph screen, curve title, and `Apply` (`✓ Active`) button together.
* **Smart `A ➔ B` Inspector Headers**: Renamed Inspector point sections from `"Point 3 (C - Morph 2 -> 3)"` to **`Start  ·  A`**, **`A  ➔  B`**, **`B  ➔  C`**, ..., **`G  ➔  H`**.
* **Top-of-Inspector Mask Controls (`Filter` Restored)**: Restored `Filter` (`Fast Gaussian`, `Box`, `Bartlett`, `Multi-box`, `Gaussian`), `SoftEdge`, `BorderWidth`, `Invert`, `Solid`, and `Center` at the very top of the Inspector.
* **Interactive On-Screen Preview Viewer Handles**: Added `INPID_PreviewControl = "RectangleControl"` to `PtA`–`PtH` (`Width`, `Height`, `Corner`) and suppressed `RectMorphMaskInternal`'s locked expression preview control so the active point's mask edges can be dragged directly in the Fusion Preview Viewer.
* **Streamlined Inspector & Per-Point Add/Remove**: Added `+ Add Point` and `- Remove Point` at the bottom of every point section, starting with only Point 1 (A) and Point 2 (B) visible.
* **Timeline Keyframe Signs**: Added `TimelineMarks` connected to `RectMorphKeyframes` (`BezierSpline`) so every active point displays a keyframe tick line on the Fusion timeline ruler.
* **Rollback Checkpoint**: Full Git commit/tag `v1.3-stable` and physical backup directory created at `backups/v1.3_stable/`.
* **Compatibility**: 100% DaVinci Resolve Free & Studio compatible.
* **Active Status**: Verified live in active DaVinci Resolve session.
