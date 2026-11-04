using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Yarn.Unity;

namespace Ominous.EditorTools
{
    /// <summary>Escena de pruebas de la fase 3: el salón con objetos que se usan, y el menú principal.</summary>
    public static partial class SalonBuilder
    {
        const string SistemasPath = "Assets/_Ominous/Scenes/Test_Sistemas.unity";
        const string MenuPath = "Assets/_Ominous/Scenes/MainMenu.unity";
        const string YarnProjectPath = "Assets/_Ominous/Dialogue/Ominous.yarnproject";

        [MenuItem("Tools/Ominous/Crear proyecto Yarn")]
        public static void CreateYarnProject()
        {
            if (!System.IO.File.Exists(YarnProjectPath))
            {
                var p = new Yarn.Compiler.Project { BaseLanguage = "es" };
                p.ExcludeFilePatterns = new[] { "**/*~/*" };
                p.SaveToFile(YarnProjectPath);
            }
            AssetDatabase.ImportAsset(YarnProjectPath, ImportAssetOptions.ForceSynchronousImport);
        }

        /// <summary>Errores de compilación del guion; cadena vacía si compila.</summary>
        public static string YarnReport()
        {
            var importer = (Yarn.Unity.Editor.YarnProjectImporter)AssetImporter.GetAtPath(YarnProjectPath);
            if (importer == null) return "sin proyecto";
            var data = importer.ImportData;
            if (data == null) return "sin datos";
            var errors = data.diagnostics.SelectMany(d => d.errorMessages.Select(m => $"{System.IO.Path.GetFileName(d.yarnFile ? AssetDatabase.GetAssetPath(d.yarnFile) : "?")}: {m}")).ToArray();
            return $"estado={data.ImportStatus} nodos={data.yarnFiles.Count} errores={errors.Length}\n" + string.Join("\n", errors.Take(25));
        }

        [MenuItem("Tools/Ominous/Construir escena de sistemas y menú")]
        public static void BuildSistemas()
        {
            CreateYarnProject();
            Build();
            var scene = EditorSceneManager.GetActiveScene();
            EditorSceneManager.SaveScene(scene, SistemasPath);
            scene = EditorSceneManager.OpenScene(SistemasPath);

            var props = GameObject.Find("Muebles").transform;
            Object.DestroyImmediate(GameObject.Find("PuertaInterior"));

            // Puerta con bisagra y un armario detrás para que abrirla tenga sentido
            Instance("PuertaMarco", PuertaMarco(), props, new Vector3(5f, 0, 2.55f), 0, false);
            var leaf = new MeshKit();
            leaf.Box(new Vector3(0, 1.0f, 0.43f), new Vector3(0.04f, 2.0f, 0.86f), door);
            leaf.Box(new Vector3(-0.05f, 0.95f, 0.77f), new Vector3(0.05f, 0.03f, 0.1f), metal);
            var doorGo = Instance("PuertaHoja", leaf, props, new Vector3(5f, 0, 2.12f));
            doorGo.AddComponent<Door>();

            var closet = new MeshKit();
            closet.Box(new Vector3(5.8f, -0.05f, 2.55f), new Vector3(1.6f, 0.1f, 1.3f), floorWood);
            closet.Box(new Vector3(5.8f, 2.05f, 2.55f), new Vector3(1.6f, 0.1f, 1.3f), ceiling);
            closet.Box(new Vector3(6.55f, 1f, 2.55f), new Vector3(0.1f, 2f, 1.3f), wall);
            closet.Box(new Vector3(5.8f, 1f, 1.95f), new Vector3(1.6f, 2f, 0.1f), wall);
            closet.Box(new Vector3(5.8f, 1f, 3.15f), new Vector3(1.6f, 2f, 0.1f), wall);
            closet.Box(new Vector3(5.8f, 2.3f, 2.55f), new Vector3(1.6f, 0.6f, 1.3f), wall);
            var closetGo = Instance("Armario_Estructura", closet, props, Vector3.zero, 0, false);
            closetGo.AddComponent<MeshCollider>();
            var box = new MeshKit().Box(new Vector3(0, 0.2f, 0), new Vector3(0.4f, 0.4f, 0.4f), woodLight);
            Instance("CajaPrueba", box, props, new Vector3(6.1f, 0, 2.7f)).AddComponent<DialogueTrigger>().Configure("Examinar", "Test_Caja");

            // Interruptor y lámpara
            var lamp = GameObject.Find("LuzLampara").GetComponent<Light>();
            var sw = new MeshKit();
            sw.Box(Vector3.zero, new Vector3(0.02f, 0.12f, 0.08f), frame);
            sw.Box(new Vector3(-0.015f, 0, 0), new Vector3(0.015f, 0.04f, 0.02f), metal);
            var swGo = Instance("Interruptor", sw, props, new Vector3(4.93f, 1.2f, 3.3f));
            swGo.GetComponent<BoxCollider>().size = new Vector3(0.1f, 0.25f, 0.2f);
            var lightSwitch = swGo.AddComponent<LightSwitch>();
            lightSwitch.lights = new[] { lamp };
            lightSwitch.isOn = true;
            lightSwitch.emissive = GameObject.Find("Lampara").GetComponent<MeshRenderer>();

            // Cómoda con cajón
            var chest = new MeshKit();
            chest.Box(new Vector3(0, 0.21f, 0), new Vector3(0.8f, 0.42f, 0.4f), woodDark);
            chest.Box(new Vector3(-0.385f, 0.54f, 0), new Vector3(0.03f, 0.24f, 0.4f), woodDark);
            chest.Box(new Vector3(0.385f, 0.54f, 0), new Vector3(0.03f, 0.24f, 0.4f), woodDark);
            chest.Box(new Vector3(0, 0.54f, 0.19f), new Vector3(0.8f, 0.24f, 0.02f), woodDark);
            chest.Box(new Vector3(0, 0.67f, 0), new Vector3(0.84f, 0.03f, 0.44f), woodLight);
            var chestGo = Instance("Comoda", chest, props, new Vector3(0.85f, 0, 4.12f));
            var drawerKit = new MeshKit();
            drawerKit.Box(new Vector3(0, 0, -0.195f), new Vector3(0.73f, 0.21f, 0.02f), woodLight);
            drawerKit.Box(new Vector3(0, -0.095f, 0), new Vector3(0.71f, 0.02f, 0.37f), woodDark);
            drawerKit.Box(new Vector3(-0.355f, -0.03f, 0), new Vector3(0.02f, 0.13f, 0.37f), woodDark);
            drawerKit.Box(new Vector3(0.355f, -0.03f, 0), new Vector3(0.02f, 0.13f, 0.37f), woodDark);
            drawerKit.Box(new Vector3(0, -0.03f, 0.18f), new Vector3(0.71f, 0.13f, 0.02f), woodDark);
            drawerKit.Box(new Vector3(0, 0.02f, -0.215f), new Vector3(0.1f, 0.02f, 0.02f), metal);
            var drawerGo = Instance("Cajon", drawerKit, chestGo.transform, new Vector3(0.85f, 0.54f, 4.12f));
            drawerGo.AddComponent<Drawer>();
            var keyKit = new MeshKit().Box(Vector3.zero, new Vector3(0.07f, 0.012f, 0.025f), metal);
            var keyGo = Instance("LlavePrueba", keyKit, drawerGo.transform, new Vector3(0.75f, 0.46f, 3.98f));
            keyGo.GetComponent<BoxCollider>().size = new Vector3(0.18f, 0.08f, 0.14f);
            keyGo.AddComponent<DialogueTrigger>().Configure("Examinar", "Test_Llave");

            // Objetos que se examinan
            var remote = new GameObject("MandoExaminable");
            remote.transform.SetParent(props);
            remote.transform.position = new Vector3(2.37f, 0.45f, 2.8f);
            remote.AddComponent<BoxCollider>().size = new Vector3(0.28f, 0.08f, 0.16f);
            remote.AddComponent<DialogueTrigger>().Configure("Examinar", "Test_Mando");
            GameObject.Find("Tele").AddComponent<DialogueTrigger>().Configure("Examinar", "Test_Tele");

            // Figura de prueba
            var figure = new MeshKit();
            figure.Cylinder(Vector3.zero, 0.17f, 0.2f, 1.4f, 8, blanket);
            figure.Box(new Vector3(0, 1.56f, 0), new Vector3(0.2f, 0.26f, 0.22f), cushion);
            var figureGo = Instance("FiguraPrueba", figure, props, new Vector3(4.3f, 0, 0.95f), 300f);
            figureGo.AddComponent<DialogueTrigger>().Configure("Hablar", "Test_Conversacion");

            // Variante: un cuadro que solo está desde el acto 2
            var picture = new MeshKit();
            picture.Box(Vector3.zero, new Vector3(0.62f, 0.47f, 0.03f), woodDark);
            picture.Box(new Vector3(0, 0, -0.018f), new Vector3(0.54f, 0.39f, 0.006f), curtain);
            var pictureGo = Instance("CuadroVariante", picture, props, new Vector3(3.2f, 1.65f, 4.32f));
            pictureGo.AddComponent<DialogueTrigger>().Configure("Examinar", "Test_Cuadro");
            var variant = pictureGo.AddComponent<HouseVariant>();
            variant.fromAct = 2;

            // Sistemas
            var player = GameObject.Find("Jugador");
            var interactor = player.AddComponent<PlayerInteractor>();
            interactor.eye = Camera.main.transform;
            var systems = new GameObject("Sistemas");
            systems.AddComponent<GameDirector>();
            systems.AddComponent<GameUI>();
            systems.AddComponent<PauseMenu>();
            var dialogue = systems.AddComponent<DialogueManager>();
            dialogue.project = AssetDatabase.LoadAssetAtPath<YarnProject>(YarnProjectPath);
            EditorSceneManager.SaveScene(scene);

            BuildMenu();
            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(MenuPath, true),
                new EditorBuildSettingsScene(SistemasPath, true),
                new EditorBuildSettingsScene(ScenePath, true),
            };
            AssetDatabase.SaveAssets();
            EditorSceneManager.OpenScene(SistemasPath);
            Debug.Log("Escena de sistemas construida");
        }

        static void BuildMenu()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var cam = new GameObject("Camara").AddComponent<Camera>();
            cam.tag = "MainCamera";
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.015f, 0.012f, 0.012f);
            cam.gameObject.AddComponent<AudioListener>();
            // La pasada de imagen también corre aquí, así que necesita sus ajustes para no dejar la pantalla negra.
            new GameObject("Imagen").AddComponent<VideoLookController>().settings = AssetDatabase.LoadAssetAtPath<VideoLookSettings>(OminousSetup.SettingsPath);
            var go = new GameObject("Menu");
            go.AddComponent<MainMenu>();
            EditorSceneManager.SaveScene(scene, MenuPath);
        }
    }
}
