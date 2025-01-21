import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Keybinder', '3.0')
from gi.repository import Gtk, Gdk, GLib, Keybinder

import asyncio
import signal
import sys
from typing import Optional

from guakegpt.ui.window import DropdownWindow
from guakegpt.config.settings import Settings, KEYRING_SERVICE
from guakegpt.llm import LLMClient

class GuakeGPT:
    def __init__(self):
        self.settings = Settings.load()
        self.window = DropdownWindow(
            width_percent=self.settings.width_percent,
            height_percent=self.settings.height_percent,
            animation_duration=self.settings.animation_duration,
            hide_on_focus_loss=self.settings.hide_on_focus_loss
        )
        self.llm_client: Optional[LLMClient] = None
        
        # Setup window callbacks
        self.window.on_settings_changed = self.on_settings_changed
        
        # Initialize LLM client if API key is configured
        self.setup_llm_client()
        
        # Setup keyboard shortcut
        self.setup_keyboard_shortcut()

    def setup_llm_client(self):
        api_key = self.settings.api_key
        if api_key:
            self.llm_client = LLMClient(self.settings)
            self.window.set_llm_client(self.llm_client)

    def setup_keyboard_shortcut(self):
        Keybinder.init()
        if not Keybinder.bind(self.settings.hotkey, self.on_hotkey):
            print(f"Failed to bind hotkey: {self.settings.hotkey}")
            sys.exit(1)

    def on_hotkey(self, keystring):
        self.window.toggle_window()
        return True

    def on_settings_changed(self, new_settings: Settings):
        # Save new settings
        old_hotkey = self.settings.hotkey
        self.settings = new_settings
        self.settings.save()
        
        # Update hotkey if changed
        if old_hotkey != new_settings.hotkey:
            Keybinder.unbind(old_hotkey)
            if not Keybinder.bind(new_settings.hotkey, self.on_hotkey):
                print(f"Failed to bind new hotkey: {new_settings.hotkey}")
        
        # Update LLM client if needed
        self.setup_llm_client()

    def run(self):
        # Setup signal handlers
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, self.on_sigint)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, self.on_sigint)
        
        # Create event loop
        loop = asyncio.get_event_loop()
        
        try:
            Gtk.main()
        except KeyboardInterrupt:
            self.on_sigint()

    def on_sigint(self, *args):
        Gtk.main_quit()
        return GLib.SOURCE_REMOVE 