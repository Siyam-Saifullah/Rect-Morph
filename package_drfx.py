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
\t\t}}
\t}},
\tActiveTool = "RectMorphProEffect"
}}
"""

    print("Edit setting brace counts:", edit_setting.count('{'), edit_setting.count('}'))
    assert edit_setting.count('{') == edit_setting.count('}')

    drfx_path = 'RectMorph_Mask_Pro.drfx'
    with zipfile.ZipFile(drfx_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('Fusion/Tools/RectMorph Mask Pro.setting', fusion_setting)
        z.writestr('Templates/Fusion/Tools/RectMorph Mask Pro.setting', fusion_setting)
        z.writestr('Edit/Effects/RectMorph Pro/RectMorph Mask Pro.setting', edit_setting)
        z.writestr('Templates/Edit/Effects/RectMorph Pro/RectMorph Mask Pro.setting', edit_setting)

    print(f"Packaged {drfx_path} successfully!")

if __name__ == '__main__':
    package_drfx()
