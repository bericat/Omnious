using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace Ominous
{
    /// <summary>Con el mando, siempre hay un botón seleccionado en los menús.</summary>
    public class GamepadMenuFocus : MonoBehaviour
    {
        void Update()
        {
            var system = EventSystem.current;
            if (system == null || !GameInput.UsingGamepad) return;
            var selected = system.currentSelectedGameObject;
            if (selected != null && selected.activeInHierarchy) return;
            Selectable best = null;
            foreach (var s in Selectable.allSelectablesArray)
                if (s.IsInteractable() && s.isActiveAndEnabled && (best == null || s.transform.position.y > best.transform.position.y))
                    best = s;
            if (best != null) system.SetSelectedGameObject(best.gameObject);
        }
    }
}
