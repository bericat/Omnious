using UnityEngine;

namespace Ominous
{
    /// <summary>Parpadeo irregular de la tele: luz de la habitación y pantalla.</summary>
    public class TVFlicker : MonoBehaviour
    {
        public Light tvLight;
        public Renderer screen;
        public int screenMaterialIndex;
        public Color colorA = new Color(0.72f, 0.8f, 0.95f);
        public Color colorB = new Color(0.9f, 0.87f, 0.8f);
        public float baseIntensity = 3.0f;
        [Tooltip("Fotogramas del programa (atlas de 4 x 4); 0 = sin programa")] public int programFrames;
        public float programFps = 4f;
        static readonly int BaseMapST = Shader.PropertyToID("_BaseMap_ST");

        static readonly int Emission = Shader.PropertyToID("_EmissionColor");
        MaterialPropertyBlock block;
        float nextShot, shotMix, target = 1f, level = 1f;

        public void TurnOn()
        {
            enabled = true;
            if (tvLight != null) tvLight.enabled = true;
        }

        public void TurnOff()
        {
            enabled = false;
            if (tvLight != null) tvLight.enabled = false;
            if (screen == null) return;
            block ??= new MaterialPropertyBlock();
            screen.GetPropertyBlock(block, screenMaterialIndex);
            block.SetColor(Emission, Color.black);
            screen.SetPropertyBlock(block, screenMaterialIndex);
        }

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
                if (programFrames > 0)
                {
                    // El programa de la tele: teletienda en un atlas de 4 x 4, de izquierda a derecha y de arriba abajo.
                    int i = (int)(Time.time * programFps) % programFrames;
                    int col = i % 4, row = i / 4;
                    block.SetVector(BaseMapST, new Vector4(0.25f, 0.25f, col * 0.25f, 1f - (row + 1) * 0.25f));
                    block.SetColor(Emission, Color.Lerp(Color.white, c, 0.35f).linear * (level * noise * 1.4f));
                }
                else block.SetColor(Emission, c.linear * (level * noise * 1.1f));
                screen.SetPropertyBlock(block, screenMaterialIndex);
            }
        }
    }
}
