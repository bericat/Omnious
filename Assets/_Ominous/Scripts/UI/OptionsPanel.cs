using System;
using TMPro;
using UnityEngine;

namespace Ominous
{
    /// <summary>Opciones: subtítulos, tamaño de texto, brillo, sensibilidad e intensidad del efecto de cámara.</summary>
    public static class OptionsPanel
    {
        public static GameObject Build(Transform parent, Action onBack)
        {
            var root = UIKit.Rect(parent, "Opciones", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(460, 480));
            UIKit.Panel(root, new Color(0.03f, 0.03f, 0.03f, 0.92f));
            var column = UIKit.Stretch(root, "Columna");
            column.offsetMin = new Vector2(20, 16); column.offsetMax = new Vector2(-20, -16);
            UIKit.Column(column, 8);

            TMP_Text subsLabel = null;
            string SubsText() => $"Subtítulos: {(OminousOptions.Subtitles ? "sí" : "no")}";
            var subs = UIKit.Button(column, SubsText(), () =>
            {
                OminousOptions.Subtitles = !OminousOptions.Subtitles;
                subsLabel.text = SubsText();
            });
            subsLabel = subs.GetComponentInChildren<TMP_Text>();

            UIKit.Slider(column, "Tamaño del texto", 0.8f, 1.6f, OminousOptions.TextSize, v => OminousOptions.TextSize = v);
            UIKit.Slider(column, "Brillo", 0.6f, 1.6f, OminousOptions.Brightness, v => OminousOptions.Brightness = v);
            UIKit.Slider(column, "Sensibilidad del ratón", 0.3f, 2.5f, OminousOptions.Sensitivity, v => OminousOptions.Sensitivity = v);
            UIKit.Slider(column, "Intensidad del efecto de cámara", 0f, 1f, OminousOptions.CameraEffectIntensity, v => OminousOptions.CameraEffectIntensity = v);
            UIKit.Button(column, "Volver", () => onBack());
            return root.gameObject;
        }
    }
}
