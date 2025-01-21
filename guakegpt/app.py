import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Keybinder', '3.0')
from gi.repository import Gtk, Gdk, GLib, Keybinder

import asyncio
import signal
import sys
import threading
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
        
        # Setup async event loop
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()
        
        # Setup window callbacks
        self.window.on_settings_changed = self.on_settings_changed
        self.window.set_event_loop(self.loop)
        
        # Initialize LLM client if API key is configured
        self.setup_llm_client()
        
        # Setup keyboard shortcut
        self.setup_keyboard_shortcut()

    def _run_event_loop(self):
        """Run the event loop in a separate thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

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

        try:
            Gtk.main()
        except KeyboardInterrupt:
            self.on_sigint()
        finally:
            # Clean up the event loop
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.loop_thread.join(timeout=1.0)
            self.loop.close()

    def on_sigint(self, *args):
        Gtk.main_quit()
        return GLib.SOURCE_REMOVE 