using UnityEngine;
using UnityEngine.InputSystem;

namespace Ominous
{
    /// <summary>Movimiento en primera persona con teclado y ratón o mando.</summary>
    [RequireComponent(typeof(CharacterController))]
    public class FirstPersonController : MonoBehaviour
    {
        public Transform cameraPivot;
        public float walkSpeed = 2.2f;
        public float crouchSpeed = 1.1f;
        public float mouseSensitivity = 0.08f;
        public float standHeight = 1.7f;
        public float crouchHeight = 1.05f;
        [Tooltip("Rapidez con la que la cámara sigue al ratón; más bajo, más pesada")]
        public float lookSmoothing = 22f;
        static readonly System.Collections.Generic.HashSet<object> blockers = new();
        /// <summary>Hay algo que impide moverse: un diálogo, la pausa o un panel.</summary>
        public static bool InputBlocked => blockers.Count > 0;
        public static void SetBlocked(object owner, bool blocked)
        {
            if (blocked) blockers.Add(owner); else blockers.Remove(owner);
        }

        CharacterController controller;
        float pitch, verticalVelocity, currentHeight, bobTime, yawTarget, pitchTarget, bobWeight, roll;

        void Awake()
        {
            controller = GetComponent<CharacterController>();
            currentHeight = standHeight;
            yawTarget = transform.eulerAngles.y;
        }

        void Start() => SetCursorLocked(true);

        void OnDestroy() => blockers.Clear();

        public void LookAt(Vector3 world)
        {
            if (cameraPivot == null) return;
            Vector3 d = world - cameraPivot.position;
            yawTarget = Mathf.Atan2(d.x, d.z) * Mathf.Rad2Deg;
            pitchTarget = -Mathf.Atan2(d.y, new Vector2(d.x, d.z).magnitude) * Mathf.Rad2Deg;
        }

        bool peeping;
        float normalFov;

        /// <summary>Mirar por la mirilla: la cámara se pone en otro sitio y con otro campo de visión.</summary>
        public void SetPeep(Vector3 position, float yaw, float fov)
        {
            if (cameraPivot == null) return;
            peeping = true;
            var cam = cameraPivot.GetComponent<Camera>();
            normalFov = cam.fieldOfView;
            cam.fieldOfView = fov;
            cameraPivot.SetPositionAndRotation(position, Quaternion.Euler(0f, yaw, 0f));
        }

        public void EndPeep()
        {
            peeping = false;
            cameraPivot.GetComponent<Camera>().fieldOfView = normalFov;
        }

        float stepPhase;

        public void Teleport(Vector3 position, float yaw)
        {
            if (controller != null) controller.enabled = false;
            transform.SetPositionAndRotation(position, Quaternion.Euler(0f, yaw, 0f));
            pitch = pitchTarget = 0f;
            verticalVelocity = 0f;
            yawTarget = yaw;
            if (controller != null) controller.enabled = true;
        }

        static void SetCursorLocked(bool locked)
        {
            Cursor.lockState = locked ? CursorLockMode.Locked : CursorLockMode.None;
            Cursor.visible = !locked;
        }

        void Update()
        {
            SetCursorLocked(!InputBlocked);

            bool active = !InputBlocked;
            Vector2 look = active ? GameInput.Look(mouseSensitivity) : Vector2.zero;
            yawTarget += look.x;
            pitchTarget = Mathf.Clamp(pitchTarget - look.y, -85f, 85f);
            // La cámara sigue al ratón con un poco de inercia, como algo que se sostiene en la mano.
            float follow = 1f - Mathf.Exp(-lookSmoothing * Time.deltaTime);
            float yaw = Mathf.LerpAngle(transform.eulerAngles.y, yawTarget, follow);
            transform.rotation = Quaternion.Euler(0f, yaw, 0f);
            pitch = Mathf.Lerp(pitch, pitchTarget, follow);

            Vector2 move = active ? GameInput.Move : Vector2.zero;
            bool crouching = active && GameInput.Crouch;
            float speed = crouching ? crouchSpeed : walkSpeed;
            Vector3 velocity = transform.TransformDirection(Vector3.ClampMagnitude(new Vector3(move.x, 0f, move.y), 1f)) * speed;

            verticalVelocity = controller.isGrounded ? -1f : verticalVelocity - 9.81f * Time.deltaTime;
            velocity.y = verticalVelocity;
            controller.Move(velocity * Time.deltaTime);

            currentHeight = Mathf.MoveTowards(currentHeight, crouching ? crouchHeight : standHeight, 2.5f * Time.deltaTime);
            controller.height = currentHeight;
            controller.center = new Vector3(0f, currentHeight * 0.5f, 0f);

            bool walking = move.sqrMagnitude > 0f;
            bobWeight = Mathf.MoveTowards(bobWeight, walking ? 1f : 0f, Time.deltaTime * 4f);
            bobTime += walking ? Time.deltaTime * speed * 3.1f : 0f;
            float bobY = Mathf.Sin(bobTime * 2f) * 0.014f * bobWeight;
            float bobX = Mathf.Sin(bobTime) * 0.009f * bobWeight;
            roll = Mathf.Lerp(roll, -move.x * 0.5f + Mathf.Sin(bobTime) * 0.18f * bobWeight, 1f - Mathf.Exp(-6f * Time.deltaTime));
            // Pulso de mano: deriva muy lenta e irregular, también con el jugador quieto.
            float t = Time.time;
            float motion = OminousOptions.ReduceEffects ? 0.2f : 1f;
            bobY *= motion;
            bobX *= motion;
            float handX = (Mathf.PerlinNoise(t * 0.33f, 1.3f) - 0.5f) * 0.55f;
            float handY = (Mathf.PerlinNoise(2.7f, t * 0.27f) - 0.5f) * 0.55f;
            float handZ = (Mathf.PerlinNoise(t * 0.21f, 5.9f) - 0.5f) * 0.4f;
            // Pasos: en el punto bajo del balanceo.
            float step = Mathf.Sin(bobTime * 2f);
            if (walking && step < -0.9f && stepPhase >= -0.9f) Sfx.Play("paso", transform.position, 0.1f);
            stepPhase = step;

            if (cameraPivot != null && !peeping)
            {
                cameraPivot.localPosition = new Vector3(bobX, currentHeight - 0.1f + bobY, 0f);
                cameraPivot.localRotation = Quaternion.Euler(pitch + handX * motion, handY * motion, (roll + handZ) * motion);
            }
        }
    }
}
