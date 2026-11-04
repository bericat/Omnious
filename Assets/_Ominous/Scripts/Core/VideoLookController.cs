using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Ominous
{
    /// <summary>Aplica la imagen de cámara doméstica, con pequeñas variaciones de exposición como las de una cámara real.</summary>
    [ExecuteAlways]
    public class VideoLookController : MonoBehaviour
    {
        public VideoLookSettings settings;

        static readonly int Optics = Shader.PropertyToID("_Video_Optics");
        static readonly int Signal = Shader.PropertyToID("_Video_Signal");
        static readonly int Grade = Shader.PropertyToID("_Video_Grade");
        static readonly int ShadowTint = Shader.PropertyToID("_Video_ShadowTint");
        static readonly int LightTint = Shader.PropertyToID("_Video_LightTint");
        static readonly int Ambient = Shader.PropertyToID("_Video_Ambient");
        static readonly int FogColor = Shader.PropertyToID("_Video_FogColor");
        static readonly int Fog = Shader.PropertyToID("_Video_Fog");
        static readonly int ExteriorFogColor = Shader.PropertyToID("_Video_ExteriorFogColor");
        static readonly int ExteriorFog = Shader.PropertyToID("_Video_ExteriorFog");

        float nextImperfection, imperfection;

        void Awake()
        {
            if (!Application.isPlaying) return;
            QualitySettings.vSyncCount = 1;
            // Copia en ejecución: los ajustes del jugador no tocan el asset del proyecto.
            if (settings != null) settings = Instantiate(settings);
            nextImperfection = Time.unscaledTime + 20f;
        }

        void OnEnable() => Apply();
        void Update() => Apply();

        public void Apply()
        {
            if (settings == null) return;
            float i = OminousOptions.CameraEffectIntensity;
            float time = Time.unscaledTime;

            // Pequeñas imperfecciones ocasionales: la cámara duda un instante, sin glitches ni líneas.
            if (Application.isPlaying && time >= nextImperfection)
            {
                imperfection = Random.Range(0.5f, 1f);
                nextImperfection = time + Random.Range(settings.imperfectionEvery.x, settings.imperfectionEvery.y);
            }
            imperfection = Mathf.MoveTowards(imperfection, 0f, Time.unscaledDeltaTime * 2.2f);

            float drift = (Mathf.PerlinNoise(time * 0.31f, 3.1f) - 0.5f) * 2f + (Mathf.PerlinNoise(time * 2.3f, 7.7f) - 0.5f) * 0.5f;
            float exposure = settings.brightness * OminousOptions.Brightness * (1f + drift * settings.exposureDrift * i - imperfection * 0.04f * i);

            Shader.SetGlobalVector(Optics, new Vector4(settings.distortion * i, settings.aberration * i, settings.softness * i, settings.vignette * i));
            Shader.SetGlobalVector(Signal, new Vector4(settings.noise * i, exposure, time, imperfection * i));
            Shader.SetGlobalVector(Grade, new Vector4(settings.liftedBlacks * i, Mathf.Lerp(1f, settings.dirtyWhites, i), Mathf.Lerp(1f, settings.saturation, i), settings.contrast));
            Shader.SetGlobalColor(ShadowTint, Color.Lerp(Color.white, settings.shadowTint, i));
            Shader.SetGlobalColor(LightTint, Color.Lerp(Color.white, settings.lightTint, i));
            Shader.SetGlobalColor(Ambient, settings.ambient.linear);
            Shader.SetGlobalColor(FogColor, settings.fogColor.linear);
            Shader.SetGlobalVector(Fog, new Vector4(settings.fogStart, settings.fogEnd, 0, 0));
            Shader.SetGlobalColor(ExteriorFogColor, settings.exteriorFogColor.linear);
            Shader.SetGlobalVector(ExteriorFog, new Vector4(settings.exteriorFogStart, settings.exteriorFogEnd, 0, 0));
            var cam = Camera.main;
            if (cam != null) cam.backgroundColor = settings.exteriorFogColor;

            var pipeline = UniversalRenderPipeline.asset;
            if (pipeline != null && Screen.height > 0)
            {
                // Resolución moderadamente baja con filtrado suave: imagen blanda, sin píxeles marcados.
                float height = Mathf.Lerp(Screen.height, settings.internalHeight, i);
                float scale = Mathf.Clamp(height / Screen.height, 0.1f, 2f);
                if (!Mathf.Approximately(pipeline.renderScale, scale)) pipeline.renderScale = scale;
                if (pipeline.upscalingFilter != UpscalingFilterSelection.Linear) pipeline.upscalingFilter = UpscalingFilterSelection.Linear;
            }
        }
    }
}
