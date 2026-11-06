using UnityEditor;
using UnityEngine;

namespace Ominous.EditorTools
{
    // Recibidor y salón según la referencia de Toni (Docs/Referencias/recibidor_salon_mejorado.png):
    // zócalo de madera, lámparas de mesa encendidas, cuadros de paisaje, reloj de pared, planta grande,
    // perchero de pared y sofá marrón. Los modelos que aún no existen se saltan sin romper nada.
    public static partial class SalonBuilder
    {
        static readonly Color LampWarm = new Color(1f, 0.7f, 0.4f);

        static void DressHallAndSalon(Transform f, Transform lights)
        {
            Skirting(f);

            // Recibidor: lámpara de mesa en el mueble, cuadro encima y perchero de pared antes de la puerta del salón.
            var hallLamp = TableLamp(f, lights, "LamparaRecibidor", new Vector3(6.86f, 0.84f, 1.98f), 270f);
            AddToSwitch("Interruptor_Recibidor", hallLamp);
            if (Model("CuadroPaisaje2", f, 6.93f, 1.5f, 270f, "CuadroRecibidor", 1.62f, collider: false) == null)
                Picture(f, "CuadroRecibidor", paintB, 6.925f, 1.62f, 1.5f, 90f, 0.5f, 0.66f);
            Model("PercheroPared", f, 5.072f, 1.45f, 90f, null, 0f, collider: false);
            Model("AlfombraPasillo", f, 6.0f, 2.25f, 0f, collider: false);

            // Salón: lámpara en el aparador, cuadro sobre la tele, reloj junto a la puerta y planta grande en la esquina.
            float sideboardTop = 0.8f;
            var salonLamp = TableLamp(f, lights, "LamparaAparador", new Vector3(3.5f, sideboardTop, 4.2f), 180f);
            AddToSwitch("Interruptor_Salon", salonLamp);
            if (Model("CuadroPaisaje1", f, 1.2f, 4.33f, 180f, "CuadroSalonTele", 1.72f, collider: false) == null)
                Picture(f, "CuadroSalonTele", paintB, 1.2f, 1.72f, 4.325f, 0f, 0.8f, 0.56f);
            Model("Reloj", f, 4.92f, 3.75f, 90f, "RelojSalon", 1.95f, collider: false);
            if (Model("PlantaGrande", f, 0.42f, 3.98f, 30f) != null)
            {
                var old = GameObject.Find("Planta");
                if (old != null && old.transform.position.x < 1f) Object.DestroyImmediate(old);
            }
            Model("Taza", f, 1.85f, 2.82f, 40f, null, 0.4175f, collider: false);
            Model("Mando", f, 2.45f, 2.68f, 75f, null, 0.4175f, collider: false);

            // Paisaje sobre el aparador en lugar de «La noche estrellada», como en la referencia.
            if (Model("CuadroPaisaje3", f, 3.22f, 4.33f, 180f, "CuadroAparador", 1.6f, collider: false) != null)
            {
                var starry = GameObject.Find("CuadroSalon");
                if (starry != null) Object.DestroyImmediate(starry);
            }
        }

        /// <summary>Lámpara de mesa del pack de Toni con su luz cálida, sin sombra.</summary>
        static Light TableLamp(Transform f, Transform lights, string name, Vector3 at, float yaw)
        {
            var lamp = PackPlace("Assets/_Ominous/Art/Externos/LamparaMesa/LamparaMesa.fbx", null, null, f, at, yaw, 1f, "LamparaMesa_Color.png", name);
            float top = at.y + 0.42f;
            if (lamp != null)
            {
                var b = lamp.GetComponentInChildren<Renderer>().bounds;
                foreach (var r in lamp.GetComponentsInChildren<Renderer>()) b.Encapsulate(r.bounds);
                top = b.min.y + b.size.y * 0.72f;
            }
            var l = Point("Luz" + name, lights, new Vector3(at.x, top, at.z), LampWarm, 1.3f, 3.2f);
            return l;
        }

        static void AddToSwitch(string switchName, Light light)
        {
            var go = GameObject.Find(switchName);
            var ls = go != null ? go.GetComponent<LightSwitch>() : null;
            if (ls == null) return;
            var list = new System.Collections.Generic.List<Light>(ls.lights ?? new Light[0]) { light };
            ls.lights = list.ToArray();
            light.enabled = ls.isOn;
        }

        /// <summary>Zócalo de madera oscura en el salón y el recibidor, cortado en las puertas.</summary>
        static void Skirting(Transform f)
        {
            var k = new MeshKit();
            const float h = 0.1f, t = 0.018f;
            float off = Thick / 2 + 0.012f + t / 2;
            void Run(float plane, bool alongX, float from, float to)
            {
                if (to - from < 0.02f) return;
                float mid = (from + to) / 2;
                var c = alongX ? new Vector3(mid, h / 2, plane) : new Vector3(plane, h / 2, mid);
                k.Box(c, alongX ? new Vector3(to - from, h, t) : new Vector3(t, h, to - from), woodDark);
            }
            // Salón (x 0-5, z 0-4,4); puerta al recibidor en x = 5, z 2,1-3.
            Run(off, true, 0f, 5f);
            Run(4.4f - off, true, 0f, 5f);
            Run(off, false, 0f, 4.4f);
            Run(5f - off, false, 0f, 2.05f);
            Run(5f - off, false, 3.05f, 4.4f);
            // Recibidor (x 5-7); puerta de entrada x 5,55-6,45 y al pasillo x 5,6-6,5.
            Run(off, true, 5f, 5.5f);
            Run(off, true, 6.5f, 7f);
            Run(4.4f - off, true, 5f, 5.55f);
            Run(4.4f - off, true, 6.55f, 7f);
            Run(5f + off, false, 0f, 2.05f);
            Run(5f + off, false, 3.05f, 4.4f);
            Run(7f - off, false, 0f, 4.4f);
            Put("Zocalo_SalonRecibidor", k, f, 0f, 0f, 0f, false);
        }
    }
}
