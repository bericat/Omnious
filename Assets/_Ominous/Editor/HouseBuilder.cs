using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Yarn.Unity;

namespace Ominous.EditorTools
{
    /// <summary>
    /// Casa completa según Docs/Diseno/plano.svg. x hacia el este, z hacia el norte (z = 10 - y del plano), calle al sur.
    /// </summary>
    public static partial class SalonBuilder
    {
        const string HousePath = "Assets/_Ominous/Scenes/House.unity";
        const string LightingPath = "Assets/_Ominous/Data/LightingHouse.lighting";
        static Material tileWall, tileFloor, linoleum, concreteIn, ceramic, chrome, mirror, carRed, carBlue, carGrey, tire, carGlass, tireIn, carGlassIn, fenceWood, paintA, paintB, pillow, sheet, paper, fridge, appliance, countertop, grime;

        static void HouseMaterials()
        {
            tileWall = ProceduralAssets.Tile("AzulejoPared", new Color(0.72f, 0.74f, 0.68f), 7, 1f);
            tileFloor = ProceduralAssets.Tile("AzulejoSuelo", new Color(0.46f, 0.48f, 0.46f), 4, 1.2f);
            linoleum = ProceduralAssets.Checker("Linoleo", new Color(0.52f, 0.5f, 0.42f), new Color(0.36f, 0.36f, 0.3f), 2.4f);
            concreteIn = ProceduralAssets.Grime("Hormigon", new Color(0.4f, 0.39f, 0.36f), 0.8f, 2f);
            ceramic = ProceduralAssets.Grime("Ceramica", new Color(0.78f, 0.78f, 0.72f), 0.25f, 1f);
            chrome = ProceduralAssets.Grime("Cromo", new Color(0.55f, 0.56f, 0.56f), 0.3f, 1f);
            mirror = ProceduralAssets.Grime("Espejo", new Color(0.52f, 0.56f, 0.56f), 0.2f, 1f);
            carRed = ProceduralAssets.Grime("CocheRojo", new Color(0.32f, 0.11f, 0.09f), 0.4f);
            carBlue = ProceduralAssets.Grime("CocheAzul", new Color(0.14f, 0.2f, 0.28f), 0.4f);
            carGrey = ProceduralAssets.Grime("CocheGris", new Color(0.36f, 0.37f, 0.36f), 0.4f);
            tire = ProceduralAssets.Grime("Rueda", new Color(0.05f, 0.05f, 0.05f), 0.3f);
            carGlass = ProceduralAssets.Grime("CristalCoche", new Color(0.06f, 0.08f, 0.09f), 0.1f);
            tireIn = ProceduralAssets.Grime("RuedaGaraje", new Color(0.05f, 0.05f, 0.05f), 0.3f);
            carGlassIn = ProceduralAssets.Grime("CristalCocheGaraje", new Color(0.07f, 0.09f, 0.1f), 0.1f);
            fenceWood = ProceduralAssets.Planks("Valla", new Color(0.24f, 0.17f, 0.11f), 1, 1f);
            paintA = ProceduralAssets.Painting("CuadroA", new Color(0.42f, 0.44f, 0.32f), new Color(0.6f, 0.52f, 0.36f));
            paintB = ProceduralAssets.Painting("CuadroB", new Color(0.26f, 0.32f, 0.38f), new Color(0.58f, 0.58f, 0.5f));
            pillow = ProceduralAssets.Fabric("Almohada", new Color(0.7f, 0.69f, 0.62f));
            sheet = ProceduralAssets.Fabric("Colcha", new Color(0.34f, 0.3f, 0.34f));
            paper = ProceduralAssets.Grime("Papel", new Color(0.72f, 0.7f, 0.62f), 0.3f);
            fridge = ProceduralAssets.Grime("Nevera", new Color(0.7f, 0.7f, 0.65f), 0.35f);
            appliance = ProceduralAssets.Grime("Electrodomestico", new Color(0.62f, 0.62f, 0.58f), 0.45f);
            countertop = ProceduralAssets.Grime("Encimera", new Color(0.5f, 0.47f, 0.4f), 0.5f);
            grime = ProceduralAssets.Grime("Baldosa", new Color(0.42f, 0.44f, 0.42f), 0.6f);
            ProceduralAssets.Sheen(0.35f, ceramic, tileWall, fridge, appliance);
            ProceduralAssets.Sheen(0.6f, chrome, mirror);
            ProceduralAssets.Sheen(0.2f, tileFloor, linoleum, countertop);
            ProceduralAssets.Exterior(carBlue, carGrey, tire, carGlass, fenceWood);
        }

        const float DoorTop = 2.0f;

        static void Static(GameObject go, bool lightmapped = true)
        {
            GameObjectUtility.SetStaticEditorFlags(go, lightmapped ? StaticEditorFlags.ContributeGI | StaticEditorFlags.BatchingStatic : StaticEditorFlags.BatchingStatic);
        }

        static GameObject Put(string name, MeshKit kit, Transform parent, float x, float z, float yaw = 0f, bool collider = true, float y = 0f)
        {
            var go = Instance(name, kit, parent, new Vector3(x, y, z), yaw, collider);
            Static(go);
            return go;
        }

        /// <summary>
        /// Coloca un modelo definitivo de Art/Models (generado con Python en la nube). Sus materiales se
        /// rehacen con el sombreado del juego y la textura que se llama igual en Art/Models/Texturas.
        /// </summary>
        static GameObject Model(string file, Transform parent, float x, float z, float yaw, string name = null,
            float y = 0f, bool exterior = false, Vector3? boxSize = null)
        {
            string path = $"Assets/_Ominous/Art/Models/{file}.fbx";
            if (AssetImporter.GetAtPath(path) is not ModelImporter importer) return null;
            if (!importer.generateSecondaryUV)
            {
                importer.generateSecondaryUV = true;
                importer.SaveAndReimport();
            }
            var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path), parent);
            go.name = name ?? file;
            go.transform.SetPositionAndRotation(new Vector3(x, y, z), Quaternion.Euler(0, yaw, 0));
            var bounds = new Bounds();
            bool first = true;
            foreach (var r in go.GetComponentsInChildren<MeshRenderer>())
            {
                r.sharedMaterials = System.Array.ConvertAll(r.sharedMaterials, m => ModelMaterial(m, exterior));
                Static(r.gameObject);
                var mesh = r.GetComponent<MeshFilter>().sharedMesh;
                var b = new Bounds(mesh.bounds.center + r.transform.localPosition, mesh.bounds.size);
                if (first) bounds = b; else bounds.Encapsulate(b);
                first = false;
            }
            Static(go);
            var box = go.AddComponent<BoxCollider>();
            box.center = bounds.center;
            box.size = boxSize ?? bounds.size;
            return go;
        }

        // Materiales de modelos ya hechos en esta construcción: varios modelos comparten nombres.
        static readonly System.Collections.Generic.Dictionary<string, Material> modelMaterials = new();

        static Material ModelMaterial(Material source, bool exterior)
        {
            string name = source.name + (exterior ? "_Exterior" : "");
            if (modelMaterials.TryGetValue(name, out var made) && made != null) return made;
            string path = $"Assets/_Ominous/Materials/Modelos/{name}.mat";
            System.IO.Directory.CreateDirectory("Assets/_Ominous/Materials/Modelos");
            var tex = AssetDatabase.LoadAssetAtPath<Texture2D>($"Assets/_Ominous/Art/Models/Texturas/{source.name}.png")
                ?? AssetDatabase.LoadAssetAtPath<Texture2D>($"Assets/_Ominous/Art/Models/Texturas/{source.name}.jpg");
            Color color = source.HasProperty("_BaseColor") ? source.GetColor("_BaseColor") : source.HasProperty("_Color") ? source.GetColor("_Color") : Color.white;
            Material mat;
            if (source.name.Contains("Pantalla"))
            {
                // La pantalla de la tele usa el material de siempre, que es el que parpadea.
                modelMaterials[name] = screen;
                return screen;
            }
            if (source.name.Contains("Cristal"))
            {
                mat = new Material(glass) { name = name };
                mat.SetColor("_Tint", new Color(color.r, color.g, color.b, 1f));
                mat.SetFloat("_Base", 0.6f);
            }
            else
            {
                string n = source.name;
                var template = n.Contains("Madera") ? woodDark : n.Contains("Ceramica") ? ceramic
                    : n.Contains("Cromo") || n.Contains("Tapacubos") || n.Contains("Pomo") ? chrome
                    : n.Contains("Neumatico") ? tire : n.Contains("Pintura") ? carRed : n.Contains("Sofa") ? sofa : plastic;
                mat = new Material(template) { name = name };
                mat.SetTexture("_BaseMap", tex);
                mat.SetTextureScale("_BaseMap", Vector2.one);
                mat.SetColor("_BaseColor", tex != null ? Color.white : new Color(color.r, color.g, color.b, 1f));
                if (mat.HasProperty("_Exterior")) mat.SetFloat("_Exterior", exterior ? 1f : 0f);
            }
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(mat, path);
            modelMaterials[name] = mat;
            return mat;
        }

        /// <summary>Largo al que se dejan los coches descargados: tienen que caber en el garaje (5 m).</summary>
        const float ExternalCarLength = 4.4f;

        /// <summary>
        /// Coche descargado (Art/Externos/Coches/Nombre): una sola textura de color con la oclusión ya
        /// multiplicada. Se quita la sombra plana que traen debajo y se escala a <see cref="ExternalCarLength"/>.
        /// </summary>
        static GameObject ExternalCar(string file, Transform parent, float x, float z, float yaw, string name, float y, bool exterior)
        {
            string dir = $"Assets/_Ominous/Art/Externos/Coches/{file}";
            var asset = AssetDatabase.LoadAssetAtPath<GameObject>($"{dir}/{file}.fbx");
            if (asset == null) return null;
            if (AssetImporter.GetAtPath($"{dir}/{file}.fbx") is ModelImporter importer && !importer.generateSecondaryUV)
            {
                importer.generateSecondaryUV = true;
                importer.SaveAndReimport();
            }
            string matPath = $"Assets/_Ominous/Materials/Modelos/{file}{(exterior ? "_Exterior" : "")}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
            if (mat == null || !modelMaterials.ContainsKey(matPath))
            {
                System.IO.Directory.CreateDirectory("Assets/_Ominous/Materials/Modelos");
                mat = new Material(carRed) { name = file };
                mat.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{dir}/{file}_Color.jpg"));
                mat.SetTextureScale("_BaseMap", Vector2.one);
                mat.SetColor("_BaseColor", Color.white);
                if (mat.HasProperty("_Exterior")) mat.SetFloat("_Exterior", exterior ? 1f : 0f);
                AssetDatabase.DeleteAsset(matPath);
                AssetDatabase.CreateAsset(mat, matPath);
                modelMaterials[matPath] = mat;
            }
            var go = (GameObject)PrefabUtility.InstantiatePrefab(asset, parent);
            go.name = name;
            var bounds = new Bounds();
            bool first = true;
            foreach (var r in go.GetComponentsInChildren<MeshRenderer>())
            {
                if (r.name.StartsWith("Plane")) { Object.DestroyImmediate(r.gameObject); continue; }
                r.sharedMaterials = System.Array.ConvertAll(r.sharedMaterials, _ => mat);
                Static(r.gameObject);
                if (first) bounds = r.bounds; else bounds.Encapsulate(r.bounds);
                first = false;
            }
            float scale = ExternalCarLength / bounds.size.z;
            go.transform.localScale = Vector3.one * scale;
            go.transform.SetPositionAndRotation(new Vector3(x, y, z), Quaternion.Euler(0, yaw, 0));
            Static(go);
            var box = go.AddComponent<BoxCollider>();
            box.center = new Vector3(bounds.center.x, bounds.center.y, bounds.center.z);
            box.size = new Vector3(bounds.size.x * 0.85f, bounds.size.y, bounds.size.z);
            return go;
        }

        /// <summary>
        /// Personaje descargado en lugar de la figura provisional de una postura. Se escala a su altura y,
        /// si viene en postura de A, se le bajan los brazos.
        /// </summary>
        static void ExternalCharacter(ActorFigure figure, string pose, string pathNoExt, float height, Material template)
        {
            var asset = AssetDatabase.LoadAssetAtPath<GameObject>(pathNoExt + ".fbx");
            if (asset == null) return;
            var root = figure.poses.Find(p => p.name == pose)?.root;
            if (root == null) return;
            root.GetComponent<MeshRenderer>().enabled = false;
            var model = (GameObject)PrefabUtility.InstantiatePrefab(asset, root.transform);
            model.name = "Modelo";
            model.transform.localPosition = Vector3.zero;
            model.transform.localRotation = Quaternion.identity;
            var skinned = model.GetComponentInChildren<SkinnedMeshRenderer>();
            model.transform.localScale = Vector3.one;
            float raw = skinned.bounds.size.y / figure.transform.lossyScale.y;
            model.transform.localScale = Vector3.one * (height / raw);
            foreach (var t in model.GetComponentsInChildren<Transform>())
            {
                if (t.name == "upper_arm.L") t.Rotate(Vector3.forward * 58f, Space.World);
                if (t.name == "upper_arm.R") t.Rotate(Vector3.forward * -58f, Space.World);
            }
            string matPath = $"Assets/_Ominous/Materials/Modelos/{asset.name}.mat";
            var mat = new Material(template) { name = asset.name };
            mat.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(pathNoExt + "_Color.png"));
            mat.SetTextureScale("_BaseMap", Vector2.one);
            mat.SetColor("_BaseColor", Color.white);
            AssetDatabase.DeleteAsset(matPath);
            AssetDatabase.CreateAsset(mat, matPath);
            foreach (var r in model.GetComponentsInChildren<Renderer>()) r.sharedMaterial = mat;
        }

        static GameObject Again(string prefab, Transform parent, float x, float z, float yaw = 0f, float y = 0f)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>($"Assets/_Ominous/Prefabs/{prefab}.prefab"), parent);
            go.transform.SetPositionAndRotation(new Vector3(x, y, z), Quaternion.Euler(0, yaw, 0));
            Static(go);
            return go;
        }

        // ---------- muebles nuevos (frente hacia +z salvo que se diga otra cosa) ----------

        static MeshKit Cama()
        {
            var k = new MeshKit();
            k.Box(new Vector3(0, 0.17f, 0), new Vector3(1.5f, 0.22f, 2f), woodDark);
            k.Box(new Vector3(0, 0.38f, 0), new Vector3(1.44f, 0.2f, 1.94f), pillow);
            k.Box(new Vector3(0, 0.49f, -0.2f), new Vector3(1.52f, 0.05f, 1.56f), sheet);
            k.Box(new Vector3(-0.77f, 0.33f, -0.2f), new Vector3(0.03f, 0.3f, 1.56f), sheet);
            k.Box(new Vector3(0.77f, 0.33f, -0.2f), new Vector3(0.03f, 0.3f, 1.56f), sheet);
            k.Box(new Vector3(0, 0.33f, -0.99f), new Vector3(1.56f, 0.3f, 0.03f), sheet);
            k.Box(new Vector3(0, 0.55f, 0.75f), new Vector3(0.6f, 0.12f, 0.42f), pillow).Box(new Vector3(0.36f, 0.54f, 0.74f), new Vector3(0.6f, 0.11f, 0.42f), pillow);
            k.Box(new Vector3(0, 0.55f, 1.0f), new Vector3(1.5f, 1.1f, 0.05f), woodDark);
            foreach (float x in new[] { -0.7f, 0.7f })
                foreach (float z in new[] { -0.95f, 0.95f })
                    k.Box(new Vector3(x, 0.03f, z), new Vector3(0.07f, 0.06f, 0.07f), woodDark);
            return k;
        }

        static MeshKit Mesilla(bool lamp)
        {
            var k = new MeshKit();
            k.Box(new Vector3(0, 0.27f, 0), new Vector3(0.45f, 0.54f, 0.4f), woodDark);
            k.Box(new Vector3(0, 0.38f, 0.205f), new Vector3(0.38f, 0.16f, 0.015f), woodLight);
            k.Box(new Vector3(0, 0.38f, 0.215f), new Vector3(0.05f, 0.015f, 0.015f), metal);
            if (lamp)
            {
                k.Cylinder(new Vector3(0, 0.54f, 0), 0.06f, 0.015f, 0.2f, 6, metal);
                k.Cylinder(new Vector3(0, 0.72f, 0), 0.11f, 0.06f, 0.14f, 8, shade);
            }
            return k;
        }

        static MeshKit Armario()
        {
            // Hueco: se puede entrar. Frente hacia +z; las hojas y el fondo son piezas aparte.
            var k = new MeshKit();
            k.Box(new Vector3(0, 2.08f, 0), new Vector3(1.4f, 0.04f, 0.58f), woodLight);
            k.Box(new Vector3(-0.69f, 1.04f, 0), new Vector3(0.02f, 2.08f, 0.58f), woodLight);
            k.Box(new Vector3(0.69f, 1.04f, 0), new Vector3(0.02f, 2.08f, 0.58f), woodLight);
            k.Box(new Vector3(0, 1.75f, -0.05f), new Vector3(1.36f, 0.02f, 0.46f), woodLight);
            k.Box(new Vector3(0, 1.62f, 0), new Vector3(1.36f, 0.02f, 0.02f), metal);
            return k;
        }

        static GameObject Part(string name, MeshKit kit, Transform parent, Vector3 local)
        {
            var mesh = kit.Build(name, out var mats);
            string path = $"Assets/_Ominous/Art/Meshes/{name}.asset";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(mesh, path);
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = local;
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterials = mats;
            return go;
        }

        static MeshKit ComodaSimple()
        {
            var k = new MeshKit();
            k.Box(new Vector3(0, 0.38f, 0), new Vector3(0.95f, 0.76f, 0.42f), woodLight);
            for (int i = 0; i < 3; i++)
            {
                k.Box(new Vector3(0, 0.15f + i * 0.23f, 0.215f), new Vector3(0.87f, 0.2f, 0.012f), woodDark);
                k.Box(new Vector3(0, 0.15f + i * 0.23f, 0.228f), new Vector3(0.1f, 0.015f, 0.015f), metal);
            }
            return k;
        }

        static MeshKit Nevera()
        {
            var k = new MeshKit();
            k.Box(new Vector3(0, 0.92f, 0), new Vector3(0.72f, 1.84f, 0.68f), fridge);
            k.Box(new Vector3(0, 0.62f, 0.35f), new Vector3(0.69f, 1.15f, 0.02f), fridge);
            k.Box(new Vector3(0, 1.48f, 0.35f), new Vector3(0.69f, 0.66f, 0.02f), fridge);
            k.Box(new Vector3(-0.29f, 1.08f, 0.375f), new Vector3(0.03f, 0.3f, 0.03f), chrome);
            k.Box(new Vector3(-0.29f, 1.36f, 0.375f), new Vector3(0.03f, 0.2f, 0.03f), chrome);
            return k;
        }

        static MeshKit Encimera()
        {
            // Bajo la ventana, contra la pared sur: el frente mira a +z. Mide 4.4 m desde x = 8.3.
            var k = new MeshKit();
            const float w = 4.4f, cx = 0f;
            k.Box(new Vector3(cx, 0.44f, 0), new Vector3(w, 0.88f, 0.58f), woodLight);
            k.Box(new Vector3(cx, 0.9f, 0.01f), new Vector3(w + 0.02f, 0.04f, 0.62f), countertop);
            for (int i = 0; i < 6; i++)
            {
                float x = -w * 0.5f + 0.37f + i * 0.733f;
                k.Box(new Vector3(x, 0.47f, 0.296f), new Vector3(0.68f, 0.76f, 0.012f), woodDark);
                k.Box(new Vector3(x + 0.26f, 0.72f, 0.31f), new Vector3(0.02f, 0.1f, 0.015f), metal);
            }
            k.Box(new Vector3(0, 0.05f, 0.27f), new Vector3(w, 0.1f, 0.04f), plastic);
            // Fregadero bajo la ventana y grifo
            k.Box(new Vector3(-0.0f, 0.923f, 0.02f), new Vector3(0.72f, 0.012f, 0.44f), chrome);
            k.Box(new Vector3(-0.0f, 0.93f, 0.02f), new Vector3(0.58f, 0.004f, 0.32f), plastic);
            k.Cylinder(new Vector3(0, 0.93f, -0.21f), 0.016f, 0.012f, 0.24f, 6, chrome);
            k.Box(new Vector3(0, 1.16f, -0.13f), new Vector3(0.022f, 0.022f, 0.17f), chrome);
            // Armarios altos a los lados de la ventana
            foreach (float x in new[] { -1.65f, 1.45f })
            {
                float width = x < 0 ? 1.05f : 1.45f;
                k.Box(new Vector3(x, 1.82f, -0.11f), new Vector3(width, 0.72f, 0.33f), woodLight);
                k.Box(new Vector3(x, 1.82f, 0.058f), new Vector3(width - 0.04f, 0.68f, 0.012f), woodDark);
            }
            return k;
        }

        static MeshKit MesaCocina()
        {
            var k = new MeshKit();
            k.Box(new Vector3(0, 0.74f, 0), new Vector3(1.4f, 0.04f, 0.8f), woodLight);
            foreach (float x in new[] { -0.64f, 0.64f })
                foreach (float z in new[] { -0.34f, 0.34f })
                    k.Box(new Vector3(x, 0.36f, z), new Vector3(0.05f, 0.72f, 0.05f), woodDark);
            return k;
        }

        static MeshKit Silla()
        {
            var k = new MeshKit();
            k.Box(new Vector3(0, 0.45f, 0), new Vector3(0.42f, 0.035f, 0.42f), woodLight);
            k.Box(new Vector3(0, 0.84f, -0.195f), new Vector3(0.4f, 0.2f, 0.025f), woodDark);
            foreach (float x in new[] { -0.19f, 0.19f })
            {
                k.Box(new Vector3(x, 0.22f, 0.19f), new Vector3(0.03f, 0.44f, 0.03f), woodDark);
                k.Box(new Vector3(x, 0.47f, -0.195f), new Vector3(0.03f, 0.94f, 0.03f), woodDark);
            }
            return k;
        }

        static MeshKit Banera()
        {
            // Largo en z; origen en el centro del suelo.
            var k = new MeshKit();
            k.Box(new Vector3(0, 0.26f, -0.82f), new Vector3(0.76f, 0.52f, 0.06f), ceramic);
            k.Box(new Vector3(0, 0.26f, 0.82f), new Vector3(0.76f, 0.52f, 0.06f), ceramic);
            k.Box(new Vector3(-0.35f, 0.26f, 0), new Vector3(0.06f, 0.52f, 1.7f), ceramic);
            k.Box(new Vector3(0.35f, 0.26f, 0), new Vector3(0.06f, 0.52f, 1.7f), ceramic);
            k.Box(new Vector3(0, 0.12f, 0), new Vector3(0.64f, 0.05f, 1.58f), ceramic);
            k.Cylinder(new Vector3(0, 0.52f, 0.79f), 0.014f, 0.012f, 0.16f, 6, chrome);
            k.Box(new Vector3(0, 0.67f, 0.72f), new Vector3(0.022f, 0.022f, 0.14f), chrome);
            return k;
        }

        static MeshKit Lavabo()
        {
            // Frente a +z. El grifo es el del guion: el que gotea.
            var k = new MeshKit();
            k.Cylinder(new Vector3(0, 0, -0.06f), 0.1f, 0.075f, 0.68f, 8, ceramic);
            k.Box(new Vector3(0, 0.74f, 0), new Vector3(0.6f, 0.12f, 0.46f), ceramic);
            k.Box(new Vector3(0, 0.805f, 0.01f), new Vector3(0.44f, 0.01f, 0.3f), mirror);
            k.Cylinder(new Vector3(0, 0.8f, -0.18f), 0.014f, 0.012f, 0.15f, 6, chrome);
            k.Box(new Vector3(0, 0.945f, -0.12f), new Vector3(0.02f, 0.02f, 0.13f), chrome);
            k.Box(new Vector3(0.09f, 0.83f, -0.18f), new Vector3(0.05f, 0.03f, 0.03f), chrome);
            return k;
        }

        static MeshKit Vater()
        {
            // Frente a +z, cisterna a -z.
            var k = new MeshKit();
            k.Cylinder(new Vector3(0, 0, 0.05f), 0.13f, 0.19f, 0.4f, 8, ceramic);
            k.Box(new Vector3(0, 0.41f, 0.06f), new Vector3(0.36f, 0.03f, 0.42f), ceramic);
            k.Box(new Vector3(0, 0.6f, -0.24f), new Vector3(0.42f, 0.42f, 0.18f), ceramic);
            k.Box(new Vector3(0, 0.82f, -0.24f), new Vector3(0.05f, 0.02f, 0.05f), chrome);
            return k;
        }

        static MeshKit Lavadora(bool drum)
        {
            var k = new MeshKit();
            k.Box(new Vector3(0, 0.43f, 0), new Vector3(0.6f, 0.86f, 0.6f), appliance);
            k.Cylinder(new Vector3(0, 0.38f, 0.3f), 0.0f, 0.0f, 0.0f, 3, chrome);
            k.Box(new Vector3(0, 0.38f, 0.305f), new Vector3(0.36f, 0.36f, 0.012f), drum ? carGlass : appliance);
            k.Box(new Vector3(0, 0.38f, 0.312f), new Vector3(0.28f, 0.28f, 0.006f), plastic);
            k.Box(new Vector3(0, 0.76f, 0.305f), new Vector3(0.52f, 0.1f, 0.012f), plastic);
            return k;
        }

        static MeshKit Coche(Material body, Material windows, Material wheels)
        {
            // Largo en z, morro hacia +z. Berlina de los 90: capó y maletero más bajos que el habitáculo.
            var k = new MeshKit();
            k.Box(new Vector3(0, 0.42f, 0), new Vector3(1.7f, 0.36f, 4.3f), body);
            k.Box(new Vector3(0, 0.63f, 1.52f), new Vector3(1.66f, 0.08f, 1.25f), body);     // Capó
            k.Box(new Vector3(0, 0.63f, -1.72f), new Vector3(1.66f, 0.08f, 0.85f), body);    // Maletero
            k.Box(new Vector3(0, 0.76f, -0.2f), new Vector3(1.62f, 0.2f, 2.3f), body);       // Cintura
            k.Box(new Vector3(0, 0.98f, -0.2f), new Vector3(1.5f, 0.26f, 1.85f), windows);   // Cristales
            k.Box(new Vector3(0, 1.13f, -0.2f), new Vector3(1.42f, 0.04f, 1.6f), body);      // Techo
            foreach (float z in new[] { -1.04f, 0.64f })
                foreach (float x in new[] { -0.74f, 0.74f })
                    k.Box(new Vector3(x, 0.98f, z - 0.2f + 0.2f), new Vector3(0.05f, 0.26f, 0.05f), body); // Montantes
            foreach (float z in new[] { -1.38f, 1.38f })
                foreach (float x in new[] { -0.8f, 0.8f })
                    k.Box(new Vector3(x, 0.3f, z), new Vector3(0.2f, 0.6f, 0.62f), wheels);
            k.Box(new Vector3(0, 0.34f, 2.17f), new Vector3(1.72f, 0.14f, 0.05f), plastic);
            k.Box(new Vector3(0, 0.34f, -2.17f), new Vector3(1.72f, 0.14f, 0.05f), plastic);
            foreach (float x in new[] { -0.62f, 0.62f })
            {
                k.Box(new Vector3(x, 0.5f, 2.155f), new Vector3(0.32f, 0.13f, 0.02f), chrome);
                k.Box(new Vector3(x, 0.5f, -2.155f), new Vector3(0.32f, 0.12f, 0.02f), carRed);
            }
            return k;
        }

        static GameObject Door(Transform parent, string name, float x, float z, bool alongX, float openYaw, bool locked = false, bool hingeAtEnd = false)
        {
            // Hoja a lo largo de +z; con yaw 90 la bisagra queda a lo largo de +x.
            float yaw = alongX ? 90f : 0f;
            var frameGo = Again("PuertaMarco", parent, alongX ? x + 0.45f : x, alongX ? z : z + 0.45f, yaw);
            frameGo.name = name + "_Marco";
            var leafGo = Again("PuertaHoja", parent, x + (alongX ? 0.02f : 0f), z + (alongX ? 0f : 0.02f), yaw);
            GameObjectUtility.SetStaticEditorFlags(leafGo, 0);
            leafGo.name = name;
            var door = leafGo.AddComponent<Door>();
            door.openYaw = openYaw;
            door.locked = locked;
            return leafGo;
        }

        /// <summary>Plafón con bombilla y su interruptor junto a la puerta.</summary>
        static void RoomLight(Transform parent, string room, float x, float z, Vector3 switchPos, float switchYaw, Color color, float intensity, bool startsOn = false, float range = 7f, float ceiling = 2.6f)
        {
            var fixture = Again("Plafon", parent, x, z, 0f, ceiling);
            fixture.name = "Plafon_" + room;
            var glow = fixture.GetComponent<MeshRenderer>();
            GameObjectUtility.SetStaticEditorFlags(fixture, StaticEditorFlags.BatchingStatic);
            var light = SpotLight("Luz_" + room, parent, new Vector3(x, ceiling - 0.14f, z), Quaternion.Euler(90, 0, 0), color, intensity, range, 168f, ~0);
            light.shadows = LightShadows.Soft;
            light.shadowStrength = 0.85f;
            // El techo y lo alto de las paredes también reciben algo de luz, sin sombra.
            var fill = Point("Relleno_" + room, parent, new Vector3(x, ceiling - 0.35f, z), color, intensity * 0.12f, 3.5f);
            var sw = Again("Interruptor", parent, switchPos.x, switchPos.z, switchYaw, switchPos.y);
            sw.name = "Interruptor_" + room;
            GameObjectUtility.SetStaticEditorFlags(sw, 0);
            sw.GetComponent<BoxCollider>().size = new Vector3(0.1f, 0.25f, 0.2f);
            var ls = sw.AddComponent<LightSwitch>();
            ls.lights = new[] { light, fill };
            ls.isOn = startsOn;
            ls.emissive = glow;
        }

        static void Picture(Transform parent, string name, Material art, float x, float y, float z, float yaw, float w = 0.62f, float h = 0.47f)
        {
            var k = new MeshKit();
            k.Box(Vector3.zero, new Vector3(w, h, 0.03f), woodDark);
            k.Box(new Vector3(0, 0, -0.018f), new Vector3(w - 0.08f, h - 0.08f, 0.006f), art);
            Put(name, k, parent, x, z, yaw, false, y);
        }

        // ---------- la casa ----------

        [MenuItem("Tools/Ominous/Construir la casa")]
        public static void BuildHouse()
        {
            OminousSetup.Configure();
            modelMaterials.Clear();
            Materials();
            HouseMaterials();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var house = new GameObject("Casa").transform;
            var furniture = new GameObject("Muebles").transform; furniture.SetParent(house);
            var doors = new GameObject("Puertas").transform; doors.SetParent(house);
            var lights = new GameObject("Luces").transform;
            var street = new GameObject("Calle").transform;

            BuildStructure(house);
            BuildPrefabs();
            BuildSalon(furniture, lights);
            BuildHall(furniture, doors, lights);
            BuildKitchen(furniture, doors, lights);
            BuildBedroom(furniture, doors, lights);
            BuildBathroom(furniture, doors, lights);
            BuildLaundry(furniture, doors, lights);
            BuildGarage(furniture, doors, lights);
            BuildExterior(street, lights);
            var tvAudio = BuildSound();
            BuildPlayerAndSystems();
            BuildStory(tvAudio);

            RenderSettings.skybox = null;
            RenderSettings.ambientMode = AmbientMode.Flat;
            // Esta luz solo cuenta al hornear: es el cielo de noche que entra por las ventanas.
            RenderSettings.ambientLight = new Color(0.55f, 0.62f, 0.72f);
            RenderSettings.ambientIntensity = 1f;
            RenderSettings.fog = false;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;

            EditorSceneManager.SaveScene(scene, HousePath);
            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(MenuPath, true),
                new EditorBuildSettingsScene(HousePath, true),
                new EditorBuildSettingsScene(SistemasPath, true),
            };
            AssetDatabase.SaveAssets();
            Debug.Log("Casa construida");
        }

        static void BuildStructure(Transform house)
        {
            var floors = new MeshKit();
            const float y = -0.05f, t = 0.1f;
            void Floor(float x0, float x1, float z0, float z1, Material m) => floors.Box(new Vector3((x0 + x1) / 2, y, (z0 + z1) / 2), new Vector3(x1 - x0, t, z1 - z0), m);
            Floor(0, 5, 0, 4.4f, floorWood);        // Salón
            Floor(5, 7, 0, 4.4f, floorWood);        // Recibidor
            Floor(7, 8.2f, 0, 4.4f, concreteIn);    // Cuartito oculto
            Floor(8.2f, 14, 0, 4.4f, linoleum);     // Cocina
            Floor(14, 19, 0, 4.4f, concreteIn);     // Garaje
            Floor(0, 14, 4.4f, 6, floorWood);       // Pasillo
            Floor(0, 6, 6, 10, floorWood);          // Dormitorio
            Floor(6, 6.8f, 6, 10, concreteIn);      // Hueco oculto
            Floor(6.8f, 10, 6, 10, tileFloor);      // Baño
            Floor(10, 14, 6, 10, linoleum);         // Colada
            GameObject go = Instance("Casa_Suelos", floors, house, Vector3.zero, 0, false);
            go.AddComponent<MeshCollider>(); Static(go);

            var ceil = new MeshKit();
            ceil.Box(new Vector3(7, Height + 0.05f, 5), new Vector3(14.2f, 0.1f, 10.2f), ceiling);
            ceil.Box(new Vector3(16.5f, Height + 0.05f, 2.2f), new Vector3(5.2f, 0.1f, 4.6f), ceiling);
            go = Instance("Casa_Techos", ceil, house, Vector3.zero, 0, false); Static(go);

            var w = new MeshKit();
            var saloonWin1 = new Opening(0.9f, 2.3f, 0.9f, 2.1f);
            var saloonWin2 = new Opening(3f, 4.4f, 0.9f, 2.1f);
            var frontDoor = new Opening(5.55f, 6.45f, 0f, DoorTop);
            var kitchenWin = new Opening(9.5f, 10.9f, 1.05f, 2.05f);
            var garageDoor = new Opening(15f, 18f, 0f, 2.2f);
            var southOpenings = new[] { saloonWin1, saloonWin2, frontDoor, kitchenWin, garageDoor };
            var northOpenings = new[] { new Opening(1.5f, 2.9f, 0.9f, 2.1f), new Opening(3.5f, 4.9f, 0.9f, 2.1f), new Opening(8f, 8.8f, 1.45f, 2.15f), new Opening(11.5f, 12.5f, 1.1f, 2.1f) };
            var westOpenings = new[] { new Opening(1.8f, 3.2f, 0.9f, 2.1f), new Opening(4.75f, 5.65f, 0f, DoorTop) };
            var eastNorthOpenings = new[] { new Opening(3.3f - 0.4f, 4.3f, 1.05f, 2.1f) }; // x = 14 desde z = 4.4
            Wall(w, new Vector3(0, 0, 0), 19f, true, wall, southOpenings);
            Wall(w, new Vector3(0, 0, 10), 14f, true, wall, northOpenings);
            Wall(w, new Vector3(0, 0, 0), 10f, false, wall, westOpenings);
            Wall(w, new Vector3(14, 0, 4.4f), 5.6f, false, wall, eastNorthOpenings);
            Wall(w, new Vector3(19, 0, 0), 4.4f, false, wall);
            Wall(w, new Vector3(14, 0, 4.4f), 5f, true, wall);
            Wall(w, new Vector3(14, 0, 0), 4.4f, false, wall, new Opening(2.1f, 3f, 0, DoorTop));
            Wall(w, new Vector3(0, 0, 4.4f), 14f, true, wall, new Opening(5.6f, 6.5f, 0, DoorTop), new Opening(7.2f, 8f, 0, 1.85f), new Opening(10f, 10.9f, 0, DoorTop));
            Wall(w, new Vector3(0, 0, 6), 14f, true, wall, new Opening(2.5f, 3.4f, 0, DoorTop), new Opening(8f, 8.9f, 0, DoorTop), new Opening(11.5f, 12.4f, 0, DoorTop));
            Wall(w, new Vector3(5, 0, 0), 4.4f, false, wall, new Opening(2.1f, 3f, 0, DoorTop));
            Wall(w, new Vector3(7, 0, 0), 4.4f, false, wall);
            Wall(w, new Vector3(8.2f, 0, 0), 4.4f, false, wall);
            Wall(w, new Vector3(6, 0, 6), 4f, false, wall, new Opening(1.35f, 1.5f, 1.52f, 1.66f), new Opening(2.3f, 3.1f, 0, 1.9f));
            Wall(w, new Vector3(6.8f, 0, 6), 4f, false, wall, new Opening(1.2f, 1.35f, 1.66f, 1.78f));
            Wall(w, new Vector3(10, 0, 6), 4f, false, wall);

            // Azulejo del baño hasta 1,6 m, y concreto en el garaje
            void Lining(Vector3 a, float len, bool alongX, Material m, float top)
            {
                Vector3 c = a + (alongX ? Vector3.right : Vector3.forward) * (len / 2) + Vector3.up * (top / 2);
                w.Box(c, alongX ? new Vector3(len, top, 0.008f) : new Vector3(0.008f, top, len), m);
            }
            Lining(new Vector3(6.87f, 0, 6.06f), 2.83f, false, tileWall, 1.6f); // Oeste del baño
            Lining(new Vector3(9.93f, 0, 6.06f), 3.88f, false, tileWall, 1.6f); // Este del baño
            Lining(new Vector3(6.86f, 0, 9.93f), 3.08f, true, tileWall, 1.45f); // Norte del baño
            Lining(new Vector3(6.86f, 0, 6.07f), 1.14f, true, tileWall, 1.6f);
            Lining(new Vector3(8.9f, 0, 6.07f), 1.04f, true, tileWall, 1.6f);
            Lining(new Vector3(8.3f, 0, 0.07f), 1.2f, true, tileWall, 0.95f);   // Salpicadero de cocina
            go = Instance("Casa_Paredes", w, house, Vector3.zero, 0, false);
            go.AddComponent<MeshCollider>(); Static(go);

            // Molduras
            var trim = new MeshKit();
            void Skirt(float x0, float x1, float z0, float z1) => trim.Box(new Vector3((x0 + x1) / 2, 0.05f, (z0 + z1) / 2), new Vector3(Mathf.Max(x1 - x0, 0.015f), 0.1f, Mathf.Max(z1 - z0, 0.015f)), woodDark);
            Skirt(0.06f, 4.94f, 4.33f, 4.33f); Skirt(0.07f, 2.05f, 6.07f, 6.07f); Skirt(3.5f, 5.93f, 6.07f, 6.07f);
            Skirt(0.06f, 5.93f, 9.93f, 9.93f); Skirt(0.07f, 0.07f, 0.06f, 1.8f); Skirt(0.07f, 0.07f, 3.2f, 4.33f);
            Skirt(0.07f, 0.07f, 6.07f, 9.93f); Skirt(5.93f, 5.93f, 6.07f, 9.93f); Skirt(4.93f, 4.93f, 0.06f, 2.1f); Skirt(4.93f, 4.93f, 3f, 4.33f);
            Skirt(0.1f, 2.5f, 4.47f, 4.47f); Skirt(0.1f, 7f, 5.93f, 5.93f); Skirt(9f, 11.5f, 5.93f, 5.93f); Skirt(12.5f, 13.93f, 5.93f, 5.93f);
            Skirt(7f, 10f, 4.47f, 4.47f); Skirt(11f, 13.93f, 4.47f, 4.47f);
            Instance("Casa_Molduras", trim, house, Vector3.zero, 0, false);
            Static(GameObject.Find("Casa_Molduras"));

            // Ventanas: marco, cristal y cortinas
            var windows = new MeshKit();
            void Win(float x, float z, float width, float height, float centerY, bool alongX, float inward, bool curtains = true)
            {
                if (curtains) WindowDressing(windows, new Vector3(x, centerY, z), width, height, alongX, inward);
                else WindowFrameOnly(windows, new Vector3(x, centerY, z), width, height, alongX, inward);
            }
            Win(1.6f, 0, 1.4f, 1.2f, 1.5f, true, 1f);
            Win(3.7f, 0, 1.4f, 1.2f, 1.5f, true, 1f);
            Win(0, 2.5f, 1.4f, 1.2f, 1.5f, false, 1f);
            Win(10.2f, 0, 1.4f, 1f, 1.55f, true, 1f, false);
            Win(2.2f, 10, 1.4f, 1.2f, 1.5f, true, -1f);
            Win(4.2f, 10, 1.4f, 1.2f, 1.5f, true, -1f);
            Win(8.4f, 10, 0.8f, 0.7f, 1.8f, true, -1f, false);
            Win(12f, 10, 1f, 1f, 1.6f, true, -1f, false);
            Win(14, 8.1f, 1.4f, 1.05f, 1.575f, false, -1f, false);
            go = Instance("Casa_Ventanas", windows, house, Vector3.zero, 0, false); Static(go);
            foreach (var (x, z, sx, sz) in new[] { (1.6f, 0f, 1.4f, 0.2f), (3.7f, 0f, 1.4f, 0.2f), (0f, 2.5f, 0.2f, 1.4f), (10.2f, 0f, 1.4f, 0.2f), (2.2f, 10f, 1.4f, 0.2f), (4.2f, 10f, 1.4f, 0.2f), (8.4f, 10f, 0.8f, 0.2f), (12f, 10f, 1f, 0.2f), (14f, 8.1f, 0.2f, 1.4f) })
                Blocker(house, new Vector3(x, 1.3f, z), new Vector3(sx, 2.6f, sz));

            // Fachada: tablas por fuera, con los mismos huecos, y tejado
            var outer = new MeshKit();
            Wall(outer, new Vector3(0, 0, -0.07f), 19f, true, siding, 0.02f, southOpenings);
            Wall(outer, new Vector3(0, 0, 10.07f), 14f, true, siding, 0.02f, northOpenings);
            Wall(outer, new Vector3(-0.07f, 0, 0), 10f, false, siding, 0.02f, westOpenings);
            Wall(outer, new Vector3(14.07f, 0, 4.4f), 5.6f, false, siding, 0.02f, eastNorthOpenings);
            Wall(outer, new Vector3(19.07f, 0, 0), 4.4f, false, siding, 0.02f, new Opening[0]);
            Wall(outer, new Vector3(14, 0, 4.47f), 5f, true, siding, 0.02f, new Opening[0]);
            for (int i = 0; i < 5; i++)
            {
                float inset = i * 0.8f, h = Height + 0.15f + i * 0.28f;
                outer.Box(new Vector3(7, h, 5), new Vector3(15f - inset * 2, 0.28f, 11f - inset * 2), roof);
            }
            outer.Box(new Vector3(16.5f, Height + 0.2f, 2.2f), new Vector3(5.8f, 0.3f, 5.2f), roof);
            // Puerta de garaje vista desde fuera y desde dentro
            outer.Box(new Vector3(16.5f, 1.1f, 0), new Vector3(3f, 2.2f, 0.05f), sidingFar);
            for (int i = 1; i < 4; i++) outer.Box(new Vector3(16.5f, i * 0.55f, -0.03f), new Vector3(3f, 0.02f, 0.01f), roof);
            go = Instance("Casa_Fachada", outer, house, Vector3.zero, 0, false);
            GameObjectUtility.SetStaticEditorFlags(go, StaticEditorFlags.BatchingStatic);
            go.layer = ExteriorLayer;
            var bc = go.AddComponent<BoxCollider>(); bc.center = new Vector3(16.5f, 1.1f, 0); bc.size = new Vector3(3f, 2.2f, 0.1f);
        }

        static void WindowFrameOnly(MeshKit kit, Vector3 center, float width, float height, bool alongX, float inward)
        {
            const float bar = 0.05f, depth = 0.19f;
            Vector3 along = alongX ? Vector3.right : Vector3.forward;
            Vector3 normal = alongX ? Vector3.forward : Vector3.right;
            Vector3 H(float w, float h, float d) => alongX ? new Vector3(w, h, d) : new Vector3(d, h, w);
            kit.Box(center + Vector3.up * (height * 0.5f), H(width + bar * 2, bar, depth), frame);
            kit.Box(center - Vector3.up * (height * 0.5f), H(width + bar * 2, bar, depth + 0.08f), frame);
            kit.Box(center + along * (width * 0.5f), H(bar, height, depth), frame);
            kit.Box(center - along * (width * 0.5f), H(bar, height, depth), frame);
            kit.Box(center, H(0.03f, height, 0.03f), frame);
            kit.Box(center - normal * (inward * 0.01f), H(width, height, 0.005f), glass);
        }

        static void BuildPrefabs()
        {
            var parent = new GameObject("_tmp").transform;
            var leaf = new MeshKit();
            leaf.Box(new Vector3(0, 1.0f, 0.43f), new Vector3(0.04f, 2.0f, 0.86f), door);
            leaf.Box(new Vector3(-0.05f, 0.95f, 0.77f), new Vector3(0.05f, 0.03f, 0.1f), metal);
            leaf.Box(new Vector3(0.05f, 0.95f, 0.77f), new Vector3(0.05f, 0.03f, 0.1f), metal);
            Instance("PuertaHoja", leaf, parent, Vector3.zero);
            Instance("PuertaMarco", PuertaMarco(), parent, Vector3.zero, 0, false);
            var sw = new MeshKit();
            sw.Box(Vector3.zero, new Vector3(0.02f, 0.12f, 0.08f), frame);
            sw.Box(new Vector3(-0.015f, 0, 0), new Vector3(0.015f, 0.04f, 0.02f), metal);
            Instance("Interruptor", sw, parent, Vector3.zero);
            var fixture = new MeshKit();
            fixture.Cylinder(new Vector3(0, -0.1f, 0), 0.17f, 0.2f, 0.1f, 10, paper);
            Instance("Plafon", fixture, parent, Vector3.zero, 0, false);
            Object.DestroyImmediate(parent.gameObject);
        }

        static void BuildSalon(Transform f, Transform lights)
        {
            Put("Alfombra", Alfombra(), f, 2.15f, 2.45f, 0, false);
            if (Model("Sofa", f, 2.15f, 1.45f, 0f, null, 0f, false, new Vector3(2.0f, 0.94f, 0.86f)) == null) Put("Sofa", Sofa(), f, 2.15f, 1.45f);
            Put("Manta", Manta(), f, 1.6f, 1.45f, 0, false);
            // La tele definitiva mira a +Z: va girada. Su pantalla es un objeto aparte para el parpadeo.
            var tele = Model("Tele", f, 2.15f, 4.08f, 180f);
            Renderer teleScreen = null;
            if (tele != null)
            {
                foreach (var r in tele.GetComponentsInChildren<MeshRenderer>())
                {
                    if (r.name == "Pantalla") teleScreen = r;
                    else r.name = "TeleMueble";
                }
            }
            else
            {
                tele = Put("Tele", Tele(), f, 2.15f, 4.08f);
                teleScreen = tele.GetComponent<MeshRenderer>();
            }
            if (Model("MesaBaja", f, 2.15f, 2.75f, 0f) == null) Put("MesaBaja", MesaBaja(), f, 2.15f, 2.75f);
            if (Model("Estanteria", f, 4.2f, 4.17f, 180f, "EstanteriaSalon") == null) Put("EstanteriaSalon", Estanteria(), f, 4.2f, 4.17f);
            var lampMesh = Put("Lampara", Lampara(), f, 0.4f, 0.5f);
            GameObjectUtility.SetStaticEditorFlags(lampMesh, StaticEditorFlags.BatchingStatic);
            Picture(f, "CuadroSalon", paintA, 0.08f, 1.65f, 3.75f, 90f);

            var tvFillLight = Point("LuzTeleResplandor", lights, new Vector3(2.15f, 1f, 3.65f), new Color(0.72f, 0.8f, 0.95f), 0.5f, 3f);
            var tv = SpotLight("LuzTele", lights, new Vector3(2.15f, 0.8f, 3.8f), Quaternion.Euler(4, 180, 0), new Color(0.72f, 0.8f, 0.95f), 3f, 8f, 150f, ~0);
            tv.shadows = LightShadows.Soft;
            tv.shadowStrength = 0.9f;
            var flicker = tele.AddComponent<TVFlicker>();
            flicker.tvLight = tv;
            flicker.screen = teleScreen;
            flicker.screenMaterialIndex = Mathf.Max(0, System.Array.IndexOf(flicker.screen.sharedMaterials, screen));

            var lamp = Point("LuzLampara", lights, new Vector3(0.42f, 1.48f, 0.52f), new Color(1f, 0.72f, 0.42f), 1.8f, 5.5f);
            lamp.shadows = LightShadows.Soft;
            lamp.shadowStrength = 0.8f;
            var sw = Again("Interruptor", f, 4.93f, 3.3f, 0f, 1.2f);
            sw.name = "Interruptor_Salon";
            GameObjectUtility.SetStaticEditorFlags(sw, 0);
            sw.GetComponent<BoxCollider>().size = new Vector3(0.1f, 0.25f, 0.2f);
            var ls = sw.AddComponent<LightSwitch>();
            ls.lights = new[] { lamp };
            ls.isOn = true;
            ls.emissive = lampMesh.GetComponent<MeshRenderer>();
        }

        static void BuildHall(Transform f, Transform d, Transform lights)
        {
            // Recibidor
            var mat = new MeshKit().Box(new Vector3(0, 0.008f, 0), new Vector3(0.8f, 0.016f, 0.5f), concreteIn);
            Put("Felpudo", mat, f, 6f, 0.42f, 0, false);
            var table = new MeshKit();
            table.Box(new Vector3(0, 0.4f, 0), new Vector3(1f, 0.8f, 0.34f), woodDark);
            table.Box(new Vector3(0, 0.82f, 0), new Vector3(1.04f, 0.03f, 0.38f), woodLight);
            table.Box(new Vector3(-0.25f, 0.5f, 0.175f), new Vector3(0.42f, 0.5f, 0.012f), woodLight);
            table.Box(new Vector3(0.25f, 0.5f, 0.175f), new Vector3(0.42f, 0.5f, 0.012f), woodLight);
            table.Cylinder(new Vector3(0.2f, 0.835f, 0), 0.06f, 0.1f, 0.05f, 8, ceramic);
            // Modelo definitivo (fase 10) si existe; si no, el provisional.
            if (Model("MuebleRecibidor", f, 6.8f, 1.5f, 270f) == null) Put("MuebleRecibidor", table, f, 6.8f, 1.5f, 270f);
            var hanger = new MeshKit();
            hanger.Cylinder(Vector3.zero, 0.17f, 0.15f, 0.03f, 6, woodDark);
            hanger.Cylinder(new Vector3(0, 0.03f, 0), 0.02f, 0.02f, 1.7f, 6, woodDark);
            foreach (float a in new[] { 0f, 1.57f, 3.14f, 4.71f }) hanger.Box(new Vector3(Mathf.Cos(a) * 0.1f, 1.63f, Mathf.Sin(a) * 0.1f), new Vector3(0.2f, 0.02f, 0.02f), woodDark);
            hanger.Box(new Vector3(0.1f, 1.35f, 0), new Vector3(0.1f, 0.65f, 0.34f), blanket);
            Put("Perchero", hanger, f, 5.28f, 0.5f);
            var front = Door(d, "PuertaEntrada", 6.45f, 0f, true, 95f, false);
            front.transform.rotation = Quaternion.Euler(0, 270, 0);
            // La bisagra de esta puerta está en el lado este: el marco va centrado en el hueco.
            GameObject.Find("PuertaEntrada_Marco").transform.position = new Vector3(6f, 0f, 0f);

            // Pasillo
            var hallShelf = Model("Estanteria", f, 7.6f, 4.62f, 0f, "EstanteriaPasillo") ?? Put("EstanteriaPasillo", Estanteria(), f, 7.6f, 4.62f, 180f);
            // Se mueve en el acto 2: ni ella ni sus piezas pueden ser estáticas.
            foreach (var t in hallShelf.GetComponentsInChildren<Transform>()) GameObjectUtility.SetStaticEditorFlags(t.gameObject, 0);
            var clock = new MeshKit();
            clock.Cylinder(new Vector3(0, 0, 0), 0.0f, 0.0f, 0f, 3, paper);
            clock.Box(Vector3.zero, new Vector3(0.32f, 0.32f, 0.03f), woodDark);
            clock.Box(new Vector3(0, 0, -0.018f), new Vector3(0.27f, 0.27f, 0.004f), paper);
            clock.Box(new Vector3(0, 0.05f, -0.023f), new Vector3(0.012f, 0.1f, 0.003f), plastic);
            clock.Box(new Vector3(0.04f, 0, -0.024f), new Vector3(0.08f, 0.012f, 0.003f), plastic);
            Put("Reloj", clock, f, 6.3f, 5.92f, 0f, false, 1.9f);
            Picture(f, "CuadroPasillo1", paintA, 4.7f, 1.6f, 5.92f, 0f);
            Picture(f, "CuadroPasillo2", paintB, 9.9f, 1.6f, 5.92f, 0f, 0.5f, 0.62f);
            Door(d, "PuertaFondoPasillo", 0f, 4.75f, false, 0f, true);

            RoomLight(lights, "Pasillo1", 3.5f, 5.2f, new Vector3(5.45f, 1.2f, 5.93f), 90f, new Color(1f, 0.74f, 0.46f), 2.2f);
            RoomLight(lights, "Pasillo2", 10f, 5.2f, new Vector3(9.8f, 1.2f, 4.47f), 90f, new Color(1f, 0.74f, 0.46f), 2.2f);
            RoomLight(lights, "Recibidor", 6f, 2.2f, new Vector3(6.93f, 1.2f, 0.55f), 0f, new Color(1f, 0.76f, 0.48f), 2.4f);

            Door(d, "PuertaSalonRecibidor", 5f, 2.12f, false, -95f);
            Door(d, "PuertaRecibidorPasillo", 5.6f, 4.4f, true, 95f);
        }

        static void BuildKitchen(Transform f, Transform d, Transform lights)
        {
            Put("Encimera", Encimera(), f, 10.5f, 0.38f);
            Put("Nevera", Nevera(), f, 13.45f, 0.46f);
            Put("MesaCocina", MesaCocina(), f, 11.3f, 3f);
            // El frente de la silla mira a +z: las del norte giran 180° para mirar a la mesa.
            Put("SillaCocina", Silla(), f, 10.9f, 3.55f, 180f);
            Again("SillaCocina", f, 11.7f, 3.55f, 180f);
            Again("SillaCocina", f, 10.9f, 2.45f, 0f);
            Again("SillaCocina", f, 11.7f, 2.45f, 0f);
            var cup = new MeshKit();
            cup.Cylinder(Vector3.zero, 0.035f, 0.04f, 0.1f, 8, ceramic);
            Put("Vaso", cup, f, 9.1f, 0.5f, 0, false, 0.92f);
            var plate = new MeshKit();
            plate.Cylinder(Vector3.zero, 0.1f, 0.12f, 0.02f, 10, ceramic);
            Put("Plato", plate, f, 11.1f, 3f, 0, false, 0.76f);
            RoomLight(lights, "Cocina", 11.1f, 2.2f, new Vector3(10.0f + 1.02f, 1.2f, 4.33f), 90f, new Color(0.94f, 0.97f, 0.9f), 3.2f, false, 7f);
            Door(d, "PuertaCocinaPasillo", 10f, 4.4f, true, 95f);
            Door(d, "PuertaCocinaGaraje", 14f, 2.12f, false, -95f);
        }

        static void BuildBedroom(Transform f, Transform d, Transform lights)
        {
            Put("Cama", Cama(), f, 1.1f, 8.1f, 270f);
            Put("MesillaLampara", Mesilla(true), f, 0.32f, 9.2f, 90f);
            Put("Mesilla", Mesilla(false), f, 0.32f, 7.0f, 90f);
            var closet = Put("Armario", Armario(), f, 5.62f, 8.7f, 270f, false);
            GameObjectUtility.SetStaticEditorFlags(closet, 0);
            closet.AddComponent<MeshCollider>();
            Put("ComodaDormitorio", ComodaSimple(), f, 3.2f, 9.72f, 180f);
            var rugKit = new MeshKit().Box(new Vector3(0, 0.006f, 0), new Vector3(1.6f, 0.012f, 1.1f), sheet);
            Put("AlfombraDormitorio", rugKit, f, 2.9f, 7.5f, 0, false);
            RoomLight(lights, "Dormitorio", 3f, 8f, new Vector3(3.55f, 1.2f, 6.07f), 90f, new Color(1f, 0.74f, 0.46f), 2.8f);
            Door(d, "PuertaDormitorio", 2.5f, 6f, true, -95f);
        }

        static void BuildBathroom(Transform f, Transform d, Transform lights)
        {
            Put("Banera", Banera(), f, 7.28f, 8.9f);
            Put("Lavabo", Lavabo(), f, 9.6f, 7.2f, 270f);
            var mirrorKit = new MeshKit();
            mirrorKit.Box(Vector3.zero, new Vector3(0.015f, 0.7f, 0.55f), chrome);
            mirrorKit.Box(new Vector3(-0.009f, 0, 0), new Vector3(0.004f, 0.66f, 0.51f), mirror);
            Put("Espejo", mirrorKit, f, 9.92f, 7.2f, 0, false, 1.5f);
            Put("Vater", Vater(), f, 9.4f, 9.55f, 180f);
            var towel = new MeshKit();
            towel.Box(new Vector3(0, 1.32f, 0), new Vector3(0.02f, 0.02f, 0.55f), chrome);
            towel.Box(new Vector3(-0.012f, 1.03f, 0), new Vector3(0.018f, 0.58f, 0.42f), pillow);
            Put("Toalla", towel, f, 9.93f, 8.35f, 0, false);
            var tile = new MeshKit().Box(new Vector3(0, 0.004f, 0), new Vector3(0.3f, 0.012f, 0.3f), grime);
            Put("BaldosaSuelta", tile, f, 7.6f, 7.6f, 3f, false);
            RoomLight(lights, "Bano", 8.4f, 8f, new Vector3(7.93f + 1.02f, 1.2f, 6.07f), 90f, new Color(0.94f, 0.97f, 0.9f), 2.6f, false, 6f);
            Door(d, "PuertaBano", 8f, 6f, true, -95f);
        }

        static void BuildLaundry(Transform f, Transform d, Transform lights)
        {
            Put("Lavadora", Lavadora(true), f, 10.38f, 9.05f, 90f);
            Put("Secadora", Lavadora(false), f, 10.38f, 8.4f, 90f);
            var shelf = new MeshKit();
            shelf.Box(new Vector3(0, 0, 0), new Vector3(0.3f, 0.025f, 1.5f), woodLight);
            shelf.Box(new Vector3(0, 0.35f, 0), new Vector3(0.3f, 0.025f, 1.5f), woodLight);
            shelf.Box(new Vector3(0.01f, 0.1f, -0.45f), new Vector3(0.14f, 0.18f, 0.2f), blanket);
            shelf.Box(new Vector3(0.01f, 0.13f, 0f), new Vector3(0.12f, 0.24f, 0.09f), ceramic);
            shelf.Box(new Vector3(0.01f, 0.45f, 0.35f), new Vector3(0.16f, 0.17f, 0.26f), paper);
            Put("Baldas", shelf, f, 10.21f, 8.7f, 0, false, 1.55f);
            var basket = new MeshKit();
            basket.Cylinder(Vector3.zero, 0.19f, 0.24f, 0.55f, 8, woodLight);
            basket.Cylinder(new Vector3(0, 0.55f, 0), 0.2f, 0.12f, 0.1f, 8, sheet);
            Put("Cesto", basket, f, 13.45f, 9.45f);
            var shoes = new MeshKit();
            foreach (float x in new[] { -0.07f, 0.07f })
            {
                shoes.Box(new Vector3(x, 0.03f, 0.04f), new Vector3(0.08f, 0.06f, 0.24f), plastic);
                shoes.Box(new Vector3(x, 0.07f, -0.03f), new Vector3(0.07f, 0.06f, 0.1f), plastic);
            }
            Put("ZapatosRoberta", shoes, f, 13.55f, 6.6f, 80f, false);
            RoomLight(lights, "Colada", 12f, 8f, new Vector3(12.47f, 1.2f, 6.07f), 90f, new Color(0.94f, 0.97f, 0.9f), 2.8f, false, 6f);
            Door(d, "PuertaColada", 11.5f, 6f, true, -95f);
        }

        static void BuildGarage(Transform f, Transform d, Transform lights)
        {
            var carBox = new Vector3(1.68f, 1.41f, 4.25f);
            if (ExternalCar("LandCruiser", f, 16.6f, 2.2f, 0f, "CocheChevas", 0f, false) == null && Model("CocheRojo", f, 16.6f, 2.2f, 0f, "CocheChevas", 0f, false, carBox) == null)
                Put("CocheChevas", Coche(carRed, glass, tireIn), f, 16.6f, 2.2f, 0f);
            var shelves = new MeshKit();
            foreach (float y in new[] { 0.3f, 0.95f, 1.6f }) shelves.Box(new Vector3(0, y, 0), new Vector3(1.4f, 0.03f, 0.42f), woodLight);
            foreach (float x in new[] { -0.68f, 0.68f }) shelves.Box(new Vector3(x, 0.95f, -0.18f), new Vector3(0.04f, 1.9f, 0.04f), metal);
            shelves.Box(new Vector3(-0.3f, 0.47f, 0), new Vector3(0.42f, 0.31f, 0.3f), paper);
            shelves.Cylinder(new Vector3(0.35f, 0.965f, 0), 0.09f, 0.09f, 0.2f, 8, metal);
            shelves.Box(new Vector3(-0.35f, 1.1f, 0), new Vector3(0.35f, 0.27f, 0.32f), blanket);
            Put("EstanteriaGaraje", shelves, f, 18.72f, 2.4f, 270f);
            RoomGarageWall(f);
            RoomLight(lights, "Garaje", 16.5f, 2.2f, new Vector3(14.07f, 1.2f, 3.3f), 0f, new Color(0.94f, 0.97f, 0.9f), 3.4f, false, 7f);
        }

        static void RoomGarageWall(Transform f)
        {
            // Cuadro eléctrico en la pared norte, con las latas delante: lo que dice el guion.
            var box = new MeshKit();
            box.Box(Vector3.zero, new Vector3(0.4f, 0.55f, 0.08f), metal);
            box.Box(new Vector3(0.14f, 0, -0.045f), new Vector3(0.02f, 0.08f, 0.012f), chrome);
            Put("CuadroElectrico", box, f, 14.8f, 4.28f, 0f, true, 1.05f);
            var cans = new MeshKit();
            foreach (var (x, z, h) in new[] { (0f, 0f, 0.22f), (0.26f, 0.04f, 0.22f), (0.12f, 0.22f, 0.18f), (0.14f, 0f, 0.0f) })
                if (h > 0f) cans.Cylinder(new Vector3(x, 0, z), 0.1f, 0.1f, h, 8, metal);
            Put("LatasPintura", cans, f, 14.55f, 3.92f);
            var ladder = new MeshKit();
            foreach (float x in new[] { -0.2f, 0.2f }) ladder.Box(new Vector3(x, 1.1f, 0), new Vector3(0.05f, 2.2f, 0.05f), woodLight);
            for (int i = 0; i < 7; i++) ladder.Box(new Vector3(0, 0.25f + i * 0.3f, 0), new Vector3(0.4f, 0.03f, 0.04f), woodLight);
            Put("Escalera", ladder, f, 15.6f, 4.22f);
        }

        static void BuildExterior(Transform street, Transform lights)
        {
            var g = new MeshKit();
            g.Box(new Vector3(9, -0.15f, 10), new Vector3(120, 0.2f, 120), grass);
            g.Box(new Vector3(9, -0.09f, -4.3f), new Vector3(120, 0.1f, 2.6f), asphalt);
            g.Box(new Vector3(9, -0.06f, -2.75f), new Vector3(120, 0.1f, 0.5f), concrete);
            g.Box(new Vector3(9, -0.06f, -5.85f), new Vector3(120, 0.1f, 0.5f), concrete);
            g.Box(new Vector3(6f, -0.05f, -1.2f), new Vector3(1.2f, 0.1f, 2.4f), concrete); // Camino de entrada
            g.Box(new Vector3(16.5f, -0.05f, -1.25f), new Vector3(3.2f, 0.1f, 2.5f), concrete); // Entrada de coches
            g.Box(new Vector3(7f, -0.05f, -7.3f), new Vector3(1.2f, 0.1f, 2.8f), concrete);
            Instance("Calle_Suelo", g, street, Vector3.zero, 0, false);
            var groundCollider = GameObject.Find("Calle_Suelo").AddComponent<BoxCollider>();
            groundCollider.center = new Vector3(9, -0.15f, 10); groundCollider.size = new Vector3(120, 0.2f, 120);

            // Porche
            var porch = new MeshKit();
            porch.Box(new Vector3(6f, -0.03f, -0.7f), new Vector3(3.4f, 0.12f, 1.4f), concrete);
            porch.Box(new Vector3(6f, 2.45f, -0.75f), new Vector3(3.5f, 0.1f, 1.5f), roof);
            foreach (float x in new[] { 4.45f, 7.55f }) porch.Box(new Vector3(x, 1.2f, -1.32f), new Vector3(0.1f, 2.4f, 0.1f), frameExt);
            Instance("Porche", porch, street, Vector3.zero, 0, false);

            var chechuHouse = Instance("CasaChechu", CasaFachada(siding, true), street, new Vector3(7f, 0, -9.6f));
            // Solo el cuerpo de la casa bloquea: hay que poder llegar andando hasta su puerta.
            var chechuBody = chechuHouse.GetComponent<BoxCollider>();
            chechuBody.center = new Vector3(0f, 2f, -3.65f);
            chechuBody.size = new Vector3(8.6f, 4f, 7.3f);
            Instance("CasaVecinos", CasaFachada(sidingFar, false), street, new Vector3(-5f, 0, -9.6f));
            void Inst(string name, float x, float z, float yaw)
            {
                var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>($"Assets/_Ominous/Prefabs/{name}.prefab"), street);
                go.transform.SetPositionAndRotation(new Vector3(x, 0, z), Quaternion.Euler(0, yaw, 0));
            }
            Inst("CasaVecinos", 19f, -9.6f, 0f);
            Inst("CasaVecinos", -22f, 3f, 90f);   // Junto a la ventana oeste
            Inst("CasaVecinos", 4f, 30f, 180f);   // Detrás del jardín
            Inst("CasaVecinos", 18f, 30f, 180f);
            Instance("Farola", Farola(), street, new Vector3(2f, 0, -2.6f));
            Inst("Farola", 13f, -6.1f, 180f);
            Inst("Farola", 26f, -2.6f, 0f);
            Instance("Arbol", Arbol(), street, new Vector3(-1.6f, 0, -1.2f));
            Inst("Arbol", 1.5f, -7.5f, 0f);
            Inst("Arbol", 21f, -1.6f, 30f);
            Inst("Arbol", 6f, 15.5f, 60f);
            Inst("Arbol", 13f, 19f, 110f);
            Inst("Arbol", -6f, 9f, 200f);
            var streetCarBox = new Vector3(1.68f, 1.41f, 4.25f);
            if (ExternalCar("GMCSierra", street, 11.2f, -3.45f, 90f, "CocheAzul", -0.04f, true) == null && Model("CocheAzul", street, 11.2f, -3.45f, 90f, null, -0.04f, true, streetCarBox) == null)
                Instance("CocheAzul", Coche(carBlue, carGlass, tire), street, new Vector3(11.2f, -0.04f, -3.45f), 90f);
            if (ExternalCar("LandCruiser", street, -2.5f, -5.15f, 270f, "CocheGris", -0.04f, true) == null && Model("CocheGris", street, -2.5f, -5.15f, 270f, null, -0.04f, true, streetCarBox) == null)
                Instance("CocheGris", Coche(carGrey, carGlass, tire), street, new Vector3(-2.5f, -0.04f, -5.15f), 270f);
            // Valla del jardín
            var fence = new MeshKit();
            fence.Box(new Vector3(7, 0.9f, 22), new Vector3(46, 0.05f, 0.03f), fenceWood);
            fence.Box(new Vector3(7, 0.45f, 22), new Vector3(46, 0.05f, 0.03f), fenceWood);
            for (int i = 0; i < 24; i++) fence.Box(new Vector3(-15f + i * 2f, 0.55f, 22f), new Vector3(0.08f, 1.1f, 0.08f), fenceWood);
            Instance("Valla", fence, street, Vector3.zero, 0, false);
            foreach (var t in street.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = ExteriorLayer;

            // Farolas: tiempo real con sombra, para que entren por las ventanas sin atravesar paredes
            foreach (var (x, z) in new[] { (2.2f, -1.8f), (13f, -5.2f), (26f, -1.8f) })
            {
                var l = SpotLight("LuzFarola", lights, new Vector3(x, 4.4f, z), Quaternion.Euler(90, 0, 0), new Color(1f, 0.72f, 0.42f), 30f, 11f, 125f, ~0);
                l.shadows = LightShadows.Soft;
            }
        }

        static AudioSource BuildSound()
        {
            AudioSource Loop(string name, AudioClip clip, Vector3 pos, float volume, float maxDistance)
            {
                var go = new GameObject(name);
                go.transform.position = pos;
                var s = go.AddComponent<AudioSource>();
                s.clip = clip; s.loop = true; s.volume = volume; s.playOnAwake = true;
                s.spatialBlend = maxDistance > 0f ? 1f : 0f;
                s.rolloffMode = AudioRolloffMode.Linear;
                s.minDistance = 0.8f;
                s.maxDistance = maxDistance > 0f ? maxDistance : 500f;
                return s;
            }
            var root = new GameObject("Sonido").transform;
            Loop("Nevera", AudioGen.Fridge(), new Vector3(13.45f, 0.9f, 0.5f), 0.32f, 8f).transform.SetParent(root);
            Loop("Reloj", AudioGen.Clock(), new Vector3(6.3f, 1.9f, 5.9f), 0.2f, 7f).transform.SetParent(root);
            Loop("Viento", AudioGen.Wind(), Vector3.zero, 0.12f, 0f).transform.SetParent(root);
            // La tele va sin sonido por ahora: sonaba demasiado fuerte y el sonido llega en el pulido.
            AudioSource tvAudio = null;
            var drip = Loop("Grifo", AudioGen.Drip(), new Vector3(9.6f, 0.9f, 7.1f), 0.28f, 5f);
            drip.transform.SetParent(root);
            var cars = new GameObject("Coches");
            cars.transform.SetParent(root);
            var src = cars.AddComponent<AudioSource>();
            src.spatialBlend = 0f;
            var a = cars.AddComponent<AmbientSounds>();
            a.carSource = src;
            a.carClip = AudioGen.Car();

            var sfx = root.gameObject.AddComponent<Sfx>();
            void Add(string name, AudioClip clip, float volume) => sfx.clips.Add(new Sfx.Entry { name = name, clip = clip, volume = volume });
            Add("llamada_puerta", AudioGen.Knock(), 0.95f);
            Add("llamada_puerta_suave", AudioGen.Knock(), 0.45f);
            Add("puerta_abre", AudioGen.Latch(), 0.5f);
            Add("puerta_cierra", AudioGen.SoftThud(), 0.6f);
            Add("puerta_cerrada", AudioGen.Rattle(), 0.5f);
            Add("interruptor", AudioGen.Click(), 0.45f);
            Add("llaves", AudioGen.Keys(), 0.5f);
            Add("paso", AudioGen.Step(), 0.22f);
            // Provisionales: el sonido definitivo llega en el pulido.
            Add("objeto_cae", AudioGen.SoftThud(), 0.75f);
            Add("golpe_armario", AudioGen.Knock(), 0.8f);
            Add("llave_se_parte", AudioGen.Rattle(), 0.85f);
            Add("tuberia_golpe", AudioGen.SoftThud(), 0.7f);
            Add("risa", AudioGen.Laugh(), 0.75f);
            return tvAudio;
        }

        static void BuildPlayerAndSystems()
        {
            var settings = AssetDatabase.LoadAssetAtPath<VideoLookSettings>(OminousSetup.SettingsPath);
            var player = new GameObject("Jugador");
            player.transform.SetPositionAndRotation(new Vector3(6f, 0.02f, -2.2f), Quaternion.identity);
            var cc = player.AddComponent<CharacterController>();
            cc.height = 1.7f; cc.radius = 0.25f; cc.center = new Vector3(0, 0.85f, 0); cc.stepOffset = 0.2f; cc.skinWidth = 0.02f;
            var fp = player.AddComponent<FirstPersonController>();
            var camGo = new GameObject("Camara");
            camGo.tag = "MainCamera";
            camGo.transform.SetParent(player.transform);
            camGo.transform.localPosition = new Vector3(0, 1.6f, 0);
            var cam = camGo.AddComponent<Camera>();
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = settings.exteriorFogColor;
            cam.fieldOfView = 62f;
            cam.nearClipPlane = 0.05f;
            cam.farClipPlane = 80f;
            camGo.AddComponent<AudioListener>();
            var data = cam.GetUniversalAdditionalCameraData();
            data.renderPostProcessing = true;
            // Suaviza el parpadeo de las líneas finas, como los marcos, a baja resolución.
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            data.antialiasingQuality = AntialiasingQuality.Low;
            fp.cameraPivot = camGo.transform;
            var interactor = player.AddComponent<PlayerInteractor>();
            interactor.eye = camGo.transform;

            var look = new GameObject("Imagen");
            var controller = look.AddComponent<VideoLookController>();
            controller.settings = settings;
            var volume = look.AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = OminousSetup.BuildVolumeProfile();
            look.AddComponent<VideoLookPanel>().controller = controller;

            var systems = new GameObject("Sistemas");
            systems.AddComponent<GameDirector>();
            systems.AddComponent<GameUI>();
            systems.AddComponent<PauseMenu>();
            systems.AddComponent<DialogueManager>().project = AssetDatabase.LoadAssetAtPath<YarnProject>(YarnProjectPath);
        }

        // ---------- historia ----------

        static MeshKit Person(Material skin, Material top, Material legs, Material hair, string pose)
        {
            var k = new MeshKit();
            void Head(Vector3 c)
            {
                k.Box(c, new Vector3(0.17f, 0.22f, 0.2f), skin);
                k.Box(c + new Vector3(0, 0.07f, -0.02f), new Vector3(0.19f, 0.13f, 0.21f), hair);
                k.Box(c + new Vector3(0, -0.02f, -0.09f), new Vector3(0.19f, 0.26f, 0.05f), hair);
            }
            if (pose == "depie")
            {
                foreach (float x in new[] { -0.09f, 0.09f })
                {
                    k.Box(new Vector3(x, 0.41f, 0), new Vector3(0.13f, 0.82f, 0.15f), legs);
                    k.Box(new Vector3(x, 0.035f, 0.04f), new Vector3(0.11f, 0.07f, 0.25f), plastic);
                    k.Box(new Vector3(x * 2.85f, 1.07f, 0), new Vector3(0.085f, 0.58f, 0.1f), top);
                    k.Box(new Vector3(x * 2.85f, 0.73f, 0.01f), new Vector3(0.08f, 0.1f, 0.09f), skin);
                }
                k.Box(new Vector3(0, 1.09f, 0), new Vector3(0.36f, 0.56f, 0.2f), top);
                k.Box(new Vector3(0, 1.41f, 0), new Vector3(0.08f, 0.1f, 0.08f), skin);
                Head(new Vector3(0, 1.56f, 0));
            }
            else if (pose == "sentada")
            {
                foreach (float x in new[] { -0.09f, 0.09f })
                {
                    k.Box(new Vector3(x, 0.55f, 0.18f), new Vector3(0.13f, 0.14f, 0.42f), legs);
                    k.Box(new Vector3(x, 0.24f, 0.36f), new Vector3(0.12f, 0.48f, 0.13f), legs);
                    k.Box(new Vector3(x, 0.035f, 0.4f), new Vector3(0.11f, 0.07f, 0.24f), plastic);
                    k.Box(new Vector3(x * 2.85f, 0.73f, 0.03f), new Vector3(0.085f, 0.42f, 0.1f), top);
                    k.Box(new Vector3(x * 2.3f, 0.57f, 0.2f), new Vector3(0.08f, 0.08f, 0.26f), skin);
                }
                k.Box(new Vector3(0, 0.82f, -0.05f), new Vector3(0.36f, 0.56f, 0.2f), top);
                k.Box(new Vector3(0, 1.14f, -0.03f), new Vector3(0.08f, 0.1f, 0.08f), skin);
                Head(new Vector3(0, 1.29f, -0.01f));
            }
            else // tumbada, de lado y con la cabeza hacia +z
            {
                k.Box(new Vector3(0, 0.13f, -0.55f), new Vector3(0.3f, 0.17f, 0.92f), legs);
                k.Box(new Vector3(0, 0.15f, 0.2f), new Vector3(0.36f, 0.2f, 0.56f), top);
                k.Box(new Vector3(0.21f, 0.14f, 0.16f), new Vector3(0.09f, 0.1f, 0.5f), top);
                k.Box(new Vector3(0, 0.14f, 0.52f), new Vector3(0.09f, 0.08f, 0.1f), skin);
                k.Box(new Vector3(0, 0.18f, 0.68f), new Vector3(0.2f, 0.17f, 0.22f), skin);
                k.Box(new Vector3(0, 0.26f, 0.66f), new Vector3(0.21f, 0.1f, 0.25f), hair);
                k.Box(new Vector3(0, 0.14f, 0.8f), new Vector3(0.21f, 0.2f, 0.05f), hair);
            }
            return k;
        }

        static GameObject Actor(string name, Material skin, Material top, Material legs, Material hair, string[] poses, Vector3 colliderSize, out ActorFigure figure)
        {
            var root = new GameObject(name);
            figure = root.AddComponent<ActorFigure>();
            foreach (string pose in poses)
            {
                var mesh = Person(skin, top, legs, hair, pose).Build($"{name}_{pose}", out var mats);
                string path = $"Assets/_Ominous/Art/Meshes/{name}_{pose}.asset";
                AssetDatabase.DeleteAsset(path);
                AssetDatabase.CreateAsset(mesh, path);
                var go = new GameObject(pose);
                go.transform.SetParent(root.transform, false);
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                go.AddComponent<MeshRenderer>().sharedMaterials = mats;
                figure.poses.Add(new ActorFigure.Pose { name = pose, root = go });
            }
            var head = new GameObject("Cabeza");
            head.transform.SetParent(root.transform, false);
            head.transform.localPosition = new Vector3(0, 1.45f, 0);
            figure.head = head.transform;
            var col = root.AddComponent<BoxCollider>();
            col.isTrigger = true;
            col.center = new Vector3(0, colliderSize.y * 0.5f, 0);
            col.size = colliderSize;
            return root;
        }

        static void Use(string id, string prompt, Vector3 position, Vector3 size, Transform parent)
        {
            var go = new GameObject("Uso_" + id);
            go.transform.SetParent(parent);
            go.transform.position = position;
            var c = go.AddComponent<BoxCollider>();
            c.isTrigger = true;
            c.size = size;
            var s = go.AddComponent<StoryObject>();
            s.id = id;
            s.prompt = prompt;
        }

        static void BuildStory(AudioSource tvAudio)
        {
            var skin = ProceduralAssets.Grime("Piel", new Color(0.62f, 0.47f, 0.38f), 0.2f);
            var pajama = ProceduralAssets.Fabric("Pijama", new Color(0.46f, 0.5f, 0.54f));
            var pajamaLegs = ProceduralAssets.Fabric("PijamaPantalon", new Color(0.36f, 0.4f, 0.45f));
            var hairR = ProceduralAssets.Grime("PeloRoberta", new Color(0.16f, 0.1f, 0.07f), 0.3f);
            var jacket = ProceduralAssets.Fabric("Chaqueta", new Color(0.24f, 0.27f, 0.23f));
            var jeans = ProceduralAssets.Fabric("Vaqueros", new Color(0.18f, 0.2f, 0.26f));
            var hairC = ProceduralAssets.Grime("PeloChechu", new Color(0.07f, 0.06f, 0.05f), 0.3f);

            var story = new GameObject("Historia");
            Actor("Roberta", skin, pajama, pajamaLegs, hairR, new[] { "sentada", "depie", "tumbada" }, new Vector3(0.7f, 1.3f, 1f), out var roberta);
            roberta.gameObject.AddComponent<StoryObject>().id = "roberta";
            roberta.head.localPosition = new Vector3(0, 1.25f, 0);
            Actor("Chechu", skin, jacket, jeans, hairC, new[] { "depie" }, new Vector3(0.6f, 1.75f, 0.5f), out var chechu);
            ExternalCharacter(chechu, "depie", "Assets/_Ominous/Art/Externos/Chechu/ChickenMan", 1.75f, skin);

            var t = story.transform;
            Use("cuenco", "Dejar las llaves", new Vector3(6.8f, 0.87f, 1.7f), new Vector3(0.26f, 0.14f, 0.26f), t);
            Use("vaso", "Beber agua", new Vector3(9.1f, 1.0f, 0.5f), new Vector3(0.3f, 0.3f, 0.3f), t);
            Use("grifo", "Mirar el grifo", new Vector3(9.5f, 0.95f, 7.2f), new Vector3(0.45f, 0.3f, 0.5f), t);
            Use("tele", "Mirar la tele", new Vector3(2.15f, 0.85f, 3.82f), new Vector3(0.8f, 0.6f, 0.1f), t);
            Use("nevera", "Abrir la nevera", new Vector3(13.45f, 1.1f, 0.85f), new Vector3(0.75f, 1.4f, 0.1f), t);
            Use("ventana", "Mirar por la ventana", new Vector3(3.7f, 1.5f, 0.12f), new Vector3(1.4f, 1.2f, 0.1f), t);
            Use("ventana", "Mirar por la ventana", new Vector3(1.6f, 1.5f, 0.12f), new Vector3(1.4f, 1.2f, 0.1f), t);
            Use("cama", "Intentar dormir", new Vector3(1.1f, 0.7f, 8.1f), new Vector3(2.1f, 0.8f, 1.6f), t);
            Use("mirilla", "Mirar por la mirilla", new Vector3(6f, 1.6f, 0.05f), new Vector3(0.35f, 0.3f, 0.1f), t);

            // Umbral: en la visita el jugador no sale a la calle
            var threshold = new GameObject("UmbralPuerta");
            threshold.transform.SetParent(t);
            threshold.transform.position = new Vector3(6f, 1f, -0.1f);
            threshold.AddComponent<BoxCollider>().size = new Vector3(1.2f, 2.2f, 0.2f);

            // Límites del jardín en la llegada
            var bounds = new GameObject("LimitesLlegada");
            bounds.transform.SetParent(t);
            foreach (var (c, size) in new[]
            {
                (new Vector3(6f, 1f, -2.95f), new Vector3(8f, 2f, 0.2f)),
                (new Vector3(2.5f, 1f, -1.3f), new Vector3(0.2f, 2f, 3.3f)),
                (new Vector3(8.5f, 1f, -1.3f), new Vector3(0.2f, 2f, 3.3f)),
            })
            {
                var w = new GameObject("Limite");
                w.transform.SetParent(bounds.transform);
                w.transform.position = c;
                w.AddComponent<BoxCollider>().size = size;
            }

            var dir = story.AddComponent<StoryDirector>();
            BuildAct2(dir, t);
            BuildAct3(dir, t);
            dir.frontDoor = GameObject.Find("PuertaEntrada").GetComponent<Door>();
            dir.roberta = roberta;
            dir.chechu = chechu;
                        dir.tvSound = tvAudio;
            dir.tvFill = GameObject.Find("LuzTeleResplandor").GetComponent<Light>();
            dir.threshold = threshold;
            dir.outsideBounds = bounds;
            dir.project = AssetDatabase.LoadAssetAtPath<YarnProject>(YarnProjectPath);

            // Luces al llegar: recibidor y lámpara del salón encendidas, como las dejó Roberta
            var hall = GameObject.Find("Interruptor_Recibidor").GetComponent<LightSwitch>();
            hall.isOn = true;
        }

        static void BuildAct3(StoryDirector dir, Transform t)
        {
            // Reloj parado a las 3:33
            dir.clockNormal = GameObject.Find("Reloj");
            var stopped = new MeshKit();
            stopped.Box(Vector3.zero, new Vector3(0.32f, 0.32f, 0.03f), woodDark);
            stopped.Box(new Vector3(0, 0, -0.018f), new Vector3(0.27f, 0.27f, 0.004f), paper);
            stopped.Box(new Vector3(0.04f, 0.005f, -0.023f), new Vector3(0.08f, 0.012f, 0.003f), plastic);   // Horas: las tres y media larga
            stopped.Box(new Vector3(-0.015f, -0.05f, -0.024f), new Vector3(0.012f, 0.1f, 0.003f), plastic);  // Minutos: y treinta y tres
            dir.clockStopped = Instance("RelojParado", stopped, t, new Vector3(6.3f, 1.9f, 5.92f), 0f, false);

            // Una puerta de más en el pasillo
            var fake = new MeshKit();
            fake.Box(new Vector3(0, 1f, 0), new Vector3(0.86f, 2f, 0.03f), door);
            fake.Box(new Vector3(0.34f, 0.95f, -0.03f), new Vector3(0.1f, 0.03f, 0.05f), metal);
            fake.Box(new Vector3(0, 2.03f, 0), new Vector3(1.02f, 0.07f, 0.05f), frame);
            fake.Box(new Vector3(-0.46f, 1f, 0), new Vector3(0.07f, 2f, 0.05f), frame);
            fake.Box(new Vector3(0.46f, 1f, 0), new Vector3(0.07f, 2f, 0.05f), frame);
            var extra = Instance("PuertaDeMas", fake, t, new Vector3(5f, 0f, 5.92f), 0f, false);
            dir.extraDoor = extra;
            var extraUse = extra.AddComponent<BoxCollider>();
            extraUse.center = new Vector3(0, 1f, 0); extraUse.size = new Vector3(0.9f, 2f, 0.15f);
            var extraStory = extra.AddComponent<StoryObject>();
            extraStory.id = "puerta_de_mas"; extraStory.prompt = "Abrir";

            // Pasillo largo: sale por la puerta del fondo y sigue donde no debería haber nada
            var hall = new MeshKit();
            const float len = 16f;
            hall.Box(new Vector3(-len / 2, -0.05f, 5.2f), new Vector3(len, 0.1f, 1.72f), floorWood);
            hall.Box(new Vector3(-len / 2, Height + 0.05f, 5.2f), new Vector3(len, 0.1f, 1.72f), ceiling);
            hall.Box(new Vector3(-len / 2, Height / 2, 4.4f), new Vector3(len, Height, Thick), wall);
            hall.Box(new Vector3(-len / 2, Height / 2, 6f), new Vector3(len, Height, Thick), wall);
            // Pared del fondo, con el hueco de la puerta al vacío
            hall.Box(new Vector3(-len, Height / 2, 4.57f), new Vector3(Thick, Height, 0.46f), wall);
            hall.Box(new Vector3(-len, Height / 2, 5.83f), new Vector3(Thick, Height, 0.46f), wall);
            hall.Box(new Vector3(-len, 2.3f, 5.2f), new Vector3(Thick, 0.6f, 0.9f), wall);
            var hallGo = Instance("PasilloLargo", hall, t, Vector3.zero, 0f, false);
            hallGo.AddComponent<MeshCollider>();
            dir.longHall = hallGo;
            var endDoor = Door(hallGo.transform, "PuertaAlVacio", -len, 4.75f, false, 95f, true);
            dir.voidDoor = endDoor.GetComponent<Door>();
            dir.streetRoot = GameObject.Find("Calle");
            dir.hallSwitch = GameObject.Find("Interruptor_Recibidor").GetComponent<LightSwitch>();
            dir.lampSwitch = GameObject.Find("Interruptor_Salon").GetComponent<LightSwitch>();
            Use("llamar", "Llamar a la puerta", new Vector3(6f, 1.1f, -0.14f), new Vector3(0.9f, 1.9f, 0.08f), t);
            GameObjectUtility.SetStaticEditorFlags(endDoor, 0);
            var hallLight = SpotLight("LuzPasilloLargo", hallGo.transform, new Vector3(-len / 2, 2.45f, 5.2f), Quaternion.Euler(90, 0, 0), new Color(1f, 0.72f, 0.42f), 1.4f, 5f, 150f, ~0);
            hallLight.shadows = LightShadows.None;
            dir.hallDoor = GameObject.Find("PuertaFondoPasillo").GetComponent<Door>();
            dir.hallDoor.openYaw = -95f;

            // Lo que cambia fuera: falta una farola
            var street = GameObject.Find("Calle").transform;
            foreach (Transform child in street)
                if (child.name == "Farola" && Mathf.Abs(child.position.x - 13f) < 0.5f) dir.streetLampMissing = child.gameObject;
            foreach (var l in GameObject.Find("Luces").GetComponentsInChildren<Light>())
                if (l.name == "LuzFarola" && Mathf.Abs(l.transform.position.x - 13f) < 0.5f) dir.streetLampLight = l;

            dir.bathLight = GameObject.Find("Luz_Bano").GetComponent<Light>();
            dir.dripSound = GameObject.Find("Grifo").GetComponent<AudioSource>();

            // Puerta del sótano en la colada
            var cellarDoor = Instance("PuertaSotano", fake, t, new Vector3(13.92f, 0f, 6.65f), 90f, false);
            dir.basementDoor = cellarDoor;
            var cellarUse = cellarDoor.AddComponent<BoxCollider>();
            cellarUse.center = new Vector3(0, 1f, 0); cellarUse.size = new Vector3(0.9f, 2f, 0.15f);
            var cellarStory = cellarDoor.AddComponent<StoryObject>();
            cellarStory.id = "puerta_sotano"; cellarStory.prompt = "Abrir";
            
            // Sótano: copia del dormitorio, muy lejos del resto
            Vector3 o = new(40f, -40f, 0f);
            var root = new GameObject("Sotano").transform;
            root.position = o;
            var shell = new MeshKit();
            shell.Box(new Vector3(3f, -0.05f, 8f), new Vector3(6.24f, 0.1f, 4.24f), floorWood);
            shell.Box(new Vector3(3f, Height + 0.05f, 8f), new Vector3(6.24f, 0.1f, 4.24f), ceiling);
            shell.Box(new Vector3(0f, Height / 2, 8f), new Vector3(Thick, Height, 4.24f), wall);
            // Pared este con el hueco de la escalera (z 8,3 a 9,2)
            shell.Box(new Vector3(6f, Height / 2, 7.09f), new Vector3(Thick, Height, 2.42f), wall);
            shell.Box(new Vector3(6f, Height / 2, 9.66f), new Vector3(Thick, Height, 0.92f), wall);
            // El dintel queda alto: en los primeros peldaños la cabeza ya pasa de 2 m.
            shell.Box(new Vector3(6f, 2.5f, 8.75f), new Vector3(Thick, 0.2f, 0.9f), wall);
            shell.Box(new Vector3(3f, Height / 2, 10f), new Vector3(6.24f, Height, Thick), wall);
            shell.Box(new Vector3(3f, Height / 2, 6f), new Vector3(6.24f, Height, Thick), wall);
            var shellGo = Instance("Sotano_Estructura", shell, root, o, 0f, false);
            shellGo.AddComponent<MeshCollider>();
            GameObject Copy(string prefab, float x, float z, float yaw, float y = 0f)
            {
                var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>($"Assets/_Ominous/Prefabs/{prefab}.prefab"), root);
                go.transform.SetPositionAndRotation(o + new Vector3(x, y, z), Quaternion.Euler(0, yaw, 0));
                return go;
            }
            Copy("Cama", 1.1f, 8.1f, 270f);
            Copy("MesillaLampara", 0.32f, 9.2f, 90f);
            Copy("Mesilla", 0.32f, 7f, 90f);
            Copy("ComodaDormitorio", 3.2f, 9.72f, 180f);
            Copy("AlfombraDormitorio", 2.9f, 7.5f, 0f);
            // Las mismas cortinas, sobre una pared sin ventana
            var fakeWindow = new MeshKit();
            fakeWindow.Box(new Vector3(0, 0, 0), new Vector3(1.4f, 1.2f, 0.01f), wall);
            foreach (float x in new[] { -0.72f, 0.72f }) fakeWindow.Box(new Vector3(x, -0.1f, -0.03f), new Vector3(0.28f, 1.45f, 0.05f), curtain);
            fakeWindow.Box(new Vector3(0, 0.7f, -0.04f), new Vector3(2.1f, 0.03f, 0.03f), metal);
            Instance("CortinasSotano", fakeWindow, root, o + new Vector3(4.2f, 1.5f, 9.93f), 180f, false);
            var photos = new MeshKit();
            var rng = new System.Random(3);
            for (int i = 0; i < 14; i++)
            {
                float x = (i % 7 - 3) * 0.32f + (float)rng.NextDouble() * 0.06f, y = (i / 7) * 0.4f + (float)rng.NextDouble() * 0.08f;
                photos.Box(new Vector3(x, y, 0), new Vector3(0.22f, 0.3f, 0.006f), paper);
                photos.Box(new Vector3(x, y, -0.004f), new Vector3(0.18f, 0.13f, 0.002f), plastic);
            }
            Instance("FotosSotano", photos, root, o + new Vector3(3f, 1.2f, 6.07f), 180f, false);
            var note = new MeshKit().Box(Vector3.zero, new Vector3(0.14f, 0.012f, 0.2f), paper);
            Instance("Libreta", note, root, o + new Vector3(0.34f, 0.55f, 9.15f), 10f, false);
            void UseAt(string id, string prompt, Vector3 p, Vector3 size)
            {
                var go = new GameObject("Uso_" + id);
                go.transform.SetParent(root);
                go.transform.position = o + p;
                var c = go.AddComponent<BoxCollider>(); c.isTrigger = true; c.size = size;
                var s = go.AddComponent<StoryObject>(); s.id = id; s.prompt = prompt;
            }
            UseAt("fotos", "Mirar las fotos", new Vector3(3f, 1.4f, 6.1f), new Vector3(2.4f, 1.1f, 0.1f));
            UseAt("libreta", "Leer la libreta", new Vector3(0.34f, 0.62f, 9.15f), new Vector3(0.4f, 0.25f, 0.45f));
            // Escalera estrecha: baja de verdad desde la puerta de arriba hasta el dormitorio copiado
            const int steps = 14;
            const float rise = 0.18f, run = 0.28f, stairZ = 8.75f, stairWidth = 0.9f;
            float topY = steps * rise, landingX = 6.06f + steps * run;
            float wallTop = topY + 2.4f, wallLength = landingX + 1f - 6f;
            var stairs = new MeshKit();
            for (int i = 0; i < steps; i++)
            {
                float x = 6.06f + (i + 0.5f) * run, y = (i + 1) * rise;
                stairs.Box(new Vector3(x, y / 2f, stairZ), new Vector3(run, y, stairWidth), woodLight);
                // Techo en escalones, macizo hasta arriba para que no queden huecos.
                float ceilingY = y + 2.2f;
                stairs.Box(new Vector3(x, (ceilingY + wallTop) / 2f, stairZ), new Vector3(run, wallTop - ceilingY, stairWidth + 0.2f), ceiling);
            }
            stairs.Box(new Vector3(landingX + 0.5f, topY / 2f, stairZ), new Vector3(1f, topY, stairWidth), woodLight);
            stairs.Box(new Vector3(landingX + 0.5f, topY + 2.25f, stairZ), new Vector3(1f, 0.1f, stairWidth + 0.2f), ceiling);
            stairs.Box(new Vector3(6f + wallLength / 2f, wallTop / 2f, stairZ - stairWidth / 2f - 0.05f), new Vector3(wallLength, wallTop, 0.1f), wall);
            stairs.Box(new Vector3(6f + wallLength / 2f, wallTop / 2f, stairZ + stairWidth / 2f + 0.05f), new Vector3(wallLength, wallTop, 0.1f), wall);
            stairs.Box(new Vector3(landingX + 1.05f, wallTop / 2f, stairZ), new Vector3(0.1f, wallTop, stairWidth + 0.2f), wall);
            var stairsGo = Instance("EscaleraSotano", stairs, root, o, 0f, false);
            stairsGo.AddComponent<MeshCollider>();
            var topLeaf = Copy("PuertaHoja", landingX + 0.98f, stairZ - 0.43f, 0f, topY);
            Object.DestroyImmediate(topLeaf.GetComponent<BoxCollider>());
            Copy("PuertaMarco", landingX + 0.98f, stairZ, 0f, topY);
            UseAt("salir_sotano", "Abrir", new Vector3(landingX + 0.92f, topY + 1f, stairZ), new Vector3(0.1f, 2f, 0.9f));
            var stairLight = Point("LuzEscalera", root, o + new Vector3(landingX + 0.3f, topY + 2f, stairZ), new Color(1f, 0.72f, 0.42f), 0.35f, 3.5f);
            Point("LuzEscaleraMedia", root, o + new Vector3(8f, 1.26f + 1.9f, stairZ), new Color(1f, 0.72f, 0.42f), 0.3f, 3.5f);
            var bulb = SpotLight("LuzSotano", root, o + new Vector3(3f, 2.45f, 8f), Quaternion.Euler(90, 0, 0), new Color(1f, 0.72f, 0.42f), 2f, 6f, 165f, ~0);
            bulb.shadows = LightShadows.Soft;
var arrival = new GameObject("LlegadaSotano");
            arrival.transform.SetParent(root);
            arrival.transform.SetPositionAndRotation(o + new Vector3(landingX + 0.45f, topY + 0.05f, stairZ), Quaternion.Euler(0, 270, 0));
            dir.basementArrival = arrival.transform;
            dir.basementRoot = root.gameObject;
            root.gameObject.SetActive(false);
        }

        static void BuildAct2(StoryDirector dir, Transform t)
        {
            // Llave inglesa encima de las latas del garaje, y el bote que cae
            var wrenchKit = new MeshKit();
            wrenchKit.Box(Vector3.zero, new Vector3(0.28f, 0.015f, 0.03f), chrome);
            wrenchKit.Box(new Vector3(0.14f, 0, 0), new Vector3(0.05f, 0.016f, 0.07f), chrome);
            var wr = Instance("LlaveInglesa", wrenchKit, t, new Vector3(14.62f, 0.235f, 3.92f), 20f, false);
            dir.wrench = wr;
            Use("llave", "Coger la llave inglesa", new Vector3(14.62f, 0.3f, 3.92f), new Vector3(0.5f, 0.35f, 0.4f), wr.transform);
            var canKit = new MeshKit().Cylinder(Vector3.zero, 0.06f, 0.06f, 0.15f, 8, metal);
            dir.fallenCan = Instance("BoteCaido", canKit, t, new Vector3(15.1f, 0.06f, 3.3f), 0f, false);
            dir.fallenCan.transform.rotation = Quaternion.Euler(90f, 30f, 0f);

            // Baldosa floja
            Use("baldosa", "Pisar la baldosa", new Vector3(7.6f, 0.03f, 7.6f), new Vector3(0.4f, 0.1f, 0.4f), t);

            // Armario de cocina abierto: aparece con el susto
            var cab = new MeshKit().Box(new Vector3(-0.25f, 0f, 0f), new Vector3(0.5f, 0.68f, 0.02f), woodDark);
            dir.kitchenCabinetOpen = Instance("HojaArmarioCocina", cab, t, new Vector3(9.3f, 1.82f, 0.46f), 70f, false);

            // Cuadro nuevo: esta casa vista desde enfrente
            var houseArt = ProceduralAssets.Painting("CuadroCasa", new Color(0.24f, 0.26f, 0.3f), new Color(0.42f, 0.42f, 0.38f));
            var pictureKit = new MeshKit();
            pictureKit.Box(Vector3.zero, new Vector3(0.62f, 0.47f, 0.03f), woodDark);
            pictureKit.Box(new Vector3(0, 0, -0.018f), new Vector3(0.54f, 0.39f, 0.006f), houseArt);
            pictureKit.Box(new Vector3(0, -0.04f, -0.022f), new Vector3(0.34f, 0.15f, 0.003f), siding);
            pictureKit.Box(new Vector3(0, 0.05f, -0.022f), new Vector3(0.38f, 0.05f, 0.003f), roof);
            pictureKit.Box(new Vector3(0, -0.06f, -0.024f), new Vector3(0.05f, 0.11f, 0.003f), plastic);
            dir.newPicture = Instance("CuadroCasa", pictureKit, t, new Vector3(2.3f, 1.6f, 5.92f), 0f, false);

            // Foto de la boda en la estantería del pasillo y su copia en el suelo
            var photo = new MeshKit();
            photo.Box(Vector3.zero, new Vector3(0.16f, 0.21f, 0.015f), woodLight);
            photo.Box(new Vector3(0, 0, -0.009f), new Vector3(0.13f, 0.18f, 0.003f), paper);
            dir.photoOnShelf = Instance("FotoBoda", photo, t, new Vector3(7.9f, 1.05f, 4.55f), 180f, false);
            dir.photoOnFloor = Instance("FotoBodaSuelo", photo, t, new Vector3(7.4f, 0.02f, 4.95f), 0f, false);
            dir.photoOnFloor.transform.rotation = Quaternion.Euler(90f, 25f, 0f);
            var pick = new GameObject("Uso_foto_suelo");
            pick.transform.SetParent(dir.photoOnFloor.transform, false);
            var pc = pick.AddComponent<BoxCollider>(); pc.isTrigger = true; pc.size = new Vector3(0.4f, 0.4f, 0.2f);
            var ps = pick.AddComponent<StoryObject>(); ps.id = "foto_suelo"; ps.prompt = "Recoger la foto";
            Use("foto_balda", "Poner la foto en la estantería", new Vector3(7.6f, 1.15f, 4.72f), new Vector3(0.9f, 1.4f, 0.1f), t);

            // Estantería del pasillo: primero cede un poco; luego se aparta
            var shelfRoot = GameObject.Find("EstanteriaPasillo");
            dir.shelfNudge = shelfRoot.AddComponent<SimpleHinge>();
            dir.shelfNudge.openOffset = new Vector3(0f, 0f, 0.06f);
            dir.shelfNudge.openYaw = 3f;
            dir.shelfNudge.seconds = 0.5f;
            dir.shelfAside = shelfRoot.AddComponent<SimpleHinge>();
            dir.shelfAside.openOffset = new Vector3(1.05f, 0f, 0.03f);
            dir.shelfAside.openYaw = -3f;
            dir.shelfAside.seconds = 2.2f;
            Use("estanteria", "Apartar la estantería", new Vector3(7.6f, 1f, 4.82f), new Vector3(1f, 1.8f, 0.1f), t);

            // Habitación oculta 1
            var room1 = new GameObject("Habitacion1").transform;
            room1.SetParent(t);
            Again("SillaCocina", room1, 7.6f, 2.4f, 270f);
            var blanket1 = new MeshKit().Box(new Vector3(0, 0.03f, 0), new Vector3(0.7f, 0.06f, 1.5f), blanket);
            Instance("MantaCuartito", blanket1, room1, new Vector3(7.65f, 0, 1.0f), 0f, false);
            var cansRoom = new MeshKit();
            foreach (var (x, z) in new[] { (0f, 0f), (0.12f, 0.1f), (-0.1f, 0.16f), (0.05f, 0.28f) })
                cansRoom.Cylinder(new Vector3(x, 0, z), 0.04f, 0.04f, 0.11f, 7, metal);
            Instance("LatasCuartito", cansRoom, room1, new Vector3(7.5f, 0, 3.4f), 0f, false);
            var coat = new MeshKit();
            coat.Box(new Vector3(0, 0, 0), new Vector3(0.1f, 0.68f, 0.42f), ProceduralAssets.Fabric("Chaqueta", new Color(0.24f, 0.27f, 0.23f)));
            coat.Box(new Vector3(0.06f, 0.3f, 0), new Vector3(0.03f, 0.03f, 0.03f), metal);
            Instance("ChaquetaColgada", coat, room1, new Vector3(8.09f, 1.3f, 3.0f), 0f, false);
            Use("chaqueta", "Mirar la chaqueta", new Vector3(8.05f, 1.2f, 3f), new Vector3(0.25f, 0.9f, 0.6f), t);
            Use("silla", "Mirar la silla", new Vector3(7.6f, 0.6f, 2.4f), new Vector3(0.5f, 1.2f, 0.5f), t);

            // Armario del dormitorio con su fondo falso: hojas y fondo en piezas móviles
            var closet = GameObject.Find("Armario").transform;
            var leafKit = new MeshKit();
            leafKit.Box(new Vector3(0.34f, 1.03f, 0), new Vector3(0.68f, 2.04f, 0.018f), woodDark);
            leafKit.Box(new Vector3(0.62f, 1.03f, 0.016f), new Vector3(0.02f, 0.14f, 0.02f), metal);
            var left = Part("ArmarioHojaIzq", leafKit, closet, new Vector3(-0.68f, 0.02f, 0.295f));
            dir.closetLeft = left.AddComponent<SimpleHinge>();
            dir.closetLeft.openYaw = -105f;
            var rightKit = new MeshKit();
            rightKit.Box(new Vector3(-0.34f, 1.03f, 0), new Vector3(0.68f, 2.04f, 0.018f), woodDark);
            rightKit.Box(new Vector3(-0.62f, 1.03f, 0.016f), new Vector3(0.02f, 0.14f, 0.02f), metal);
            var right = Part("ArmarioHojaDer", rightKit, closet, new Vector3(0.68f, 0.02f, 0.295f));
            dir.closetRight = right.AddComponent<SimpleHinge>();
            dir.closetRight.openYaw = 105f;
            var backKit = new MeshKit().Box(new Vector3(0.68f, 1.04f, 0), new Vector3(1.36f, 2.08f, 0.02f), woodLight);
            var back = Part("ArmarioFondo", backKit, closet, new Vector3(-0.68f, 0f, -0.28f));
            dir.closetBack = back.AddComponent<SimpleHinge>();
            dir.closetBack.openYaw = -82f;
            dir.closetBack.seconds = 1.6f;
            var backCollider = back.AddComponent<BoxCollider>();
            backCollider.center = new Vector3(0.68f, 1.04f, 0);
            backCollider.size = new Vector3(1.36f, 2.08f, 0.04f);
            Use("armario", "Abrir el armario", new Vector3(5.28f, 1.1f, 8.7f), new Vector3(0.1f, 1.6f, 1.3f), t);
            Use("fondo", "Empujar el fondo", new Vector3(5.88f, 1.1f, 8.7f), new Vector3(0.1f, 1.6f, 1.2f), t);

            // Habitación oculta 2: agujeros
            Use("agujero_cama", "Mirar por el agujero", new Vector3(6.08f, 1.59f, 7.43f), new Vector3(0.1f, 0.35f, 0.4f), t);
            Use("agujero_bano", "Mirar por el agujero", new Vector3(6.72f, 1.72f, 7.27f), new Vector3(0.1f, 0.35f, 0.4f), t);

            // La tele, para apagarla
            dir.tv = GameObject.Find("Tele").GetComponent<TVFlicker>();

            // Casa de Chechu: luz, silueta y puerta
            var street = GameObject.Find("Calle").transform;
            var lit = ProceduralAssets.Solid("VentanaEncendida", new Color(0.05f, 0.05f, 0.04f), new Color(0.62f, 0.5f, 0.3f));
            var winKit = new MeshKit().Box(Vector3.zero, new Vector3(1.4f, 1.15f, 0.01f), lit);
            dir.chechuWindowLight = Instance("VentanaChechuLuz", winKit, street, new Vector3(4.4f, 1.5f, -9.565f), 0f, false);
            var sil = new MeshKit();
            sil.Box(new Vector3(0, -0.27f, 0), new Vector3(0.38f, 0.62f, 0.01f), plastic);
            sil.Box(new Vector3(0, 0.17f, 0), new Vector3(0.2f, 0.24f, 0.01f), plastic);
            dir.chechuSilhouette = Instance("SiluetaChechu", sil, street, new Vector3(4.4f, 1.48f, -9.55f), 0f, false);
            var doorDark = new MeshKit().Box(Vector3.zero, new Vector3(0.95f, 2.05f, 0.02f), windowLit);
            dir.chechuDoorDark = Instance("PuertaChechuHueco", doorDark, street, new Vector3(7f, 1.0f, -9.54f), 0f, false);
            var leaf = new MeshKit().Box(Vector3.zero, new Vector3(0.95f, 2.05f, 0.02f), doorExt);
            leaf.Box(new Vector3(0.36f, -0.05f, 0.02f), new Vector3(0.1f, 0.03f, 0.03f), metalExt);
            dir.chechuDoorLeaf = Instance("PuertaChechuHoja", leaf, street, new Vector3(7f, 1.0f, -9.53f), 0f, false);
            Use("puerta_chechu", "Llamar a la puerta", new Vector3(7f, 1.1f, -9.4f), new Vector3(1f, 1.9f, 0.2f), t);

            // Calle en la visita 4: del porche a la puerta de Chechu y poco más
            var limits = new GameObject("LimitesCalle");
            limits.transform.SetParent(t);
            foreach (var (c, size) in new[]
            {
                (new Vector3(3.2f, 1f, -5f), new Vector3(0.2f, 2f, 10f)),
                (new Vector3(10.6f, 1f, -5f), new Vector3(0.2f, 2f, 10f)),
                (new Vector3(7f, 1f, -9.75f), new Vector3(8f, 2f, 0.2f)),
            })
            {
                var w = new GameObject("Limite");
                w.transform.SetParent(limits.transform);
                w.transform.position = c;
                w.AddComponent<BoxCollider>().size = size;
            }
            dir.streetBounds = limits;

            // Bombilla olvidada en el cuartito: solo se enciende al descubrirlo
            var bulb = SpotLight("LuzCuartito", t, new Vector3(7.6f, 2.45f, 2.2f), Quaternion.Euler(90, 0, 0), new Color(1f, 0.7f, 0.42f), 1.3f, 4f, 160f, ~0);
            bulb.shadows = LightShadows.Soft;
            dir.hiddenRoomLight = bulb;
            // Luz del porche de Chechu: sin ella su ropa negra desaparece contra la puerta oscura
            var porch = Point("LuzPorcheChechu", t, new Vector3(7f, 2.4f, -8.6f), new Color(1f, 0.74f, 0.46f), 1.5f, 5f);
            dir.chechuPorchLight = porch;
            foreach (var x in street.GetComponentsInChildren<Transform>(true)) x.gameObject.layer = ExteriorLayer;
        }

        /// <summary>Hornea la luz que entra por las ventanas. Tarda varios minutos: se lanza en segundo plano.</summary>
        [MenuItem("Tools/Ominous/Hornear la luz de la casa")]
        public static void BakeHouse()
        {
            var settings = AssetDatabase.LoadAssetAtPath<LightingSettings>(LightingPath);
            if (settings == null)
            {
                settings = new LightingSettings { name = "LightingHouse" };
                AssetDatabase.CreateAsset(settings, LightingPath);
            }
            settings.bakedGI = true;
            settings.realtimeGI = false;
            settings.lightmapper = LightingSettings.Lightmapper.ProgressiveCPU;
            settings.lightmapResolution = 10f;
            settings.lightmapMaxSize = 1024;
            settings.lightmapPadding = 3;
            settings.directSampleCount = 16;
            settings.indirectSampleCount = 96;
            settings.environmentSampleCount = 96;
            settings.maxBounces = 3;
            settings.directionalityMode = LightmapsMode.NonDirectional;
            settings.lightmapCompression = LightmapCompression.NormalQuality;
            settings.filteringMode = LightingSettings.FilterMode.Auto;
            EditorUtility.SetDirty(settings);
            AssetDatabase.SaveAssets();
            Lightmapping.lightingSettings = settings;
            Lightmapping.BakeAsync();
        }
    }
}
