using UnityEngine;

namespace Ominous
{
    /// <summary>Panel único de ajustes de la imagen de cámara doméstica.</summary>
    [CreateAssetMenu(menuName = "Ominous/Ajustes de imagen")]
    public class VideoLookSettings : ScriptableObject
    {
        [Header("Resolución y óptica")]
        [Range(360, 800)] public int internalHeight = 600;
        [Range(0f, 0.4f)] public float distortion = 0.1f;
        [Range(0f, 0.02f)] public float aberration = 0.006f;
        [Range(0f, 2f)] public float softness = 0.55f;
        [Range(0f, 0.6f)] public float vignette = 0.28f;

        [Header("Señal")]
        [Range(0f, 0.1f)] public float noise = 0.055f;
        [Range(0f, 0.08f)] public float exposureDrift = 0.02f;
        [Tooltip("Segundos entre pequeñas imperfecciones momentáneas")]
        public Vector2 imperfectionEvery = new(25f, 70f);

        [Header("Color")]
        [Range(0f, 0.1f)] public float liftedBlacks = 0.035f;
        [Range(0.7f, 1f)] public float dirtyWhites = 0.93f;
        [Range(0f, 1.2f)] public float saturation = 0.72f;
        [Range(0.7f, 1.5f)] public float contrast = 1.05f;
        [Range(0.5f, 2f)] public float brightness = 1.15f;
        public Color shadowTint = new(1f, 1.04f, 0.8f);
        public Color lightTint = new(1.06f, 0.98f, 0.72f);

        [Header("Iluminación y niebla")]
        public Color ambient = new(0.2f, 0.2f, 0.17f);
        public Color fogColor = new(0.025f, 0.028f, 0.018f);
        [Range(0f, 30f)] public float fogStart = 14f;
        [Range(5f, 80f)] public float fogEnd = 50f;
        public Color exteriorFogColor = new(0.08f, 0.1f, 0.055f); // oliva, como la referencia de Toni
        [Range(0f, 15f)] public float exteriorFogStart = 1f;
        [Range(5f, 60f)] public float exteriorFogEnd = 18f;
    }
}
