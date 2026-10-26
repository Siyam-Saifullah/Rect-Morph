import os
import math
from PIL import Image, ImageDraw

OUT_DIR = r"d:\02 Code\01 Drafting Projects\Shape Morph Pro\assets\curves"
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 136, 58
SCALE = 4
SW, SH = W * SCALE, H * SCALE

def f_out(u, m, amp=1.45, freq=2.5):
    if u <= 0.0:
        return 0.0
    if u >= 1.0:
        return 1.0
    if m == 0:
        return u
    elif m == 1:
        return math.sin((u * math.pi) / 2.0)
    elif m == 2:
        return 1.0 - (1.0 - u) ** 2
    elif m == 3:
        return 1.0 - (1.0 - u) ** 3
    elif m == 4:
        return 1.0 - (1.0 - u) ** 4
    elif m == 5:
        return 1.0 - (1.0 - u) ** 5
    elif m == 6:
        return 1.0 - (2.0 ** (-10.0 * u))
    elif m == 7:
        return math.sqrt(max(0.0, 1.0 - (u - 1.0) ** 2))
    elif m == 8:
        c1 = 1.70158 * amp
        c3 = c1 + 1.0
        return 1.0 + c3 * ((u - 1.0) ** 3) + c1 * ((u - 1.0) ** 2)
    elif m == 9:
        p = 0.3 / max(0.5, freq * 0.4)
        return (2.0 ** (-10.0 * u)) * math.sin((u - p / 4.0) * (2.0 * math.pi) / p) * amp + 1.0
    elif m == 10:
        n1 = 7.5625
        d1 = 2.75
        x = u
        if x < 1.0 / d1:
            return n1 * x * x
        elif x < 2.0 / d1:
            x -= 1.5 / d1
            return n1 * x * x + 0.75
        elif x < 2.5 / d1:
            x -= 2.25 / d1
            return n1 * x * x + 0.9375
        else:
            x -= 2.625 / d1
            return n1 * x * x + 0.984375
    return u

def ease(t, m, d):
    if m == 0:
        return t
    if d == 0: # Out
        return f_out(t, m)
    elif d == 1: # In
        return 1.0 - f_out(1.0 - t, m)
    else: # InOut
        if t < 0.5:
            return 0.5 * (1.0 - f_out(1.0 - 2.0 * t, m))
        else:
            return 0.5 + 0.5 * f_out(2.0 * t - 1.0, m)

curves = [
    (0, "Linear"),
    (1, "Sine"),
    (2, "Quad"),
    (3, "Cubic"),
    (4, "Quart"),
    (5, "Quint"),
    (6, "Expo"),
    (7, "Circ"),
    (8, "Back"),
    (9, "Elastic"),
    (10, "Bounce"),
]

dirs = [
    (0, "Out"),
    (1, "In"),
    (2, "InOut"),
]

BG_COLOR = (20, 20, 22, 255)      # Deep matte charcoal (#141416)
LINE_COLOR = (154, 255, 28, 255)  # Vibrant lime-green (#9aff1c)

for m, name in curves:
    for d, d_suffix in dirs:
        img = Image.new("RGBA", (SW, SH), BG_COLOR)
        draw = ImageDraw.Draw(img)

        pad_x = 18 * SCALE
        pad_top = 10 * SCALE
        pad_bot = 10 * SCALE

        plot_w = SW - 2 * pad_x
        plot_h = SH - pad_top - pad_bot

        steps = 200
        raw_vals = [ease(i / steps, m, d) for i in range(steps + 1)]
        min_v = min(0.0, min(raw_vals))
        max_v = max(1.0, max(raw_vals))
        span_v = max(0.001, max_v - min_v)

        pts = []
        for i, v in enumerate(raw_vals):
            t = i / steps
            norm_v = (v - min_v) / span_v
            px = pad_x + t * plot_w
            py = (SH - pad_bot) - norm_v * plot_h
            pts.append((px, py))

        stroke_w = int(2.4 * SCALE)
        draw.line(pts, fill=LINE_COLOR, width=stroke_w, joint="curve")
        r = stroke_w / 2.0
        for end_pt in (pts[0], pts[-1]):
            ex, ey = end_pt
            draw.ellipse((ex - r, ey - r, ex + r, ey + r), fill=LINE_COLOR)

        out_img = img.resize((W, H), Image.Resampling.LANCZOS)
        dir_filename = os.path.join(OUT_DIR, f"{name}_{d_suffix}.png")
        out_img.save(dir_filename)
        if d == 0:
            default_filename = os.path.join(OUT_DIR, f"{name}.png")
            out_img.save(default_filename)

print("Regenerated all 136x58 curve thumbnails with normalized overshoot bounds!")
