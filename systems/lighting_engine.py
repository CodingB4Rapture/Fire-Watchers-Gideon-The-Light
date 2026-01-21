import pygame
import random
import math

class LightSource:
    def __init__(self, x, y, radius, color=(255, 220, 180), flicker_strength=0.0):
        self.x = x
        self.y = y
        self.base_radius = radius
        self.radius = radius
        self.color = color
        self.flicker_strength = flicker_strength
        self.flicker_timer = 0.0
        self.flicker_offset = 0
        
    def update(self, dt):
        """Update light flickering."""
        if self.flicker_strength > 0:
            self.flicker_timer += dt
            if self.flicker_timer >= 0.1:  # Flicker every 0.1 seconds
                self.flicker_timer = 0
                # Random flicker offset
                self.flicker_offset = random.randint(-int(self.flicker_strength), int(self.flicker_strength))
                self.radius = max(10, self.base_radius + self.flicker_offset)

class LightingEngine:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Darkness layer (will be multiplied with scene)
        self.light_layer = pygame.Surface((screen_width, screen_height))
        self.darkness_color = (10, 10, 30)  # Dark blue-black
        
        # Light sources
        self.lights = []
        
    def clear_lights(self):
        """Remove all light sources."""
        self.lights.clear()
    
    def add_light(self, x, y, radius, color=(255, 220, 180), flicker_strength=0):
        """Add a light source."""
        light = LightSource(x, y, radius, color, flicker_strength)
        self.lights.append(light)
        return light
    
    def update(self, dt):
        """Update all light sources (flickering, etc)."""
        for light in self.lights:
            light.update(dt)
    
    def render(self, target_surface):
        """Render lighting layer onto target surface."""
        # Fill with darkness
        self.light_layer.fill(self.darkness_color)
        
        # Draw each light source
        for light in self.lights:
            self._draw_light(light)
        
        # Apply lighting layer using multiply blend
        target_surface.blit(self.light_layer, (0, 0), special_flags=pygame.BLEND_MULT)
    
    def _draw_light(self, light):
        """Draw a single light source with radial gradient."""
        # Create a gradient from bright center to dark edges
        # We'll draw multiple circles with decreasing alpha
        
        # Number of gradient steps
        steps = 20
        
        for i in range(steps, 0, -1):
            # Calculate radius and intensity for this step
            step_radius = int(light.radius * (i / steps))
            
            # Intensity falls off with distance (inverse square-ish)
            intensity = (i / steps) ** 1.5  # Power curve for softer falloff
            
            # Calculate color with intensity
            r = int(min(255, self.darkness_color[0] + (255 - self.darkness_color[0]) * intensity))
            g = int(min(255, self.darkness_color[1] + (255 - self.darkness_color[1]) * intensity))
            b = int(min(255, self.darkness_color[2] + (255 - self.darkness_color[2]) * intensity))
            
            # Tint with light color
            r = int(r * (light.color[0] / 255))
            g = int(g * (light.color[1] / 255))
            b = int(b * (light.color[2] / 255))
            
            if step_radius > 0:
                pygame.draw.circle(self.light_layer, (r, g, b), 
                                 (int(light.x), int(light.y)), step_radius)
    
    def add_fire_light(self, x, y, fuel_percent=1.0):
        """Add a flickering fire light source."""
        # Fire light properties
        base_radius = 150 + (fuel_percent * 50)  # Larger fires = more light
        flicker = 15  # Flicker strength
        
        # Warm orange-yellow color
        color = (255, 180, 100)
        
        return self.add_light(x, y, base_radius, color, flicker)
    
    def add_player_light(self, x, y):
        """Add player's personal light (small, steady)."""
        # Small personal light so player is always visible
        return self.add_light(x, y, 80, (200, 200, 220), flicker_strength=2)
    
    def add_torch_light(self, x, y):
        """Add torch light (medium, flickering)."""
        return self.add_light(x, y, 100, (255, 200, 150), flicker_strength=8)
