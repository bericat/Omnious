using TMPro;
using UnityEngine;

namespace Ominous
{
    /// <summary>
    /// Ajuste de brillo del primer arranque (OSCURIDAD.md): tres logos en gris sobre negro. El de la izquierda tiene
    /// que verse apenas, el del centro verse y el de la derecha verse claro.
    /// </summary>
    public static class BrightnessCalibration
    {
        public static bool Done => PlayerPrefs.GetInt("calibrado", 0) == 1;

        public static void Show(Transform canvas, GameObject hide)
        {
            hide.SetActive(false);
            var root = UIKit.Stretch(canvas, "Calibracion");
            UIKit.Panel(root, Color.black);
            var title = UIKit.Label(UIKit.Rect(root, "Texto", new Vector2(0.5f, 1f), new Vector2(0.5f, 1f), new Vector2(0.5f, 1f), new Vector2(0, -60), new Vector2(900, 80)),
                "Ajusta el brillo hasta que el logo de la izquierda apenas se vea", 20f, UIKit.Ink);
            float[] greys = { 0.035f, 0.09f, 0.22f };
            var logos = new TextMeshProUGUI[3];
            for (int i = 0; i < 3; i++)
            {
                logos[i] = UIKit.Label(UIKit.Rect(root, "Logo" + i, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2((i - 1) * 330f, 40f), new Vector2(320, 90)),
                    "OMINOUS", 44f, Color.white);
            }
            void Paint()
            {
                for (int i = 0; i < 3; i++)
                {
                    float g = Mathf.Clamp01(greys[i] * OminousOptions.Brightness);
                    logos[i].color = new Color(g, g, g);
                }
            }
            Paint();
            var column = UIKit.Rect(root, "Controles", new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0, 60), new Vector2(460, 150));
            UIKit.Column(column, 10);
            UIKit.Slider(column, "Brillo", 0.6f, 1.6f, OminousOptions.Brightness, v => { OminousOptions.Brightness = v; Paint(); });
            UIKit.Button(column, "Listo", () =>
            {
                PlayerPrefs.SetInt("calibrado", 1);
                PlayerPrefs.Save();
                Object.Destroy(root.gameObject);
                hide.SetActive(true);
            });
        }
    }
}
