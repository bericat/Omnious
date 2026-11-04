using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Ominous.EditorTools
{
    /// <summary>Deja URP preparado para la imagen de cámara doméstica en la Steam Deck.</summary>
    public static class OminousSetup
    {
        public const string SettingsPath = "Assets/_Ominous/Data/VideoLook.asset";
        const string RendererPath = "Assets/Settings/PC_Renderer.asset";
        const string VolumePath = "Assets/_Ominous/Data/VideoVolume.asset";
        const string PipelinePath = "Assets/Settings/PC_RPAsset.asset";
        const string PostMatPath = "Assets/_Ominous/Materials/Video/VideoPost.mat";

        [MenuItem("Tools/Ominous/Configurar imagen")]
        public static void Configure()
        {
            var settings = AssetDatabase.LoadAssetAtPath<VideoLookSettings>(SettingsPath);
            if (settings == null)
            {
                settings = ScriptableObject.CreateInstance<VideoLookSettings>();
                AssetDatabase.CreateAsset(settings, SettingsPath);
            }

            var tags = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
            tags.FindProperty("layers").GetArrayElementAtIndex(8).stringValue = "Exterior";
            tags.ApplyModifiedProperties();

            var post = AssetDatabase.LoadAssetAtPath<Material>(PostMatPath);
            if (post == null)
            {
                post = new Material(Shader.Find("Hidden/Ominous/Video Post"));
                AssetDatabase.CreateAsset(post, PostMatPath);
            }

            var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(PipelinePath);
            var so = new SerializedObject(pipeline);
            so.FindProperty("m_SupportsHDR").boolValue = false;
            so.FindProperty("m_MSAA").intValue = 1;
            so.FindProperty("m_MainLightShadowsSupported").boolValue = false;
            so.FindProperty("m_AdditionalLightShadowsSupported").boolValue = true;
            so.FindProperty("m_AdditionalLightsShadowmapResolution").intValue = 1024;
            so.FindProperty("m_SoftShadowsSupported").boolValue = true;
            so.FindProperty("m_SoftShadowQuality").intValue = 1;
            so.FindProperty("m_AdditionalLightsRenderingMode").intValue = 1;
            so.FindProperty("m_UpscalingFilter").intValue = (int)UpscalingFilterSelection.Linear;
            so.ApplyModifiedProperties();
            EditorUtility.SetDirty(pipeline);

            var data = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(RendererPath);
            // Forward+: una casa con muchas luces sin el límite por objeto; no respeta las máscaras de luz.
            data.renderingMode = RenderingMode.ForwardPlus;
            foreach (var f in data.rendererFeatures.Where(f => f != null && !(f is FullScreenPassRendererFeature))) f.SetActive(false);

            var feature = data.rendererFeatures.OfType<FullScreenPassRendererFeature>().FirstOrDefault();
            if (feature == null)
            {
                feature = ScriptableObject.CreateInstance<FullScreenPassRendererFeature>();
                feature.name = "VideoPost";
                AssetDatabase.AddObjectToAsset(feature, data);
                data.rendererFeatures.Add(feature);
                AssetDatabase.TryGetGUIDAndLocalFileIdentifier(feature, out string _, out long id);
                var map = new SerializedObject(data).FindProperty("m_RendererFeatureMap");
                map.arraySize++;
                map.GetArrayElementAtIndex(map.arraySize - 1).longValue = id;
                map.serializedObject.ApplyModifiedProperties();
            }
            feature.passMaterial = post;
            feature.injectionPoint = FullScreenPassRendererFeature.InjectionPoint.AfterRenderingPostProcessing;
            feature.fetchColorBuffer = true;
            feature.SetActive(true);
            EditorUtility.SetDirty(feature);
            EditorUtility.SetDirty(data);
            BuildVolumeProfile();
            AssetDatabase.SaveAssets();
        }

        /// <summary>Solo el bloom de URP: el resto va en la pasada propia, más barata en la Deck.</summary>
        public static VolumeProfile BuildVolumeProfile()
        {
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(VolumePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                AssetDatabase.CreateAsset(profile, VolumePath);
            }
            if (!profile.TryGet<Bloom>(out var bloom))
            {
                bloom = profile.Add<Bloom>(true);
                AssetDatabase.AddObjectToAsset(bloom, profile);
            }
            bloom.threshold.Override(0.8f);
            bloom.intensity.Override(0.5f);
            bloom.scatter.Override(0.62f);
            bloom.highQualityFiltering.Override(false);
            EditorUtility.SetDirty(bloom);
            EditorUtility.SetDirty(profile);
            return profile;
        }
    }
}
