using System;
using UnityEngine;

namespace Ominous
{
    /// <summary>
    /// Luz de la casa (OSCURIDAD.md): con el diferencial bajado se apagan las luces, la tele y la nevera,
    /// y el interior se queda en negro de verdad; solo entra la farola por las ventanas.
    /// </summary>
    public static class HouseLights
    {
        public static bool Power { get; private set; } = true;
        public static event Action Changed;

        static readonly int Darkness = Shader.PropertyToID("_Video_Darkness");
        static float level = 1f, target = 1f;

        /// <summary>Al cargar la escena la casa siempre empieza con luz.</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        static void Reset()
        {
            Power = true;
            level = target = 1f;
            Shader.SetGlobalVector(Darkness, Vector4.one);
        }

        public static void SetPower(bool on)
        {
            if (Power == on) return;
            Power = on;
            target = on ? 1f : 0f;
            foreach (var s in UnityEngine.Object.FindObjectsByType<LightSwitch>(FindObjectsSortMode.None)) s.Refresh();
            foreach (var tv in UnityEngine.Object.FindObjectsByType<TVFlicker>(FindObjectsSortMode.None)) tv.SetPowered(on);
            foreach (var l in UnityEngine.Object.FindObjectsByType<Light>(FindObjectsInactive.Include, FindObjectsSortMode.None))
                if (l.name == "LuzTeleResplandor") l.enabled = on;
            foreach (var a in UnityEngine.Object.FindObjectsByType<AudioSource>(FindObjectsSortMode.None))
                if (a.name == "Nevera") a.mute = !on;
            if (GameDirector.Instance != null) GameDirector.Instance.Night.powerOff = !on;
            Changed?.Invoke();
        }

        /// <summary>
        /// La llama el controlador de imagen cada fotograma. Devuelve 1 con luz y 0 en apagón, con una transición corta:
        /// x escala la luz horneada del interior, y la luz ambiente del interior.
        /// </summary>
        public static float Tick(float dt)
        {
            level = Mathf.MoveTowards(level, target, dt * 2.5f);
            // En apagón queda un resto mínimo para que la farola por la ventana se lea como luz de noche.
            float lightmap = Mathf.Lerp(0.18f, 1f, level);
            float ambient = Mathf.Lerp(0.04f, 1f, level);
            Shader.SetGlobalVector(Darkness, new Vector4(lightmap, ambient, level, 0f));
            return level;
        }
    }
}
