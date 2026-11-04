using System;
using System.Collections.Generic;

namespace Ominous
{
    /// <summary>Todo lo que hay que saber de la noche. El resto del juego pregunta aquí.</summary>
    [Serializable]
    public class NightState
    {
        public int act = 1;
        public int visit;
        public int storyStep;
        public string hour = "01:50";
        public string objective = "";
        public bool robertaInBed;
        public string houseVariant = "normal";
        public List<int> openRooms = new();
        public List<string> flags = new();
    }
}
