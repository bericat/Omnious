using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;

namespace Ominous
{
    /// <summary>Pausa con Esc: continuar, opciones, cargar y salir al menú.</summary>
    public class PauseMenu : MonoBehaviour
    {
        public static bool IsPaused { get; private set; }

        GameObject main, options, shade, loadButton;

        void Start()
        {
            var root = GameUI.Instance.Canvas.transform;
            var dim = UIKit.Stretch(root, "Pausa");
            UIKit.Panel(dim, new Color(0, 0, 0, 0.72f));
            shade = dim.gameObject;

            var column = UIKit.Rect(dim, "Menu", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(420, 330));
            UIKit.Column(column, 10);
            UIKit.Label(UIKit.Rect(column, "Titulo", Vector2.zero, Vector2.zero, Vector2.zero, Vector2.zero, new Vector2(420, 60)), "PAUSA", 40, UIKit.Ink);
            UIKit.Button(column, "Continuar", () => SetPaused(false));
            UIKit.Button(column, "Opciones", () => { main.SetActive(false); options.SetActive(true); });
            loadButton = UIKit.Button(column, "Cargar el último punto de control", LoadCheckpoint).gameObject;
            UIKit.Button(column, "Salir al menú", ExitToMenu);
            main = column.gameObject;

            options = OptionsPanel.Build(dim, () => { options.SetActive(false); main.SetActive(true); });
            options.SetActive(false);
            shade.SetActive(false);
        }

        void OnDestroy()
        {
            if (IsPaused) Time.timeScale = 1f;
            IsPaused = false;
        }

        void Update()
        {
            if (Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame) SetPaused(!IsPaused);
        }

        public void SetPaused(bool paused)
        {
            IsPaused = paused;
            Time.timeScale = paused ? 0f : 1f;
            FirstPersonController.SetBlocked(this, paused);
            shade.SetActive(paused);
            GameUI.Instance.SetHudVisible(!paused);
            if (paused)
            {
                main.SetActive(true);
                options.SetActive(false);
                loadButton.SetActive(SaveSystem.Exists);
            }
        }

        public void LoadCheckpoint()
        {
            SetPaused(false);
            SaveSystem.LoadRequested = true;
            SceneManager.LoadScene(SceneManager.GetActiveScene().name);
        }

        void ExitToMenu()
        {
            SetPaused(false);
            SceneManager.LoadScene(MainMenu.SceneName);
        }
    }
}
