#!/usr/bin/env python3
"""news-image-20261122 v1 — front-page generator.

Draws a 1024x1024 newspaper front page for SUNDAY 22 NOVEMBER 2026 from the
verified ledger (35 stories, 6 stat boxes, 13+1 map pins, 8-item DATE CHECK).
Build-time tool only: it needs Pillow + the Liberation/DejaVu fonts installed
on this machine. The graded entrypoint is main.py (stdlib only), which copies
the entry.png this script produces. Deterministic: fixed fonts, fixed layout,
no timestamps, no randomness.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (250, 247, 240)   # #FAF7F0
INK = (17, 17, 17)        # #111111
RED = (185, 28, 28)       # #B91C1C
GREY = (107, 114, 128)    # #6B7280
BORDER = (216, 210, 196)
WHITE = (255, 255, 255)
LAND = (217, 211, 197)
LAND_EDGE = (154, 147, 138)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns list of lines (never splits a word)."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, f, max_w, max_lines, label):
    """Wrap text; print a warning (and truncate) if it exceeds max_lines."""
    lines = wrap(draw, text, f, max_w)
    if len(lines) > max_lines:
        print(f"OVERFLOW {label}: {len(lines)} lines > {max_lines}: {text!r}",
              file=sys.stderr)
        lines = lines[:max_lines]
        # trim last line with an ellipsis if it was cut mid-thought
        while lines and text_w(draw, lines[-1] + " ...", f) > max_w:
            lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else ""
        if lines:
            lines[-1] = lines[-1] + " ..."
    return lines


def draw_lines(draw, x, y, lines, f, fill=INK, leading=None):
    if leading is None:
        leading = f.size + 2
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def draw_rich(draw, x, y, segments, gap=0):
    """Draw [(text, font, fill), ...] left to right; returns end x."""
    cx = x
    for text, f, fill in segments:
        draw.text((cx, y), text, font=f, fill=fill)
        cx += text_w(draw, text, f) + gap
    return cx


def rich_width(draw, segments):
    return sum(text_w(draw, t, f) for t, f, _ in segments)


def center_rich(draw, cx, y, segments):
    draw_rich(draw, cx - rich_width(draw, segments) / 2, y, segments)


def hline(draw, x0, x1, y, fill=INK, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def box(draw, x0, y0, x1, y1, outline=BORDER, width=1, fill=None):
    draw.rectangle([x0, y0, x1, y1], outline=outline, width=width, fill=fill)


# ---------------------------------------------------------------- world map
# Coarse hand-drawn continent outlines in (lon, lat). Simplified on purpose:
# a stylised locator map, not a survey chart.
NORTH_AMERICA = [(-168, 66), (-160, 58), (-150, 60), (-140, 60), (-135, 58),
    (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24),
    (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9),
    (-80, 8), (-79, 9), (-82, 13), (-85, 16), (-87, 21), (-90, 21),
    (-91, 19), (-96, 19), (-97, 26), (-93, 30), (-89, 30), (-84, 30),
    (-81, 26), (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 45),
    (-65, 44), (-60, 47), (-55, 52), (-60, 55), (-65, 60), (-68, 58),
    (-75, 62), (-80, 66), (-85, 66), (-90, 69), (-95, 69), (-100, 68),
    (-110, 68), (-120, 69), (-130, 70), (-140, 70), (-150, 71), (-160, 71)]
GREENLAND = [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68),
    (-25, 70), (-20, 74), (-25, 78), (-35, 80), (-55, 80), (-60, 76),
    (-58, 70)]
SOUTH_AMERICA = [(-80, 8), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
    (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50),
    (-70, -54), (-66, -55), (-65, -50), (-62, -45), (-58, -38), (-52, -33),
    (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3),
    (-44, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11),
    (-72, 12), (-76, 10)]
AFRICA = [(-17, 15), (-16, 20), (-15, 27), (-10, 31), (-5, 35), (0, 36),
    (10, 37), (11, 34), (15, 32), (20, 32), (25, 32), (30, 31), (32, 31),
    (34, 28), (35, 24), (37, 20), (39, 18), (41, 15), (43, 12), (46, 11),
    (51, 12), (51, 10), (48, 5), (45, 2), (41, -2), (40, -6), (40, -10),
    (39, -15), (36, -20), (33, -26), (32, -29), (28, -33), (20, -35),
    (17, -32), (15, -27), (13, -20), (12, -15), (13, -10), (12, -6),
    (9, -1), (9, 4), (-5, 5), (-8, 5), (-13, 8), (-17, 12)]
EURASIA = [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-1, 50),
    (2, 51), (5, 53), (8, 55), (8, 57), (10, 59), (5, 60), (5, 62),
    (10, 64), (12, 66), (18, 69), (25, 71), (30, 70), (35, 68), (40, 68),
    (45, 68), (50, 69), (55, 68), (60, 69), (65, 69), (70, 72), (75, 73),
    (80, 73), (85, 74), (90, 75), (95, 76), (100, 77), (105, 77),
    (110, 74), (115, 73), (120, 73), (125, 72), (130, 72), (135, 71),
    (140, 72), (145, 72), (150, 70), (155, 69), (160, 69), (165, 66),
    (170, 66), (178, 65), (178, 62), (170, 62), (162, 60), (156, 52),
    (142, 50), (140, 45), (135, 43), (130, 42), (127, 40), (126, 38),
    (122, 38), (120, 35), (122, 31), (120, 28), (118, 25), (115, 23),
    (110, 20), (108, 18), (106, 10), (104, 9), (101, 7), (100, 8),
    (98, 10), (97, 15), (94, 17), (92, 21), (90, 22), (88, 22), (86, 20),
    (84, 19), (82, 17), (80, 13), (78, 9), (76, 8), (75, 12), (73, 16),
    (70, 20), (67, 24), (64, 25), (61, 25), (58, 26), (56, 27), (54, 27),
    (52, 28), (50, 29), (48, 30), (47, 30), (48, 28), (50, 26), (52, 25),
    (54, 24), (56, 26), (57, 25), (59, 22), (58, 20), (55, 17), (52, 15),
    (48, 14), (45, 13), (43, 12), (41, 14), (39, 18), (37, 22), (35, 24),
    (34, 28), (34, 30), (36, 36), (33, 36), (30, 36), (27, 37), (26, 38),
    (23, 36), (22, 37), (20, 39), (19, 40), (15, 40), (12, 42), (10, 44),
    (8, 44), (3, 43), (0, 40), (-1, 38), (-2, 37), (-5, 36)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 35), (140, 38),
    (141, 41), (142, 44), (144, 43), (142, 39), (140, 36), (138, 34),
    (136, 33), (133, 32)]
BORNEO = [(109, 1), (113, 4), (117, 6), (118, 1), (116, -3), (112, -3),
    (110, -1)]
SUMATRA = [(95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (103, -5),
    (100, -1), (97, 3)]
JAVA = [(105, -6), (108, -7), (112, -7), (114, -8), (110, -8), (106, -7)]
NEW_GUINEA = [(131, -1), (136, -2), (141, -3), (146, -6), (147, -8),
    (143, -8), (138, -7), (134, -4)]
AUSTRALIA = [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33),
    (129, -32), (132, -32), (135, -35), (137, -35), (140, -38), (145, -38),
    (147, -39), (150, -37), (153, -32), (153, -27), (150, -22), (146, -19),
    (142, -15), (142, -11), (140, -17), (136, -15), (135, -12), (132, -11),
    (130, -13), (126, -14), (122, -17), (118, -20)]
NEW_ZEALAND = [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
    (176, -40), (174, -41), (172, -43), (169, -46)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (49, -20), (47, -25),
    (44, -25), (43, -21)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
              UK, JAPAN, BORNEO, SUMATRA, JAVA, NEW_GUINEA, AUSTRALIA,
              NEW_ZEALAND, MADAGASCAR]

# (label, story number, lon, lat, map-label?, display offset px (dx, dy),
#  label placement: right/left/above/below)
# NOTE: the ledger lists 14 pin locations; the brief says "13 pins". All 14
# listed locations are drawn so no story loses its map presence.
PINS = [
    ("Gulf of Finland", "1", 25.0, 60.0, True, (-24, -10), "left"),
    ("Antalya", "2", 30.7, 36.9, True, (-22, 14), "below"),
    ("Guasave", "3", -108.5, 25.6, True, (8, -10), "right"),
    ("Brasilia", "04", -47.9, -15.8, False, (0, 0), "right"),
    ("Kyiv", "05", 30.5, 50.4, True, (16, 6), "right"),
    ("Jerusalem", "06", 35.2, 31.8, False, (12, 8), "right"),
    ("New Delhi", "07", 77.2, 28.6, True, (8, -12), "right"),
    ("Tyre", "08", 35.2, 33.3, False, (-20, -14), "left"),
    ("Basra", "09", 47.8, 30.5, False, (14, 6), "right"),
    ("Tupancireta", "10", -53.6, -29.0, False, (0, 0), "right"),
    ("Bayelsa", "11", 6.3, 4.9, False, (0, 0), "right"),
    ("Wellington", "12", 174.8, -41.3, True, (-16, -12), "left"),
    ("Geneva", "17", 6.1, 46.2, False, (-20, 16), "left"),
    ("Paris / Lisbon", "13", 2.35, 48.85, False, (-52, 18), "right"),
]


def draw_map(draw, x0, y0, x1, y1):
    """Simplified world map with numbered pins. lon -170..190, lat 75..-55."""
    def px(lon, lat):
        return (x0 + (lon + 170) / 360 * (x1 - x0),
                y0 + (75 - lat) / 130 * (y1 - y0))
    # faint graticule
    for lon in range(-150, 181, 30):
        gx = x0 + (lon + 170) / 360 * (x1 - x0)
        draw.line([(gx, y0), (gx, y1)], fill=(232, 229, 221), width=1)
    for lat in (60, 30, 0, -30):
        gy = y0 + (75 - lat) / 130 * (y1 - y0)
        draw.line([(x0, gy), (x1, gy)], fill=(232, 229, 221), width=1)
    for poly in CONTINENTS:
        pts = [px(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_EDGE)
    f_pin = font(SANS_B, 8)
    f_lab = font(SANS_B, 9)
    for name, num, lon, lat, labelled, (dx, dy), place in PINS:
        cx, cy = px(lon, lat)
        ox, oy = cx + dx, cy + dy
        if dx or dy:
            draw.line([(cx, cy), (ox, oy)], fill=RED, width=1)
        r = 7
        draw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=RED,
                     outline=WHITE, width=1)
        tw = text_w(draw, num, f_pin)
        draw.text((ox - tw / 2, oy - 5), num, font=f_pin, fill=WHITE)
        if labelled:
            # white halo so the label reads over land
            lw = text_w(draw, name, f_lab)
            if place == "right":
                lx, ly = ox + 9, oy - 4
            elif place == "left":
                lx, ly = ox - 9 - lw, oy - 4
            elif place == "above":
                lx, ly = ox - lw / 2, oy - 20
            else:  # below
                lx, ly = ox - lw / 2, oy + 9
            for hx in (-1, 0, 1):
                for hy in (-1, 0, 1):
                    draw.text((lx + hx, ly + hy), name, font=f_lab,
                              fill=PAPER)
            draw.text((lx, ly), name, font=f_lab, fill=INK)


# ---------------------------------------------------------------- illustrations
def draw_tanker(draw, x0, y0, x1, y1):
    """Lead 1: burning tanker on a dark Baltic sea, dusk."""
    w, h = x1 - x0, y1 - y0
    # dusk sky: smooth 8-band gradient, deep blue-grey to pale horizon
    top, bot = (28, 40, 56), (96, 110, 130)
    for i in range(8):
        t = i / 7
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        draw.rectangle([x0, y0 + i * h // 8, x1, y0 + (i + 1) * h // 8],
                       fill=c)
    # sea
    sea_y = y0 + int(h * 0.62)
    draw.rectangle([x0, sea_y, x1, y1], fill=(30, 46, 62))
    for i in range(5):
        yy = sea_y + 8 + i * 9
        draw.line([(x0 + 6, yy), (x1 - 6, yy)], fill=(52, 70, 88), width=1)
    # fire glow on the water (flat, under the flames)
    draw.ellipse([x0 + w * 0.36, sea_y + 8, x0 + w * 0.56, sea_y + 20],
                 fill=(140, 70, 24))
    # hull (lighter than the night sea so it reads)
    hx0, hx1 = x0 + int(w * 0.08), x0 + int(w * 0.92)
    hy = sea_y - 6
    draw.polygon([(hx0, hy - 26), (hx1, hy - 26), (hx1 - 14, hy + 12),
                  (hx0 + 18, hy + 12)], fill=(36, 50, 66))
    draw.polygon([(hx0, hy - 26), (hx1, hy - 26), (hx1 - 4, hy - 14),
                  (hx0 + 5, hy - 14)], fill=(58, 74, 92))
    draw.line([(hx0, hy - 26), (hx1, hy - 26)], fill=(185, 28, 28), width=3)
    # white wake at the bow
    draw.line([(hx1 - 14, hy + 12), (hx1 + 8, hy + 16)], fill=(200, 210, 220),
              width=2)
    # deck structures + containers
    draw.rectangle([x0 + w * 0.70, hy - 52, x0 + w * 0.86, hy - 26],
                   fill=(52, 66, 82))
    draw.rectangle([x0 + w * 0.73, hy - 66, x0 + w * 0.83, hy - 52],
                   fill=(70, 86, 104))
    draw.rectangle([x0 + w * 0.76, hy - 66, x0 + w * 0.80, hy - 58],
                   fill=(251, 191, 36))
    for i, c in enumerate([(150, 90, 50), (90, 120, 140), (170, 110, 70)]):
        cx = x0 + w * (0.14 + i * 0.13)
        draw.rectangle([cx, hy - 48, cx + w * 0.11, hy - 26], fill=c,
                       outline=(30, 46, 62))
    # mast with a small pennant
    draw.line([(x0 + w * 0.68, hy - 26), (x0 + w * 0.68, hy - 74)],
              fill=(20, 30, 42), width=3)
    draw.polygon([(x0 + w * 0.68, hy - 74), (x0 + w * 0.68 + 12, hy - 71),
                  (x0 + w * 0.68, hy - 68)], fill=(185, 28, 28))
    # flames: three narrow tongues above mid-ship
    fx = x0 + w * 0.45
    for (fw, fh, col) in [(34, 44, (249, 115, 22)), (24, 34, (251, 191, 36)),
                          (13, 22, (254, 243, 199))]:
        draw.polygon([(fx - fw / 2, hy - 24), (fx - fw / 5, hy - 24 - fh),
                      (fx, hy - 24 - fh - 10), (fx + fw / 5, hy - 24 - fh),
                      (fx + fw / 2, hy - 24)], fill=col)
    for (sx, sy, sr) in [(0.36, 0.30, 6), (0.54, 0.28, 6)]:
        draw.polygon([(x0 + w * sx - sr, hy - 24),
                      (x0 + w * sx, hy - 24 - sr * 2),
                      (x0 + w * sx + sr, hy - 24)], fill=(249, 115, 22))
    # smoke: small puffs trailing up and right, shrinking as they rise
    for (sx, sy, sr, col) in [
            (0.45, 0.44, 10, (96, 102, 112)), (0.49, 0.34, 12, (110, 116, 126)),
            (0.54, 0.24, 13, (122, 128, 138)), (0.60, 0.14, 14, (134, 140, 150)),
            (0.67, 0.06, 12, (146, 152, 160))]:
        draw.ellipse([x0 + w * sx - sr, y0 + h * sy - sr,
                      x0 + w * sx + sr, y0 + h * sy + sr], fill=col)
    # birds
    for bx, by in [(0.18, 0.12), (0.24, 0.09), (0.82, 0.14)]:
        draw.arc([x0 + w * bx - 6, y0 + h * by - 4, x0 + w * bx + 6,
                  y0 + h * by + 4], 200, 340, fill=(200, 210, 220), width=2)


def draw_plenary(draw, x0, y0, x1, y1):
    """Lead 2: empty plenary hall at dawn, Antalya."""
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(231, 220, 195))
    # dawn windows
    for i in range(4):
        wx0 = x0 + 14 + i * (w - 28) // 4
        wx1 = wx0 + (w - 28) // 4 - 10
        draw.rectangle([wx0, y0 + 8, wx1, y0 + int(h * 0.42)],
                       fill=(245, 217, 139), outline=(180, 150, 100))
        draw.line([(wx0 + (wx1 - wx0) // 2, y0 + 8),
                   (wx0 + (wx1 - wx0) // 2, y0 + int(h * 0.42))],
                  fill=(180, 150, 100), width=1)
    # light beams on the floor
    for i in range(4):
        bx = x0 + 30 + i * (w - 60) // 4
        draw.polygon([(bx, y0 + int(h * 0.42)), (bx + 26, y0 + int(h * 0.42)),
                      (bx + 52, y1), (bx + 8, y1)], fill=(238, 226, 180))
    # floor
    draw.rectangle([x0, y0 + int(h * 0.62), x1, y1], fill=(138, 123, 99))
    # curved desk rows (three arcs approximated by trapezoid rows)
    for r, (ry, rw, dh) in enumerate([(0.52, 0.86, 16), (0.64, 0.94, 17),
                                      (0.77, 1.0, 18)]):
        dw = int(w * rw)
        dx0 = x0 + (w - dw) // 2
        dy = y0 + int(h * ry)
        draw.polygon([(dx0, dy), (dx0 + dw, dy), (dx0 + dw + 8, dy + dh),
                      (dx0 - 8, dy + dh)], fill=(124, 90, 58))
        draw.polygon([(dx0 + 4, dy + 2), (dx0 + dw - 4, dy + 2),
                      (dx0 + dw - 2, dy + dh - 2), (dx0 + 2, dy + dh - 2)],
                     fill=(156, 122, 77))
        # papers + microphones on the desks
        n = 5 if r < 2 else 6
        for i in range(n):
            px = dx0 + 12 + i * (dw - 24) // max(n - 1, 1)
            draw.rectangle([px, dy + 4, px + 12, dy + 10], fill=(250, 247, 240))
            draw.line([(px + 6, dy + 4), (px + 6, dy - 2)], fill=INK, width=1)
        # empty chairs behind the row
        for i in range(n):
            px = dx0 + 12 + i * (dw - 24) // max(n - 1, 1)
            draw.rectangle([px - 2, dy - 12, px + 10, dy - 2],
                           fill=(60, 48, 38))
    # podium, centre front
    px0 = x0 + w // 2 - 26
    draw.rectangle([px0, y0 + int(h * 0.86), px0 + 52, y1 - 6],
                   fill=(90, 64, 40))
    draw.rectangle([px0 + 4, y0 + int(h * 0.86) - 8, px0 + 48,
                    y0 + int(h * 0.86)], fill=(124, 90, 58))
    draw.line([(x0 + w // 2, y0 + int(h * 0.86) - 8),
               (x0 + w // 2, y0 + int(h * 0.86) - 22)], fill=INK, width=2)
    draw.ellipse([x0 + w // 2 - 3, y0 + int(h * 0.86) - 25,
                  x0 + w // 2 + 3, y0 + int(h * 0.86) - 19], fill=INK)
    # flags: EU (blue, gold dots) and host (red) flanking the podium
    for fx, col in [(x0 + w * 0.28, (0, 51, 153)), (x0 + w * 0.72, (185, 28, 28))]:
        draw.line([(fx, y0 + int(h * 0.70)), (fx, y1 - 6)], fill=(90, 80, 60),
                  width=2)
        draw.rectangle([fx, y0 + int(h * 0.70), fx + 32, y0 + int(h * 0.70) + 20],
                       fill=col)
        if col[0] == 0:
            for k in range(6):
                draw.ellipse([fx + 7 + k * 3, y0 + int(h * 0.70) + 8,
                              fx + 9 + k * 3, y0 + int(h * 0.70) + 10],
                             fill=(251, 191, 36))


def draw_raid(draw, x0, y0, x1, y1):
    """Lead 3: Sinaloa night raid — helicopter, searchlight, rooftops."""
    w, h = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(15, 27, 45))
    # stars + moon
    for sx, sy, sr in [(0.08, 0.10, 1), (0.20, 0.06, 2), (0.34, 0.14, 1),
                       (0.55, 0.08, 1), (0.72, 0.05, 2), (0.88, 0.12, 1),
                       (0.94, 0.22, 1), (0.12, 0.26, 1), (0.46, 0.04, 1)]:
        draw.ellipse([x0 + w * sx - sr, y0 + h * sy - sr,
                      x0 + w * sx + sr, y0 + h * sy + sr], fill=(226, 232, 240))
    draw.ellipse([x0 + w * 0.82, y0 + h * 0.04, x0 + w * 0.90, y0 + h * 0.14],
                 fill=(226, 220, 190))
    # searchlight cone from the helicopter down to the street
    hx, hy = x0 + w * 0.46, y0 + h * 0.28
    draw.polygon([(hx - 8, hy + 6), (hx + 8, hy + 6),
                  (x0 + w * 0.72, y0 + h * 0.92),
                  (x0 + w * 0.42, y0 + h * 0.92)], fill=(253, 230, 138))
    # helicopter silhouette (larger, so the shape reads)
    draw.ellipse([hx - 46, hy - 16, hx + 36, hy + 14], fill=(5, 8, 13))
    draw.polygon([(hx + 28, hy - 6), (hx + 88, hy - 14), (hx + 88, hy - 2),
                  (hx + 28, hy + 6)], fill=(5, 8, 13))
    draw.polygon([(hx + 82, hy - 14), (hx + 96, hy - 26), (hx + 96, hy - 2),
                  (hx + 88, hy - 2)], fill=(5, 8, 13))
    draw.line([(hx - 72, hy - 24), (hx + 62, hy - 24)], fill=(5, 8, 13),
              width=5)
    draw.line([(hx + 90, hy - 30), (hx + 90, hy + 4)], fill=(5, 8, 13),
              width=3)
    draw.line([(hx - 16, hy + 14), (hx - 10, hy + 26)], fill=(5, 8, 13),
              width=3)
    draw.line([(hx + 12, hy + 14), (hx + 18, hy + 26)], fill=(5, 8, 13),
              width=3)
    draw.line([(hx - 16, hy + 26), (hx + 18, hy + 26)], fill=(5, 8, 13),
              width=3)
    draw.ellipse([hx - 36, hy - 8, hx - 16, hy + 4], fill=(120, 140, 160))
    # distant hills
    draw.polygon([(x0, y0 + h * 0.78), (x0 + w * 0.25, y0 + h * 0.66),
                  (x0 + w * 0.5, y0 + h * 0.76), (x0 + w * 0.75, y0 + h * 0.68),
                  (x1, y0 + h * 0.78), (x1, y1), (x0, y1)], fill=(26, 38, 54))
    # rooftops
    roofs = [(0.02, 0.86, 0.20, 0.10), (0.22, 0.82, 0.18, 0.14),
             (0.42, 0.88, 0.16, 0.08), (0.60, 0.84, 0.18, 0.12),
             (0.80, 0.88, 0.18, 0.08)]
    for rx, ry, rw, rh in roofs:
        draw.rectangle([x0 + w * rx, y0 + h * ry, x0 + w * (rx + rw),
                        y0 + h * (ry + rh)], fill=(10, 16, 26))
        draw.rectangle([x0 + w * rx - 3, y0 + h * ry - 5,
                        x0 + w * (rx + rw) + 3, y0 + h * ry],
                       fill=(16, 24, 36))
    # lit windows
    for wx, wy in [(0.07, 0.88), (0.13, 0.90), (0.27, 0.84), (0.33, 0.87),
                   (0.47, 0.90), (0.65, 0.86), (0.71, 0.89), (0.85, 0.90)]:
        draw.rectangle([x0 + w * wx, y0 + h * wy, x0 + w * wx + 6,
                        y0 + h * wy + 7], fill=(251, 191, 36))
    # street + headlights in the beam
    draw.rectangle([x0, y0 + int(h * 0.95), x1, y1], fill=(8, 12, 20))
    for vx in (0.50, 0.56, 0.62):
        draw.ellipse([x0 + w * vx - 3, y0 + h * 0.94,
                      x0 + w * vx + 3, y0 + h * 0.97], fill=(254, 243, 199))
    # dust haze at the beam foot
    draw.ellipse([x0 + w * 0.44, y0 + h * 0.88, x0 + w * 0.70, y0 + h * 0.96],
                 fill=(120, 100, 70))


# ---------------------------------------------------------------- content
# All figures from ledger-v1.md only. Day-labels are honest: Sat = 21 Nov,
# Fri = 20 Nov, Sun = 22 Nov.
STRIP = [
    ("BALTIC", "Sparta II still burning in the Gulf of Finland — fire rages into Sunday"),
    ("CLIMATE", "COP31 nears a deal in Antalya — objections due 03:00 GMT, vote 06:00 GMT"),
    ("MEXICO", "El Chapo Isidro seized in a Friday-night raid on Guasave, Sinaloa"),
    ("UKRAINE", "Kryvyi Rih toll: 2 dead, ~60 wounded; Kyiv hit by 110 missiles + 400 drones"),
]

STATS = [
    ("110 + 400", "missiles + drones, Kyiv barrage"),
    ("03:00 GMT", "objections due on COP31 package"),
    ("440,000", "evacuated ahead of Cyclone Akvan"),
    ("82,500", "marched in France on Saturday"),
    ("$120bn", "adaptation target dropped from COP31 draft"),
    ("128", "countries at the Geneva killer-robot talks"),
]

LEADS = [
    dict(tag="SUNDAY — GULF OF FINLAND",
         head=["BALTIC ABLAZE", "SPARTA II STILL BURNING"],
         body=("Sanctioned Russian cargo ship hit by a drone strike in the Gulf "
               "of Finland on Saturday; the fire still burns on Sunday. 16 crew "
               "evacuated. Finland warns the war is 'spilling over'."),
         art=draw_tanker),
    dict(tag="SUNDAY — ANTALYA",
         head=["COP31: DEAL", "IN SIGHT"],
         body=("A new package was announced at a late-night plenary; President "
               "Murat Kurum says it is a text all parties can agree on. "
               "Objections due 03:00 GMT, approval session at 06:00 GMT Sunday. "
               "Fossil fuels and finance remain the sticking points."),
         art=draw_plenary),
    dict(tag="FRIDAY NIGHT — GUASAVE, SINALOA",
         head=["EL CHAPO ISIDRO", "SEIZED"],
         body=("FBI most-wanted Fausto Isidro Meza-Flores was captured in a raid "
               "on Guasave, Sinaloa, on Friday night. 11 dead, 8 arrested. "
               "Flown to Mexico City on Saturday."),
         art=draw_raid),
]

CARDS = [
    ("04", "BOLSONARO IN ICU",
     "Admitted Fri with a bowel obstruction; in ICU in Brasilia Sat, stable "
     "at 71. Serving a 27-year sentence."),
    ("05", "KRYVYI RIH: 2 DEAD, ~60 WOUNDED",
     "Russian 'triple-tap' strike Fri night on Zelenskyy's hometown: a boy of 7 "
     "and a paramedic of 20 killed, ~60 wounded."),
    ("06", "EISENKOT INVITES LIKUD",
     "Gadi Eisenkot invites Likud to resume coalition talks beginning Sunday. "
     "His mandate expires in early Dec."),
    ("07", "NEPAL PM SHAH ARRIVES",
     "Balendra Shah arrives in New Delhi today for a two-day state visit, his "
     "first bilateral trip since March."),
    ("08", "UNIFIL HANDOVER BEGINS",
     "Peacekeepers began transferring positions in south Lebanon to the army, "
     "announced Sat in Tyre. Mandate ends 31 Dec 2026."),
    ("09", "BASRA POWER-STATION FIRE",
     "Fire at the Hartha power station Sat: at least 4 dead, 35 injured. Gas "
     "pipeline blast; ~17 houses damaged."),
    ("10", "BRAZIL SUPERCELL",
     "Rare supercell hit Tupancireta Fri with 114 km/h gusts: at least 3 dead, "
     "5,000+ homes damaged."),
    ("11", "NIGERIA BOAT: AT LEAST 24 DEAD",
     "Funeral boat capsized Fri in Bayelsa, 300+ aboard; at least 24 dead "
     "(AP/NEMA), 24 rescued. Search goes on."),
    ("12", "INDIA v NZ: PANT 128",
     "Day 4 live in Wellington: Pant's 128 lifts India to 629/6, a lead of 261. "
     "His 9th Test hundred."),
    ("13", "EUROPE PROTESTS",
     "82,500 marched in France Sat (21,500 Paris); thousands in Lisbon in "
     "the rain; Berlin ~4,000; Helsinki ~200."),
]

# (bold lead-in incl. colon, rest) — one line each, 11 rows per column.
DIGEST_A = [
    ("PENTAGON–CANADA MEMO (Sat): ", "Hegseth memo limits think tanks, not ops — Rounds"),
    ("QESHM (Sat): ", "Tehran says blasts were ordnance disposal, not a strike — unverified"),
    ("AKVAN AFTERMATH (Sat): ", "Odisha crop survey; 440,000+ evacuated; 0 deaths"),
    ("KILLER ROBOTS (Sat, Geneva): ", "128 states to draft rules by 2028; no binding deal"),
    ("ZELENSKY (Sat): ", "calls Putin 'a killer' after Trump called him a 'friend'"),
    ("TRUMP ON IRAN (Sat): ", "presses for a 'permanent deal'; 'took out two regimes'"),
    ("ESTONIA BORDER (Sat): ", "5 crossings shut from 1 Dec for 6 months"),
    ("AUSTRALIA T20 WIN (Sat): ", "chased 188, beat England by 3 wickets at the MCG"),
    ("NITISH SETU (Sat): ", "Modi opens 19.7 km bridge in Bihar; Rs 4,280 crore"),
    ("MAMDANI: RIKERS BY 2032 (Fri): ", "plan for 4 borough jails; $146m"),
    ("MELANIA CEASEFIRE REMARKS (Fri): ", "at Christmas tree lighting; reported Sat"),
]
DIGEST_B = [
    ("VIRGINIA MEASLES DEATH (Fri): ", "child aged 0-4; first in Virginia since 1978"),
    ("GUPTA SENTENCED 235 MONTHS (Fri): ", "Pannun murder-for-hire plot"),
    ("DENMARK EXPELS ATTACHE (Fri): ", "Russian defence attache expelled over plot claim"),
    ("IRGC CLAIMS 58TH MQ-9 (Sat): ", "claim, unverified, no US comment"),
    ("THIRD CARRIER GROUP (Sat): ", "USS Theodore Roosevelt joins two carriers in Gulf"),
    ("FBI NCIC HACK (Sat): ", "FBI probes apparent breach of crime database"),
    ("PALISADES VERDICT (Fri): ", "Rinderknecht guilty; fire killed 12, ~7,000 homes"),
    ("CUMMINS STAYS CAPTAIN (Sat): ", "Cricket Australia backs him unanimously"),
    ("TRAFALGAR TREE FELLED (Fri): ", "'Jolly Cheery', 21 m, ~75 years, felled"),
    ("KHARKIV SATURDAY STRIKES (Sat): ", "11 wounded in drone hit on flats"),
    ("STREETING: 'COLD-BLOODED KILLER' (Sat): ", "UK defence chief in Kyiv on Putin"),
]

DATE_CHECK = [
    "Peru quake M6.9 — Fri 20 Nov",
    "Iran strikes on Kuwait + Bahrain — Wed 19 Nov",
    "Shenzhen Trump–Xi–Putin summit — 19 Nov",
    "ICJ Rohingya verdict — 19 Nov",
    "UK–EU reset deal — 20 Nov",
    "BepiColombo Mercury arrival — 20 Nov",
    "US aviation warning — Thu 19 Nov",
    "ADNOC vessel attack — Tue 17 Nov",
]

FOOTER = [
    "Sources: Reuters, AP, BBC, CNN, ESPNcricinfo, NPR, PressTV, The Times of India — 21–22 November 2026.",
    "All figures as reported; unverified claims labelled. Generated deterministically; no photographs.",
]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 14                      # side margin
    CW = W - 2 * MX              # 996 content width

    # ---- 1. masthead (y 0-66)
    f_kick = font(SANS_B, 14)
    kick = "SUNDAY 22 NOVEMBER 2026"
    d.text((W - MX - text_w(d, kick, f_kick), 8), kick, font=f_kick, fill=RED)
    f_title = font(SERIF_B, 34)
    title = "THE WORLD IN ONE DAY"
    d.text(((W - text_w(d, title, f_title)) / 2, 6), title, font=f_title,
           fill=INK)
    f_sub = font(SANS_R, 11)
    sub = "Thirty-five stories from the weekend — every date checked."
    d.text(((W - text_w(d, sub, f_sub)) / 2, 52), sub, font=f_sub, fill=GREY)
    hline(d, MX, W - MX, 66, fill=INK, width=2)

    # ---- region counts (y 68-80)
    f_reg = font(SANS_B, 11)
    f_regn = font(SANS_B, 11)
    segs = []
    for name, num in [("EUROPE ", "11"), (" · THE AMERICAS ", "11"),
                      (" · MIDDLE EAST ", "6"), (" · ASIA-PACIFIC ", "3"),
                      (" · OCEANIA ", "3"), (" · AFRICA ", "1")]:
        segs.append((name, f_reg, INK))
        segs.append((num, f_regn, RED))
    center_rich(d, W / 2, 70, segs)

    # ---- 2. four-story strip (y 82-140)
    f_tag = font(SANS_B, 12)
    f_strip = font(SANS_R, 12)
    y = 84
    for tag, text in STRIP:
        d.text((MX, y), tag, font=f_tag, fill=RED)
        d.text((MX + 92, y), text, font=f_strip, fill=INK)
        y += 14
    hline(d, MX, W - MX, 141, fill=BORDER, width=1)

    # ---- 3. stat strip (y 142-188): 6 boxes
    f_num = font(SANS_B, 19)
    f_lab = font(SANS_R, 10)
    bw = CW // 6
    for i, (num, lab) in enumerate(STATS):
        x0 = MX + i * bw
        x1 = x0 + bw - 2 if i < 5 else W - MX
        box(d, x0, 143, x1, 188, outline=BORDER, width=1, fill=WHITE)
        nw = text_w(d, num, f_num)
        d.text((x0 + (x1 - x0 - nw) / 2, 146), num, font=f_num, fill=RED)
        lines = fit(d, lab, f_lab, (x1 - x0) - 10, 2, f"stat {num}")
        ly = 168
        for ln in lines:
            lw = text_w(d, ln, f_lab)
            d.text((x0 + (x1 - x0 - lw) / 2, ly), ln, font=f_lab, fill=INK)
            ly += 11

    # ---- 4. region tabs (y 190-206)
    f_tab = font(SANS_B, 11)
    tabs = "EUROPE      |      MIDDLE EAST      |      AMERICAS      |      ASIA-PACIFIC      |      AFRICA"
    tw = text_w(d, tabs, f_tab)
    tx = (W - tw) / 2
    d.text((tx, 192), tabs, font=f_tab, fill=GREY)
    ew = text_w(d, "EUROPE", f_tab)
    hline(d, tx, tx + ew, 206, fill=RED, width=2)
    hline(d, MX, W - MX, 208, fill=BORDER, width=1)

    # ---- 5. three illustrated leads (y 210-522)
    lw3 = 325
    f_ltag = font(SANS_B, 11)
    f_lhead = font(SERIF_B, 20)
    f_lbody = font(SANS_R, 11)
    for i, lead in enumerate(LEADS):
        x0 = MX + i * (lw3 + 10)
        x1 = x0 + lw3
        lead["art"](d, x0, 212, x1, 356)
        box(d, x0, 212, x1, 356, outline=BORDER, width=1)
        d.text((x0, 362), lead["tag"], font=f_ltag, fill=RED)
        hy = 378
        for ln in lead["head"]:
            d.text((x0, hy), ln, font=f_lhead, fill=INK)
            hy += 23
        lines = fit(d, lead["body"], f_lbody, lw3, 5, f"lead {i + 1}")
        draw_lines(d, x0, 428, lines, f_lbody, leading=13)
        if i < 2:
            d.line([(x1 + 5, 212), (x1 + 5, 516)], fill=BORDER, width=1)
    hline(d, MX, W - MX, 522, fill=INK, width=1)

    # ---- 6. numbered cards 04-13 (y 524-700): 2 rows x 5
    f_cnum = font(SERIF_B, 16)
    f_chead = font(SANS_B, 11)
    f_cbody = font(SANS_R, 10)
    cw5, ch5, gap5 = 192, 86, 8
    for idx, (num, head, body) in enumerate(CARDS):
        row, col = divmod(idx, 5)
        x0 = MX + col * (cw5 + gap5)
        y0 = 526 + row * (ch5 + 4)
        box(d, x0, y0, x0 + cw5, y0 + ch5, outline=BORDER, width=1,
            fill=WHITE)
        d.text((x0 + 6, y0 + 5), num, font=f_cnum, fill=RED)
        lines = fit(d, head, f_chead, cw5 - 44, 2, f"card {num} head")
        draw_lines(d, x0 + 38, y0 + 6, lines, f_chead, leading=12)
        blines = fit(d, body, f_cbody, cw5 - 12, 4, f"card {num} body")
        draw_lines(d, x0 + 6, y0 + 34, blines, f_cbody, leading=12)
    hline(d, MX, W - MX, 702, fill=BORDER, width=1)

    # ---- 7. map (left) + DATE CHECK (right), titles y 704-718
    f_sect = font(SANS_B, 13)
    d.text((MX, 706), "WHERE IT HAPPENED", font=f_sect, fill=INK)
    dc_title = "DATE CHECK — NOT 22 NOVEMBER"
    d.text((660, 706), dc_title, font=f_sect, fill=RED)
    hline(d, MX, 650, 722, fill=INK, width=1)
    hline(d, 660, W - MX, 722, fill=RED, width=2)
    draw_map(d, MX, 726, 650, 850)
    # DATE CHECK box
    box(d, 660, 726, W - MX, 850, outline=RED, width=2, fill=WHITE)
    f_dc = font(SANS_R, 10)
    f_dcb = font(SANS_B, 10)
    y = 731
    for item in DATE_CHECK:
        # bold the item name (before the em dash), regular the date
        if " — " in item:
            name, date = item.rsplit(" — ", 1)
            d.text((668, y), name + " — ", font=f_dcb, fill=INK)
            d.text((668 + text_w(d, name + " — ", f_dcb), y), date,
                   font=f_dc, fill=GREY)
        else:
            d.text((668, y), item, font=f_dc, fill=INK)
        y += 11
    f_dcfoot = font(SANS_I, 10)
    foot = ["Other front pages feature these as", "today's news. They are not."]
    draw_lines(d, 668, y + 2, foot, f_dcfoot, fill=RED, leading=11)

    # ---- 8. digest (y 854-992)
    d.text((MX, 856), "ALSO ON SUNDAY 22 NOVEMBER", font=f_sect, fill=INK)
    hline(d, MX, W - MX, 872, fill=INK, width=1)
    f_dig = font(SANS_R, 10)
    f_digb = font(SANS_B, 10)
    col_w = 488
    for ci, col in enumerate((DIGEST_A, DIGEST_B)):
        cx = MX + ci * (col_w + 20)
        y = 877
        for lead_in, rest in col:
            total = text_w(d, lead_in, f_digb) + text_w(d, rest, f_dig)
            if total > col_w:
                print(f"OVERFLOW digest: {lead_in + rest!r} "
                      f"({total:.0f}px > {col_w}px)", file=sys.stderr)
            d.text((cx, y), lead_in, font=f_digb, fill=INK)
            d.text((cx + text_w(d, lead_in, f_digb), y), rest, font=f_dig,
                   fill=INK)
            y += 11

    # ---- 9. footer (y 994-1022)
    hline(d, MX, W - MX, 994, fill=BORDER, width=1)
    f_foot = font(SANS_R, 10)
    y = 998
    for ln in FOOTER:
        lw = text_w(d, ln, f_foot)
        d.text(((W - lw) / 2, y), ln, font=f_foot, fill=GREY)
        y += 12
    return img


def main():
    import os
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = build()
    img.save(out, format="PNG", optimize=True, compress_level=6)
    print(f"wrote {out} {os.path.getsize(out)} bytes")


if __name__ == "__main__":
    main()
