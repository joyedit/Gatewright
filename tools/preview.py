#!/usr/bin/env python3
"""Orthographic front-view preview of a VS block shape, as SVG.

Walks the element tree the way the game does - child coordinates are relative to
the parent's `from`, and a parent's rotationZ carries down to its children - then
paints the XY footprint of every box back-to-front.
"""
import json
import math
import sys

SRC = sys.argv[1]
OUT = sys.argv[2]

shape = json.load(open(SRC))

WOOD = ["#7a5533", "#8a6039", "#6d4a2c", "#94693f"]
IRON = "#585c63"
IRON_HI = "#71767e"


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def translate(dx, dy):
    return [[1, 0, dx], [0, 1, dy], [0, 0, 1]]


def rotate_about(cx, cy, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return mat_mul(translate(cx, cy), mat_mul([[c, -s, 0], [s, c, 0], [0, 0, 1]],
                                              translate(-cx, -cy)))


def apply(m, x, y):
    return (m[0][0] * x + m[0][1] * y + m[0][2],
            m[1][0] * x + m[1][1] * y + m[1][2])


IDENT = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
quads = []


def walk(els, xform, zoff):
    for e in els:
        f, t = e.get("from"), e.get("to")
        m = xform
        if f is None or t is None:
            walk(e.get("children", []), m, zoff)
            continue
        if e.get("rotationZ"):
            ro = e.get("rotationOrigin") or f
            m = mat_mul(xform, rotate_about(ro[0], ro[1], e["rotationZ"]))
        z = zoff + f[2]
        if abs(t[0] - f[0]) > 1e-6 and abs(t[1] - f[1]) > 1e-6:
            corners = [apply(m, f[0], f[1]), apply(m, t[0], f[1]),
                       apply(m, t[0], t[1]), apply(m, f[0], t[1])]
            tex = ""
            for fc in (e.get("faces") or {}).values():
                tex = fc.get("texture", "")
                break
            quads.append((z, corners, tex, e["name"]))
        walk(e.get("children", []), mat_mul(m, translate(f[0], f[1])), z)


walk(shape["elements"], IDENT, 0.0)
quads.sort(key=lambda q: -q[0])

xs = [p[0] for _, c, _, _ in quads for p in c]
ys = [p[1] for _, c, _, _ in quads for p in c]
print(f"drawn quads: {len(quads)}")
print(f"projected extent  x {min(xs):.2f}..{max(xs):.2f}   y {min(ys):.2f}..{max(ys):.2f}")

S = 14                                   # px per shape unit
PAD = 24
W = int((48 + 4) * S) + PAD * 2
H = int(48 * S) + PAD * 2


def sx(x):
    return PAD + (x + 2) * S


def sy(y):
    return PAD + (48 - y) * S


out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="#20242b"/>']

# block grid: the three cells the gate occupies
for gx in range(4):
    out.append(f'<line x1="{sx(gx*16):.1f}" y1="{sy(0):.1f}" x2="{sx(gx*16):.1f}" '
               f'y2="{sy(48):.1f}" stroke="#3a4150" stroke-width="1"/>')
for gy in range(4):
    out.append(f'<line x1="{sx(0):.1f}" y1="{sy(gy*16):.1f}" x2="{sx(48):.1f}" '
               f'y2="{sy(gy*16):.1f}" stroke="#3a4150" stroke-width="1"/>')

wi = 0
for z, corners, tex, name in quads:
    if tex == "#iron":
        fill = IRON_HI if name.startswith(("brace", "pintle")) else IRON
    elif name.startswith("V-Board"):
        fill = WOOD[hash(name) % len(WOOD)]
    else:
        wi += 1
        fill = WOOD[wi % len(WOOD)]
    pts = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in corners)
    out.append(f'<polygon points="{pts}" fill="{fill}" stroke="#00000055" '
               f'stroke-width="0.5"/>')

out.append('</svg>')
open(OUT, "w").write("\n".join(out))
print(f"wrote {OUT}")
