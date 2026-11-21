"""Render one newspaper front page summing up world news of Saturday
21 November 2026. Pure Pillow, no network, fully deterministic.

Run:  python3 render_news.py [output.png]
Default output is entry.png next to this file.
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 241, 226)
INK = (20, 20, 20)
RED = (179, 35, 27)
DARKBLUE = (31, 58, 95)
TEAL = (15, 118, 110)
GOLD = (201, 162, 39)
GREY = (90, 86, 76)
LIGHTGREY = (222, 214, 196)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        try:
            return ImageFont.truetype(SANS, size)
        except Exception:
            return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, text, fnt, x, y, max_w, fill=INK, leading=None):
    if leading is None:
        leading = int(fnt.size * 1.22)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def star_points(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_explosion(draw, cx, cy, r):
    # jagged starburst: red outer, orange mid, yellow core
    outer = star_points(cx, cy, r, r * 0.42, 12, rot=-90)
    draw.polygon(outer, fill=(198, 52, 30))
    mid = star_points(cx, cy, r * 0.62, r * 0.28, 12, rot=-78)
    draw.polygon(mid, fill=(232, 126, 32))
    core = star_points(cx, cy, r * 0.34, r * 0.16, 8, rot=-90)
    draw.polygon(core, fill=(245, 196, 66))
    # missile trails arcing in from the top corners, kept inside the burst
    draw.arc([cx - r - 10, cy - r - 46, cx + 30, cy - 6], 200, 330, fill=INK, width=4)
    draw.arc([cx - 10, cy - r - 52, cx + r + 16, cy - 14], 210, 340, fill=INK, width=4)
    draw.ellipse([cx - r - 14, cy - r - 30, cx - r + 2, cy - r - 14], fill=INK)
    draw.ellipse([cx + r - 2, cy - r - 36, cx + r + 14, cy - r - 20], fill=INK)


def draw_scales(draw, x, y, s, color):
    # simple scales of justice inside a square of side s at (x, y)
    cx, cy = x + s // 2, y + s // 2
    draw.line([(cx, y + 8), (cx, y + s - 22)], fill=color, width=4)
    draw.line([(x + 8, y + 22), (x + s - 8, y + 22)], fill=color, width=4)
    draw.line([(cx, y + 22), (x + 16, y + 52)], fill=color, width=3)
    draw.line([(cx, y + 22), (x + s - 16, y + 52)], fill=color, width=3)
    draw.pieslice([x + 4, y + 48, x + 28, y + 66], 0, 180, fill=color)
    draw.pieslice([x + s - 28, y + 48, x + s - 4, y + 66], 0, 180, fill=color)
    draw.line([(x + 14, y + s - 12), (x + s - 14, y + s - 12)], fill=color, width=5)
    draw.ellipse([cx - 6, y + 4, cx + 6, y + 16], fill=color)


def draw_chart(draw, x, y, s, color):
    # falling market chart: axes, descending red line, bars
    draw.line([(x + 6, y + 8), (x + 6, y + s - 8)], fill=INK, width=3)
    draw.line([(x + 6, y + s - 8), (x + s - 6, y + s - 8)], fill=INK, width=3)
    pts = [(x + 12, y + 16), (x + 30, y + 26), (x + 46, y + 22),
           (x + 62, y + 44), (x + 78, y + 58), (x + s - 12, y + s - 20)]
    draw.line(pts, fill=color, width=5, joint="curve")
    draw.polygon([(x + s - 12, y + s - 20), (x + s - 26, y + s - 24),
                  (x + s - 22, y + s - 34)], fill=color)
    for bx, bh in [(18, 18), (36, 26), (54, 20), (72, 12)]:
        draw.rectangle([x + bx, y + s - 14 - bh, x + bx + 10, y + s - 14],
                       fill=(180, 180, 170))


def draw_cyclone(draw, x, y, s, color):
    # spiral storm: concentric arcs + rain ticks
    cx, cy = x + s // 2, y + s // 2
    for i, r in enumerate(range(10, s // 2 + 2, 9)):
        start = 20 + i * 55
        draw.arc([cx - r, cy - r, cx + r, cy + r], start, start + 250,
                 fill=color, width=4)
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=color)
    for dx in (-26, 0, 26):
        draw.line([(cx + dx, y + s - 12), (cx + dx - 5, y + s - 2)],
                  fill=color, width=3)


def draw_flags(draw, x, y, s):
    # three small flags: US, China, Russia
    bw, bh = s // 3 - 6, s // 2
    # US: stripes + blue canton
    fx = x
    for i in range(7):
        draw.rectangle([fx, y + i * bh // 7, fx + bw, y + (i + 1) * bh // 7],
                       fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    draw.rectangle([fx, y, fx + bw // 2, y + bh // 2], fill=(30, 58, 95))
    draw.polygon(star_points(fx + bw // 4, y + bh // 4, 6, 2.5), fill=(255, 255, 255))
    # China: red field, yellow star
    fx = x + s // 3
    draw.rectangle([fx, y, fx + bw, y + bh], fill=(222, 41, 16))
    draw.polygon(star_points(fx + bw // 2, y + bh // 2, 12, 5), fill=(255, 222, 0))
    # Russia: white / blue / red bands
    fx = x + 2 * s // 3
    for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 0, 50)]):
        draw.rectangle([fx, y + i * bh // 3, fx + bw, y + (i + 1) * bh // 3],
                       fill=c)
    draw.rectangle([x, y, x + s - 6, y + bh], outline=INK, width=2)


def draw_stars_ring(draw, x, y, s, color):
    cx, cy = x + s // 2, y + s // 2
    for i in range(12):
        a = math.radians(i * 30 - 90)
        sx, sy = cx + (s // 2 - 10) * math.cos(a), cy + (s // 2 - 10) * math.sin(a)
        draw.polygon(star_points(sx, sy, 6, 2.5), fill=color)


def kicker(draw, text, x, y, color, size=17):
    f = font(SANS_BOLD, size)
    draw.text((x, y), text, font=f, fill=color)
    return y + size + 8


def story_panel(draw, x, y, w, h, kick, kick_color, headline, deck,
                icon=None, head_size=30, deck_size=19):
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    draw.rectangle([x + 2, y + 2, x + w - 2, y + 6], fill=kick_color)
    pad = 16
    tx, ty = x + pad, y + 14
    text_w = w - 2 * pad - (110 if icon else 0)
    ty = kicker(draw, kick, tx, ty, kick_color)
    ty = draw_wrapped(draw, headline, font(SERIF_BOLD, head_size),
                      tx, ty, text_w, leading=head_size + 6)
    # never let the deck run past the panel: trim it to the lines that fit
    deck_fnt = font(SANS, deck_size)
    deck_leading = deck_size + 6
    room = (y + h - pad) - (ty + 4)
    max_lines = max(1, room // deck_leading)
    lines = wrap(draw, deck, deck_fnt, text_w)[:max_lines]
    yy = ty + 4
    for line in lines:
        draw.text((tx, yy), line, font=deck_fnt, fill=(40, 38, 32))
        yy += deck_leading
    if icon:
        icon(draw, x + w - 104, y + 16, 88)


def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    m = 30  # margin

    # ---- masthead ----
    title = "THE WORLD TODAY"
    tf = font(SERIF_BOLD, 68)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, 22), title, font=tf, fill=INK)
    d.line([(m, 108), (W - m, 108)], fill=INK, width=3)
    d.line([(m, 114), (W - m, 114)], fill=INK, width=1)
    date_f = font(SANS_BOLD, 26)
    d.text((m, 126), "SATURDAY, 21 NOVEMBER 2026", font=date_f, fill=RED)
    tag_f = font(SANS, 20)
    tag = "THE DAY IN ONE PAGE"
    d.text((W - m - d.textlength(tag, font=tag_f), 128), tag,
           font=tag_f, fill=GREY)
    d.line([(m, 160), (W - m, 160)], fill=RED, width=3)

    # ---- lead story: missiles fall on Poland ----
    lx, ly, lw, lh = m, 172, W - 2 * m, 264
    d.rectangle([lx, ly, lx + lw, ly + lh], outline=INK, width=2)
    d.rectangle([lx + 2, ly + 2, lx + lw - 2, ly + 8], fill=RED)
    ty = kicker(d, "POLAND  •  NATO  •  LEAD STORY", lx + 18, ly + 16, RED, 18)
    ty = draw_wrapped(d, "RUSSIAN MISSILES FALL ON POLAND",
                      font(SERIF_BOLD, 50), lx + 18, ty, 620,
                      leading=56)
    draw_wrapped(d,
                 "Two Russian missiles and a suspected drone come down on "
                 "Polish soil. Warsaw calls it a deliberate provocation; "
                 "NATO condemns a grave violation of its airspace.",
                 font(SANS, 20), lx + 18, ty + 6, 620,
                 fill=(40, 38, 32), leading=26)
    draw_explosion(d, lx + lw - 128, ly + 160, 78)

    # ---- row 2: ICJ + markets ----
    y2, h2 = 448, 208
    story_panel(d, m, y2, 470, h2,
                "THE HAGUE  •  JUSTICE", DARKBLUE,
                "MYANMAR GUILTY OF GENOCIDE",
                "The World Court rules Myanmar's forces committed genocide "
                "against the Rohingya.",
                icon=lambda dr, x, y, s: draw_scales(dr, x, y, s, DARKBLUE),
                head_size=27, deck_size=18)
    story_panel(d, W - m - 470, y2, 470, h2,
                "NEW YORK  •  MARKETS", RED,
                "STOCKS TUMBLE INTO CORRECTION",
                "The S&P 500 and the Dow slide as AI shares sell off; "
                "Wall Street falls about 3.7% in a day.",
                icon=lambda dr, x, y, s: draw_chart(dr, x, y, s, RED),
                head_size=27, deck_size=18)

    # ---- row 3: cyclone + trilateral summit ----
    y3, h3 = 668, 208
    story_panel(d, m, y3, 470, h3,
                "INDIA  •  WEATHER", TEAL,
                "CYCLONE AKVAN HITS INDIA'S COAST",
                "The storm crosses the Odisha coast near Gopalpur; 300,000 "
                "people evacuated.",
                icon=lambda dr, x, y, s: draw_cyclone(dr, x, y, s, TEAL),
                head_size=27, deck_size=18)
    story_panel(d, W - m - 470, y3, 470, h3,
                "SHENZHEN  •  SUMMIT", DARKBLUE,
                "TRUMP, XI AND PUTIN MEET — FEW RESULTS",
                "The first trilateral summit of the three biggest nuclear "
                "powers ends with little concrete to show.",
                icon=lambda dr, x, y, s: draw_flags(dr, x, y, s),
                head_size=24, deck_size=18)

    # ---- row 4: UK-EU deals + ticker ----
    y4, h4 = 888, 74
    d.rectangle([m, y4, W - m, y4 + h4], outline=INK, width=2)
    d.rectangle([m + 2, y4 + 2, m + 6, y4 + h4 - 2], fill=GOLD)
    draw_stars_ring(d, m + 12, y4 + 8, 60, GOLD)
    d.text((m + 84, y4 + 10), "BRITAIN AND THE EU SIGN NEW DEALS",
           font=font(SERIF_BOLD, 24), fill=INK)
    d.text((m + 84, y4 + 42),
           "Food trade, carbon markets and youth mobility agreed in Brussels.",
           font=font(SANS, 18), fill=(40, 38, 32))

    # ---- footer ticker ----
    fy = 974
    d.text((m, fy),
           "ALSO TODAY: UK pledges 1,000 drones for Ukraine  •  NSE now the "
           "world's 5th-largest exchange",
           font=font(SANS, 16), fill=GREY)

    img.save(path, "PNG", optimize=True)
    return path


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    render(out)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
