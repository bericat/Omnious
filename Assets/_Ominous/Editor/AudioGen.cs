using System;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace Ominous.EditorTools
{
    /// <summary>Sonido ambiente sintetizado por script: se puede regenerar y no depende de bancos externos.</summary>
    public static class AudioGen
    {
        const string Dir = "Assets/_Ominous/Audio";
        const int Rate = 22050;

        static AudioClip Save(string name, float[] samples, AudioImporterFormat? _ = null)
        {
            string path = $"{Dir}/{name}.wav";
            using (var w = new BinaryWriter(File.Create(path)))
            {
                int bytes = samples.Length * 2;
                w.Write("RIFF".ToCharArray()); w.Write(36 + bytes); w.Write("WAVEfmt ".ToCharArray());
                w.Write(16); w.Write((short)1); w.Write((short)1); w.Write(Rate); w.Write(Rate * 2); w.Write((short)2); w.Write((short)16);
                w.Write("data".ToCharArray()); w.Write(bytes);
                foreach (float s in samples) w.Write((short)(Mathf.Clamp(s, -1f, 1f) * 32000f));
            }
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
            return AssetDatabase.LoadAssetAtPath<AudioClip>(path);
        }

        /// <summary>Hace que el final empalme con el principio.</summary>
        static float[] Loopable(float[] s, int fade)
        {
            var o = new float[s.Length - fade];
            Array.Copy(s, o, o.Length);
            for (int i = 0; i < fade; i++)
            {
                float t = (float)i / fade;
                o[i] = s[i] * t + s[s.Length - fade + i] * (1f - t);
            }
            return o;
        }

        public static AudioClip Fridge()
        {
            var r = new System.Random(11);
            var s = new float[Rate * 8];
            float low = 0f;
            for (int i = 0; i < s.Length; i++)
            {
                float t = (float)i / Rate;
                low += (((float)r.NextDouble() * 2f - 1f) - low) * 0.03f;
                float wobble = 1f + 0.08f * Mathf.Sin(t * 2f * Mathf.PI * 0.25f);
                s[i] = (Mathf.Sin(t * 2f * Mathf.PI * 100f) * 0.22f + Mathf.Sin(t * 2f * Mathf.PI * 200f) * 0.1f + Mathf.Sin(t * 2f * Mathf.PI * 300f) * 0.03f) * wobble + low * 0.5f;
            }
            return Save("Nevera", Loopable(s, Rate / 2));
        }

        public static AudioClip Clock()
        {
            var r = new System.Random(23);
            var s = new float[Rate * 2];
            for (int tick = 0; tick < 2; tick++)
            {
                int start = tick * Rate;
                float tone = tick == 0 ? 2300f : 1900f;
                for (int i = 0; i < 900; i++)
                {
                    float t = (float)i / Rate;
                    float env = Mathf.Exp(-t * 320f);
                    s[start + i] += (Mathf.Sin(t * 2f * Mathf.PI * tone) * 0.5f + ((float)r.NextDouble() * 2f - 1f) * 0.5f) * env * 0.5f;
                }
            }
            return Save("Reloj", s);
        }

        public static AudioClip Wind()
        {
            var r = new System.Random(37);
            var s = new float[Rate * 16];
            float low = 0f, lower = 0f;
            for (int i = 0; i < s.Length; i++)
            {
                float t = (float)i / Rate;
                float gust = 0.45f + 0.55f * Mathf.PerlinNoise(t * 0.28f, 3.1f);
                low += (((float)r.NextDouble() * 2f - 1f) - low) * (0.012f + 0.02f * gust);
                lower += (low - lower) * 0.08f;
                s[i] = (low - lower * 0.6f) * gust * 2.4f;
            }
            return Save("Viento", Loopable(s, Rate));
        }

        public static AudioClip Car()
        {
            var r = new System.Random(5);
            var s = new float[Rate * 7];
            float low = 0f;
            for (int i = 0; i < s.Length; i++)
            {
                float t = (float)i / s.Length;
                float env = Mathf.Pow(Mathf.Sin(t * Mathf.PI), 2.4f);
                float time = (float)i / Rate;
                low += (((float)r.NextDouble() * 2f - 1f) - low) * (0.03f + env * 0.05f);
                float engine = Mathf.Sin(time * 2f * Mathf.PI * Mathf.Lerp(82f, 64f, t)) * 0.2f;
                s[i] = (low * 1.6f + engine) * env;
            }
            return Save("CocheLejano", s);
        }

        public static AudioClip TvMurmur()
        {
            var r = new System.Random(61);
            var s = new float[Rate * 14];
            float a = 0f, b = 0f;
            for (int i = 0; i < s.Length; i++)
            {
                float t = (float)i / Rate;
                float n = (float)r.NextDouble() * 2f - 1f;
                a += (n - a) * 0.18f;
                b += (a - b) * 0.08f;
                // Sílabas: una voz que no se entiende, con pausas.
                float syllable = Mathf.SmoothStep(0.46f, 0.62f, Mathf.PerlinNoise(t * 3.7f, 8.8f));
                float phrase = Mathf.SmoothStep(0.3f, 0.5f, Mathf.PerlinNoise(t * 0.4f, 1.2f));
                s[i] = (a - b) * syllable * phrase * 3.2f;
            }
            return Save("TeleMurmullo", Loopable(s, Rate));
        }
    }
}
