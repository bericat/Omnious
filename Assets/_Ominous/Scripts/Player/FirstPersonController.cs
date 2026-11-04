using UnityEngine;
using UnityEngine.InputSystem;

namespace Ominous
{
    /// <summary>Movimiento en primera persona con teclado y ratón.</summary>
    [RequireComponent(typeof(CharacterController))]
    public class FirstPersonController : MonoBehaviour
    {
        public Transform cameraPivot;
        public float walkSpeed = 2.2f;
        public float crouchSpeed = 1.1f;
        public float mouseSensitivity = 0.08f;
        public float standHeight = 1.7f;
        public float crouchHeight = 1.05f;
        static readonly System.Collections.Generic.HashSet<object> blockers = new();
        /// <summary>Hay algo que impide moverse: un diálogo, la pausa o un panel.</summary>
        public static bool InputBlocked => blockers.Count > 0;
        public static void SetBlocked(object owner, bool blocked)
        {
            if (blocked) blockers.Add(owner); else blockers.Remove(owner);
        }

        CharacterController controller;
        float pitch, verticalVelocity, currentHeight, bobTime;

        void Awake()
        {
            controller = GetComponent<CharacterController>();
            currentHeight = standHeight;
        }

        void Start() => SetCursorLocked(true);

        void OnDestroy() => blockers.Clear();

        public void Teleport(Vector3 position, float yaw)
        {
            if (controller != null) controller.enabled = false;
            transform.SetPositionAndRotation(position, Quaternion.Euler(0f, yaw, 0f));
            pitch = 0f;
            if (controller != null) controller.enabled = true;
        }

        static void SetCursorLocked(bool locked)
        {
            Cursor.lockState = locked ? CursorLockMode.Locked : CursorLockMode.None;
            Cursor.visible = !locked;
        }

        void Update()
        {
            var keyboard = Keyboard.current;
            var mouse = Mouse.current;
            if (keyboard == null || mouse == null) return;

            SetCursorLocked(!InputBlocked);

            bool active = !InputBlocked;
            Vector2 look = active ? mouse.delta.ReadValue() * (mouseSensitivity * OminousOptions.Sensitivity) : Vector2.zero;
            transform.Rotate(0f, look.x, 0f);
            pitch = Mathf.Clamp(pitch - look.y, -85f, 85f);

            Vector2 move = Vector2.zero;
            if (active)
            {
                if (keyboard.wKey.isPressed) move.y += 1f;
                if (keyboard.sKey.isPressed) move.y -= 1f;
                if (keyboard.dKey.isPressed) move.x += 1f;
                if (keyboard.aKey.isPressed) move.x -= 1f;
            }
            bool crouching = active && keyboard.leftCtrlKey.isPressed;
            float speed = crouching ? crouchSpeed : walkSpeed;
            Vector3 velocity = transform.TransformDirection(new Vector3(move.x, 0f, move.y).normalized) * speed;

            verticalVelocity = controller.isGrounded ? -1f : verticalVelocity - 9.81f * Time.deltaTime;
            velocity.y = verticalVelocity;
            controller.Move(velocity * Time.deltaTime);

            currentHeight = Mathf.MoveTowards(currentHeight, crouching ? crouchHeight : standHeight, 2.5f * Time.deltaTime);
            controller.height = currentHeight;
            controller.center = new Vector3(0f, currentHeight * 0.5f, 0f);

            bobTime += move.sqrMagnitude > 0f ? Time.deltaTime * speed * 3.2f : 0f;
            float bob = Mathf.Sin(bobTime) * 0.012f;
            if (cameraPivot != null)
            {
                cameraPivot.localPosition = new Vector3(0f, currentHeight - 0.1f + bob, 0f);
                cameraPivot.localRotation = Quaternion.Euler(pitch, 0f, 0f);
            }
        }
    }
}
