using UnityEngine;

namespace Ominous
{
    /// <summary>
    /// Linterna de Chevas (OSCURIDAD.md): F la enciende y la apaga; con el clic derecho mantenido la tapa con la mano,
    /// deja una luz rojiza mínima y deja de verse desde fuera. No gasta pilas.
    /// </summary>
    public class Flashlight : MonoBehaviour
    {
        public const string Flag = "linterna";
        public static Flashlight Instance { get; private set; }

        public Light beam;
        public bool IsOn { get; private set; }
        public bool IsCovered { get; private set; }

        /// <summary>Cuánto se ve a Chevas por su linterna: 1 encendida, casi 0 tapada o apagada.</summary>
        public float Exposure => !IsOn ? 0f : IsCovered ? 0.05f : 1f;

        static readonly Color Warm = new(1f, 0.9f, 0.72f);
        static readonly Color Covered = new(0.55f, 0.08f, 0.04f);

        public static bool Owned => GameDirector.Instance != null && GameDirector.Instance.Night.flags.Contains(Flag);

        void Awake()
        {
            Instance = this;
            if (beam == null) beam = Build();
            beam.enabled = false;
            if (System.Array.IndexOf(System.Environment.GetCommandLineArgs(), "-linterna") >= 0) { Give(); Invoke(nameof(TurnOnForTest), 1f); }
        }

        void OnDestroy() { if (Instance == this) Instance = null; }

        void TurnOnForTest() => Set(true);

        public static void Give()
        {
            if (GameDirector.Instance != null && !GameDirector.Instance.Night.flags.Contains(Flag))
                GameDirector.Instance.Night.flags.Add(Flag);
        }

        Light Build()
        {
            var go = new GameObject("Linterna");
            go.transform.SetParent(transform, false);
            go.transform.localPosition = new Vector3(0.18f, -0.22f, 0.1f);
            var l = go.AddComponent<Light>();
            l.type = LightType.Spot;
            l.range = 8f;
            l.spotAngle = 52f;
            l.innerSpotAngle = 18f;
            l.intensity = 2.6f;
            l.color = Warm;
            l.shadows = LightShadows.Hard;
            l.shadowResolution = UnityEngine.Rendering.LightShadowResolution.Low;
            l.cookie = Cookie();
            return l;
        }

        /// <summary>Haz irregular de linterna barata: centro brillante, un anillo y bordes sucios.</summary>
        static Texture2D Cookie()
        {
            const int n = 64;
            var t = new Texture2D(n, n, TextureFormat.R8, false) { wrapMode = TextureWrapMode.Clamp, name = "LinternaCookie" };
            for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    float u = (x + 0.5f) / n - 0.5f, v = (y + 0.5f) / n - 0.5f;
                    float r = Mathf.Sqrt(u * u + v * v) * 2f;
                    float core = Mathf.Clamp01(1f - r * 1.1f);
                    float ring = Mathf.Exp(-Mathf.Pow((r - 0.62f) * 9f, 2f)) * 0.35f;
                    float dirt = Mathf.Lerp(0.8f, 1f, Mathf.PerlinNoise(x * 0.3f, y * 0.3f));
                    float edge = r < 0.95f ? 1f : 0f;
                    float c = Mathf.Clamp01((core * core * 0.9f + ring + 0.12f) * dirt) * edge;
                    t.SetPixel(x, y, new Color(c, c, c, c));
                }
            t.Apply();
            return t;
        }

        void Update()
        {
            if (!Owned || FirstPersonController.InputBlocked && !IsOn) { if (beam.enabled && !Owned) Set(false); return; }
            if (GameInput.FlashlightPressed && !PauseMenu.IsPaused)
            {
                Sfx.Play("linterna", transform.position);
                Set(!IsOn);
            }
            bool cover = IsOn && GameInput.CoverHeld && !PauseMenu.IsPaused;
            if (cover != IsCovered)
            {
                IsCovered = cover;
                if (cover) Sfx.Play("linterna_tapar", transform.position);
            }
            if (!IsOn) return;
            beam.color = IsCovered ? Covered : Warm;
            beam.intensity = IsCovered ? 0.13f : 2.6f;
            beam.range = IsCovered ? 2f : 8f;
            beam.shadows = IsCovered ? LightShadows.None : LightShadows.Hard;
        }

        public void Set(bool on)
        {
            IsOn = on;
            beam.enabled = on;
            if (!on) IsCovered = false;
        }
    }
}
