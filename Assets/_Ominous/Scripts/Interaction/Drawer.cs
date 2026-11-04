using UnityEngine;

namespace Ominous
{
    /// <summary>Cajón que se desliza en local.</summary>
    public class Drawer : Interactable
    {
        public Vector3 openOffset = new(0f, 0f, -0.28f);
        public float speed = 0.8f;
        public bool IsOpen { get; private set; }

        Vector3 closedPosition;

        void Awake() => closedPosition = transform.localPosition;

        public override string Prompt => IsOpen ? "Cerrar el cajón" : "Abrir el cajón";

        public override void Interact()
        {
            IsOpen = !IsOpen;
            Sfx.Play("puerta_cierra", transform.position, 0.2f);
            base.Interact();
        }

        void Update()
        {
            Vector3 target = closedPosition + (IsOpen ? openOffset : Vector3.zero);
            transform.localPosition = Vector3.MoveTowards(transform.localPosition, target, speed * Time.deltaTime);
        }
    }
}
