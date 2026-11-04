using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Ominous
{
    /// <summary>Personaje provisional: cambia de postura y se desliza por una ruta, abriendo las puertas que pisa.</summary>
    public class ActorFigure : MonoBehaviour
    {
        [Serializable] public class Pose { public string name; public GameObject root; }
        public List<Pose> poses = new();
        public float walkSpeed = 0.95f;
        public Transform head;

        Coroutine walking;

        public void SetPose(string pose)
        {
            foreach (var p in poses) p.root.SetActive(p.name == pose);
        }

        public void Show(bool visible) => gameObject.SetActive(visible);

        public void Place(Vector3 position, float yaw)
        {
            if (walking != null) StopCoroutine(walking);
            walking = null;
            transform.SetPositionAndRotation(position, Quaternion.Euler(0f, yaw, 0f));
        }

        public void Walk(Vector3[] path, Action done = null)
        {
            if (walking != null) StopCoroutine(walking);
            walking = StartCoroutine(WalkRoutine(path, done));
        }

        public void Slump(float degrees)
        {
            foreach (var p in poses)
                if (p.root.activeSelf) p.root.transform.localRotation = Quaternion.Euler(degrees, 0f, degrees * 0.4f);
        }

        IEnumerator WalkRoutine(Vector3[] path, Action done)
        {
            SetPose("depie");
            foreach (var target in path)
            {
                var doorCheck = Physics.OverlapSphere(target, 0.8f);
                foreach (var hit in doorCheck)
                {
                    var door = hit.GetComponentInParent<Door>();
                    if (door != null && !door.IsOpen && !door.locked) door.Interact();
                }
                while (true)
                {
                    Vector3 to = target - transform.position;
                    to.y = 0f;
                    if (to.magnitude < 0.05f) break;
                    Quaternion look = Quaternion.LookRotation(to);
                    transform.rotation = Quaternion.RotateTowards(transform.rotation, look, 260f * Time.deltaTime);
                    transform.position += to.normalized * Mathf.Min(walkSpeed * Time.deltaTime, to.magnitude);
                    yield return null;
                }
            }
            walking = null;
            done?.Invoke();
        }
    }
}
