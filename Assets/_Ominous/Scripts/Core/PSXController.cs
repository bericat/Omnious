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

        void Awake()
        {
            // 60 fps con sincronía vertical: sin tearing y sin gastar batería de más en la Deck.
            if (Application.isPlaying) QualitySettings.vSyncCount = 1;
        }

        void OnEnable() => Apply();
        void Update() => Apply();

        public void Apply()
        {
            if (settings == null) return;
            float height = settings.internalHeight;
            float aspect = Screen.height > 0 ? (float)Screen.width / Screen.height : 16f / 10f;
            Shader.SetGlobalVector(SnapRes, new Vector4(height * aspect * 0.5f, height * 0.5f, settings.vertexSnap, 0));
            Shader.SetGlobalVector(Params, new Vector4(settings.affine, settings.fogStart, settings.fogEnd, 0));
            Shader.SetGlobalVector(Post, new Vector4(settings.dither, settings.colorLevels, settings.brightness, 0));
            Shader.SetGlobalColor(Ambient, settings.ambient.linear);
            Shader.SetGlobalColor(FogColor, settings.fogColor.linear);

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
