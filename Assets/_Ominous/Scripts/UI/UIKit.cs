using System;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.UI;

namespace Ominous
{
    /// <summary>Monta la interfaz por código, sin prefabs.</summary>
    public static class UIKit
    {
        public static readonly Color Ink = new(0.86f, 0.82f, 0.74f);
        public static readonly Color Dim = new(0.6f, 0.58f, 0.54f);
        public static readonly Color Accent = new(0.62f, 0.12f, 0.1f);

        public static Canvas Canvas(string name, int order)
        {
            var go = new GameObject(name, typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            var canvas = go.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = order;
            var scaler = go.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1280, 800);
            scaler.matchWidthOrHeight = 0.5f;
            if (UnityEngine.Object.FindAnyObjectByType<EventSystem>() == null)
                new GameObject("EventSystem", typeof(EventSystem), typeof(InputSystemUIInputModule));
            return canvas;
        }

        public static RectTransform Rect(Transform parent, string name, Vector2 anchorMin, Vector2 anchorMax, Vector2 pivot, Vector2 position, Vector2 size)
        {
            var go = new GameObject(name, typeof(RectTransform));
            var r = go.GetComponent<RectTransform>();
            r.SetParent(parent, false);
            r.anchorMin = anchorMin; r.anchorMax = anchorMax; r.pivot = pivot;
            r.anchoredPosition = position; r.sizeDelta = size;
            return r;
        }

        public static RectTransform Stretch(Transform parent, string name)
            => Rect(parent, name, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero);

        public static Image Panel(RectTransform r, Color color)
        {
            var image = r.gameObject.AddComponent<Image>();
            image.color = color;
            return image;
        }

        public static TextMeshProUGUI Label(RectTransform r, string text, float size, Color color, TextAlignmentOptions align = TextAlignmentOptions.Center)
        {
            var t = r.gameObject.AddComponent<TextMeshProUGUI>();
            t.text = text; t.fontSize = size; t.color = color; t.alignment = align; t.raycastTarget = false;
            t.textWrappingMode = TextWrappingModes.Normal;
            return t;
        }

        public static VerticalLayoutGroup Column(RectTransform r, float spacing)
        {
            var v = r.gameObject.AddComponent<VerticalLayoutGroup>();
            v.spacing = spacing; v.childAlignment = TextAnchor.MiddleCenter;
            v.childControlHeight = true; v.childControlWidth = true; v.childForceExpandHeight = false; v.childForceExpandWidth = true;
            return v;
        }

        public static Button Button(Transform parent, string text, Action onClick, float height = 44f, float fontSize = 22f)
        {
            var r = Rect(parent, text, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(420, height));
            r.gameObject.AddComponent<LayoutElement>().preferredHeight = height;
            var image = Panel(r, new Color(0.09f, 0.08f, 0.08f, 0.9f));
            var b = r.gameObject.AddComponent<Button>();
            b.targetGraphic = image;
            var c = b.colors;
            c.normalColor = Color.white; c.highlightedColor = new Color(2.6f, 1.2f, 1.2f); c.pressedColor = new Color(3.6f, 1.2f, 1.2f); c.selectedColor = Color.white;
            b.colors = c;
            b.onClick.AddListener(() => onClick());
            var label = Stretch(r, "Texto");
            label.offsetMin = new Vector2(12, 2); label.offsetMax = new Vector2(-12, -2);
            Label(label, text, fontSize, Ink);
            return b;
        }

        public static Slider Slider(Transform parent, string text, float min, float max, float value, Action<float> onChange)
        {
            var row = Rect(parent, text, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(420, 58));
            row.gameObject.AddComponent<LayoutElement>().preferredHeight = 58;
            Label(Rect(row, "Etiqueta", new Vector2(0, 1), new Vector2(1, 1), new Vector2(0.5f, 1), Vector2.zero, new Vector2(0, 26)), text, 20, Ink, TextAlignmentOptions.Left);
            var go = DefaultControls.CreateSlider(new DefaultControls.Resources());
            var r = go.GetComponent<RectTransform>();
            r.SetParent(row, false);
            r.anchorMin = new Vector2(0, 0); r.anchorMax = new Vector2(1, 0); r.pivot = new Vector2(0.5f, 0);
            r.anchoredPosition = new Vector2(0, 4); r.sizeDelta = new Vector2(0, 22);
            var s = go.GetComponent<Slider>();
            s.minValue = min; s.maxValue = max; s.value = value;
            s.onValueChanged.AddListener(v => onChange(v));
            foreach (var i in go.GetComponentsInChildren<Image>())
                i.color = i.name == "Fill" ? Accent : i.name == "Handle" ? Ink : new Color(0.16f, 0.15f, 0.15f);
            return s;
        }
    }
}
