import zipfile
import re
import os

def package_drfx():
    setting_path = 'RectMorph_Mask_Pro.setting'
    if not os.path.exists(setting_path):
        print(f"Error: {setting_path} not found.")
        return

    with open(setting_path, 'r', encoding='utf-8') as f:
        fusion_setting = f.read()

    # Extract instance inputs from fusion macro
    m_inputs = re.search(r'Inputs = ordered\(\) \{(.*?)\n\t\t\t\},\n\t\t\tOutputs = \{', fusion_setting, re.DOTALL)
    macro_inputs = m_inputs.group(1) if m_inputs else ""

    # For Edit Effect, expose MainInput1 at the top
    edit_inputs = """\t\t\t\tMainInput1 = InstanceInput {
\t\t\t\t\tSourceOp = "RectMorphMatte",
\t\t\t\t\tSource = "Background",
\t\t\t\t},
""" + macro_inputs

    # Extract inner RectangleMask body
    m_mask = re.search(r'RectMorphMaskInternal = RectangleMask \{(.*?)\n\t\t\t\}\n\t\t\}\n\t\},', fusion_setting, re.DOTALL)
    mask_body = m_mask.group(1) if m_mask else ""

    edit_setting = f"""{{
\tTools = ordered() {{
\t\tRectMorphProEffect = MacroOperator {{
\t\t\tCtrlWZoom = false,
\t\t\tNameSet = true,
\t\t\tInputs = ordered() {{
{edit_inputs}
\t\t\t}},
\t\t\tOutputs = {{
\t\t\t\tMainOutput1 = InstanceOutput {{
\t\t\t\t\tSourceOp = "RectMorphMatte",
\t\t\t\t\tSource = "Output",
\t\t\t\t}}
\t\t\t}},
\t\t\tViewInfo = GroupInfo {{ Pos = {{ 0, 0 }} }},
\t\t\tTools = ordered() {{
\t\t\t\tRectMorphMaskInternal = RectangleMask {{{mask_body},
\t\t\t\tRectMorphMatte = MatteControl {{
\t\t\t\t\tCtrlWShown = false,
\t\t\t\t\tNameSet = true,
\t\t\t\t\tInputs = {{
\t\t\t\t\t\tFilter = Input {{ Value = FuID {{ "Fast Gaussian" }}, }},
\t\t\t\t\t\tMatteCombine = Input {{ Value = 4, }},
\t\t\t\t\t\tGarbageMatte = Input {{
\t\t\t\t\t\t\tSourceOp = "RectMorphMaskInternal",
\t\t\t\t\t\t\tSource = "Mask",
\t\t\t\t\t\t}},
\t\t\t\t\t}},
\t\t\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 0, 65 }} }},
\t\t\t\t}}
\t\t\t}}
\t\t}},
\t\tRectMorphKeyframes = BezierSpline {{
\t\t\tSplineColor = {{ Red = 74, Green = 222, Blue = 128 }},
\t\t\tCtrlWZoom = false,
\t\t\tNameSet = true,
\t\t\tKeyFrames = {{
\t\t\t\t[0] = {{ 1, RH = {{ 15, 1 }}, Flags = {{ Linear = true }} }},
\t\t\t\t[45] = {{ 2, LH = {{ 30, 2 }}, Flags = {{ Linear = true }} }}
\t\t\t}}
\t\t}}
\t}},
\tActiveTool = "RectMorphProEffect"
}}
"""

    print("Edit setting brace counts:", edit_setting.count('{'), edit_setting.count('}'))
    assert edit_setting.count('{') == edit_setting.count('}')

    # Read CurveBrowser.lua script
    curve_script_path = os.path.join('scripts', 'CurveBrowser.lua')
    with open(curve_script_path, 'r', encoding='utf-8') as f:
        curve_script = f.read()

    # Collect asset files
    assets_to_package = []
    assets_dir = 'assets'
    for root, _, files in os.walk(assets_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, assets_dir).replace('\\', '/')
            assets_to_package.append((full_path, rel_path))

    # Output bundle filenames
    bundle_names = ['Rect_Morph_Pro.drfx', 'RectMorph_Mask_Pro.drfx']

    for drfx_path in bundle_names:
        with zipfile.ZipFile(drfx_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            # 1. Fusion Tools
            z.writestr('Fusion/Tools/Rect Morph Pro/Rect Morph Pro.setting', fusion_setting)
            z.writestr('Templates/Fusion/Tools/Rect Morph Pro/Rect Morph Pro.setting', fusion_setting)
            z.writestr('Fusion/Tools/Rect Morph Pro/RectMorph Mask Pro.setting', fusion_setting)
            z.writestr('Templates/Fusion/Tools/Rect Morph Pro/RectMorph Mask Pro.setting', fusion_setting)

            # 2. Edit Page Effects
            z.writestr('Edit/Effects/Rect Morph Pro/Rect Morph Pro.setting', edit_setting)
            z.writestr('Templates/Edit/Effects/Rect Morph Pro/Rect Morph Pro.setting', edit_setting)
            z.writestr('Edit/Effects/Rect Morph Pro/RectMorph Mask Pro.setting', edit_setting)
            z.writestr('Templates/Edit/Effects/Rect Morph Pro/RectMorph Mask Pro.setting', edit_setting)

            # 3. Scripts
            z.writestr('Scripts/Comp/Rect Morph Pro/Curve Browser.lua', curve_script)
            z.writestr('Scripts/Comp/RectMorph Pro/Curve Browser.lua', curve_script)

            # 4. Assets (curves and ui slices)
            for full_p, rel_p in assets_to_package:
                with open(full_p, 'rb') as af:
                    content = af.read()
                    z.writestr(f'Scripts/Comp/Rect Morph Pro/assets/{rel_p}', content)
                    z.writestr(f'Scripts/Comp/RectMorph Pro/assets/{rel_p}', content)

        size_kb = os.path.getsize(drfx_path) / 1024
        print(f"Packaged {drfx_path} successfully! ({size_kb:.1f} KB)")

if __name__ == '__main__':
    package_drfx()
