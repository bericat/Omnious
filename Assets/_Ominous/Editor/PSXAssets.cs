using System;
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

        static Texture2D Texture(string name, int w, int h, Func<int, int, System.Random, Color> pixel)
        {
            var rng = new System.Random(name.GetHashCode() & 0xFFFF);
            var t = new Texture2D(w, h, TextureFormat.RGB24, false);
            for (int y = 0; y < h; y++)
                for (int x = 0; x < w; x++)
                    t.SetPixel(x, y, pixel(x, y, rng));
            string path = $"{TexDir}/{name}.png";
            File.WriteAllBytes(path, t.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(t);
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
            var imp = (TextureImporter)AssetImporter.GetAtPath(path);
            imp.filterMode = FilterMode.Point;
            imp.mipmapEnabled = false;
            imp.wrapMode = TextureWrapMode.Repeat;
            imp.textureCompression = TextureImporterCompression.Uncompressed;
            imp.maxTextureSize = 128;
            imp.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        static Color Vary(Color c, System.Random r, float amount)
        {
            float v = 1f + ((float)r.NextDouble() - 0.5f) * amount;
            return new Color(c.r * v, c.g * v, c.b * v);
        }

        public static Material Noise(string name, Color color, float amount = 0.18f, float metersPerTile = 1f)
            => Make(name, Texture(name, 32, 32, (x, y, r) => Vary(color, r, amount)), metersPerTile);

        public static Material Planks(string name, Color color, int planks = 4)
            => Make(name, Texture(name, 64, 64, (x, y, r) =>
            {
                int row = y * planks / 64;
                float tone = 0.86f + 0.2f * Mathf.PerlinNoise(row * 3.1f, 0.5f);
                bool seam = y % (64 / planks) == 0 || (x + row * 23) % 58 == 0;
                float grain = 0.92f + 0.14f * Mathf.PerlinNoise(x * 0.12f + row * 7f, y * 0.8f);
                return seam ? color * 0.45f : Vary(color * tone * grain, r, 0.06f);
            }));

        public static Material Siding(string name, Color color)
            => Make(name, Texture(name, 32, 32, (x, y, r) => y % 8 == 0 ? color * 0.55f : Vary(color, r, 0.08f)));

        public static Material Fabric(string name, Color color)
            => Make(name, Texture(name, 32, 32, (x, y, r) => Vary(color, r, 0.16f)));

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
            var tex = Texture(name, 64, 16, (x, y, r) =>
            {
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
            var tex = Texture(name, 2, 2, (x, y, r) => color);
            var m = Make(name, tex);
            m.SetColor("_EmissionColor", emission);
            EditorUtility.SetDirty(m);
            return m;
        }

        public static void Exterior(params Material[] mats)
        {
            foreach (var m in mats) { m.SetFloat("_AmbientBoost", 6f); EditorUtility.SetDirty(m); }
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
