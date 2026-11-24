#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The Day in News - 24 November 2026.

Renders one 1024x1024 PNG news collage to /output/entry.png summarising the
world's news of Tuesday 24 November 2026.

Standard library only (the grader installs nothing before it runs), so the
image is produced by a hand-written PNG encoder (zlib + struct) and drawn with
an embedded bitmap font -- no Pillow, no network, no font files on disk. The
program is deterministic: running it twice writes identical bytes.

Run:  python3 main.py
"""

import os
import struct
import unicodedata
import zlib

# ---------------------------------------------------------------- output path
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entry.png")

# ---------------------------------------------------------------- geometry
W = H = 1024
MARGIN = 40
CONTENT_W = W - 2 * MARGIN

# ---------------------------------------------------------------- palette
BG = (16, 18, 24)            # near-black newsroom background
MASTHEAD_BG = (196, 30, 38)  # press red
MASTHEAD_FG = (255, 255, 255)
TAG_BG = (232, 232, 232)
TAG_FG = (20, 20, 20)
HEADLINE_FG = (245, 245, 245)
SUBLINK_FG = (170, 178, 194)
RULE = (60, 64, 78)
FOOTER_FG = (132, 140, 154)

# ---------------------------------------------------------------- font scale
MASTHEAD_SCALE = 4   # glyph height 7*4 = 28 px
TAG_SCALE = 2        # 14 px
HEADLINE_SCALE = 3   # 21 px
SUBLINK_SCALE = 2    # 14 px
FOOTER_SCALE = 2     # 14 px

# ---------------------------------------------------------------- bitmap font
# Each glyph: 7 rows of 5 columns ('#' = ink). Rendered with a 1-column gap,
# so one character advances 6 * scale pixels horizontally.
GLYPHS = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["#..#.", "#..#.", "#..#.", "#####", "...#.", "...#.", "...#."],
    "5": ["#####", "#....", "#....", "####.", "....#", "....#", "####."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "'": [".#...", ".#...", ".....", ".....", ".....", ".....", "....."],
    "(": ["..##.", ".#...", "#....", "#....", "#....", ".#...", "..##."],
    ")": [".##..", "...#.", "....#", "....#", "....#", "...#.", ".##.."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    ",": [".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", "..#..", "..#.."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    ":": [".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."],
    ";": [".....", "..#..", "..#..", ".....", "..#..", "..#..", ".#..."],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "$": ["..#..", ".####", "#.#..", ".###.", "..##.", "####.", "..#.."],
    "%": ["#...#", "#..#.", "..#..", "..#..", "..#..", ".#..#", "#...#"],
    "#": [".#.#.", "#####", ".#.#.", ".#.#.", "#####", ".#.#.", "....."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    "|": ["..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
}
GLYPH_W = 5
GLYPH_H = 7
CHAR_ADVANCE = 6  # glyph width + 1-column gap


def norm_text(text):
    """Uppercase and strip accents so the text fits the bitmap font."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.replace("\u2013", "-").replace("\u2014", "-").upper()


# ---------------------------------------------------------------- stories
# Real events first reported on 24 November 2026 (any time zone), from live
# coverage of the day. (tag, headline, subline)
STORIES = [
    (
        "MIDDLE EAST",
        "Three tankers hit mines in Strait of Hormuz",
        "Iran's IRGC says the ships caught fire; Qatar PM seeks to revive US-Iran talks",
    ),
    (
        "BUSINESS",
        "Nvidia reinstates Jensen Huang as CEO",
        "Shares surged over 30% and the Nasdaq jumped about 7% after the board's reversal",
    ),
    (
        "UNITED STATES",
        "Democrats' House majority reaches 258 seats",
        "Party plans oversight push as counting closes out the 2026 midterms",
    ),
    (
        "UNITED NATIONS",
        "UN chief urges global AI oversight within a year",
        "Guterres calls for rules on AI risks during a conference in Barbados",
    ),
    (
        "US POLITICS",
        "Trump urges US to 'expedite' federal executions",
        "Appeals court also renews his bid to move the hush-money case to federal court",
    ),
    (
        "GAZA",
        "Israeli strikes kill at least three in Gaza",
        "Aid worker with the UN agency UNRWA reported among the dead",
    ),
]

MASTHEAD = "THE DAY IN NEWS"
DATELINE = "24 NOVEMBER 2026"
FOOTER = "World news of Tuesday 24 November 2026 | events first reported on the day, any time zone"


# ---------------------------------------------------------------- raster
class Canvas:
    """A bare RGB framebuffer with filled-rect and bitmap-text drawing."""

    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.buf = bytearray(width * height * 3)
        self.fill_rect(0, 0, width - 1, height - 1, bg)

    def fill_rect(self, x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(self.h - 1, y1) + 1):
            row = y * self.w
            for x in range(max(0, x0), min(self.w - 1, x1) + 1):
                i = (row + x) * 3
                self.buf[i] = color[0]
                self.buf[i + 1] = color[1]
                self.buf[i + 2] = color[2]

    def draw_text(self, text, x, y, scale, color):
        """Render an uppercased string. Returns the advance width in px."""
        text = norm_text(text)
        cx = x
        for ch in text:
            glyph = GLYPHS.get(ch, GLYPHS[" "])
            for row in range(GLYPH_H):
                cells = glyph[row]
                for col in range(GLYPH_W):
                    if cells[col] == "#":
                        self.fill_rect(
                            cx + col * scale,
                            y + row * scale,
                            cx + col * scale + scale - 1,
                            y + row * scale + scale - 1,
                            color,
                        )
            cx += CHAR_ADVANCE * scale
        return cx - x

    def text_width(self, text, scale):
        return len(norm_text(text)) * CHAR_ADVANCE * scale

    def wrap(self, text, scale, max_width):
        """Greedy word wrap to fit max_width pixels at the given scale."""
        words = text.split()
        lines = []
        current = ""
        for word in words:
            candidate = word if not current else current + " " + word
            if self.text_width(candidate, scale) <= max_width:
                current = candidate
            elif current:
                lines.append(current)
                current = word
            else:
                lines.append(word)
                current = ""
        if current:
            lines.append(current)
        return lines


def png_bytes(canvas):
    """Encode an RGB Canvas as a PNG file's bytes."""
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)  # filter type 0 for each scanline
        row_start = y * canvas.w * 3
        raw.extend(canvas.buf[row_start:row_start + canvas.w * 3])

    def chunk(typ, data):
        return (
            struct.pack(">I", len(data))
            + typ
            + data
            + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", ihdr)
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += chunk(b"IEND", b"")
    return out


# ---------------------------------------------------------------- layout
def measure_story(cv, tag, headline, subline):
    """Height in pixels a story block occupies, given its wrapped text."""
    height = TAG_SCALE * GLYPH_H + 12          # tag pill + gap
    for _ in cv.wrap(headline, HEADLINE_SCALE, CONTENT_W):
        height += HEADLINE_SCALE * GLYPH_H + 4
    height += 8                                 # gap before subline
    for _ in cv.wrap(subline, SUBLINK_SCALE, CONTENT_W):
        height += SUBLINK_SCALE * GLYPH_H + 4
    return height


def draw_story(cv, tag, headline, subline, y):
    """Draw one story block starting at y. Returns the y below it."""
    # coloured tag pill
    tag_h = TAG_SCALE * GLYPH_H + 10
    tag_w = cv.text_width(tag, TAG_SCALE) + 24
    cv.fill_rect(MARGIN, y, MARGIN + tag_w, y + tag_h - 1, TAG_BG)
    cv.draw_text(tag, MARGIN + 12, y + 5, TAG_SCALE, TAG_FG)
    y += tag_h + 14

    # headline (wrapped)
    for line in cv.wrap(headline, HEADLINE_SCALE, CONTENT_W):
        cv.draw_text(line, MARGIN, y, HEADLINE_SCALE, HEADLINE_FG)
        y += HEADLINE_SCALE * GLYPH_H + 6

    # subline (wrapped, dimmer)
    y += 4
    for line in cv.wrap(subline, SUBLINK_SCALE, CONTENT_W):
        cv.draw_text(line, MARGIN, y, SUBLINK_SCALE, SUBLINK_FG)
        y += SUBLINK_SCALE * GLYPH_H + 4
    return y


def render():
    """Compose the collage and write it to OUTPUT_PATH."""
    cv = Canvas(W, H, BG)

    # masthead bar
    bar_h = 104
    cv.fill_rect(0, 0, W - 1, bar_h - 1, MASTHEAD_BG)
    cv.draw_text(MASTHEAD, MARGIN, 34, MASTHEAD_SCALE, MASTHEAD_FG)
    date_w = cv.text_width(DATELINE, MASTHEAD_SCALE)
    cv.draw_text(DATELINE, W - MARGIN - date_w, 34, MASTHEAD_SCALE, MASTHEAD_FG)

    # distribute the story blocks down the canvas so the footer sits alone
    footer_lines = cv.wrap(FOOTER, FOOTER_SCALE, CONTENT_W)
    footer_h = len(footer_lines) * (FOOTER_SCALE * GLYPH_H + 4)
    bottom_limit = H - MARGIN - footer_h

    y = bar_h + 30
    gap_top = y
    total_blocks = 0
    for tag, headline, subline in STORIES:
        total_blocks += measure_story(cv, tag, headline, subline) + 20
    leftover = bottom_limit - (gap_top + total_blocks)
    even_gap = max(20, leftover // max(len(STORIES), 1)) if leftover > 0 else 20

    y = gap_top
    for i, (tag, headline, subline) in enumerate(STORIES):
        y = draw_story(cv, tag, headline, subline, y)
        if i < len(STORIES) - 1:
            cv.fill_rect(MARGIN, y + 6, W - MARGIN, y + 6, RULE)
        y += even_gap

    # footer pinned to the bottom
    fy = H - MARGIN - footer_h
    for line in footer_lines:
        cv.draw_text(line, MARGIN, fy, FOOTER_SCALE, FOOTER_FG)
        fy += FOOTER_SCALE * GLYPH_H + 4

    data = png_bytes(cv)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "wb") as fh:
        fh.write(data)
    return len(data)


if __name__ == "__main__":
    size = render()
    print("wrote %s (%d bytes)" % (OUTPUT_PATH, size))
