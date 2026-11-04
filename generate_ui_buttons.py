"""
Generates anti-aliased UI images for the Curve & Point Sequencer window:
  1. Curve card bottom slices (160 x 30): card surface + 8px bottom corners + inset 5px rounded pill
  2. Upper Deck slices (height 44px, total width 840px, supporting up to 12 points A..L):
     Width sum: 78 + 58 + 11*(10 + 46) + 10 + 66 + 12 = 840px
     - deck_left78.png (78 x 44): left cap with 8px rounded top-left & bottom-left corners
     - deck_btn58_{normal,hover,pressed,selected,selected_hover}.png (58 x 44): Start·A pill
     - deck_mid10.png (10 x 44): arrow slot / spacer with top & bottom deck borders
     - deck_btn46_{normal,hover,pressed,selected,selected_hover,add,add_hover}.png (46 x 44): transition / +Add pill
     - deck_empty46.png (46 x 44): empty slot with top & bottom deck borders
     - deck_rem66_{normal,hover,pressed,disabled}.png (66 x 44): right-corner Remove pill
     - deck_right12.png (12 x 44): right cap with 8px rounded top-right & bottom-right corners

All images are rendered at 8x supersampling and downsampled with LANCZOS.
"""
import os
from PIL import Image, ImageDraw

SS = 8
W, H = 160, 30
CARD_R = 8
PILL = (8, 1, 152, 24)  # x0, y0, x1, y1 (exclusive) -> 144 x 23
PILL_R = 5

DECK_H = 44
DECK_R = 8
DECK_BG = "#212636"
DECK_BORDER = "#363f58"
DECK_PILL_Y = (8, 36)  # 28px tall pill centered vertically inside 44px bar (8px top, 8px bottom)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "ui")

THEMES = {
    "idle": {
        "card": "#212636", "card_border": "#363f58",
        "top": "#3c4864", "bot": "#272f42",
        "border": "#4d5c7f", "rim": "#6376a2", "shadow": "#141822",
    },
    "idle_hover": {
        "card": "#212636", "card_border": "#363f58",
        "top": "#46587a", "bot": "#2c364c",
        "border": "#6a9a34", "rim": "#86b84c", "shadow": "#141822",
    },
    "idle_pressed": {
        "card": "#212636", "card_border": "#363f58",
        "top": "#1b2130", "bot": "#232b3d",
        "border": "#3a4562", "rim": "#1b2130", "shadow": "#4d5c7f",
    },
    "active": {
        "card": "#1f2a1d", "card_border": "#5c7f33",
        "top": "#2f4226", "bot": "#25351f",
        "border": "#6a9a34", "rim": "#86b84c", "shadow": "#121a0e",
    },
    "active_hover": {
        "card": "#1f2a1d", "card_border": "#5c7f33",
        "top": "#36502b", "bot": "#2a3d22",
        "border": "#7aac3e", "rim": "#9acb5c", "shadow": "#121a0e",
    },
}

DECK_PILL_THEMES = {
    "normal": {
        "top": "#3c4864", "bot": "#272f42",
        "border": "#4d5c7f", "rim": "#6376a2", "shadow": "#141822",
    },
    "hover": {
        "top": "#46587a", "bot": "#2c364c",
        "border": "#6a9a34", "rim": "#86b84c", "shadow": "#141822",
    },
    "pressed": {
        "top": "#1b2130", "bot": "#232b3d",
        "border": "#3a4562", "rim": "#1b2130", "shadow": "#4d5c7f",
    },
    "selected": {
        "top": "#2f4226", "bot": "#25351f",
        "border": "#6a9a34", "rim": "#86b84c", "shadow": "#121a0e",
    },
    "selected_hover": {
        "top": "#36502b", "bot": "#2a3d22",
        "border": "#7aac3e", "rim": "#9acb5c", "shadow": "#121a0e",
    },
    "add": {
        "top": "#333e57", "bot": "#232b3d",
        "border": "#465474", "rim": "#5a6c94", "shadow": "#141822",
    },
    "add_hover": {
        "top": "#36502b", "bot": "#263820",
        "border": "#6a9a34", "rim": "#86b84c", "shadow": "#141822",
    },
    "rem_normal": {
        "top": "#333e57", "bot": "#232b3d",
        "border": "#465474", "rim": "#5a6c94", "shadow": "#141822",
    },
    "rem_hover": {
        "top": "#3f2e3a", "bot": "#2c202a",
        "border": "#8a4b56", "rim": "#a65d6a", "shadow": "#141822",
    },
    "rem_disabled": {
        "top": "#283044", "bot": "#202636",
        "border": "#343e56", "rim": "#3d4965", "shadow": "#181d29",
    },
}


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rr_mask(size, box, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, radius=r, fill=255)
    return m


def vgrad(size, top, bot):
    w, h = size
    g = Image.new("RGBA", size)
    t, b = hex_rgb(top), hex_rgb(bot)
    px = ImageDraw.Draw(g)
    for y in range(h):
        k = y / max(1, h - 1)
        c = tuple(round(t[i] + (b[i] - t[i]) * k) for i in range(3)) + (255,)
        px.line([(0, y), (w, y)], fill=c)
    return g


def solid(size, color):
    return Image.new("RGBA", size, hex_rgb(color) + (255,))


def draw_pill(img, S, pill_box, r_px, theme):
    px = SS
    x0, y0, x1, y1 = (v * SS for v in pill_box)
    r = r_px * SS
    # bottom shadow (1px below the pill)
    img.paste(solid(S, theme["shadow"]), (0, 0), rr_mask(S, (x0, y0 + px, x1 - 1, y1 - 1 + px), r))
    # border
    img.paste(solid(S, theme["border"]), (0, 0), rr_mask(S, (x0, y0, x1 - 1, y1 - 1), r))
    # top rim highlight
    img.paste(solid(S, theme["rim"]), (0, 0), rr_mask(S, (x0, y0, x1 - 1, y1 - 1 - px), r))
    img.paste(solid(S, theme["border"]), (0, 0), rr_mask(S, (x0, y0 + px, x1 - 1, y1 - 1), r))
    # gradient face
    face_box = (x0 + px, y0 + px, x1 - 1 - px, y1 - 1 - px)
    img.paste(vgrad(S, theme["top"], theme["bot"]), (0, 0), rr_mask(S, face_box, r - px))


def render_card_bottom(theme):
    S = (W * SS, H * SS)
    img = Image.new("RGBA", S, (0, 0, 0, 0))
    px = SS

    outer = (0, -CARD_R * 4 * SS, W * SS - 1, H * SS - 1)
    inner = (px, -CARD_R * 4 * SS, W * SS - 1 - px, H * SS - 1 - px)
    img.paste(solid(S, theme["card_border"]), (0, 0), rr_mask(S, outer, CARD_R * SS))
    img.paste(solid(S, theme["card"]), (0, 0), rr_mask(S, inner, (CARD_R - 1) * SS))

    draw_pill(img, S, PILL, PILL_R, theme)
    return img.resize((W, H), Image.LANCZOS)


def render_deck_cap(w, side):
    """side='left' or 'right': renders rounded end cap of the 840x44 Upper Deck."""
    S = (w * SS, DECK_H * SS)
    img = Image.new("RGBA", S, (0, 0, 0, 0))
    px = SS
    if side == "left":
        outer = (0, 0, (w + DECK_R * 4) * SS - 1, DECK_H * SS - 1)
        inner = (px, px, (w + DECK_R * 4) * SS - 1, DECK_H * SS - 1 - px)
    else:
        outer = (-DECK_R * 4 * SS, 0, w * SS - 1, DECK_H * SS - 1)
        inner = (-DECK_R * 4 * SS, px, w * SS - 1 - px, DECK_H * SS - 1 - px)
    img.paste(solid(S, DECK_BORDER), (0, 0), rr_mask(S, outer, DECK_R * SS))
    img.paste(solid(S, DECK_BG), (0, 0), rr_mask(S, inner, (DECK_R - 1) * SS))
    return img.resize((w, DECK_H), Image.LANCZOS)


def render_deck_mid(w, pill_theme=None):
    """Middle slice of the 840x44 Upper Deck (top & bottom 1px border, optional centered pill)."""
    S = (w * SS, DECK_H * SS)
    img = solid(S, DECK_BG)
    px = SS
    d = ImageDraw.Draw(img)
    bcol = hex_rgb(DECK_BORDER) + (255,)
    d.rectangle([0, 0, w * SS - 1, px - 1], fill=bcol)
    d.rectangle([0, (DECK_H - 1) * SS, w * SS - 1, DECK_H * SS - 1], fill=bcol)
    if pill_theme is not None:
        y0, y1 = DECK_PILL_Y
        draw_pill(img, S, (0, y0, w, y1), PILL_R, pill_theme)
    return img.resize((w, DECK_H), Image.LANCZOS)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    # 1. Card bottom buttons (160 x 30)
    for name, theme in THEMES.items():
        path = os.path.join(OUT_DIR, f"card_btn_{name}.png")
        render_card_bottom(theme).save(path)

    # 2. Upper Deck end caps & middle spacers (height 44)
    render_deck_cap(78, "left").save(os.path.join(OUT_DIR, "deck_left78.png"))
    render_deck_cap(12, "right").save(os.path.join(OUT_DIR, "deck_right12.png"))
    render_deck_mid(10).save(os.path.join(OUT_DIR, "deck_mid10.png"))
    render_deck_mid(46).save(os.path.join(OUT_DIR, "deck_empty46.png"))

    # 3. Slot 1 (Start · A, 58 x 44)
    for state in ("normal", "hover", "pressed", "selected", "selected_hover"):
        render_deck_mid(58, DECK_PILL_THEMES[state]).save(
            os.path.join(OUT_DIR, f"deck_btn58_{state}.png")
        )

    # 4. Slots 2..12 (Transitions & +Add, 46 x 44)
    for state in ("normal", "hover", "pressed", "selected", "selected_hover", "add", "add_hover"):
        render_deck_mid(46, DECK_PILL_THEMES[state]).save(
            os.path.join(OUT_DIR, f"deck_btn46_{state}.png")
        )

    # 5. Right Corner Remove button (66 x 44)
    for state, tkey in (("normal", "rem_normal"), ("hover", "rem_hover"), ("pressed", "pressed"), ("disabled", "rem_disabled")):
        render_deck_mid(66, DECK_PILL_THEMES[tkey]).save(
            os.path.join(OUT_DIR, f"deck_rem66_{state}.png")
        )

    print("Generated all card & 12-point upper deck UI assets in", OUT_DIR)


if __name__ == "__main__":
    main()
