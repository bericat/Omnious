using TMPro;
using UnityEditor;
using UnityEngine;
using UnityEngine.TextCore.LowLevel;

namespace Ominous.EditorTools
{
    /// <summary>Fuente de la interfaz: Noto Sans Mono (licencia OFL), de aire sobrio como el texto de una cámara.</summary>
    public static class FontSetup
    {
        const string FontPath = "Assets/_Ominous/Art/Fonts/NotoSansMono-Regular.ttf";
        const string AssetPath = "Assets/_Ominous/Resources/Fuentes/OminousUI.asset";
        const string Characters = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~¡¿áéíóúüñÁÉÍÓÚÜÑ«»…·ºª";

        [MenuItem("Tools/Ominous/Crear fuente")]
        public static void Create()
        {
            AssetDatabase.ImportAsset(FontPath, ImportAssetOptions.ForceSynchronousImport);
            var font = AssetDatabase.LoadAssetAtPath<Font>(FontPath);
            AssetDatabase.DeleteAsset(AssetPath);
            var asset = TMP_FontAsset.CreateFontAsset(font, 64, 6, GlyphRenderMode.SDFAA, 1024, 1024, AtlasPopulationMode.Dynamic);
            asset.name = "OminousUI";
            AssetDatabase.CreateAsset(asset, AssetPath);
            asset.atlasTexture.name = "OminousUI Atlas";
            asset.material.name = "OminousUI Material";
            AssetDatabase.AddObjectToAsset(asset.atlasTexture, asset);
            AssetDatabase.AddObjectToAsset(asset.material, asset);
            asset.TryAddCharacters(Characters, out string missing);
            if (!string.IsNullOrEmpty(missing)) Debug.LogWarning($"Faltan caracteres en la fuente: {missing}");
            EditorUtility.SetDirty(asset);
            AssetDatabase.SaveAssets();
        }
    }
}
