using System.Collections;
using UnityEngine;

namespace Ominous
{
    /// <summary>
    /// Oscuridad, bloque C (OSCURIDAD.md): en el acto 3 la casa está a oscuras y el diferencial no aguanta.
    /// Chechu recorre la casa despacio con una luz; si ve a Chevas medio segundo, lo «encuentra»: su cara de golpe,
    /// negro y Chevas despierta junto a la cama. Las farolas de la calle se apagan una a una.
    /// </summary>
    public partial class StoryDirector
    {
        Light chechuLamp;
        Coroutine hunting;
        bool huntOn, caught;
        float seenTime, lampTimer;
        int lampsOff, wakeLine;
        bool coldAirFelt;

        // Ruta de Chechu por la casa: pasillo, cocina, salón. Se para en los puntos marcados con y = 1.
        static readonly Vector3[] HuntRoute =
        {
            new(12.4f, 0f, 5.2f), new(10.45f, 1f, 5.2f), new(10.45f, 0f, 3.0f), new(10.45f, 1f, 2.6f), new(10.45f, 0f, 5.2f),
            new(6.05f, 0f, 5.2f), new(2.95f, 1f, 5.2f), new(6.05f, 0f, 5.2f), new(6.05f, 0f, 3.6f), new(5.6f, 0f, 2.55f),
            new(3.2f, 1f, 2.4f), new(5.6f, 0f, 2.55f), new(6.05f, 0f, 3.6f), new(6.05f, 0f, 5.2f),
        };

        float huntClock;
        /// <summary>Para pruebas automáticas: sin ronda de Chechu.</summary>
        public static bool HuntDisabled;

        /// <summary>
        /// Chechu no ronda siempre: 30 s de margen al empezar el acto 3 y después tramos de 100 s con 120 s de calma.
        /// </summary>
        bool HuntTime
        {
            get
            {
                if (HuntDisabled || (Current != Step.Acto3 && Current != Step.SotanoPuerta)) return false;
                float t = huntClock - 30f;
                return t > 0f && t % 220f < 100f;
            }
        }

        void UpdateHunt()
        {
            // El diferencial ya no sube en el acto 3.
            if (BreakerBox.Instance != null) BreakerBox.Instance.failsToHold = Current >= Step.Acto3 && Current < Step.BucleLlegada;

            if (Current == Step.Acto3 || Current == Step.SotanoPuerta) { if (!DialogueManager.Instance.IsBusy) huntClock += Time.deltaTime; }
            else huntClock = 0f;
            bool want = HuntTime && !caught && !blinking && Current != Step.Sotano;
            if (want != huntOn)
            {
                huntOn = want;
                if (want) StartHunt(); else StopHunt();
            }
            UpdateStreetLamps();
            // La rejilla del sótano se nota por el aire frío al acercarse.
            if (Current == Step.SotanoPuerta && !coldAirFelt && basementDoor != null && basementDoor.activeInHierarchy &&
                Vector3.Distance(player.transform.position, basementDoor.transform.position) < 2.2f && !DialogueManager.Instance.IsBusy)
            {
                coldAirFelt = true;
                DialogueManager.Instance.Play("Oscuridad_Rejilla");
            }
            // Los pensamientos no paran la ronda; solo las escenas en las que Chevas no puede moverse.
            if (!huntOn || caught || FirstPersonController.InputBlocked || peeping) return;

            if (CanChechuSee()) seenTime += Time.deltaTime;
            else seenTime = Mathf.Max(0f, seenTime - Time.deltaTime);
            if (seenTime > 0.5f)
            {
                Debug.Log($"[Chechu] te encuentra: distancia {Vector3.Distance(chechu.head.position, player.transform.position):F1}, linterna {(Flashlight.Instance != null ? Flashlight.Instance.Exposure : 0f)}, agachado {player.Crouching}");
                StartCoroutine(Caught());
            }
        }

        void StartHunt()
        {
            if (chechuLamp == null)
            {
                var go = new GameObject("LuzChechu");
                go.transform.SetParent(chechu.transform, false);
                go.transform.localPosition = new Vector3(0.18f, 1.2f, 0.25f);
                go.transform.localRotation = Quaternion.Euler(12f, 0f, 0f);
                chechuLamp = go.AddComponent<Light>();
                chechuLamp.type = LightType.Spot;
                chechuLamp.range = 7f;
                chechuLamp.spotAngle = 55f;
                chechuLamp.intensity = 1.8f;
                chechuLamp.color = new Color(0.85f, 0.9f, 1f);
                chechuLamp.shadows = LightShadows.Hard;
                chechuLamp.shadowResolution = UnityEngine.Rendering.LightShadowResolution.Low;
            }
            chechuLamp.enabled = true;
            chechu.Show(true);
            chechu.SetPose("depie");
            chechu.walkSpeed = 0.75f;
            // Aparece en el punto de la ronda más alejado de Chevas, nunca encima.
            int start = 0; float best = -1f;
            for (int k = 0; k < HuntRoute.Length; k++)
            {
                float dd = Vector3.Distance(new Vector3(HuntRoute[k].x, 0f, HuntRoute[k].z), player.transform.position);
                if (dd > best) { best = dd; start = k; }
            }
            chechu.Place(new Vector3(HuntRoute[start].x, 0f, HuntRoute[start].z), 0f);
            seenTime = 0f;
            hunting = StartCoroutine(Patrol(start));
        }

        void StopHunt()
        {
            if (hunting != null) StopCoroutine(hunting);
            hunting = null;
            if (chechuLamp != null) chechuLamp.enabled = false;
            if (!caught && HuntTime == false && Current < Step.BucleLlegada) chechu.Show(false);
        }

        IEnumerator Patrol(int i)
        {
            while (true)
            {
                var p = HuntRoute[i];
                bool pause = p.y > 0.5f;
                p.y = 0f;
                bool arrived = false;
                chechu.Walk(new[] { p }, () => arrived = true);
                while (!arrived) yield return null;
                if (pause)
                {
                    // Se para y mira: a un lado, al otro.
                    float yaw = chechu.transform.eulerAngles.y;
                    foreach (float d in new[] { -50f, 50f, 0f })
                    {
                        float t = 0f;
                        Quaternion from = chechu.transform.rotation, to = Quaternion.Euler(0f, yaw + d, 0f);
                        while (t < 1f) { t += Time.deltaTime * 0.8f; chechu.transform.rotation = Quaternion.Slerp(from, to, t); yield return null; }
                        yield return new WaitForSeconds(0.9f);
                    }
                }
                i = (i + 1) % HuntRoute.Length;
            }
        }

        /// <summary>
        /// Chechu ve a Chevas si está delante de él, sin paredes en medio y o bien lleva la linterna destapada,
        /// o bien está dentro de su luz sin agacharse. Tapada la linterna y agachado, la luz puede pasar cerca.
        /// </summary>
        bool CanChechuSee()
        {
            Vector3 eye = chechu.head.position;
            Vector3 target = player.cameraPivot != null ? player.cameraPivot.position : player.transform.position + Vector3.up * 1.5f;
            Vector3 to = target - eye;
            float dist = to.magnitude;
            if (dist > 7.5f) return false;
            if (Vector3.Angle(chechu.transform.forward, to) > 38f) return false;
            foreach (var h in Physics.RaycastAll(eye, to / dist, dist - 0.2f, ~0, QueryTriggerInteraction.Ignore))
            {
                if (h.collider is CharacterController || h.collider.transform.IsChildOf(chechu.transform)) continue;
                var door = h.collider.GetComponentInParent<Door>();
                if (h.collider is MeshCollider || (door != null && !door.IsOpen)) return false;
            }
            float exposure = Flashlight.Instance != null ? Flashlight.Instance.Exposure : 0f;
            if (dist < 4f) exposure += player.Crouching ? 0.15f : 0.6f;
            if (HidingSpot()) exposure = 0f;
            return exposure >= 0.5f;
        }

        bool HidingSpot()
        {
            Vector3 p = player.transform.position;
            bool underTable = player.Crouching && p.x > 8.5f && p.x < 9.5f && p.z > 1.5f && p.z < 3.2f;
            bool inCloset = p.x > 5.3f && p.x < 5.95f && p.z > 7.95f && p.z < 9.45f;
            return underTable || inCloset;
        }

        IEnumerator Caught()
        {
            caught = true;
            if (hunting != null) StopCoroutine(hunting);
            FirstPersonController.SetBlocked(this, true);
            // La cara de Chechu, de golpe.
            Vector3 cam = player.cameraPivot.position;
            Vector3 fwd = player.cameraPivot.forward; fwd.y = 0f; fwd.Normalize();
            chechu.Place(new Vector3(cam.x, 0f, cam.z) + fwd * 0.55f, Quaternion.LookRotation(-fwd).eulerAngles.y);
            Sfx.Play("encontrado", cam);
            yield return new WaitForSeconds(0.45f);
            GameUI.Instance.SetBlack();
            chechu.Show(false);
            if (chechuLamp != null) chechuLamp.enabled = false;
            yield return new WaitForSeconds(1.4f);
            // Despierta junto a la cama, con Roberta en ella como si nada.
            player.Teleport(new Vector3(1.95f, 0.02f, 6.85f), 330f);
            Sfx.Play("despertar", player.transform.position);
            roberta.Show(true);
            PutRobertaInBed();
            yield return GameUI.Instance.Fade(0f, 1.6f);
            string[] lines = { "Oscuridad_Despertar1", "Oscuridad_Despertar2", "Oscuridad_Despertar3", "Oscuridad_Despertar4" };
            bool done = false;
            DialogueManager.Instance.Play(lines[wakeLine++ % lines.Length], () => done = true);
            while (!done) yield return null;
            // Al parpadear, Roberta ya no está.
            yield return GameUI.Instance.Fade(1f, 0.25f);
            HideRoberta();
            yield return new WaitForSeconds(0.4f);
            yield return GameUI.Instance.Fade(0f, 0.6f);
            FirstPersonController.SetBlocked(this, false);
            caught = false;
            huntOn = false;   // vuelve a empezar la ronda desde el principio
        }

        void UpdateStreetLamps()
        {
            if (Current < Step.Acto3 || Current >= Step.BucleLlegada) { lampTimer = 0f; return; }
            lampTimer += Time.deltaTime;
            if (lampTimer < 45f) return;
            lampTimer = 0f;
            // Se apaga la siguiente farola que quede encendida, con su bombilla.
            foreach (var l in FindObjectsByType<Light>(FindObjectsSortMode.None))
            {
                if (l.name != "LuzFarola" || !l.enabled) continue;
                l.enabled = false;
                foreach (var r in FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))
                    if (r.name == "Luz" && Vector3.Distance(new Vector3(r.transform.position.x, 0, r.transform.position.z), new Vector3(l.transform.position.x, 0, l.transform.position.z)) < 1.2f)
                        r.enabled = false;
                lampsOff++;
                break;
            }
        }
    }
}
