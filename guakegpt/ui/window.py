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

        # Window setup - creates a borderless window that appears above other windows
        self.set_decorated(False)  # Remove window decorations (title bar, etc.)
        self.set_skip_taskbar_hint(True)  # Don't show in taskbar
        self.set_skip_pager_hint(True)  # Don't show in pager
        self.set_keep_above(True)  # Keep window on top
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)  # Normal window type for proper focus handling
        self.set_can_focus(True)  # Enable window focus for focus-out detection
        self.connect('focus-out-event', self.on_focus_out)  # Hide window when focus is lost

        # Store settings that control window behavior
        self.width_percent = width_percent  # Window width as percentage of screen width
        self.height_percent = height_percent  # Window height as percentage of screen height
        self.animation_duration = animation_duration  # Duration of show/hide animation in ms
        self.hide_on_focus_loss = hide_on_focus_loss  # Whether to hide window when focus is lost
        self.hidden = True  # Track window visibility state
        self.animation_in_progress = False  # Prevent multiple animations running simultaneously
        self.settings_dialog = None  # Track settings dialog state
        self.on_settings_changed = None  # Callback for when settings are changed

        # Initialize window dimensions based on screen size
        self.update_screen_dimensions()
        self.window_width = int(self.screen_width * self.width_percent / 100)
        self.window_height = int(self.screen_height * self.height_percent / 100)
        
        # Initialize animation properties - window starts hidden above screen
        self.current_y = -self.window_height
        self.target_y = -self.window_height
        self.update_window_dimensions()

        # Setup UI layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.main_box)

        # Add settings button in header
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        settings_button = Gtk.Button()
        settings_button.set_relief(Gtk.ReliefStyle.NONE)
        settings_icon = Gtk.Image.new_from_icon_name("preferences-system", Gtk.IconSize.SMALL_TOOLBAR)
        settings_button.add(settings_icon)
        settings_button.connect("clicked", self.on_settings_clicked)
        header_box.pack_end(settings_button, False, False, 5)
        self.main_box.pack_start(header_box, False, False, 5)

        # Setup chat interface with message history and input
        self.setup_chat_interface()

    def update_screen_dimensions(self):
        """Get the primary monitor dimensions for window sizing"""
        screen = self.get_screen()
        monitor = screen.get_primary_monitor()
        geometry = screen.get_monitor_geometry(monitor)
        self.screen_width = geometry.width
        self.screen_height = geometry.height

    def update_window_dimensions(self):
        """Update window size and position based on screen dimensions and settings"""
        # Calculate new dimensions as percentage of screen size
        self.window_width = int(self.screen_width * self.width_percent / 100)
        self.window_height = int(self.screen_height * self.height_percent / 100)
        
        self.set_default_size(self.window_width, self.window_height)
        self.resize(self.window_width, self.window_height)
        
        # Update animation positions if window is hidden
        if self.hidden:
            self.target_y = -self.window_height
            self.current_y = -self.window_height
        
        # Center window horizontally
        x_pos = (self.screen_width - self.window_width) // 2
        self.move(x_pos, int(self.current_y))

    def setup_chat_interface(self):
        """Create the chat interface with message history view and input field"""
        # Message history view
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.chat_buffer = Gtk.TextBuffer()
        self.chat_view = Gtk.TextView(buffer=self.chat_buffer)
        self.chat_view.set_editable(False)
        self.chat_view.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled.add(self.chat_view)
        self.main_box.pack_start(scrolled, True, True, 0)

        # Message input area
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.input_entry = Gtk.Entry()
        self.input_entry.set_placeholder_text("Type your message here...")  # Add placeholder text
        self.input_entry.connect('activate', self.on_send_message)  # Send on Enter
        send_button = Gtk.Button.new_with_label("Send")
        send_button.connect('clicked', self.on_send_message)

        input_box.pack_start(self.input_entry, True, True, 5)
        input_box.pack_start(send_button, False, False, 5)
        self.main_box.pack_start(input_box, False, False, 5)

    def on_settings_clicked(self, button):
        """Handle settings button click by showing settings dialog"""
        # Store current visibility state
        was_visible = not self.hidden
        
        settings = self.get_settings()
        dialog = SettingsDialog(self, settings)
        self.settings_dialog = dialog
        
        self.emit('settings-opened')
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            new_settings = dialog.get_settings()
            self.apply_settings(new_settings)
            if self.on_settings_changed:
                self.on_settings_changed(new_settings)
        
        dialog.destroy()
        self.settings_dialog = None
        self.emit('settings-closed')

        # Restore previous visibility state
        if was_visible and self.hidden:
            self.toggle_window()

    def on_focus_out(self, widget, event):
        """Hide window when it loses focus (if enabled in settings)"""
        if self.hide_on_focus_loss and not self.hidden and not self.settings_dialog:
            self.toggle_window()
        return False

    def toggle_window(self):
        """Show or hide window with animation"""
        if self.animation_in_progress:
            return

        if self.hidden:
            self.show_all()
            self.hidden = False
            self.target_y = 0  # Animate down to visible
            # Set focus to input entry when window shows
            self.input_entry.grab_focus()
            if self.settings_dialog:
                self.settings_dialog.present()
        else:
            self.target_y = -self.window_height  # Animate up to hide
            self.hidden = True

        self.start_animation()

    def start_animation(self):
        """Start the show/hide animation"""
        self.animation_in_progress = True
        self.animation_start_time = time.time() * 1000
        self.animation_start_y = self.current_y
        GLib.timeout_add(16, self.animate_step)  # ~60 FPS animation

    def animate_step(self):
        """Perform one step of the show/hide animation"""
        current_time = time.time() * 1000
        progress = min(1.0, (current_time - self.animation_start_time) / self.animation_duration)
        
        # Apply easing for smooth animation
        progress = self.ease_in_out_quad(progress)
        
        # Update window position
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
        """Quadratic easing function for smooth animation"""
        return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2

    def get_settings(self):
        """Get current window settings"""
        from guakegpt.config.settings import Settings
        return Settings(
            width_percent=self.width_percent,
            height_percent=self.height_percent,
            animation_duration=self.animation_duration,
            hotkey="F12",
            hide_on_focus_loss=self.hide_on_focus_loss
        )

    def apply_settings(self, settings):
        """Apply new settings and update window accordingly"""
        # Update stored settings
        self.width_percent = settings.width_percent
        self.height_percent = settings.height_percent
        self.animation_duration = settings.animation_duration
        self.hide_on_focus_loss = settings.hide_on_focus_loss

        # Recalculate window dimensions
        self.update_screen_dimensions()
        old_height = self.window_height
        self.window_width = int(self.screen_width * self.width_percent / 100)
        self.window_height = int(self.screen_height * self.height_percent / 100)
        
        # Adjust window position based on visibility
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

        self.queue_draw()

    def on_send_message(self, widget):
        """Handle sending a message"""
        message = self.input_entry.get_text()
        if message:
            # Get current timestamp
            timestamp = time.strftime("%H:%M:%S")
            
            # Update chat buffer
            end_iter = self.chat_buffer.get_end_iter()
            self.chat_buffer.insert(end_iter, f"[{timestamp}] You: {message}\n")
            
            # Log to console with timestamp
            print(f"[{timestamp}] Message sent: {message}")
            
            self.input_entry.set_text("") 