import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from guakegpt.config.settings import Settings

class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent, settings: Settings):
        super().__init__(
            title="GuakeGPT Settings",
            parent=parent,
            modal=True,
            destroy_with_parent=True,
            use_header_bar=True
        )
        
        # Add buttons to header bar
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        
        self.settings = settings
        self.set_default_size(400, 300)
        
        # Create settings grid
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_margin_start(10)
        grid.set_margin_end(10)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        
        # Window size settings
        width_label = Gtk.Label(label="Window Width (%)")
        self.width_spin = Gtk.SpinButton.new_with_range(20, 100, 5)
        self.width_spin.set_value(settings.width_percent)
        grid.attach(width_label, 0, 0, 1, 1)
        grid.attach(self.width_spin, 1, 0, 1, 1)
        
        height_label = Gtk.Label(label="Window Height (%)")
        self.height_spin = Gtk.SpinButton.new_with_range(20, 100, 5)
        self.height_spin.set_value(settings.height_percent)
        grid.attach(height_label, 0, 1, 1, 1)
        grid.attach(self.height_spin, 1, 1, 1, 1)
        
        # Animation duration
        anim_label = Gtk.Label(label="Animation Duration (ms)")
        self.anim_spin = Gtk.SpinButton.new_with_range(0, 1000, 50)
        self.anim_spin.set_value(settings.animation_duration)
        grid.attach(anim_label, 0, 2, 1, 1)
        grid.attach(self.anim_spin, 1, 2, 1, 1)
        
        # Hotkey setting
        hotkey_label = Gtk.Label(label="Toggle Hotkey")
        self.hotkey_entry = Gtk.Entry()
        self.hotkey_entry.set_text(settings.hotkey)
        grid.attach(hotkey_label, 0, 3, 1, 1)
        grid.attach(self.hotkey_entry, 1, 3, 1, 1)
        
        # Auto-hide setting
        self.autohide_check = Gtk.CheckButton(label="Hide on Focus Loss")
        self.autohide_check.set_active(settings.hide_on_focus_loss)
        grid.attach(self.autohide_check, 0, 4, 2, 1)
        
        # Add grid to dialog
        content_area = self.get_content_area()
        content_area.add(grid)
        self.show_all()
    
    def get_settings(self) -> Settings:
        return Settings(
            width_percent=int(self.width_spin.get_value()),
            height_percent=int(self.height_spin.get_value()),
            animation_duration=int(self.anim_spin.get_value()),
            hotkey=self.hotkey_entry.get_text(),
            hide_on_focus_loss=self.autohide_check.get_active()
        ) 