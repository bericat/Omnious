using UnityEngine;
using UnityEngine.InputSystem;

namespace Ominous
{
    /// <summary>Mira qué hay delante, muestra el aviso y usa el objeto con E o clic.</summary>
    public class PlayerInteractor : MonoBehaviour
    {
        public Transform eye;
        public float reach = 2.4f;
        public Interactable Current { get; private set; }

        const float AimRadius = 0.3f;
        readonly RaycastHit[] hits = new RaycastHit[16];

        /// <summary>
        /// Basta estar cerca y apuntar más o menos. Paredes y puertas cerradas tapan lo de detrás;
        /// los muebles no, para que se pueda hablar con alguien sentado en el sofá.
        /// </summary>
        Interactable FindTarget()
        {
            Vector3 origin = eye.position, dir = eye.forward;
            float blocked = reach;
            int count = Physics.RaycastNonAlloc(origin, dir, hits, reach, ~0, QueryTriggerInteraction.Ignore);
            for (int i = 0; i < count; i++)
            {
                var c = hits[i].collider;
                var door = c.GetComponentInParent<Door>();
                bool closedDoor = door != null && !door.IsOpen;
                if ((c is MeshCollider || closedDoor) && hits[i].distance < blocked) blocked = hits[i].distance;
            }

            count = Physics.SphereCastNonAlloc(origin, AimRadius, dir, hits, reach, ~0, QueryTriggerInteraction.Collide);
            Interactable best = null;
            float bestScore = float.MaxValue;
            for (int i = 0; i < count; i++)
            {
                var c = hits[i].collider;
                var found = c.GetComponentInParent<Interactable>();
                if (found == null || !found.CanUse) continue;
                Vector3 nearest = c.bounds.ClosestPoint(origin + dir * Mathf.Min(blocked, 1f));
                float along = Vector3.Dot(nearest - origin, dir);
                if (along > blocked + 0.05f) continue;
                // Lo más cercano a la línea de mirada.
                float score = Vector3.Cross(dir, c.bounds.center - origin).magnitude / Mathf.Max(0.3f, (c.bounds.center - origin).magnitude);
                if (c.bounds.IntersectRay(new Ray(origin, dir))) score -= 1f;
                if (score < bestScore)
                {
                    bestScore = score;
                    best = found;
                }
            }
            return best;
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
