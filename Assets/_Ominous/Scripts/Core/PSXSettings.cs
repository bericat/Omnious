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
        [Range(0f, 1f)] public float dither = 0.9f;
        [Range(8, 64)] public int colorLevels = 32;
        [Range(0.5f, 2f)] public float brightness = 1.15f;
        public Color ambient = new Color(0.05f, 0.055f, 0.08f);
        public Color fogColor = new Color(0.012f, 0.016f, 0.028f);
        [Range(0f, 30f)] public float fogStart = 12f;
        [Range(5f, 80f)] public float fogEnd = 48f;
    }
}
