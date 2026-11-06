using System;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;

namespace Ominous
{
    public enum GameAction { Adelante, Atras, Izquierda, Derecha, Usar, Agachar, Linterna }

    /// <summary>Todo lo que el jugador pulsa, con teclas reasignables y mando.</summary>
    public static class GameInput
    {
        const float StickDeadZone = 0.15f, StickLookSpeed = 130f;

        public static readonly GameAction[] Actions = (GameAction[])Enum.GetValues(typeof(GameAction));

        /// <summary>El último dispositivo usado fue el mando: los avisos muestran sus botones.</summary>
        public static bool UsingGamepad
        {
            get
            {
                Refresh();
                return usingGamepad;
            }
        }

        static bool usingGamepad;
        static int refreshedFrame = -1;

        static void Refresh()
        {
            if (refreshedFrame == Time.frameCount) return;
            refreshedFrame = Time.frameCount;
            var pad = Gamepad.current;
            if (pad != null && (pad.wasUpdatedThisFrame && PadActive(pad))) usingGamepad = true;
            else if ((Keyboard.current != null && Keyboard.current.anyKey.wasPressedThisFrame) ||
                     (Mouse.current != null && Mouse.current.delta.ReadValue().sqrMagnitude > 1f)) usingGamepad = false;
        }

        static bool PadActive(Gamepad pad)
        {
            if (pad.leftStick.ReadValue().magnitude > 0.3f || pad.rightStick.ReadValue().magnitude > 0.3f) return true;
            if (pad.dpad.ReadValue().sqrMagnitude > 0f) return true;
            return pad.buttonSouth.isPressed || pad.buttonEast.isPressed || pad.startButton.isPressed || pad.leftStickButton.isPressed;
        }

        public static Key Binding(GameAction action) => (Key)PlayerPrefs.GetInt("tecla_" + action, (int)DefaultKey(action));

        static Key DefaultKey(GameAction action) => action switch
        {
            GameAction.Adelante => Key.W,
            GameAction.Atras => Key.S,
            GameAction.Izquierda => Key.A,
            GameAction.Derecha => Key.D,
            GameAction.Usar => Key.E,
            GameAction.Linterna => Key.F,
            _ => Key.LeftCtrl,
        };

        /// <summary>Asigna la tecla; si otra acción la tenía, se intercambian.</summary>
        public static void Rebind(GameAction action, Key key)
        {
            var previous = Binding(action);
            foreach (var other in Actions)
                if (other != action && Binding(other) == key) PlayerPrefs.SetInt("tecla_" + other, (int)previous);
            PlayerPrefs.SetInt("tecla_" + action, (int)key);
            PlayerPrefs.Save();
        }

        public static void ResetBindings()
        {
            foreach (var action in Actions) PlayerPrefs.DeleteKey("tecla_" + action);
            PlayerPrefs.Save();
        }

        public static string KeyName(Key key)
        {
            var keyboard = Keyboard.current;
            var name = keyboard != null ? keyboard[key].displayName : null;
            return string.IsNullOrEmpty(name) ? key.ToString() : name.ToUpperInvariant();
        }

        public static string UseLabel => UsingGamepad ? "A" : KeyName(Binding(GameAction.Usar));

        static bool Held(GameAction action)
        {
            var keyboard = Keyboard.current;
            return keyboard != null && keyboard[Binding(action)].isPressed;
        }

        static bool PressedPad(ButtonControl Button) => Button != null && Button.wasPressedThisFrame;

        /// <summary>Movimiento pedido, con cada eje entre -1 y 1.</summary>
        public static Vector2 Move
        {
            get
            {
                Vector2 move = Vector2.zero;
                if (Held(GameAction.Adelante)) move.y += 1f;
                if (Held(GameAction.Atras)) move.y -= 1f;
                if (Held(GameAction.Derecha)) move.x += 1f;
                if (Held(GameAction.Izquierda)) move.x -= 1f;
                var pad = Gamepad.current;
                if (pad != null)
                {
                    Vector2 stick = pad.leftStick.ReadValue();
                    if (stick.magnitude > StickDeadZone) move += stick;
                }
                return Vector2.ClampMagnitude(move, 1f);
            }
        }

        /// <summary>Giro de cámara en grados para este fotograma.</summary>
        public static Vector2 Look(float mouseDegreesPerPixel)
        {
            Vector2 look = Vector2.zero;
            if (Mouse.current != null) look += Mouse.current.delta.ReadValue() * (mouseDegreesPerPixel * OminousOptions.Sensitivity);
            var pad = Gamepad.current;
            if (pad != null)
            {
                Vector2 stick = pad.rightStick.ReadValue();
                if (stick.magnitude > StickDeadZone)
                    look += stick * stick.magnitude * (StickLookSpeed * OminousOptions.Sensitivity * Time.unscaledDeltaTime);
            }
            return look;
        }

        public static bool Crouch
        {
            get
            {
                var pad = Gamepad.current;
                return Held(GameAction.Agachar) || (pad != null && (pad.buttonEast.isPressed || pad.leftStickButton.isPressed));
            }
        }

        public static bool UsePressed
        {
            get
            {
                var keyboard = Keyboard.current;
                return (keyboard != null && keyboard[Binding(GameAction.Usar)].wasPressedThisFrame) ||
                       PressedPad(Gamepad.current?.buttonSouth);
            }
        }

        /// <summary>Pasar a la siguiente línea de diálogo.</summary>
        public static bool AdvancePressed =>
            UsePressed || (Keyboard.current != null && Keyboard.current.spaceKey.wasPressedThisFrame) ||
            (Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame);

        public static bool FlashlightPressed =>
            (Keyboard.current != null && Keyboard.current[Binding(GameAction.Linterna)].wasPressedThisFrame) ||
            PressedPad(Gamepad.current?.buttonNorth);

        /// <summary>Tapar la linterna: clic derecho o gatillo izquierdo, mantenidos.</summary>
        public static bool CoverHeld =>
            (Mouse.current != null && Mouse.current.rightButton.isPressed) ||
            (Gamepad.current != null && Gamepad.current.leftTrigger.ReadValue() > 0.4f);

        public static bool PausePressed =>
            (Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame) ||
            PressedPad(Gamepad.current?.startButton);
    }
}
