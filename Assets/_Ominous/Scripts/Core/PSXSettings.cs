using UnityEngine;

namespace Ominous
{
    /// <summary>Panel único de ajustes del efecto PSX.</summary>
    [CreateAssetMenu(menuName = "Ominous/Ajustes PSX")]
    public class PSXSettings : ScriptableObject
    {
        [Range(240, 480)] public int internalHeight = 360;
        [Range(0f, 1f)] public float vertexSnap = 0.7f;
        [Range(0f, 1f)] public float affine = 0.3f;
        [Range(0f, 1f)] public float dither = 1f;
        [Range(6, 64)] public int colorLevels = 12;
        [Range(0.5f, 2f)] public float brightness = 1.1f;
        [Range(0.8f, 2f)] public float contrast = 1.2f;
        [Range(0f, 1.2f)] public float saturation = 0.8f;
        [Range(0f, 1f)] public float shadowTint = 0.7f;
        public Color ambient = new Color(0.05f, 0.05f, 0.065f);
        public Color fogColor = new Color(0.012f, 0.016f, 0.028f);
        [Range(0f, 30f)] public float fogStart = 12f;
        [Range(5f, 80f)] public float fogEnd = 48f;
        public Color exteriorFogColor = new Color(0.14f, 0.16f, 0.19f);
        [Range(0f, 15f)] public float exteriorFogStart = 2f;
        [Range(5f, 60f)] public float exteriorFogEnd = 21f;
    }
}
