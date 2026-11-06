using UnityEngine;

namespace Ominous
{
    /// <summary>
    /// El diferencial de la casa, en la colada. Bajarlo o subirlo corta o devuelve la luz.
    /// El guion puede hacerlo saltar, bloquearlo o hacer que la luz vuelva un segundo y se vaya.
    /// </summary>
    public class BreakerBox : Interactable
    {
        public static BreakerBox Instance { get; private set; }

        [Tooltip("Acto 3: al subirlo, la luz vuelve un instante y se va")] public bool failsToHold;
        public System.Action onRaised;

        public override string Prompt => HouseLights.Power ? "Bajar el diferencial" : "Subir el diferencial";

        void Awake() => Instance = this;
        void OnDestroy() { if (Instance == this) Instance = null; }

        public override void Interact()
        {
            Sfx.Play(HouseLights.Power ? "diferencial_baja" : "diferencial_sube", transform.position);
            if (HouseLights.Power) HouseLights.SetPower(false);
            else if (failsToHold) StartCoroutine(FlickerOut());
            else
            {
                HouseLights.SetPower(true);
                onRaised?.Invoke();
            }
            base.Interact();
        }

        /// <summary>Salta solo: la casa se queda a oscuras.</summary>
        public void Trip()
        {
            Sfx.Play("diferencial_baja", transform.position);
            HouseLights.SetPower(false);
        }

        System.Collections.IEnumerator FlickerOut()
        {
            HouseLights.SetPower(true);
            yield return new WaitForSeconds(0.9f);
            Sfx.Play("diferencial_baja", transform.position);
            HouseLights.SetPower(false);
        }
    }
}
