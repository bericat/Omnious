using UnityEngine;

namespace Ominous
{
    /// <summary>Gira o desliza un objeto hasta su posición abierta.</summary>
    public class SimpleHinge : MonoBehaviour
    {
        public float openYaw;
        public Vector3 openOffset;
        public float seconds = 1f;
        public bool IsOpen { get; private set; }
        float t;
        Vector3 start;
        Quaternion startRotation;
        bool ready;

        void Prepare()
        {
            if (ready) return;
            start = transform.localPosition;
            startRotation = transform.localRotation;
            ready = true;
        }

        void Awake() => Prepare();

        public void Open() { Prepare(); IsOpen = true; }
        public void OpenNow() { Prepare(); IsOpen = true; t = 1f; Apply(); }

        void Update()
        {
            if (!IsOpen || t >= 1f) return;
            t = Mathf.Min(1f, t + Time.deltaTime / Mathf.Max(0.01f, seconds));
            Apply();
        }

        void Apply()
        {
            float e = Mathf.SmoothStep(0f, 1f, t);
            transform.localPosition = start + openOffset * e;
            transform.localRotation = startRotation * Quaternion.Euler(0f, openYaw * e, 0f);
        }
    }
}
