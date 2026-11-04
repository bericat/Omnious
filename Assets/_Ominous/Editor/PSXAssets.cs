
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace Ominous.EditorTools
{
    /// <summary>Paleta común, texturas por script y materiales PSX provisionales.</summary>
    public static class PSXAssets
    {
        const string TexDir = "Assets/_Ominous/Art/Textures";
        const string MatDir = "Assets/_Ominous/Materials/PSX";
        static readonly Dictionary<string, Material> cache = new();

        public static void Clear() => cache.Clear();

        // Ruido de valor periódico: las texturas se repiten sin costuras.
        static float Hash(int x, int y, int seed)
        {
            unchecked
            {
                int h = x * 374761393 + y * 668265263 + seed * 2147483647;
                h = (h ^ (h >> 13)) * 1274126177;
                return ((h ^ (h >> 16)) & 0xFFFF) / 65535f;
            }
        }

        static float Value(float x, float y, int period, int seed)
        {
            int x0 = Mathf.FloorToInt(x), y0 = Mathf.FloorToInt(y);
            float fx = x - x0, fy = y - y0;
            fx = fx * fx * (3f - 2f * fx); fy = fy * fy * (3f - 2f * fy);
            int M(int v) => ((v % period) + period) % period;
            float a = Hash(M(x0), M(y0), seed), b = Hash(M(x0 + 1), M(y0), seed);
            float c = Hash(M(x0), M(y0 + 1), seed), d = Hash(M(x0 + 1), M(y0 + 1), seed);
            return Mathf.Lerp(Mathf.Lerp(a, b, fx), Mathf.Lerp(c, d, fx), fy);
        }

        /// <summary>Ruido fractal periódico en coordenadas 0-1, de 0 a 1.</summary>
        static float Fbm(float u, float v, int cells, int octaves, int seed)
        {
            float sum = 0f, amp = 0.5f, total = 0f;
            for (int i = 0; i < octaves; i++)
            {
                sum += Value(u * cells, v * cells, cells, seed + i * 17) * amp;
                total += amp; amp *= 0.5f; cells *= 2;
            }
            return sum / total;
        }

        static int Seed(string name)
        {
            int s = 7;
            foreach (char c in name) s = s * 31 + c;
            return s & 0xFFFF;
        }

        static Texture2D Texture(string name, int w, int h, System.Func<float, float, Color> pixel)
        {
            var t = new Texture2D(w, h, TextureFormat.RGB24, false);
            for (int y = 0; y < h; y++)
                for (int x = 0; x < w; x++)
                    t.SetPixel(x, y, pixel((x + 0.5f) / w, (y + 0.5f) / h));
            string path = $"{TexDir}/{name}.png";
            File.WriteAllBytes(path, t.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(t);
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
            var imp = (TextureImporter)AssetImporter.GetAtPath(path);
            imp.filterMode = FilterMode.Point;
            imp.mipmapEnabled = false;
            imp.wrapMode = TextureWrapMode.Repeat;
            imp.textureCompression = TextureImporterCompression.Uncompressed;
            imp.maxTextureSize = 256;
            imp.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        static Color Mul(Color c, float v) => new Color(c.r * v, c.g * v, c.b * v);

        /// <summary>Manchas oscuras y parduscas sobre un color base.</summary>
        static Color Stain(Color c, float u, float v, int seed, float amount)
        {
            float big = Mathf.SmoothStep(0.46f, 0.66f, Fbm(u, v, 6, 4, seed));
            float fine = Mathf.SmoothStep(0.25f, 0.75f, Fbm(u, v, 40, 2, seed + 50));
            Color dirty = new Color(c.r * 0.5f, c.g * 0.42f, c.b * 0.34f);
            Color o = Color.Lerp(c, dirty, big * amount);
            return Mul(o, Mathf.Lerp(1f, 0.72f + fine * 0.56f, amount));
        }

        /// <summary>Superficie genérica con suciedad.</summary>
        public static Material Grime(string name, Color color, float amount = 0.6f, float metersPerTile = 1f)
        {
            int seed = Seed(name);
            return Make(name, Texture(name, 128, 128, (u, v) => Stain(color, u, v, seed, amount)), metersPerTile);
        }

        /// <summary>Yeso viejo: manchas, humedad y chorretones verticales.</summary>
        public static Material Plaster(string name, Color color)
        {
            int seed = Seed(name);
            return Make(name, Texture(name, 128, 128, (u, v) =>
            {
                Color c = Stain(color, u, v, seed, 0.6f);
                return c;
            }), 2f);
        }

        public static Material Planks(string name, Color color, int planks, float metersPerTile)
        {
            int seed = Seed(name);
            return Make(name, Texture(name, 128, 128, (u, v) =>
            {
                int row = Mathf.Min(planks - 1, Mathf.FloorToInt(v * planks));
                float tone = 0.8f + 0.4f * Hash(row, 3, seed);
                float grain = Fbm(u * 1f + Hash(row, 8, seed), v * 0.25f, 16, 3, seed + row);
                Color c = Stain(Mul(color, tone * (0.72f + grain * 0.56f)), u, v, seed, 0.55f);
                float vRow = v * planks - row;
                bool seam = planks > 1 && vRow < 0.035f;
                float joint = Mathf.Repeat(u + Hash(row, 5, seed), 1f);
                seam |= planks > 1 && joint < 0.012f;
                return seam ? Mul(c, 0.32f) : c;
            }), metersPerTile);
        }

        public static Material Siding(string name, Color color)
        {
            int seed = Seed(name);
            return Make(name, Texture(name, 128, 128, (u, v) =>
            {
                float board = Mathf.Repeat(v * 8f, 1f);
                Color c = Stain(color, u, v, seed, 0.7f);
                return Mul(c, board < 0.12f ? 0.45f : 0.82f + board * 0.2f);
            }), 2f);
        }

        /// <summary>Tela de trama fina con zonas gastadas.</summary>
        public static Material Fabric(string name, Color color)
        {
            int seed = Seed(name);
            return Make(name, Texture(name, 128, 128, (u, v) =>
            {
                int x = Mathf.FloorToInt(u * 128f), y = Mathf.FloorToInt(v * 128f);
                float weave = (x + y) % 2 == 0 ? 1.06f : 0.9f;
                float worn = Mathf.SmoothStep(0.5f, 0.72f, Fbm(u, v, 4, 3, seed));
                Color c = Mul(Stain(color, u, v, seed, 0.55f), weave);
                return Color.Lerp(c, Mul(c, 1.4f), worn * 0.5f);
            }), 1f);
        }

        public static Material Curtain(string name, Color color)
        {
            int seed = Seed(name);
            return Make(name, Texture(name, 128, 128, (u, v) =>
            {
                float fold = 0.72f + 0.34f * Mathf.Abs(Mathf.Sin(u * Mathf.PI * 6f));
                return Mul(Stain(color, u, v, seed, 0.5f), fold);
            }), 1f);
        }

        public static Material Rug(string name, Color field, Color border, float widthMeters, float depthMeters)
        {
            int seed = Seed(name);
            var tex = Texture(name, 192, 136, (u, v) =>
            {
                float edge = Mathf.Min(Mathf.Min(u, 1f - u) * widthMeters, Mathf.Min(v, 1f - v) * depthMeters);
                Color c = field;
                if (edge < 0.05f) c = Mul(field, 0.5f);
                else if (edge < 0.1f) c = border;
                else if (edge < 0.2f) c = Mathf.Repeat((u * widthMeters + v * depthMeters) * 7f, 1f) < 0.5f ? Mul(field, 0.65f) : Mul(border, 0.7f);
                else if (edge < 0.24f) c = border;
                else
                {
                    float du = Mathf.Abs(u - 0.5f) * widthMeters, dv = Mathf.Abs(v - 0.5f) * depthMeters;
                    float d = du + dv;
                    if (d > 0.45f && d < 0.5f) c = border;
                    else if (d <= 0.45f) c = Mathf.Repeat(d * 9f, 1f) < 0.5f ? Mul(field, 0.6f) : Mul(border, 0.75f);
                }
                return Stain(c, u, v, seed, 0.65f);
            });
            var m = Make(name, tex);
            m.SetTextureScale("_BaseMap", new Vector2(1f / widthMeters, 1f / depthMeters));
            EditorUtility.SetDirty(m);
            return m;
        }

        /// <summary>Imagen borrosa con líneas de barrido, multiplica la emisión de la pantalla.</summary>
        public static Material TvScreen(string name)
        {
            int seed = Seed(name);
            var tex = Texture(name, 64, 48, (u, v) =>
            {
                float image = 0.35f + 0.65f * Fbm(u, v, 3, 3, seed);
                float scan = Mathf.Repeat(v * 24f, 1f) < 0.5f ? 1f : 0.72f;
                return Mul(Color.white, image * scan);
            });
            var m = Make(name, tex);
            m.SetTextureScale("_BaseMap", new Vector2(1f / 0.58f, 1f / 0.42f));
            m.SetColor("_BaseColor", new Color(0.05f, 0.05f, 0.06f));
            m.SetColor("_EmissionColor", new Color(0.3f, 0.4f, 0.6f));
            EditorUtility.SetDirty(m);
            return m;
        }

/// <summary>Cartel «VENDIDA» con letras 5x7.</summary>
        public static Material Sign(string name)
        {
            var font = new Dictionary<char, string[]>
            {
                ['V'] = new[] { "X...X", "X...X", "X...X", "X...X", ".X.X.", ".X.X.", "..X.." },
                ['E'] = new[] { "XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX" },
                ['N'] = new[] { "X...X", "XX..X", "X.X.X", "X.X.X", "X..XX", "X...X", "X...X" },
                ['D'] = new[] { "XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX." },
                ['I'] = new[] { "XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "XXXXX" },
                ['A'] = new[] { ".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X" },
            };
            const string word = "VENDIDA";
            Color paper = new(0.85f, 0.82f, 0.74f), ink = new(0.55f, 0.1f, 0.08f);
            var tex = Texture(name, 64, 16, (u, v) =>
            {
                int x = Mathf.FloorToInt(u * 64f), y = Mathf.FloorToInt(v * 16f);
                int gx = x - 11, gy = 11 - y;
                if (gx >= 0 && gy >= 0 && gy < 7)
                {
                    int i = gx / 6, col = gx % 6;
                    if (i < word.Length && col < 5 && font[word[i]][gy][col] == 'X') return ink;
                }
                return paper;
            });
            return Make(name, tex);
        }

        public static Material Solid(string name, Color color, Color emission = default)
        {
            var tex = Texture(name, 2, 2, (u, v) => color);
            var m = Make(name, tex);
            m.SetColor("_EmissionColor", emission);
            EditorUtility.SetDirty(m);
            return m;
        }

        /// <summary>Suelos, paredes y techos: el temblor PSX los estira al caminar porque son polígonos muy grandes.</summary>
        public static void Stable(params Material[] mats)
        {
            foreach (var m in mats) { m.SetFloat("_Stable", 1f); EditorUtility.SetDirty(m); }
        }

        public static void Exterior(params Material[] mats)
        {
            foreach (var m in mats) { m.SetFloat("_AmbientBoost", 6f); m.SetFloat("_Exterior", 1f); EditorUtility.SetDirty(m); }
        }

        static Material Make(string name, Texture2D tex, float metersPerTile = 1f)
        {
            if (cache.TryGetValue(name, out var existing)) return existing;
            string path = $"{MatDir}/{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                m = new Material(Shader.Find("Ominous/PSX Lit"));
                AssetDatabase.CreateAsset(m, path);
            }
            m.SetTexture("_BaseMap", tex);
            m.SetTextureScale("_BaseMap", Vector2.one / metersPerTile);
            EditorUtility.SetDirty(m);
            cache[name] = m;
            return m;
        }
    }
}
