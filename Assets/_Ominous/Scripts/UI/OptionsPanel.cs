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
            var root = UIKit.Rect(parent, "Opciones", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(560, 640));
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

            TMP_Text reduceLabel = null;
            string ReduceText() => $"Reducir efectos: {(OminousOptions.ReduceEffects ? "sí" : "no")}";
            var reduce = UIKit.Button(column, ReduceText(), () =>
            {
                OminousOptions.ReduceEffects = !OminousOptions.ReduceEffects;
                reduceLabel.text = ReduceText();
            });
            reduceLabel = reduce.GetComponentInChildren<TMP_Text>();

            TMP_Text backLabel = null;
            string BackText() => $"Fondo de los subtítulos: {OminousOptions.SubtitleBackground switch { 0 => "no", 2 => "fuerte", _ => "suave" }}";
            var back = UIKit.Button(column, BackText(), () =>
            {
                OminousOptions.SubtitleBackground = (OminousOptions.SubtitleBackground + 1) % 3;
                backLabel.text = BackText();
            });
            backLabel = back.GetComponentInChildren<TMP_Text>();

            UIKit.Slider(column, "Tamaño de subtítulos y textos", 0.8f, 2f, OminousOptions.TextSize, v => OminousOptions.TextSize = v);
            UIKit.Slider(column, "Brillo", 0.6f, 1.6f, OminousOptions.Brightness, v => OminousOptions.Brightness = v);
            UIKit.Slider(column, "Sensibilidad de la cámara", 0.3f, 2.5f, OminousOptions.Sensitivity, v => OminousOptions.Sensitivity = v);
            UIKit.Slider(column, "Intensidad del efecto de cámara", 0f, 1f, OminousOptions.CameraEffectIntensity, v => OminousOptions.CameraEffectIntensity = v);
            GameObject keys = null;
            UIKit.Button(column, "Teclas", () => { column.gameObject.SetActive(false); keys.SetActive(true); });
            UIKit.Button(column, "Volver", () => onBack());
            keys = KeysPanel.Build(root, () => { keys.SetActive(false); column.gameObject.SetActive(true); });
            keys.SetActive(false);
            return root.gameObject;
        }
    }
}
