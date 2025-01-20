import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import time

class DropdownWindow(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)

        # Window setup
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)

        # Default settings
        self.width_percent = 80
        self.height_percent = 50
        self.animation_duration = 250
        self.hidden = True
        self.animation_in_progress = False

        # Get screen dimensions
        screen = self.get_screen()
        monitor = screen.get_primary_monitor()
        geometry = screen.get_monitor_geometry(monitor)
        self.screen_width = geometry.width
        self.screen_height = geometry.height

        # Calculate window dimensions
        self.window_width = int(self.screen_width * self.width_percent / 100)
        self.window_height = int(self.screen_height * self.height_percent / 100)
        self.set_size_request(self.window_width, self.window_height)

        # Position window
        self.move((self.screen_width - self.window_width) // 2, 0)

        # Setup main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.main_box)

        # Setup chat interface
        self.setup_chat_interface()

        # Connect focus out event
        self.connect('focus-out-event', self.on_focus_out)

        # Initialize animation properties
        self.current_y = -self.window_height
        self.target_y = -self.window_height

    def setup_chat_interface(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.chat_buffer = Gtk.TextBuffer()
        self.chat_view = Gtk.TextView(buffer=self.chat_buffer)
        self.chat_view.set_editable(False)
        self.chat_view.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled.add(self.chat_view)
        self.main_box.pack_start(scrolled, True, True, 0)

        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.input_entry = Gtk.Entry()
        self.input_entry.connect('activate', self.on_send_message)
        send_button = Gtk.Button.new_with_label("Send")
        send_button.connect('clicked', self.on_send_message)

        input_box.pack_start(self.input_entry, True, True, 5)
        input_box.pack_start(send_button, False, False, 5)
        self.main_box.pack_start(input_box, False, False, 5)

    def on_send_message(self, widget):
        message = self.input_entry.get_text()
        if message:
            end_iter = self.chat_buffer.get_end_iter()
            self.chat_buffer.insert(end_iter, f"You: {message}\n")
            self.input_entry.set_text("")

    def on_focus_out(self, widget, event):
        self.hide_window()
        return False

    def toggle_window(self):
        if self.animation_in_progress:
            return

        if self.hidden:
            self.show_all()
            self.hidden = False
            self.target_y = 0
        else:
            self.target_y = -self.window_height
            self.hidden = True

        self.start_animation()

    def hide_window(self):
        if not self.hidden:
            self.toggle_window()

    def start_animation(self):
        self.animation_in_progress = True
        self.animation_start_time = time.time() * 1000
        self.animation_start_y = self.current_y
        GLib.timeout_add(16, self.animate_step)

    def animate_step(self):
        current_time = time.time() * 1000
        progress = min(1.0, (current_time - self.animation_start_time) / self.animation_duration)
        
        progress = self.ease_in_out_quad(progress)
        
        self.current_y = self.animation_start_y + (self.target_y - self.animation_start_y) * progress
        self.move((self.screen_width - self.window_width) // 2, int(self.current_y))

        if progress >= 1.0:
            self.animation_in_progress = False
            if self.hidden:
                self.hide()
            return False
        return True

    def ease_in_out_quad(self, t: float) -> float:
        return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2 