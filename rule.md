# Development Rules & Guidelines: Shape Morph Pro

This document governs the engineering standards, best practices, strict rules, common pitfalls, and tracking tasks for the **Shape Morph Pro** (`RectMorph Mask Pro`) DaVinci Resolve plugin.

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

---

## 5. Active Task List (To-Do & Backlog)

### Completed
- [x] Verified testing workflow in Fusion Studio / Fusion page via direct clipboard paste (`Set-Clipboard`).
- [x] 100% DaVinci Resolve Free compatibility verified and audited.
- [x] Created `package_drfx.py` automated repackaging script.
- [x] Eliminated ugly expression boxes from Inspector via `MacroOperator` encapsulation.
- [x] Context-Aware Dynamic Curve Controls: `Intensity` only appears for Back & Elastic; `Frequency` only appears for Elastic. Both remain hidden for all other 9 curves.
- [x] **Live Hot-Reload Replacement**: Automated instant node replacement directly inside active Fusion comp via API, preserving grid position and downstream mask wiring.

### High Priority / Next Up
- [ ] Clean up / remove redundant 'Filter' dropdown from top of Inspector.
- [ ] Add Center (X, Y) morphing support to match Width, Height, and Corner radius.
- [ ] Add Angle / Rotation morphing support.

### Medium Priority
- [ ] Refactor duplicated Lua expression logic between `Width`, `Height`, and `Corner` into shared utility or cleaner modular expressions.
- [ ] Add preset dropdowns (e.g. "Notification Banner", "Stories 9:16", "Card 16:9", "Icon Square").
