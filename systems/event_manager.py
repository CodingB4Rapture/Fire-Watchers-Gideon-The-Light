import random
import pygame

class EventManager:
    def __init__(self):
        self.active_event = None
        self.redemption_stage = 0
        self.npc_ref = None
        self.event_timer = 0.0
        self.warning_timer = 0.0
        self.is_warning = False
        
        # Event Settings
        self.COLD_SNAP_DURATION = 24.0  # 20 ticks * 1.2s = 24 seconds (CAPPED)
        self.WARNING_DURATION = 12.0  # 10 ticks * 1.2s = 12 seconds (TELEGRAPH)
        self.GRACE_PERIOD = 60.0  # 50 ticks * 1.2s = 60 seconds
        self.warning_ticks_remaining = 0
        
    def update(self, dt, run_state, audio_manager=None, camera=None):
        # Update zone timer for grace period
        if run_state:
            run_state.time_in_current_zone += dt
            
        if self.is_warning:
            self.warning_timer -= dt
            if self.warning_timer <= 0:
                self.is_warning = False
                self.trigger_cold_snap(run_state, audio_manager, camera)
        
        if self.active_event == "COLD_SNAP":
            self.event_timer -= dt
            if self.event_timer <= 0:
                self.active_event = None
                print("[EVENT] Cold Snap has ended.")
                
    def check_trigger(self, run_state):
        """Called every tick for random events."""
        if self.active_event or self.is_warning:
            return
        
        if run_state.current_zone_id == 0:
            return

        # GRACE PERIOD: No Cold Snaps for first 60 seconds in a zone
        if run_state and run_state.time_in_current_zone < self.GRACE_PERIOD:
            return
            
        if random.random() < 0.01: # 1% chance per tick
            self.start_warning()
            
    def start_warning(self):
        self.is_warning = True
        self.warning_timer = self.WARNING_DURATION
        print("[EVENT] Warning: Cold Snap approaching!")
        
    def trigger_cold_snap(self, run_state, audio_manager, camera=None):
        self.active_event = "COLD_SNAP"
        self.event_timer = self.COLD_SNAP_DURATION
        
        # Instant effects
        if run_state:
            run_state.body_temp -= 5.0
            
        # Screen shake
        if camera:
            camera.shake(5)
            
        # Audio
        if audio_manager:
            audio_manager.play_sound("wind", volume=1.0) # Play wind loop/gust
            
        print("[EVENT] COLD SNAP ACTIVE!")
        
    def render(self, screen, width, height):
        if self.is_warning:
            # Draw big warning text
            font = pygame.font.SysFont("Arial", 48, bold=True)
            text = "A COLD SNAP IS APPROACHING"
            color = (255, 100, 100) # Urgent Red
            
            # Pulsing effect
            import math
            alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.01))
            
            surf = font.render(text, True, color)
            surf.set_alpha(alpha)
            rect = surf.get_rect(center=(width // 2, height // 3))
            screen.blit(surf, rect)
            
            # TELEGRAPH: Wind streak particles
            # Draw horizontal wind streaks moving across screen
            streak_count = 15
            time = pygame.time.get_ticks() / 1000.0
            for i in range(streak_count):
                y = (i * (height // streak_count) + int(time * 50) % height) % height
                x_offset = (time * 300 + i * 50) % (width + 200) - 100
                # Draw wind streak (horizontal line)
                streak_length = 80 + (i % 3) * 20
                streak_alpha = int(100 + 50 * math.sin(time * 3 + i))
                streak_surf = pygame.Surface((streak_length, 3), pygame.SRCALPHA)
                streak_surf.fill((200, 220, 255, streak_alpha))
                screen.blit(streak_surf, (x_offset, y))
            
        if self.active_event == "COLD_SNAP":
            # Cyan tint
            overlay = pygame.Surface((width, height))
            overlay.fill((0, 50, 100)) # Cyan-blue
            screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            
            # Status text
            font = pygame.font.SysFont("Arial", 24, bold=True)
            text = f"COLD SNAP ACTIVE: {int(self.event_timer)}s"
            surf = font.render(text, True, (0, 200, 255))
            screen.blit(surf, (width // 2 - 100, 20))
