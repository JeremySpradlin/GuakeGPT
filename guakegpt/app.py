import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Keybinder', '3.0')
from gi.repository import Gtk, Keybinder

from guakegpt.ui.window import DropdownWindow

class GuakeGPT:
    def __init__(self):
        print("Initializing GuakeGPT...")
        self.window = DropdownWindow()
        
        # Initialize keybinder
        print("Setting up global hotkey (F12)...")
        Keybinder.init()
        if not Keybinder.bind('F12', self.on_hotkey, None):
            print("Failed to bind F12 key!")
        else:
            print("F12 key bound successfully")

    def on_hotkey(self, key, user_data):
        print(f"Hotkey pressed: {key}")
        self.window.toggle_window()

    def run(self):
        print("Starting main loop...")
        Gtk.main()

    def quit(self):
        print("Quitting...")
        Gtk.main_quit() 