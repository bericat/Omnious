using System;
using UnityEngine;

namespace Ominous
{
    /// <summary>Opciones del jugador, guardadas entre partidas.</summary>
    public static class OminousOptions
    {
        public static event Action Changed;

        public static bool Subtitles { get => PlayerPrefs.GetInt("subs", 1) == 1; set => Set("subs", value ? 1 : 0); }
        public static float TextSize { get => PlayerPrefs.GetFloat("texto", 1f); set => Set("texto", value); }
        public static float Brightness { get => PlayerPrefs.GetFloat("brillo", 1f); set => Set("brillo", value); }
        public static float Sensitivity { get => PlayerPrefs.GetFloat("sensibilidad", 1f); set => Set("sensibilidad", value); }
        public static float CameraEffectIntensity { get => PlayerPrefs.GetFloat("camara", 1f); set => Set("camara", value); }

        /// <summary>Menos balanceo y menos efectos de lente, para quien se marea.</summary>
        public static bool ReduceEffects { get => PlayerPrefs.GetInt("reducir", 0) == 1; set => Set("reducir", value ? 1 : 0); }

        static void Set(string key, int value) { PlayerPrefs.SetInt(key, value); PlayerPrefs.Save(); Changed?.Invoke(); }
        static void Set(string key, float value) { PlayerPrefs.SetFloat(key, value); PlayerPrefs.Save(); Changed?.Invoke(); }
    }
}
