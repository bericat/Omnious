using System;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using Yarn.Unity;

namespace Ominous
{
    /// <summary>Lo que se ve durante el juego: mira, avisos, objetivo, subtítulos y elecciones.</summary>
    public class GameUI : MonoBehaviour
    {
        public static GameUI Instance { get; private set; }
        public Canvas Canvas { get; private set; }

        TextMeshProUGUI prompt, objective, subtitle, speakerName, ambientLine;
        UnityEngine.UI.Image fade, subtitleBack;
        float subtitleHeight, subtitleWidth;
        RectTransform subtitleBody;
        RectTransform subtitleBox, optionsBox;
        GameObject crosshair;
        readonly List<GameObject> optionButtons = new();
        const float SubtitleSize = 17f, NameSize = 13f, PromptSize = 15f, ObjectiveSize = 13f;

        void Awake()
        {
            Instance = this;
            Canvas = UIKit.Canvas("InterfazJuego", 10);
            var root = Canvas.transform;

            var dot = UIKit.Rect(root, "Mira", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(3, 3));
            UIKit.Panel(dot, new Color(1f, 1f, 1f, 0.3f)).raycastTarget = false;
            crosshair = dot.gameObject;

            // Todos los textos van abajo, pequeños y sin llamar la atención.
            objective = UIKit.Label(UIKit.Rect(root, "Objetivo", new Vector2(0, 0), new Vector2(0, 0), new Vector2(0, 0), new Vector2(16, 12), new Vector2(420, 24)), "", ObjectiveSize, UIKit.Dim, TextAlignmentOptions.Left);

            subtitleBox = UIKit.Rect(root, "Subtitulos", new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0, 40), new Vector2(760, 66));
            subtitleBack = UIKit.Panel(subtitleBox, new Color(0, 0, 0, 0.3f));
            subtitleBack.raycastTarget = false;
            subtitleHeight = subtitleBox.sizeDelta.y;
            speakerName = UIKit.Label(UIKit.Rect(subtitleBox, "Nombre", new Vector2(0, 1), new Vector2(1, 1), new Vector2(0.5f, 1), new Vector2(0, -3), new Vector2(-30, 18)), "", NameSize, UIKit.Dim);
            var body = UIKit.Rect(subtitleBox, "Texto", Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero);
            body.offsetMin = new Vector2(16, 4); body.offsetMax = new Vector2(-16, -20);
            subtitleBody = body;
            subtitleWidth = subtitleBox.sizeDelta.x;
            subtitle = UIKit.Label(body, "", SubtitleSize, UIKit.Ink);
            subtitleBox.gameObject.SetActive(false);

            prompt = UIKit.Label(UIKit.Rect(root, "Aviso", new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0, 112), new Vector2(620, 24)), "", PromptSize, UIKit.Ink);

            optionsBox = UIKit.Rect(root, "Elecciones", new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0, 40), new Vector2(640, 170));
            UIKit.Column(optionsBox, 5).childAlignment = TextAnchor.LowerCenter;
            optionsBox.gameObject.SetActive(false);

            ambientLine = UIKit.Label(UIKit.Rect(root, "VozLejana", new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0, 138), new Vector2(760, 24)), "", 14f, UIKit.Dim);
            ambientLine.fontStyle = FontStyles.Italic;

            var black = UIKit.Stretch(root, "Fundido");
            fade = UIKit.Panel(black, new Color(0, 0, 0, 0));
            fade.raycastTarget = false;

            OminousOptions.Changed += ApplyOptions;
            ApplyOptions();
            if (GameDirector.Instance != null) GameDirector.Instance.Changed += RefreshObjective;
        }

        void OnDestroy()
        {
            OminousOptions.Changed -= ApplyOptions;
            if (GameDirector.Instance != null) GameDirector.Instance.Changed -= RefreshObjective;
            if (Instance == this) Instance = null;
        }

        void ApplyOptions()
        {
            float scale = OminousOptions.TextSize;
            subtitle.fontSize = SubtitleSize * scale;
            speakerName.fontSize = NameSize * scale;
            prompt.fontSize = PromptSize * scale;
            objective.fontSize = ObjectiveSize * scale;
            ambientLine.fontSize = 14f * scale;
            subtitleBox.sizeDelta = new Vector2(subtitleWidth * Mathf.Max(1f, scale * 0.75f), subtitleHeight * Mathf.Max(1f, scale));
            subtitleBody.offsetMax = new Vector2(-16f, -20f * Mathf.Max(1f, scale));
            subtitleBack.color = new Color(0f, 0f, 0f, OminousOptions.SubtitleBackground switch { 0 => 0f, 2 => 0.75f, _ => 0.3f });
        }

        void RefreshObjective()
        {
            string text = GameDirector.Instance != null ? GameDirector.Instance.Night.objective : "";
            objective.text = string.IsNullOrEmpty(text) ? "" : text;
        }

        public void SetPrompt(string text)
        {
            prompt.text = text ?? "";
        }

        public void SetHudVisible(bool visible)
        {
            crosshair.SetActive(visible);
            prompt.gameObject.SetActive(visible);
        }

        public void ShowSubtitle(string speaker, string text, bool thought)
        {
            if (!OminousOptions.Subtitles) return;
            subtitleBox.gameObject.SetActive(true);
            speakerName.text = speaker ?? "";
            subtitle.text = text;
            subtitle.fontStyle = thought ? FontStyles.Italic : FontStyles.Normal;
            subtitle.color = thought ? UIKit.Dim : UIKit.Ink;
        }

        /// <summary>Alguien que habla lejos: el texto se apaga con la distancia.</summary>
        public void SetAmbientLine(string text, float alpha)
        {
            bool show = !string.IsNullOrEmpty(text) && alpha > 0.02f && OminousOptions.Subtitles;
            ambientLine.text = show ? text : "";
            var c = ambientLine.color;
            c.a = alpha;
            ambientLine.color = c;
        }

        public System.Collections.IEnumerator Fade(float target, float seconds)
        {
            float start = fade.color.a, t = 0f;
            while (t < seconds)
            {
                t += Time.unscaledDeltaTime;
                fade.color = new Color(0, 0, 0, Mathf.Lerp(start, target, t / seconds));
                yield return null;
            }
            fade.color = new Color(0, 0, 0, target);
        }

        public void SetBlack() => fade.color = Color.black;

        /// <summary>Créditos sobre negro, por encima de todo lo demás.</summary>
        public System.Collections.IEnumerator Credits()
        {
            SetHudVisible(false);
            SetAmbientLine(null, 0f);
            objective.text = "";
            string[] pages =
            {
                "Ominous",
                "Un juego de Toni",
                "Personajes\nChevas · Roberta · Chechu",
                "Desarrollo con Claude",
                "Fuente: Noto Sans Mono\n© The Noto Project Authors. Licencia SIL OFL 1.1",
                "Sonido generado por script para este juego",
            };
            var page = UIKit.Label(UIKit.Rect(Canvas.transform, "Creditos", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(1000, 200)), "", 20f, UIKit.Ink);
            foreach (string text in pages)
            {
                page.text = text;
                yield return new WaitForSecondsRealtime(3.2f);
                page.text = "";
                yield return new WaitForSecondsRealtime(0.7f);
            }
            Destroy(page.gameObject);
        }

        public void HideSubtitle() => subtitleBox.gameObject.SetActive(false);

        public void ShowOptions(DialogueOption[] options, Action<int> choose)
        {
            HideOptions();
            optionsBox.gameObject.SetActive(true);
            for (int i = 0; i < options.Length; i++)
            {
                if (!options[i].IsAvailable) continue;
                int index = i;
                var button = UIKit.Button(optionsBox, options[i].Line.TextWithoutCharacterName.Text, () => choose(index), 32f, 16f * OminousOptions.TextSize);
                optionButtons.Add(button.gameObject);
            }
        }

        public void HideOptions()
        {
            foreach (var b in optionButtons) Destroy(b);
            optionButtons.Clear();
            optionsBox.gameObject.SetActive(false);
        }
    }
}
