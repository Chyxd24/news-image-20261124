#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The Day in News - 24 November 2026.

Renders one 1024x1024 PNG news collage to /output/entry.png summarising the
world's news of Tuesday 24 November 2026. Pure PIL, standard library only,
no network access. Safe to run twice: it writes the same bytes every time.

Run:  python3 main.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- output path
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entry.png")

# ---------------------------------------------------------------- geometry
W = H = 1024
MARGIN = 34
CONTENT_W = W - 2 * MARGIN

# ---------------------------------------------------------------- palette
BG = (16, 18, 24)          # near-black newsroom background
MASTHEAD_BG = (196, 30, 38)  # press red
MASTHEAD_FG = (255, 255, 255)
TAG_BG = (232, 232, 232)
TAG_FG = (20, 20, 20)
HEADLINE_FG = (245, 245, 245)
SUBLINK_FG = (168, 176, 192)
RULE = (60, 64, 78)
FOOTER_FG = (130, 138, 152)

# ---------------------------------------------------------------- font lookup
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def _font(path, size):
    """Load a TTF font, falling back to PIL's bitmap default if missing."""
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def load_fonts():
    """Return the (masthead, tag, headline, subline, footer) font tuple."""
    masthead = _font(BOLD, 40)
    tag = _font(BOLD, 18)
    headline = _font(BOLD, 29)
    subline = _font(REGULAR, 20)
    footer = _font(REGULAR, 17)
    return masthead, tag, headline, subline, footer


# ---------------------------------------------------------------- stories
# Real events first reported on 24 November 2026 (any time zone), sourced from
# live coverage of the day. (tag, headline, subline)
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
FOOTER = "World news of Tuesday 24 November 2026  |  events first reported on the day, any time zone"


# ---------------------------------------------------------------- helpers
def wrap(draw, text, font, max_width):
    """Greedy word wrap. Returns a list of lines fitting max_width pixels."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        elif current:
            lines.append(current)
            current = word
        else:
            # single word longer than the box: hard-break it
            chunk = ""
            for ch in word:
                if draw.textlength(chunk + ch, font=font) <= max_width:
                    chunk += ch
                else:
                    lines.append(chunk)
                    chunk = ch
            current = chunk
    if current:
        lines.append(current)
    return lines


def draw_masthead(draw, fonts):
    """Draw the red masthead bar. Returns the y coordinate below it."""
    masthead_font, _, _, _, _ = fonts
    bar_h = 92
    draw.rectangle([0, 0, W, bar_h], fill=MASTHEAD_BG)
    draw.text((MARGIN, 24), MASTHEAD, font=masthead_font, fill=MASTHEAD_FG)
    # right-aligned dateline
    date_w = draw.textlength(DATELINE, font=masthead_font)
    draw.text((W - MARGIN - date_w, 30), DATELINE, font=masthead_font, fill=MASTHEAD_FG)
    return bar_h


def _measure_story(draw, fonts, story):
    """Height in pixels a story block will occupy when drawn at any y."""
    _, _, headline_font, subline_font, _ = fonts
    tag_text, headline_text, subline_text = story
    tag_h = 30
    y = tag_h + 10
    y += len(wrap(draw, headline_text, headline_font, CONTENT_W)) * int(headline_font.size * 1.22)
    y += 6
    y += len(wrap(draw, subline_text, subline_font, CONTENT_W)) * int(subline_font.size * 1.28)
    return y


def draw_story(draw, fonts, story, y):
    """Draw one story block. Returns the y coordinate below the block."""
    _, tag_font, headline_font, subline_font, _ = fonts
    tag_text, headline_text, subline_text = story

    # coloured tag pill
    tag_pad_x = 14
    tag_h = 30
    tag_w = draw.textlength(tag_text, font=tag_font) + 2 * tag_pad_x
    draw.rectangle([MARGIN, y, MARGIN + tag_w, y + tag_h], fill=TAG_BG)
    draw.text((MARGIN + tag_pad_x, y + 5), tag_text, font=tag_font, fill=TAG_FG)
    y += tag_h + 10

    # headline (wrapped)
    for line in wrap(draw, headline_text, headline_font, CONTENT_W):
        draw.text((MARGIN, y), line, font=headline_font, fill=HEADLINE_FG)
        y += int(headline_font.size * 1.22)

    # subline (wrapped, dimmer)
    y += 6
    for line in wrap(draw, subline_text, subline_font, CONTENT_W):
        draw.text((MARGIN, y), line, font=subline_font, fill=SUBLINK_FG)
        y += int(subline_font.size * 1.28)
    return y


def render():
    """Compose the collage and write it to OUTPUT_PATH."""
    fonts = load_fonts()
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    y = draw_masthead(draw, fonts)
    y += 26

    # Distribute the six story blocks down the canvas so there is no dead
    # space above the pinned footer: pre-measure each block, then spread the
    # leftover vertical room evenly between them.
    separator, post_gap = 4, 18
    gap_top = y
    for story in STORIES:
        block_h = _measure_story(draw, fonts, story)
        y += block_h + separator + post_gap
    # Room between the last block's separator and the top of the pinned footer.
    footer_font = fonts[4]
    footer_h = int(footer_font.size * 1.3) * len(wrap(draw, FOOTER, footer_font, CONTENT_W))
    bottom_limit = H - MARGIN - footer_h
    leftover = bottom_limit - (y - post_gap)
    even_gap = max(post_gap, leftover // max(len(STORIES), 1)) if leftover > 0 else post_gap

    y = gap_top
    for i, story in enumerate(STORIES):
        y = draw_story(draw, fonts, story, y)
        if i < len(STORIES) - 1:
            draw.line([MARGIN, y + separator, W - MARGIN, y + separator], fill=RULE, width=1)
        y += even_gap

    # footer pinned to the bottom
    _, _, _, _, footer_font = fonts
    footer_lines = wrap(draw, FOOTER, footer_font, CONTENT_W)
    fy = H - MARGIN - int(footer_font.size * 1.3) * len(footer_lines)
    for line in footer_lines:
        draw.text((MARGIN, fy), line, font=footer_font, fill=FOOTER_FG)
        fy += int(footer_font.size * 1.3)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img.save(OUTPUT_PATH, "PNG", optimize=True)


if __name__ == "__main__":
    render()
    size = os.path.getsize(OUTPUT_PATH)
    print("wrote %s (%d bytes)" % (OUTPUT_PATH, size))
