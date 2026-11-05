using UnityEngine;

namespace Ominous
{
    /// <summary>Mira qué hay delante, muestra el aviso y usa el objeto con E o clic.</summary>
    public class PlayerInteractor : MonoBehaviour
    {
        public Transform eye;
        public float reach = 2.4f;
        public Interactable Current { get; private set; }

        readonly RaycastHit[] hits = new RaycastHit[16];

        /// <summary>
        /// El aviso sale justo al apuntar al objeto. Paredes y puertas cerradas tapan lo de detrás;
        /// los muebles no, para que se pueda hablar con alguien sentado en el sofá.
        /// </summary>
        Interactable FindTarget()
        {
            int count = Physics.RaycastNonAlloc(eye.position, eye.forward, hits, reach, ~0, QueryTriggerInteraction.Collide);
            System.Array.Sort(hits, 0, count, System.Collections.Generic.Comparer<RaycastHit>.Create((a, b) => a.distance.CompareTo(b.distance)));
            for (int i = 0; i < count; i++)
            {
                var c = hits[i].collider;
                var found = c.GetComponentInParent<Interactable>();
                if (found != null && found.CanUse) return found;
                var door = c.GetComponentInParent<Door>();
                if (c is MeshCollider || (door != null && !door.IsOpen)) return null;
            }
            return null;
        }

        void Update()
        {
            Current = null;
            bool free = !FirstPersonController.InputBlocked && !(DialogueManager.Instance != null && DialogueManager.Instance.IsRunning);
            if (free && eye != null) Current = FindTarget();

            GameUI.Instance?.SetPrompt(Current != null ? $"[{GameInput.UseLabel}] {Current.Prompt}" : null);

            if (Current != null && GameInput.UsePressed) Current.Interact();
        }
    }
}
