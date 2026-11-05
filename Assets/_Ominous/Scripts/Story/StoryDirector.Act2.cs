using System.Collections;
using UnityEngine;
using Yarn.Unity;

namespace Ominous
{
    /// <summary>Acto 2: el grifo, las visitas 2 a 4, las habitaciones ocultas y la desaparición de Roberta.</summary>
    public partial class StoryDirector
    {
        [Header("Acto 2")]
        public GameObject wrench;
        public GameObject fallenCan;
        public GameObject kitchenCabinetOpen;
        public GameObject newPicture;
        public GameObject photoOnShelf;
        public GameObject photoOnFloor;
        public SimpleHinge shelfNudge;
        public SimpleHinge shelfAside;
        public SimpleHinge closetLeft;
        public SimpleHinge closetRight;
        public SimpleHinge closetBack;
        public TVFlicker tv;
        public Light tvFill;
        public GameObject chechuWindowLight;
        public GameObject chechuSilhouette;
        public GameObject chechuDoorLeaf;
        public GameObject chechuDoorDark;
        public GameObject streetBounds;
        public Light hiddenRoomLight;
        public Light chechuPorchLight;

        bool hasWrench, cuartitoSeen, huecoSeen, kitchenScare, tvOff, holeBed, holeBath;
        float stepTime;
        int searched;
        readonly System.Collections.Generic.HashSet<string> searchedRooms = new();

        static readonly Vector3 ChechuAtHome = new(7f, 0f, -9.15f);

        void BeginAct2State()
        {
            wrench.SetActive(true);
            fallenCan.SetActive(false);
            kitchenCabinetOpen.SetActive(false);
            newPicture.SetActive(false);
            photoOnShelf.SetActive(true);
            photoOnFloor.SetActive(false);
            chechuWindowLight.SetActive(false);
            chechuSilhouette.SetActive(false);
            chechuDoorLeaf.SetActive(true);
            chechuDoorDark.SetActive(false);
            streetBounds.SetActive(false);
            hiddenRoomLight.enabled = false;
            chechuPorchLight.enabled = false;
        }

        bool InRoom(float x0, float x1, float z0, float z1)
        {
            Vector3 p = player.transform.position;
            return p.x >= x0 && p.x <= x1 && p.z >= z0 && p.z <= z1;
        }

        void RegisterAct2Commands(DialogueRunner r)
        {
            r.AddCommandHandler("animacion_llave_grifo", () => { player.LookAt(new Vector3(9.5f, 0.95f, 7.2f)); });
            r.AddCommandHandler("objeto_roto", (string what) => { });
            r.AddCommandHandler("susto", (string what) => Scare(what));
            r.AddCommandHandler("estanteria_cede", () =>
            {
                shelfNudge.Open();
                Sfx.Play("objeto_cae", shelfNudge.transform.position);
            });
            r.AddCommandHandler("roberta_desaparece", () => HideRoberta());
            r.AddCommandHandler("roberta_aparece", (string where) => ShowRoberta(where));
            r.AddCommandHandler("puerta_chechu_se_abre", () =>
            {
                chechuDoorLeaf.SetActive(false);
                chechuDoorDark.SetActive(true);
                chechu.Show(true);
                chechu.SetPose("depie");
                chechu.Place(ChechuAtHome, 0f);
                player.LookAt(chechu.head.position);
            });
            r.AddCommandHandler("puerta_chechu_se_cierra", () =>
            {
                chechuDoorLeaf.SetActive(true);
                chechuDoorDark.SetActive(false);
                chechu.Show(false);
            });
        }

        void Scare(string what)
        {
            switch (what)
            {
                case "bote_cae_garaje":
                    fallenCan.SetActive(true);
                    Sfx.Play("objeto_cae", fallenCan.transform.position);
                    break;
                case "armario_cocina_abierto":
                    kitchenCabinetOpen.SetActive(true);
                    Sfx.Play("objeto_cae", kitchenCabinetOpen.transform.position);
                    break;
                case "foto_cae_estanteria":
                    photoOnShelf.SetActive(false);
                    photoOnFloor.SetActive(true);
                    Sfx.Play("objeto_cae", photoOnFloor.transform.position);
                    break;
            }
        }

        void HideRoberta()
        {
            roberta.Show(false);
            GameDirector.Instance.Night.robertaInBed = false;
            TurnTvOff();
        }

        void TurnTvOff()
        {
            if (tvOff) return;
            tvOff = true;
            tv.TurnOff();
            if (tvFill != null) tvFill.enabled = false;
            if (tvSound != null) tvSound.Stop();
        }

        void ShowRoberta(string where)
        {
            roberta.Show(true);
            roberta.SetPose("depie");
            if (where == "cocina") roberta.Place(new Vector3(9.6f, 0f, 1.25f), 45f);
            else if (where == "colada") roberta.Place(new Vector3(13.2f, 0f, 8.9f), 225f);
            else if (where == "ventana_enfrente") roberta.Place(new Vector3(4.4f, 0.45f, -9.5f), 0f);
            else if (where == "garaje_coche")
            {
                roberta.SetPose("sentada");
                roberta.Place(carSeat, 0f);
            }
        }

        // ---------- objetos ----------

        bool CanUseAct2(string id) => id switch
        {
            "llave" => Current == Step.GrifoArreglar && !hasWrench,
            "baldosa" => Current >= Step.CerrarV2 && !usedOnce.Contains("baldosa"),
            "foto_suelo" => Current == Step.FotoCaida,
            "foto_balda" => Current == Step.FotoEnMano,
            "estanteria" => Current == Step.EstanteriaCedida,
            "chaqueta" => Current == Step.Cuartito && !usedOnce.Contains("chaqueta"),
            "silla" => Current == Step.Cuartito && !usedOnce.Contains("silla"),
            "armario" => Current == Step.ArmarioGolpe,
            "fondo" => Current == Step.ArmarioFondo,
            "agujero_cama" => Current == Step.Hueco && !peeping,
            "agujero_bano" => Current == Step.Hueco && !peeping,
            "puerta_chechu" => Current == Step.SalirCasa,
            _ => CanUseAct3(id),
        };

        void OnUseAct2(string id)
        {
            if (OnUseAct3(id)) return;
            var dm = DialogueManager.Instance;
            switch (id)
            {
                case "llave":
                    hasWrench = true;
                    wrench.SetActive(false);
                    dm.Play("Acto2_Garaje_Herramienta");
                    break;
                case "baldosa":
                    usedOnce.Add("baldosa");
                    dm.Play("Acto2_Baldosa");
                    break;
                case "foto_suelo":
                    photoOnFloor.SetActive(false);
                    Set(Step.FotoEnMano);
                    GameDirector.Instance.SetObjective("Vuelve a poner la foto en la estantería");
                    break;
                case "foto_balda":
                    photoOnShelf.SetActive(true);
                    Set(Step.EstanteriaCedida);
                    dm.Play("Acto2_Objeto_Colocado");
                    break;
                case "estanteria":
                    Set(Step.Cuartito);
                    shelfAside.Open();
                    hiddenRoomLight.enabled = true;
                    Sfx.Play("objeto_cae", shelfAside.transform.position);
                    GameDirector.Instance.SetObjective("Entra a ver qué hay detrás");
                    stepTime = 0f;
                    break;
                case "chaqueta":
                    usedOnce.Add("chaqueta");
                    dm.Play("Habitacion1_Chaqueta");
                    break;
                case "silla":
                    usedOnce.Add("silla");
                    dm.Play("Habitacion1_Silla");
                    break;
                case "armario":
                    closetLeft.Open();
                    closetRight.Open();
                    Set(Step.ArmarioFondo);
                    dm.Play("Roberta_Busqueda_Armario");
                    break;
                case "fondo":
                    closetBack.Open();
                    Sfx.Play("objeto_cae", closetBack.transform.position);
                    Set(Step.Hueco);
                    GameDirector.Instance.SetObjective("Entra en el hueco y mira por los agujeros");
                    break;
                case "agujero_cama":
                    holeBed = true;
                    StartCoroutine(HolePeep(new Vector3(5.9f, 1.59f, 7.43f), 270f, "Habitacion2_Agujero_Dormitorio"));
                    break;
                case "agujero_bano":
                    holeBath = true;
                    StartCoroutine(HolePeep(new Vector3(6.9f, 1.72f, 7.27f), 90f, "Habitacion2_Agujero_Bano"));
                    break;
                case "puerta_chechu":
                    Set(Step.VisitaV4);
                    GameDirector.Instance.SetObjective("");
                    dm.Play("Visita4", () =>
                    {
                        Set(Step.Volver);
                        ShowRoberta("cocina");
                    });
                    break;
            }
        }

        IEnumerator HolePeep(Vector3 position, float yaw, string node)
        {
            peeping = true;
            FirstPersonController.SetBlocked(this, true);
            player.SetPeep(position, yaw, 74f);
            DialogueManager.Instance.Play(node);
            yield return new WaitForSeconds(1f);
            while (DialogueManager.Instance.IsBusy) yield return null;
            yield return new WaitForSeconds(0.8f);
            player.EndPeep();
            FirstPersonController.SetBlocked(this, false);
            peeping = false;
            if (holeBed && holeBath) StartLeaveHouse();
        }

        void StartLeaveHouse()
        {
            if (Current != Step.Hueco) return;
            Set(Step.SalirCasa);
            frontDoor.locked = false;
            threshold.SetActive(false);
            streetBounds.SetActive(true);
            chechuPorchLight.enabled = true;
            DialogueManager.Instance.Play("Visita4_Salir", () => GameDirector.Instance.Checkpoint("visita4"));
        }

        void UseFaucet()
        {
            var dm = DialogueManager.Instance;
            if (!hasWrench) { dm.Play("Acto2_Grifo_SinHerramienta"); return; }
            Set(Step.GrifoRoto);
            GameDirector.Instance.SetObjective("");
            stepTime = 0f;
            dm.Play("Acto2_Grifo_Intento", () => stepTime = 0f);
        }

        void PrepareVisit(Step waiting, string checkpoint)
        {
            Set(waiting);
            knockTimer = 0f;
            PlaceChechu();
            frontDoor.locked = false;
            Sfx.Play("llamada_puerta", frontDoor.transform.position + Vector3.up * 1.2f);
            GameDirector.Instance.SetObjective("Abre la puerta");
            GameDirector.Instance.Checkpoint(checkpoint);
        }

        bool OnFrontDoorAct2()
        {
            var dm = DialogueManager.Instance;
            if (Current == Step.EsperaV2 && frontDoor.IsOpen)
            {
                Set(Step.VisitaV2);
                GameDirector.Instance.SetObjective("");
                player.LookAt(chechu.head.position);
                dm.Play("Visita2", () =>
                {
                    Set(Step.CerrarV2);
                    GameDirector.Instance.SetObjective("Cierra la puerta");
                    chechuWindowLight.SetActive(true);
                    newPicture.SetActive(true);
                });
                return true;
            }
            if (Current == Step.CerrarV2 && !frontDoor.IsOpen)
            {
                frontDoor.locked = true;
                threshold.SetActive(false);
                Set(Step.Explorar);
                GameDirector.Instance.SetObjective("Da una vuelta por la casa");
                stepTime = 0f;
                return true;
            }
            if (Current == Step.EsperaV3 && frontDoor.IsOpen)
            {
                Set(Step.VisitaV3);
                GameDirector.Instance.SetObjective("");
                player.LookAt(chechu.head.position);
                dm.Play("Visita3", () =>
                {
                    Set(Step.CerrarV3);
                    GameDirector.Instance.SetObjective("Cierra la puerta");
                    chechuSilhouette.SetActive(true);
                });
                return true;
            }
            if (Current == Step.CerrarV3 && !frontDoor.IsOpen)
            {
                frontDoor.locked = true;
                threshold.SetActive(false);
                Set(Step.IrDormitorio);
                GameDirector.Instance.SetObjective("Ve a ver a Roberta");
                return true;
            }
            return false;
        }

        void UpdateAct2()
        {
            if (DialogueManager.Instance.IsBusy || peeping) return;
            var dm = DialogueManager.Instance;
            stepTime += Time.deltaTime;
            switch (Current)
            {
                case Step.GrifoRoto:
                    if (stepTime > 7f) PrepareVisit(Step.EsperaV2, "visita2");
                    break;
                case Step.Explorar:
                    if (!kitchenScare && InRoom(8.2f, 14f, 0f, 4.4f))
                    {
                        kitchenScare = true;
                        dm.Play("Acto2_Ruido_Cocina");
                    }
                    else if (stepTime > 8f && InRoom(6.3f, 8.9f, 4.4f, 6f))
                    {
                        Set(Step.FotoCaida);
                        dm.Play("Acto2_Objeto_Cae");
                    }
                    break;
                case Step.Cuartito:
                    if (!cuartitoSeen && InRoom(7f, 8.2f, 0f, 4.4f))
                    {
                        cuartitoSeen = true;
                        stepTime = 0f;
                        GameDirector.Instance.SetObjective("Mira lo que hay en el cuartito");
                        GameDirector.Instance.OpenRoom(1);
                        dm.Play("Habitacion1");
                    }
                    else if (cuartitoSeen && !InRoom(7f, 8.2f, 0f, 4.4f) && stepTime > 12f) PrepareVisit(Step.EsperaV3, "visita3");
                    else if (cuartitoSeen && stepTime > 60f) PrepareVisit(Step.EsperaV3, "visita3");
                    break;
                case Step.IrDormitorio:
                    if (InRoom(0f, 6f, 6f, 10f))
                    {
                        Set(Step.Busqueda);
                        dm.Play("Roberta_CamaVacia");
                    }
                    break;
                case Step.Busqueda:
                    Search("bano", "Roberta_Busqueda_Bano", 6.8f, 10f, 6f, 10f);
                    Search("salon", "Roberta_Busqueda_Salon", 0f, 5f, 0f, 4.4f);
                    Search("cocina", "Roberta_Busqueda_Cocina", 8.2f, 14f, 0f, 4.4f);
                    Search("garaje", "Roberta_Busqueda_Garaje", 14f, 19f, 0f, 4.4f);
                    Search("puerta", "Roberta_Busqueda_Puerta", 5f, 7f, 0f, 1.4f);
                    if (searched >= 3 && !dm.IsBusy)
                    {
                        Set(Step.ArmarioGolpe);
                        Sfx.Play("golpe_armario", closetBack.transform.position);
                        GameDirector.Instance.SetObjective("Algo ha sonado en el dormitorio");
                    }
                    break;
                case Step.Hueco:
                    if (!huecoSeen && InRoom(6f, 6.8f, 6f, 10f))
                    {
                        huecoSeen = true;
                        GameDirector.Instance.OpenRoom(2);
                        dm.Play("Habitacion2");
                    }
                    break;
                case Step.Volver:
                    if (InRoom(5f, 7f, 0.8f, 4.4f) && frontDoor.IsOpen)
                    {
                        frontDoor.Interact();
                        frontDoor.locked = true;
                        streetBounds.SetActive(false);
                    }
                    if (InRoom(8.2f, 14f, 0f, 4.4f))
                    {
                        Set(Step.RobertaCocina);
                        player.LookAt(roberta.head.position);
                        dm.Play("Roberta_Cocina", StartAct3);
                    }
                    break;
            }
        }

        void Search(string room, string node, float x0, float x1, float z0, float z1)
        {
            if (searchedRooms.Contains(room) || !InRoom(x0, x1, z0, z1)) return;
            searchedRooms.Add(room);
            searched++;
            DialogueManager.Instance.Play(node);
        }

        /// <summary>Para pruebas: salta a un paso como si se cargara una partida.</summary>
        public void JumpForTest(Step step)
        {
            StopMonologue();
            var night = GameDirector.Instance.Night;
            night.act = step >= Step.GrifoArreglar ? 2 : 1;
            ApplyRestored(step);
            Set(step);
        }

        void RestoreAct2(Step step)
        {
            BeginAct2State();
            hasWrench = step >= Step.GrifoRoto;
            wrench.SetActive(!hasWrench);
            if (step > Step.EsperaV2)
            {
                chechuWindowLight.SetActive(true);
                newPicture.SetActive(true);
            }
            if (step > Step.Cuartito)
            {
                kitchenScare = true;
                cuartitoSeen = true;
                shelfNudge.OpenNow();
                shelfAside.OpenNow();
                hiddenRoomLight.enabled = true;
                photoOnShelf.SetActive(true);
            }
            if (step > Step.EsperaV3) chechuSilhouette.SetActive(true);
            if (step >= Step.SalirCasa)
            {
                HideRoberta();
                closetLeft.OpenNow();
                closetRight.OpenNow();
                closetBack.OpenNow();
                huecoSeen = true;
                streetBounds.SetActive(true);
                threshold.SetActive(false);
                chechuPorchLight.enabled = true;
            }
        }
    }
}
