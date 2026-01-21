import pygame
import random

class SnowParticle:
    def __init__(self, x, y, dx, dy, size=1):
        self.x = x
        self.y = y
        self.dx = dx  # Horizontal velocity (wind)
        self.dy = dy  # Vertical velocity (fall)
        self.size = size
        self.alpha = random.randint(150, 255)
        
    def update(self, dt, wind_multiplier=1.0):
        """Update particle position with wind effect."""
        self.x += self.dx * wind_multiplier * dt * 60  # Scale by 60 for frame-independent
        self.y += self.dy * dt * 60
        
    def is_offscreen(self, screen_width, screen_height):
        """Check if particle has left the screen."""
        return (self.y > screen_height or 
                self.x < -10 or 
                self.x > screen_width + 10)

class WeatherSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Particles
        self.particles = []
        self.max_particles = 300
        self.spawn_rate = 5  # Particles per frame
        
        # Wind configuration (set by zone)
        self.base_dx = 0  # Base horizontal wind
        self.base_dy = 2  # Base vertical fall
        
        # Gusting system
        self.gust_timer = 0.0
        self.gust_interval = 10.0  # Gust every 10 seconds
        self.gust_duration = 2.0   # Gust lasts 2 seconds
        self.is_gusting = False
        self.gust_time_remaining = 0.0
        self.gust_multiplier = 2.0  # Wind doubles during gust
        
        # Current wind multiplier
        self.current_wind_multiplier = 1.0
        
    def set_zone_weather(self, zone_id):
        """Configure weather based on zone."""
        if zone_id == 1:
            # Zone 1: Gentle fall
            self.base_dx = 0
            self.base_dy = 2
            self.spawn_rate = 3
            print(f"Weather: Gentle snow (Zone {zone_id})")
        elif zone_id == 2:
            # Zone 2: Hard wind
            self.base_dx = -3
            self.base_dy = 4
            self.spawn_rate = 6
            print(f"Weather: Harsh blizzard (Zone {zone_id})")
        else:
            # Default
            self.base_dx = 0
            self.base_dy = 2
            self.spawn_rate = 3
    
    def update(self, dt, audio_manager=None):
        """Update weather particles and gusting."""
        # Update gust timer
        self.gust_timer += dt
        
        # Check for gust trigger
        if not self.is_gusting and self.gust_timer >= self.gust_interval:
            self.trigger_gust()
            self.gust_timer = 0.0
            
            # Audio hook: Increase wind volume during gust
            if audio_manager and "wind" in audio_manager.sounds:
                audio_manager.ambient_channel.set_volume(1.0)
        
        # Update gust state
        if self.is_gusting:
            self.gust_time_remaining -= dt
            if self.gust_time_remaining <= 0:
                self.end_gust()
                
                # Audio hook: Return wind to normal volume
                if audio_manager and "wind" in audio_manager.sounds:
                    audio_manager.ambient_channel.set_volume(0.5)
        
        # Spawn new particles
        for _ in range(self.spawn_rate):
            if len(self.particles) < self.max_particles:
                self.spawn_particle()
        
        # Update existing particles
        for particle in self.particles[:]:
            particle.update(dt, self.current_wind_multiplier)
            
            # Remove offscreen particles
            if particle.is_offscreen(self.screen_width, self.screen_height):
                self.particles.remove(particle)
    
    def spawn_particle(self):
        """Spawn a new snow particle at the top of the screen."""
        x = random.randint(-50, self.screen_width + 50)
        y = random.randint(-20, 0)
        
        # Slight variation in particle velocity
        dx = self.base_dx + random.uniform(-0.5, 0.5)
        dy = self.base_dy + random.uniform(-0.3, 0.3)
        
        # Vary particle size slightly
        size = random.choice([1, 1, 1, 2])  # Mostly 1px, occasionally 2px
        
        particle = SnowParticle(x, y, dx, dy, size)
        self.particles.append(particle)
    
    def trigger_gust(self):
        """Trigger a wind gust."""
        self.is_gusting = True
        self.gust_time_remaining = self.gust_duration
        self.current_wind_multiplier = self.gust_multiplier
        print("GUST! Wind intensifies...")
    
    def end_gust(self):
        """End the wind gust."""
        self.is_gusting = False
        self.current_wind_multiplier = 1.0
        print("Gust subsides...")
    
    def render(self, surface):
        """Render snow particles."""
        for particle in self.particles:
            # Draw particle as a small white circle or rect
            color = (255, 255, 255, particle.alpha)
            
            if particle.size == 1:
                # Single pixel
                if 0 <= particle.x < self.screen_width and 0 <= particle.y < self.screen_height:
                    surface.set_at((int(particle.x), int(particle.y)), color[:3])
            else:
                # Larger snowflake
                pygame.draw.circle(surface, color[:3], 
                                 (int(particle.x), int(particle.y)), 
                                 particle.size)
    
    def clear(self):
        """Remove all particles (for zone transitions)."""
        self.particles.clear()
