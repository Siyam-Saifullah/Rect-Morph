-- ==============================================================================
-- Curve Browser - Rect Morph Pro (v3.0 12-Point Seamless Upper Deck & Inspector Direction)
-- Landscape Visual Easing & Point Sequencer with Seamless Lighter Card Boxes
-- ==============================================================================

local f_app = fu or fusion or app
local ui = f_app.UIManager
local disp = bmd.UIDispatcher(ui)

-- Exhaustive cleanup of any existing Curve Browser or test windows
for _, wName in ipairs({
    "CurveBrowserWin", "VisualCurveBrowserWin", "ShapeMorphCurveBrowser",
    "ShapeMorphCurveBrowserV2", "ShapeMorphFlowBrowser", "TestBtnIconCompare",
    "TestBtnIconWin", "TestBtnIconWin2", "TestGapWin", "TestHideWin",
    "TestHideWin2", "TestHideWin3", "TestHideWin4", "TestHideGroupWin",
    "TestAddRemoveWin", "TestHideNoSizeWin", "TestOnWin", "TestSliderWin",
    "TestSliderWin2", "TestCardBoxWin", "TestCardBoxWin2"
}) do
    local existing = ui:FindWindow(wName)
    local guard = 0
    while existing and guard < 25 do
        guard = guard + 1
        pcall(function() existing.WindowTitle = "Closed" end)
        pcall(function() existing:Hide() end)
        pcall(function() ui:QueueEvent(existing, "Close", {}) end)
        pcall(function() existing.ID = "Closed_" .. wName .. "_" .. tostring(guard) .. "_" .. tostring(os.clock()) end)
        existing = ui:FindWindow(wName)
    end
end

local curComp = f_app:GetCurrentComp()
local WIN_TITLE = "Rect Morph Pro - Curve & Point Sequencer"

-- Locate asset paths: check DaVinci PathMaps, script-relative directory, and dev path fallback
local assetDir = "d:/02 Code/01 Drafting Projects/Shape Morph Pro/assets/curves/"
local uiDir = "d:/02 Code/01 Drafting Projects/Shape Morph Pro/assets/ui/"

local function findAssets()
    local candidates = {
        curComp and curComp:MapPath("Scripts:/Comp/Rect Morph Pro/assets/"),
        curComp and curComp:MapPath("Scripts:/Comp/RectMorph Pro/assets/"),
        curComp and curComp:MapPath("Scripts:/Comp/Shape Morph Pro/assets/"),
    }
    local src = debug.getinfo(1, "S").source
    if src and src:sub(1,1) == "@" then
        local sPath = src:sub(2)
        local sDir = sPath:match("(.*[/\\])")
        if sDir then
            table.insert(candidates, sDir .. "assets/")
            table.insert(candidates, sDir .. "../assets/")
        end
    end
    for _, base in ipairs(candidates) do
        if base and bmd.direxists(base .. "curves") then
            assetDir = base .. "curves/"
            uiDir = base .. "ui/"
            return
        end
    end
end
findAssets()

-- 10 Easing curves in 2 rows x 5 columns (Linear removed per user preference)
local curveList = {
    -- Row 1
    { idx = 1, base = "Sine", row = 1 },
    { idx = 2, base = "Quad", row = 1 },
    { idx = 3, base = "Cubic", row = 1 },
    { idx = 4, base = "Quart", row = 1 },
    { idx = 5, base = "Quint", row = 1 },
    -- Row 2
    { idx = 6, base = "Expo", row = 2 },
    { idx = 7, base = "Circ", row = 2 },
    { idx = 8, base = "Back", row = 2 },
    { idx = 9, base = "Elastic", row = 2 },
    { idx = 10, base = "Bounce", row = 2 },
}

local pointLetters = { "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L" }
local dirPrefixes = { "Ease Out ", "Ease In ", "Ease In-Out " }
local dirSuffixes = { "Out", "In", "InOut" }

-- Track active selection & last synced values (prevents async echo events)
local selectedPointLetter = "B"
local selectedPointIdx = 2
local lastSyncedFrame = 45
local lastSyncedDirIdx = 0
local lastSyncedAnimIdx = -1
local lastPointDirs = {}
local lastPointAnims = {}

-- ==============================================================================
-- Unified Lighter Slate Card Palette (#212636 Cards on #11141d Canvas)
-- ==============================================================================

-- Top Sequence Pipeline Node Buttons inside #212636 Upper Deck (44px full-height slices)
-- Each button's 8x supersampled PNG includes the #212636 deck surface, top/bottom #363f58
-- deck borders, and the centered 28px-tall (y=8..36) 5px-rounded beveled pill.
local function deckBtnStyle(prefix, base, hover, pressed, textColor, hoverText)
    local function bg(name)
        return "background-image: url('" .. uiDir .. prefix .. "_" .. name .. ".png'); background-repeat: no-repeat; background-position: top left;"
    end
    return "QPushButton { background-color: #212636; " .. bg(base) .. " color: " .. textColor .. "; border: none; border-radius: 0px; font-weight: bold; font-size: 10px; padding: 0px 0px 1px 0px; margin: 0px; }"
        .. " QPushButton:hover { " .. bg(hover) .. " color: " .. hoverText .. "; }"
        .. " QPushButton:pressed { " .. bg(pressed) .. " }"
end

local STYLE_NODE1_NORMAL   = deckBtnStyle("deck_btn58", "normal", "hover", "pressed", "#f1f5f9", "#c4f07a")
local STYLE_NODE1_SELECTED = deckBtnStyle("deck_btn58", "selected", "selected_hover", "selected", "#c4f07a", "#d4f79a")

local STYLE_NODE_NORMAL    = deckBtnStyle("deck_btn46", "normal", "hover", "pressed", "#f1f5f9", "#c4f07a")
local STYLE_NODE_SELECTED  = deckBtnStyle("deck_btn46", "selected", "selected_hover", "selected", "#c4f07a", "#d4f79a")
local STYLE_NODE_ADD       = deckBtnStyle("deck_btn46", "add", "add_hover", "pressed", "#b6e36b", "#c4f07a")
local STYLE_NODE_EMPTY     = "QPushButton { background-color: #212636; background-image: url('" .. uiDir .. "deck_empty46.png'); background-repeat: no-repeat; background-position: top left; color: transparent; border: none; border-radius: 0px; padding: 0px; margin: 0px; }"

local STYLE_REM_ACTIVE     = deckBtnStyle("deck_rem66", "normal", "hover", "pressed", "#94a3b8", "#e8a3ac")
local STYLE_REM_DISABLED   = deckBtnStyle("deck_rem66", "disabled", "disabled", "disabled", "#4b566e", "#4b566e")

local STYLE_DECK_LEFT      = "QLabel { background-color: #212636; background-image: url('" .. uiDir .. "deck_left78.png'); background-repeat: no-repeat; background-position: top left; color: #8892b0; border: none; padding: 0px 0px 1px 12px; margin: 0px; font-weight: bold; font-size: 10px; }"
local STYLE_DECK_MID10     = "QLabel { background-color: #212636; background-image: url('" .. uiDir .. "deck_mid10.png'); background-repeat: no-repeat; background-position: top left; color: transparent; border: none; padding: 0px; margin: 0px; }"
local STYLE_DECK_RIGHT     = "QLabel { background-color: #212636; background-image: url('" .. uiDir .. "deck_right12.png'); background-repeat: no-repeat; background-position: top left; color: transparent; border: none; padding: 0px; margin: 0px; }"

local STYLE_ARR_ACTIVE     = "QLabel { background-color: #212636; background-image: url('" .. uiDir .. "deck_mid10.png'); background-repeat: no-repeat; background-position: top left; color: #86b84c; border: none; padding: 0px 0px 1px 0px; margin: 0px; font-weight: bold; }"
local STYLE_ARR_IDLE       = "QLabel { background-color: #212636; background-image: url('" .. uiDir .. "deck_mid10.png'); background-repeat: no-repeat; background-position: top left; color: #4b566e; border: none; padding: 0px 0px 1px 0px; margin: 0px; font-weight: bold; }"
local STYLE_ARR_EMPTY      = "QLabel { background-color: #212636; background-image: url('" .. uiDir .. "deck_mid10.png'); background-repeat: no-repeat; background-position: top left; color: transparent; border: none; padding: 0px; margin: 0px; }"

-- ==============================================================================
-- Unified 3-Part Luxury Card Box Styles (Graph + Title + Separate Rounded Pill Button)
-- ==============================================================================
-- Idle Card Box (#212636 surface, #363f58 border, 8px rounded corners)
local STYLE_TOP_IDLE = "QLabel { background-color: #212636; border-top: 1px solid #363f58; border-left: 1px solid #363f58; border-right: 1px solid #363f58; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; padding: 5px; margin: 0px; }"
local STYLE_MID_IDLE = "QPushButton { background-color: #212636; color: #e2e8f0; border-left: 1px solid #363f58; border-right: 1px solid #363f58; border-top: none; border-bottom: none; border-radius: 0px; padding: 0px 4px; margin: 0px; font-weight: bold; font-size: 11px; } QPushButton:hover { color: #c4f07a; }"
-- Bottom slice = card surface + separate inset rounded pill button, baked into one
-- anti-aliased PNG (generate_ui_buttons.py) so the pill corners never expose the canvas.
local function cardBtnStyle(base, hover, pressed, textColor, hoverText)
    local function bg(name)
        return "background-image: url('" .. uiDir .. "card_btn_" .. name .. ".png'); background-repeat: no-repeat; background-position: top left;"
    end
    return "QPushButton { background-color: transparent; " .. bg(base) .. " color: " .. textColor .. "; border: none; border-radius: 0px; font-weight: bold; font-size: 11px; padding: 1px 0px 6px 0px; margin: 0px; }"
        .. " QPushButton:hover { " .. bg(hover) .. " color: " .. hoverText .. "; }"
        .. " QPushButton:pressed { " .. bg(pressed) .. " }"
end
local STYLE_BOT_IDLE = cardBtnStyle("idle", "idle_hover", "idle_pressed", "#e2e8f0", "#c4f07a")

-- Active Card Box (calm dark sage surface, muted sage-lime border, 8px rounded corners)
local STYLE_TOP_ACTIVE = "QLabel { background-color: #1f2a1d; border-top: 1px solid #5c7f33; border-left: 1px solid #5c7f33; border-right: 1px solid #5c7f33; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; padding: 5px; margin: 0px; }"
local STYLE_MID_ACTIVE = "QPushButton { background-color: #1f2a1d; color: #b6e36b; border-left: 1px solid #5c7f33; border-right: 1px solid #5c7f33; border-top: none; border-bottom: none; border-radius: 0px; padding: 0px 4px; margin: 0px; font-weight: bold; font-size: 11px; }"
local STYLE_BOT_ACTIVE = cardBtnStyle("active", "active_hover", "active", "#c4f07a", "#d4f79a")

-- ==============================================================================
-- Build Upper Deck Master Single-Row Toolbar (Exact 840 x 44 pixels, up to 12 points!)
-- Width sum: 78 + 58 + 11*(10+46) + 10 + 66 + 12 = 840px
-- ==============================================================================
local flowRowWidgets = {}

-- 1. Left Rounded Cap + SEQUENCE Title (78 x 44)
table.insert(flowRowWidgets, ui:Label {
    ID = "DeckLeftCap",
    Text = "SEQUENCE",
    Weight = 0,
    MinimumSize = { 78, 44 },
    MaximumSize = { 78, 44 },
    Alignment = { AlignLeft = true, AlignVCenter = true },
    Font = ui:Font { Family = "Segoe UI", PixelSize = 10, Bold = true },
    StyleSheet = STYLE_DECK_LEFT,
})

-- 2. Slot 1: Start · A (58 x 44)
table.insert(flowRowWidgets, ui:Button {
    ID = "PtBtn_1",
    Text = "Start · A",
    ToolTip = "Select Start State (Point A) & Jump Playhead",
    Weight = 0,
    MinimumSize = { 58, 44 },
    MaximumSize = { 58, 44 },
    Font = ui:Font { Family = "Segoe UI", PixelSize = 10, Bold = true },
    StyleSheet = STYLE_NODE1_NORMAL,
})

-- 3. Slots 2..12: Transitions A ➔ B through K ➔ L (or + Add / empty slot) (11 * (10 + 46) = 616px)
for i = 2, 12 do
    table.insert(flowRowWidgets, ui:Label {
        ID = "PtArr_" .. i,
        Text = "➔",
        Weight = 0,
        MinimumSize = { 10, 44 },
        MaximumSize = { 10, 44 },
        Alignment = { AlignHCenter = true, AlignVCenter = true },
        Font = ui:Font { Family = "Segoe UI", PixelSize = 9, Bold = true },
        StyleSheet = STYLE_ARR_IDLE,
    })
    table.insert(flowRowWidgets, ui:Button {
        ID = "PtBtn_" .. i,
        Text = "",
        Weight = 0,
        MinimumSize = { 46, 44 },
        MaximumSize = { 46, 44 },
        Font = ui:Font { Family = "Segoe UI", PixelSize = 10, Bold = true },
        StyleSheet = STYLE_NODE_NORMAL,
    })
end

-- 4. Right-Side Spacer before Remove button (10 x 44)
table.insert(flowRowWidgets, ui:Label {
    ID = "DeckMidGap",
    Text = "",
    Weight = 0,
    MinimumSize = { 10, 44 },
    MaximumSize = { 10, 44 },
    StyleSheet = STYLE_DECK_MID10,
})

-- 5. Dedicated Right-Corner Remove Button (66 x 44)
table.insert(flowRowWidgets, ui:Button {
    ID = "PtBtn_Remove",
    Text = "− Remove",
    ToolTip = "Remove Last Transition Point",
    Weight = 0,
    MinimumSize = { 66, 44 },
    MaximumSize = { 66, 44 },
    Font = ui:Font { Family = "Segoe UI", PixelSize = 10, Bold = true },
    StyleSheet = STYLE_REM_ACTIVE,
})

-- 6. Right Rounded Cap (12 x 44)
table.insert(flowRowWidgets, ui:Label {
    ID = "DeckRightCap",
    Text = "",
    Weight = 0,
    MinimumSize = { 12, 44 },
    MaximumSize = { 12, 44 },
    StyleSheet = STYLE_DECK_RIGHT,
})

-- ==============================================================================
-- Build 2x5 Lighter-Colored Card Boxes Wrapping 1:1 Native 144x54 Graphs
-- ==============================================================================
local function makeCurveCard(c)
    local imgPath = assetDir .. c.base .. "_Out.png"
    local cardW = 160

    return ui:VGroup {
        ID = "Card_" .. c.idx,
        Weight = 0,
        Spacing = 0,
        Margin = 0,
        MinimumSize = { cardW, 116 },
        MaximumSize = { cardW, 116 },

        -- 1. Top of Card Box (Exact 1:1 Native 144x54 Anti-Aliased Graph!)
        ui:Label {
            ID = "Img_" .. c.idx,
            Weight = 0,
            Text = '<img src="' .. imgPath .. '">',
            Alignment = { AlignHCenter = true, AlignVCenter = true },
            MinimumSize = { cardW, 64 },
            MaximumSize = { cardW, 64 },
            StyleSheet = STYLE_TOP_IDLE,
        },

        -- 2. Middle of Card Box (Curve Title)
        ui:Button {
            ID = "Lbl_" .. c.idx,
            Weight = 0,
            Text = "Ease Out " .. c.base,
            MinimumSize = { cardW, 22 },
            MaximumSize = { cardW, 22 },
            Font = ui:Font { Family = "Segoe UI", PixelSize = 11, Bold = true },
            StyleSheet = STYLE_MID_IDLE,
        },

        -- 3. Bottom of Card Box: separate inset rounded pill button (card surface baked into image)
        ui:Button {
            ID = "Apply_" .. c.idx,
            Weight = 0,
            Text = "Apply",
            MinimumSize = { cardW, 30 },
            MaximumSize = { cardW, 30 },
            Font = ui:Font { Family = "Segoe UI", PixelSize = 11, Bold = true },
            StyleSheet = STYLE_BOT_IDLE,
        },
    }
end

local row1Cards = {}
local row2Cards = {}
for _, c in ipairs(curveList) do
    if c.row == 1 then
        table.insert(row1Cards, makeCurveCard(c))
    else
        table.insert(row2Cards, makeCurveCard(c))
    end
end

local unpackFn = table.unpack or unpack

-- ==============================================================================
-- Assemble Master Landscape Window Layout
-- ==============================================================================
local win = disp:AddWindow({
    ID = "ShapeMorphFlowBrowser",
    WindowTitle = WIN_TITLE,
    Geometry = { 480, 200, 868, 322 },
    Margin = 14,
    Spacing = 10,
    StyleSheet = "#ShapeMorphFlowBrowser { background-color: #11141d; color: #f4f4f5; font-family: 'Segoe UI', sans-serif; }",

    ui:VGroup {
        Margin = 0,
        Spacing = 10,

        -- ======================================================================
        -- 1. UNIFIED LIGHTER SLATE UPPER CONTROL DECK (840 x 44 Seamless Toolbar)
        -- ======================================================================
        ui:HGroup {
            ID = "UpperDeck",
            Weight = 0,
            Spacing = 0,
            Margin = 0,
            MinimumSize = { 840, 44 },
            MaximumSize = { 840, 44 },
            unpackFn(flowRowWidgets),
        },

        -- ======================================================================
        -- 2. 2 ROWS x 5 COLUMNS LIGHTER-COLORED CURVE CARDS
        -- ======================================================================
        ui:VGroup {
            Weight = 0,
            Spacing = 8,
            Margin = 0,

            ui:HGroup {
                Weight = 0,
                Spacing = 10,
                unpackFn(row1Cards),
            },

            ui:HGroup {
                Weight = 0,
                Spacing = 10,
                unpackFn(row2Cards),
            },
        },
    }
})

local itm = win:GetItems()

-- ==============================================================================
-- Helper: Query Comp, Macro Tool, and Internal RectangleMask Tool
-- ==============================================================================
local function getTools()
    local c = f_app:GetCurrentComp()
    if not c then return nil, nil, nil end
    local tool = c:FindTool("RectMorphMaskPro")
    local tgt = c:FindTool("RectMorphMaskInternal")
    if not tool then
        local list = c:GetToolList(false)
        if list then
            for _, v in pairs(list) do
                if v.Name and string.find(v.Name, "RectMorphMaskPro") then
                    tool = v
                    break
                end
            end
        end
    end
    if not tgt then tgt = tool end
    if not tool then tool = tgt end
    return c, tool, tgt
end

-- Safe numeric reader from tgt/tool
local function readNum(tool, tgt, inpName, t, fallback)
    if tgt then
        local ok, v = pcall(function() return tonumber(tgt:GetInput(inpName, t)) end)
        if ok and v ~= nil then return v end
        local ok2, v2 = pcall(function() return tonumber(tgt[inpName][t]) end)
        if ok2 and v2 ~= nil then return v2 end
    end
    if tool then
        local ok, v = pcall(function() return tonumber(tool:GetInput(inpName, t)) end)
        if ok and v ~= nil then return v end
        local ok2, v2 = pcall(function() return tonumber(tool[inpName][t]) end)
        if ok2 and v2 ~= nil then return v2 end
    end
    return fallback
end

-- Safe numeric writer to both tgt and tool
local function writeNum(tool, tgt, inpName, val, t)
    if tgt then
        pcall(function() tgt:SetInput(inpName, val, t) end)
        pcall(function() tgt[inpName][t] = val end)
    end
    if tool and tool ~= tgt then
        pcall(function() tool:SetInput(inpName, val, t) end)
        pcall(function() tool[inpName][t] = val end)
    end
end

-- Sync TimelineMarks BezierSpline so keyframe tick marks stay accurate on timeline ruler
local function syncTimelineMarks(c, tool, tgt, t, forceActiveIdx)
    if not c or not tool then return end
    local out = tool.TimelineMarks and tool.TimelineMarks:GetConnectedOutput()
    local sp = out and out:GetTool()
    if not sp then
        pcall(function()
            sp = c:BezierSpline()
            tool.TimelineMarks = sp
        end)
    end
    if sp then
        pcall(function() sp:DeleteKeyFrames(-100000, 100000) end)
        for i = 1, 12 do
            local pL = pointLetters[i]
            local en = (i <= 2) or (i == forceActiveIdx) or (readNum(tool, tgt, "Pt" .. pL .. "_Enable", t, 0) >= 0.5)
            if en then
                local f = math.floor(readNum(tool, tgt, "Pt" .. pL .. "_Frame", t, 0) + 0.5)
                pcall(function() tool.TimelineMarks[f] = i end)
                if tgt and tgt ~= tool then
                    pcall(function() tgt.TimelineMarks[f] = i end)
                end
            end
        end
    end
end

-- Activate On-Screen Viewer RectangleControl for Selected Point (1..12)
local lastActivePCIdx = nil
local function activatePointViewerHandle(selIdx)
    local _, tool, tgt = getTools()
    if not tool or not tgt then return end

    if not lastActivePCIdx then
        pcall(function() tgt.Width:SetAttrs({ INPB_PC_Visible = false }) end)
        pcall(function() tgt.Height:SetAttrs({ INPB_PC_Visible = false }) end)
        pcall(function() tgt.CornerRadius:SetAttrs({ INPB_PC_Visible = false }) end)
        for i = 1, 12 do
            local pL = pointLetters[i]
            local showPC = (i == selIdx)
            for _, p in ipairs({ "Width", "Height", "Corner" }) do
                local cn = "Pt" .. pL .. "_" .. p
                pcall(function() tool[cn]:SetAttrs({ INPB_PC_Visible = showPC }) end)
                pcall(function() tgt[cn]:SetAttrs({ INPB_PC_Visible = showPC }) end)
            end
        end
    elseif lastActivePCIdx ~= selIdx then
        local oldL = pointLetters[lastActivePCIdx]
        if oldL then
            for _, p in ipairs({ "Width", "Height", "Corner" }) do
                local cn = "Pt" .. oldL .. "_" .. p
                pcall(function() tool[cn]:SetAttrs({ INPB_PC_Visible = false }) end)
                pcall(function() tgt[cn]:SetAttrs({ INPB_PC_Visible = false }) end)
            end
        end
        local newL = pointLetters[selIdx]
        if newL then
            for _, p in ipairs({ "Width", "Height", "Corner" }) do
                local cn = "Pt" .. newL .. "_" .. p
                pcall(function() tool[cn]:SetAttrs({ INPB_PC_Visible = true }) end)
                pcall(function() tgt[cn]:SetAttrs({ INPB_PC_Visible = true }) end)
            end
        end
    end
    lastActivePCIdx = selIdx
end

-- Refresh Highlight on 10 Seamless Lighter Card Boxes
local function refreshCurveHighlights(activeAnimIdx)
    for _, c in ipairs(curveList) do
        local img = itm["Img_" .. c.idx]
        local lbl = itm["Lbl_" .. c.idx]
        local btn = itm["Apply_" .. c.idx]

        if img and lbl and btn then
            if c.idx == activeAnimIdx then
                img:SetStyleSheet(STYLE_TOP_ACTIVE)
                lbl:SetStyleSheet(STYLE_MID_ACTIVE)
                btn:SetStyleSheet(STYLE_BOT_ACTIVE)
                btn.Text = "✓ Active"
            else
                img:SetStyleSheet(STYLE_TOP_IDLE)
                lbl:SetStyleSheet(STYLE_MID_IDLE)
                btn:SetStyleSheet(STYLE_BOT_IDLE)
                btn.Text = "Apply"
            end
        end
    end
end

-- Refresh Curve Thumbnails (1:1 Native 144x54) and Titles when Inspector Direction changes
local function refreshThumbnailsForDir(dirIdx)
    local suffix = dirSuffixes[dirIdx + 1] or "Out"
    local prefix = dirPrefixes[dirIdx + 1] or "Ease Out "
    for _, c in ipairs(curveList) do
        local imgFile = assetDir .. c.base .. "_" .. suffix .. ".png"
        local lbl = itm["Img_" .. c.idx]
        local title = itm["Lbl_" .. c.idx]
        if lbl then
            lbl.Text = '<img src="' .. imgFile .. '">'
        end
        if title then
            title.Text = prefix .. c.base
        end
    end
end

-- Forward declarations
local selectPoint
local slotModes = {} -- Tracks what each slot 2..12 does ("point", "add", "empty")

-- Refresh Flow Visibility inside Seamless #212636 Upper Deck (fixed geometry, zero holes)
local function refreshFlowVisibility()
    local c, tool, tgt = getTools()
    local t = c and c.CurrentTime or 0
    local highestActive = 2

    for i = 3, 12 do
        local L = pointLetters[i]
        local en = readNum(tool, tgt, "Pt" .. L .. "_Enable", t, 0)
        if en >= 0.5 then
            highestActive = i
        end
    end

    local addSlot = (highestActive < 12) and (highestActive + 1) or nil

    for i = 2, 12 do
        local arr = itm["PtArr_" .. i]
        local btn = itm["PtBtn_" .. i]
        if arr and btn then
            if i <= highestActive then
                slotModes[i] = "point"
                local prevL = pointLetters[i - 1]
                local L = pointLetters[i]
                arr.Text = "➔"
                arr:SetStyleSheet((i == selectedPointIdx) and STYLE_ARR_ACTIVE or STYLE_ARR_IDLE)
                btn.Text = prevL .. "➔" .. L
                btn.ToolTip = "Select Transition " .. prevL .. " ➔ " .. L .. " & Jump Playhead"
                btn:SetStyleSheet((i == selectedPointIdx) and STYLE_NODE_SELECTED or STYLE_NODE_NORMAL)
            elseif i == addSlot then
                slotModes[i] = "add"
                local prevL = pointLetters[highestActive]
                local L = pointLetters[highestActive + 1]
                arr.Text = "➔"
                arr:SetStyleSheet(STYLE_ARR_IDLE)
                btn.Text = "+ Add"
                btn.ToolTip = "Add Transition " .. prevL .. " ➔ " .. L
                btn:SetStyleSheet(STYLE_NODE_ADD)
            else
                slotModes[i] = "empty"
                arr.Text = ""
                arr:SetStyleSheet(STYLE_ARR_EMPTY)
                btn.Text = ""
                btn.ToolTip = ""
                btn:SetStyleSheet(STYLE_NODE_EMPTY)
            end
        end
    end

    -- Dedicated Right-Corner Remove Button
    if itm.PtBtn_Remove then
        if highestActive > 2 then
            local prevL = pointLetters[highestActive - 1]
            local L = pointLetters[highestActive]
            itm.PtBtn_Remove.Text = "− Remove"
            itm.PtBtn_Remove.ToolTip = "Remove Transition " .. prevL .. " ➔ " .. L
            itm.PtBtn_Remove:SetStyleSheet(STYLE_REM_ACTIVE)
        else
            itm.PtBtn_Remove.Text = "− Remove"
            itm.PtBtn_Remove.ToolTip = "Minimum 2 points required (Start · A and A ➔ B)"
            itm.PtBtn_Remove:SetStyleSheet(STYLE_REM_DISABLED)
        end
    end

    return highestActive
end

-- Select a Point, jump playhead to its frame, activate Viewer RectangleControl, and sync UI
selectPoint = function(idx, jumpPlayhead)
    selectedPointIdx = idx
    selectedPointLetter = pointLetters[idx] or "B"
    local L = selectedPointLetter

    itm.PtBtn_1:SetStyleSheet((idx == 1) and STYLE_NODE1_SELECTED or STYLE_NODE1_NORMAL)

    refreshFlowVisibility()

    local c, tool, tgt = getTools()
    local t = c and c.CurrentTime or 0
    local ptFrame = (idx == 1) and 0 or 45
    local animVal = 4 -- default Quart
    local dirVal = 0  -- default Ease Out (0)

    if tool and tgt then
        ptFrame = math.floor(readNum(tool, tgt, "Pt" .. L .. "_Frame", t, ptFrame) + 0.5)

        if jumpPlayhead and c then
            pcall(function() c.CurrentTime = ptFrame end)
            t = ptFrame
        end

        if idx >= 2 then
            animVal = math.floor(readNum(tool, tgt, "Pt" .. L .. "_Anim", t, animVal) + 0.5)
            dirVal = math.floor(readNum(tool, tgt, "Pt" .. L .. "_Dir", t, dirVal) + 0.5)
        end

        for i = 2, 12 do
            local pL = pointLetters[i]
            lastPointDirs[i] = math.floor(readNum(tool, tgt, "Pt" .. pL .. "_Dir", t, 0) + 0.5)
            lastPointAnims[i] = math.floor(readNum(tool, tgt, "Pt" .. pL .. "_Anim", t, 4) + 0.5)
        end

        activatePointViewerHandle(idx)
    end

    lastSyncedFrame = ptFrame
    lastSyncedDirIdx = dirVal

    if idx == 1 then
        lastSyncedAnimIdx = -1
        refreshCurveHighlights(-1)
        return
    end

    lastSyncedAnimIdx = animVal
    refreshThumbnailsForDir(dirVal)
    refreshCurveHighlights(animVal)
end

-- Apply Curve to Selected Point (reads Direction from the Inspector tab!)
local function applyCurve(curveIdx, baseName)
    local c, tool, tgt = getTools()
    if not c or not tool or not tgt then
        return
    end

    if selectedPointIdx < 2 then
        selectPoint(2, true)
    end

    local L = selectedPointLetter
    local prevL = pointLetters[selectedPointIdx - 1] or "A"
    local t = c.CurrentTime or 0
    local dirIdx = math.floor(readNum(tool, tgt, "Pt" .. L .. "_Dir", t, 0) + 0.5)

    local prefix = dirPrefixes[dirIdx + 1] or "Ease Out "
    local fullCurveName = prefix .. baseName

    c:StartUndo("Apply " .. fullCurveName .. " to " .. prevL .. " -> " .. L)

    writeNum(tool, tgt, "Pt" .. L .. "_Anim", curveIdx, t)

    local curEn = readNum(tool, tgt, "Pt" .. L .. "_Enable", t, 0)
    if curEn < 0.5 then
        writeNum(tool, tgt, "Pt" .. L .. "_Enable", 1, t)
    end

    local showInt = (curveIdx == 8 or curveIdx == 9)
    local showFreq = (curveIdx == 9)

    pcall(function() tool["Pt" .. L .. "_Intensity"]:SetAttrs({ INPB_IC_Visible = showInt }) end)
    pcall(function() tool["Pt" .. L .. "_Freq"]:SetAttrs({ INPB_IC_Visible = showFreq }) end)
    pcall(function() tgt["Pt" .. L .. "_Intensity"]:SetAttrs({ INPB_IC_Visible = showInt }) end)
    pcall(function() tgt["Pt" .. L .. "_Freq"]:SetAttrs({ INPB_IC_Visible = showFreq }) end)

    c:EndUndo(true)

    pcall(function()
        c:SetActiveTool(nil)
        c:SetActiveTool(tool)
    end)

    lastSyncedDirIdx = dirIdx
    lastSyncedAnimIdx = curveIdx
    lastPointDirs[selectedPointIdx] = dirIdx
    lastPointAnims[selectedPointIdx] = curveIdx
    refreshThumbnailsForDir(dirIdx)
    refreshCurveHighlights(curveIdx)
end

-- Add Next Point (3..12)
local function addPoint(targetIdx)
    local c, tool, tgt = getTools()
    if not c or not tool or not tgt then return end
    if targetIdx < 3 or targetIdx > 12 then return end

    local t = math.floor((c.CurrentTime or 0) + 0.5)
    local letters = pointLetters

    local L = letters[targetIdx]
    local prevL = letters[targetIdx - 1]

    local maxF = readNum(tool, tgt, "Pt" .. prevL .. "_Frame", t, 0)
    for i = 1, targetIdx - 1 do
        local pL = letters[i]
        if i <= 2 or readNum(tool, tgt, "Pt" .. pL .. "_Enable", t, 0) >= 0.5 then
            local f = readNum(tool, tgt, "Pt" .. pL .. "_Frame", t, 0)
            if f > maxF then maxF = f end
        end
    end

    local prevW = readNum(tool, tgt, "Pt" .. prevL .. "_Width", t, 0.45)
    local prevH = readNum(tool, tgt, "Pt" .. prevL .. "_Height", t, 0.35)
    local prevC = readNum(tool, tgt, "Pt" .. prevL .. "_Corner", t, 0.15)

    local newF = math.floor(((t > maxF) and t or (maxF + 30)) + 0.5)

    c:StartUndo("Add Transition " .. prevL .. " -> " .. L)

    writeNum(tool, tgt, "Pt" .. L .. "_Enable", 1, t)
    writeNum(tool, tgt, "Pt" .. L .. "_Group", 1, t)
    writeNum(tool, tgt, "Pt" .. L .. "_Frame", newF, t)
    writeNum(tool, tgt, "Pt" .. L .. "_Dir", 0, t) -- Default Ease Out
    writeNum(tool, tgt, "Pt" .. L .. "_Width", prevW, t)
    writeNum(tool, tgt, "Pt" .. L .. "_Height", prevH, t)
    writeNum(tool, tgt, "Pt" .. L .. "_Corner", prevC, t)

    local suffixes = { "Group", "Frame", "SetFrameBtn", "Anim", "Dir", "Intensity", "Freq", "Width", "Height", "Corner" }
    local animVal = math.floor(readNum(tool, tgt, "Pt" .. L .. "_Anim", t, 4) + 0.5)
    local showInt = (animVal == 8 or animVal == 9)
    local showFreq = (animVal == 9)

    for _, s in ipairs(suffixes) do
        local vis = true
        if s == "Intensity" then vis = showInt elseif s == "Freq" then vis = showFreq end
        local cname = "Pt" .. L .. "_" .. s
        pcall(function() tool[cname]:SetAttrs({ INPB_IC_Visible = vis }) end)
        pcall(function() tgt[cname]:SetAttrs({ INPB_IC_Visible = vis }) end)
    end

    syncTimelineMarks(c, tool, tgt, t, targetIdx)
    c:EndUndo(true)

    pcall(function() c.CurrentTime = newF end)
    pcall(function() c:SetActiveTool(nil); c:SetActiveTool(tool) end)

    selectPoint(targetIdx, true)
end

-- Remove Highest Active Point (> 2)
local function removeHighestPoint()
    local c, tool, tgt = getTools()
    if not c or not tool or not tgt then return end

    local t = c.CurrentTime or 0
    local letters = pointLetters

    local remIdx = nil
    for i = 12, 3, -1 do
        local L = letters[i]
        local en = readNum(tool, tgt, "Pt" .. L .. "_Enable", t, 0)
        if en >= 0.5 then
            remIdx = i
            break
        end
    end

    if not remIdx or remIdx <= 2 then return end

    local L = letters[remIdx]
    local prevL = letters[remIdx - 1]
    c:StartUndo("Remove Transition " .. prevL .. " -> " .. L)

    writeNum(tool, tgt, "Pt" .. L .. "_Enable", 0, t)
    writeNum(tool, tgt, "Pt" .. L .. "_Group", 0, t)

    local suffixes = { "Group", "Frame", "SetFrameBtn", "Anim", "Dir", "Intensity", "Freq", "Width", "Height", "Corner" }
    for _, s in ipairs(suffixes) do
        local cname = "Pt" .. L .. "_" .. s
        pcall(function() tool[cname]:SetAttrs({ INPB_IC_Visible = false, INPB_PC_Visible = false }) end)
        pcall(function() tgt[cname]:SetAttrs({ INPB_IC_Visible = false, INPB_PC_Visible = false }) end)
    end

    syncTimelineMarks(c, tool, tgt, t, nil)
    c:EndUndo(true)

    pcall(function() c:SetActiveTool(nil); c:SetActiveTool(tool) end)

    if lastActivePCIdx == remIdx then lastActivePCIdx = nil end
    if selectedPointIdx >= remIdx then
        selectPoint(remIdx - 1, true)
    else
        selectPoint(selectedPointIdx, false)
    end
end

-- Connect Click on Curve Cards / Apply Buttons & Titles
for _, c in ipairs(curveList) do
    local bId = "Apply_" .. c.idx
    if win.On[bId] then
        win.On[bId].Clicked = function(ev)
            applyCurve(c.idx, c.base)
        end
    end
    local lId = "Lbl_" .. c.idx
    if win.On[lId] then
        win.On[lId].Clicked = function(ev)
            applyCurve(c.idx, c.base)
        end
    end
end

-- Connect Click on Point Flow Slots 1..12 & Right-Corner Remove Button
win.On.PtBtn_1.Clicked = function(ev)
    selectPoint(1, true)
end

for i = 2, 12 do
    local bId = "PtBtn_" .. i
    if win.On[bId] then
        win.On[bId].Clicked = function(ev)
            local mode = slotModes[i]
            if mode == "point" then
                selectPoint(i, true)
            elseif mode == "add" then
                addPoint(i)
            end
        end
    end
end

if win.On.PtBtn_Remove then
    win.On.PtBtn_Remove.Clicked = function(ev)
        removeHighestPoint()
    end
end

-- Live Inspector Sync Timer: when the user changes Direction or Curve in the Inspector tab,
-- the open Curve & Point Sequencer window updates its graphs and active highlight automatically.
local syncTimer = ui:Timer {
    ID = "InspectorSyncTimer",
    Interval = 200,
    SingleShot = false,
}

function disp.On.Timeout(ev)
    if not ev or ev.who ~= "InspectorSyncTimer" then return end
    if not win.Visible or win.WindowTitle == "Closed" then
        pcall(function() syncTimer:Stop() end)
        disp:ExitLoop()
        return
    end
    local c, tool, tgt = getTools()
    if not c or not tool or not tgt then return end
    local t = c.CurrentTime or 0
    for i = 2, 12 do
        local pL = pointLetters[i]
        local en = (i == 2) or (readNum(tool, tgt, "Pt" .. pL .. "_Enable", t, 0) >= 0.5)
        if en then
            local curDir = math.floor(readNum(tool, tgt, "Pt" .. pL .. "_Dir", t, lastPointDirs[i] or 0) + 0.5)
            local curAnim = math.floor(readNum(tool, tgt, "Pt" .. pL .. "_Anim", t, lastPointAnims[i] or 4) + 0.5)
            if curDir ~= lastPointDirs[i] or curAnim ~= lastPointAnims[i] then
                lastPointDirs[i] = curDir
                lastPointAnims[i] = curAnim
                if i ~= selectedPointIdx then
                    selectPoint(i, false)
                else
                    if curDir ~= lastSyncedDirIdx then
                        lastSyncedDirIdx = curDir
                        refreshThumbnailsForDir(curDir)
                    end
                    if curAnim ~= lastSyncedAnimIdx then
                        lastSyncedAnimIdx = curAnim
                        refreshCurveHighlights(curAnim)
                    end
                end
                break
            end
        end
    end
end

-- Window Close Handler
function win.On.ShapeMorphFlowBrowser.Close(ev)
    pcall(function() syncTimer:Stop() end)
    pcall(function() win.WindowTitle = "Closed" end)
    pcall(function() win:Hide() end)
    pcall(function() win.ID = "Closed_ShapeMorph_" .. tostring(os.clock()) end)
    disp:ExitLoop()
end

-- Apply Custom Dark Slate-Indigo Windows Title Bar Color via Win32 DWM API
local function styleWindowTitleBar()
    pcall(function()
        local ffi = require("ffi")
        pcall(function()
            ffi.cdef[[
                typedef void* HWND;
                typedef unsigned long DWORD;
                typedef const void* LPCVOID;
                typedef long HRESULT;
                HWND FindWindowA(const char* lpClassName, const char* lpWindowName);
                HRESULT DwmSetWindowAttribute(HWND hwnd, DWORD dwAttribute, LPCVOID pvAttribute, DWORD cbAttribute);
            ]]
        end)
        local user32 = ffi.load("user32")
        local dwmapi = ffi.load("dwmapi")
        local hwnd = user32.FindWindowA(nil, WIN_TITLE)
        if hwnd ~= nil then
            local dark = ffi.new("int[1]", 1)
            dwmapi.DwmSetWindowAttribute(hwnd, 20, dark, 4)
            dwmapi.DwmSetWindowAttribute(hwnd, 19, dark, 4)
            local capColor = ffi.new("DWORD[1]", 0x0034221B)
            dwmapi.DwmSetWindowAttribute(hwnd, 35, capColor, 4)
            local txtColor = ffi.new("DWORD[1]", 0x00F0E8E2)
            dwmapi.DwmSetWindowAttribute(hwnd, 36, txtColor, 4)
            local bdrColor = ffi.new("DWORD[1]", 0x004F362D)
            dwmapi.DwmSetWindowAttribute(hwnd, 34, bdrColor, 4)
        end
    end)
end

-- If opened with requested point, select that point and jump playhead to its frame
local reqPt = curComp and curComp:GetData("ShapeMorph_TargetPoint")
local initialPoint = 2
if reqPt then
    for i, L in ipairs(pointLetters) do
        if L == reqPt then
            initialPoint = i
            break
        end
    end
end

selectPoint(initialPoint, true)

win:Show()
styleWindowTitleBar()
pcall(function() syncTimer:Start() end)
disp:RunLoop()
pcall(function() syncTimer:Stop() end)
win:Hide()
