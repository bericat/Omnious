using UnityEngine;

namespace Ominous
{
    /// <summary>Parpadeo irregular de la tele: luz de la habitación y pantalla.</summary>
    public class TVFlicker : MonoBehaviour
    {
        public Light tvLight;
        public Renderer screen;
        public int screenMaterialIndex;
        public Color colorA = new Color(0.55f, 0.7f, 1f);
        public Color colorB = new Color(0.9f, 0.85f, 0.75f);
        public float baseIntensity = 2.4f;

        static readonly int Emission = Shader.PropertyToID("_EmissionColor");
        MaterialPropertyBlock block;
        float nextShot, shotMix, target = 1f, level = 1f;

        void Update()
        {
            if (Time.time >= nextShot)
            {
                nextShot = Time.time + Random.Range(0.4f, 3.5f);
                shotMix = Random.value;
                target = Random.Range(0.55f, 1.15f);
            }
            level = Mathf.Lerp(level, target, Time.deltaTime * 12f);
            float noise = Mathf.PerlinNoise(Time.time * 7f, 0.3f) * 0.2f + 0.9f;
            Color c = Color.Lerp(colorA, colorB, shotMix);
            if (tvLight != null)
            {
                tvLight.color = c;
                tvLight.intensity = baseIntensity * level * noise;
            }
            if (screen != null)
            {
                block ??= new MaterialPropertyBlock();
                screen.GetPropertyBlock(block, screenMaterialIndex);
                block.SetColor(Emission, c.linear * (level * noise * 1.1f));
                screen.SetPropertyBlock(block, screenMaterialIndex);
            }
        }
    }
}
