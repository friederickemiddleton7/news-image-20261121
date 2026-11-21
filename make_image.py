#!/usr/bin/env python3
"""Build-time drawing of entry.png: a front page summing up 21 November 2026.

Everything is fixed geometry and fixed text, so repeated runs produce
byte-identical output. Run with: python3 make_image.py
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

NAVY = (11, 18, 32)
CARD = (21, 31, 51)
RULE = (42, 58, 87)
BODY = (215, 222, 234)
WHITE = (255, 255, 255)
AMBER = (242, 179, 61)
TEAL = (79, 209, 197)
MUTED = (150, 166, 188)
GREY = (148, 164, 190)

FONTS = "/usr/share/fonts/truetype/dejavu"
BOLD = os.path.join(FONTS, "DejaVuSans-Bold.ttf")
REG = os.path.join(FONTS, "DejaVuSans.ttf")
SERIF = os.path.join(FONTS, "DejaVuSerif-Bold.ttf")

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def width(d, text, fnt, tracking=0):
    if not tracking:
        return d.textlength(text, font=fnt)
    return sum(d.textlength(c, font=fnt) for c in text) + tracking * max(0, len(text) - 1)


def spaced(d, x, y, text, fnt, fill, tracking=2):
    cx = float(x)
    for i, ch in enumerate(text):
        d.text((cx, y), ch, font=fnt, fill=fill)
        cx += d.textlength(ch, font=fnt)
        if i < len(text) - 1:
            cx += tracking
    return cx


def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if not cur or d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, path, start, max_w, max_lines, floor, tracking=0):
    """Biggest size <= start that wraps into <= max_lines lines inside max_w."""
    size = start
    while size > floor:
        fnt = F(path, size)
        lines = wrap(d, text, fnt, max_w)
        if len(lines) <= max_lines and all(width(d, ln, fnt, tracking) <= max_w for ln in lines):
            return fnt, lines, size
        size -= 1
    fnt = F(path, floor)
    return fnt, wrap(d, text, fnt, max_w), floor


def one_line(d, text, path, start, max_w, floor, tracking=0):
    size = start
    while size > floor and width(d, text, F(path, size), tracking) > max_w:
        size -= 1
    return F(path, size), size


# ------------------------------------------------------------------ pictograms

def p_missile(d, x0, y0, x1, y1):
    """Tapered missile, dashed descent arc, city blocks, amber impact block."""
    a = math.radians(38)
    ux, uy = math.cos(a), -math.sin(a)
    px, py = -uy, ux

    def side(pt, k):
        return (pt[0] + px * k, pt[1] + py * k)

    tail = (x0 + 16, y0 + 92)
    blen, half = 96.0, 8.0
    neck = (tail[0] + ux * blen, tail[1] + uy * blen)
    tip = (neck[0] + ux * 26, neck[1] + uy * 26)

    d.polygon([side(tail, half), side(neck, half), side(neck, -half), side(tail, -half)],
              fill=(120, 136, 160))
    d.polygon([side(neck, half), side(neck, -half), tip], fill=(166, 182, 206))
    for s in (1, -1):
        d.polygon([side(tail, half * s), side(tail, (half + 12) * s),
                   side((tail[0] + ux * 24, tail[1] + uy * 24), half * s)],
                  fill=(120, 136, 160))

    ground = y1 - 14
    d.line([(x0 + 2, ground), (x1 - 2, ground)], fill=(96, 112, 138), width=2)
    blocks = [(x0 + 8, 34, 34), (x0 + 46, 52, 26), (x0 + 76, 26, 28),
              (x0 + 110, 44, 26), (x0 + 142, 62, 24), (x0 + 172, 30, 32),
              (x0 + 208, 48, 26), (x0 + 238, 24, 22)]
    hit_x = x0 + 142
    for bx, bh, bw in blocks:
        d.rectangle([bx, ground - bh, bx + bw, ground], fill=CARD, outline=GREY, width=2)
    d.rectangle([hit_x, ground - 62, hit_x + 24, ground], fill=AMBER)

    start, ctrl, end = tip, (x0 + 268, y0 - 6), (hit_x + 12, ground - 64)
    prev = None
    for i in range(49):
        t = i / 48
        bx = (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * ctrl[0] + t * t * end[0]
        by = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * ctrl[1] + t * t * end[1]
        if prev and i % 4 in (1, 2):
            d.line([prev, (bx, by)], fill=(196, 206, 220), width=2)
        prev = (bx, by)


def p_shield(d, x, y):
    w = 54
    d.polygon([(x + w / 2, y), (x + w - 7, y + 10), (x + w - 7, y + 28),
               (x + w / 2, y + 54), (x + 7, y + 28), (x + 7, y + 10)],
              fill=CARD, outline=GREY, width=2)
    d.line([(x + 30, y + 8), (x + 23, y + 20), (x + 31, y + 25),
            (x + 23, y + 33), (x + 29, y + 41)], fill=AMBER, width=3, joint="curve")


def p_doc(d, x, y):
    d.rectangle([x + 6, y, x + 46, y + 54], outline=GREY, width=2)
    d.polygon([(x + 34, y), (x + 34, y + 15), (x + 46, y + 15)], fill=CARD, outline=GREY, width=2)
    for i in range(3):
        d.line([(x + 13, y + 17 + i * 7), (x + 39 - i * 7, y + 17 + i * 7)], fill=GREY, width=2)
    d.line([(x + 15, y + 41), (x + 23, y + 49), (x + 40, y + 31)], fill=AMBER, width=4, joint="curve")


def p_chart(d, x, y):
    s = 50
    d.line([(x + 4, y + 2), (x + 4, y + s), (x + s + 2, y + s)], fill=GREY, width=2)
    pts = [(x + 11, y + 17), (x + 20, y + 9), (x + 28, y + 18), (x + 36, y + 12), (x + 44, y + 33)]
    d.line(pts, fill=TEAL, width=3, joint="curve")
    d.polygon([(x + 44, y + 44), (x + 37, y + 32), (x + 50, y + 29)], fill=AMBER)


def p_flag(d, x, y):
    d.line([(x + 16, y + 2), (x + 16, y + 50)], fill=GREY, width=3)
    d.rectangle([x + 16, y + 5, x + 46, y + 30], fill=CARD, outline=GREY, width=2)
    pts = []
    for i in range(10):
        r = 8.5 if i % 2 == 0 else 3.4
        ang = math.radians(-90 + i * 36)
        pts.append((x + 31 + r * math.cos(ang), y + 18 + r * math.sin(ang)))
    d.polygon(pts, fill=TEAL)
    d.arc([x - 2, y + 32, x + 24, y + 52], 200, 340, fill=AMBER, width=2)
    d.polygon([(x + 22, y + 40), (x + 15, y + 49), (x + 26, y + 50)], fill=AMBER)
    d.arc([x + 34, y + 32, x + 60, y + 52], 200, 340, fill=AMBER, width=2)
    d.polygon([(x + 38, y + 40), (x + 45, y + 49), (x + 34, y + 50)], fill=AMBER)


# ------------------------------------------------------------------ page parts

def header(d):
    spaced(d, 20, 28, "WORLD NEWS", F(BOLD, 26), AMBER, 7)

    fnt, size = one_line(d, "21 NOVEMBER 2026", BOLD, 78, 984, 60)
    d.text((18, 58), "21 NOVEMBER 2026", font=fnt, fill=WHITE)
    d.rectangle([20, 146, 1004, 149], fill=AMBER)
    return size


def lead(d):
    d.rounded_rectangle([20, 168, 1004, 470], radius=16, fill=CARD)

    spaced(d, 48, 194, "EUROPE  \u00b7  POLAND", F(BOLD, 23), AMBER, 3)

    f_head, lines, size = fit(
        d, "RUSSIAN MISSILES LAND IN POLAND \u2014 NATO CALLS IT A VIOLATION",
        BOLD, 50, 628, 3, 30)
    y = 230
    lh = int(round(size * 1.14))
    for ln in lines:
        d.text((48, y), ln, font=f_head, fill=WHITE)
        y += lh

    f_body, blines, bsize = fit(
        d, "A Kh-101 and a drone strike southeastern Poland during a mass overnight attack on Ukraine.",
        REG, 23, 628, 2, 20)
    by = y + 8
    for ln in blines:
        d.text((48, by), ln, font=f_body, fill=BODY)
        by += int(round(bsize * 1.28))

    p_missile(d, 716, 186, 986, 444)
    return size, bsize, len(lines), len(blines)


def tile(d, box, chip, headline, body, picto):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=14, fill=CARD)
    spaced(d, x0 + 20, y0 + 15, chip, F(BOLD, 19), TEAL, 2)
    picto(d, x1 - 74, y0 + 12)

    inner = (x1 - x0) - 106
    f_h, hlines, hsize = fit(d, headline, BOLD, 32, inner, 2, 24)
    y = y0 + 72
    lh = int(round(hsize * 1.14))
    for ln in hlines:
        d.text((x0 + 20, y), ln, font=f_h, fill=WHITE)
        y += lh

    f_b, blines, bsize = fit(d, body, REG, 21, inner, 2, 19)
    bl = int(round(bsize * 1.34))
    by = y1 - 16 - bl * len(blines)
    by = max(by, y + 4)
    for ln in blines:
        d.text((x0 + 20, by), ln, font=f_b, fill=BODY)
        by += bl


def footer(d):
    y = 950
    d.text((20, y), "ALSO TODAY", font=F(BOLD, 21), fill=AMBER)
    d.text((178, y), "US Senate rebuffs Iran war-powers curb \u00b7 Iraq retakes Jurf al-Sakhar",
           font=F(REG, 21), fill=MUTED)
    d.text((178, y + 30), "Visa/Mastercard data leak \u00b7 Cyclone Xavier record",
           font=F(REG, 21), fill=MUTED)


def build(path):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    date_px = header(d)
    lead_px, body_px, nl, nbl = lead(d)

    cw, ch = 482, 222
    xa, xb = 20, 522
    ya, yb = 486, 726

    tile(d, (xa, ya, xa + cw, ya + ch), "EUROPE  \u00b7  UKRAINE",
         "NIGHT STRIKES KILL 8 IN UKRAINE",
         "Kyiv and Lviv hit; the EU adds EUR 1bn more aid.", p_shield)
    tile(d, (xb, ya, xb + cw, ya + ch), "DIPLOMACY  \u00b7  WASHINGTON",
         "TRUMP: DEAL FIRST, THEN GUARANTEES",
         "US aims for a Ukraine peace deal by January; Europe demands a role.", p_doc)
    tile(d, (xa, yb, xa + cw, yb + ch), "MARKETS  \u00b7  ASIA-PACIFIC",
         "AI RALLY FIZZLES, ASIA SELL-OFF",
         "Anthropic's record $1.8tn debut, then stocks' worst week since 2020.", p_chart)
    tile(d, (xb, yb, xb + cw, yb + ch), "SOUTH ASIA  \u00b7  ROHINGYA",
         "BANGLADESH DEMANDS ROHINGYA RETURN",
         "After the ICJ genocide ruling, Dhaka calls on Myanmar to compensate.", p_flag)

    footer(d)
    img.save(path, "PNG", optimize=True)
    print(f"date {date_px}px | lead {lead_px}px x{nl} lines | lead body {body_px}px x{nbl}")


if __name__ == "__main__":
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    build(dest)
    print("wrote", dest, os.path.getsize(dest), "bytes")
    sys.exit(0)
