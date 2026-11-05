#if UNITY_EDITOR
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

namespace Ominous
{
    /// <summary>
    /// Jugador automático para buscar bloqueos: solo existe en el Editor. Usa lo mismo que el jugador
    /// (apuntar y pulsar sobre lo que dice PlayerInteractor) y solo va a sitios a los que se llega andando.
    /// </summary>
    public class AutoPlayer : MonoBehaviour
    {
        const float Cell = 0.25f;
        /// <summary>Elige siempre la última opción de los diálogos en lugar de la primera.</summary>
        public static bool PickLast;
        static readonly Vector2Int[] Neighbours = { new(1, 0), new(-1, 0), new(0, 1), new(0, -1) };

        StoryDirector story;
        FirstPersonController player;
        PlayerInteractor interactor;
        string logPath;
        readonly Dictionary<Vector2Int, float> cells = new();
        readonly Dictionary<Interactable, int> tries = new();
        readonly Collider[] overlap = new Collider[32];
        readonly RaycastHit[] rayHits = new RaycastHit[16];
        readonly HashSet<string> reported = new();

        void Log(string text)
        {
            string line = $"{Time.realtimeSinceStartup,7:F1} [{story.Current}] {text}";
            File.AppendAllText(logPath, line + "\n");
        }

        void Start()
        {
            story = StoryDirector.Instance;
            player = FindFirstObjectByType<FirstPersonController>();
            interactor = FindFirstObjectByType<PlayerInteractor>();
            logPath = Path.Combine(Application.dataPath, "../Temp/bot.log");
            File.WriteAllText(logPath, "");
            Application.logMessageReceived += OnLog;
            Time.timeScale = 3f;
            StartCoroutine(Run());
        }

        void OnDestroy()
        {
            Application.logMessageReceived -= OnLog;
            Time.timeScale = 1f;
            File.AppendAllText(logPath, "--- fin del jugador automático\n");
        }

        void OnLog(string message, string trace, LogType type)
        {
            if (type == LogType.Error || type == LogType.Exception) File.AppendAllText(logPath, $"ERROR {message}\n{trace}\n");
        }

        void Update()
        {
            foreach (var p in FindObjectsByType<SubtitlePresenter>(FindObjectsSortMode.None))
            {
                p.AdvanceRequested = true;
                if (p.OptionCount > 0 && p.RequestedOption < 0) p.RequestedOption = PickLast ? p.OptionCount - 1 : 0;
            }
        }

        bool Free(Vector3 floor)
        {
            int n = Physics.OverlapCapsuleNonAlloc(floor + Vector3.up * 0.65f, floor + Vector3.up * 1.45f, 0.24f, overlap, ~0, QueryTriggerInteraction.Ignore);
            for (int i = 0; i < n; i++)
            {
                var c = overlap[i];
                if (c is CharacterController) continue;
                var door = c.GetComponentInParent<Door>();
                if (door != null && !door.locked) continue;
                return false;
            }
            return true;
        }

        /// <summary>Todo lo que se puede pisar andando desde donde está el jugador.</summary>
        void FloodWalkable()
        {
            cells.Clear();
            Vector3 start = player.transform.position;
            var first = new Vector2Int(Mathf.RoundToInt(start.x / Cell), Mathf.RoundToInt(start.z / Cell));
            cells[first] = start.y;
            var open = new Queue<Vector2Int>();
            open.Enqueue(first);
            while (open.Count > 0 && cells.Count < 40000)
            {
                var c = open.Dequeue();
                float y = cells[c];
                foreach (var d in Neighbours)
                {
                    var next = c + d;
                    if (cells.ContainsKey(next)) continue;
                    if (next.y * Cell < -14f || (next.x * Cell > 22f && y > -5f) || next.x * Cell < -22f) continue;
                    var top = new Vector3(next.x * Cell, y + 0.45f, next.y * Cell);
                    if (!Physics.Raycast(top, Vector3.down, out var hit, 0.9f, ~0, QueryTriggerInteraction.Ignore)) continue;
                    var floor = new Vector3(top.x, hit.point.y, top.z);
                    if (!Free(floor)) continue;
                    cells[next] = floor.y;
                    open.Enqueue(next);
                }
            }
        }

        static Vector3 AimPoint(Interactable target)
        {
            var c = target.GetComponent<Collider>() ?? target.GetComponentInChildren<Collider>();
            if (c == null) return target.transform.position;
            if (c is BoxCollider b && b.isTrigger) return b.transform.TransformPoint(b.center);
            Vector3 p = c.bounds.center;
            return target is Door ? new Vector3(p.x, 1.25f, p.z) : p;
        }

        bool Sees(Vector3 eye, Vector3 point, Interactable target)
        {
            Vector3 d = point - eye;
            if (d.magnitude > interactor.reach - 0.05f) return false;
            int n = Physics.RaycastNonAlloc(eye, d.normalized, rayHits, d.magnitude + 0.3f, ~0, QueryTriggerInteraction.Collide);
            System.Array.Sort(rayHits, 0, n, Comparer<RaycastHit>.Create((a, b) => a.distance.CompareTo(b.distance)));
            for (int i = 0; i < n; i++)
            {
                var c = rayHits[i].collider;
                if (c is CharacterController) continue;
                var found = c.GetComponentInParent<Interactable>();
                if (found == target) return true;
                if (found != null && found.CanUse) return false;
                var door = c.GetComponentInParent<Door>();
                if (c is MeshCollider || (door != null && !door.IsOpen)) return false;
            }
            return false;
        }

        IEnumerator Use(Interactable target)
        {
            tries.TryGetValue(target, out int t);
            tries[target] = t + 1;
            Vector3 point = AimPoint(target);
            FloodWalkable();
            var spots = cells
                .Select(kv => new Vector3(kv.Key.x * Cell, kv.Value, kv.Key.y * Cell))
                .Where(s => { float h = new Vector2(s.x - point.x, s.z - point.z).magnitude; return h > 0.45f && h < 2.2f && !(target.name == "PuertaAlVacio" && s.x < -15.8f) && !(target.name == "PuertaEntrada" && s.z < 0.3f && story.Current != StoryDirector.Step.Llegada && story.Current < StoryDirector.Step.BucleLlegada); })
                .OrderBy(s => Mathf.Abs(new Vector2(s.x - point.x, s.z - point.z).magnitude - 1.2f));
            foreach (var s in spots)
            {
                if (!Sees(s + Vector3.up * 1.62f, point, target)) continue;
                player.Teleport(s + Vector3.up * 0.02f, 0f);
                player.LookAt(point);
                for (float w = 0f; w < 1.2f; w += Time.unscaledDeltaTime)
                {
                    if (interactor.Current == target) break;
                    player.LookAt(point);
                    yield return null;
                }
                if (interactor.Current != target)
                {
                    Log($"NO APUNTA a {target.name}: desde {s:F1} sale {(interactor.Current == null ? "nada" : interactor.Current.name)}");
                    yield break;
                }
                Log($"usa {target.name} ({target.Prompt})");
                target.Interact();
                yield return new WaitForSecondsRealtime(0.3f);
                yield break;
            }
            Log($"INALCANZABLE {target.name} ({target.Prompt}) desde {player.transform.position:F1}; celdas {cells.Count}");
        }

        IEnumerator Run()
        {
            var last = story.Current;
            float stuckSince = Time.realtimeSinceStartup;
            int tour = 0;
            var tourCells = new List<Vector3>();
            Log("empieza");
            while (story != null)
            {
                yield return new WaitForSecondsRealtime(0.1f);
                if (story.Current != last)
                {
                    Log($"--> {story.Current} (antes {last}, {Time.realtimeSinceStartup - stuckSince:F0}s) objetivo: {GameDirector.Instance.Night?.objective}");
                    last = story.Current;
                    stuckSince = Time.realtimeSinceStartup;
                    tries.Clear();
                    tourCells.Clear();
                }
                if (Time.realtimeSinceStartup - stuckSince > 200f)
                {
                    Log($"BLOQUEADO {story.Current}: 200 s sin avanzar. Ocupado={DialogueManager.Instance.IsBusy} objetivo={GameDirector.Instance.Night?.objective}");
                    yield break;
                }
                if (DialogueManager.Instance.IsBusy)
                {
                    if (story.Current == StoryDirector.Step.FinalPuerta && !FirstPersonController.InputBlocked && Time.realtimeSinceStartup - stuckSince > 25f)
                    {
                        Log("se tira al vacío");
                        player.Teleport(new Vector3(-16.4f, 0.02f, 5.2f), 270f);
                        yield return new WaitForSecondsRealtime(1f);
                    }
                    continue;
                }

                var all = FindObjectsByType<Interactable>(FindObjectsSortMode.None);
                var next = all.OfType<StoryObject>().Where(o => o.CanUse && Tries(o) < 2).Cast<Interactable>().FirstOrDefault()
                    ?? all.OfType<LightSwitch>().Where(s => s.isOn && Tries(s) < 1 && story.Current == StoryDirector.Step.ApagarLuces).Cast<Interactable>().FirstOrDefault()
                    ?? all.OfType<Door>().Where(d => Tries(d) < 2).Cast<Interactable>().FirstOrDefault();
                if (next != null)
                {
                    yield return Use(next);
                    continue;
                }

                // Nada que usar: recorre la casa a pie, por si el paso espera a que entre en algún sitio.
                if (tourCells.Count == 0)
                {
                    FloodWalkable();
                    tourCells = cells.Where(kv => kv.Key.x % 6 == 0 && kv.Key.y % 6 == 0)
                        .Select(kv => new Vector3(kv.Key.x * Cell, kv.Value, kv.Key.y * Cell)).ToList();
                    tries.Clear();
                    tour++;
                    if (reported.Add(story.Current + "/recorrido")) Log($"recorre la zona: {tourCells.Count} puntos, {cells.Count} celdas");
                }
                var spot = tourCells[^1];
                tourCells.RemoveAt(tourCells.Count - 1);
                player.Teleport(spot + Vector3.up * 0.02f, 0f);
                yield return new WaitForSecondsRealtime(0.15f);
            }
        }

        int Tries(Interactable i) => tries.TryGetValue(i, out int t) ? t : 0;
    }
}
#endif
