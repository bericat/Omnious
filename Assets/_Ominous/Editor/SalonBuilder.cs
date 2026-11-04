using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine;

namespace Ominous.EditorTools
{
    /// <summary>
    /// Construye Test_Salon desde cero: muebles provisionales como prefabs, estancia y calle.
    /// Coordenadas en metros: x hacia el este, z hacia el norte; la calle queda al sur.
    /// El salón ocupa x 0-5, z 0-4.4, altura 2.6 (ver Docs/Diseno/plano.svg).
    /// </summary>
    public static partial class SalonBuilder
    {
        const string ScenePath = "Assets/_Ominous/Scenes/Test_Salon.unity";
        const float Height = 2.6f, Thick = 0.12f;
        const int ExteriorLayer = 8;
        const int ExteriorMask = 1 << ExteriorLayer;

        static Material wall, floorWood, ceiling, woodDark, woodLight, sofa, cushion, rug, plastic, screen, frame, curtain,
            glass, metal, shade, frameExt, doorExt, metalExt, asphalt, concrete, grass, siding, sidingFar, roof, trunk, leaves, lampGlow, sign, windowLit, door, blanket;

        static void Materials()
        {
            ProceduralAssets.Clear();
            wall = ProceduralAssets.Plaster("Pared", new Color(0.6f, 0.59f, 0.49f));
            floorWood = ProceduralAssets.Planks("SueloMadera", new Color(0.38f, 0.28f, 0.18f), 5, 1.6f);
            ceiling = ProceduralAssets.Plaster("Techo", new Color(0.66f, 0.65f, 0.58f));
            woodDark = ProceduralAssets.Planks("MaderaOscura", new Color(0.27f, 0.16f, 0.09f), 1, 0.8f);
            woodLight = ProceduralAssets.Planks("MaderaClara", new Color(0.5f, 0.34f, 0.2f), 1, 0.8f);
            sofa = ProceduralAssets.Fabric("TelaSofa", new Color(0.3f, 0.33f, 0.26f));
            cushion = ProceduralAssets.Fabric("TelaCojin", new Color(0.36f, 0.38f, 0.3f));
            rug = ProceduralAssets.Rug("Alfombra", new Color(0.34f, 0.2f, 0.16f), new Color(0.56f, 0.5f, 0.38f), 2.4f, 1.7f);
            blanket = ProceduralAssets.Fabric("Manta", new Color(0.2f, 0.27f, 0.36f));
            curtain = ProceduralAssets.Curtain("Cortina", new Color(0.56f, 0.45f, 0.3f));
            plastic = ProceduralAssets.Grime("Plastico", new Color(0.1f, 0.1f, 0.1f), 0.4f);
            screen = ProceduralAssets.TvScreen("PantallaTele");
            frame = ProceduralAssets.Grime("Marco", new Color(0.72f, 0.69f, 0.6f), 0.5f);
            door = ProceduralAssets.Planks("Puerta", new Color(0.44f, 0.3f, 0.2f), 1, 1f);
            metal = ProceduralAssets.Grime("Metal", new Color(0.24f, 0.24f, 0.25f), 0.6f);
            shade = ProceduralAssets.Fabric("Pantalla", new Color(0.66f, 0.56f, 0.38f));
            asphalt = ProceduralAssets.Grime("Asfalto", new Color(0.17f, 0.17f, 0.18f), 0.8f, 3f);
            concrete = ProceduralAssets.Grime("Acera", new Color(0.4f, 0.39f, 0.36f), 0.7f, 2f);
            grass = ProceduralAssets.Grime("Cesped", new Color(0.15f, 0.22f, 0.1f), 0.9f, 3f);
            siding = ProceduralAssets.Siding("Fachada", new Color(0.52f, 0.52f, 0.47f));
            sidingFar = ProceduralAssets.Siding("FachadaVecinos", new Color(0.38f, 0.36f, 0.33f));
            roof = ProceduralAssets.Grime("Tejado", new Color(0.16f, 0.13f, 0.13f), 0.7f, 2f);
            trunk = ProceduralAssets.Grime("Tronco", new Color(0.2f, 0.13f, 0.08f), 0.8f);
            leaves = ProceduralAssets.Grime("Hojas", new Color(0.09f, 0.15f, 0.07f), 0.9f, 2f);
            lampGlow = ProceduralAssets.Solid("Farola", new Color(0.1f, 0.1f, 0.1f), new Color(1f, 0.75f, 0.42f));
            windowLit = ProceduralAssets.Solid("VentanaOscura", new Color(0.02f, 0.025f, 0.035f));
            sign = ProceduralAssets.Sign("CartelVendida");
            frameExt = ProceduralAssets.Grime("MarcoExterior", new Color(0.6f, 0.58f, 0.52f), 0.5f);
            doorExt = ProceduralAssets.Planks("PuertaExterior", new Color(0.3f, 0.22f, 0.16f), 1, 1f);
            metalExt = ProceduralAssets.Grime("MetalExterior", new Color(0.24f, 0.24f, 0.25f), 0.6f);
            ProceduralAssets.Exterior(asphalt, concrete, grass, siding, sidingFar, roof, trunk, leaves, sign, windowLit, lampGlow, frameExt, doorExt, metalExt);
            ProceduralAssets.Sheen(0.14f, woodLight, woodDark);
            ProceduralAssets.Sheen(0.3f, plastic);
            ProceduralAssets.Sheen(0.08f, floorWood, door);
            glass = ProceduralAssets.Glass("Cristal");
            wall.SetFloat("_RoomAO", 1f);
            EditorUtility.SetDirty(wall);
        }

        // ---------- utilidades ----------

        static GameObject Instance(string name, MeshKit kit, Transform parent, Vector3 position, float yaw = 0f, bool collider = true)
        {
            var mesh = kit.Build(name, out var mats);
            // Segundo juego de UV para hornear la luz.
            Unwrapping.GenerateSecondaryUVSet(mesh);
            string meshPath = $"Assets/_Ominous/Art/Meshes/{name}.asset";
            AssetDatabase.DeleteAsset(meshPath);
            AssetDatabase.CreateAsset(mesh, meshPath);
            var go = new GameObject(name);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterials = mats;
            if (collider)
            {
                var box = go.AddComponent<BoxCollider>();
                box.center = mesh.bounds.center;
                box.size = mesh.bounds.size;
            }
            string prefabPath = $"Assets/_Ominous/Prefabs/{name}.prefab";
            var prefab = PrefabUtility.SaveAsPrefabAsset(go, prefabPath);
            Object.DestroyImmediate(go);
            var inst = (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
            inst.transform.SetPositionAndRotation(position, Quaternion.Euler(0, yaw, 0));
            return inst;
        }

        struct Opening { public float from, to, sill, top; public Opening(float f, float t, float s, float tp) { from = f; to = t; sill = s; top = tp; } }

        /// <summary>Pared con huecos. Recorre x (alongX) o z desde <paramref name="start"/> durante <paramref name="length"/>.</summary>
        static void Wall(MeshKit kit, Vector3 start, float length, bool alongX, Material m, params Opening[] openings) => Wall(kit, start, length, alongX, m, Thick, openings);

        static void Wall(MeshKit kit, Vector3 start, float length, bool alongX, Material m, float thick, Opening[] openings)
        {
            void Piece(float a, float b, float y0, float y1)
            {
                if (b - a <= 0.001f || y1 - y0 <= 0.001f) return;
                float mid = (a + b) * 0.5f;
                Vector3 c = start + (alongX ? Vector3.right : Vector3.forward) * mid + Vector3.up * ((y0 + y1) * 0.5f);
                Vector3 size = alongX ? new Vector3(b - a, y1 - y0, thick) : new Vector3(thick, y1 - y0, b - a);
                kit.Box(c, size, m);
            }
            float cursor = 0f;
            foreach (var o in openings)
            {
                Piece(cursor, o.from, 0, Height);
                Piece(o.from, o.to, 0, o.sill);
                Piece(o.from, o.to, o.top, Height);
                cursor = o.to;
            }
            Piece(cursor, length, 0, Height);
        }

        /// <summary>Marco y cortinas de una ventana.</summary>
        static void WindowDressing(MeshKit kit, Vector3 center, float width, float height, bool alongX, float inward)
        {
            const float bar = 0.05f, depth = 0.16f;
            Vector3 along = alongX ? Vector3.right : Vector3.forward;
            Vector3 normal = alongX ? Vector3.forward : Vector3.right;
            Vector3 H(float w, float h, float d) => alongX ? new Vector3(w, h, d) : new Vector3(d, h, w);
            kit.Box(center + Vector3.up * (height * 0.5f), H(width + bar * 2, bar, depth), frame);
            kit.Box(center - Vector3.up * (height * 0.5f), H(width + bar * 2, bar, depth + 0.08f), frame);
            kit.Box(center + along * (width * 0.5f), H(bar, height, depth), frame);
            kit.Box(center - along * (width * 0.5f), H(bar, height, depth), frame);
            kit.Box(center, H(0.03f, height, 0.03f), frame);
            kit.Box(center, H(width, 0.03f, 0.03f), frame);
            kit.Box(center - normal * (inward * 0.01f), H(width, height, 0.005f), glass);
            Vector3 inner = normal * (inward * 0.14f);
            kit.Box(center + inner + along * (width * 0.5f + 0.02f) - Vector3.up * 0.1f, H(0.28f, height + 0.25f, 0.05f), curtain);
            kit.Box(center + inner - along * (width * 0.5f + 0.02f) - Vector3.up * 0.1f, H(0.28f, height + 0.25f, 0.05f), curtain);
            kit.Box(center + inner + Vector3.up * (height * 0.5f + 0.1f), H(width + 0.7f, 0.03f, 0.03f), metal);
        }

        static void Blocker(Transform parent, Vector3 center, Vector3 size)
        {
            var b = new GameObject("BloqueoVentana");
            b.transform.SetParent(parent);
            var c = b.AddComponent<BoxCollider>();
            c.center = center;
            c.size = size;
        }

        // ---------- muebles (origen en el suelo, frente hacia +z) ----------

        static MeshKit Sofa()
        {
            var k = new MeshKit();
            k.Box(new Vector3(0, 0.26f, 0), new Vector3(2.0f, 0.24f, 0.86f), sofa);
            k.Box(new Vector3(0, 0.6f, -0.34f), new Vector3(2.0f, 0.68f, 0.2f), sofa);
            k.Box(new Vector3(-0.91f, 0.42f, 0), new Vector3(0.18f, 0.4f, 0.86f), sofa);
            k.Box(new Vector3(0.91f, 0.42f, 0), new Vector3(0.18f, 0.4f, 0.86f), sofa);
            for (int i = -1; i <= 1; i++)
            {
                k.Box(new Vector3(i * 0.55f, 0.43f, 0.06f), new Vector3(0.53f, 0.11f, 0.62f), cushion);
                k.Box(new Vector3(i * 0.55f, 0.67f, -0.2f), new Vector3(0.53f, 0.38f, 0.1f), cushion);
            }
            foreach (float x in new[] { -0.9f, 0.9f })
                foreach (float z in new[] { -0.36f, 0.36f })
                    k.Box(new Vector3(x, 0.07f, z), new Vector3(0.07f, 0.14f, 0.07f), woodDark);
            return k;
        }

        static MeshKit Tele()
        {
            // El frente mira a -z: la tele está contra la pared norte.
            var k = new MeshKit();
            k.Box(new Vector3(0, 0.26f, 0), new Vector3(1.2f, 0.5f, 0.46f), woodDark);
            k.Box(new Vector3(0, 0.26f, -0.232f), new Vector3(1.08f, 0.4f, 0.01f), woodLight);
            k.Box(new Vector3(0, 0.77f, 0.02f), new Vector3(0.76f, 0.54f, 0.5f), plastic);
            k.Box(new Vector3(0, 0.78f, -0.235f), new Vector3(0.58f, 0.42f, 0.015f), screen);
            k.Box(new Vector3(0.31f, 0.59f, -0.235f), new Vector3(0.05f, 0.03f, 0.015f), metal);
            return k;
        }

        static MeshKit MesaBaja()
        {
            var k = new MeshKit();
            k.Box(new Vector3(0, 0.4f, 0), new Vector3(1.0f, 0.04f, 0.55f), woodLight);
            k.Box(new Vector3(0, 0.15f, 0), new Vector3(0.88f, 0.025f, 0.45f), woodLight);
            foreach (float x in new[] { -0.45f, 0.45f })
                foreach (float z in new[] { -0.22f, 0.22f })
                    k.Box(new Vector3(x, 0.19f, z), new Vector3(0.05f, 0.38f, 0.05f), woodDark);
            k.Box(new Vector3(0.22f, 0.435f, 0.05f), new Vector3(0.16f, 0.03f, 0.05f), plastic);
            return k;
        }

        static MeshKit Estanteria()
        {
            var k = new MeshKit();
            const float w = 1.0f, h = 1.9f, d = 0.3f;
            k.Box(new Vector3(-w * 0.5f, h * 0.5f, 0), new Vector3(0.03f, h, d), woodDark);
            k.Box(new Vector3(w * 0.5f, h * 0.5f, 0), new Vector3(0.03f, h, d), woodDark);
            k.Box(new Vector3(0, h * 0.5f, d * 0.5f - 0.01f), new Vector3(w, h, 0.02f), woodDark);
            for (int i = 0; i <= 4; i++) k.Box(new Vector3(0, 0.02f + i * 0.465f, 0), new Vector3(w, 0.03f, d), woodLight);
            var rng = new System.Random(7);
            Material[] covers = { sofa, rug, blanket, plastic, cushion };
            for (int shelf = 0; shelf < 4; shelf++)
            {
                float x = -0.44f;
                while (x < 0.3f)
                {
                    float bw = 0.03f + (float)rng.NextDouble() * 0.04f, bh = 0.2f + (float)rng.NextDouble() * 0.12f;
                    k.Box(new Vector3(x + bw * 0.5f, 0.035f + shelf * 0.465f + bh * 0.5f, -0.01f), new Vector3(bw, bh, 0.18f), covers[rng.Next(covers.Length)]);
                    x += bw + 0.002f + (rng.NextDouble() < 0.18 ? 0.14f : 0f);
                }
            }
            return k;
        }

        static MeshKit Lampara()
        {
            var k = new MeshKit();
            k.Cylinder(Vector3.zero, 0.15f, 0.13f, 0.03f, 8, metal);
            k.Cylinder(new Vector3(0, 0.03f, 0), 0.012f, 0.012f, 1.42f, 6, metal);
            k.Cylinder(new Vector3(0, 1.4f, 0), 0.23f, 0.13f, 0.26f, 8, shade);
            return k;
        }

        static MeshKit Alfombra() => new MeshKit().Box(new Vector3(0, 0.006f, 0), new Vector3(2.4f, 0.012f, 1.7f), rug);

        static MeshKit Manta()
        {
            var k = new MeshKit();
            k.Box(new Vector3(0, 0.495f, 0.05f), new Vector3(0.52f, 0.015f, 0.66f), blanket);
            k.Box(new Vector3(0, 0.3f, 0.385f), new Vector3(0.52f, 0.39f, 0.015f), blanket);
            return k;
        }

        static MeshKit PuertaInterior()
        {
            var k = PuertaMarco();
            k.Box(new Vector3(0, 1.0f, 0), new Vector3(0.04f, 2.0f, 0.86f), door);
            k.Box(new Vector3(-0.05f, 0.95f, -0.34f), new Vector3(0.05f, 0.03f, 0.1f), metal);
            return k;
        }

        static MeshKit PuertaMarco()
        {
            var k = new MeshKit();
            k.Box(new Vector3(0, 2.03f, 0), new Vector3(0.16f, 0.06f, 1.0f), frame);
            k.Box(new Vector3(0, 1.0f, 0.46f), new Vector3(0.16f, 2.0f, 0.06f), frame);
            k.Box(new Vector3(0, 1.0f, -0.46f), new Vector3(0.16f, 2.0f, 0.06f), frame);
            return k;
        }

        static MeshKit Farola()
        {
            var k = new MeshKit();
            k.Cylinder(Vector3.zero, 0.08f, 0.05f, 4.6f, 6, metalExt);
            k.Box(new Vector3(0, 4.6f, 0.45f), new Vector3(0.06f, 0.06f, 0.9f), metalExt);
            k.Box(new Vector3(0, 4.53f, 0.85f), new Vector3(0.22f, 0.08f, 0.4f), lampGlow);
            return k;
        }

        static MeshKit Arbol()
        {
            var k = new MeshKit();
            k.Cylinder(Vector3.zero, 0.2f, 0.13f, 2.6f, 6, trunk);
            k.Cylinder(new Vector3(0, 2.1f, 0), 1.7f, 0.9f, 1.9f, 7, leaves);
            k.Cylinder(new Vector3(0, 4.0f, 0), 1.2f, 0.01f, 1.8f, 7, leaves);
            return k;
        }

        static MeshKit CasaFachada(Material facade, bool chechu)
        {
            // Decorado de bajo detalle: fachada hacia +z, origen en el centro del frente.
            var k = new MeshKit();
            const float w = 8f, h = 2.9f, d = 7f;
            k.Box(new Vector3(0, h * 0.5f, -d * 0.5f), new Vector3(w, h, d), facade);
            // Tejado a dos aguas simplificado en dos escalones.
            k.Box(new Vector3(0, h + 0.2f, -d * 0.5f), new Vector3(w + 0.6f, 0.4f, d + 0.6f), roof);
            k.Box(new Vector3(0, h + 0.6f, -d * 0.5f), new Vector3(w - 0.8f, 0.4f, d - 1.4f), roof);
            k.Box(new Vector3(0, h + 0.95f, -d * 0.5f), new Vector3(w - 2.2f, 0.3f, d - 3.6f), roof);
            foreach (float x in new[] { -2.6f, 2.4f })
            {
                k.Box(new Vector3(x, 1.5f, 0.01f), new Vector3(1.4f, 1.15f, 0.02f), windowLit);
                k.Box(new Vector3(x, 2.1f, 0.03f), new Vector3(1.5f, 0.06f, 0.05f), frameExt);
                k.Box(new Vector3(x, 0.92f, 0.03f), new Vector3(1.5f, 0.06f, 0.05f), frameExt);
            }
            k.Box(new Vector3(0, 1.0f, 0.02f), new Vector3(0.95f, 2.05f, 0.04f), doorExt);
            k.Box(new Vector3(0, 0.1f, 0.8f), new Vector3(2.4f, 0.2f, 1.6f), concrete);
            if (chechu)
            {
                k.Cylinder(new Vector3(2f, 0, 3.2f), 0.03f, 0.03f, 1.05f, 4, metalExt);
                k.Box(new Vector3(2f, 1.0f, 3.22f), new Vector3(0.75f, 0.28f, 0.02f), sign);
            }
            return k;
        }

        // ---------- escena ----------

        [MenuItem("Tools/Ominous/Construir salón de pruebas")]
        public static void Build()
        {
            OminousSetup.Configure();
            Materials();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var room = new GameObject("Salon").transform;
            var props = new GameObject("Muebles").transform;
            props.SetParent(room);
            var street = new GameObject("Calle").transform;
            var lights = new GameObject("Luces").transform;

            // Estancia
            var shell = new MeshKit();
            shell.Box(new Vector3(2.5f, -0.05f, 2.2f), new Vector3(5.24f, 0.1f, 4.64f), floorWood);
            shell.Box(new Vector3(2.5f, Height + 0.05f, 2.2f), new Vector3(5.24f, 0.1f, 4.64f), ceiling);
            Wall(shell, new Vector3(0, 0, 0), 5f, true, wall, new Opening(0.9f, 2.3f, 0.9f, 2.1f), new Opening(3.0f, 4.4f, 0.9f, 2.1f));
            Wall(shell, new Vector3(0, 0, 4.4f), 5f, true, wall);
            Wall(shell, new Vector3(0, 0, 0), 4.4f, false, wall, new Opening(1.8f, 3.2f, 0.9f, 2.1f));
            Wall(shell, new Vector3(5, 0, 0), 4.4f, false, wall, new Opening(2.1f, 3.0f, 0f, 2.0f));
            foreach (var (x, z, along, w) in new[] { (1.6f, 0f, true, 1.4f), (3.7f, 0f, true, 1.4f), (0f, 2.5f, false, 1.4f) })
                WindowDressing(shell, new Vector3(x, 1.5f, z), w, 1.2f, along, 1f);
            // Rodapié
            shell.Box(new Vector3(2.5f, 0.05f, 4.33f), new Vector3(4.88f, 0.1f, 0.02f), woodDark);
            shell.Box(new Vector3(0.45f, 0.05f, 0.07f), new Vector3(0.78f, 0.1f, 0.02f), woodDark);
            shell.Box(new Vector3(2.65f, 0.05f, 0.07f), new Vector3(0.7f, 0.1f, 0.02f), woodDark);
            shell.Box(new Vector3(4.7f, 0.05f, 0.07f), new Vector3(0.48f, 0.1f, 0.02f), woodDark);
            var shellGo = Instance("Salon_Estructura", shell, room, Vector3.zero, 0, false);
            shellGo.AddComponent<MeshCollider>();
            GameObjectUtility.SetStaticEditorFlags(shellGo, StaticEditorFlags.BatchingStatic);

            // Bloqueos invisibles en las ventanas
            Blocker(room.transform, new Vector3(1.6f, 1.3f, 0f), new Vector3(1.4f, 2.6f, 0.2f));
            Blocker(room.transform, new Vector3(3.7f, 1.3f, 0f), new Vector3(1.4f, 2.6f, 0.2f));
            Blocker(room.transform, new Vector3(0f, 1.3f, 2.5f), new Vector3(0.2f, 2.6f, 1.4f));

            // Muebles, a escala real y con espacio para andar
            Instance("Alfombra", Alfombra(), props, new Vector3(2.15f, 0, 2.45f), 0, false);
            Instance("Sofa", Sofa(), props, new Vector3(2.15f, 0, 1.45f));
            Instance("Manta", Manta(), props, new Vector3(1.6f, 0, 1.45f), 0, false);
            var tele = Instance("Tele", Tele(), props, new Vector3(2.15f, 0, 4.08f));
            Instance("MesaBaja", MesaBaja(), props, new Vector3(2.15f, 0, 2.75f));
            Instance("Estanteria", Estanteria(), props, new Vector3(4.2f, 0, 4.17f));
            Instance("Lampara", Lampara(), props, new Vector3(0.4f, 0, 0.5f));
            Instance("PuertaInterior", PuertaInterior(), props, new Vector3(5f, 0, 2.55f));

            // Calle: decorado de bajo detalle con niebla
            var ground = new MeshKit();
            ground.Box(new Vector3(4, -0.1f, -1.25f), new Vector3(50, 0.1f, 2.5f), grass);
            ground.Box(new Vector3(4, -0.04f, -2.75f), new Vector3(50, 0.1f, 0.5f), concrete);
            ground.Box(new Vector3(4, -0.1f, -4.3f), new Vector3(50, 0.1f, 2.6f), asphalt);
            ground.Box(new Vector3(4, -0.04f, -5.85f), new Vector3(50, 0.1f, 0.5f), concrete);
            ground.Box(new Vector3(4, -0.1f, -14f), new Vector3(50, 0.1f, 15.8f), grass);
            ground.Box(new Vector3(4, -0.1f, 16f), new Vector3(50, 0.1f, 26f), grass);
            ground.Box(new Vector3(-13.5f, -0.1f, 2.2f), new Vector3(15f, 0.1f, 4.6f), grass);
            Instance("Calle_Suelo", ground, street, Vector3.zero, 0, false);
            Instance("CasaChechu", CasaFachada(siding, true), street, new Vector3(7f, 0, -9.6f));
            Instance("CasaVecinos", CasaFachada(sidingFar, false), street, new Vector3(-5f, 0, -9.6f));
            var v2 = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Ominous/Prefabs/CasaVecinos.prefab"), street);
            v2.transform.position = new Vector3(19f, 0, -9.6f);
            Instance("Farola", Farola(), street, new Vector3(2f, 0, -2.6f));
            var f2 = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Ominous/Prefabs/Farola.prefab"), street);
            f2.transform.SetPositionAndRotation(new Vector3(13f, 0, -6.1f), Quaternion.Euler(0, 180, 0));
            Instance("Arbol", Arbol(), street, new Vector3(-1.6f, 0, -1.2f));
            var t2 = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Ominous/Prefabs/Arbol.prefab"), street);
            t2.transform.position = new Vector3(1.5f, 0, -7.5f);

            foreach (var t in street.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = ExteriorLayer;

            // Luces de noche: la tele es la fuente principal; la farola entra por la ventana
            var tvLight = SpotLight("LuzTele", lights, new Vector3(2.15f, 0.8f, 3.8f), Quaternion.Euler(4, 180, 0), new Color(0.72f, 0.8f, 0.95f), 3.0f, 8f, 150f, ~ExteriorMask);
            tvLight.shadows = LightShadows.Soft;
            tvLight.shadowStrength = 0.9f;
            // Resplandor de la tele en la pared de detrás y a los lados.
            var tvFill = Point("LuzTeleResplandor", lights, new Vector3(2.15f, 1.0f, 3.65f), new Color(0.72f, 0.8f, 0.95f), 0.5f, 4.5f);
            tvFill.cullingMask = ~ExteriorMask;
            SpotLight("LuzFarola", lights, new Vector3(2.2f, 4.4f, -1.8f), Quaternion.Euler(90, 0, 0), new Color(1f, 0.72f, 0.42f), 30f, 10f, 120f, ExteriorMask);
            var windowLight = SpotLight("LuzFarolaVentana", lights, new Vector3(2.0f, 3.3f, -1.5f), Quaternion.LookRotation(new Vector3(1.9f, 0f, 2.5f) - new Vector3(2.0f, 3.3f, -1.5f)), new Color(1f, 0.74f, 0.46f), 7f, 8.5f, 62f, ~ExteriorMask);
            windowLight.shadows = LightShadows.Soft;
            SpotLight("LuzFarolaLejana", lights, new Vector3(13f, 4.4f, -5.2f), Quaternion.Euler(90, 0, 0), new Color(1f, 0.72f, 0.42f), 30f, 10f, 120f, ExteriorMask);
            // Bombilla cálida de la lámpara: sombra no, para no gastar seis mapas de sombra de un punto.
            var lamp = Point("LuzLampara", lights, new Vector3(0.45f, 1.5f, 0.55f), new Color(1f, 0.72f, 0.42f), 1.8f, 5.5f);
            lamp.cullingMask = ~ExteriorMask;
            var flicker = tele.AddComponent<TVFlicker>();
            flicker.tvLight = tvLight;
            flicker.screen = tele.GetComponent<MeshRenderer>();
            var mats = flicker.screen.sharedMaterials;
            flicker.screenMaterialIndex = System.Array.IndexOf(mats, screen);

            // Jugador
            var player = new GameObject("Jugador");
            player.transform.SetPositionAndRotation(new Vector3(4.2f, 0.02f, 2.6f), Quaternion.Euler(0, 270, 0));
            var cc = player.AddComponent<CharacterController>();
            cc.height = 1.7f; cc.radius = 0.25f; cc.center = new Vector3(0, 0.85f, 0); cc.stepOffset = 0.2f; cc.skinWidth = 0.02f;
            var fp = player.AddComponent<FirstPersonController>();
            var camGo = new GameObject("Camara");
            camGo.tag = "MainCamera";
            camGo.transform.SetParent(player.transform);
            camGo.transform.localPosition = new Vector3(0, 1.6f, 0);
            var cam = camGo.AddComponent<Camera>();
            cam.clearFlags = CameraClearFlags.SolidColor;
            var settings = AssetDatabase.LoadAssetAtPath<VideoLookSettings>(OminousSetup.SettingsPath);
            cam.backgroundColor = settings.exteriorFogColor;
            cam.fieldOfView = 62f;
            cam.nearClipPlane = 0.05f;
            cam.farClipPlane = 80f;
            camGo.AddComponent<AudioListener>();
            var data = cam.GetUniversalAdditionalCameraData();
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.None;
            fp.cameraPivot = camGo.transform;

            // Control de la imagen
            var psx = new GameObject("Imagen");
            var controller = psx.AddComponent<VideoLookController>();
            controller.settings = settings;
            var volume = psx.AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = OminousSetup.BuildVolumeProfile();
            psx.AddComponent<VideoLookPanel>().controller = controller;

            RenderSettings.skybox = null;
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = Color.black;
            RenderSettings.fog = false;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;

            EditorSceneManager.SaveScene(scene, ScenePath);
                        AssetDatabase.SaveAssets();
            Debug.Log("Salón de pruebas construido");
        }

        static Light Point(string name, Transform parent, Vector3 pos, Color c, float intensity, float range)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent);
            go.transform.position = pos;
            var l = go.AddComponent<Light>();
            l.type = LightType.Point; l.color = c; l.intensity = intensity; l.range = range; l.shadows = LightShadows.None;
            return l;
        }

        static Light SpotLight(string name, Transform parent, Vector3 pos, Quaternion rot, Color c, float intensity, float range, float angle, int mask)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent);
            go.transform.SetPositionAndRotation(pos, rot);
            var l = go.AddComponent<Light>();
            l.type = LightType.Spot; l.color = c; l.intensity = intensity; l.range = range; l.spotAngle = angle; l.shadows = LightShadows.None; l.cullingMask = mask;
            return l;
        }
    }
}
