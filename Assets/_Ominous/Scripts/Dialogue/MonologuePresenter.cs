using UnityEngine;
using Yarn.Unity;

namespace Ominous
{
    /// <summary>
    /// Alguien habla a lo suyo, en segundo plano: no para al jugador ni ocupa el diálogo principal.
    /// El subtítulo se ve según la distancia, igual que se oiría la voz.
    /// </summary>
    public class MonologuePresenter : DialoguePresenterBase
    {
        public Transform speaker;
        public Transform listener;
        public float hearingRange = 6f;

        public override YarnTask OnDialogueStartedAsync() => YarnTask.CompletedTask;

        public override YarnTask OnDialogueCompleteAsync()
        {
            GameUI.Instance?.SetAmbientLine(null, 0f);
            return YarnTask.CompletedTask;
        }

        public override async YarnTask RunLineAsync(LocalizedLine line, LineCancellationToken token)
        {
            string text = line.TextWithoutCharacterName.Text;
            float duration = Mathf.Max(2.4f, text.Split(' ').Length * 0.42f);
            float elapsed = 0f;
            while (elapsed < duration && !token.NextContentToken.IsCancellationRequested)
            {
                elapsed += Time.deltaTime;
                float d = speaker != null && listener != null ? Vector3.Distance(speaker.position, listener.position) : 0f;
                float a = Mathf.Clamp01((hearingRange - d) / (hearingRange * 0.45f));
                GameUI.Instance?.SetAmbientLine(text, a);
                await YarnTask.Yield();
            }
            GameUI.Instance?.SetAmbientLine(null, 0f);
        }
    }
}
