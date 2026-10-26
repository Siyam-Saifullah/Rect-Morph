# Development Rules & Guidelines: Rect Morph Pro

This document governs the engineering standards, best practices, strict rules, common pitfalls, and tracking tasks for the **Rect Morph Pro** (`RectMorph Mask Pro`) DaVinci Resolve plugin.

> [!IMPORTANT]
> **Persistent Rule**: Both [`project.md`](file:///d:/02%20Code/01%20Drafting%20Projects/Shape%20Morph%20Pro/project.md) and [`rule.md`](file:///d:/02%20Code/01%20Drafting%20Projects/Shape%20Morph%20Pro/rule.md) **MUST** be updated after every task, conversation step, bugfix, or feature change to remain in continuous sync with the codebase.

---

## 1. General Rules & Principles

1. **Free Version Compatibility (Zero Studio-Exclusive Dependencies)**:
   - The plugin must operate 100% seamlessly in the **Free version of DaVinci Resolve** without watermarks, Studio-only dialog popups, or missing tool errors.
   - Rely exclusively on standard core Fusion tools (`RectangleMask`, `MatteControl`, `Background`, `Transform`, etc.) and pure inline Lua expressions.
   - Strictly prohibit Studio-exclusive ResolveFX / OpenFX plugins, Studio-locked Fusion nodes (e.g. Optical Flow, Surface Tracker, Magic Mask), or features that require a Studio license.

2. **Encapsulate Internal Math in `MacroOperator`**:
   - In Fusion, when an input on a raw tool has an expression, Fusion forces open a raw code box in the Inspector.
   - To keep the Inspector clean and professional, always encapsulate the driven node inside a `MacroOperator`.
   - Expose only user-facing sliders and buttons via `InstanceInput`. **Never** expose internally driven inputs (like `Width`, `Height`, `CornerRadius` expressions) to the macro's exposed inputs.

3. **Context-Aware Dynamic UI Visibility**:
   - Sliders that only apply to specific modes (e.g., `Intensity` for Back/Elastic, `Frequency` for Elastic) must **only** appear when those modes are active.
   - Use `INP_DoNotifyChanged = true` and `INPS_ExecuteOnChange` on multi-buttons, targeting `INPB_IC_Visible` on both the macro tool and internal tool.
   - Always set matching initial `IC_Visible = true/false` defaults on both the internal UserControls and the Macro's `InstanceInput` declarations so the tool spawns with the correct visibility state immediately upon pasting.

4. **Hermetic & Thread-Safe Expressions**:
   - Fusion expressions execute every frame across threads. They must **never** call external non-sandbox OS operations or blocking code.
   - Expressions must handle boundary conditions (e.g., zero points configured, playhead before first point, playhead after last point, division by zero when frame duration is 0).

5. **Button Script Dual-Targeting (`BTNCS_Execute`)**:
   - In button execution scripts, use `local tgt = tool.RectMorphMaskInternal or tool` so the script works seamlessly whether clicked on the `MacroOperator` or inside an expanded tool.
   - Always wrap execution calls in `pcall` so unexpected state doesn't throw pop-up error dialogs.

6. **Live Hot-Reload Replacement Workflow**:
   - Instead of asking the user to copy/paste and reconnect nodes manually, always execute [`sync_to_resolve.py`](file:///d:/02%20Code/01%20Drafting%20Projects/Shape%20Morph%20Pro/sync_to_resolve.py) or direct Lua scripting via Resolve API.
   - The script must record the active `RectMorphMaskPro` node's flow coordinates (`flow:GetPos(old)`) and downstream mask connections (`out:GetConnectedInputs()`), replace the tool with the updated `.setting`, restore canvas position, reconnect downstream targets, and activate the new tool.

7. **Packaging & Delivery Sync**:
   - Keep [`RectMorph_Mask_Pro.setting`](file:///d:/02%20Code/01%20Drafting%20Projects/Shape%20Morph%20Pro/RectMorph_Mask_Pro.setting) as the single source of truth.
   - Run `python package_drfx.py` to synchronize both the Fusion Tool and the Edit Page Effect inside `RectMorph_Mask_Pro.drfx`.

8. **Custom Tool / Macro Architecture Over Modifiers**:
   - Build features as unified, self-contained macro tools rather than separate parameter modifiers.
   - Ensures 1-click drag-and-drop usability, unified multi-dimensional timing (width, height, corner, position), and full Edit Page effect compatibility.

---

## 2. The DOs

* ✅ **DO** ensure all easing curves return clean values in the range $[0, 1]$ (or overshoot cleanly for Elastic/Back) without `NaN` or `nil` returns.
* ✅ **DO** use `math.max(0.0001, p2.f - p1.f)` when dividing by frame durations to eliminate division-by-zero errors when two points share the same frame.
* ✅ **DO** verify `.drfx` directory hierarchy:
  - Fusion tool: `Fusion/Tools/` and `Templates/Fusion/Tools/`
  - Edit effect: `Edit/Effects/<Category>/` and `Templates/Edit/Effects/<Category>/`
* ✅ **DO** run `python package_drfx.py` after editing `.setting` to keep `.drfx` up-to-date.
* ✅ **DO** verify that all nodes and features work out of the box in the **Free version of DaVinci Resolve** with zero watermarks.
* ✅ **DO** test both Fusion Page (Mask mode) and Edit Page (Clip effect mode).

---

## 3. The DON'Ts

* ❌ **DON'T** expose raw expression-driven inputs (`Width`, `Height`, `CornerRadius`) on the MacroOperator; keep them hidden inside the internal node.
* ❌ **DON'T** display irrelevant parameter sliders (like spring oscillations) when non-spring curves (Linear, Sine, Quad, etc.) are selected.
* ❌ **DON'T** use any Studio-exclusive nodes, ResolveFX / OpenFX tools, or Studio-only Fusion operators.
* ❌ **DON'T** rely on Studio-locked external Python scripting bridges; stick to built-in Lua UI execution scripts (`BTNCS_Execute`).
* ❌ **DON'T** use multi-line comments (`--[[ ... ]]`) inside inline Lua expressions in `.setting` files.
* ❌ **DON'T** leave unescaped quotes or unbalanced braces in `.setting` table structures.

---

## 4. Common Errors & Troubleshooting

| Issue / Error | Root Cause | Solution |
| :--- | :--- | :--- |
| **Messy expression text boxes in Inspector** | Expressions attached directly to raw `RectangleMask` inputs exposed in GUI. | Wrap node in a `MacroOperator` and expose only user controls (`InstanceInput`), omitting driven inputs. |
| **Sliders visible when irrelevant** | `Intensity` or `Frequency` exposed statically without dynamic visibility. | Attach `INPS_ExecuteOnChange` to Curve button toggling `INPB_IC_Visible`, and set matching initial `IC_Visible` state. |
| **Mask disappears / Red node error** | Expression evaluated to `nil` or `NaN` at current frame. | Ensure all conditional branches return a valid numerical fallback (`return pts[#pts].v` or `return 0.25`). |
| **Animation freezes between points** | Points array not sorted chronologically or frame difference is 0. | Always execute `table.sort(pts, function(a, b) return a.f < b.f end)` and clamp duration with `math.max(0.0001, ...)`. |
| **Button clicks do not update macro state** | Button script referenced `tool` instead of dual-targeting `tool.RectMorphMaskInternal or tool`. | Use dual-targeting in `BTNCS_Execute` and update both target and macro input. |
| **Curve Browser window does not appear** | `ui:ScrollArea` does not exist in Fusion's Lua `UIManager` (even though Python proxy `hasattr` returns `True`). | Never use `ui:ScrollArea`; use compact thumbnails (`145x64`) inside a standard `ui:VGroup` / `ui:HGroup` grid. |
| **Graph images show as empty boxes in UIManager** | `ui:Label` does not have an `Icon` property (`Icon = ui:Icon{...}` only works on `ui:Button`). | Render PNG images in `ui:Label` via HTML `Text = '<img src="' .. imgPath .. '" width="136" height="58">'` with fixed `MinimumSize`/`MaximumSize`. Avoid `ui:TextEdit` for small thumbnails as it adds scrollbars and large minimum height hints. |
| **Window buttons or curve labels cut off** | Insufficient button height or CSS padding clipping descenders (`y`, `g`, `p`). | Give `ui:Label` an explicit height (`18px`) and `ui:Button` a height of `24px` with `padding: 0px 0px 1px 0px;` in `StyleSheet`. |
| **Hidden widgets keep empty gap in `HGroup`** | Qt `QLayout` in Fusion UIManager retains geometry allocation for hidden widgets (`retainSizeWhenHidden = true`). | Rather than placing dynamic `+` buttons after all inactive point widgets, configure the immediate next point slot (`highestActive + 1`) to act as the in-line `+` button in the pipeline. It eliminates voids and collapses cleanly. |
| **Timeline keyframe ticks missing or extra tick at current frame** | `comp:BezierSpline()` automatically inserts a key at `comp.CurrentTime` when assigned. | Connect a hidden `TimelineMarks` input to `RectMorphKeyframes` (`BezierSpline`) and call `sp:DeleteKeyFrames(-100000, 100000)` before writing active point frames. |
| **Viewer mask edges not draggable in Preview Viewer** | `RectMorphMaskInternal`'s `Width`/`Height`/`CornerRadius` are expression-driven (locking their viewer handles), while `Pt{L}_Width`/`Height`/`Corner` lacked `RectangleControl`. | Add `INPID_PreviewControl = "RectangleControl"`, `PC_ControlGroup = idx`, `PC_ControlID = 0/1/2`, `RCD_SetX = 0.5`, `RCD_SetY = 0.5` to `PtA`–`PtH` (`Width`, `Height`, `Corner`), set `INPB_PC_Visible = false` on `RectMorphMaskInternal`'s driven inputs, and set `INPB_PC_Visible = true` only on the currently selected point. |
| **`ui:Slider` ignores `Maximum` / `Value` in constructor table** | Fusion's `ui:Slider { Maximum = 1000, Value = 500 }` ignores `Maximum` at construction time (clamping `Value` to 100). | Always set `itm.SliderID.Minimum`, `itm.SliderID.Maximum`, and `itm.SliderID.Value` after `local itm = win:GetItems()`. |
| **Child `ui:Label` text clipped inside styled `ui:HGroup`** | Setting `padding: 5px 10px;` on a parent `ui:HGroup` without a selector cascades horizontal padding to child `QLabel` widgets. | Always explicitly set `padding: 0px;` in the `StyleSheet` of child `ui:Label` widgets inside styled container groups. |
| **Window buttons/sliders unresponsive when launched from external Python script** | Launching `disp:RunLoop()` via `comp.Execute('ldofile(...)')` inside a short-lived Python subprocess kills the `disp:RunLoop()` when the Python process exits, leaving a zombie Qt window on screen. | Always launch `UIManager` scripts via `comp:RunScript(path)` so Fusion spawns a persistent internal `fuscript` thread that keeps `disp:RunLoop()` alive. |
| **`ui:FindWindow(id)` returns old hidden window instead of active window** | `existing:Hide()` keeps the hidden `UIWindow` in `UIManager`'s window list with the same `ID`, shadowing newer windows. | When closing/hiding any window, always rename `existing.ID = "Closed_" .. tostring(os.clock())` after queueing `Close`. |
| **Borders on `ui:VGroup` / `ui:HGroup` do not render** | In Fusion's Qt `UIManager`, layout containers (`VGroup`/`HGroup` = `QBoxLayout`) do not paint their own `border` or `background-color` stylesheet; they only cascade styles to children. | To wrap multiple widgets (e.g., graph + title + Apply button) inside a lighter card box with a unified border, use `Spacing = 0` inside `ui:VGroup` and apply matching `#212636` background + top/side/bottom `1px solid` borders to the top `Img` `QLabel`, middle `Lbl` `QPushButton`, and bottom `PadL`/`PadB`/`PadR` `QLabel` walls surrounding the `Apply` button. |
| **Programmatic `Slider.Value` / `SpinBox.Value` change fires `ValueChanged` asynchronously** | `UIManager` queues `ValueChanged` events asynchronously, so a synchronous `isSyncingControls = true/false` flag is already `false` when the event fires. | Track `lastSyncedFrame` and `lastSyncedDirIdx` and ignore `ValueChanged` events matching the last synced value. |
| **Default white Windows OS title bar clashes with dark UI** | `UIManager` windows use the default Win32 light caption bar on Windows 10/11. | Use LuaJIT `ffi` (`dwmapi.DwmSetWindowAttribute`) after `win:Show()` with `DWMWA_USE_IMMERSIVE_DARK_MODE` (20) and `DWMWA_CAPTION_COLOR` (35) to paint the title bar a custom dark color (`#1b2234`). |
| **Right-aligned `− REMOVE` button clipped off right edge of `HGroup`** | Hidden point slots (`PtBtn_4..8`) retain their initial width hint (`retainSizeWhenHidden = true`) even after `MinimumSize = {0,0}`, pushing widgets placed after them off the right edge. | Place `+ ADD` in slot `highestActive + 1` and `− REMOVE` in slot `highestActive + 2` so all hidden slots sit *after* `− REMOVE`. |
| **Curve graph lines look jagged / broken in `ui:Label`** | Specifying `width="144" height="52"` in Qt's HTML `<img src="...">` when the PNG on disk is `136x58` triggers nearest-neighbor scaling in `QTextDocument`, dropping pixel rows and breaking thin diagonal lines. | Generate curve PNGs with 8× supersampling + `LANCZOS` downsampling to the exact 1:1 display size (`144x54`) and use `<img src="...">` without `width`/`height` attributes so Qt renders 1:1 pixels with zero rescaling. |
| **Dark / black cutout triangles in corners of buttons inside styled card groups** | Placing an inner button with `border-radius: 5px` inside hollow layout padding or labels with square borders exposes the parent container's transparent background or window canvas through corner gaps (layout groups paint nothing). | Keep the separate inset pill look by baking the card surface + border + rounded pill into one supersampled PNG (`generate_ui_buttons.py` → `assets/ui/card_btn_*.png` and `deck_*.png`) and set it as the button's `background-image` (with `border: none`, `background-repeat: no-repeat`) so Qt only draws the text on top. Use `:hover` / `:pressed` rules with alternate images for states. (Fusion's Qt stylesheet accepts `url('d:/path with spaces/x.png')`.) |
| **Upper deck buttons top-aligned with dark strip underneath or dark hole in hidden slots** | In Fusion's Qt `UIManager`, `ui:HGroup` (`QBoxLayout`) does not paint a background color, top-aligns `28px` buttons inside a `36px` row (exposing `8px` of `#11141d` window canvas below each button), and retains empty unpainted space when child slots have `Visible = false`. Also, `border-top-left-radius: 8px` on a `7px`-tall `QLabel` cap is ignored by Qt (`8px > 7px`). | Make every widget in the `840 × 44` `UpperDeck` `HGroup` full height (`44px`), keep all slots `Visible = true` with fixed widths summing to `840px`, and use 8× supersampled `w × 44` PNG `background-image` slices (`deck_*.png`) that bake the `#212636` deck surface, `1px` `#363f58` top/bottom border, `8px` outer rounded corners, and `28px`-tall centered (`y = 8..36`) beveled pills. |
| **Hovering on a PNG-styled `QPushButton` causes a black-out effect** | If the `QPushButton:hover` stylesheet references a `background-image: url(...)` filename that does not exist on disk (e.g., `_hover.png` when the generator wrote `_normal_hover.png`) and `background-color` is `transparent`, Qt clears the normal background image on hover and exposes the dark `#11141d` window canvas. | Ensure every `:hover` and `:pressed` state image filename (`_normal.png`, `_hover.png`, `_pressed.png`, `_selected.png`, `_selected_hover.png`) matches `generate_ui_buttons.py` and set `background-color: #212636;` as a solid fallback. |
| **Flat, dull button borders in Qt UIManager** | Flat 1px solid borders lack depth, looking harsh and non-tactile. | Apply subtle top-to-bottom depth gradients (`qlineargradient`), top rim highlight bevels (`border-top: 1px solid <highlight>`), and grounded bottom shadows (`border-bottom: 1px solid <shadow>`) to create a luxurious beveled finish. |

---

## 5. Active Task List (To-Do & Backlog)

### Completed
- [x] **12-Point Support (`A`–`L`) & Hover Black-Out Fix (v3.0)**: Fixed hover black-out on sequence point buttons by aligning `_hover.png` / `_selected_hover.png` filenames between `generate_ui_buttons.py` and `CurveBrowser.lua` and setting `#212636` fallback background color. Expanded `build_setting.py`, `RectMorph_Mask_Pro.setting`, `generate_ui_buttons.py`, and `CurveBrowser.lua` to support 12 points (`Start · A` + 11 transitions `A➔B` through `K➔L` + right-corner `− Remove` inside the `840 × 44` upper deck).
- [x] **Seamless `840 × 44` Baked-PNG Upper Deck, Right-Corner `− Remove` & Inspector `Direction` Control (v2.9)**: Removed `DIRECTION` from the window (controlled from each transition point's `Direction` control in the Inspector tab, synced live via `InspectorSyncTimer`). Fitted `− Remove` permanently in the right corner of the upper deck. Rendered the entire `840 × 44` upper deck from 8× supersampled full-height (`44px`) PNG slices (`deck_*.png`) so outer `8px` corners, centered `28px` beveled pills (`y = 8..36`), and unused slots are 100% seamless with zero bottom cutoffs or dark gaps.
- [x] **Calm Selected States & Neutral Remove (User Preference)**: Replaced flashy neon fills/borders on selected card, `✓ Active` pill, selected sequence pill, and badge with a muted dark-sage fill + sage-lime outline. `− Remove` is neutral slate (rose hint on hover only). Do **not** reintroduce solid neon (`#9aff1c`) fills or red-filled buttons.
- [x] **Separate Rounded `Apply` / `✓ Active` Pills Restored (User Preference)**: Reverted the full-width card-bottom bar back to a separate inset rounded pill, rendered via baked PNG `background-image` so corners stay artifact-free. Do **not** switch back to the full-width bar.
- [x] **Luxury Button Bevels & Flawless Corner Radii**: Replaced flat 1px borders with top-to-bottom depth gradients (`qlineargradient`), top rim highlight chamfers, and grounded bottom shadows. Eliminated all dark corner clipping artifacts by redesigning curve cards into unified 3-part layout with full-width bottom-capped Apply buttons and smooth 4px/5px/8px corners across all buttons, dropdowns, and badges.
- [x] **Per-Point `Set = Playhead` in Inspector**: Added `Set = Playhead` button directly underneath the `Frame` slider for every point (A through H), writing `comp.CurrentTime` to the point's frame and updating timeline keyframes and viewer handles.
- [x] **Sequencer Window De-Clutter**: Removed the bottom telemetry text and the `FRAME` spinbox from the window, keeping only the Sequence pipeline, active transition badge, Direction dropdown, and 10 curve cards.
- [x] **Default Direction Set to `Ease Out` (0)**: Configured all points (`PtA_Dir`–`PtH_Dir`), expression fallbacks, sequencer window initialization, card thumbnails, and new point creation to default to `Ease Out` (`0`).
- [x] Verified testing workflow in Fusion Studio / Fusion page via direct clipboard paste (`Set-Clipboard`).
- [x] 100% DaVinci Resolve Free compatibility verified and audited.
- [x] Created `package_drfx.py` automated repackaging script.
- [x] Eliminated ugly expression boxes from Inspector via `MacroOperator` encapsulation.
- [x] Context-Aware Dynamic Curve Controls: `Intensity` only appears for Back & Elastic; `Frequency` only appears for Elastic. Both remain hidden for all other 9 curves.
- [x] **Live Hot-Reload Replacement**: Automated instant node replacement directly inside active Fusion comp via API, preserving grid position and downstream mask wiring.
- [x] **Landscape Curve & Point Sequencer Window (v2.1)**:
  - Custom colored dark-indigo Windows title bar (`#1b2234`) via LuaJIT `ffi` + `DwmSetWindowAttribute`.
  - Refined `1px solid` strokes and zero right-side clipping (`868 x 376`).
  - In-line `+ ADD` (`highestActive + 1`) and `− REMOVE` (`highestActive + 2`) sequence pipeline.
  - Lighter-colored card boxes (`#212636` idle / `#1e2e18` active) wrapping each curve graph, curve name, and `Apply` (`✓ Active`) button together.
  - Removed slow IPC `Width`/`Height` window sliders in favor of native 60fps Preview Viewer handles and Inspector sliders.
- [x] **Streamlined Clean Inspector**: Single `📈 Open Curve & Point Sequencer` button at the top of the Inspector below `Filter`, `SoftEdge`, `BorderWidth`, `Invert`, `Solid`, and `Center`; removed redundant per-point `Set = Playhead`, `Go to Frame`, `Open Visual Curve Browser`, `+ Add Point`, and `- Remove Point` buttons.
- [x] **Restored `Filter` Parameter at Top of Inspector**: Restored `Filter` (`Fast Gaussian`, `Box`, `Bartlett`, `Multi-box`, `Gaussian`) at the top of the Inspector alongside `SoftEdge`, `BorderWidth`, `Invert`, `Solid`, and `Center`.
- [x] **Interactive On-Screen Preview Viewer Handles**: Bound `PtA`–`PtH` (`Width`, `Height`, `Corner`) to `RectangleControl` (`PC_ControlGroup = 1..8`, `PC_ControlID = 0, 1, 2`) and suppressed `RectMorphMaskInternal`'s locked expression handles so users can drag mask edges directly in the Fusion Preview Viewer.
- [x] **Rollback Checkpoint Created**: Git tag `v1.3-stable` committed and verified physical snapshot in `backups/v1.3_stable/`.
- [x] **Clean UI & Per-Point Bottom Add/Remove Buttons**: Started with only Point 1 (A) and Point 2 (B) visible, and placed `+ Add Point` / `- Remove Point` at the bottom of every point's parameter section.
- [x] **Timeline Keyframe Visualization**: Added `RectMorphKeyframes` (`BezierSpline`) linked to hidden `TimelineMarks` input so every active point displays a keyframe tick mark on the Fusion timeline ruler.

### High Priority / Next Up
- [ ] Add Center (X, Y) morphing support to match Width, Height, and Corner radius.
- [ ] Add Angle / Rotation morphing support.

### Medium Priority
- [ ] Refactor duplicated Lua expression logic between `Width`, `Height`, and `Corner` into shared utility or cleaner modular expressions.
- [ ] Add preset dropdowns (e.g. "Notification Banner", "Stories 9:16", "Card 16:9", "Icon Square").
