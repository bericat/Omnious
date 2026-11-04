using UnityEngine;
using UnityEngine.InputSystem;

namespace Ominous
{
    /// <summary>Panel de pruebas (F1): ajustes de imagen en vivo y medición de fps.</summary>
    public class VideoLookPanel : MonoBehaviour
    {
        public VideoLookController controller;
        VideoLookSettings settings => controller != null ? controller.settings : null;
        bool open;
        float smooth = 1f / 60f, worst, worstTimer;
        GUIStyle style;
        float logSeconds, logTime, logWorst; int logFrames; float started = -1f;

        void Start()
        {
            // Medición sin pantalla de por medio: ./Ominous -fpslog 30 escribe en Player.log y sale.
            var args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, "-fpslog");
            if (i >= 0 && i + 1 < args.Length) float.TryParse(args[i + 1], out logSeconds);
        }

        void Update()
        {
            float dt = Time.unscaledDeltaTime;
            if (logSeconds > 0f && Time.realtimeSinceStartup > 8f)
            {
                if (started < 0f) started = Time.realtimeSinceStartup;
                logTime += dt; logFrames++; logWorst = Mathf.Max(logWorst, dt);
                if (Time.realtimeSinceStartup - started >= logSeconds)
                {
                    Debug.Log($"FPSLOG media={logFrames / logTime:0.0} peor_ms={logWorst * 1000f:0.0} frames={logFrames} {Screen.width}x{Screen.height} {SystemInfo.graphicsDeviceType}");
                    Application.Quit();
                }
            }
            smooth = Mathf.Lerp(smooth, dt, 0.05f);
            worst = Mathf.Max(worst, dt);
            worstTimer += dt;
            if (worstTimer > 2f) { worst = dt; worstTimer = 0f; }
            if (Keyboard.current != null && Keyboard.current.f1Key.wasPressedThisFrame)
            {
                open = !open;
                FirstPersonController.SetBlocked(this, open);
            }
        }

        void OnDisable() => FirstPersonController.SetBlocked(this, false);

        float Slider(string label, float value, float min, float max)
        {
            GUILayout.Label($"{label}: {value:0.##}", style);
            return GUILayout.HorizontalSlider(value, min, max);
        }

        void OnGUI()
        {
            style ??= new GUIStyle(GUI.skin.label) { fontSize = 16 };
            GUI.color = new Color(1f, 1f, 1f, 0.9f);
            GUI.Label(new Rect(8, 4, 500, 26), $"{1f / smooth:0} fps · peor {worst * 1000f:0} ms · F1 ajustes", style);
            if (!open || settings == null) return;
            GUILayout.BeginArea(new Rect(8, 32, 340, 620), GUI.skin.box);
            settings.internalHeight = Mathf.RoundToInt(Slider("Resolución interna", settings.internalHeight, 360, 800));
            settings.softness = Slider("Suavizado", settings.softness, 0f, 2f);
            settings.noise = Slider("Ruido", settings.noise, 0f, 0.1f);
            settings.aberration = Slider("Separación RGB", settings.aberration, 0f, 0.02f);
            settings.vignette = Slider("Viñeta", settings.vignette, 0f, 0.6f);
            settings.distortion = Slider("Distorsión de lente", settings.distortion, 0f, 0.4f);
            settings.saturation = Slider("Saturación", settings.saturation, 0f, 1.2f);
            settings.brightness = Slider("Brillo", settings.brightness, 0.5f, 2f);
            settings.exteriorFogEnd = Slider("Niebla de la calle", settings.exteriorFogEnd, 5f, 60f);
            GUILayout.EndArea();
        }
    }
}
