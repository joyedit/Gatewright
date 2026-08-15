# Gatewright

A 3×3 swinging wooden gate for Vintage Story — three blocks wide, three blocks
tall, with real iron cross-braces.

## What it adds

One block, `gatewright:gate-3x3gate-{wood}`, in all 12 wood types plus `aged`
and `veryaged`:

- 12 vertical planks over three nailed rails
- two riveted iron straps running corner to corner (bottom rail → middle rail →
  top rail), the classic Z-brace of a real braced gate
- three pintle hinge knuckles on the hanging edge
- a hinged peep window with a drop-bar latch across it
- an iron ring handle on the free edge

It is built on the vanilla `Door` block behavior, so locking, double gates
(place two side by side for a six-wide opening), airtight cellar sealing and
reinforced-door interaction all work exactly as they do for vanilla doors.

## Crafting

Full 3×3 grid, **nails in the top-left corner**, planks in the other eight:

```
N W W      N = 10 nails and strips, any metal
W W W      W = 4 planks each, 32 total, all the same wood
W W W
```

The wood type of the planks determines the gate's wood type.

The pattern has to differ from vanilla's four gate recipes, not just in
quantities — two recipes sharing a pattern both match, and vanilla's wins. Nails
bottom-left is vanilla's 2×3 gate, bottom-right is its 2×4, and `WWW,WNW,WWW` is
a chest.

## Building the model

The shape is generated rather than hand-authored. `tools/gen_gate.py` reads
vanilla's `block/wood/door/2x3gate` shape, widens it from 32 to 48 units, moves
the peep window to the new centre, and adds the iron braces and pintles that
vanilla's gate does not have. Run it after changing the game version if vanilla's
gate shape changes:

```sh
python3 tools/gen_gate.py
```

`tools/preview.py` renders a flat front-view SVG of the resulting shape, which is
much faster than launching the game to check geometry:

```sh
python3 tools/preview.py assets/gatewright/shapes/block/gate/3x3gate.json /tmp/gate.svg
```

## Deploying

```sh
./deploy.sh
```

Content-only mod — nothing to compile. Packages `assets/` and `modinfo.json`
into `Gatewright-<version>.zip` and drops it in
`~/.config/VintagestoryData/Mods`, removing any older versioned zip first.
