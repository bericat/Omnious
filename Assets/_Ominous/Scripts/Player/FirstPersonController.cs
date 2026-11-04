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
        public static bool InputBlocked;

        CharacterController controller;
        float pitch, verticalVelocity, currentHeight, bobTime;

        void Awake()
        {
            controller = GetComponent<CharacterController>();
            currentHeight = standHeight;
        }

        void Start() => SetCursorLocked(true);

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

            if (keyboard.escapeKey.wasPressedThisFrame) SetCursorLocked(false);
            else if (!InputBlocked && mouse.leftButton.wasPressedThisFrame) SetCursorLocked(true);
            if (InputBlocked) SetCursorLocked(false);

            bool active = !InputBlocked && Cursor.lockState == CursorLockMode.Locked;
            Vector2 look = active ? mouse.delta.ReadValue() * mouseSensitivity : Vector2.zero;
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
