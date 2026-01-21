import pygame
import random
import math

class Camera:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Camera position (center point)
        self.x = 0
        self.y = 0
        
        # Smoothing parameters
        self.lerp_speed = 0.1  # How fast camera follows (0.1 = smooth, 1.0 = instant)
        
        # Look-ahead
        self.look_ahead_distance = 50  # Pixels to shift in movement direction
        self.look_ahead_x = 0
        self.look_ahead_y = 0
        self.look_ahead_lerp = 0.05  # Slower lerp for look-ahead (smoother)
        
        # Trauma system (screen shake)
        self.trauma = 0.0  # 0.0 to 1.0
        self.trauma_decay = 1.0  # Decay per second
        self.max_shake_offset = 20  # Maximum pixel offset from shake
        self.shake_angle = 0.1  # Maximum rotation in radians (not used for 2D offset, but available)
        
    def update(self, dt, target_x, target_y, player_velocity=None):
        """Update camera position to follow target with smoothing."""
        # Calculate look-ahead offset based on player velocity
        target_look_ahead_x = 0
        target_look_ahead_y = 0
        
        if player_velocity:
            # Normalize velocity and scale by look-ahead distance
            vel_length = math.sqrt(player_velocity[0]**2 + player_velocity[1]**2)
            if vel_length > 0.1:  # Only look ahead if moving
                target_look_ahead_x = (player_velocity[0] / vel_length) * self.look_ahead_distance
                target_look_ahead_y = (player_velocity[1] / vel_length) * self.look_ahead_distance
        
        # Smooth look-ahead transition
        self.look_ahead_x += (target_look_ahead_x - self.look_ahead_x) * self.look_ahead_lerp
        self.look_ahead_y += (target_look_ahead_y - self.look_ahead_y) * self.look_ahead_lerp
        
        # Target position with look-ahead
        final_target_x = target_x + self.look_ahead_x
        final_target_y = target_y + self.look_ahead_y
        
        # Lerp camera position toward target
        self.x += (final_target_x - self.x) * self.lerp_speed
        self.y += (final_target_y - self.y) * self.lerp_speed
        
        # Update trauma (decay)
        if self.trauma > 0:
            self.trauma -= self.trauma_decay * dt
            self.trauma = max(0, self.trauma)
    
    def add_trauma(self, amount):
        """Add screen shake trauma (0.0 to 1.0)."""
        self.trauma = min(1.0, self.trauma + amount)
    
    def shake(self, intensity):
        """Convenience method to add trauma based on intensity scale."""
        # Scale intensity so 10 is max trauma
        self.add_trauma(intensity / 10.0)
    
    def get_shake_offset(self):
        """Calculate screen shake offset based on trauma."""
        if self.trauma <= 0:
            return (0, 0)
        
        # Shake intensity is trauma squared (makes it more punchy)
        shake = self.trauma * self.trauma
        
        # Random offset in both directions
        offset_x = (random.random() * 2 - 1) * self.max_shake_offset * shake
        offset_y = (random.random() * 2 - 1) * self.max_shake_offset * shake
        
        return (int(offset_x), int(offset_y))
    
    def apply(self, world_x, world_y):
        """Convert world coordinates to screen coordinates with camera offset and shake."""
        shake_x, shake_y = self.get_shake_offset()
        
        # Center camera on screen
        screen_x = world_x - self.x + self.screen_width // 2 + shake_x
        screen_y = world_y - self.y + self.screen_height // 2 + shake_y
        
        return (screen_x, screen_y)
    
    def apply_rect(self, rect):
        """Apply camera transformation to a pygame.Rect."""
        screen_pos = self.apply(rect.x, rect.y)
        return pygame.Rect(screen_pos[0], screen_pos[1], rect.width, rect.height)
    
    def get_offset(self):
        """Get the current camera offset (for rendering backgrounds, etc)."""
        shake_x, shake_y = self.get_shake_offset()
        offset_x = -self.x + self.screen_width // 2 + shake_x
        offset_y = -self.y + self.screen_height // 2 + shake_y
        return (offset_x, offset_y)
