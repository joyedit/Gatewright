#!/usr/bin/env python3
"""Derive a 3-wide x 3-tall braced wooden gate shape from vanilla's 2x3gate.

The vanilla gate is 32 units wide (2 blocks). Everything here widens it to 48
(3 blocks) while leaving the element hierarchy, the ROTATOR hinge pivot and the
z-plane of the leaf exactly as vanilla authored them, so the Door behavior sees
the same conventions it already understands. On top of that we add the thing
vanilla's gate does not have: real iron cross-braces and pintle hinges.
"""
import copy
import json
import math
import os

VS = os.path.expanduser("~/Apps/vintagestory")
SRC = f"{VS}/assets/survival/shapes/block/wood/door/2x3gate.json"
OUT = os.path.expanduser("~/Dev/Gatewright/assets/gatewright/shapes/block/gate/3x3gate.json")

# Vanilla spans rel x -1..31; we extend to -1..47 (3 blocks of 16).
NEW_EDGE = 47.0
# Rail centre heights, from the three H-Boards below.
RAIL_Y = {"H-BoardA1": 8.0, "H-BoardA3": 24.5, "H-BoardA2": 39.0}

shape = json.load(open(SRC))


def find(els, name):
    for e in els:
        if e["name"] == name:
            return e
        r = find(e.get("children", []), name)
        if r:
            return r
    return None


root = shape["elements"][0]
rotator = find(shape["elements"], "ROTATOR")
kids = rotator["children"]


# --- 1. four more vertical boards, continuing the hand-hewn z jitter ------------
template = find(shape["elements"], "V-BoardA7")
Z_JITTER = [-1.0, -1.1, -0.9, -1.2]
for i, x0 in enumerate([31.0, 35.0, 39.0, 43.0]):
    b = copy.deepcopy(template)
    n = 9 + i
    z = Z_JITTER[i]
    b["name"] = f"V-BoardA{n}"
    b["from"] = [x0, 0.0, z]
    b["to"] = [x0 + 4.0, 16.0, z + 2.0]
    b["rotationOrigin"] = [x0 + 1.0, 0.0, z + 1.0]
    for c in b["children"]:
        c["name"] = c["name"].replace("7", str(n))
    kids.append(b)


# --- 2. extend the three horizontal rails to the new edge -----------------------
for board_name in RAIL_Y:
    board = find(shape["elements"], board_name)
    seg = board_name.replace("H-BoardA", "")  # "1" / "2" / "3"
    b_seg = find(board["children"], f"H-B{seg}")
    c_seg = copy.deepcopy(b_seg)
    c_seg["name"] = f"H-C{seg}"
    c_seg["children"] = []          # the window/latch stay on the middle segment
    c_seg["from"] = [31.0, 0.0, 0.0]
    c_seg["to"] = [NEW_EDGE, 4.0, 2.0]
    c_seg["rotationOrigin"] = [31.0, 0.0, 0.0]
    board["children"].append(c_seg)


# --- 3. nails across the newly exposed rail ------------------------------------
nail_no = 100
for board_name in RAIL_Y:
    board = find(shape["elements"], board_name)
    nails = [c for c in board["children"] if c["name"].startswith("Nail")]
    last_x = max(n["from"][0] for n in nails)
    x = last_x + 4.0
    while x < NEW_EDGE - 1.0:
        n = copy.deepcopy(nails[-1])
        nail_no += 1
        n["name"] = f"Nail{nail_no}"
        dx = x - nails[-1]["from"][0]
        n["from"] = [nails[-1]["from"][0] + dx, nails[-1]["from"][1], nails[-1]["from"][2]]
        n["to"] = [nails[-1]["to"][0] + dx, nails[-1]["to"][1], nails[-1]["to"][2]]
        n["rotationOrigin"] = [nails[-1]["rotationOrigin"][0] + dx,
                               nails[-1]["rotationOrigin"][1],
                               nails[-1]["rotationOrigin"][2]]
        board["children"].append(n)
        x += 4.0


# --- 4. recentre window + drop-bar latch on the wider leaf ----------------------
# Vanilla cuts the peep-window hole by starting boards 5 and 6 at y=23 instead of
# y=16, putting the hole at x 15..23 - centred on a 32-wide leaf. On a 48-wide
# leaf the centre moves to x 23, so the hole moves one board right (boards 6 and
# 8, x 19..27) and the shutter, its hinges and the drop bar shift by the same 4.
WINDOW_SHIFT = 4.0
find(shape["elements"], "V-BoardB5")["from"][1] = 16.0   # board 5 becomes solid
find(shape["elements"], "V-BoardB8")["from"][1] = 23.0   # board 8 gains the notch

mid = find(shape["elements"], "H-B3")
for c in mid["children"]:
    for key in ("from", "to", "rotationOrigin"):
        if key in c and c[key] is not None:
            c[key][0] += WINDOW_SHIFT
bar = find(shape["elements"], "Bar")
if bar:                      # lengthen the drop bar to suit the wider gate
    bar["to"][0] = bar["from"][0] + 20.0


# --- 5. move the ring handle out to the new free edge ---------------------------
handle = find(shape["elements"], "HandleD")
for key in ("from", "to", "rotationOrigin"):
    if key in handle and handle[key] is not None:
        handle[key][0] += 16.0


# --- 6. iron cross-braces (the part vanilla's gate lacks) -----------------------
def iron_faces(length, h, d):
    return {
        "north": {"texture": "#iron", "uv": [0.0, 0.0, min(length, 16.0), h]},
        "south": {"texture": "#iron", "uv": [0.0, 0.0, min(length, 16.0), h]},
        "up":    {"texture": "#iron", "uv": [0.0, 0.0, min(length, 16.0), d]},
        "down":  {"texture": "#iron", "uv": [0.0, 0.0, min(length, 16.0), d]},
        "east":  {"texture": "#iron", "uv": [0.0, 0.0, d, h]},
        "west":  {"texture": "#iron", "uv": [0.0, 0.0, d, h]},
    }


BRACE_H, BRACE_D = 2.5, 2.0
BRACE_Z = -2.4                       # sits 0.4 proud of the wooden rails

def add_brace(tag, x0, y_from, y_to):
    """One iron strap running from the hinge edge up to the free edge."""
    dx = 45.0
    dy = y_to - y_from
    length = math.hypot(dx, dy)
    theta = math.degrees(math.atan2(dy, dx))

    seg_len = 16.0
    nsegs = int(math.ceil(length / seg_len))
    parent = None
    for i in range(nsegs):
        a = i * seg_len
        b = min((i + 1) * seg_len, length)
        el = {
            "name": f"brace{tag}{i + 1}",
            "from": [x0 if i == 0 else a, (y_from - BRACE_H / 2) if i == 0 else 0.0,
                     BRACE_Z if i == 0 else 0.0],
            "to": [(x0 + b) if i == 0 else b,
                   (y_from - BRACE_H / 2 + BRACE_H) if i == 0 else BRACE_H,
                   (BRACE_Z + BRACE_D) if i == 0 else BRACE_D],
            "rotationOrigin": [x0, y_from, BRACE_Z + BRACE_D / 2] if i == 0 else [a, 0.0, 0.0],
            "faces": iron_faces(b - a, BRACE_H, BRACE_D),
            "children": [],
        }
        if i == 0:
            el["rotationZ"] = theta
            parent = el
        else:
            parent["children"].append(el)
    # Rivets pinning the brace to each board it crosses. The later segments are
    # siblings sharing the first segment's frame, so rivets hang off it directly.
    for j, rx in enumerate([6.0, 18.0, 30.0, 42.0]):
        if rx > length - 2:
            continue
        parent["children"].append({
            "name": f"braceRivet{tag}{j + 1}",
            "from": [rx - 0.4, BRACE_H / 2 - 0.4, -0.3],
            "to": [rx + 0.4, BRACE_H / 2 + 0.4, BRACE_D + 0.3],
            "rotationOrigin": [rx, BRACE_H / 2, BRACE_D / 2],
            "rotationZ": -45.0,
            "faces": iron_faces(0.8, 0.8, 0.8),
            "children": [],
        })
    return parent


kids.append(add_brace("A", 1.0, RAIL_Y["H-BoardA1"], RAIL_Y["H-BoardA3"]))
kids.append(add_brace("B", 1.0, RAIL_Y["H-BoardA3"], RAIL_Y["H-BoardA2"]))


# --- 7. pintle hinge knuckles on the hanging edge -------------------------------
for i, ry in enumerate(sorted(RAIL_Y.values())):
    kids.append({
        "name": f"pintle{i + 1}",
        "from": [-2.5, ry - 1.6, -1.6],
        "to": [0.5, ry + 1.6, 0.6],
        "rotationOrigin": [-1.0, ry, -0.5],
        "faces": iron_faces(3.0, 3.2, 2.2),
    })


# --- 8. textures ----------------------------------------------------------------
shape["textures"] = {
    "iron": "game:block/metal/ingot/iron",
    "wood": "game:block/wood/debarked/oak",
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(shape, open(OUT, "w"), indent=1)


def count(els):
    return sum(1 + count(e.get("children", [])) for e in els)


def bbox(els, off=(0.0, 0.0, 0.0), acc=None):
    if acc is None:
        acc = [[1e9, -1e9], [1e9, -1e9], [1e9, -1e9]]
    for e in els:
        f, t = e.get("from"), e.get("to")
        if f and t:
            for i in range(3):
                acc[i][0] = min(acc[i][0], off[i] + f[i], off[i] + t[i])
                acc[i][1] = max(acc[i][1], off[i] + f[i], off[i] + t[i])
            bbox(e.get("children", []), tuple(off[i] + f[i] for i in range(3)), acc)
        else:
            bbox(e.get("children", []), off, acc)
    return acc


bb = bbox(shape["elements"])
print(f"elements: {count(shape['elements'])}")
print(f"absolute bbox  x {bb[0]}  y {bb[1]}  z {bb[2]}")
print(f"animations: {[a['name'] for a in shape['animations']]}")
print(f"rotates element: {list(shape['animations'][0]['keyframes'][0]['elements'])}")
print(f"wrote {OUT}")
