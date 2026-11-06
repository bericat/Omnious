using TMPro;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Ominous
{
    /// <summary>Menú principal discreto.</summary>
    public class MainMenu : MonoBehaviour
    {
        public const string SceneName = "MainMenu";
        public const string GameScene = "House";

        TextMeshProUGUI logo;
        GameObject column, options;
        float nextFlicker;

        void Start()
        {
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
            var root = UIKit.Canvas("Menu", 10).transform;

            logo = UIKit.Label(UIKit.Rect(root, "Logo", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0, 215), new Vector2(1000, 150)), "Ominous", 74, UIKit.Ink);
            logo.characterSpacing = 6f;

            var col = UIKit.Rect(root, "Botones", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0, -70), new Vector2(380, 270));
            UIKit.Column(col, 12);
            if (SaveSystem.Exists)
                UIKit.Button(col, "Continuar", () => { SaveSystem.LoadRequested = true; SceneManager.LoadScene(GameScene); });
            UIKit.Button(col, "Nueva partida", () => { SaveSystem.LoadRequested = false; SceneManager.LoadScene(GameScene); });
            UIKit.Button(col, "Opciones", () => { column.SetActive(false); options.SetActive(true); });
            UIKit.Button(col, "Salir", Application.Quit);
            column = col.gameObject;
            options = OptionsPanel.Build(root, () => { options.SetActive(false); column.SetActive(true); });
            options.SetActive(false);
            // Primer arranque: ajustar el brillo para que la oscuridad se vea como se diseñó.
            if (!BrightnessCalibration.Done) BrightnessCalibration.Show(root, column);
        }

        void Update()
        {
            if (Time.unscaledTime < nextFlicker) return;
            bool dark = logo.color.a > 0.5f && Random.value < 0.5f;
            logo.color = new Color(UIKit.Ink.r, UIKit.Ink.g, UIKit.Ink.b, dark ? 0.55f : 1f);
            nextFlicker = Time.unscaledTime + (dark ? Random.Range(0.04f, 0.12f) : Random.Range(4f, 14f));
        }
    }
}
