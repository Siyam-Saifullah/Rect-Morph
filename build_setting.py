import os

def generate_setting():
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    def_frames = {'A': 0, 'B': 45, 'C': 90, 'D': 120, 'E': 150, 'F': 180, 'G': 210, 'H': 240, 'I': 270, 'J': 300, 'K': 330, 'L': 360}
    def_widths = {'A': 0.22, 'B': 0.62, 'C': 0.34, 'D': 0.26, 'E': 0.44, 'F': 0.26, 'G': 0.44, 'H': 0.26, 'I': 0.44, 'J': 0.26, 'K': 0.44, 'L': 0.26}
    def_heights = {'A': 0.14, 'B': 0.36, 'C': 0.52, 'D': 0.62, 'E': 0.46, 'F': 0.62, 'G': 0.46, 'H': 0.62, 'I': 0.46, 'J': 0.62, 'K': 0.46, 'L': 0.62}
    def_corners = {'A': 0.08, 'B': 0.24, 'C': 0.45, 'D': 0.45, 'E': 0.45, 'F': 0.45, 'G': 0.45, 'H': 0.45, 'I': 0.45, 'J': 0.45, 'K': 0.45, 'L': 0.45}
    def_anims = {'A': 0, 'B': 4, 'C': 9, 'D': 8, 'E': 9, 'F': 8, 'G': 9, 'H': 8, 'I': 9, 'J': 8, 'K': 9, 'L': 8}
    # Default Direction = 0 (Ease Out) per user preference
    def_dirs = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'H': 0, 'I': 0, 'J': 0, 'K': 0, 'L': 0}
    def_ints = {'B': 1.4, 'C': 1.45, 'D': 1.45, 'E': 1.45, 'F': 1.45, 'G': 1.45, 'H': 1.45, 'I': 1.45, 'J': 1.45, 'K': 1.45, 'L': 1.45}
    def_freqs = {'B': 2.5, 'C': 2.6, 'D': 2.6, 'E': 2.6, 'F': 2.6, 'G': 2.6, 'H': 2.6, 'I': 2.6, 'J': 2.6, 'K': 2.6, 'L': 2.6}

    # Core expression template for Width, Height, Corner
    def make_expr(prop_suffix, fallback_val):
        return (
            f"(function() local pts = {{}}; local letters = {{'A','B','C','D','E','F','G','H','I','J','K','L'}}; "
            f"local defM = {{0,4,9,8,9,8,9,8,9,8,9,8}}; local defD = {{0,0,0,0,0,0,0,0,0,0,0,0}}; "
            f"for idx = 1, 12 do local L = letters[idx]; "
            f"local en = (idx <= 2) or ((self['Pt'..L..'_Enable'] or 0) >= 0.5); "
            f"if en then "
            f"local fVal = self['Pt'..L..'_Frame'] or 0; "
            f"local mVal = math.floor((self['Pt'..L..'_Anim'] or defM[idx]) + 0.5); "
            f"local dVal = math.floor((self['Pt'..L..'_Dir'] or defD[idx]) + 0.5); "
            f"table.insert(pts, {{ f = fVal, v = self['Pt'..L..'_{prop_suffix}'] or 0, m = mVal, d = dVal, amp = self['Pt'..L..'_Intensity'] or 1.4, freq = self['Pt'..L..'_Freq'] or 2.5 }}) "
            f"end end; "
            f"if #pts == 0 then return {fallback_val} end; "
            f"table.sort(pts, function(a, b) return a.f < b.f end); "
            f"if time <= pts[1].f then return pts[1].v end; "
            f"if time >= pts[#pts].f then return pts[#pts].v end; "
            f"local function fOut(u, m, amp, freq) if u <= 0 then return 0 elseif u >= 1 then return 1 end; "
            f"if m == 0 then return u elseif m == 1 then return math.sin((u * math.pi) / 2) "
            f"elseif m == 2 then return 1 - (1 - u)^2 elseif m == 3 then return 1 - (1 - u)^3 "
            f"elseif m == 4 then return 1 - (1 - u)^4 elseif m == 5 then return 1 - (1 - u)^5 "
            f"elseif m == 6 then return 1 - 2^(-10 * u) elseif m == 7 then return math.sqrt(math.max(0, 1 - (u - 1)^2)) "
            f"elseif m == 8 then local c1 = 1.70158 * amp; local c3 = c1 + 1; return 1 + c3 * ((u - 1)^3) + c1 * ((u - 1)^2) "
            f"elseif m == 9 then local p = 0.3 / math.max(0.5, freq * 0.4); return (2^(-10 * u)) * math.sin((u - p / 4) * (2 * math.pi) / p) * amp + 1 "
            f"elseif m == 10 then local n1 = 7.5625; local d1 = 2.75; local x = u; "
            f"if x < 1 / d1 then return n1 * x * x elseif x < 2 / d1 then x = x - 1.5 / d1; return n1 * x * x + 0.75 "
            f"elseif x < 2.5 / d1 then x = x - 2.25 / d1; return n1 * x * x + 0.9375 "
            f"else x = x - 2.625 / d1; return n1 * x * x + 0.984375 end end; return u end; "
            f"local function ease(t, m, d, amp, freq) if m == 0 then return t end; "
            f"if d == 0 then return fOut(t, m, amp, freq) elseif d == 1 then return 1 - fOut(1 - t, m, amp, freq) "
            f"else if t < 0.5 then return 0.5 * (1 - fOut(1 - 2 * t, m, amp, freq)) else return 0.5 + 0.5 * fOut(2 * t - 1, m, amp, freq) end end end; "
            f"for i = 1, #pts - 1 do local p1 = pts[i]; local p2 = pts[i+1]; "
            f"if time >= p1.f and time <= p2.f then local dur = math.max(0.0001, p2.f - p1.f); "
            f"local t = (time - p1.f) / dur; local e = ease(t, p2.m, p2.d, p2.amp, p2.freq); "
            f"return p1.v + (p2.v - p1.v) * e end end; return pts[#pts].v end)()"
        )

    # Shared Lua snippet to sync TimelineMarks keyframes with active points
    sync_keys_lua = (
        "local function syncKeys() "
        "local letters = {'A','B','C','D','E','F','G','H','I','J','K','L'}; "
        "local out = tool.TimelineMarks and tool.TimelineMarks:GetConnectedOutput(); "
        "local sp = out and out:GetTool(); "
        "if not sp then sp = comp:BezierSpline(); tool.TimelineMarks = sp end; "
        "if sp then sp:DeleteKeyFrames(-100000, 100000) end; "
        "for i = 1, 12 do local L = letters[i]; "
        "local en = (i <= 2) or ((tonumber(tgt:GetInput('Pt'..L..'_Enable', t)) or tonumber(tool:GetInput('Pt'..L..'_Enable', t)) or 0) >= 0.5); "
        "if en then local f = math.floor((tonumber(tgt:GetInput('Pt'..L..'_Frame', t)) or tonumber(tool:GetInput('Pt'..L..'_Frame', t)) or 0) + 0.5); "
        "pcall(function() tool.TimelineMarks[f] = i end); pcall(function() tgt.TimelineMarks[f] = i end) end end end; "
    )

    # Shared Lua snippet to activate on-screen Viewer RectangleControl for a target point index (1..12)
    set_active_pc_lua = (
        "local function setActivePC(selIdx) "
        "local letters = {'A','B','C','D','E','F','G','H','I','J','K','L'}; "
        "pcall(function() tgt.Width:SetAttrs({ INPB_PC_Visible = false }) end); "
        "pcall(function() tgt.Height:SetAttrs({ INPB_PC_Visible = false }) end); "
        "pcall(function() tgt.CornerRadius:SetAttrs({ INPB_PC_Visible = false }) end); "
        "for i = 1, 12 do local pL = letters[i]; local showPC = (i == selIdx); "
        "for _, p in ipairs({'Width','Height','Corner'}) do local cn = 'Pt'..pL..'_'..p; "
        "pcall(function() tool[cn]:SetAttrs({ INPB_PC_Visible = showPC }) end); "
        "pcall(function() tgt[cn]:SetAttrs({ INPB_PC_Visible = showPC }) end) end end end; "
    )

    # Streamlined point control suffixes (clean Inspector with per-point Set = Playhead button)
    point_ctrl_suffixes = [
        "Group", "Frame", "SetFrameBtn", "Anim", "Dir", "Intensity", "Freq", "Width", "Height", "Corner"
    ]

    def make_frame_change_lua(idx):
        return (
            "local t = comp.CurrentTime or 0; local tgt = comp:FindTool('RectMorphMaskInternal') or tool.RectMorphMaskInternal or tool; "
            + sync_keys_lua + set_active_pc_lua + f"syncKeys(); setActivePC({idx})"
        )

    def make_set_frame_btn_lua(idx, L):
        return (
            "local t = comp.CurrentTime or 0; local tgt = comp:FindTool('RectMorphMaskInternal') or tool.RectMorphMaskInternal or tool; "
            + sync_keys_lua + set_active_pc_lua
            + f"pcall(function() tool:SetInput('Pt{L}_Frame', t, t) end); "
            + f"pcall(function() tool.Pt{L}_Frame[t] = t end); "
            + f"pcall(function() tgt:SetInput('Pt{L}_Frame', t, t) end); "
            + f"pcall(function() tgt.Pt{L}_Frame[t] = t end); "
            + f"syncKeys(); setActivePC({idx})"
        )

    def make_top_curve_btn_lua():
        return (
            "local tgt = comp:FindTool('RectMorphMaskInternal') or tool.RectMorphMaskInternal or tool; "
            + set_active_pc_lua + "setActivePC(2); "
            "local s = comp:MapPath('Scripts:/Comp/Rect Morph Pro/Curve Browser.lua'); "
            "if not bmd.fileexists(s) then s = comp:MapPath('Scripts:/Comp/Shape Morph Pro/Curve Browser.lua') end; "
            "if not bmd.fileexists(s) then s = [[d:/02 Code/01 Drafting Projects/Shape Morph Pro/scripts/CurveBrowser.lua]] end; "
            "comp:RunScript(s)"
        )

    def make_anim_change_lua(L):
        return (
            "local t = comp.CurrentTime or 0; "
            f"local a = math.floor((tool:GetInput('Pt{L}_Anim', t) or tool.Pt{L}_Anim[t] or 0) + 0.5); "
            "local b = (a == 8); local e = (a == 9); local si = (b or e); local sf = e; "
            "local tgt = comp:FindTool('RectMorphMaskInternal') or tool.RectMorphMaskInternal or tool; "
            f"pcall(function() tool.Pt{L}_Intensity:SetAttrs({{ INPB_IC_Visible = si }}) end); "
            f"pcall(function() tool.Pt{L}_Freq:SetAttrs({{ INPB_IC_Visible = sf }}) end); "
            f"pcall(function() tgt.Pt{L}_Intensity:SetAttrs({{ INPB_IC_Visible = si }}) end); "
            f"pcall(function() tgt.Pt{L}_Freq:SetAttrs({{ INPB_IC_Visible = sf }}) end)"
        )

    # 1. Build InstanceInputs and UserControls in matching order
    instance_inputs = []
    user_controls = []
    internal_inputs = [
        '\t\t\t\t\t\tFilter = Input { Value = FuID { "Fast Gaussian" }, },',
        '\t\t\t\t\t\tSoftEdge = Input { Value = 0, },',
        '\t\t\t\t\t\tBorderWidth = Input { Value = 0, },',
        '\t\t\t\t\t\tInvert = Input { Value = 0, },',
        '\t\t\t\t\t\tSolid = Input { Value = 1, },',
        f'\t\t\t\t\t\tWidth = Input {{\n\t\t\t\t\t\t\tValue = 0.22,\n\t\t\t\t\t\t\tExpression = "{make_expr("Width", 0.25)}",\n\t\t\t\t\t\t}},',
        f'\t\t\t\t\t\tHeight = Input {{\n\t\t\t\t\t\t\tValue = 0.14,\n\t\t\t\t\t\t\tExpression = "{make_expr("Height", 0.25)}",\n\t\t\t\t\t\t}},',
        f'\t\t\t\t\t\tCornerRadius = Input {{\n\t\t\t\t\t\t\tValue = 0.08,\n\t\t\t\t\t\t\tExpression = "{make_expr("Corner", 0.08)}",\n\t\t\t\t\t\t}},',
        '\t\t\t\t\t\tTimelineMarks = Input {\n\t\t\t\t\t\t\tSourceOp = "RectMorphKeyframes",\n\t\t\t\t\t\t\tSource = "Value",\n\t\t\t\t\t\t},',
    ]

    def add_inst(name, src, vis=True, pc_group=None, pc_id=None):
        vis_str = "" if vis else "\n\t\t\t\t\tIC_Visible = false,"
        pc_str = ""
        if pc_group is not None and pc_id is not None:
            pc_str = f"\n\t\t\t\t\tPC_ControlGroup = {pc_group},\n\t\t\t\t\tPC_ControlID = {pc_id},"
        instance_inputs.append(
            f'\t\t\t\t{name} = InstanceInput {{\n'
            f'\t\t\t\t\tSourceOp = "RectMorphMaskInternal",\n'
            f'\t\t\t\t\tSource = "{src}",{vis_str}{pc_str}\n'
            f'\t\t\t\t}},'
        )

    # Expose top mask parameters including Filter at the very top of the Inspector
    for m_ctrl in ["Filter", "SoftEdge", "BorderWidth", "Invert", "Solid", "Center"]:
        add_inst(m_ctrl, m_ctrl, True)

    # Single prominent Curve & Point Sequencer button at top of Inspector
    add_inst("OpenCurveBrowserBtn", "OpenCurveBrowserBtn", True)
    user_controls.append(f'''\t\t\t\tOpenCurveBrowserBtn = {{
\t\t\t\t\tLINKS_Name = "📈 Open Curve & Point Sequencer",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "ButtonControl",
\t\t\t\t\tBTNCS_Execute = "{make_top_curve_btn_lua()}",
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},''')

    # Hidden TimelineMarks input on MacroOperator so keyframe ticks show on timeline ruler
    add_inst("TimelineMarks", "TimelineMarks", False)
    user_controls.append('''\t\t\t\tTimelineMarks = {
\t\t\t\t\tLINKS_Name = "Timeline Keyframes",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "SliderControl",
\t\t\t\t\tINP_Default = 1,
\t\t\t\t\tIC_Visible = false,
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t},''')

    # Point A (Start State) - Clean Inspector: Group, Frame, Width, Height, Corner
    internal_inputs.extend([
        '\t\t\t\t\t\tPtA_Group = Input { Value = 1, },',
        f'\t\t\t\t\t\tPtA_Frame = Input {{ Value = {def_frames["A"]}, }},',
        f'\t\t\t\t\t\tPtA_Width = Input {{ Value = {def_widths["A"]}, }},',
        f'\t\t\t\t\t\tPtA_Height = Input {{ Value = {def_heights["A"]}, }},',
        f'\t\t\t\t\t\tPtA_Corner = Input {{ Value = {def_corners["A"]}, }},',
    ])

    for s in ["Group", "Frame", "SetFrameBtn", "Width", "Height", "Corner"]:
        if s == "Width":
            add_inst(f"PtA_{s}", f"PtA_{s}", True, pc_group=1, pc_id=0)
        elif s == "Height":
            add_inst(f"PtA_{s}", f"PtA_{s}", True, pc_group=1, pc_id=1)
        elif s == "Corner":
            add_inst(f"PtA_{s}", f"PtA_{s}", True, pc_group=1, pc_id=2)
        else:
            add_inst(f"PtA_{s}", f"PtA_{s}", True)

    user_controls.append(f'''\t\t\t\tPtA_Group = {{
\t\t\t\t\tLINKS_Name = "Start  ·  A",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "LabelControl",
\t\t\t\t\tLBLC_DropDownButton = true,
\t\t\t\t\tLBLC_NumInputs = 5,
\t\t\t\t\tINP_Default = 1,
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPtA_Frame = {{
\t\t\t\t\tLINKS_Name = "Frame",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "SliderControl",
\t\t\t\t\tINP_Integer = true,
\t\t\t\t\tINP_Default = {def_frames['A']},
\t\t\t\t\tINP_MinScale = 0,
\t\t\t\t\tINP_MaxScale = 300,
\t\t\t\t\tINP_DoNotifyChanged = true,
\t\t\t\t\tINPS_ExecuteOnChange = "{make_frame_change_lua(1)}",
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPtA_SetFrameBtn = {{
\t\t\t\t\tLINKS_Name = "Set = Playhead",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "ButtonControl",
\t\t\t\t\tBTNCS_Execute = "{make_set_frame_btn_lua(1, 'A')}",
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPtA_Width = {{
\t\t\t\t\tLINKS_Name = "Width",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "SliderControl",
\t\t\t\t\tINPID_PreviewControl = "RectangleControl",
\t\t\t\t\tPC_ControlGroup = 1,
\t\t\t\t\tPC_ControlID = 0,
\t\t\t\t\tPC_Visible = true,
\t\t\t\t\tRCD_SetX = 0.5,
\t\t\t\t\tRCD_SetY = 0.5,
\t\t\t\t\tINP_Default = {def_widths['A']},
\t\t\t\t\tINP_MinScale = 0.0,
\t\t\t\t\tINP_MaxScale = 1.0,
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPtA_Height = {{
\t\t\t\t\tLINKS_Name = "Height",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "SliderControl",
\t\t\t\t\tINPID_PreviewControl = "RectangleControl",
\t\t\t\t\tPC_ControlGroup = 1,
\t\t\t\t\tPC_ControlID = 1,
\t\t\t\t\tPC_Visible = true,
\t\t\t\t\tRCD_SetX = 0.5,
\t\t\t\t\tRCD_SetY = 0.5,
\t\t\t\t\tINP_Default = {def_heights['A']},
\t\t\t\t\tINP_MinScale = 0.0,
\t\t\t\t\tINP_MaxScale = 1.0,
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPtA_Corner = {{
\t\t\t\t\tLINKS_Name = "Corner",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "SliderControl",
\t\t\t\t\tINPID_PreviewControl = "RectangleControl",
\t\t\t\t\tPC_ControlGroup = 1,
\t\t\t\t\tPC_ControlID = 2,
\t\t\t\t\tPC_Visible = true,
\t\t\t\t\tRCD_SetX = 0.5,
\t\t\t\t\tRCD_SetY = 0.5,
\t\t\t\t\tINP_Default = {def_corners['A']},
\t\t\t\t\tINP_MinScale = 0.0,
\t\t\t\t\tINP_MaxScale = 1.0,
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},''')

    # Points B through L (Point B visible at start; C..L hidden at start)
    for idx in range(2, 13):
        L = letters[idx - 1]
        is_b = (idx == 2)
        pt_vis = True if is_b else False
        en_val = 1 if is_b else 0
        grp_val = 1 if is_b else 0
        a_def = def_anims[L]
        int_vis = pt_vis and (a_def in [8, 9])
        freq_vis = pt_vis and (a_def == 9)

        internal_inputs.extend([
            f'\t\t\t\t\t\tPt{L}_Group = Input {{ Value = {grp_val}, }},',
            f'\t\t\t\t\t\tPt{L}_Enable = Input {{ Value = {en_val}, }},',
            f'\t\t\t\t\t\tPt{L}_Frame = Input {{ Value = {def_frames[L]}, }},',
            f'\t\t\t\t\t\tPt{L}_Anim = Input {{ Value = {a_def}, }},',
            f'\t\t\t\t\t\tPt{L}_Dir = Input {{ Value = {def_dirs[L]}, }},',
            f'\t\t\t\t\t\tPt{L}_Intensity = Input {{ Value = {def_ints[L]}, }},',
            f'\t\t\t\t\t\tPt{L}_Freq = Input {{ Value = {def_freqs[L]}, }},',
            f'\t\t\t\t\t\tPt{L}_Width = Input {{ Value = {def_widths[L]}, }},',
            f'\t\t\t\t\t\tPt{L}_Height = Input {{ Value = {def_heights[L]}, }},',
            f'\t\t\t\t\t\tPt{L}_Corner = Input {{ Value = {def_corners[L]}, }},',
        ])

        for s in point_ctrl_suffixes:
            c_vis = pt_vis
            if s == "Intensity":
                c_vis = int_vis
            elif s == "Freq":
                c_vis = freq_vis
            if s == "Width":
                add_inst(f"Pt{L}_{s}", f"Pt{L}_{s}", c_vis, pc_group=idx, pc_id=0)
            elif s == "Height":
                add_inst(f"Pt{L}_{s}", f"Pt{L}_{s}", c_vis, pc_group=idx, pc_id=1)
            elif s == "Corner":
                add_inst(f"Pt{L}_{s}", f"Pt{L}_{s}", c_vis, pc_group=idx, pc_id=2)
            else:
                add_inst(f"Pt{L}_{s}", f"Pt{L}_{s}", c_vis)

        # Hidden Enable control (used internally by expression and Add/Remove in window)
        add_inst(f"Pt{L}_Enable", f"Pt{L}_Enable", False)

        vis_tag = "" if pt_vis else "\n\t\t\t\t\tIC_Visible = false,"
        int_vis_tag = "" if int_vis else "\n\t\t\t\t\tIC_Visible = false,"
        freq_vis_tag = "" if freq_vis else "\n\t\t\t\t\tIC_Visible = false,"

        prev_L = letters[idx - 2]
        user_controls.append(f'''\t\t\t\tPt{L}_Group = {{
\t\t\t\t\tLINKS_Name = "{prev_L}  ➔  {L}",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "LabelControl",
\t\t\t\t\tLBLC_DropDownButton = true,
\t\t\t\t\tLBLC_NumInputs = 9,
\t\t\t\t\tINP_Default = {grp_val},{vis_tag}
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPt{L}_Frame = {{
\t\t\t\t\tLINKS_Name = "Frame",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "SliderControl",
\t\t\t\t\tINP_Integer = true,
\t\t\t\t\tINP_Default = {def_frames[L]},
\t\t\t\t\tINP_MinScale = 0,
\t\t\t\t\tINP_MaxScale = 300,{vis_tag}
\t\t\t\t\tINP_DoNotifyChanged = true,
\t\t\t\t\tINPS_ExecuteOnChange = "{make_frame_change_lua(idx)}",
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPt{L}_SetFrameBtn = {{
\t\t\t\t\tLINKS_Name = "Set = Playhead",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "ButtonControl",
\t\t\t\t\tBTNCS_Execute = "{make_set_frame_btn_lua(idx, L)}",{vis_tag}
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPt{L}_Anim = {{
\t\t\t\t\tLINKS_Name = "Curve",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "MultiButtonControl",
\t\t\t\t\tINP_Integer = true,
\t\t\t\t\tINP_Default = {a_def},{vis_tag}
\t\t\t\t\tINP_DoNotifyChanged = true,
\t\t\t\t\tINPS_ExecuteOnChange = "{make_anim_change_lua(L)}",
\t\t\t\t\tMBTNC_ShowBasicButton = true,
\t\t\t\t\tMBTNC_StretchToFit = true,
\t\t\t\t\tMBTNC_ShowName = true,
\t\t\t\t\t{{ MBTNC_AddButton = "Linear", MBTNCD_ButtonWidth = 0.25 }},
\t\t\t\t\t{{ MBTNC_AddButton = "Sine", MBTNCD_ButtonWidth = 0.25 }},
\t\t\t\t\t{{ MBTNC_AddButton = "Quad", MBTNCD_ButtonWidth = 0.25 }},
\t\t\t\t\t{{ MBTNC_AddButton = "Cubic", MBTNCD_ButtonWidth = 0.25 }},
\t\t\t\t\t{{ MBTNC_AddButton = "Quart", MBTNCD_ButtonWidth = 0.25 }},
\t\t\t\t\t{{ MBTNC_AddButton = "Quint", MBTNCD_ButtonWidth = 0.25 }},
\t\t\t\t\t{{ MBTNC_AddButton = "Expo", MBTNCD_ButtonWidth = 0.25 }},
\t\t\t\t\t{{ MBTNC_AddButton = "Circ", MBTNCD_ButtonWidth = 0.25 }},
\t\t\t\t\t{{ MBTNC_AddButton = "Back", MBTNCD_ButtonWidth = 0.33 }},
\t\t\t\t\t{{ MBTNC_AddButton = "Elastic", MBTNCD_ButtonWidth = 0.34 }},
\t\t\t\t\t{{ MBTNC_AddButton = "Bounce", MBTNCD_ButtonWidth = 0.33 }},
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPt{L}_Dir = {{
\t\t\t\t\tLINKS_Name = "Direction",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "MultiButtonControl",
\t\t\t\t\tINP_Integer = true,
\t\t\t\t\tINP_Default = {def_dirs[L]},{vis_tag}
\t\t\t\t\tMBTNC_ShowBasicButton = true,
\t\t\t\t\tMBTNC_StretchToFit = true,
\t\t\t\t\tMBTNC_ShowName = true,
\t\t\t\t\t{{ MBTNC_AddButton = "Ease Out", MBTNCD_ButtonWidth = 0.33 }},
\t\t\t\t\t{{ MBTNC_AddButton = "Ease In", MBTNCD_ButtonWidth = 0.33 }},
\t\t\t\t\t{{ MBTNC_AddButton = "Ease In-Out", MBTNCD_ButtonWidth = 0.34 }},
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPt{L}_Intensity = {{
\t\t\t\t\tLINKS_Name = "Intensity",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "SliderControl",
\t\t\t\t\tINP_Default = {def_ints[L]},
\t\t\t\t\tINP_MinScale = 0.2,
\t\t\t\t\tINP_MaxScale = 3.0,{int_vis_tag}
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPt{L}_Freq = {{
\t\t\t\t\tLINKS_Name = "Frequency",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "SliderControl",
\t\t\t\t\tINP_Default = {def_freqs[L]},
\t\t\t\t\tINP_MinScale = 0.5,
\t\t\t\t\tINP_MaxScale = 6.0,{freq_vis_tag}
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPt{L}_Width = {{
\t\t\t\t\tLINKS_Name = "Width",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "SliderControl",
\t\t\t\t\tINPID_PreviewControl = "RectangleControl",
\t\t\t\t\tPC_ControlGroup = {idx},
\t\t\t\t\tPC_ControlID = 0,
\t\t\t\t\tPC_Visible = false,
\t\t\t\t\tRCD_SetX = 0.5,
\t\t\t\t\tRCD_SetY = 0.5,
\t\t\t\t\tINP_Default = {def_widths[L]},
\t\t\t\t\tINP_MinScale = 0.0,
\t\t\t\t\tINP_MaxScale = 1.0,{vis_tag}
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPt{L}_Height = {{
\t\t\t\t\tLINKS_Name = "Height",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "SliderControl",
\t\t\t\t\tINPID_PreviewControl = "RectangleControl",
\t\t\t\t\tPC_ControlGroup = {idx},
\t\t\t\t\tPC_ControlID = 1,
\t\t\t\t\tPC_Visible = false,
\t\t\t\t\tRCD_SetX = 0.5,
\t\t\t\t\tRCD_SetY = 0.5,
\t\t\t\t\tINP_Default = {def_heights[L]},
\t\t\t\t\tINP_MinScale = 0.0,
\t\t\t\t\tINP_MaxScale = 1.0,{vis_tag}
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPt{L}_Corner = {{
\t\t\t\t\tLINKS_Name = "Corner",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "SliderControl",
\t\t\t\t\tINPID_PreviewControl = "RectangleControl",
\t\t\t\t\tPC_ControlGroup = {idx},
\t\t\t\t\tPC_ControlID = 2,
\t\t\t\t\tPC_Visible = false,
\t\t\t\t\tRCD_SetX = 0.5,
\t\t\t\t\tRCD_SetY = 0.5,
\t\t\t\t\tINP_Default = {def_corners[L]},
\t\t\t\t\tINP_MinScale = 0.0,
\t\t\t\t\tINP_MaxScale = 1.0,{vis_tag}
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},
\t\t\t\tPt{L}_Enable = {{
\t\t\t\t\tLINKS_Name = "Enable Point {idx} ({L})",
\t\t\t\t\tLINKID_DataType = "Number",
\t\t\t\t\tINPID_InputControl = "CheckboxControl",
\t\t\t\t\tCBC_TriState = false,
\t\t\t\t\tINP_Integer = true,
\t\t\t\t\tINP_Default = {en_val},
\t\t\t\t\tIC_Visible = false,
\t\t\t\t\tICS_ControlPage = "Controls",
\t\t\t\t}},''')

    inputs_block = "\n".join(instance_inputs)
    internal_inps_block = "\n".join(internal_inputs)
    uc_block = "\n".join(user_controls)

    setting_str = f"""{{
\tTools = ordered() {{
\t\tRectMorphMaskPro = MacroOperator {{
\t\t\tCtrlWZoom = false,
\t\t\tNameSet = true,
\t\t\tCustomData = {{
\t\t\t\tPath = {{
\t\t\t\t\tMap = {{
\t\t\t\t\t\t["Setting:"] = "Templates:/Fusion/Tools/"
\t\t\t\t\t}}
\t\t\t\t}},
\t\t\t}},
\t\t\tInputs = ordered() {{
{inputs_block}
\t\t\t}},
\t\t\tOutputs = {{
\t\t\t\tMask = InstanceOutput {{
\t\t\t\t\tSourceOp = "RectMorphMaskInternal",
\t\t\t\t\tSource = "Mask",
\t\t\t\t}}
\t\t\t}},
\t\t\tViewInfo = GroupInfo {{ Pos = {{ 440, 148.5 }} }},
\t\t\tTools = ordered() {{
\t\t\t\tRectMorphKeyframes = BezierSpline {{
\t\t\t\t\tSplineColor = {{ Red = 145, Green = 255, Blue = 25 }},
\t\t\t\t\tCtrlWShown = false,
\t\t\t\t\tNameSet = true,
\t\t\t\t\tKeyFrames = {{
\t\t\t\t\t\t[0] = {{ 1, RH = {{ 15, 1.33333333333333 }} }},
\t\t\t\t\t\t[45] = {{ 2, LH = {{ 30, 1.66666666666667 }} }}
\t\t\t\t\t}}
\t\t\t\t}},
\t\t\t\tRectMorphMaskInternal = RectangleMask {{
\t\t\t\t\tCtrlWZoom = false,
\t\t\t\t\tCtrlWShown = false,
\t\t\t\t\tNameSet = true,
\t\t\t\t\tInputs = {{
{internal_inps_block}
\t\t\t\t\t}},
\t\t\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 440, 148.5 }} }},
\t\t\t\t\tUserControls = ordered() {{
{uc_block}
\t\t\t\t\t}}
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t}},
\tActiveTool = "RectMorphMaskPro"
}}
"""

    open_c = setting_str.count('{')
    close_c = setting_str.count('}')
    assert open_c == close_c, f"Brace mismatch: {open_c} != {close_c}"

    with open('RectMorph_Mask_Pro.setting', 'w', encoding='utf-8') as f:
        f.write(setting_str)

    print(f"Successfully generated RectMorph_Mask_Pro.setting! (Braces: {open_c})")

if __name__ == '__main__':
    generate_setting()
