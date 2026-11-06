using System.Collections;
using UnityEngine;
using Yarn.Unity;

namespace Ominous
{
    /// <summary>Desenlace: la puerta al vacío y el bucle en el que Chechu abre con la frase de Chevas.</summary>
    public partial class StoryDirector
    {
        [Header("Desenlace")]
        public Door voidDoor;
        public GameObject streetRoot;
        public LightSwitch hallSwitch;
        public LightSwitch lampSwitch;

        const float VoidEdgeX = -16.15f;
        bool routineDone, finalHallStarted;

        void RegisterFinalCommands(DialogueRunner r)
        {
            VideoLookController.BlackVoid = false;
            r.AddCommandHandler("pasillo_alargado", () => { });
            r.AddCommandHandler("esperar_salto_jugador", () => YarnTask.WaitUntil(() => player.transform.position.x < VoidEdgeX));
            r.AddCommandHandler("caida", () =>
            {
                Set(Step.Caida);
                FirstPersonController.SetBlocked(this, true);
                return YarnTask.Delay(System.TimeSpan.FromSeconds(2.5));
            });
            r.AddCommandHandler("fundido_negro", (float seconds) => RunRoutine(GameUI.Instance.Fade(1f, seconds)));
            r.AddCommandHandler("reiniciar_noche", () => RestartNight());
            r.AddCommandHandler("puerta_se_abre", () =>
            {
                frontDoor.locked = false;
                frontDoor.Interact();
                chechu.Show(true);
                chechu.SetPose("depie");
                chechu.Place(new Vector3(6f, 0f, 0.8f), 180f);
                // La luz del porche le da en la cara: hay que reconocerlo.
                var porch = new GameObject("LuzPorche").AddComponent<Light>();
                porch.type = LightType.Point;
                porch.range = 4f;
                porch.intensity = 1.6f;
                porch.color = new Color(1f, 0.86f, 0.66f);
                porch.transform.position = new Vector3(6f, 2.1f, -0.5f);
                player.LookAt(chechu.head.position);
            });
            r.AddCommandHandler("corte_negro", () => GameUI.Instance.SetBlack());
            r.AddCommandHandler("creditos", () => RunRoutine(GameUI.Instance.Credits()));
        }

        YarnTask RunRoutine(IEnumerator routine)
        {
            routineDone = false;
            StartCoroutine(Track(routine));
            return YarnTask.WaitUntil(() => routineDone);
        }

        IEnumerator Track(IEnumerator routine)
        {
            yield return routine;
            routineDone = true;
        }

        bool CanUseFinal(string id) => id switch
        {
            "llamar" => Current == Step.BucleLlamar,
            _ => CanUseDark(id),
        };

        bool OnUseFinal(string id)
        {
            if (id != "llamar") return OnUseDark(id);
            Set(Step.BucleFinal);
            FirstPersonController.SetBlocked(this, true);
            GameDirector.Instance.SetObjective("");
            DialogueManager.Instance.Play("Bucle_Puerta", EndGame);
            return true;
        }

        void StartFinalHall()
        {
            Set(Step.FinalPasillo);
            hallDoor.locked = false;
            voidDoor.locked = false;
            GameDirector.Instance.SetObjective("Vuelve al pasillo");
            GameDirector.Instance.Checkpoint("final");
        }

        void UpdateFinal()
        {
            if (Current == Step.FinalPasillo && !finalHallStarted && InRoom(-20f, 14f, 4.4f, 6f) && !DialogueManager.Instance.IsBusy)
            {
                finalHallStarted = true;
                DialogueManager.Instance.Play("Final_Pasillo");
            }
        }

        void OnVoidDoor()
        {
            if (Current != Step.FinalPasillo || !voidDoor.IsOpen) return;
            Set(Step.FinalPuerta);
            // Al otro lado no hay nada: ni calle, ni suelo.
            streetRoot.SetActive(false);
            VideoLookController.BlackVoid = true;
            GameDirector.Instance.SetObjective("");
            DialogueManager.Instance.Play("Final_Puerta");
        }

        void RestartNight()
        {
            Set(Step.BucleLlegada);
            FirstPersonController.SetBlocked(this, false);
            streetRoot.SetActive(true);
            VideoLookController.BlackVoid = false;
            longHall.SetActive(false);
            BeginAct2State();
            BeginAct3State();
            basementRoot.SetActive(false);
            clockNormal.SetActive(true);
            streetLampMissing.SetActive(true);
            if (streetLampLight != null) streetLampLight.enabled = true;
            tv.TurnOn();
            if (tvFill != null) tvFill.enabled = true;
            tvOff = false;
            chechu.Show(false);
            roberta.Show(true);
            roberta.Place(RobertaSofa, 0f);
            roberta.SetPose("sentada");
            foreach (var s in FindObjectsByType<LightSwitch>(FindObjectsSortMode.None))
                if (s.isOn != (s == hallSwitch || s == lampSwitch)) s.Interact();
            threshold.SetActive(false);
            outsideBounds.SetActive(true);
            if (voidDoor.IsOpen) voidDoor.Interact();
            if (frontDoor.IsOpen)
            {
                frontDoor.locked = false;
                frontDoor.Interact();
            }
            frontDoor.locked = true;
            frontDoor.onLockedTry = KeysFail;
            player.Teleport(new Vector3(6f, 0.02f, -2.2f), 0f);
            StartCoroutine(GameUI.Instance.Fade(0f, 2.5f));
        }

        void KeysFail()
        {
            if (Current != Step.BucleLlegada) return;
            frontDoor.onLockedTry = null;
            DialogueManager.Instance.Play("Bucle_Llaves", () => Set(Step.BucleLlamar));
        }

        void EndGame()
        {
            Set(Step.Fin);
            SaveSystem.Delete();
            FirstPersonController.SetBlocked(this, false);
            UnityEngine.SceneManagement.SceneManager.LoadScene(MainMenu.SceneName);
        }

        /// <summary>Para pruebas: empieza en el pasillo final.</summary>
        public void StartFinalForTest()
        {
            StartAct3ForTest();
            StartFinalHall();
        }
    }
}
