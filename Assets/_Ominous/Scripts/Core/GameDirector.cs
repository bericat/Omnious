using System;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Ominous
{
    /// <summary>Lleva el estado de la noche, aplica las variantes de la casa y guarda en los puntos de control.</summary>
    [DefaultExecutionOrder(-50)]
    public class GameDirector : MonoBehaviour
    {
        public static GameDirector Instance { get; private set; }
        public NightState Night { get; private set; } = new();
        public event Action Changed;
        /// <summary>La partida viene de un punto de control: el director de historia debe recolocar la escena.</summary>
        public bool Restored { get; private set; }

        void Awake() => Instance = this;

        void OnDestroy()
        {
            if (Instance == this) Instance = null;
        }

        void Start()
        {
            if (SaveSystem.LoadRequested)
            {
                SaveSystem.LoadRequested = false;
                RestoreCheckpoint();
                Restored = true;
            }
            else ApplyVariants();
            Changed?.Invoke();
        }

        public void SetAct(int act) { Night.act = act; ApplyVariants(); Changed?.Invoke(); }
        public void SetVisit(int visit) { Night.visit = visit; Changed?.Invoke(); }
        public void SetHour(string hour) { Night.hour = hour; Changed?.Invoke(); }
        public void SetObjective(string objective) { Night.objective = objective; Changed?.Invoke(); }
        public void SetHouseVariant(string variant) { Night.houseVariant = variant; ApplyVariants(); Changed?.Invoke(); }

        public void OpenRoom(int room)
        {
            if (!Night.openRooms.Contains(room)) Night.openRooms.Add(room);
            Changed?.Invoke();
        }

        void ApplyVariants()
        {
            foreach (var v in FindObjectsByType<HouseVariant>(FindObjectsInactive.Include, FindObjectsSortMode.None))
                v.Apply(Night);
        }

        public void Checkpoint(string id)
        {
            var player = FindAnyObjectByType<FirstPersonController>();
            SaveSystem.Save(new SaveData
            {
                scene = SceneManager.GetActiveScene().name,
                checkpoint = id,
                night = Night,
                playerPosition = player != null ? player.transform.position : Vector3.zero,
                playerYaw = player != null ? player.transform.eulerAngles.y : 0f,
            });
        }

        public void RestoreCheckpoint()
        {
            var data = SaveSystem.Load();
            if (data == null) return;
            Night = data.night ?? new NightState();
            var player = FindAnyObjectByType<FirstPersonController>();
            if (player != null) player.Teleport(data.playerPosition, data.playerYaw);
            ApplyVariants();
            Changed?.Invoke();
        }
    }
}
