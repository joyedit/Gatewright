using HarmonyLib;
using Vintagestory.API.Common;
using Vintagestory.API.MathTools;
using Vintagestory.GameContent;

namespace Gatewright
{
    /// <summary>
    /// Vanilla's door system is written generically over `width` in almost every
    /// respect, but two methods assume a width of 1 or 2. Vanilla ships nothing
    /// wider than 2, so the assumptions have never bitten. A 3-wide gate trips
    /// both. Both patches no-op for width &lt;= 2, so vanilla doors are untouched.
    /// </summary>
    internal static class DoorGeometry
    {
        /// <summary>
        /// The cells a door leaf can ever occupy: the row along `right` when
        /// closed, and the row along `back` once it has swung a quarter turn.
        /// An L, not the full square - the diagonal cells are only crossed
        /// mid-swing and vanilla already reports no collision for them.
        /// </summary>
        internal static bool Visit(BlockPos tmpPos, BlockPos pos, int right, int back, int up,
                                   float yRotRad, bool invertHandle, ActionConsumable<BlockPos> onBlock)
        {
            Vec3i offset = BEBehaviorDoor.getAdjacentOffset(right, back, up, yRotRad, invertHandle);
            tmpPos.Set(pos.X + offset.X, pos.Y + offset.Y, pos.Z + offset.Z);
            return onBlock(tmpPos);
        }
    }

    /// <summary>
    /// IterateOverEach reserves a width x height x width volume - for a 3-wide
    /// gate that is 27 cells, including 4 diagonal cells per level that the leaf
    /// never rests in. Every one must be free or placement fails with "Not enough
    /// space", which makes a 3-wide gate unplaceable in most doorways and stops
    /// two of them being paired into a double gate. Reserve the L instead: 15
    /// cells for a 3x3, all of them cells the leaf can actually occupy.
    /// </summary>
    [HarmonyPatch(typeof(BlockBehaviorDoor), "IterateOverEach")]
    public static class DoorFootprintPatch
    {
        static bool Prefix(BlockBehaviorDoor __instance, BlockPos pos, float yRotRad,
                           bool invertHandle, ActionConsumable<BlockPos> onBlock)
        {
            int w = __instance.width;
            if (w <= 2) return true;

            BlockPos tmpPos = new BlockPos(pos.dimension);

            for (int up = 0; up < __instance.height; up++)
            {
                for (int right = 0; right < w; right++)
                {
                    if (!DoorGeometry.Visit(tmpPos, pos, right, 0, up, yRotRad, invertHandle, onBlock)) return false;
                }
                for (int back = 1; back < w; back++)
                {
                    if (!DoorGeometry.Visit(tmpPos, pos, 0, back, up, yRotRad, invertHandle, onBlock)) return false;
                }
            }

            return false;
        }
    }

    /// <summary>
    /// getColSelBoxes decides which ghost cells are solid using hardcoded offsets
    /// of one, under its own comment:
    ///
    ///     // Works only for 1 and 2 wide doors
    ///     // Would need to loop across width to make n-width doors
    ///
    /// Cells two steps out therefore stay solid in every state - invisible walls
    /// that block movement while naming themselves as the gate. This is that loop.
    /// </summary>
    [HarmonyPatch(typeof(BlockBehaviorDoor), "getColSelBoxes")]
    public static class DoorColSelBoxPatch
    {
        static bool Prefix(IBlockAccessor blockAccessor, BlockPos pos, Vec3i offset, ref Cuboidf[] __result)
        {
            var beh = blockAccessor
                .GetBlockEntity(pos.AddCopy(offset.X, offset.Y, offset.Z))
                ?.GetBehavior<BEBehaviorDoor>();
            if (beh?.doorBh == null) return true;

            int w = beh.doorBh.width;
            if (w <= 2) return true;

            // `offset` runs from ghost to controller, the opposite of the sense
            // placeMultiblockParts used, so cell (right, back) sits at
            // getAdjacentOffset(-right, -back).
            for (int right = 0; right < w; right++)
            {
                for (int back = 0; back < w; back++)
                {
                    Vec3i cell = beh.getAdjacentOffset(-right, -back, 0);
                    if (cell.X != offset.X || cell.Z != offset.Z) continue;

                    bool solid = beh.Opened ? right == 0 : back == 0;
                    __result = solid ? beh.ColSelBoxes : null;
                    return false;
                }
            }

            __result = beh.ColSelBoxes;
            return false;
        }
    }
}
