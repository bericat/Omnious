using UnityEngine;
using UnityEngine.Events;

namespace Ominous
{
    /// <summary>Base de todo lo que se usa con E: aviso en pantalla y evento.</summary>
    public class Interactable : MonoBehaviour
    {
        public string prompt = "Usar";
        public UnityEvent onInteract;

        public virtual string Prompt => prompt;
        public virtual void Interact() => onInteract?.Invoke();
    }
}
