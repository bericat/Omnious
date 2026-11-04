using UnityEngine;

namespace Ominous
{
    public class LightSwitch : Interactable
    {
        public Light[] lights;
        public bool isOn;

        void Start() => ApplyState();

        public override string Prompt => isOn ? "Apagar la luz" : "Encender la luz";

        public override void Interact()
        {
            isOn = !isOn;
            ApplyState();
            base.Interact();
        }

        void ApplyState()
        {
            foreach (var l in lights)
                if (l != null) l.enabled = isOn;
        }
    }
}
