using UnityEngine;

namespace Ominous
{
    /// <summary>Coches lejanos de vez en cuando; el resto del ambiente son fuentes en bucle colocadas en la casa.</summary>
    public class AmbientSounds : MonoBehaviour
    {
        public AudioSource carSource;
        public AudioClip carClip;
        public Vector2 carEvery = new(35f, 110f);
        float next;

        void Start() => next = Time.time + Random.Range(12f, 40f);

        void Update()
        {
            if (Time.time < next || carSource == null || carClip == null) return;
            carSource.pitch = Random.Range(0.85f, 1.1f);
            carSource.panStereo = Random.Range(-0.5f, 0.5f);
            carSource.volume = Random.Range(0.14f, 0.26f);
            carSource.PlayOneShot(carClip);
            next = Time.time + Random.Range(carEvery.x, carEvery.y);
        }
    }
}
