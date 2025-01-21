import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from guakegpt.config.settings import Settings, LLMSettings, KEYRING_SERVICE

class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent, settings: Settings):
        super().__init__(
            title="Settings",
            parent=parent,
            flags=0
        )

        # Store reference to original settings
        self.settings = settings
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("OK", Gtk.ResponseType.OK)

        self.set_default_size(400, 300)

        notebook = Gtk.Notebook()
        self.get_content_area().pack_start(notebook, True, True, 0)

        # Window Settings Tab
        window_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        window_page.set_border_width(10)
        notebook.append_page(window_page, Gtk.Label(label="Window"))

        # Width setting
        width_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        width_label = Gtk.Label(label="Width (%)")
        self.width_adjustment = Gtk.Adjustment(value=settings.width_percent, lower=20, upper=100, step_increment=1)
        self.width_spin = Gtk.SpinButton(adjustment=self.width_adjustment, digits=0)
        width_box.pack_start(width_label, False, False, 0)
        width_box.pack_end(self.width_spin, False, False, 0)
        window_page.pack_start(width_box, False, False, 0)

        # Height setting
        height_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        height_label = Gtk.Label(label="Height (%)")
        self.height_adjustment = Gtk.Adjustment(value=settings.height_percent, lower=20, upper=100, step_increment=1)
        self.height_spin = Gtk.SpinButton(adjustment=self.height_adjustment, digits=0)
        height_box.pack_start(height_label, False, False, 0)
        height_box.pack_end(self.height_spin, False, False, 0)
        window_page.pack_start(height_box, False, False, 0)

        # Animation duration setting
        anim_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        anim_label = Gtk.Label(label="Animation Duration (ms)")
        self.anim_adjustment = Gtk.Adjustment(value=settings.animation_duration, lower=0, upper=1000, step_increment=10)
        self.anim_spin = Gtk.SpinButton(adjustment=self.anim_adjustment, digits=0)
        anim_box.pack_start(anim_label, False, False, 0)
        anim_box.pack_end(self.anim_spin, False, False, 0)
        window_page.pack_start(anim_box, False, False, 0)

        # Hide on focus loss setting
        self.focus_check = Gtk.CheckButton(label="Hide on Focus Loss")
        self.focus_check.set_active(settings.hide_on_focus_loss)
        window_page.pack_start(self.focus_check, False, False, 0)

        # LLM Settings Tab
        llm_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        llm_page.set_border_width(10)
        notebook.append_page(llm_page, Gtk.Label(label="LLM"))

        # Provider selection
        provider_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        provider_label = Gtk.Label(label="Provider")
        self.provider_combo = Gtk.ComboBoxText()
        providers = ["openai", "anthropic"]
        for provider in providers:
            self.provider_combo.append_text(provider)
        # Set active provider
        provider_index = providers.index(settings.llm.provider)
        self.provider_combo.set_active(provider_index)
        self.provider_combo.connect("changed", self.on_provider_changed)
        provider_box.pack_start(provider_label, False, False, 0)
        provider_box.pack_end(self.provider_combo, False, False, 0)
        llm_page.pack_start(provider_box, False, False, 0)

        # API Key
        api_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        api_label = Gtk.Label(label="API Key")
        self.api_entry = Gtk.Entry()
        self.api_entry.set_visibility(False)
        self.api_entry.set_text(settings.api_key)
        api_box.pack_start(api_label, False, False, 0)
        api_box.pack_end(self.api_entry, True, True, 0)
        llm_page.pack_start(api_box, False, False, 0)

        # Model selection
        model_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        model_label = Gtk.Label(label="Model")
        self.model_combo = Gtk.ComboBoxText()
        self.update_model_choices()
        model_box.pack_start(model_label, False, False, 0)
        model_box.pack_end(self.model_combo, False, False, 0)
        llm_page.pack_start(model_box, False, False, 0)

        # Temperature
        temp_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        temp_label = Gtk.Label(label="Temperature")
        self.temp_adjustment = Gtk.Adjustment(value=settings.llm.temperature, lower=0.0, upper=1.0, step_increment=0.1)
        self.temp_spin = Gtk.SpinButton(adjustment=self.temp_adjustment, digits=1)
        temp_box.pack_start(temp_label, False, False, 0)
        temp_box.pack_end(self.temp_spin, False, False, 0)
        llm_page.pack_start(temp_box, False, False, 0)

        # Max tokens
        tokens_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        tokens_label = Gtk.Label(label="Max Tokens")
        self.tokens_adjustment = Gtk.Adjustment(value=settings.llm.max_tokens, lower=1, upper=4096, step_increment=1)
        self.tokens_spin = Gtk.SpinButton(adjustment=self.tokens_adjustment, digits=0)
        tokens_box.pack_start(tokens_label, False, False, 0)
        tokens_box.pack_end(self.tokens_spin, False, False, 0)
        llm_page.pack_start(tokens_box, False, False, 0)

        # System prompt
        prompt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        prompt_label = Gtk.Label(label="System Prompt")
        prompt_label.set_halign(Gtk.Align.START)
        self.prompt_buffer = Gtk.TextBuffer()
        self.prompt_buffer.set_text(settings.llm.system_prompt)
        self.prompt_view = Gtk.TextView(buffer=self.prompt_buffer)
        self.prompt_view.set_wrap_mode(Gtk.WrapMode.WORD)
        prompt_scroll = Gtk.ScrolledWindow()
        prompt_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        prompt_scroll.add(self.prompt_view)
        prompt_scroll.set_size_request(-1, 100)
        prompt_box.pack_start(prompt_label, False, False, 0)
        prompt_box.pack_start(prompt_scroll, True, True, 0)
        llm_page.pack_start(prompt_box, True, True, 0)

        self.show_all()

    def update_model_choices(self):
        active_provider = self.provider_combo.get_active_text()
        self.model_combo.remove_all()
        
        if active_provider == "openai":
            models = ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]
        else:  # anthropic
            models = ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240229"]
        
        for model in models:
            self.model_combo.append_text(model)
        
        # Set active model based on current settings
        if self.settings.llm.provider == active_provider and self.settings.llm.model in models:
            self.model_combo.set_active(models.index(self.settings.llm.model))
        else:
            self.model_combo.set_active(0)

    def on_provider_changed(self, combo):
        self.update_model_choices()

    def get_settings(self) -> Settings:
        start_iter = self.prompt_buffer.get_start_iter()
        end_iter = self.prompt_buffer.get_end_iter()
        system_prompt = self.prompt_buffer.get_text(start_iter, end_iter, True)

        llm_settings = LLMSettings(
            provider=self.provider_combo.get_active_text(),
            model=self.model_combo.get_active_text(),
            temperature=self.temp_adjustment.get_value(),
            max_tokens=int(self.tokens_adjustment.get_value()),
            system_prompt=system_prompt
        )

        settings = Settings(
            width_percent=int(self.width_adjustment.get_value()),
            height_percent=int(self.height_adjustment.get_value()),
            animation_duration=int(self.anim_adjustment.get_value()),
            hide_on_focus_loss=self.focus_check.get_active(),
            llm=llm_settings
        )

        # Handle API key separately since it's stored in keyring
        api_key = self.api_entry.get_text()
        settings.api_key = api_key

        return settings 