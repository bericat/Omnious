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

        void Update()
        {
            Current = null;
            bool free = !FirstPersonController.InputBlocked && !(DialogueManager.Instance != null && DialogueManager.Instance.IsRunning);
            if (free && eye != null && Physics.Raycast(eye.position, eye.forward, out var hit, reach, ~0, QueryTriggerInteraction.Ignore))
                Current = hit.collider.GetComponentInParent<Interactable>();

            GameUI.Instance?.SetPrompt(Current != null ? $"[E] {Current.Prompt}" : null);

            var keyboard = Keyboard.current;
            if (Current != null && keyboard != null && keyboard.eKey.wasPressedThisFrame) Current.Interact();
        }
    }
}
