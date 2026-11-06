using System.Collections;
using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;
using Yarn.Unity;

namespace Ominous
{
    /// <summary>Lleva la noche paso a paso: prólogo y acto 1. El guion está en Yarn; aquí se decide cuándo pasa cada cosa.</summary>
    public partial class StoryDirector : MonoBehaviour
    {
        public enum Step { Llegada, Tareas, HablarRoberta, Conversacion, ApagarLuces, Deambular, Llamada, EsperaPuerta, Visita, CerrarPuerta, MirarVentana,
            GrifoArreglar, GrifoRoto, EsperaV2, VisitaV2, CerrarV2, Explorar, FotoCaida, FotoEnMano, EstanteriaCedida, Cuartito, EsperaV3, VisitaV3, CerrarV3, IrDormitorio, Busqueda, ArmarioGolpe, ArmarioFondo, Hueco, SalirCasa, VisitaV4, Volver, RobertaCocina, Acto3, SotanoPuerta, Sotano, SotanoSalir, FinalPasillo, FinalPuerta, Caida, BucleLlegada, BucleLlamar, BucleFinal, Fin }

        public static StoryDirector Instance { get; private set; }
        public Step Current { get; private set; }

        public Door frontDoor;
        public ActorFigure roberta;
        public ActorFigure chechu;
                public AudioSource tvSound;
        public GameObject threshold;
        public GameObject outsideBounds;
        public YarnProject project;
        public Vector3 peepPosition = new(6f, 1.58f, -0.1f);

        FirstPersonController player;
        bool keysLeft, doorClosed;
        [Tooltip("Las llaves dentro del cuenco: aparecen al dejarlas")] public GameObject keysInBowl;
        int wanderUses;
        float wanderTime, knockTimer;
        readonly System.Collections.Generic.HashSet<string> usedOnce = new();
        DialogueRunner monologue;
        bool peeping;

        static readonly Vector3 RobertaSofa = new(2.5f, 0f, 1.5f);
        static readonly Vector3 RobertaBed = new(1.15f, 0.52f, 8.05f);
        static readonly Vector3 ChechuPorch = new(6f, 0f, -0.82f);

        void Awake() => Instance = this;

        void OnDestroy()
        {
            if (Instance == this) Instance = null;
        }

        void Start()
        {
            player = FindAnyObjectByType<FirstPersonController>();
            RegisterCommands();
            frontDoor.onInteract.AddListener(OnFrontDoor);
            voidDoor.onInteract.AddListener(OnVoidDoor);
            foreach (var s in FindObjectsByType<LightSwitch>(FindObjectsSortMode.None))
                s.onInteract.AddListener(OnLightChanged);
            BuildMonologue();

            var night = GameDirector.Instance.Night;
            if (GameDirector.Instance.Restored) ApplyRestored((Step)night.storyStep);
            else BeginNight();

            // Para probar sin rejugar todo: ./Ominous -saltar acto2
            var args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, "-saltar");
            if (i >= 0 && i + 1 < args.Length && args[i + 1] == "acto2" && !GameDirector.Instance.Restored)
            {
                JumpForTest(Step.GrifoArreglar);
                player.Teleport(new Vector3(6f, 0.02f, 1.6f), 0f);
                DialogueManager.Instance.Play("Acto2_Inicio");
            }
            if (i >= 0 && i + 1 < args.Length && args[i + 1] == "final" && !GameDirector.Instance.Restored)
            {
                StartFinalForTest();
                player.Teleport(new Vector3(12f, 0.02f, 5.2f), 270f);
            }
            if (i >= 0 && i + 1 < args.Length && args[i + 1] == "acto3" && !GameDirector.Instance.Restored)
            {
                StartAct3ForTest();
                player.Teleport(new Vector3(10.4f, 0.02f, 3.2f), 180f);
            }
        }

        void Set(Step step)
        {
            Current = step;
            GameDirector.Instance.Night.storyStep = (int)step;
        }

        void BuildMonologue()
        {
            var go = new GameObject("MonologoRoberta");
            go.transform.SetParent(transform);
            var presenter = go.AddComponent<MonologuePresenter>();
            presenter.speaker = roberta.transform;
            presenter.listener = player.transform;
            monologue = go.AddComponent<DialogueRunner>();
            monologue.autoStart = false;
            monologue.DialoguePresenters = new DialoguePresenterBase[] { presenter };
            monologue.SetProject(project);
            monologue.AddCommandHandler("esperar", (float s) => YarnTask.Delay(System.TimeSpan.FromSeconds(s)));
            monologue.AddCommandHandler("audio_espacial", (string who, float meters) => { presenter.hearingRange = meters; });
        }

        void RegisterCommands()
        {
            var r = DialogueManager.Instance.Runner;
            r.AddCommandHandler("roberta_se_adormece", () => roberta.Slump(10f));
            r.AddCommandHandler("roberta_va_al_dormitorio", () => WalkRobertaToBed());
            r.AddCommandHandler("chechu_se_gira", () => chechu.transform.rotation = Quaternion.Euler(0f, 215f, 0f));
            r.AddCommandHandler("chechu_se_va", () => WalkChechuAway());
            r.AddCommandHandler("mirar", (string who) => LookAtActor(who));
            r.AddCommandHandler("sonido", (string name) => Sfx.Play(name, SoundPosition(name)));
            RegisterAct2Commands(r);
            RegisterAct3Commands(r);
            RegisterFinalCommands(r);
        }

        Vector3 SoundPosition(string name) => name.StartsWith("llamada") ? frontDoor.transform.position + Vector3.up * 1.2f : player.transform.position;

        void LookAtActor(string who)
        {
            var actor = who == "Chechu" ? chechu : roberta;
            if (actor != null && actor.head != null) player.LookAt(actor.head.position);
        }

        // ---------- principio ----------

        void BeginNight()
        {
            Set(Step.Llegada);
            roberta.Place(RobertaSofa, 0f);
            roberta.SetPose("sentada");
            chechu.Show(false);
            threshold.SetActive(false);
            frontDoor.locked = false;
            BeginAct2State();
            BeginAct3State();
            StartMonologue();
            DialogueManager.Instance.Play("Prologo_Coche");
        }

        void StartMonologue()
        {
            if (monologue.IsDialogueRunning) return;
                        _ = monologue.StartDialogue("Prologo_RobertaTele");
        }

        void StopMonologue()
        {
                        if (monologue.IsDialogueRunning) _ = monologue.Stop();
            GameUI.Instance?.SetAmbientLine(null, 0f);
        }

        // ---------- qué se puede usar y cuándo ----------

        public bool CanUse(string id) => id switch
        {
            "roberta" => Current == Step.HablarRoberta || (Current >= Step.Deambular && Current <= Step.Llamada && !usedOnce.Contains("cama")),
            "cuenco" => !keysLeft && Current >= Step.Tareas && Current < Step.Llamada,
            "tele" => Current >= Step.Deambular && Current <= Step.Llamada && !usedOnce.Contains("tele"),
            "nevera" => Current >= Step.Deambular && Current <= Step.Llamada && !usedOnce.Contains("nevera"),
            "ventana" => (Current >= Step.Deambular && Current <= Step.Llamada && !usedOnce.Contains("ventana")) || Current == Step.MirarVentana || ((Current == Step.Acto3 || Current == Step.SotanoPuerta) && !(streetSeen && robertaWindow)),
            "vaso" => Current >= Step.Tareas && Current <= Step.MirarVentana && !usedOnce.Contains("vaso"),
            "grifo" => (Current >= Step.Tareas && Current <= Step.MirarVentana && !usedOnce.Contains("grifo")) || Current == Step.GrifoArreglar,
            "cama" => Current == Step.Deambular && !usedOnce.Contains("acostarse"),
            "mirilla" => (Current == Step.EsperaPuerta || Current == Step.EsperaV2 || Current == Step.EsperaV3) && !peeping,
            _ => CanUseAct2(id),
        };

        public string PromptFor(string id, string fallback) => id switch
        {
            "roberta" => Current == Step.HablarRoberta ? "Hablar con Roberta" : "Mirar",
            "grifo" => Current == Step.GrifoArreglar ? (hasWrench ? "Arreglar el grifo" : "Arreglar el grifo") : fallback,
            _ => fallback,
        };

        public void OnUse(string id)
        {
            var dm = DialogueManager.Instance;
            switch (id)
            {
                case "cuenco":
                    keysLeft = true;
                    if (keysInBowl != null) keysInBowl.SetActive(true);
                    Sfx.Play("llaves", player.transform.position);
                    dm.Play("Prologo_Llaves");
                    RefreshPending();
                    break;
                case "vaso":
                    usedOnce.Add("vaso");
                    dm.Play("Prologo_Agua");
                    break;
                case "grifo":
                    if (Current == Step.GrifoArreglar) { UseFaucet(); break; }
                    usedOnce.Add("grifo");
                    dm.Play("Prologo_Grifo_Examinar");
                    break;
                case "roberta":
                    if (Current == Step.HablarRoberta) StartConversation();
                    else
                    {
                        usedOnce.Add("cama");
                        Wander("Acto1_Dormitorio");
                    }
                    break;
                case "cama":
                    // Antes de acostarse hay que dejar las llaves y cerrar la puerta.
                    if (!keysLeft || !doorClosed) { dm.Play("Acto1_CamaPendiente"); break; }
                    usedOnce.Add("acostarse");
                    StartCoroutine(TryToSleep());
                    break;
                case "tele":
                    usedOnce.Add("tele");
                    Wander("Acto1_Tele");
                    break;
                case "nevera":
                    usedOnce.Add("nevera");
                    Wander("Acto1_Nevera");
                    break;
                case "ventana":
                    if (OnWindowAct3()) break;
                    if (Current == Step.MirarVentana)
                    {
                        Set(Step.GrifoArreglar);
                        dm.Play("Acto1_VentanaFinal");
                        dm.Play("Acto2_Inicio");
                    }
                    else
                    {
                        usedOnce.Add("ventana");
                        Wander("Acto1_Ventana");
                    }
                    break;
                case "mirilla":
                    StartCoroutine(Peep());
                    break;
                default:
                    OnUseAct2(id);
                    break;
            }
        }

        IEnumerator TryToSleep()
        {
            FirstPersonController.SetBlocked(this, true);
            yield return GameUI.Instance.Fade(1f, 1.2f);
            yield return new WaitForSecondsRealtime(2.5f);
            yield return GameUI.Instance.Fade(0f, 1.2f);
            FirstPersonController.SetBlocked(this, false);
            DialogueManager.Instance.Play("Acto1_Cama");
            // Justo cuando deja de intentarlo, llaman a la puerta.
            wanderUses = 2;
            wanderTime = 20f;
        }

        void Wander(string node)
        {
            wanderUses++;
            DialogueManager.Instance.Play(node);
        }

        /// <summary>Las llaves y la puerta quedan pendientes, sin bloquear nada, hasta antes de la primera visita.</summary>
        void RefreshPending()
        {
            bool early = Current >= Step.Tareas && Current < Step.Llamada;
            var tasks = new System.Collections.Generic.List<string>();
            if (early && !keysLeft) tasks.Add("Deja las llaves en el cuenco");
            if (early && !doorClosed) tasks.Add("Cierra la puerta de casa");
            GameUI.Instance?.SetPending(tasks.Count > 0 ? "Pendiente: " + string.Join(" · ", tasks) : null);
        }

        void OnFrontDoor()
        {
            var dm = DialogueManager.Instance;
            if (Current == Step.Llegada && frontDoor.IsOpen)
            {
                // Al entrar ya se puede hacer de todo; llaves y puerta quedan como pendientes.
                Set(Step.HablarRoberta);
                Sfx.Play("llaves", frontDoor.transform.position);
                GameDirector.Instance.SetObjective("Habla con Roberta");
                RefreshPending();
                return;
            }
            // Cerrarla desde fuera no cuenta: se quedaría encerrado en la calle.
            if (!doorClosed && Current >= Step.Tareas && Current < Step.Llamada && !frontDoor.IsOpen && player.transform.position.z > 0.1f)
            {
                doorClosed = true;
                frontDoor.locked = true;
                outsideBounds.SetActive(false);
                dm.Play("Prologo_Puerta");
                RefreshPending();
                return;
            }
            if (Current == Step.EsperaPuerta && frontDoor.IsOpen)
            {
                Set(Step.Visita);
                player.LookAt(chechu.head.position);
                dm.Play("Visita1", () => { Set(Step.CerrarPuerta); });
                return;
            }
            if (OnFrontDoorAct2()) return;
            if (Current == Step.CerrarPuerta && !frontDoor.IsOpen)
            {
                frontDoor.locked = true;
                Set(Step.MirarVentana);
                dm.Play("Acto1_Despues");
            }
        }

        void StartConversation()
        {
            Set(Step.Conversacion);
            StopMonologue();
            LookAtActor("Roberta");
            DialogueManager.Instance.Play("Prologo_Sofa", () =>
            {
                Set(Step.ApagarLuces);
                OnLightChanged();
            });
        }

        void WalkRobertaToBed()
        {
            if (Current >= Step.Volver)
            {
                roberta.Walk(new[]
                {
                    new Vector3(10.45f, 0f, 3.8f), new Vector3(10.45f, 0f, 5.2f), new Vector3(2.95f, 0f, 5.2f), new Vector3(2.95f, 0f, 6.9f), new Vector3(2.35f, 0f, 7.4f),
                }, PutRobertaInBed);
                return;
            }
            if (tvSound != null) tvSound.volume *= 0.45f;
            roberta.Slump(0f);
            roberta.Walk(new[]
            {
                new Vector3(4.2f, 0f, 2.55f), new Vector3(5.7f, 0f, 2.55f), new Vector3(6.05f, 0f, 3.8f), new Vector3(6.05f, 0f, 5.2f),
                new Vector3(2.95f, 0f, 5.2f), new Vector3(2.95f, 0f, 6.9f), new Vector3(2.35f, 0f, 7.4f),
            }, PutRobertaInBed);
        }

        void PutRobertaInBed()
        {
            roberta.Place(RobertaBed, 270f);
            roberta.SetPose("tumbada");
            GameDirector.Instance.Night.robertaInBed = true;
        }

        void OnLightChanged()
        {
            if (Current != Step.ApagarLuces) return;
            bool anyOn = FindObjectsByType<LightSwitch>(FindObjectsSortMode.None).Any(s => s.isOn);
            if (anyOn) return;
            Set(Step.Deambular);
            DialogueManager.Instance.Play("Prologo_Fin");
            DialogueManager.Instance.Play("Acto1_Deambular", () => GameDirector.Instance.SetObjective("No tienes sueño: da una vuelta por la casa o intenta acostarte"));
        }

        void Update()
        {
            if (Current == Step.Deambular && !DialogueManager.Instance.IsBusy)
            {
                wanderTime += Time.deltaTime;
                // Chechu no llama hasta que las llaves estén en el cuenco y la puerta cerrada.
                if ((wanderUses >= 2 && wanderTime > 25f || wanderTime > 90f) && keysLeft && doorClosed) Knock();
            }
            UpdateAct2();
            UpdateAct3();
            UpdateFinal();
            if ((Current == Step.EsperaPuerta || Current == Step.EsperaV2 || Current == Step.EsperaV3) && !DialogueManager.Instance.IsBusy && !peeping)
            {
                knockTimer += Time.deltaTime;
                if (knockTimer > 28f)
                {
                    knockTimer = 0f;
                    Sfx.Play("llamada_puerta", frontDoor.transform.position + Vector3.up * 1.2f);
                }
            }
        }

        void Knock()
        {
            Set(Step.Llamada);
            RefreshPending();
            DialogueManager.Instance.Play("Acto1_Llamada", ReadyForVisit);
            PlaceChechu();
        }

        void ReadyForVisit()
        {
            Set(Step.EsperaPuerta);
            frontDoor.locked = false;
            GameDirector.Instance.Checkpoint("visita1");
        }

        void PlaceChechu()
        {
            chechu.Show(true);
            chechu.SetPose("depie");
            chechu.Place(ChechuPorch, 0f);
            threshold.SetActive(true);
        }

        void WalkChechuAway()
        {
            chechu.Walk(new[]
            {
                new Vector3(6f, 0f, -2.3f), new Vector3(7f, 0f, -3f), new Vector3(7f, 0f, -6f), new Vector3(7f, 0f, -8.9f),
            }, () => chechu.Show(false));
        }

        IEnumerator Peep()
        {
            peeping = true;
            FirstPersonController.SetBlocked(this, true);
            player.SetPeep(peepPosition, 180f, 98f);
            DialogueManager.Instance.Play("Acto1_Mirilla");
            yield return new WaitForSeconds(1f);
            while (DialogueManager.Instance.IsBusy) yield return null;
            yield return new WaitForSeconds(0.8f);
            player.EndPeep();
            FirstPersonController.SetBlocked(this, false);
            peeping = false;
        }

        void EndDemo()
        {
            GameDirector.Instance.Checkpoint("fin_acto1");
            StartCoroutine(EndRoutine());
        }

        IEnumerator EndRoutine()
        {
            FirstPersonController.SetBlocked(this, true);
            yield return GameUI.Instance.Fade(1f, 3f);
            yield return new WaitForSecondsRealtime(1.5f);
            SaveSystem.Delete();
            SceneManager.LoadScene(MainMenu.SceneName);
        }

        void ApplyRestored(Step step)
        {
            if (GameDirector.Instance.Night.powerOff) HouseLights.SetPower(false);
            Current = step;
            keysLeft = doorClosed = true;
            if (keysInBowl != null) keysInBowl.SetActive(true);
            outsideBounds.SetActive(false);
            frontDoor.locked = !(step == Step.EsperaPuerta || step == Step.EsperaV2 || step == Step.EsperaV3 || step == Step.SalirCasa);
            PutRobertaInBed();
            foreach (var s in FindObjectsByType<LightSwitch>(FindObjectsSortMode.None))
                if (s.isOn) s.Interact();
            if (tvSound != null) tvSound.volume *= 0.45f;
            if (step == Step.EsperaPuerta || step == Step.EsperaV2 || step == Step.EsperaV3) PlaceChechu();
            else chechu.Show(false);
            RestoreAct2(step);
            RestoreAct3(step);
            if (step >= Step.FinalPasillo) { hallDoor.locked = false; voidDoor.locked = false; }
            GameDirector.Instance.SetObjective(GameDirector.Instance.Night.objective);
        }
    }
}
