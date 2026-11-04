using System.Collections;
using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;
using Yarn.Unity;

namespace Ominous
{
    /// <summary>Lleva la noche paso a paso: prólogo y acto 1. El guion está en Yarn; aquí se decide cuándo pasa cada cosa.</summary>
    public class StoryDirector : MonoBehaviour
    {
        public enum Step { Llegada, Tareas, HablarRoberta, Conversacion, ApagarLuces, Deambular, Llamada, EsperaPuerta, Visita, CerrarPuerta, MirarVentana, Fin }

        public static StoryDirector Instance { get; private set; }
        public Step Current { get; private set; }

        public Door frontDoor;
        public ActorFigure roberta;
        public ActorFigure chechu;
        public AudioSource robertaVoice;
        public AudioSource tvSound;
        public GameObject threshold;
        public GameObject outsideBounds;
        public YarnProject project;
        public Vector3 peepPosition = new(6f, 1.58f, -0.1f);

        FirstPersonController player;
        bool keysLeft, doorClosed;
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
            foreach (var s in FindObjectsByType<LightSwitch>(FindObjectsSortMode.None))
                s.onInteract.AddListener(OnLightChanged);
            BuildMonologue();

            var night = GameDirector.Instance.Night;
            if (GameDirector.Instance.Restored) ApplyRestored((Step)night.storyStep);
            else BeginNight();
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
            StartMonologue();
            DialogueManager.Instance.Play("Prologo_Coche");
        }

        void StartMonologue()
        {
            if (monologue.IsDialogueRunning) return;
            if (robertaVoice != null) robertaVoice.Play();
            _ = monologue.StartDialogue("Prologo_RobertaTele");
        }

        void StopMonologue()
        {
            if (robertaVoice != null) robertaVoice.Stop();
            if (monologue.IsDialogueRunning) _ = monologue.Stop();
            GameUI.Instance?.SetAmbientLine(null, 0f);
        }

        // ---------- qué se puede usar y cuándo ----------

        public bool CanUse(string id) => id switch
        {
            "roberta" => Current == Step.HablarRoberta || (Current >= Step.Deambular && !usedOnce.Contains("cama")),
            "cuenco" => !keysLeft && Current >= Step.Tareas && Current <= Step.ApagarLuces,
            "tele" => Current >= Step.Deambular && Current <= Step.Llamada && !usedOnce.Contains("tele"),
            "nevera" => Current >= Step.Deambular && Current <= Step.Llamada && !usedOnce.Contains("nevera"),
            "ventana" => (Current >= Step.Deambular && Current <= Step.Llamada && !usedOnce.Contains("ventana")) || Current == Step.MirarVentana,
            "vaso" => Current >= Step.Tareas && !usedOnce.Contains("vaso"),
            "grifo" => Current >= Step.Tareas && !usedOnce.Contains("grifo"),
            "mirilla" => Current == Step.EsperaPuerta && !peeping,
            _ => false,
        };

        public string PromptFor(string id, string fallback) => id switch
        {
            "roberta" => Current == Step.HablarRoberta ? "Hablar con Roberta" : "Mirar",
            _ => fallback,
        };

        public void OnUse(string id)
        {
            var dm = DialogueManager.Instance;
            switch (id)
            {
                case "cuenco":
                    keysLeft = true;
                    Sfx.Play("llaves", player.transform.position);
                    dm.Play("Prologo_Llaves");
                    CheckTasks();
                    break;
                case "vaso":
                    usedOnce.Add("vaso");
                    dm.Play("Prologo_Agua");
                    break;
                case "grifo":
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
                case "tele":
                    usedOnce.Add("tele");
                    Wander("Acto1_Tele");
                    break;
                case "nevera":
                    usedOnce.Add("nevera");
                    Wander("Acto1_Nevera");
                    break;
                case "ventana":
                    if (Current == Step.MirarVentana)
                    {
                        Set(Step.Fin);
                        dm.Play("Acto1_VentanaFinal", EndDemo);
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
            }
        }

        void Wander(string node)
        {
            wanderUses++;
            DialogueManager.Instance.Play(node);
        }

        void CheckTasks()
        {
            if (Current == Step.Tareas && keysLeft && doorClosed)
            {
                Set(Step.HablarRoberta);
                GameDirector.Instance.SetObjective("Habla con Roberta");
            }
        }

        void OnFrontDoor()
        {
            var dm = DialogueManager.Instance;
            if (Current == Step.Llegada && frontDoor.IsOpen)
            {
                Set(Step.Tareas);
                Sfx.Play("llaves", frontDoor.transform.position);
                dm.Play("Prologo_Tareas");
                return;
            }
            if (Current == Step.Tareas && !frontDoor.IsOpen)
            {
                doorClosed = true;
                frontDoor.locked = true;
                outsideBounds.SetActive(false);
                dm.Play("Prologo_Puerta");
                CheckTasks();
                return;
            }
            if (Current == Step.EsperaPuerta && frontDoor.IsOpen)
            {
                Set(Step.Visita);
                player.LookAt(chechu.head.position);
                dm.Play("Visita1", () => { Set(Step.CerrarPuerta); });
                return;
            }
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
            DialogueManager.Instance.Play("Acto1_Deambular");
        }

        void Update()
        {
            if (Current == Step.Deambular && !DialogueManager.Instance.IsBusy)
            {
                wanderTime += Time.deltaTime;
                if (wanderUses >= 2 && wanderTime > 25f || wanderTime > 180f) Knock();
            }
            if (Current == Step.EsperaPuerta && !DialogueManager.Instance.IsBusy && !peeping)
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
            yield return new WaitForSeconds(4.5f);
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
            Current = step;
            keysLeft = doorClosed = true;
            outsideBounds.SetActive(false);
            frontDoor.locked = step != Step.EsperaPuerta;
            PutRobertaInBed();
            foreach (var s in FindObjectsByType<LightSwitch>(FindObjectsSortMode.None))
                if (s.isOn) s.Interact();
            if (tvSound != null) tvSound.volume *= 0.45f;
            if (step == Step.EsperaPuerta) PlaceChechu();
            else chechu.Show(false);
            GameDirector.Instance.SetObjective(GameDirector.Instance.Night.objective);
        }
    }
}
