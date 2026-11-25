#!/usr/bin/env python3
"""news-image-20261124 — "The Day in News: 24 November 2026".

Generates /output/entry.png: one 1024x1024 image summing up the world's news
of Tuesday 24 November 2026.

STDLIB ONLY (zlib + struct + binascii.crc32). No PIL / no network / no fonts.
Text is rendered with a built-in anti-aliased vector (stroke) font.

Run: python3 main.py
"""
import os
import struct
import zlib
import binascii

OUT = "/output/entry.png"
W = H = 1024


# ---------------------------------------------------------------- PNG encoder
def write_png(path, width, height, rgb):
    """rgb: bytes/bytearray of width*height*3, top-down rows."""
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter type 0 (None)
        raw += rgb[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF))

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(bytes(png))
    return len(png)


# ------------------------------------------------------------------- Canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bg * (w * h))

    def _blend(self, x, y, col, cov):
        if x < 0 or y < 0 or x >= self.w or y >= self.h or cov <= 0:
            return
        i = (y * self.w + x) * 3
        a = cov
        self.buf[i] = int(self.buf[i] * (1 - a) + col[0] * a)
        self.buf[i + 1] = int(self.buf[i + 1] * (1 - a) + col[1] * a)
        self.buf[i + 2] = int(self.buf[i + 2] * (1 - a) + col[2] * a)

    def fill(self, col):
        self.buf = bytearray(col * (self.w * self.h))

    def rect(self, x, y, w, h, col):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(self.w, int(x + w)), min(self.h, int(y + h))
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for _ in range(x1 - x0):
                self.buf[i] = col[0]
                self.buf[i + 1] = col[1]
                self.buf[i + 2] = col[2]
                i += 3

    def line(self, x0, y0, x1, y1, col, thick=2.0):
        """Anti-aliased thick line with round caps (distance coverage)."""
        half = thick / 2.0
        pad = half + 1.5
        minx = int(min(x0, x1) - pad); maxx = int(max(x0, x1) + pad) + 1
        miny = int(min(y0, y1) - pad); maxy = int(max(y0, y1) + pad) + 1
        minx = max(0, minx); miny = max(0, miny)
        maxx = min(self.w, maxx); maxy = min(self.h, maxy)
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        for py in range(miny, maxy):
            cy = py + 0.5
            for px in range(minx, maxx):
                cx = px + 0.5
                if L2 == 0:
                    d = ((cx - x0) ** 2 + (cy - y0) ** 2) ** 0.5
                else:
                    t = ((cx - x0) * dx + (cy - y0) * dy) / L2
                    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
                    qx = x0 + t * dx - cx
                    qy = y0 + t * dy - cy
                    d = (qx * qx + qy * qy) ** 0.5
                cov = half + 0.5 - d
                if cov > 0:
                    self._blend(px, py, col, cov if cov < 1 else 1.0)


# ------------------------------------------------- vector stroke font (built-in)
# Coordinates: x right, y UP, baseline y=0, cap-height 100. Each glyph =
# (advance_width_units, [stroke, stroke, ...]); a stroke is a polyline.
# Round forms are sampled as Bezier/ellipse curves so they render smoothly.
SS = 4  # supersampling factor for crisp glyph anti-aliasing


def arc(cx, cy, rx, ry, a0, a1, n=12):
    """Ellipse arc, angles in degrees (0=right, CCW)."""
    import math
    pts = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        pts.append([cx + rx * math.cos(a), cy + ry * math.sin(a)])
    return pts


def qbez(p0, p1, p2, n=10):
    """Quadratic Bezier."""
    pts = []
    for k in range(n + 1):
        t = k / n
        u = 1 - t
        pts.append([u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]])
    return pts


GLYPHS = {
    'A': (64, [[[0, 0], [32, 100], [64, 0]], [[14, 34], [50, 34]]]),
    'B': (62, [[[0, 0], [0, 100], [40, 100]] + qbez([40, 100], [64, 100], [64, 76], 8) +
               qbez([64, 76], [64, 54], [40, 52], 8) + [[0, 52]],
               [[0, 52], [42, 52]] + qbez([42, 52], [64, 52], [64, 28], 8) +
               qbez([64, 28], [64, 0], [40, 0], 8) + [[0, 0]]]),
    'C': (60, [arc(32, 50, 28, 50, 22, -22, 14)]),
    'D': (60, [[[0, 0], [0, 100], [36, 100]] + qbez([36, 100], [60, 100], [60, 74], 8) +
               qbez([60, 74], [60, 22], [36, 0], 8) + [[0, 0]]]),
    'E': (58, [[[56, 100], [0, 100], [0, 0], [56, 0]], [[0, 50], [44, 50]]]),
    'F': (54, [[[56, 100], [0, 100], [0, 0]], [[0, 50], [42, 50]]]),
    'G': (62, [arc(32, 50, 28, 50, 22, -30, 14), [[60, -4], [60, 30], [36, 30]]]),
    'H': (64, [[[0, 0], [0, 100]], [[64, 0], [64, 100]], [[0, 50], [64, 50]]]),
    'I': (24, [[[0, 0], [0, 100]], [[-12, 100], [12, 100]], [[-12, 0], [12, 0]]]),
    'J': (30, [[[24, 100], [24, 18]] + qbez([24, 18], [24, 0], [8, 0], 8) +
               qbez([8, 0], [-10, 0], [-10, 20], 8)]),
    'K': (58, [[[0, 0], [0, 100]], [[56, 100], [0, 44]], [[14, 60], [56, 0]]]),
    'L': (54, [[[0, 100], [0, 0], [52, 0]]]),
    'M': (72, [[[0, 0], [0, 100], [36, 55], [72, 100], [72, 0]]]),
    'N': (60, [[[0, 0], [0, 100], [60, 0], [60, 100]]]),
    'O': (62, [arc(31, 50, 31, 50, 0, 360, 20)]),
    'P': (60, [[[0, 0], [0, 100], [40, 100]] + qbez([40, 100], [60, 100], [60, 76], 8) +
               qbez([60, 76], [60, 52], [40, 52], 8) + [[0, 52]]]),
    'Q': (64, [arc(31, 53, 31, 47, 0, 360, 20), [[40, 26], [66, -6]]]),
    'R': (60, [[[0, 0], [0, 100], [40, 100]] + qbez([40, 100], [60, 100], [60, 76], 8) +
               qbez([60, 76], [60, 54], [40, 52], 8) + [[0, 52]],
               [[30, 52], [60, 0]]]),
    'S': (60, [arc(29, 74, 24, 24, -10, -180, 10) + arc(29, 26, 24, 24, 170, 0, 10)]),
    'T': (64, [[[0, 100], [64, 100]], [[32, 100], [32, 0]]]),
    'U': (62, [[[0, 100], [0, 22]] + arc(31, 22, 31, 24, 180, 360, 12) + [[62, 100]]]),
    'V': (60, [[[0, 100], [30, 0], [60, 100]]]),
    'W': (72, [[[0, 100], [18, 0], [36, 60], [54, 0], [72, 100]]]),
    'X': (60, [[[0, 0], [60, 100]], [[60, 0], [0, 100]]]),
    'Y': (60, [[[0, 100], [30, 52], [60, 100]], [[30, 52], [30, 0]]]),
    'Z': (60, [[[0, 100], [60, 100], [0, 0], [60, 0]]]),
    '0': (60, [arc(30, 50, 30, 50, 0, 360, 20)]),
    '1': (42, [[[18, 78], [30, 100], [30, 0]], [[10, 0], [52, 0]]]),
    '2': (60, [[[2, 84]] + qbez([2, 84], [14, 100], [32, 100], 8) +
               qbez([32, 100], [56, 100], [56, 78], 8) +
               qbez([56, 78], [56, 58], [40, 40], 8) + [[2, 0], [60, 0]]]),
    '3': (58, [arc(30, 74, 24, 24, -20, -200, 10) + arc(30, 26, 24, 24, 200, -30, 12)]),
    '4': (60, [[[44, 0], [44, 100], [0, 32], [60, 32]]]),
    '5': (58, [[[54, 100], [4, 100], [0, 58]] + arc(28, 30, 28, 28, 75, -220, 14)]),
    '6': (58, [[[52, 100]] + qbez([52, 100], [20, 100], [8, 70], 8) +
               qbez([8, 70], [0, 40], [0, 28], 6) + arc(29, 28, 29, 28, 180, 360, 12)]),
    '7': (58, [[[0, 100], [60, 100], [24, 0]]]),
    '8': (64, [arc(32, 78, 21, 22, 0, 360, 16), arc(32, 26, 25, 26, 0, 360, 16)]),
    '9': (58, [arc(29, 72, 29, 28, 0, 180, 12) + [[58, 60]] +
               qbez([58, 60], [58, 88], [36, 100], 8) + [[4, 100]]]),
    'a': (52, [arc(25, 27, 25, 27, 20, -250, 16) + [[50, 55], [50, 0]]]),
    'b': (52, [[[0, 0], [0, 100]]] + [arc(25, 27, 25, 27, 90, -270, 16)]),
    'c': (48, [arc(25, 27, 23, 27, 30, -250, 14)]),
    'd': (52, [[[50, 0], [50, 100]]] + [arc(25, 27, 25, 27, 90, -270, 16)]),
    'e': (50, [arc(25, 27, 25, 27, 12, -348, 18), [[0, 28], [48, 28]]]),
    'f': (36, [[[46, 100], [30, 100]] + qbez([30, 100], [14, 100], [14, 78], 8) +
               [[14, 0]], [[0, 55], [34, 55]]]),
    'g': (52, [[[50, 55], [50, -18]] + qbez([50, -18], [50, -30], [30, -30], 8) +
               qbez([30, -30], [6, -30], [2, -18], 8),
               arc(25, 27, 25, 27, 20, -250, 16)]),
    'h': (50, [[[0, 0], [0, 100]], [[0, 20]] + arc(25, 20, 25, 22, 180, 360, 12) +
               [[50, 55]]]),
    'i': (22, [[[0, 0], [0, 55]], [[0, 80], [0, 82]]]),
    'j': (26, [[[22, 55], [22, -18]] + qbez([22, -18], [22, -30], [6, -30], 8) +
               qbez([6, -30], [-6, -30], [-6, -20], 6), [[22, 80], [22, 82]]]),
    'k': (48, [[[0, 0], [0, 100]], [[44, 55], [0, 20]], [[14, 32], [46, 0]]]),
    'l': (22, [[[0, 0], [0, 100]], [[-10, 100], [10, 100]]]),
    'm': (78, [[[0, 0], [0, 55]], [[0, 20]] + arc(18, 20, 18, 20, 180, 360, 10) + [[36, 55]],
               [[36, 20]] + arc(56, 20, 20, 20, 180, 360, 10) + [[76, 55]]]),
    'n': (50, [[[0, 0], [0, 55]], [[0, 20]] + arc(23, 20, 23, 22, 180, 360, 12) + [[46, 55]]]),
    'o': (50, [arc(25, 27, 25, 27, 0, 360, 18)]),
    'p': (52, [[[0, 0], [0, -30]]] + [arc(25, 27, 25, 27, 90, -270, 16)]),
    'q': (52, [[[50, 0], [50, -30]]] + [arc(25, 27, 25, 27, 90, -270, 16)]),
    'r': (44, [[[0, 0], [0, 55]], [[0, 26]] + qbez([0, 26], [12, 8], [30, 4], 8) +
               [[42, 6]]]),
    's': (46, [arc(23, 40, 20, 15, -20, -195, 9) + arc(23, 15, 20, 15, 160, -10, 9)]),
    't': (40, [[[14, 100], [14, 16]] + qbez([14, 16], [22, 4], [38, 2], 8) +
               [[44, 6]], [[0, 55], [34, 55]]]),
    'u': (50, [[[0, 55], [0, 20]] + arc(23, 20, 23, 22, 180, 360, 12) + [[46, 0], [46, 55]]]),
    'v': (48, [[[0, 55], [23, 0], [46, 55]]]),
    'w': (70, [[[0, 55], [18, 0], [34, 38], [50, 0], [68, 55]]]),
    'x': (48, [[[0, 0], [46, 55]], [[46, 0], [0, 55]]]),
    'y': (48, [[[0, 55], [23, 0], [46, 55]], [[23, 0], [23, -22], [12, -30], [-4, -30]]]),
    'z': (48, [[[0, 55], [46, 55], [0, 0], [46, 0]]]),
    ' ': (34, []),
    '.': (24, [[[0, 3], [0, 5]]]),
    ',': (24, [[[0, 6], [0, 4], [-4, -16]]]),
    ':': (24, [[[0, 52], [0, 54]], [[0, 6], [0, 8]]]),
    ';': (24, [[[0, 52], [0, 54]], [[0, 8], [0, 6], [-4, -14]]]),
    '-': (40, [[[6, 45], [34, 45]]]),
    '\u2013': (56, [[[0, 45], [56, 45]]]),
    '\u2014': (64, [[[0, 45], [64, 45]]]),
    "'": (20, [[[0, 70], [2, 100]]]),
    '\u2019': (20, [[[0, 70], [2, 100]]]),
    '"': (34, [[[0, 70], [2, 100]], [[16, 70], [18, 100]]]),
    '/': (60, [[[4, 0], [56, 100]]]),
    '+': (52, [[[8, 50], [44, 50]], [[26, 32], [26, 68]]]),
    '=': (52, [[[8, 58], [44, 58]], [[8, 36], [44, 36]]]),
    '(': (30, [[[20, 100], [4, 78], [4, 22], [20, 0]]]),
    ')': (30, [[[6, 100], [22, 78], [22, 22], [6, 0]]]),
    '>': (48, [[[8, 82], [40, 50], [8, 18]]]),
    '<': (48, [[[40, 82], [8, 50], [40, 18]]]),
    '%': (72, [[[3, 96], [3, 98]], [[64, 4], [64, 6]], [[8, 96], [62, 4]]]),
    '&': (62, [[[56, 20], [44, 6], [28, 4], [16, 16], [34, 42], [48, 58],
                [46, 74], [30, 84], [14, 78], [4, 62], [30, 26], [44, 8], [54, 0]]]),
    '!': (24, [[[0, 30], [0, 100]], [[0, 0], [0, 3]]]),
    '?': (54, [[[2, 78], [14, 100], [40, 100], [52, 84], [48, 64], [30, 52],
                [28, 40]], [[28, 0], [28, 3]]]),
    '#': (64, [[[14, 0], [20, 100]], [[44, 0], [50, 100]], [[4, 34], [60, 34]],
               [[2, 66], [58, 66]]]),
}


def text_width(s, cap):
    """Width in px for string at cap-height `cap` px."""
    sc = cap / 100.0
    return sum(GLYPHS.get(ch, GLYPHS['?'])[0] for ch in s) * sc


def _smooth(t):
    return t * t * (3 - 2 * t)


_GLYPH_CACHE = {}


def glyph_coverage(ch, cap, thick):
    """Return (w, h, top, rows_of_coverage) for a glyph, supersampled SS×.

    Coverage uses a hard edge with a narrow smoothstep for crisp AA.
    Cached per (char, cap, thick) so headline text rasterizes quickly.
    """
    key = (ch, round(cap, 2), round(thick, 3))
    hit = _GLYPH_CACHE.get(key)
    if hit is not None:
        return hit
    adv, strokes = GLYPHS.get(ch, GLYPHS['?'])
    sc = cap / 100.0
    th = thick / sc                       # thickness in glyph units
    half = th / 2.0
    if not strokes:                       # e.g. space
        res = (0, 0, 0, [])
        _GLYPH_CACHE[key] = res
        return res
    xs, ys = [], []
    for st in strokes:
        for px, py in st:
            xs.append(px); ys.append(py)
    xmin = min(xs) - half - 1.5; xmax = max(xs) + half + 1.5
    ymin = min(ys) - half - 1.5; ymax = max(ys) + half + 1.5
    gw = int(xmax * sc) + 2
    gh = int((ymax - ymin) * sc) + 2
    top = int(ymax * sc)                  # px above baseline to grid top
    # grid corners in glyph units
    gux0, guy0 = 0.0, ymax
    w_ss, h_ss = gw * SS, gh * SS
    step = 1.0 / SS / sc                  # glyph units per supersample step
    edge = step / 1.7                     # smooth edge width (glyph units)
    cov = [0.0] * (gw * gh)
    segs = [(st[i], st[i + 1]) for st in strokes for i in range(len(st) - 1)]
    for gsy in range(h_ss):
        gy = guy0 - (gsy + 0.5) * step
        cyr = (gsy // SS)
        for gsx in range(w_ss):
            gx = gux0 + (gsx + 0.5) * step
            best = 1e9
            for (ax, ay), (bx, by) in segs:
                dx = bx - ax; dy = by - ay
                L2 = dx * dx + dy * dy
                if L2 == 0:
                    d = ((gx - ax) ** 2 + (gy - ay) ** 2) ** 0.5
                else:
                    t = ((gx - ax) * dx + (gy - ay) * dy) / L2
                    if t < 0.0:
                        t = 0.0
                    elif t > 1.0:
                        t = 1.0
                    qx = ax + t * dx - gx
                    qy = ay + t * dy - gy
                    d = (qx * qx + qy * qy) ** 0.5
                if d < best:
                    best = d
            if best < half:
                u = (half - best) / edge
                if u > 1.0:
                    u = 1.0
                cov[cyr * gw + (gsx // SS)] += _smooth(u)
    n = SS * SS
    cov = [c / n for c in cov]
    res = (gw, gh, top, cov)
    _GLYPH_CACHE[key] = res
    return res


def draw_text(cv, x, y_base, s, cap, col, thick=None, spacing=0.0):
    """Draw string with baseline y_base (canvas coords, y down). Crisp AA."""
    sc = cap / 100.0
    if thick is None:
        thick = max(1.4, cap * 0.115)
    cx = x
    for ch in s:
        adv = GLYPHS.get(ch, GLYPHS['?'])[0]
        gw, gh, top, cov = glyph_coverage(ch, cap, thick)
        ox = int(round(cx))
        ytop = y_base - top
        oy = int(round(ytop))
        for r in range(gh):
            py = oy + r
            if py < 0 or py >= cv.h:
                continue
            base = r * gw
            brow = py * cv.w
            for c in range(gw):
                a = cov[base + c]
                if a <= 0.0:
                    continue
                px = ox + c
                if px < 0 or px >= cv.w:
                    continue
                i = (brow + px) * 3
                cv.buf[i] = int(cv.buf[i] * (1 - a) + col[0] * a)
                cv.buf[i + 1] = int(cv.buf[i + 1] * (1 - a) + col[1] * a)
                cv.buf[i + 2] = int(cv.buf[i + 2] * (1 - a) + col[2] * a)
        cx += adv * sc + spacing
    return cx - x


def wrap(cv, s, cap, maxw):
    words = s.split(' ')
    lines, cur = [], ''
    for w_ in words:
        t = (cur + ' ' + w_) if cur else w_
        if text_width(t, cap) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- palette
BG_TOP = (13, 17, 23)
BG_BOT = (22, 27, 34)
WHITE = (240, 242, 245)
GREY = (139, 148, 158)
RULE = (48, 54, 61)
RED = (248, 81, 73)

STORIES = [
    ("NVIDIA", (46, 204, 113), "Nvidia board reinstates Jensen Huang as CEO; stock soars 30%", "+30%"),
    ("IRAN", (253, 151, 31), "Iran vows to use all available tools against US naval blockade", "WAR"),
    ("UKRAINE", (88, 166, 255), "Russian strike on Zaporizhzhia kills 2, wounds 40, four are children", "40"),
    ("CLIMATE", (45, 212, 191), "COP31 ends in deadlock in Antalya over fossil fuel wording", "NO DEAL"),
    ("MEXICO", (192, 132, 252), "Cartel boss El Chapo Isidro captured in Sinaloa; extradition denied", "FBI"),
    ("YEMEN", (248, 81, 73), "Houthis: 41 civilians killed in Saudi strikes using US-made arms", "41"),
    ("SUDAN", (250, 204, 21), "RSF drones hit Khartoum as the national grid nears collapse", "GRID"),
    ("SPACE", (167, 139, 250), "BepiColombo reaches Mercury orbit after eight-year voyage", "8 YRS"),
]


def build():
    cv = Canvas(W, H, BG_TOP)
    # vertical gradient background
    for y in range(H):
        t = y / H
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        i = y * W * 3
        for x in range(W):
            cv.buf[i] = r; cv.buf[i + 1] = g; cv.buf[i + 2] = b; i += 3

    # ---- masthead
    mx = 46
    draw_text(cv, mx, 96, "THE DAY IN NEWS", 56, WHITE, thick=7.0)
    # date block, right aligned
    d = "TUESDAY 24 NOV 2026"
    dw = text_width(d, 22)
    draw_text(cv, W - 46 - dw, 74, d, 22, GREY, thick=3.0)
    sub = "THE WORLD IN EIGHT STORIES"
    sw = text_width(sub, 20)
    draw_text(cv, W - 46 - sw, 100, sub, 20, RED, thick=3.0)
    # rule under masthead
    cv.rect(mx, 124, W - 92, 3, RULE)
    cv.rect(mx, 130, 150, 4, RED)

    # ---- headline rows
    top = 156
    bottom = 946
    n = len(STORIES)
    rowh = (bottom - top) / n
    tagw = 132
    for idx, (tag, col, head, num) in enumerate(STORIES):
        ry = top + idx * rowh
        cy = ry + rowh / 2
        # row separator
        if idx:
            cv.rect(mx, ry, W - 92, 1, RULE)
        # category tag box
        boxh = 34
        bx, by = mx, cy - boxh / 2
        cv.rect(bx, by, tagw, boxh, col)
        tc = text_width(tag, 19)
        draw_text(cv, bx + (tagw - tc) / 2, by + boxh / 2 + 8, tag, 19, (13, 17, 23), thick=3.4)
        # headline
        hx = mx + tagw + 26
        avail = (W - 46 - (text_width(num, 40) + 30 if num else 0)) - hx
        lines = wrap(cv, head, 30, avail)[:2]
        lh = 38
        blockh = len(lines) * lh
        y0 = cy - blockh / 2 + 22
        for ln in lines:
            draw_text(cv, hx, y0, ln, 27, WHITE, thick=3.6)
            y0 += lh
        # big stat, right aligned
        if num:
            nw = text_width(num, 40)
            draw_text(cv, W - 46 - nw, cy + 14, num, 40, col, thick=5.0)

    # ---- footer
    cv.rect(mx, 962, W - 92, 1, RULE)
    ft = "make.fun news-image-20261124  \u00b7  generated by an AI agent from 24 Nov 2026 reporting  \u00b7  no network, stdlib only"
    draw_text(cv, mx, 996, ft, 17, GREY, thick=2.4)
    return cv


def main():
    os.makedirs("/output", exist_ok=True)
    cv = build()
    rgb = bytes(cv.buf)
    size = write_png(OUT, W, H, rgb)
    print("wrote", OUT, size, "bytes", W, "x", H)
    assert size <= 1024 * 1024, "image exceeds 1 MiB"
    print("OK stdlib-only PNG, no PIL used")


if __name__ == "__main__":
    main()
