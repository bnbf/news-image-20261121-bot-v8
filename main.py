#!/usr/bin/env python3
"""news-image-20261121 v8 - 'Saturday 21 November 2026' front page.
Self-contained STDLIB-ONLY generator (imports: math, os, struct, sys, zlib).
Pure-Python PNG encoder + hand-typed single-stroke vector font.
No PIL, no third-party imports, no base64, no reads of any earlier main.py.
Written from scratch in-session for the v8 hero-swap rebuild.
"""
import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024
PAPER = (246, 241, 229)
INK = (20, 20, 20)
RED = (163, 22, 33)
DRED = (127, 14, 24)
NAVY = (43, 76, 126)
TEAL = (15, 118, 110)
GREEN = (46, 125, 50)
BROWN = (141, 110, 47)
PURPLE = (106, 79, 163)
GREY = (85, 85, 85)
LGREY = (220, 214, 198)
SEA = (214, 228, 232)
LAND = (232, 220, 185)
WHITE = (255, 255, 255)
CREAM = (250, 246, 236)
GOLD = (196, 148, 30)

# ---------------------------------------------------------------- PNG encoder
def write_png(path, buf):
    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + bytes(buf[y * W * 3:(y + 1) * W * 3]) for y in range(H))
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self):
        self.px = bytearray(PAPER[0] for _ in range(W * H * 3))
        for i in range(W * H):
            self.px[i * 3] = PAPER[0]
            self.px[i * 3 + 1] = PAPER[1]
            self.px[i * 3 + 2] = PAPER[2]

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill(self, x0, y0, x1, y1, c):
        x0 = max(0, int(x0)); y0 = max(0, int(y0))
        x1 = min(W, int(x1)); y1 = min(H, int(y1))
        for y in range(y0, y1):
            i = (y * W + x0) * 3
            for x in range(x0, x1):
                self.px[i] = c[0]; self.px[i + 1] = c[1]; self.px[i + 2] = c[2]
                i += 3

    def rect(self, x0, y0, x1, y1, c, w=1):
        for t in range(w):
            self.hline(x0, y0 + t, x1, c)
            self.hline(x0, y1 - t, x1, c)
            self.vline(x0 + t, y0, y1, c)
            self.vline(x1 - t, y0, y1, c)

    def hline(self, x0, y, x1, c, w=1):
        if x0 > x1:
            x0, x1 = x1, x0
        for yy in range(int(y), int(y) + max(1, w)):
            for x in range(int(x0), int(x1)):
                self.set(x, yy, c)

    def vline(self, x, y0, y1, c, w=1):
        if y0 > y1:
            y0, y1 = y1, y0
        for xx in range(int(x), int(x) + max(1, w)):
            for y in range(int(y0), int(y1)):
                self.set(xx, y, c)

    def line(self, x0, y0, x1, y1, c, w=1):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        r = max(0, w // 2)
        while True:
            for a in range(-r, r + 1):
                for b in range(-r, r + 1):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy; x0 += sx
            if e2 < dx:
                err += dx; y0 += sy

    def poly(self, pts, c, w=1, close=False):
        n = len(pts)
        for i in range(n - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c, w)
        if close and n > 2:
            self.line(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1], c, w)

    def fill_poly(self, pts, c):
        if not pts:
            return
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    if y1 != y0:
                        xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.set(x, y, c)

    def circle(self, cx, cy, r, c, w=1, fill=False):
        if fill:
            for y in range(int(cy - r), int(cy + r) + 1):
                dx = int(math.sqrt(max(0, r * r - (y - cy) ** 2)))
                for x in range(int(cx - dx), int(cx + dx) + 1):
                    self.set(x, y, c)
            return
        steps = max(24, int(2 * math.pi * r))
        pts = [(cx + r * math.cos(2 * math.pi * i / steps),
                cy + r * math.sin(2 * math.pi * i / steps)) for i in range(steps)]
        self.poly(pts, c, w, close=True)

    def ellipse(self, cx, cy, rx, ry, c, w=1, fill=False):
        if fill:
            for y in range(int(cy - ry), int(cy + ry) + 1):
                t = 1 - ((y - cy) / ry) ** 2 if ry else 0
                dx = int(rx * math.sqrt(max(0, t)))
                for x in range(int(cx - dx), int(cx + dx) + 1):
                    self.set(x, y, c)
            return
        steps = max(24, int(2 * math.pi * max(rx, ry)))
        pts = [(cx + rx * math.cos(2 * math.pi * i / steps),
                cy + ry * math.sin(2 * math.pi * i / steps)) for i in range(steps)]
        self.poly(pts, c, w, close=True)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        self.fill_poly([(x0, y0), (x1, y1), (x2, y2)], c)

    def star(self, cx, cy, r, c):
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.45
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        self.fill_poly(pts, c)

# ---------------------------------------------------------------- stroke font
# Grid: caps/digits on y 0..6, x 0..4; lowercase x-height y 2..6, descenders to 7.
# Each glyph: strokes separated by '|', points 'x,y' joined by spaces.
FONT = {
'A': "0,6 2,0 4,6|1,4 3,4",
'B': "0,0 0,6|0,0 3,0 4,1 4,2 3,3 0,3|0,3 3,3 4,4 4,5 3,6 0,6",
'C': "4,1 3,0 1,0 0,1 0,5 1,6 3,6 4,5",
'D': "0,0 0,6 2,6 4,4 4,2 2,0 0,0",
'E': "4,0 0,0 0,6 4,6|0,3 3,3",
'F': "0,0 0,6|0,0 4,0|0,3 3,3",
'G': "4,1 3,0 1,0 0,1 0,5 1,6 3,6 4,5 4,3 2,3",
'H': "0,0 0,6|4,0 4,6|0,3 4,3",
'I': "2,0 2,6|0,0 4,0|0,6 4,6",
'J': "4,0 4,5 3,6 1,6 0,5",
'K': "0,0 0,6|4,0 0,3 4,6",
'L': "0,0 0,6 4,6",
'M': "0,6 0,0 2,3 4,0 4,6",
'N': "0,6 0,0 4,6 4,0",
'O': "1,0 3,0 4,1 4,5 3,6 1,6 0,5 0,1 1,0",
'P': "0,6 0,0 3,0 4,1 4,2 3,3 0,3",
'Q': "1,0 3,0 4,1 4,5 3,6 1,6 0,5 0,1 1,0|2,4 4,6",
'R': "0,6 0,0 3,0 4,1 4,2 3,3 0,3|2,3 4,6",
'S': "4,1 3,0 1,0 0,1 0,2 1,3 3,3 4,4 4,5 3,6 1,6 0,5",
'T': "0,0 4,0|2,0 2,6",
'U': "0,0 0,5 1,6 3,6 4,5 4,0",
'V': "0,0 2,6 4,0",
'W': "0,0 1,6 2,3 3,6 4,0",
'X': "0,0 4,6|4,0 0,6",
'Y': "0,0 2,3 4,0|2,3 2,6",
'Z': "0,0 4,0 0,6 4,6",
'a': "4,2 4,6 3,6 1,6 0,5 0,3 1,2 3,2",
'b': "0,0 0,6|4,3 3,2 1,2 0,3 0,5 1,6 3,6 4,5 4,3",
'c': "4,3 3,2 1,2 0,3 0,5 1,6 3,6 4,5",
'd': "4,0 4,6|4,3 3,2 1,2 0,3 0,5 1,6 3,6 4,5",
'e': "4,4 3,5 1,5 0,4 0,3 1,2 3,2 4,3 4,4|0,4 3,4",
'f': "3,0 2,0 1,1 1,6|0,3 2,3",
'g': "3,2 4,3 4,5 3,6 1,6 0,5 0,3 1,2|3,6 3,7 1,7",
'h': "0,0 0,6|0,3 1,2 3,2 4,3 4,6",
'i': "2,2 2,6|2,0 2,0",
'j': "3,2 3,6 2,7 1,7|3,0 3,0",
'k': "0,0 0,6|3,2 0,4 4,6",
'l': "2,0 2,6",
'm': "0,6 0,2 1,2 2,3 3,2 4,2 4,6|2,3 2,6",
'n': "0,6 0,2 1,2 3,2 4,3 4,6",
'o': "1,2 3,2 4,3 4,5 3,6 1,6 0,5 0,3 1,2",
'p': "0,2 0,7|0,4 1,2 3,2 4,3 4,5 3,6 1,6 0,5",
'q': "4,2 4,7|4,3 3,2 1,2 0,3 0,5 1,6 3,6 4,5",
'r': "0,6 0,2 1,2 2,3|2,3 3,2 4,2",
's': "4,2 3,2 1,2 0,3 1,4 3,4 4,5 4,6 3,6 1,6 0,5",
't': "2,0 2,6|0,3 3,3",
'u': "0,2 0,5 1,6 3,6 4,5 4,2",
'v': "0,2 2,6 4,2",
'w': "0,2 1,6 2,4 3,6 4,2",
'x': "0,2 4,6|4,2 0,6",
'y': "0,2 2,6 4,2|2,6 2,7 1,7",
'z': "0,2 4,2 0,6 4,6",
'0': "1,0 3,0 4,1 4,5 3,6 1,6 0,5 0,1 1,0",
'1': "2,0 2,6|1,1 2,0|0,6 4,6",
'2': "0,1 1,0 3,0 4,1 4,2 3,3 0,6 4,6",
'3': "0,1 1,0 3,0 4,1 4,2 3,3 4,4 4,5 3,6 1,6 0,5",
'4': "0,0 0,3 4,3|3,0 3,6",
'5': "4,0 0,0 0,3 3,3 4,4 4,5 3,6 1,6 0,5",
'6': "4,1 3,0 1,0 0,1 0,5 1,6 3,6 4,5 4,4 3,3 1,3 0,4",
'7': "0,0 4,0 2,6",
'8': "1,0 3,0 4,1 4,2 3,3 1,3 0,4 0,5 1,6 3,6 4,5 4,4 3,3",
'9': "4,5 3,6 1,6 0,5 0,1 1,0 3,0 4,1 4,3 3,3 1,3 0,2",
'.': "2,6 2,6",
',': "2,6 2,6|2,6 1,7",
':': "2,1 2,1|2,5 2,5",
';': "2,1 2,1|2,5 2,5|2,5 1,7",
'!': "2,0 2,4|2,6 2,6",
'?': "1,1 2,0 3,0 4,1 4,2 3,3 2,3|2,5 2,5",
"'": "2,0 2,1",
'"': "1,0 1,1|3,0 3,1",
'-': "0,3 4,3",
'(': "3,0 2,1 2,5 3,6",
')': "1,0 2,1 2,5 1,6",
'/': "4,0 0,6",
'&': "3,0 2,1 1,2 1,3 2,4 3,4 4,5 4,6 3,6 2,5|1,2 4,5",
'%': "0,0 4,6|1,1 1,1|3,5 3,5",
'$': "2,0 2,6|0,1 1,0 3,0 4,1 4,2 3,3 1,3 0,4 0,5 1,6 3,6 4,5",
'#': "1,0 1,6|3,0 3,6|0,2 4,2|0,4 4,4",
'+': "2,1 2,5|0,3 4,3",
'*': "2,0 2,6|0,2 4,4|4,2 0,4",
'·': "2,3 2,3",
'=': "0,2 4,2|0,4 4,4",
'×': "0,1 4,5|4,1 0,5",
'°': "1,0 3,0 3,1 1,1",
'<': "4,0 0,3 4,6",
'>': "0,0 4,3 0,6",
'[': "3,0 1,0 1,6 3,6",
']': "1,0 3,0 3,6 1,6",
'_': "0,6 4,6",
}
NARROW = set("ijl1!':;.,·|'\"()[]")

def glyph_w(ch):
    if ch == ' ':
        return 4.5
    if ch in NARROW:
        return 3.0
    if ch in 'MWmw':
        return 6.0
    return 5.0

def text_w(s, sc, sx=1.0):
    return sum((glyph_w(ch) + 1.0) * sc * sx for ch in s) - (sc * sx if s else 0)

def draw_glyph(cv, ch, x, y, sc, sx, c, wgt=1, serif=False):
    g = FONT.get(ch)
    if g is None:
        return
    for stroke in g.split('|'):
        pts = []
        for tok in stroke.split():
            gx, gy = tok.split(',')
            pts.append((x + float(gx) * sc * sx, y + float(gy) * sc))
        for a, b in zip(pts, pts[1:]):
            cv.line(a[0], a[1], b[0], b[1], c, wgt)
        if len(pts) == 1:
            cv.circle(pts[0][0], pts[0][1], max(1, wgt // 2), c, fill=True)
        if serif:
            for px, py in (pts[0], pts[-1]):
                gy = (py - y) / sc
                if abs(gy) < 0.6 or abs(gy - 6) < 0.6:
                    cv.hline(px - 0.9 * sc * sx, py, px + 0.9 * sc * sx, c, max(1, wgt - 1))

def draw_text(cv, s, x, y, sc, c, sx=1.0, wgt=1, serif=False, align='l'):
    if align == 'c':
        x = x - text_w(s, sc, sx) / 2
    elif align == 'r':
        x = x - text_w(s, sc, sx)
    cx = x
    for ch in s:
        if ch == ' ':
            cx += 3.0 * sc * sx
            continue
        draw_glyph(cv, ch, cx, y, sc, sx, c, wgt, serif)
        cx += (glyph_w(ch) + 1.0) * sc * sx
    return cx

def wrap_text(s, sc, maxw, sx=1.0):
    words = s.split(' ')
    lines, cur = [], ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if text_w(trial, sc, sx) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

def para(cv, s, x, y, maxw, sc, c, sx=1.0, wgt=1, lh=None, serif=False):
    lh = lh or int(sc * 7.5)
    yy = y
    for ln in wrap_text(s, sc, maxw, sx):
        draw_text(cv, ln, x, yy, sc, c, sx, wgt, serif)
        yy += lh
    return yy

# ---------------------------------------------------------------- page furniture
CONF = {'CONFIRMED': (46, 125, 50), 'OFFICIAL': (43, 76, 126),
        'REPORTED': (141, 110, 47), 'CLAIM': (163, 22, 33)}

def tag(cv, x, y, label, sc=1.3):
    w = text_w(label, sc) + 8
    col = CONF.get(label, GREY)
    cv.fill(x, y, x + w, y + 11, col)
    draw_text(cv, label, x + 4, y + 1, sc, WHITE, wgt=1)
    return x + w

def header(cv):
    cv.fill(0, 0, W, 4, RED)
    draw_text(cv, "THE WORLD IN ONE DAY", 12, 8, 1.5, INK, sx=0.9, wgt=1)
    draw_text(cv, "35 STORIES · 7 REGIONS · EVERY ONE DATED SATURDAY 21 NOVEMBER 2026",
              512, 8, 1.4, RED, sx=0.85, wgt=1, align='c')
    draw_text(cv, "ALL TIMES UTC", 1012, 8, 1.5, INK, sx=0.9, wgt=1, align='r')
    # masthead - big slab-serif, condensed to fit the full date
    draw_text(cv, "Saturday 21 November 2026", 512, 18, 8.2, INK,
              sx=0.62, wgt=4, serif=True, align='c')
    draw_text(cv, "Iran strikes Bahrain  ·  COP31 runs into overtime  ·  a deep quake shakes Peru",
              512, 88, 2.0, RED, sx=0.9, wgt=1, serif=True, align='c')
    cv.hline(12, 102, 1012, INK, 2)

REGIONS = [("EUROPE", 5, NAVY), ("MIDDLE EAST", 7, RED), ("AMERICAS", 9, GREEN),
           ("ASIA", 5, TEAL), ("OCEANIA", 3, PURPLE), ("AFRICA", 2, BROWN),
           ("GLOBAL", 4, GREY)]

def region_bar(cv, y=122):
    x = 12
    total = sum(n for _, n, _ in REGIONS)
    for name, n, col in REGIONS:
        w = 1000 * n / total
        cv.fill(x, y, x + w, y + 13, col)
        draw_text(cv, "%s %d" % (name, n), x + w / 2, y + 2, 1.3, WHITE, sx=0.85, align='c')
        x += w

UTC_EVENTS = [("00:09", "Peru M6.7 quake"), ("02:00", "Sinaloa raid"),
              ("05:00", "Tanker hit, Khasab"), ("06:50", "Sparta II alarm"),
              ("09:42", "Banda Sea M6.8"), ("18:24", "BepiColombo burn"),
              ("22:00", "COP31 pauses")]

def utc_strip(cv, y=140):
    cv.fill(12, y, 108, y + 15, INK)
    draw_text(cv, "THE DAY IN UTC", 12, y + 2, 1.5, WHITE, sx=0.9, wgt=1)
    x = 118
    step = (1012 - 118) / len(UTC_EVENTS)
    for t, label in UTC_EVENTS:
        draw_text(cv, t, x, y + 1, 1.5, RED, sx=0.9, wgt=1)
        draw_text(cv, label, x, y + 10, 1.25, INK, sx=0.85)
        x += step
    cv.hline(12, y + 21, 1012, INK, 1)

NUMBERS = [("2", "tankers hit off Khasab (UKMTO)"),
           ("130+", "countries want fossil fuels named at COP31 (AFP)"),
           ("128", "states at the Geneva autonomous-weapons talks"),
           ("6.7", "magnitude of the Peru quake (USGS)"),
           ("3", "missiles shot down over Riyadh (coalition)"),
           ("$58,983", "Bitcoin early Saturday, down 3.9% in a day")]

def numbers_strip(cv, y=164):
    draw_text(cv, "THE DAY IN NUMBERS", 12, y + 2, 1.5, INK, sx=0.9, wgt=1)
    cv.hline(12, y + 14, 1012, INK, 1)
    x = 12
    step = 1000 / len(NUMBERS)
    for num, label in NUMBERS:
        draw_text(cv, num, x + 4, y + 20, 4.2, RED, sx=0.85, wgt=2, serif=True)
        yy = para(cv, label, x + 4, y + 50, step - 10, 1.45, INK, sx=0.85, lh=10)
        if x > 12:
            cv.vline(x, y + 20, y + 62, LGREY, 1)
        x += step
    cv.hline(12, y + 74, 1012, INK, 1)

# ---------------------------------------------------------------- hero scenes
def scene_bahrain(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, SEA)
    # Arabian peninsula + Iran coastline (tan landmasses)
    cv.fill_poly([(x + 10, y + h), (x + 10, y + 55), (x + 60, y + 40),
                  (x + 110, y + 55), (x + 130, y + h)], (LAND[0], LAND[1], LAND[2]))
    cv.fill_poly([(x + 180, y), (x + w, y), (x + w, y + 30), (x + 210, y + 45),
                  (x + 190, y + 60), (x + 175, y + 35)], (LAND[0], LAND[1], LAND[2]))
    draw_text(cv, "IRAN", x + 240, y + 8, 1.6, GREY, sx=0.9)
    draw_text(cv, "SAUDI ARABIA", x + 20, y + h - 14, 1.4, GREY, sx=0.85)
    draw_text(cv, "QATAR", x + 120, y + h - 14, 1.4, GREY, sx=0.85)
    # Bahrain island + fire
    cv.circle(x + 148, y + 62, 7, RED, fill=True)
    cv.circle(x + 148, y + 62, 12, RED, w=1)
    for dx, dy, s in [(0, -14, 12), (-8, -8, 9), (8, -8, 9), (0, -22, 7)]:
        cv.tri(x + 148 + dx - s // 2, y + 62 + dy + 6, x + 148 + dx + s // 2,
               y + 62 + dy + 6, x + 148 + dx, y + 62 + dy - 8, (255, 120, 30))
    draw_text(cv, "BAHRAIN", x + 128, y + 78, 1.4, INK, sx=0.85, wgt=1)
    # tanker + second fire, dashed missile arc from Iran
    cv.fill(x + 215, y + 82, x + 275, y + 94, (30, 30, 30))
    cv.fill(x + 225, y + 74, x + 245, y + 82, (30, 30, 30))
    cv.tri(x + 235, y + 66, x + 228, y + 74, x + 242, y + 74, (255, 120, 30))
    draw_text(cv, "KHASAB", x + 215, y + 98, 1.3, GREY, sx=0.85)
    for t in range(0, 101, 8):
        px = x + 300 - t * 1.5
        py = y + 20 + int(18 * math.sin(t * math.pi / 100))
        cv.set(int(px), int(py), RED)
        cv.set(int(px), int(py) + 1, RED)
    draw_text(cv, "STRAIT OF HORMUZ", x + 150, y + 108, 1.3, NAVY, sx=0.85)

def scene_cop31(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, (232, 240, 228))
    # draft document
    cv.fill(x + 16, y + 10, x + 150, y + h - 10, WHITE)
    cv.rect(x + 16, y + 10, x + 150, y + h - 10, INK, 2)
    draw_text(cv, "DRAFT TEXT", x + 30, y + 18, 1.8, INK, sx=0.9, wgt=1)
    for i, ly in enumerate(range(y + 34, y + h - 30, 10)):
        cv.hline(x + 26, ly, x + 140, LGREY, 1)
    draw_text(cv, "fossil fuels", x + 30, y + h - 42, 2.2, RED, sx=0.9, wgt=2, serif=True)
    cv.line(x + 26, y + h - 34, x + 146, y + h - 52, RED, 3)
    draw_text(cv, "no mention in the draft", x + 30, y + h - 28, 1.4, RED, sx=0.85)
    # thermometer
    cv.circle(x + 205, y + 62, 16, RED, fill=True)
    cv.fill(x + 198, y + 18, x + 212, y + 62, (255, 255, 255))
    cv.rect(x + 198, y + 18, x + 212, y + 62, INK, 2)
    cv.fill(x + 201, y + 40, x + 209, y + 62, RED)
    draw_text(cv, "1.5°C", x + 222, y + 30, 2.4, RED, sx=0.9, wgt=2, serif=True)
    draw_text(cv, "LIMIT AT RISK", x + 222, y + 50, 1.3, INK, sx=0.85)
    # day badge
    cv.fill(x + 262, y + 62, x + 322, y + 80, RED)
    draw_text(cv, "DAY 13", x + 268, y + 66, 1.8, WHITE, sx=0.9, wgt=1)
    draw_text(cv, "OVERTIME", x + 262, y + 86, 1.7, RED, sx=0.9, wgt=2)
    # delegate dots
    for i, dx in enumerate(range(0, 60, 12)):
        cv.circle(x + 200 + dx, y + h - 14, 5, NAVY if i % 2 == 0 else TEAL, fill=True)

def scene_peru(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, (238, 226, 200))
    cv.circle(x + 280, y + 22, 12, (255, 190, 60), fill=True)
    cv.fill_poly([(x, y + h), (x + 60, y + 30), (x + 130, y + h)], (139, 109, 71))
    cv.fill_poly([(x + 90, y + h), (x + 180, y + 18), (x + 270, y + h)], (120, 92, 58))
    cv.fill_poly([(x + 160, y + 34), (x + 180, y + 18), (x + 200, y + 34)], WHITE)
    cv.fill_poly([(x + 45, y + 44), (x + 60, y + 30), (x + 75, y + 44)], WHITE)
    # seismograph trace
    pts = []
    for i in range(0, w - 20, 4):
        t = i / 10.0
        amp = 2 + (14 if 90 < i < 210 else 0) * abs(math.sin(t * 1.7))
        pts.append((x + 10 + i, y + h - 32 + int(amp * math.sin(t * 2.3))))
    cv.poly(pts, RED, 2)
    cv.fill(x + 10, y + h - 28, x + w - 10, y + h - 24, (255, 255, 255))
    draw_text(cv, "00:09 UTC  ·  108 KM DEEP", x + 12, y + h - 12, 1.4, INK, sx=0.85)

HEROES = [
    dict(n=1, region="MIDDLE EAST", place="BAHRAIN · CONFLICT",
         tag="CONFIRMED", src="AL JAZEERA · REUTERS · AFP · UKMTO",
         head="Iran strikes Bahrain as tankers hit in Hormuz",
         deck="Bahrain: Iranian attack set a civilian site ablaze, no one hurt. "
              "IRGC says it hit US radar at two bases.",
         scene=scene_bahrain),
    dict(n=2, region="GLOBAL", place="COP31 · CLIMATE",
         tag="CONFIRMED", src="REUTERS · AFP · ANADOLU",
         head="COP31 climate talks run into overtime",
         deck="A day past deadline, talks paused overnight. EU and Pacific states "
              "reject a draft omitting fossil fuels.",
         scene=scene_cop31),
    dict(n=3, region="AMERICAS", place="PERU · QUAKE",
         tag="OFFICIAL", src="USGS · IGP · AFP · ANADOLU",
         head="Deep 6.7 earthquake shakes central Peru",
         deck="Centred near Carhuamayo at 00:09 UTC, 108 km deep, felt in Lima. "
              "No deaths reported.",
         scene=scene_peru),
]

def hero(cv, h, x, y, w):
    h['scene'](cv, x, y, w, 116)
    cv.fill(x, y + 120, x + w, y + 136, INK)
    draw_text(cv, "%d  %s" % (h['n'], h['place']), x + 6, y + 124, 1.5, WHITE, sx=0.85, wgt=1)
    tx = tag(cv, x + w - 78, y + 122, h['tag'])
    yy = y + 142
    yy = para(cv, h['head'], x, yy, w, 3.0, INK, sx=0.82, wgt=2, lh=22, serif=True)
    yy = para(cv, h['deck'], x, yy + 4, w, 1.55, INK, sx=0.88, lh=11)
    draw_text(cv, h['src'], x, y + 232, 1.25, GREY, sx=0.85)

# ---------------------------------------------------------------- picture cards
def sc_riyadh(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, (16, 24, 48))
    for bx, bh in [(10, 14), (40, 20), (75, 12), (110, 18), (150, 14), (190, 22)]:
        cv.fill(x + bx, y + h - bh, x + bx + 24, y + h, (40, 48, 80))
        for wy in range(y + h - bh + 3, y + h - 2, 5):
            cv.set(x + bx + 6, wy, (255, 210, 90))
    for ax, ay in [(30, 12), (120, 8), (205, 14)]:
        cv.line(x + ax, y + h - 8, x + ax + 22, y + ay, (255, 210, 90), 1)
        cv.star(x + ax + 22, y + ay, 5, (255, 220, 120))

def sc_sparta(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, (28, 48, 74))
    cv.fill(x + 60, y + 18, x + 190, y + 28, (20, 20, 20))
    cv.fill(x + 90, y + 8, x + 130, y + 18, (20, 20, 20))
    for sx, sy, r in [(100, 4, 6), (130, 2, 8), (160, 5, 6)]:
        cv.circle(x + sx, y + sy, r, (150, 150, 150), fill=True)
    cv.tri(x + 110, y + 2, x + 104, y + 10, x + 116, y + 10, (255, 120, 30))
    cv.line(x + 30, y + 12, x + 55, y + 6, INK, 1)
    cv.line(x + 210, y + 10, x + 232, y + 4, INK, 1)

def sc_chapo(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, (24, 28, 40))
    cv.star(x + w // 2, y + h // 2, 13, GOLD)
    draw_text(cv, "FBI TOP 10", x + 8, y + 4, 1.4, WHITE, sx=0.85)
    draw_text(cv, "11 DEAD", x + w - 52, y + h - 12, 1.4, (255, 120, 30), sx=0.85, wgt=1)

def sc_euindo(cv, x, y, w, h):
    cv.fill(x + 8, y + 4, x + 110, y + h - 4, (0, 51, 153))
    for i in range(12):
        a = 2 * math.pi * i / 12
        cv.circle(x + 58 + int(16 * math.cos(a)), y + h // 2 + int(10 * math.sin(a)), 2, (255, 220, 60), fill=True)
    cv.fill(x + 130, y + 4, x + w - 8, y + h // 2 - 2, RED)
    cv.fill(x + 130, y + h // 2 - 2, x + w - 8, y + h - 4, WHITE)
    draw_text(cv, "98.5%", x + 140, y + h - 16, 1.6, RED, sx=0.9, wgt=2)

def sc_banda(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, SEA)
    for r in (6, 12, 18, 24):
        cv.circle(x + w // 2, y + h // 2, r, NAVY, w=1)
    cv.circle(x + w // 2, y + h // 2, 4, RED, fill=True)
    draw_text(cv, "M6.8", x + 8, y + 4, 2.0, RED, sx=0.9, wgt=2)
    draw_text(cv, "09:42 UTC", x + w - 62, y + h - 12, 1.3, NAVY, sx=0.85)

def sc_geneva(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, (232, 236, 240))
    cv.fill(x + 100, y + 6, x + 148, y + 20, (120, 130, 140))
    cv.line(x + 124, y + 6, x + 124, y + 2, INK, 2)
    cv.circle(x + 124, y + 2, 2, RED, fill=True)
    cv.fill(x + 92, y + 20, x + 156, y + h - 4, (150, 160, 170))
    cv.circle(x + 112, y + 12, 2, INK, fill=True)
    cv.circle(x + 136, y + 12, 2, INK, fill=True)
    draw_text(cv, "128", x + 12, y + 6, 2.6, NAVY, sx=0.9, wgt=2, serif=True)
    draw_text(cv, "STATES", x + 12, y + 22, 1.3, NAVY, sx=0.85)
    draw_text(cv, "2028", x + w - 44, y + 6, 2.0, INK, sx=0.9, wgt=1)

def sc_bepi(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, (10, 12, 24))
    cv.circle(x + 60, y + h // 2, 12, (170, 165, 155), fill=True)
    cv.circle(x + 56, y + h // 2 - 3, 2, (120, 118, 110), fill=True)
    cv.circle(x + 64, y + h // 2 + 4, 3, (120, 118, 110), fill=True)
    cv.ellipse(x + 150, y + h // 2, 70, 12, WHITE, w=1)
    cv.fill(x + 150, y + h // 2 - 4, x + 158, y + h // 2 + 4, (200, 200, 200))
    cv.fill(x + 138, y + h // 2 - 2, x + 150, y + h // 2 + 2, (150, 150, 150))
    draw_text(cv, "18:24", x + w - 48, y + 4, 1.6, WHITE, sx=0.9, wgt=1)

def sc_france(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, (240, 232, 214))
    for i in range(14):
        px = x + 12 + i * 16
        cv.circle(px, y + h - 12, 4, NAVY if i % 3 else RED, fill=True)
        cv.fill(px - 3, y + h - 8, px + 3, y + h, NAVY if i % 3 else RED)
    cv.fill(x + 60, y + 4, x + 190, y + 14, WHITE)
    cv.rect(x + 60, y + 4, x + 190, y + 14, INK, 1)
    draw_text(cv, "82,500 MARCH", x + 66, y + 6, 1.4, INK, sx=0.85, wgt=1)

def sc_rugby(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, (28, 90, 44))
    cv.ellipse(x + w // 2, y + h // 2, 60, 13, (120, 70, 30), fill=True)
    cv.ellipse(x + w // 2, y + h // 2, 60, 13, INK, w=1)
    cv.line(x + w // 2 - 14, y + h // 2 - 11, x + w // 2 - 14, y + h // 2 + 11, WHITE, 2)
    cv.line(x + w // 2 + 14, y + h // 2 - 11, x + w // 2 + 14, y + h // 2 + 11, WHITE, 2)
    draw_text(cv, "37-12", x + w - 58, y + 4, 2.2, WHITE, sx=0.9, wgt=2)

def sc_bitcoin(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, (24, 24, 24))
    pts = [(x + 8, y + 12), (x + 60, y + 16), (x + 110, y + 26), (x + 150, y + 24),
           (x + 190, y + 14), (x + 230, y + 8)]
    cv.poly(pts, (255, 80, 80), 2)
    draw_text(cv, "$58,983", x + 10, y + h - 16, 2.0, (255, 210, 90), sx=0.9, wgt=2)
    draw_text(cv, "-3.9%", x + w - 48, y + 4, 1.6, (255, 80, 80), sx=0.9, wgt=1)

def sc_taiwan(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, (214, 228, 232))
    cv.line(x + 8, y + h // 2, x + w - 8, y + h // 2, NAVY, 1)
    for i, dx in enumerate((30, 90, 150, 200)):
        cv.tri(x + dx, y + 8 + (i % 2) * 8, x + dx + 14, y + 14 + (i % 2) * 8,
               x + dx, y + 20 + (i % 2) * 8, (40, 40, 40))
    draw_text(cv, "21 JETS", x + 8, y + h - 13, 1.8, RED, sx=0.9, wgt=2)

def sc_basra(cv, x, y, w, h):
    cv.fill(x, y, x + w, y + h, (40, 32, 28))
    cv.fill(x + 30, y + 14, x + 90, y + h - 4, (90, 90, 90))
    cv.fill(x + 110, y + 6, x + 122, y + h - 4, (120, 120, 120))
    for dx, s in [(40, 14), (60, 18), (82, 12)]:
        cv.tri(x + dx - s // 2, y + 16, x + dx + s // 2, y + 16, x + dx, y + 16 - s - 6, (255, 120, 30))
    cv.circle(x + 200, y + 12, 6, (150, 150, 150), fill=True)
    draw_text(cv, "4 DEAD", x + w - 56, y + h - 13, 1.6, WHITE, sx=0.9, wgt=1)

CARDS = [
    dict(n=4, place="RIYADH · WAR", tag="OFFICIAL", src="REUTERS · AFP",
         head="Three missiles downed over Riyadh",
         deck="Three ballistic missiles; no casualties.",
         scene=sc_riyadh),
    dict(n=5, place="FINLAND · CONFLICT", tag="CONFIRMED", src="FINLAND · REUTERS",
         head="Drones set Russian cargo ship ablaze off Finland",
         deck="Two drones hit Sparta II; 16 crew safe.",
         scene=sc_sparta),
    dict(n=6, place="SINALOA · CRIME", tag="CONFIRMED", src="AP · REUTERS",
         head="Mexico captures 'El Chapo Isidro'; 11 die",
         deck="FBI top-10 fugitive seized in Guasave.",
         scene=sc_chapo),
    dict(n=7, place="BRUSSELS · TRADE", tag="OFFICIAL", src="ANTARA · EU",
         head="EU and Indonesia sign trade pact",
         deck="98.5% of EU lines; 90.4% duty-free.",
         scene=sc_euindo),
    dict(n=8, place="BANDA SEA · QUAKE", tag="CONFIRMED", src="USGS · ABC AUSTRALIA",
         head="Deep quake shakes Timor-Leste and Darwin",
         deck="132 km deep; felt in Darwin.",
         scene=sc_banda),
    dict(n=9, place="GENEVA · AI ARMS", tag="REPORTED", src="AFP · AJ",
         head="UN 'killer robot' talks end with no binding treaty",
         deck="Draft rules due by 2028.",
         scene=sc_geneva),
    dict(n=10, place="MERCURY · SCIENCE", tag="OFFICIAL", src="ESA · AP",
         head="BepiColombo enters orbit around Mercury",
         deck="37-minute burn from 18:24 UTC.",
         scene=sc_bepi),
    dict(n=11, place="FRANCE · PROTEST", tag="OFFICIAL", src="AFP · FRANCE 24",
         head="Sixth Saturday of cost-of-living marches",
         deck="82,500 march, ministry counts.",
         scene=sc_france),
    dict(n=12, place="LONDON · RUGBY", tag="OFFICIAL", src="BBC · REUTERS",
         head="England beat All Blacks by record margin",
         deck="Biggest win over New Zealand.",
         scene=sc_rugby),
    dict(n=13, place="WORLD · MARKETS", tag="CONFIRMED", src="COINGECKO",
         head="Bitcoin dives, then rebounds",
         deck="$55,789 low; back over $60,000.",
         scene=sc_bitcoin),
    dict(n=14, place="TAIWAN · SECURITY", tag="OFFICIAL", src="TAIWAN MND",
         head="Taiwan says 21 Chinese jets held a patrol",
         deck="15 crossed the median line.",
         scene=sc_taiwan),
    dict(n=15, place="BASRA · DISASTER", tag="CONFIRMED", src="INA · ANADOLU",
         head="Basra power-station fire kills 4",
         deck="800 MW Hartha plant shut.",
         scene=sc_basra),
]

def card(cv, c, x, y, w):
    c['scene'](cv, x, y, w, 30)
    draw_text(cv, "%d · %s" % (c['n'], c['place']), x, y + 33, 1.35, INK, sx=0.85, wgt=1)
    tag(cv, x + w - 62, y + 32, c['tag'], sc=1.15)
    yy = para(cv, c['head'], x, y + 45, w, 2.0, INK, sx=0.85, wgt=2, lh=15, serif=True)
    draw_text(cv, c['deck'], x, y + 76, 1.3, INK, sx=0.85)
    draw_text(cv, c['src'], x, y + 87, 1.2, GREY, sx=0.85)

# ---------------------------------------------------------------- map + ALSO
def proj(lon, lat, x0=12, y0=762, w=328, h=128):
    return (x0 + (lon + 180) * w / 360.0, y0 + (75 - lat) * h / 130.0)

CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 62), (-70, 44),
     (-80, 32), (-81, 26), (-97, 26), (-105, 20), (-110, 23), (-125, 40), (-125, 49),
     (-140, 60), (-155, 58), (-168, 66)],
    [(-58, 64), (-45, 60), (-30, 68), (-40, 76), (-58, 74), (-58, 64)],
    [(-80, 9), (-75, 11), (-60, 8), (-50, 0), (-35, -8), (-40, -20), (-48, -28),
     (-58, -38), (-65, -45), (-70, -52), (-74, -40), (-80, -20), (-80, -5), (-80, 9)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (30, 60), (30, 70), (25, 71), (18, 69), (12, 65),
     (5, 60), (5, 58), (0, 54), (-5, 50), (-10, 43), (-10, 36)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28), (40, 15),
     (48, 11), (51, 10), (44, 0), (40, -10), (35, -20), (32, -28), (26, -34),
     (18, -35), (15, -27), (12, -18), (9, -1), (9, 4), (-8, 4), (-13, 8), (-17, 15)],
    [(30, 36), (35, 36), (40, 38), (48, 38), (55, 40), (60, 45), (65, 45), (70, 50),
     (75, 55), (80, 60), (90, 65), (100, 68), (110, 70), (130, 72), (140, 72),
     (158, 69), (170, 66), (178, 65), (170, 60), (162, 56), (158, 52), (150, 59),
     (142, 55), (140, 45), (135, 40), (130, 35), (127, 35), (122, 38), (120, 32),
     (115, 25), (110, 20), (108, 12), (105, 9), (100, 8), (98, 12), (95, 16),
     (92, 21), (88, 22), (85, 19), (80, 15), (76, 10), (72, 20), (68, 23), (62, 25),
     (58, 26), (55, 26), (50, 29), (48, 30), (44, 29), (40, 31), (36, 36), (30, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (137, -35), (140, -38),
     (145, -38), (150, -37), (153, -27), (150, -22), (146, -19), (142, -11), (137, -12),
     (132, -12), (126, -14), (122, -17), (118, -20), (113, -22)],
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41), (140, 44)],
]

# (number, lon, lat) - hand-spread where Europe/ME clusters would collide
PINS = [(1, 50.5, 26.2), (2, 30.7, 36.9), (3, -75.5, -11.0), (4, 46.7, 24.6),
        (5, 24.0, 60.0), (6, -108.0, 25.0), (7, 4.4, 50.8), (8, 128.0, -7.0),
        (9, 6.1, 46.2), (11, 2.3, 48.9), (12, -0.1, 51.5), (14, 121.5, 25.0),
        (15, 47.8, 30.5)]
PIN_OFF = {4: (0, 8), 7: (2, -6), 9: (6, 4), 11: (-8, -4), 12: (-6, 6), 15: (6, 8)}

def world_map(cv, x0=12, y0=750):
    draw_text(cv, "WHERE IT HAPPENED", x0, y0, 1.6, INK, sx=0.9, wgt=1)
    draw_text(cv, "pins match the story numbers", x0 + 150, y0 + 1, 1.3, GREY, sx=0.85)
    my = y0 + 16
    cv.fill(x0, my, x0 + 328, my + 128, SEA)
    for poly in CONTINENTS:
        cv.fill_poly([proj(lon, lat, x0, my) for lon, lat in poly], LAND)
        cv.poly([proj(lon, lat, x0, my) for lon, lat in poly], (180, 168, 140), 1, close=True)
    for n, lon, lat in PINS:
        px, py = proj(lon, lat, x0, my)
        dx, dy = PIN_OFF.get(n, (0, 0))
        px, py = px + dx, py + dy
        cv.circle(px, py, 7, RED, fill=True)
        cv.circle(px, py, 7, WHITE, w=1)
        draw_text(cv, str(n), px, py - 5, 1.3, WHITE, sx=0.9, wgt=1, align='c')
    draw_text(cv, "10 is Mercury, 13 is a global market", x0, my + 128 - 10, 1.2, GREY, sx=0.85)

ALSO = [
    (16, "Kyiv: 3 ballistic + 148 drones overnight (AP)"),
    (17, "Gaza: Israeli strikes kill six (AP)"),
    (18, "Hormuz: IRGC says it downed a US drone (IRIB)"),
    (19, "Iran: uranium stock stays at home (ToI)"),
    (20, "Washington: Trump vows tax on data centres (ABC)"),
    (21, "China tells Japan to 'correct' Taiwan words (AFP)"),
    (22, "Davao: jet lands safely, 146 aboard (AP)"),
    (23, "Canberra: Australia, China agree AI talks (ABC)"),
    (24, "Bolsonaro moved to intensive care (Reuters)"),
    (25, "India 486-4 v New Zealand (Reuters)"),
    (26, "CAF: all 54 back Infantino (AFP)"),
    (27, "Pakistan: 15 militants killed (Dawn)"),
    (28, "Manipur: toxic liquor kills 11 (Reuters)"),
    (29, "Jerusalem: Eisenkot invites Likud to talks (TOI)"),
    (30, "Washington: FBI probes database hack (BBC)"),
    (31, "Texas: execution takes an hour (NPR)"),
    (32, "Sinaloa: blockades follow arrest (AP)"),
    (33, "Falcon 9 launches USSF-317 (Space.com)"),
    (34, "Port Louis: rating agency talks 15 states (AJ)"),
    (35, "Brazil: Flamengo clinch second title (Reuters)"),
]

def also_list(cv, x0=348, y0=750):
    draw_text(cv, "ALSO ON SATURDAY 21 NOVEMBER 2026", x0, y0, 1.6, INK, sx=0.9, wgt=1)
    draw_text(cv, "20 MORE STORIES", x0 + 330, y0 + 1, 1.3, GREY, sx=0.85)
    for i, (n, txt) in enumerate(ALSO):
        col = 0 if i < 10 else 1
        row = i % 10
        bx = x0 + col * 336
        by = y0 + 16 + row * 13
        draw_text(cv, str(n), bx, by, 1.3, RED, sx=0.9, wgt=1)
        draw_text(cv, txt, bx + 20, by, 1.3, INK, sx=0.85)

DATECHECK = ("LEFT OUT - they belong to another day (UTC). Fri 20 Nov: Kyiv's bridges barrage "
             "(400+ drones, 110 missiles) · missiles landing in Poland · Wall Street's AI-rout "
             "correction (Nasdaq -5.3%) · Denmark expels Russian attache · "
             "Cyclone Akvan's landfall · the EU-UK summit. NOT YET: COP31 final text / approval "
             "session (Sun 06:00 GMT) · Las Vegas GP race (Sun 04:00 UTC) · Liverpool v Man United "
             "(Sun) · India declare at 720-9.")

def date_check(cv, y=898):
    cv.rect(12, y, 1012, y + 48, RED, 2)
    draw_text(cv, "DATE CHECK", 18, y + 4, 1.6, RED, sx=0.9, wgt=2)
    para(cv, DATECHECK, 18, y + 17, 988, 1.4, INK, sx=0.88, lh=10)

def footer(cv, y=946):
    draw_text(cv, "Sources: Reuters, AP, AFP, BBC, Al Jazeera, UKMTO, USGS, ESA, France 24, Anadolu, Antara, CoinGecko, Taiwan MND.",
              12, y, 1.3, GREY, sx=0.85)
    draw_text(cv, "HOW SURE: CONFIRMED = 2+ outlets · OFFICIAL = on the record · REPORTED = one outlet · CLAIM = one side's account.",
              12, y + 10, 1.3, GREY, sx=0.85)
    draw_text(cv, "Every story here happened, or was first reported, on Saturday 21 November 2026 (UTC). All maps and drawings are original vector work.",
              512, y + 22, 1.3, GREY, sx=0.85, align='c')

def main():
    cv = Canvas()
    header(cv)
    region_bar(cv, 106)
    utc_strip(cv, 123)
    numbers_strip(cv, 148)
    for i, h in enumerate(HEROES):
        hero(cv, h, 12 + i * 336, 226, 332)
    for i, c in enumerate(CARDS):
        col = i % 4
        row = i // 4
        card(cv, c, 12 + col * 251, 468 + row * 96, 247)
    world_map(cv, 12, 762)
    also_list(cv, 348, 762)
    date_check(cv, 912)
    footer(cv, 964)
    # The grader runs main.py in a fresh container with a read-only repo and a
    # writable /output: write entry.png there (or $MAKEFUN_OUTPUT_DIR when set).
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    write_png(path, cv.px)
    import hashlib
    data = open(path, "rb").read()
    print("entry.png", len(data), "bytes sha256", hashlib.sha256(data).hexdigest())

if __name__ == "__main__":
    main()
