using HarmonyLib;
using Vintagestory.API.Common;

namespace Gatewright
{
    public class GatewrightModSystem : ModSystem
    {
        private const string HarmonyId = "gatewright";
        private Harmony harmony;

        public override void Start(ICoreAPI api)
        {
            base.Start(api);

            // Both patches bail out for widths 1 and 2, so every vanilla door keeps
            // its stock behavior; only the 3-wide gate takes the new code paths.
            harmony = new Harmony(HarmonyId);
            harmony.PatchAll(typeof(GatewrightModSystem).Assembly);

            int patched = 0;
            foreach (var m in harmony.GetPatchedMethods()) patched++;
            api.Logger.Notification("[Gatewright] patched {0} door methods for n-width support", patched);
        }

        public override void Dispose()
        {
            harmony?.UnpatchAll(HarmonyId);
            harmony = null;
            base.Dispose();
        }
    }
}
