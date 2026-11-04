using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Ominous
{
    /// <summary>Aplica los ajustes PSX al render, también en el editor.</summary>
    [ExecuteAlways]
    public class PSXController : MonoBehaviour
    {
        public PSXSettings settings;

        static readonly int SnapRes = Shader.PropertyToID("_PSX_SnapRes");
        static readonly int Params = Shader.PropertyToID("_PSX_Params");
        static readonly int Post = Shader.PropertyToID("_PSX_Post");
        static readonly int Ambient = Shader.PropertyToID("_PSX_Ambient");
        static readonly int FogColor = Shader.PropertyToID("_PSX_FogColor");
        static readonly int ExteriorFogColor = Shader.PropertyToID("_PSX_ExteriorFogColor");
        static readonly int ExteriorFog = Shader.PropertyToID("_PSX_ExteriorFog");
        static readonly int Grade = Shader.PropertyToID("_PSX_Grade");

        void Awake()
        {
            // 60 fps con sincronía vertical: sin tearing y sin gastar batería de más en la Deck.
            if (!Application.isPlaying) return;
            QualitySettings.vSyncCount = 1;
            // Copia en ejecución: los ajustes del jugador no tocan el asset del proyecto.
            if (settings != null) settings = Instantiate(settings);
        }

        void OnEnable() => Apply();
        void Update() => Apply();

        public void Apply()
        {
            if (settings == null) return;
            float intensity = OminousOptions.PsxIntensity;
            float height = Mathf.Lerp(480f, settings.internalHeight, intensity);
            float aspect = Screen.height > 0 ? (float)Screen.width / Screen.height : 16f / 10f;
            Shader.SetGlobalVector(SnapRes, new Vector4(height * aspect * 0.5f, height * 0.5f, settings.vertexSnap * intensity, 0));
            Shader.SetGlobalVector(Params, new Vector4(settings.affine * intensity, settings.fogStart, settings.fogEnd, 0));
            Shader.SetGlobalVector(Post, new Vector4(settings.dither * intensity, Mathf.Lerp(48f, settings.colorLevels, intensity), settings.brightness * OminousOptions.Brightness, 0));
            Shader.SetGlobalColor(Ambient, settings.ambient.linear);
            Shader.SetGlobalColor(FogColor, settings.fogColor.linear);
            Shader.SetGlobalColor(ExteriorFogColor, settings.exteriorFogColor.linear);
            Shader.SetGlobalVector(ExteriorFog, new Vector4(settings.exteriorFogStart, settings.exteriorFogEnd, 0, 0));
            Shader.SetGlobalVector(Grade, new Vector4(settings.contrast, settings.saturation, settings.shadowTint, 0));
            var cam = Camera.main;
            if (cam != null) cam.backgroundColor = settings.exteriorFogColor;

            var pipeline = UniversalRenderPipeline.asset;
            if (pipeline != null && Screen.height > 0)
            {
                float scale = Mathf.Clamp(height / Screen.height, 0.1f, 2f);
                if (!Mathf.Approximately(pipeline.renderScale, scale)) pipeline.renderScale = scale;
                if (pipeline.upscalingFilter != UpscalingFilterSelection.Point) pipeline.upscalingFilter = UpscalingFilterSelection.Point;
            }
        }
    }
}
