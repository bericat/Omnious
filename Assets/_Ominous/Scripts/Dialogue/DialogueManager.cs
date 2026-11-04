using System;
using UnityEngine;
using Yarn.Unity;

namespace Ominous
{
    /// <summary>Conecta Yarn con el juego: lanza nodos y atiende los comandos del guion.</summary>
    public class DialogueManager : MonoBehaviour
    {
        public static DialogueManager Instance { get; private set; }
        public YarnProject project;
        public DialogueRunner Runner { get; private set; }
        public SubtitlePresenter Presenter { get; private set; }
        readonly System.Collections.Generic.Queue<(string, Action)> queue = new();
        (string, Action)? current;
        bool wasRunning;
        int startedFrame;
        public bool IsRunning => Runner != null && Runner.IsDialogueRunning;

        // Comandos del guion que aún no hacen nada: los implementan las fases 5 a 8.
        static readonly string[] PendingNoArgs =
        {
            "reloj_parado",
            "animacion_llave_grifo", "estanteria_cede", "chechu_entrega_tornillo", "roberta_desaparece",
            "chechu_desaparece", "chechu_desaparece_riendo", "pasillo_alargado", "esperar_salto_jugador", "caida",
            "reiniciar_noche", "puerta_se_abre", "corte_negro", "creditos", "puerta_chechu_se_abre",
            "puerta_chechu_se_cierra",
        };

        static readonly string[] PendingOneArg =
        {
            "susto", "objeto_roto", "roberta_aparece", "chechu_aparece", "fundido_negro",
        };

        void Awake()
        {
            Instance = this;
            Presenter = gameObject.AddComponent<SubtitlePresenter>();
            Runner = gameObject.AddComponent<DialogueRunner>();
            Runner.autoStart = false;
            Runner.DialoguePresenters = new DialoguePresenterBase[] { Presenter };
            if (project != null) Runner.SetProject(project);
            RegisterCommands();
        }

        void OnDestroy()
        {
            if (Instance == this) Instance = null;
        }

        void RegisterCommands()
        {
            Action<string> log = c => Debug.Log($"[Guion] {c} todavía no hace nada");
            Runner.AddCommandHandler("hora", (string v) => GameDirector.Instance?.SetHour(v));
            Runner.AddCommandHandler("objetivo", (string v) => GameDirector.Instance?.SetObjective(v));
            Runner.AddCommandHandler("acto", (int v) => GameDirector.Instance?.SetAct(v));
            Runner.AddCommandHandler("visita", (int v) => GameDirector.Instance?.SetVisit(v));
            Runner.AddCommandHandler("casa_variante", (string v) => GameDirector.Instance?.SetHouseVariant(v));
            Runner.AddCommandHandler("habitacion_abierta", (int v) => GameDirector.Instance?.OpenRoom(v));
            Runner.AddCommandHandler("punto_control", (string v) => GameDirector.Instance?.Checkpoint(v));
            Runner.AddCommandHandler("hablante", (string v) => Presenter.NextSpeaker = v);
            Runner.AddCommandHandler("esperar", (float seconds) => YarnTask.Delay(TimeSpan.FromSeconds(seconds)));
            Runner.AddCommandHandler("audio_espacial", (string who, float meters) => log("audio_espacial"));
            foreach (string c in PendingNoArgs)
            {
                string name = c;
                Runner.AddCommandHandler(name, () => log(name));
            }
            foreach (string c in PendingOneArg)
            {
                string name = c;
                Runner.AddCommandHandler(name, (string arg) => log(name));
            }
        }

        /// <summary>Lanza un nodo. Si ya hay un diálogo en marcha, espera su turno.</summary>
        public void Play(string node, Action done = null)
        {
            if (Runner == null || string.IsNullOrEmpty(node)) return;
            queue.Enqueue((node, done));
        }

        /// <summary>Hay diálogo en marcha o en cola.</summary>
        public bool IsBusy => IsRunning || queue.Count > 0 || current != null;

        void Update()
        {
            if (Runner == null) return;
            if (IsRunning) { wasRunning = true; return; }
            if (wasRunning || current != null && startedFrame < Time.frameCount - 2)
            {
                wasRunning = false;
                var finished = current;
                current = null;
                if (finished.HasValue) finished.Value.Item2?.Invoke();
                if (queue.Count == 0) return;
            }
            if (current == null && queue.Count > 0)
            {
                current = queue.Dequeue();
                startedFrame = Time.frameCount;
                _ = Runner.StartDialogue(current.Value.Item1);
            }
        }
    }
}
