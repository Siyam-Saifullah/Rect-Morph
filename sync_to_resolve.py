import sys
import os

def sync_node():
    # Attempt to load DaVinci Resolve Scripting API if run standalone or via tool
    resolve = None
    try:
        import DaVinciResolveScript as bmd
        resolve = bmd.scriptapp("Resolve")
    except Exception:
        pass

    if not resolve:
        # Check if resolve is available in builtins/globals (when run via MCP tool)
        resolve = globals().get('resolve')

    if not resolve:
        print("Error: Could not connect to DaVinci Resolve.")
        return False

    fusion = resolve.Fusion()
    if not fusion:
        print("Error: Could not get Fusion instance.")
        return False

    comp = fusion.GetCurrentComp()
    if not comp:
        print("Error: No active Fusion composition found.")
        return False

    script_dir = os.path.dirname(os.path.abspath(__file__))
    setting_file = os.path.join(script_dir, 'RectMorph_Mask_Pro.setting').replace('\\', '/')
    if not os.path.exists(setting_file):
        print(f"Error: {setting_file} does not exist.")
        return False

    lua_code = f"""
    local flow = comp.CurrentFrame.FlowView
    local old = comp:FindTool("RectMorphMaskPro")
    local x, y = 0, 0
    local targets = {{}}

    if old then
        if flow then
            x, y = flow:GetPos(old)
        end
        local out = old.Mask
        if out then
            for _, inp in pairs(out:GetConnectedInputs()) do
                table.insert(targets, inp)
            end
        end
        old:Delete()
    end
    local oldKf = comp:FindTool("RectMorphKeyframes")
    if oldKf then oldKf:Delete() end

    local path = [[{setting_file}]]
    local tbl = bmd.readfile(path)
    if tbl then
        comp:Paste(tbl)
        local newTool = comp:FindTool("RectMorphMaskPro")
        if newTool then
            if flow and x and y then
                flow:SetPos(newTool, x, y)
            end
            for _, inp in ipairs(targets) do
                inp:ConnectTo(newTool.Mask)
            end
            local tgt = comp:FindTool("RectMorphMaskInternal")
            if tgt then
                pcall(function() tgt.Width:SetAttrs({{ INPB_PC_Visible = false }}) end)
                pcall(function() tgt.Height:SetAttrs({{ INPB_PC_Visible = false }}) end)
                pcall(function() tgt.CornerRadius:SetAttrs({{ INPB_PC_Visible = false }}) end)
            end
            comp:SetActiveTool(newTool)
            print("Successfully replaced RectMorphMaskPro live in comp!")
            return true
        end
    end
    return false
    """

    comp.Execute(lua_code)
    print("Live replacement script executed in active comp!")
    return True

if __name__ == '__main__':
    sync_node()
