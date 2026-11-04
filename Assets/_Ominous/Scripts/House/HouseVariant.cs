using UnityEngine;

namespace Ominous
{
    /// <summary>Muestra este objeto solo en los actos indicados. Nada de duplicar escenas.</summary>
    public class HouseVariant : MonoBehaviour
    {
        public int fromAct = 1;
        public int toAct = 99;

        public void Apply(NightState night) => gameObject.SetActive(night.act >= fromAct && night.act <= toAct);
    }
}
