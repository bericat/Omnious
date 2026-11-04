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

        TextMeshProUGUI prompt, objective, subtitle, speakerName;
        RectTransform subtitleBox, optionsBox;
        GameObject crosshair;
        readonly List<GameObject> optionButtons = new();
        const float SubtitleSize = 26f, NameSize = 20f, PromptSize = 22f;

        void Awake()
        {
            Instance = this;
            Canvas = UIKit.Canvas("InterfazJuego", 10);
            var root = Canvas.transform;

            var dot = UIKit.Rect(root, "Mira", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(4, 4));
            UIKit.Panel(dot, new Color(1f, 1f, 1f, 0.55f)).raycastTarget = false;
            crosshair = dot.gameObject;

            prompt = UIKit.Label(UIKit.Rect(root, "Aviso", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 1f), new Vector2(0, -22), new Vector2(620, 34)), "", PromptSize, UIKit.Ink);
            objective = UIKit.Label(UIKit.Rect(root, "Objetivo", new Vector2(0, 1), new Vector2(0, 1), new Vector2(0, 1), new Vector2(14, -34), new Vector2(640, 32)), "", 20f, UIKit.Dim, TextAlignmentOptions.Left);

            subtitleBox = UIKit.Rect(root, "Subtitulos", new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0, 46), new Vector2(1000, 120));
            UIKit.Panel(subtitleBox, new Color(0, 0, 0, 0.62f)).raycastTarget = false;
            speakerName = UIKit.Label(UIKit.Rect(subtitleBox, "Nombre", new Vector2(0, 1), new Vector2(1, 1), new Vector2(0.5f, 1), new Vector2(0, -6), new Vector2(-40, 26)), "", NameSize, new Color(0.85f, 0.42f, 0.32f));
            var body = UIKit.Rect(subtitleBox, "Texto", Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero);
            body.offsetMin = new Vector2(24, 8); body.offsetMax = new Vector2(-24, -30);
            subtitle = UIKit.Label(body, "", SubtitleSize, UIKit.Ink);
            subtitleBox.gameObject.SetActive(false);

            optionsBox = UIKit.Rect(root, "Elecciones", new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0, 46), new Vector2(760, 240));
            UIKit.Column(optionsBox, 8).childAlignment = TextAnchor.LowerCenter;
            optionsBox.gameObject.SetActive(false);

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
            objective.fontSize = 20f * scale;
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

        public void HideSubtitle() => subtitleBox.gameObject.SetActive(false);

        public void ShowOptions(DialogueOption[] options, Action<int> choose)
        {
            HideOptions();
            optionsBox.gameObject.SetActive(true);
            for (int i = 0; i < options.Length; i++)
            {
                if (!options[i].IsAvailable) continue;
                int index = i;
                var button = UIKit.Button(optionsBox, options[i].Line.TextWithoutCharacterName.Text, () => choose(index), 46f, 22f * OminousOptions.TextSize);
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
