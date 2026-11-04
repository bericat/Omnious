using UnityEngine;

namespace Ominous
{
    /// <summary>Puerta con bisagra en el origen de este objeto.</summary>
    public class Door : Interactable
    {
        public float openYaw = 95f;
        public float speed = 200f;
        public bool locked;
        [TextArea] public string lockedNode;
        public bool IsOpen { get; private set; }

        float closedYaw, current;

        void Awake() => closedYaw = transform.localEulerAngles.y;

        public override string Prompt => IsOpen ? "Cerrar" : "Abrir";

        public override void Interact()
        {
            if (locked)
            {
                if (!string.IsNullOrEmpty(lockedNode)) DialogueManager.Instance?.Play(lockedNode);
                return;
            }
            IsOpen = !IsOpen;
            base.Interact();
        }

        void Update()
        {
            current = Mathf.MoveTowards(current, IsOpen ? openYaw : 0f, speed * Time.deltaTime);
            transform.localRotation = Quaternion.Euler(0f, closedYaw + current, 0f);
        }
    }
}
