using System;
using System.Collections.Generic;
using UnityEngine;

namespace Ominous
{
    /// <summary>Efectos de sonido por nombre, colocados en el mundo.</summary>
    public class Sfx : MonoBehaviour
    {
        [Serializable] public class Entry { public string name; public AudioClip clip; public float volume = 0.6f; }
        public List<Entry> clips = new();
        static Sfx instance;
        readonly Dictionary<string, Entry> map = new();

        void Awake()
        {
            instance = this;
            foreach (var e in clips) map[e.name] = e;
        }

        void OnDestroy()
        {
            if (instance == this) instance = null;
        }

        public static void Play(string name, Vector3 position, float pitchSpread = 0.05f)
        {
            if (instance == null || !instance.map.TryGetValue(name, out var e) || e.clip == null) return;
            var go = new GameObject("Sfx_" + name);
            go.transform.position = position;
            var s = go.AddComponent<AudioSource>();
            s.clip = e.clip;
            s.volume = e.volume;
            s.spatialBlend = 1f;
            s.minDistance = 1.2f;
            s.maxDistance = 22f;
            s.rolloffMode = AudioRolloffMode.Linear;
            s.pitch = 1f + UnityEngine.Random.Range(-pitchSpread, pitchSpread);
            s.Play();
            Destroy(go, e.clip.length + 0.2f);
        }
    }
}
