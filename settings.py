import json
import os

class GameSettings:
    """Manages game settings with save/load functionality."""
    
    def __init__(self):
        self.settings_file = "settings.json"
        
        # Default settings
        self.defaults = {
            "audio": {
                "master_volume": 100,
                "music_volume": 80,
                "sfx_volume": 100,
                "muted": False
            },
            "graphics": {
                "display_mode": "Windowed",  # Windowed, Fullscreen, Borderless
                "resolution": "1280x720",
                "vsync": True,
                "show_fps": False,
                "particle_effects": True
            },
            "gameplay": {
                "difficulty": "Normal",  # Easy, Normal, Hard
                "tick_interval": 1.2,
                "starting_temperature": 0,
                "temperature_loss_rate": 1,
                "temperature_gain_rate": 1
            },
            "controls": {
                "move_up": "w",
                "move_down": "s",
                "move_left": "a",
                "move_right": "d",
                "toggle_fire": "f",
                "switch_tool": "tab",
                "action": "mouse1",
                "pause": "escape"
            }
        }
        
        self.settings = self.defaults.copy()
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new settings
                    for category in self.defaults:
                        if category in loaded:
                            self.settings[category].update(loaded[category])
        except Exception as e:
            print(f"Failed to load settings: {e}")
            self.settings = self.defaults.copy()
    
    def save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Failed to save settings: {e}")
            return False
    
    def get(self, category, key):
        """Get a specific setting value."""
        return self.settings.get(category, {}).get(key)
    
    def set(self, category, key, value):
        """Set a specific setting value."""
        if category in self.settings:
            self.settings[category][key] = value
            return True
        return False
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.settings = self.defaults.copy()
        self.save_settings()
