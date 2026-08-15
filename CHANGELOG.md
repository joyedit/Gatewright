# Changelog

## 0.2.1

- Fix the recipe producing vanilla's 2×3 gate instead of this one. Its pattern
  (`WWW,WWW,NWW`) was identical to vanilla's 2×3 gate recipe and differed only
  in quantities, which do not distinguish two recipes — both matched and
  vanilla's won. Nails move to the top-left corner (`NWW,WWW,WWW`), a pattern no
  vanilla plank-and-nails recipe uses.

## 0.2.0

Now a code mod. Vanilla's door system turned out not to support widths above 2,
so two Harmony patches (`src/DoorPatches.cs`) supply the missing generality.
Both no-op for widths 1 and 2, so vanilla doors behave exactly as before.

- Fix invisible blocks around the gate that stopped movement and named
  themselves as the gate. `BlockBehaviorDoor.getColSelBoxes` picked solid cells
  using hardcoded offsets of one — vanilla's own comment there reads *"Works
  only for 1 and 2 wide doors / Would need to loop across width to make n-width
  doors"*. Replaced with that loop.
- Fix "Not enough space!" when placing the gate in a doorway or pairing two into
  a double gate. `IterateOverEach` reserved a width × height × width volume — 27
  cells for a 3×3, including diagonal cells the leaf never rests in. Now reserves
  the 15 cells the leaf can actually occupy.

## 0.1.0

Initial release. Built against Vintage Story 1.22.5.

- Adds `gatewright:gate-3x3gate-{wood}`, a 3-block-wide by 3-block-tall swinging
  wooden gate, in all 12 wood types plus aged and very aged.
- Shape derived from vanilla's `2x3gate`, widened to 48 units, with the peep
  window and drop-bar latch recentred on the wider leaf.
- Adds iron cross-braces with rivets and pintle hinge knuckles, neither of which
  vanilla's wooden gates have.
- Uses the vanilla `Door` behavior, so it locks, pairs into double gates and
  seals cellars like any other door.
