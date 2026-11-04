using System;
using System.IO;
using UnityEngine;

namespace Ominous
{
    [Serializable]
    public class SaveData
    {
        public string scene;
        public string checkpoint;
        public NightState night;
        public Vector3 playerPosition;
        public float playerYaw;
    }

    /// <summary>Partida única en JSON. Se escribe a un temporal para no corromperla si el juego se cierra a medias.</summary>
    public static class SaveSystem
    {
        /// <summary>Lo activa el menú al elegir Continuar; lo consume GameDirector.</summary>
        public static bool LoadRequested;

        static string SavePath => Path.Combine(Application.persistentDataPath, "partida.json");

        public static bool Exists => File.Exists(SavePath);

        public static void Save(SaveData data)
        {
            string temp = SavePath + ".tmp";
            File.WriteAllText(temp, JsonUtility.ToJson(data, true));
            File.Copy(temp, SavePath, true);
            File.Delete(temp);
        }

        public static SaveData Load()
        {
            if (!Exists) return null;
            try { return JsonUtility.FromJson<SaveData>(File.ReadAllText(SavePath)); }
            catch (Exception e)
            {
                Debug.LogError($"No se pudo leer la partida: {e.Message}");
                return null;
            }
        }

        public static void Delete()
        {
            if (Exists) File.Delete(SavePath);
        }
    }
}
