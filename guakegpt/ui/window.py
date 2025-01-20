import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject
import time

from guakegpt.ui.settings_dialog import SettingsDialog

class DropdownWindow(Gtk.Window):
    __gsignals__ = {
        'settings-opened': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'settings-closed': (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    def __init__(self, width_percent: int = 80, height_percent: int = 50,
                 animation_duration: int = 250, hide_on_focus_loss: bool = True):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)

        # Window setup
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)

        # Store settings
        self.width_percent = width_percent
        self.height_percent = height_percent
        self.animation_duration = animation_duration
        self.hide_on_focus_loss = hide_on_focus_loss
        self.hidden = True
        self.animation_in_progress = False
        self.focus_handler_id = None
        self.settings_dialog = None

        # Get screen dimensions
        self.update_screen_dimensions()
        
        # Initialize window dimensions
        self.window_width = int(self.screen_width * self.width_percent / 100)
        self.window_height = int(self.screen_height * self.height_percent / 100)
        
        # Initialize animation properties
        self.current_y = -self.window_height
        self.target_y = -self.window_height
        
        # Update window size and position
        self.update_window_dimensions()

        # Setup main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.main_box)

        # Setup header with settings button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        settings_button = Gtk.Button()
        settings_button.set_relief(Gtk.ReliefStyle.NONE)
        settings_icon = Gtk.Image.new_from_icon_name("preferences-system", Gtk.IconSize.SMALL_TOOLBAR)
        settings_button.add(settings_icon)
        settings_button.connect("clicked", self.on_settings_clicked)
        header_box.pack_end(settings_button, False, False, 5)
        self.main_box.pack_start(header_box, False, False, 5)

        # Setup chat interface
        self.setup_chat_interface()

        # Connect focus out event if enabled
        self.update_focus_handler()

    def update_screen_dimensions(self):
        screen = self.get_screen()
        monitor = screen.get_primary_monitor()
        geometry = screen.get_monitor_geometry(monitor)
        self.screen_width = geometry.width
        self.screen_height = geometry.height

    def update_window_dimensions(self):
        # Calculate new dimensions
        self.window_width = int(self.screen_width * self.width_percent / 100)
        self.window_height = int(self.screen_height * self.height_percent / 100)
        
        # Update window size
        self.set_default_size(self.window_width, self.window_height)
        self.resize(self.window_width, self.window_height)
        
        # If window is hidden, update target and current y positions
        if self.hidden:
            self.target_y = -self.window_height
            self.current_y = -self.window_height
        
        # Center horizontally and maintain vertical position
        x_pos = (self.screen_width - self.window_width) // 2
        self.move(x_pos, int(self.current_y))

    def update_focus_handler(self):
        if self.focus_handler_id is not None:
            self.disconnect(self.focus_handler_id)
            self.focus_handler_id = None

        if self.hide_on_focus_loss:
            self.focus_handler_id = self.connect('focus-out-event', self.on_focus_out)

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

    def on_settings_clicked(self, button):
        # Create new settings dialog
        settings = self.get_settings()
        dialog = SettingsDialog(self, settings)
        
        # Emit signal that settings are opened
        self.emit('settings-opened')
        
        # Run dialog modally
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            new_settings = dialog.get_settings()
            self.apply_settings(new_settings)
            if hasattr(self, 'on_settings_changed'):
                self.on_settings_changed(new_settings)
        
        # Always destroy the dialog when done
        dialog.destroy()
        
        # Emit signal that settings are closed
        self.emit('settings-closed')

    def on_focus_out(self, widget, event):
        if self.hide_on_focus_loss:
            self.hide_window()
        return False

    def toggle_window(self):
        if self.animation_in_progress:
            return

        if self.hidden:
            self.show_all()
            self.hidden = False
            self.target_y = 0
            # If settings dialog is open, ensure it stays on top
            if self.settings_dialog:
                self.settings_dialog.present()
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
        x_pos = (self.screen_width - self.window_width) // 2
        self.move(x_pos, int(self.current_y))

        if progress >= 1.0:
            self.animation_in_progress = False
            if self.hidden:
                self.hide()
            return False
        return True

    def ease_in_out_quad(self, t: float) -> float:
        return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2

    def get_settings(self):
        from guakegpt.config.settings import Settings
        return Settings(
            width_percent=self.width_percent,
            height_percent=self.height_percent,
            animation_duration=self.animation_duration,
            hotkey="F12",  # This will be overwritten by the actual value from app
            hide_on_focus_loss=self.hide_on_focus_loss
        )

    def apply_settings(self, settings):
        # Store new settings
        self.width_percent = settings.width_percent
        self.height_percent = settings.height_percent
        self.animation_duration = settings.animation_duration
        self.hide_on_focus_loss = settings.hide_on_focus_loss

        # Update screen dimensions in case they changed
        self.update_screen_dimensions()
        
        # Calculate new dimensions
        old_height = self.window_height
        self.window_width = int(self.screen_width * self.width_percent / 100)
        self.window_height = int(self.screen_height * self.height_percent / 100)
        
        # Adjust current_y if height changed while window is visible
        if not self.hidden and old_height != self.window_height:
            self.current_y = 0
            self.target_y = 0
        elif self.hidden:
            self.current_y = -self.window_height
            self.target_y = -self.window_height
        
        # Update window size and position
        self.set_default_size(self.window_width, self.window_height)
        self.resize(self.window_width, self.window_height)
        x_pos = (self.screen_width - self.window_width) // 2
        self.move(x_pos, int(self.current_y))

        # Update focus-out handling
        self.update_focus_handler()

        # Force a redraw
        self.queue_draw()

    def on_send_message(self, widget):
        message = self.input_entry.get_text()
        if message:
            end_iter = self.chat_buffer.get_end_iter()
            self.chat_buffer.insert(end_iter, f"You: {message}\n")
            self.input_entry.set_text("") 