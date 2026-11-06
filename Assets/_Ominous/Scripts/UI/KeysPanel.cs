using System;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;

namespace Ominous
{
    /// <summary>Reasignar teclas: se pulsa una acción y luego la tecla nueva. Esc cancela.</summary>
    public class KeysPanel : MonoBehaviour
    {
        readonly Dictionary<GameAction, TMP_Text> labels = new();
        bool waiting;
        GameAction waitingFor;

        static string ActionName(GameAction action) => action switch
        {
            GameAction.Adelante => "Adelante",
            GameAction.Atras => "Atrás",
            GameAction.Izquierda => "Izquierda",
            GameAction.Derecha => "Derecha",
            GameAction.Usar => "Usar",
            GameAction.Linterna => "Linterna",
            _ => "Agacharse",
        };

        public static GameObject Build(Transform parent, Action onBack)
        {
            var root = UIKit.Rect(parent, "Teclas", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(520, 440));
            UIKit.Panel(root, new Color(0.03f, 0.03f, 0.03f, 0.92f));
            var column = UIKit.Stretch(root, "Columna");
            column.offsetMin = new Vector2(20, 16); column.offsetMax = new Vector2(-20, -16);
            UIKit.Column(column, 8);
            var panel = root.gameObject.AddComponent<KeysPanel>();
            foreach (var action in GameInput.Actions)
            {
                var chosen = action;
                var button = UIKit.Button(column, "", () => panel.StartWaiting(chosen));
                panel.labels[action] = button.GetComponentInChildren<TMP_Text>();
            }
            UIKit.Button(column, "Restablecer", () => { GameInput.ResetBindings(); panel.Refresh(); });
            UIKit.Button(column, "Volver", () => { panel.waiting = false; onBack(); });
            panel.Refresh();
            return root.gameObject;
        }

        /// <summary>Empezar a esperar la tecla para esa acción.</summary>
        public void StartWaiting(GameAction action)
        {
            waiting = true;
            waitingFor = action;
            EventSystem.current?.SetSelectedGameObject(null);
            Refresh();
        }

        void OnEnable() => Refresh();

        void Refresh()
        {
            foreach (var pair in labels)
                pair.Value.text = waiting && pair.Key == waitingFor
                    ? $"{ActionName(pair.Key)}: pulsa una tecla"
                    : $"{ActionName(pair.Key)}: {GameInput.KeyName(GameInput.Binding(pair.Key))}";
        }

        void Update()
        {
            var keyboard = Keyboard.current;
            if (!waiting || keyboard == null || !keyboard.anyKey.wasPressedThisFrame) return;
            foreach (var control in keyboard.allKeys)
            {
                if (control == null || !control.wasPressedThisFrame) continue;
                if (control.keyCode != Key.Escape) GameInput.Rebind(waitingFor, control.keyCode);
                waiting = false;
                Refresh();
                return;
            }
        }
    }
}
