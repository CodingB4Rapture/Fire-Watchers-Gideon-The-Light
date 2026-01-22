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
        
        # Optimization: Cache light gradients
        # Key: (radius, color_tuple) -> Surface
        self.light_cache = {}
        
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
    
    def _get_cached_light_surf(self, radius, color):
        """Retrieve or create a cached gradient surface."""
        key = (radius, color)
        if key in self.light_cache:
            return self.light_cache[key]
        
        # Create new gradient surface
        surf = pygame.Surface((radius * 2, radius * 2))
        surf.fill(self.darkness_color) # Base darkness
        
        cx, cy = radius, radius
        steps = 20
        
        # Draw gradient circles
        for i in range(steps, 0, -1):
            step_radius = int(radius * (i / steps))
            intensity = (i / steps) ** 1.5
            
            r = int(min(255, self.darkness_color[0] + (255 - self.darkness_color[0]) * intensity))
            g = int(min(255, self.darkness_color[1] + (255 - self.darkness_color[1]) * intensity))
            b = int(min(255, self.darkness_color[2] + (255 - self.darkness_color[2]) * intensity))
            
            # Tint
            r = int(r * (color[0] / 255))
            g = int(g * (color[1] / 255))
            b = int(b * (color[2] / 255))
            
            if step_radius > 0:
                pygame.draw.circle(surf, (r, g, b), (cx, cy), step_radius)
                
        self.light_cache[key] = surf
        return surf

    def _draw_light(self, light):
        """Draw a single light source using cached surface."""
        radius = int(light.radius)
        if radius <= 0: return
        
        # Get cached surface
        light_surf = self._get_cached_light_surf(radius, light.color)
        
        # Blit centered at light position
        # We need to subtract radius to center top-left
        dest_x = int(light.x) - radius
        dest_y = int(light.y) - radius
        
        # Optimization: Don't blit special flags for individual lights onto darkness layer
        # Just simple blit, because the light surf includes the darkness color background
        # Actually, if we overlap lights, we might want MAX blend?
        # But simple replacement is faster and looks okay for separated lights.
        # Ideally we use ADD blend for lights overlap, but that requires black background.
        # Our base is dark blue. Let's use MAX or just blit. Blit is fastest.
        # But overlapping lights (torch + fire) should look brighter.
        
        # Let's try Special Flag BLEND_MAX to merge lights correctly in darkness
        self.light_layer.blit(light_surf, (dest_x, dest_y), special_flags=pygame.BLEND_MAX)
    
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
