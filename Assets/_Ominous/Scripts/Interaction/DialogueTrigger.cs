using UnityEngine;

namespace Ominous
{
    /// <summary>Lanza un nodo de Yarn: examinar un objeto o hablar con alguien.</summary>
    public class DialogueTrigger : Interactable
    {
        public string node;

        public void Configure(string promptText, string yarnNode)
        {
            prompt = promptText;
            node = yarnNode;
        }

        public override void Interact()
        {
            DialogueManager.Instance?.Play(node);
            base.Interact();
        }
    }
}
