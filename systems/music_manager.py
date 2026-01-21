import pygame
import numpy as np
import threading
import time

class MusicManager:
    def __init__(self, audio_manager):
        self.audio_manager = audio_manager
        self.sample_rate = 22050
        self.volume = 0.4
        self.current_theme = None
        self.theme_thread = None
        self.stop_event = threading.Event()
        
        # Chord frequencies (Key of G Major)
        self.CHORDS = {
            "G": [196.00, 246.94, 293.66],
            "EM": [164.81, 196.00, 246.94],
            "C": [130.81, 164.81, 196.00],
            "D": [146.83, 185.00, 220.00]
        }
        
    def _generate_tone(self, frequencies, duration=2.0, fade=0.5):
        """Generates a soft, pad-like chord."""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # Mix frequencies
        wave = np.zeros(samples)
        for f in frequencies:
            # Main wave
            wave += np.sin(2 * np.pi * f * t)
            # Add subtle harmonics for warmth
            wave += 0.5 * np.sin(2 * np.pi * f * 2 * t)
            wave += 0.25 * np.sin(2 * np.pi * f * 0.5 * t)
            
        wave = wave / len(frequencies)
        
        # Apply envelope (Soft attack and long decay)
        attack = int(self.sample_rate * 0.5)
        decay = int(self.sample_rate * fade)
        envelope = np.ones(samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-decay:] = np.linspace(1, 0, decay)
        
        wave = wave * envelope * 0.3
        
        # Convert to 16-bit
        wave = (wave * 32767).astype(np.int16)
        
        # Stereo
        stereo_wave = np.column_stack((wave, wave))
        return pygame.mixer.Sound(buffer=stereo_wave.tobytes())

    def start_theme(self):
        """Starts the procedural theme loop in a background thread."""
        if self.theme_thread and self.theme_thread.is_alive():
            return
            
        self.stop_event.clear()
        self.theme_thread = threading.Thread(target=self._music_loop, daemon=True)
        self.theme_thread.start()
        print("[MUSIC] Theme Loop Started")

    def stop_theme(self):
        self.stop_event.set()
        if self.theme_thread:
            self.theme_thread.join(timeout=1.0)
            
    def _music_loop(self):
        """The actual sequence logic."""
        # Progression 1: G, Em, C, D
        # Progression 2: G, C, D, Em
        p1 = ["G", "EM", "C", "D"]
        p2 = ["G", "C", "D", "EM"]
        
        sequences = [p1, p2]
        seq_index = 0
        
        while not self.stop_event.is_set():
            seq = sequences[seq_index]
            for chord_name in seq:
                if self.stop_event.is_set(): break
                
                # Generate/Get chord
                chord_sound = self._generate_tone(self.CHORDS[chord_name], duration=3.0)
                chord_sound.set_volume(self.audio_manager.music_volume)
                chord_sound.play()
                
                # Wait for next chord (with overlap)
                time.sleep(2.5) 
                
            seq_index = (seq_index + 1) % len(sequences)
            # Short break between sequences
            time.sleep(1.0)

    def play_win_jingle(self):
        """Plays a nice completion jingle."""
        # Rapid arpeggio of G Major 9
        freqs = [196.00, 246.94, 293.66, 392.00, 493.88] # G3, B3, D4, G4, B4
        samples = int(self.sample_rate * 1.5)
        t = np.linspace(0, 1.5, samples, False)
        wave = np.zeros(samples)
        
        for i, f in enumerate(freqs):
            start = int(i * 0.1 * self.sample_rate)
            duration_samples = samples - start
            if duration_samples <= 0: continue
            
            t_sub = t[:duration_samples]
            # Chiming tone
            sub_wave = np.sin(2 * np.pi * f * t_sub) * np.exp(-t_sub * 4)
            wave[start:start+duration_samples] += sub_wave * 0.4
            
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        jingle = pygame.mixer.Sound(buffer=stereo_wave.tobytes())
        jingle.set_volume(self.audio_manager.sfx_volume)
        jingle.play()
