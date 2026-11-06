using System.Collections;
using UnityEngine;

namespace Ominous
{
    /// <summary>
    /// Oscuridad, bloque B (OSCURIDAD.md): la linterna del cajón, la luz del móvil de Chechu en la visita 1,
    /// la casa de enfrente que responde a la linterna, el gran apagón del salón, la línea de luz bajo la
    /// estantería, el porche que se enciende al subir el diferencial y el apagón de la búsqueda de Roberta.
    /// </summary>
    public partial class StoryDirector
    {
        [Header("Oscuridad")]
        public GameObject lightUnderShelf;
        public GameObject[] wallDots;

        Light phoneLight;
        bool windowFlashDone, blackout1Done, blackout1Raised, blackout2Done;
        float windowFlashTimer;

        bool CanUseDark(string id) => id switch
        {
            "linterna" => !Flashlight.Owned && Current >= Step.Tareas && Current < Step.Fin,
            _ => false,
        };

        bool OnUseDark(string id)
        {
            if (id != "linterna") return false;
            Flashlight.Give();
            DialogueManager.Instance.Play("Oscuridad_Linterna");
            return true;
        }

        void StartDark()
        {
            AudioListener.volume = 1f;
            if (BreakerBox.Instance != null)
            {
                BreakerBox.Instance.onRaised = OnPowerBack;
                BreakerBox.Instance.onFailed = () => DialogueManager.Instance.Play("Oscuridad_SinLuz");
            }
            var go = new GameObject("LuzMovilChechu");
            phoneLight = go.AddComponent<Light>();
            phoneLight.type = LightType.Point;
            phoneLight.color = new Color(0.72f, 0.82f, 1f);
            phoneLight.range = 1.3f;
            phoneLight.intensity = 0.9f;
            phoneLight.shadows = LightShadows.None;
            phoneLight.enabled = false;
        }

        void UpdateDark()
        {
            // Visita 1: Chechu espera al otro lado con la cara iluminada desde abajo por el móvil.
            bool phone = (Current == Step.Llamada || Current == Step.EsperaPuerta || Current == Step.Visita) && chechu.gameObject.activeInHierarchy;
            if (phoneLight != null)
            {
                phoneLight.enabled = phone;
                if (phone) phoneLight.transform.position = chechu.head.position + new Vector3(0f, -0.45f, 0.22f);
            }

            // Después de la visita 1: si Chevas apunta con la linterna a la calle, enfrente se enciende una luz un momento.
            if (!windowFlashDone && Current >= Step.CerrarPuerta && Current < Step.EsperaV2 && Flashlight.Instance != null &&
                Flashlight.Instance.Exposure > 0.5f && NearFrontWindow())
            {
                windowFlashTimer += Time.deltaTime;
                if (windowFlashTimer > 3f)
                {
                    windowFlashDone = true;
                    StartCoroutine(WindowFlash());
                }
            }
            else windowFlashTimer = 0f;

            // La línea de luz bajo la estantería: solo se ve con la casa a oscuras y antes de descubrir el cuartito.
            if (lightUnderShelf != null) lightUnderShelf.SetActive(!HouseLights.Power && Current < Step.Cuartito);
            // Los puntos de luz de los agujeros del dormitorio, durante el apagón de la búsqueda. Uno se apaga al acercarse.
            if (wallDots != null)
            {
                bool dots = !HouseLights.Power && Current >= Step.Busqueda && Current <= Step.ArmarioFondo;
                for (int i = 0; i < wallDots.Length; i++)
                {
                    if (wallDots[i] == null) continue;
                    bool near = Vector3.Distance(player.transform.position, wallDots[i].transform.position) < 1.6f;
                    wallDots[i].SetActive(dots && !(i == 0 && near));
                }
            }

            if (DialogueManager.Instance.IsBusy) return;
            // Primer apagón: con Chevas en el salón, se apagan las luces y la tele la última.
            if (Current == Step.Explorar && !blackout1Done && InRoom(0f, 5f, 0f, 4.4f) && stepTime > 2f)
            {
                blackout1Done = true;
                StartCoroutine(BigBlackout());
            }
            // Segundo apagón: mientras busca a Roberta.
            if (Current == Step.Busqueda && !blackout2Done && stepTime > 4f)
            {
                blackout2Done = true;
                BreakerBox.Instance?.Trip();
                EnsureLight();
                DialogueManager.Instance.Play("Oscuridad_Apagon2");
            }
        }

        bool NearFrontWindow()
        {
            Vector3 p = player.transform.position;
            Vector3 f = player.cameraPivot != null ? player.cameraPivot.forward : player.transform.forward;
            bool salon = p.x > 0.5f && p.x < 4.8f && p.z < 1.8f;
            return salon && f.z < -0.6f;
        }

        IEnumerator WindowFlash()
        {
            chechuWindowLight.SetActive(true);
            yield return new WaitForSeconds(1.3f);
            chechuWindowLight.SetActive(false);
            DialogueManager.Instance.Play("Oscuridad_LuzEnfrente");
        }

        IEnumerator BigBlackout()
        {
            // Se van las luces de la casa y, un momento después, la tele.
            foreach (var s in FindObjectsByType<LightSwitch>(FindObjectsSortMode.None))
                foreach (var l in s.lights) if (l != null) l.enabled = false;
            yield return new WaitForSeconds(1.4f);
            BreakerBox.Instance?.Trip();
            EnsureLight();
            yield return new WaitForSeconds(0.8f);
            DialogueManager.Instance.Play("Oscuridad_Apagon1", () => GameDirector.Instance.SetObjective("Sube el diferencial del garaje"));
            yield return new WaitForSeconds(7f);
            Sfx.Play("puerta_lejos", new Vector3(11f, 1f, 8f));
        }

        /// <summary>Si aún no ha cogido la linterna, la lleva encima: nunca se queda totalmente a ciegas.</summary>
        void EnsureLight()
        {
            if (Flashlight.Owned) return;
            Flashlight.Give();
            DialogueManager.Instance.Play("Oscuridad_LinternaBolsillo");
        }

        void OnPowerBack()
        {
            if (Current != Step.Explorar && Current != Step.FotoCaida && Current != Step.FotoEnMano && Current != Step.EstanteriaCedida) return;
            if (blackout1Raised) return;
            blackout1Raised = true;
            // Enfrente se enciende la luz del porche, como si respondiera.
            chechuPorchLight.enabled = true;
            DialogueManager.Instance.Play("Oscuridad_Porche", () =>
            {
                if (Current == Step.Explorar) GameDirector.Instance.SetObjective("Da una vuelta por la casa");
            });
        }
    }
}
