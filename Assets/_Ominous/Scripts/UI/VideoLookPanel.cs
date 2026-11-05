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
        float logSeconds, logTime, logWorst; int logFrames; float started = -1f, tourTime; int tourIndex; bool tour;
        // Vistas para medir el rendimiento recorriendo toda la casa, sin nadie a los mandos.
        static readonly (float x, float z, float yaw)[] TourStops =
        {
            (6f, 1.1f, 0f), (4.3f, 2.6f, 270f), (1.5f, 1.2f, 40f), (6f, 5.2f, 90f), (13f, 5.2f, 270f), (9f, 3.7f, 125f), (13.3f, 3.8f, 220f),
            (5f, 6.8f, 300f), (1f, 6.6f, 45f), (8.4f, 6.5f, 0f), (12f, 6.6f, 345f), (14.7f, 3.2f, 110f), (9f, -4.3f, 340f),
        };

        void Start()
        {
            // Medición sin pantalla de por medio: ./Ominous -fpslog 30 escribe en Player.log y sale.
            var args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, "-fpslog");
            if (i >= 0 && i + 1 < args.Length) float.TryParse(args[i + 1], out logSeconds);
            tour = System.Array.IndexOf(args, "-recorrido") >= 0;
            if (System.Array.IndexOf(args, "-todasluces") >= 0)
                foreach (var s in FindObjectsByType<LightSwitch>(FindObjectsSortMode.None))
                    if (!s.isOn) s.Interact();
        }

        void Update()
        {
            float dt = Time.unscaledDeltaTime;
            if (logSeconds > 0f && Time.realtimeSinceStartup > 8f)
            {
                if (started < 0f) started = Time.realtimeSinceStartup;
                logTime += dt; logFrames++; logWorst = Mathf.Max(logWorst, dt);
                tourTime += dt;
                if (tour && tourTime > 1.5f)
                {
                    tourTime = 0f;
                    var stop = TourStops[tourIndex++ % TourStops.Length];
                    FindAnyObjectByType<FirstPersonController>()?.Teleport(new Vector3(stop.x, 0.02f, stop.z), stop.yaw);
                }
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
            if (!open || settings == null) return;
            GUI.Label(new Rect(8, 4, 500, 26), $"{1f / smooth:0} fps · peor {worst * 1000f:0} ms", style);
            GUILayout.BeginArea(new Rect(8, 32, 340, 620), GUI.skin.box);
            settings.internalHeight = Mathf.RoundToInt(Slider("Resolución interna", settings.internalHeight, 360, 800));
            settings.softness = Slider("Suavizado", settings.softness, 0f, 2f);
            settings.painterly = Slider("Aspecto pintado", settings.painterly, 0f, 1f);
            settings.sharpen = Slider("Afilado", settings.sharpen, 0f, 2.5f);
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
