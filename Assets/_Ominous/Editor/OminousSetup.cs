using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Ominous.EditorTools
{
    /// <summary>Deja URP preparado para el estilo PSX en la Steam Deck.</summary>
    public static class OminousSetup
    {
        public const string SettingsPath = "Assets/_Ominous/Data/PSXSettings.asset";
        const string RendererPath = "Assets/Settings/PC_Renderer.asset";
        const string PipelinePath = "Assets/Settings/PC_RPAsset.asset";
        const string PostMatPath = "Assets/_Ominous/Materials/PSX/PSXPost.mat";

        [MenuItem("Tools/Ominous/Configurar PSX")]
        public static void Configure()
        {
            var settings = AssetDatabase.LoadAssetAtPath<PSXSettings>(SettingsPath);
            if (settings == null)
            {
                settings = ScriptableObject.CreateInstance<PSXSettings>();
                AssetDatabase.CreateAsset(settings, SettingsPath);
            }

            var tags = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
            tags.FindProperty("layers").GetArrayElementAtIndex(8).stringValue = "Exterior";
            tags.ApplyModifiedProperties();

            var post = AssetDatabase.LoadAssetAtPath<Material>(PostMatPath);
            if (post == null)
            {
                post = new Material(Shader.Find("Hidden/Ominous/PSX Post"));
                AssetDatabase.CreateAsset(post, PostMatPath);
            }

            var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(PipelinePath);
            var so = new SerializedObject(pipeline);
            so.FindProperty("m_SupportsHDR").boolValue = false;
            so.FindProperty("m_MSAA").intValue = 1;
            so.FindProperty("m_MainLightShadowsSupported").boolValue = false;
            so.FindProperty("m_AdditionalLightShadowsSupported").boolValue = false;
            so.FindProperty("m_AdditionalLightsRenderingMode").intValue = 1;
            so.FindProperty("m_UpscalingFilter").intValue = (int)UpscalingFilterSelection.Point;
            so.ApplyModifiedProperties();
            EditorUtility.SetDirty(pipeline);

            var data = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(RendererPath);
            data.renderingMode = RenderingMode.Forward;
            foreach (var f in data.rendererFeatures.Where(f => f != null && !(f is FullScreenPassRendererFeature))) f.SetActive(false);

            var feature = data.rendererFeatures.OfType<FullScreenPassRendererFeature>().FirstOrDefault();
            if (feature == null)
            {
                feature = ScriptableObject.CreateInstance<FullScreenPassRendererFeature>();
                feature.name = "PSXPost";
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
            AssetDatabase.SaveAssets();
        }
    }
}
