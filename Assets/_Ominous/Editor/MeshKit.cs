using System.Collections.Generic;
using UnityEngine;

namespace Ominous.EditorTools
{
    /// <summary>Monta mallas de pocos polígonos con UV en metros, una submalla por material.</summary>
    public class MeshKit
    {
        readonly List<Vector3> vertices = new();
        readonly List<Vector3> normals = new();
        readonly List<Vector2> uvs = new();
        readonly List<Material> materials = new();
        readonly List<List<int>> triangles = new();

        List<int> Sub(Material m)
        {
            int i = materials.IndexOf(m);
            if (i >= 0) return triangles[i];
            materials.Add(m);
            var list = new List<int>();
            triangles.Add(list);
            return list;
        }

        void Quad(Vector3 c, Vector3 u, Vector3 v, Vector3 n, Material m, float uvScale)
        {
            var tris = Sub(m);
            int s = vertices.Count;
            vertices.Add(c - u - v); vertices.Add(c - u + v); vertices.Add(c + u + v); vertices.Add(c + u - v);
            for (int i = 0; i < 4; i++) normals.Add(n);
            float a = u.magnitude * 2f * uvScale, b = v.magnitude * 2f * uvScale;
            uvs.Add(new Vector2(0, 0)); uvs.Add(new Vector2(0, b)); uvs.Add(new Vector2(a, b)); uvs.Add(new Vector2(a, 0));
            tris.AddRange(new[] { s, s + 1, s + 2, s, s + 2, s + 3 });
        }

        /// <summary>Caja por centro y tamaño en metros.</summary>
        public MeshKit Box(Vector3 center, Vector3 size, Material m, float uvScale = 1f)
        {
            Vector3 h = size * 0.5f;
            Vector3 x = new(h.x, 0, 0), y = new(0, h.y, 0), z = new(0, 0, h.z);
            Quad(center + x, z, y, Vector3.right, m, uvScale);
            Quad(center - x, -z, y, Vector3.left, m, uvScale);
            Quad(center + y, x, z, Vector3.up, m, uvScale);
            Quad(center - y, -x, z, Vector3.down, m, uvScale);
            Quad(center + z, -x, y, Vector3.forward, m, uvScale);
            Quad(center - z, x, y, Vector3.back, m, uvScale);
            return this;
        }

        /// <summary>Cilindro o cono truncado apoyado en <paramref name="baseCenter"/>.</summary>
        public MeshKit Cylinder(Vector3 baseCenter, float radiusBottom, float radiusTop, float height, int sides, Material m)
        {
            var tris = Sub(m);
            Vector3 top = baseCenter + Vector3.up * height;
            for (int i = 0; i < sides; i++)
            {
                float a0 = i * Mathf.PI * 2f / sides, a1 = (i + 1) * Mathf.PI * 2f / sides;
                Vector3 d0 = new(Mathf.Cos(a0), 0, Mathf.Sin(a0)), d1 = new(Mathf.Cos(a1), 0, Mathf.Sin(a1));
                int s = vertices.Count;
                vertices.Add(baseCenter + d0 * radiusBottom); vertices.Add(top + d0 * radiusTop);
                vertices.Add(top + d1 * radiusTop); vertices.Add(baseCenter + d1 * radiusBottom);
                Vector3 n = ((d0 + d1).normalized + Vector3.up * ((radiusBottom - radiusTop) / Mathf.Max(height, 0.01f))).normalized;
                for (int k = 0; k < 4; k++) normals.Add(n);
                uvs.Add(new Vector2(i, 0)); uvs.Add(new Vector2(i, height)); uvs.Add(new Vector2(i + 1, height)); uvs.Add(new Vector2(i + 1, 0));
                tris.AddRange(new[] { s, s + 1, s + 2, s, s + 2, s + 3 });
                if (radiusTop > 0.001f)
                {
                    int t = vertices.Count;
                    vertices.Add(top); vertices.Add(top + d1 * radiusTop); vertices.Add(top + d0 * radiusTop);
                    for (int k = 0; k < 3; k++) { normals.Add(Vector3.up); uvs.Add(Vector2.zero); }
                    tris.AddRange(new[] { t, t + 1, t + 2 });
                }
            }
            return this;
        }

        public Mesh Build(string name, out Material[] mats)
        {
            var mesh = new Mesh { name = name };
            mesh.SetVertices(vertices);
            mesh.SetNormals(normals);
            mesh.SetUVs(0, uvs);
            mesh.subMeshCount = triangles.Count;
            for (int i = 0; i < triangles.Count; i++) mesh.SetTriangles(triangles[i], i);
            mesh.RecalculateBounds();
            mats = materials.ToArray();
            return mesh;
        }
    }
}
