namespace Ominous
{
    /// <summary>Objeto que avisa al director de historia. El director decide si se puede usar ahora.</summary>
    public class StoryObject : Interactable
    {
        public string id;

        public override bool CanUse => StoryDirector.Instance != null && StoryDirector.Instance.CanUse(id);
        public override string Prompt => StoryDirector.Instance != null ? StoryDirector.Instance.PromptFor(id, prompt) : prompt;

        public override void Interact()
        {
            StoryDirector.Instance?.OnUse(id);
            base.Interact();
        }
    }
}
