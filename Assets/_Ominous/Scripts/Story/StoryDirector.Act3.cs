using System.Collections;
using UnityEngine;
using Yarn.Unity;

namespace Ominous
{
    /// <summary>Acto 3: la casa deja de tener sentido. Sin cortes de carga: geometría ya presente y saltos de un parpadeo.</summary>
    public partial class StoryDirector
    {
        [Header("Acto 3")]
        public GameObject clockNormal;
        public GameObject clockStopped;
        public GameObject extraDoor;
        public GameObject longHall;
        public Door hallDoor;
        public GameObject streetLampMissing;
        public Light streetLampLight;
        public GameObject basementDoor;
        public GameObject basementRoot;
        public Light bathLight;
        public AudioSource dripSound;
        public Transform basementArrival;
        public Vector3 carSeat = new(16.2f, -0.28f, 2f);

        bool repeatedRoom, hallSeen, robertaLaundry, robertaCar, robertaWindow, chechuSeen, basementSeen, notebookRead;
        bool streetSeen, wasInKitchen;

        void BeginAct3State()
        {
            clockStopped.SetActive(false);
            extraDoor.SetActive(false);
            longHall.SetActive(false);
            basementDoor.SetActive(false);
        }

        void RegisterAct3Commands(DialogueRunner r)
        {
            r.AddCommandHandler("reloj_parado", () =>
            {
                clockNormal.SetActive(false);
                clockStopped.SetActive(true);
            });
            r.AddCommandHandler("chechu_aparece", (string where) =>
            {
                chechu.Show(true);
                chechu.SetPose("depie");
                chechu.Place(new Vector3(8.45f, 0f, 7.75f), 180f);
                player.LookAt(chechu.head.position);
            });
            r.AddCommandHandler("chechu_desaparece_riendo", () => StartCoroutine(ChechuLeaves()));
        }

        IEnumerator ChechuLeaves()
        {
            Sfx.Play("risa", chechu.head.position);
            bool lit = bathLight != null && bathLight.enabled;
            yield return new WaitForSeconds(1.3f);
            for (int i = 0; i < 4; i++)
            {
                if (bathLight != null) bathLight.enabled = i % 2 == 1 && lit;
                yield return new WaitForSeconds(0.09f);
            }
            chechu.Show(false);
            if (bathLight != null) bathLight.enabled = lit;
        }

        void StartAct3()
        {
            Set(Step.Acto3);
            GameDirector.Instance.Night.houseVariant = "acto3";
            extraDoor.SetActive(true);
            chechuSilhouette.SetActive(false);
            streetLampMissing.SetActive(false);
            if (streetLampLight != null) streetLampLight.enabled = false;
            wasInKitchen = true;
            DialogueManager.Instance.Play("Acto3_Inicio", () =>
            {
                GameDirector.Instance.SetObjective("Busca a Roberta");
                GameDirector.Instance.Checkpoint("acto3");
            });
        }

        bool CanUseAct3(string id) => id switch
        {
            "puerta_de_mas" => Current == Step.Acto3,
            "puerta_sotano" => Current == Step.SotanoPuerta,
            "fotos" => Current == Step.Sotano && !usedOnce.Contains("fotos"),
            "libreta" => Current == Step.Sotano && !notebookRead,
            "salir_sotano" => Current == Step.SotanoSalir,
            _ => false,
        };

        bool OnUseAct3(string id)
        {
            var dm = DialogueManager.Instance;
            switch (id)
            {
                case "puerta_de_mas":
                    // Una puerta que no debería estar y lleva a otro sitio.
                    Sfx.Play("puerta_abre", extraDoor.transform.position);
                    StartCoroutine(Blink(() =>
                    {
                        player.Teleport(new Vector3(13.3f, 0.02f, 3.3f), 250f);
                        Sfx.Play("puerta_cierra", player.transform.position);
                    }));
                    return true;
                case "puerta_sotano":
                    Set(Step.Sotano);
                    dm.Play("Sotano_Puerta", () => StartCoroutine(Blink(() =>
                    {
                        basementRoot.SetActive(true);
                        GameDirector.Instance.SetObjective("");
                        player.Teleport(basementArrival.position, basementArrival.eulerAngles.y);
                        dm.Play("Habitacion3");
                        GameDirector.Instance.OpenRoom(3);
                    })));
                    return true;
                case "fotos":
                    usedOnce.Add("fotos");
                    dm.Play("Habitacion3_Fotos");
                    return true;
                case "libreta":
                    notebookRead = true;
                    Set(Step.SotanoSalir);
                    dm.Play("Habitacion3_Libreta");
                    dm.Play("Habitacion3_Salida");
                    return true;
                case "salir_sotano":
                    StartCoroutine(Blink(() =>
                    {
                        player.Teleport(new Vector3(13.2f, 0.02f, 6.7f), 270f);
                        basementRoot.SetActive(false);
                        hallDoor.locked = false;
                        Set(Step.Fin);
                        EndDemo();
                    }));
                    return true;
            }
            return false;
        }

        IEnumerator Blink(System.Action middle)
        {
            FirstPersonController.SetBlocked(this, true);
            yield return GameUI.Instance.Fade(1f, 0.1f);
            middle();
            yield return new WaitForSecondsRealtime(0.14f);
            yield return GameUI.Instance.Fade(0f, 0.16f);
            FirstPersonController.SetBlocked(this, false);
        }

        void UpdateAct3()
        {
            var dm = DialogueManager.Instance;
            bool corridor = InRoom(-20f, 14f, 4.4f, 6f);
            // El pasillo largo solo existe mientras se está en el pasillo: no se puede ver desde fuera.
            if (Current >= Step.SotanoPuerta) longHall.SetActive(corridor);
            if (Current == Step.Acto3 || Current == Step.SotanoPuerta)
            {
                if (dm.IsBusy) return;
                bool kitchen = InRoom(8.2f, 14f, 0f, 4.4f);
                if (!repeatedRoom && wasInKitchen && !kitchen && corridor)
                {
                    // Sale de la cocina y vuelve a entrar en ella.
                    repeatedRoom = true;
                    StartCoroutine(Blink(() =>
                    {
                        player.Teleport(new Vector3(10.45f, 0.02f, 3.7f), 180f);
                        dm.Play("Acto3_HabitacionRepetida");
                    }));
                    return;
                }
                wasInKitchen = kitchen || wasInKitchen && !corridor;
                if (repeatedRoom && !hallSeen && corridor)
                {
                    hallSeen = true;
                    dm.Play("Acto3_Pasillo");
                    return;
                }
                if (!robertaLaundry && InRoom(10f, 14f, 6f, 10f))
                {
                    robertaLaundry = true;
                    ShowRoberta("colada");
                    player.LookAt(roberta.head.position);
                    dm.Play("Roberta_Imposible_Colada");
                    return;
                }
                if (!robertaCar && InRoom(14f, 19f, 0f, 4.4f))
                {
                    robertaCar = true;
                    ShowRoberta("garaje_coche");
                    dm.Play("Roberta_Imposible_Coche");
                    return;
                }
                if (!chechuSeen && Current == Step.Acto3 && InRoom(6.8f, 10f, 6f, 10f) && (robertaLaundry ? 1 : 0) + (robertaCar ? 1 : 0) + (robertaWindow ? 1 : 0) >= 2)
                {
                    chechuSeen = true;
                    if (dripSound != null) dripSound.Stop();
                    dm.Play("Chechu_Dentro", () =>
                    {
                        Set(Step.SotanoPuerta);
                        basementDoor.SetActive(true);
                        hallDoor.locked = false;
                        GameDirector.Instance.SetObjective("Vuelve a la colada");
                    });
                }
            }
        }

        bool OnWindowAct3()
        {
            if (Current != Step.Acto3 && Current != Step.SotanoPuerta) return false;
            var dm = DialogueManager.Instance;
            if (!streetSeen)
            {
                streetSeen = true;
                dm.Play("Acto3_VentanaCalle");
            }
            else if (!robertaWindow)
            {
                robertaWindow = true;
                ShowRoberta("ventana_enfrente");
                dm.Play("Roberta_Imposible_Ventana");
            }
            return true;
        }

        /// <summary>Para pruebas: empieza el acto 3.</summary>
        public void StartAct3ForTest()
        {
            JumpForTest(Step.RobertaCocina);
            HideRoberta();
            streetBounds.SetActive(false);
            StartAct3();
        }

        void RestoreAct3(Step step)
        {
            BeginAct3State();
            if (step < Step.Acto3) return;
            HideRoberta();
            streetBounds.SetActive(false);
            chechuPorchLight.enabled = false;
            chechuSilhouette.SetActive(false);
            clockNormal.SetActive(false);
            clockStopped.SetActive(true);
            extraDoor.SetActive(true);
            streetLampMissing.SetActive(false);
            if (streetLampLight != null) streetLampLight.enabled = false;
            frontDoor.locked = true;
        }
    }
}
