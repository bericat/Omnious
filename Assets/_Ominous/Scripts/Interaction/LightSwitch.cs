using UnityEngine;

namespace Ominous
{
    public class LightSwitch : Interactable
    {
        public Light[] lights;
        public bool isOn;
        public Renderer emissive;
        /// <summary>Más piezas que brillan con esta luz (bombillas, tubos).</summary>
        public Renderer[] emissives = new Renderer[0];
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

        /// <summary>Vuelve a aplicar el estado (por ejemplo, al irse o volver la luz de la casa).</summary>
        public void Refresh() => ApplyState();

        void ApplyState()
        {
            bool lit = isOn && HouseLights.Power;
            foreach (var l in lights)
                if (l != null) l.enabled = lit;
            var block = new MaterialPropertyBlock();
            block.SetColor(Emission, lit ? new Color(0.9f, 0.78f, 0.58f) : Color.black);
            if (emissive != null) emissive.SetPropertyBlock(block);
            foreach (var r in emissives)
            {
                if (r == null) continue;
                var own = new MaterialPropertyBlock();
                own.SetColor(Emission, lit ? r.sharedMaterial.GetColor(Emission) : Color.black);
                r.SetPropertyBlock(own);
            }
        }
    }
}
