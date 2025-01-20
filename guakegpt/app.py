import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Keybinder', '3.0')
from gi.repository import Gtk, Keybinder

from guakegpt.ui.window import DropdownWindow
from guakegpt.config.settings import Settings

class GuakeGPT:
    def __init__(self):
        print("Initializing GuakeGPT...")
        
        # Load settings
        self.settings = Settings.load()
        
        # Initialize window with settings
        self.window = DropdownWindow(
            width_percent=self.settings.width_percent,
            height_percent=self.settings.height_percent,
            animation_duration=self.settings.animation_duration,
            hide_on_focus_loss=self.settings.hide_on_focus_loss
        )
        
        # Initialize keybinder
        print(f"Setting up global hotkey ({self.settings.hotkey})...")
        Keybinder.init()
        if not Keybinder.bind(self.settings.hotkey, self.on_hotkey, None):
            print(f"Failed to bind {self.settings.hotkey} key!")
        else:
            print(f"{self.settings.hotkey} key bound successfully")

    def on_hotkey(self, key, user_data):
        print(f"Hotkey pressed: {key}")
        self.window.toggle_window()

    def run(self):
        print("Starting main loop...")
        Gtk.main()

    def quit(self):
        print("Quitting...")
        Gtk.main_quit() 