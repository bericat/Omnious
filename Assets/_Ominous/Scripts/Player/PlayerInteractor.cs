using UnityEngine;
using UnityEngine.InputSystem;

namespace Ominous
{
    /// <summary>Mira qué hay delante, muestra el aviso y usa el objeto con E o clic.</summary>
    public class PlayerInteractor : MonoBehaviour
    {
        public Transform eye;
        public float reach = 2.1f;
        public Interactable Current { get; private set; }

        readonly RaycastHit[] hits = new RaycastHit[12];

        /// <summary>Lo primero que se pueda usar en línea de mirada; una zona inactiva no tapa lo que hay detrás.</summary>
        Interactable FindTarget()
        {
            int count = Physics.RaycastNonAlloc(eye.position, eye.forward, hits, reach, ~0, QueryTriggerInteraction.Collide);
            System.Array.Sort(hits, 0, count, System.Collections.Generic.Comparer<RaycastHit>.Create((a, b) => a.distance.CompareTo(b.distance)));
            for (int i = 0; i < count; i++)
            {
                var found = hits[i].collider.GetComponentInParent<Interactable>();
                if (found != null && found.CanUse) return found;
                if (!hits[i].collider.isTrigger && found == null) return null;
            }
            return null;
        }

        void Update()
        {
            Current = null;
            bool free = !FirstPersonController.InputBlocked && !(DialogueManager.Instance != null && DialogueManager.Instance.IsRunning);
            if (free && eye != null) Current = FindTarget();

            GameUI.Instance?.SetPrompt(Current != null ? $"[E] {Current.Prompt}" : null);

            var keyboard = Keyboard.current;
            if (Current != null && keyboard != null && keyboard.eKey.wasPressedThisFrame) Current.Interact();
        }
    }
}
