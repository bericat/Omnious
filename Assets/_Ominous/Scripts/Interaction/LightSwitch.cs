using UnityEngine;

namespace Ominous
{
    public class LightSwitch : Interactable
    {
        public Light[] lights;
        public bool isOn;
        public Renderer emissive;
        static readonly int Emission = Shader.PropertyToID("_EmissionColor");

        void Start() => ApplyState();

        public override string Prompt => isOn ? "Apagar la luz" : "Encender la luz";

        public override void Interact()
        {
            isOn = !isOn;
            Sfx.Play("interruptor", transform.position);
            ApplyState();
            base.Interact();
        }

        void ApplyState()
        {
            foreach (var l in lights)
                if (l != null) l.enabled = isOn;
            if (emissive == null) return;
            var block = new MaterialPropertyBlock();
            block.SetColor(Emission, isOn ? new Color(0.9f, 0.78f, 0.58f) : Color.black);
            emissive.SetPropertyBlock(block);
        }
    }
}
