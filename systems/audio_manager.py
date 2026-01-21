import pygame
import os

class DummySound:
    def play(self, loops=0, maxtime=0, fade_ms=0): pass
    def stop(self): pass
    def set_volume(self, value): pass
    def get_volume(self): return 0.0

class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.mixer_initialized = True
        except Exception as e:
            print(f"Audio System Failed to Init: {e}")
            self.mixer_initialized = False
            
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        
        # Channels
        if self.mixer_initialized:
            self.ambient_channel = pygame.mixer.Channel(0) 
            self.step_channel = pygame.mixer.Channel(1)    
            self.action_channel = pygame.mixer.Channel(2)  
        else:
            self.ambient_channel = None
            self.step_channel = None
            self.action_channel = None
        
        # Procedural Music
        try:
            from systems.music_manager import MusicManager
            self.music = MusicManager(self)
        except ImportError:
            self.music = None
        
    def load_sound(self, name, filepath):
        """Load a sound effect safely."""
        if not self.mixer_initialized:
            self.sounds[name] = DummySound()
            return False
            
        try:
            if os.path.exists(filepath):
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(self.sfx_volume)
                self.sounds[name] = sound
                print(f"Loaded sound: {name}")
                return True
            else:
                print(f"Sound file not found: {filepath}")
                self.sounds[name] = DummySound() # Fallback
                return False
        except Exception as e:
            print(f"Failed to load sound {name}: {e}")
            self.sounds[name] = DummySound() # Fallback
            return False
    
    def play_sound(self, name, loops=0, channel=None, volume=None):
        """Play a sound effect."""
        if name in self.sounds:
            sound = self.sounds[name]
            if volume is not None:
                sound.set_volume(volume * self.sfx_volume)
            
            if channel:
                channel.play(sound, loops=loops)
            else:
                sound.play(loops=loops)
                
    def stop_sound(self, name):
        """Stop a specific sound."""
        if name in self.sounds:
            self.sounds[name].stop()
    
    def play_ambient(self, name, loops=-1):
        """Play ambient sound on dedicated channel."""
        if name in self.sounds:
            self.ambient_channel.play(self.sounds[name], loops=loops)
    
    def stop_ambient(self):
        """Stop ambient sounds."""
        self.ambient_channel.stop()
    
    def play_step(self):
        """Play footstep sound (non-overlapping)."""
        if not self.step_channel.get_busy():
            self.play_sound("step", channel=self.step_channel)
    
    def play_chop(self):
        """Play chop sound."""
        self.play_sound("chop", channel=self.action_channel)
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def generate_placeholder_sounds(self):
        """Generate simple placeholder sounds if audio files don't exist."""
        # This creates very basic beep sounds as placeholders
        # In production, you'd use actual audio files
        print("Using placeholder sounds (no audio files found)")
        
        # Create simple sine wave sounds
        try:
            # Chop sound (short click)
            chop_sound = pygame.mixer.Sound(buffer=self._generate_click())
            chop_sound.set_volume(self.sfx_volume)
            self.sounds["chop"] = chop_sound
            
            # Step sound (soft click)
            step_sound = pygame.mixer.Sound(buffer=self._generate_click(frequency=200, duration=0.1))
            step_sound.set_volume(self.sfx_volume * 0.3)
            self.sounds["step"] = step_sound
            
            # Ice Crack (high pitch sharp snap)
            ice_sound = pygame.mixer.Sound(buffer=self._generate_click(frequency=800, duration=0.4))
            ice_sound.set_volume(self.sfx_volume)
            self.sounds["ice_crack"] = ice_sound
            
            print("Placeholder sounds generated")
        except Exception as e:
            print(f"Could not generate placeholder sounds: {e}")
    
    def _generate_click(self, frequency=440, duration=0.15):
        """Generate a simple click sound."""
        try:
            import numpy as np
            sample_rate = 22050
            samples = int(sample_rate * duration)
            t = np.linspace(0, duration, samples, False)
            
            # Simple sine wave with envelope
            wave = np.sin(frequency * 2 * np.pi * t)
            envelope = np.exp(-t * 10)  # Decay envelope
            wave = wave * envelope * 0.3
            
            # Convert to 16-bit
            wave = (wave * 32767).astype(np.int16)
            
            # Stereo
            stereo_wave = np.column_stack((wave, wave))
            return stereo_wave.tobytes()
        except ImportError:
            # Simple square wave fallback without numpy
            import math
            import struct
            sample_rate = 22050
            samples = int(sample_rate * duration)
            buf = bytearray()
            for i in range(samples):
                t = i / sample_rate
                # Square wave
                val = 16000 if (int(t * frequency * 2) % 2 == 0) else -16000
                # Very simple linear decay envelope
                envelope = max(0, 1.0 - (t / duration))
                val = int(val * envelope * 0.3)
                # Pack as 16-bit signed little endian, stereo
                buf.extend(struct.pack('<hh', val, val))
            return bytes(buf)
