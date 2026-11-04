using UnityEngine;
using UnityEngine.InputSystem;

namespace Ominous
{
    /// <summary>Panel de pruebas (F1): ajustes PSX en vivo y medición de fps.</summary>
    public class PSXPanel : MonoBehaviour
    {
        public PSXSettings settings;
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
                FirstPersonController.InputBlocked = open;
            }
        }

        void OnDisable() => FirstPersonController.InputBlocked = false;

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
            GUILayout.BeginArea(new Rect(8, 32, 340, 520), GUI.skin.box);
            settings.internalHeight = Mathf.RoundToInt(Slider("Resolución interna", settings.internalHeight, 240, 480));
            settings.vertexSnap = Slider("Temblor de vértices", settings.vertexSnap, 0f, 1f);
            settings.affine = Slider("Deformación de texturas", settings.affine, 0f, 1f);
            settings.dither = Slider("Tramado", settings.dither, 0f, 1f);
            settings.colorLevels = Mathf.RoundToInt(Slider("Niveles de color", settings.colorLevels, 8, 64));
            settings.brightness = Slider("Brillo", settings.brightness, 0.5f, 2f);
            settings.fogStart = Slider("Niebla: inicio", settings.fogStart, 0f, 30f);
            settings.fogEnd = Slider("Niebla: fin", settings.fogEnd, 5f, 80f);
            GUILayout.EndArea();
        }
    }
}
