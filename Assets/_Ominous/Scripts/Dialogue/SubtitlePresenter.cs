using System.Threading;
using UnityEngine;
using UnityEngine.InputSystem;
using Yarn.Unity;

namespace Ominous
{
    /// <summary>
    /// Muestra los diálogos. Los pensamientos de Chevas salen en cursiva y gris, avanzan solos y no paran al jugador;
    /// las líneas habladas esperan a E, espacio o clic.
    /// </summary>
    public class SubtitlePresenter : DialoguePresenterBase
    {
        public const string ThoughtSpeaker = "Pensamiento";
        public string NextSpeaker { get; set; }
        public bool AdvanceRequested { get; set; }
        public int RequestedOption { get; set; } = -1;
        /// <summary>Opciones en pantalla ahora mismo.</summary>
        public int OptionCount { get; private set; }
        /// <summary>Para pruebas: qué se está mostrando ahora mismo.</summary>
        public string CurrentText { get; private set; }

        public override YarnTask OnDialogueStartedAsync() => YarnTask.CompletedTask;

        public override YarnTask OnDialogueCompleteAsync()
        {
            NextSpeaker = null;
            CurrentText = null;
            GameUI.Instance?.HideSubtitle();
            OptionCount = 0;
            GameUI.Instance?.HideOptions();
            FirstPersonController.SetBlocked(this, false);
            return YarnTask.CompletedTask;
        }

        public override async YarnTask RunLineAsync(LocalizedLine line, LineCancellationToken token)
        {
            string speaker = line.CharacterName ?? NextSpeaker;
            NextSpeaker = null;
            string text = line.TextWithoutCharacterName.Text;
            bool thought = speaker == ThoughtSpeaker;
            CurrentText = text;
            AdvanceRequested = false;

            FirstPersonController.SetBlocked(this, !thought);
            GameUI.Instance?.ShowSubtitle(thought ? null : speaker, text, thought);

            float minTime = 0.7f;
            float thoughtTime = Mathf.Max(4f, text.Split(' ').Length * 0.62f);
            float elapsed = 0f;
            while (!token.NextContentToken.IsCancellationRequested)
            {
                elapsed += Time.unscaledDeltaTime;
                if (elapsed > minTime && !PauseMenu.IsPaused && (AdvanceRequested || (!thought && PressedAdvance()))) break;
                if (thought && elapsed > thoughtTime) break;
                await YarnTask.Yield();
            }
            AdvanceRequested = false;
            GameUI.Instance?.HideSubtitle();
        }

        static bool PressedAdvance() => GameInput.AdvancePressed;

        public override async YarnTask<DialogueOption> RunOptionsAsync(DialogueOption[] options, LineCancellationToken token)
        {
            FirstPersonController.SetBlocked(this, true);
            RequestedOption = -1;
            OptionCount = options.Length;
            CurrentText = options.Length > 0 ? options[0].Line.TextWithoutCharacterName.Text : null;
            GameUI.Instance?.ShowOptions(options, index => RequestedOption = index);
            while (RequestedOption < 0 && !token.NextContentToken.IsCancellationRequested)
                await YarnTask.Yield();
            OptionCount = 0;
            GameUI.Instance?.HideOptions();
            return RequestedOption >= 0 ? options[RequestedOption] : null;
        }
    }
}
