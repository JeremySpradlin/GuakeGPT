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
        self.settings_open = False
        
        # Initialize window with settings
        self.window = DropdownWindow(
            width_percent=self.settings.width_percent,
            height_percent=self.settings.height_percent,
            animation_duration=self.settings.animation_duration,
            hide_on_focus_loss=self.settings.hide_on_focus_loss
        )
        
        # Connect to window's settings events
        self.window.connect('settings-opened', self.on_settings_opened)
        self.window.connect('settings-closed', self.on_settings_closed)
        self.window.on_settings_changed = self.on_settings_changed
        
        # Initialize keybinder
        print(f"Setting up global hotkey ({self.settings.hotkey})...")
        Keybinder.init()
        self.bind_hotkey()

    def bind_hotkey(self):
        # Unbind previous hotkey if it exists
        try:
            Keybinder.unbind(self.settings.hotkey)
        except:
            pass
            
        if not Keybinder.bind(self.settings.hotkey, self.on_hotkey, None):
            print(f"Failed to bind {self.settings.hotkey} key!")
        else:
            print(f"{self.settings.hotkey} key bound successfully")

    def on_settings_opened(self, window):
        self.settings_open = True
        print("Settings opened, hotkey disabled")

    def on_settings_closed(self, window):
        self.settings_open = False
        print("Settings closed, hotkey enabled")

    def on_settings_changed(self, new_settings):
        # Update hotkey if changed
        if new_settings.hotkey != self.settings.hotkey:
            self.settings.hotkey = new_settings.hotkey
            self.bind_hotkey()
        
        # Update other settings
        self.settings = new_settings
        
        # Save to disk
        self.settings.save()
        print("Settings saved successfully")

    def on_hotkey(self, key, user_data):
        if not self.settings_open:
            print(f"Hotkey pressed: {key}")
            self.window.toggle_window()

    def run(self):
        print("Starting main loop...")
        Gtk.main()

    def quit(self):
        print("Quitting...")
        Gtk.main_quit() 