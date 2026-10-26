# Project Overview: Shape Morph Pro (RectMorph Mask Pro)

**Shape Morph Pro** (`RectMorph Mask Pro`) is a DaVinci Resolve procedural shape-morphing plugin/macro. It allows video editors and motion designers to create dynamic, springy, mathematical morph transitions between rounded rectangles, cards, overlays, and masks without manually keyframing complex spline curves.

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
* Morph states are defined mathematically via custom **UserControls** for up to **8 key morph points** (labeled `PtA` through `PtH`).
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

### A. Point Controller System (Points A to H)
* **Point A (Start State)**:
  * Baseline frame (default: `0`), Width, Height, Corner radius.
* **Points B through H (Morph Targets 2 through 8)**:
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
    * `Ease Out`
    * `Ease In`
    * `Ease In-Out`
  * **Dynamics Tuning (Context-Aware Dynamic Visibility)**:
    * `Intensity` (Amplitude): Controls overshoot extent for `Back` and `Elastic`. Automatically **hidden** for all other curves; only visible when `Back` or `Elastic` is selected.
    * `Frequency` (Period): Adjusts spring oscillations for `Elastic`. Automatically **hidden** for all other curves; only visible when `Elastic` is selected.

### B. Interactive Automation Buttons
Each point includes interactive Lua script buttons:
* **`Set = Playhead`**: Captures `comp.CurrentTime` and writes it directly to the point's `Frame` property.
* **`Go to Frame`**: Teleports the playhead (`comp.CurrentTime`) directly to the point's configured frame.

### C. Master Controls
* **`TotalPoints`**: Dynamic control slider/stepper to reveal or hide points.
* **`Add Point` / `Remove Point`**: One-click increment/decrement workflow.

---

## 4. File Structure

```
Shape Morph Pro/
├── RectMorph_Mask_Pro.setting       # Single active source file for development & live testing
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
2. The active comp is inspected to find the existing `RectMorphMaskPro` node.
3. Its **canvas position** (X/Y grid) and all **downstream mask connections** (e.g. to `Background1.EffectMask`) are recorded.
4. The node is replaced with the newly updated tool settings.
5. Canvas position and mask connections are instantly restored, and the tool is selected in the Inspector.
6. The editor sees updates immediately without touching anything!

---

## 6. Changelog & Current State

* **Current Version**: v1.3 (Live API Hot-Reload Integration).
* **Live Hot-Reload Replacement**: Integrated direct API synchronization. Updates to `RectMorphMaskPro` are pushed live into the user's active comp, maintaining node position and re-linking downstream mask connections automatically.
* **Dynamic Control Visibility**: Context-aware curve sliders. `Intensity` only appears when `Back` or `Elastic` is active; `Frequency` only appears when `Elastic` is active.
* **UI Encapsulation**: Encapsulated inside `MacroOperator`. Master dimensions and expressions are 100% hidden from the Inspector.
* **Compatibility**: 100% DaVinci Resolve Free & Studio compatible.
* **Active Status**: Ready for feature enhancements and live testing.
