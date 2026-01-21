import pygame
import random
import math

def generate_rock_tile(size=64):
    """Generates a 64x64 pixelated rock texture with rustic mountain feel."""
    tile = pygame.Surface((size, size))
    # Lighter, warmer base color for rustic mountain/fall vibe
    base_color = (85, 90, 95)  # Much lighter gray
    tile.fill(base_color)
    
    # Add noise / clumps with warmer tones
    for _ in range(20):
        shade = random.randint(-15, 20)  # More variation toward lighter
        c = (max(0, min(255, base_color[0] + shade)),
             max(0, min(255, base_color[1] + shade)),
             max(0, min(255, base_color[2] + shade)))
        
        w = random.randint(4, 16)
        h = random.randint(4, 16)
        x = random.randint(0, size-w)
        y = random.randint(0, size-h)
        pygame.draw.rect(tile, c, (x, y, w, h))
        
    # Add some "cracks" (less dark)
    for _ in range(5):
        shade = -15  # Less harsh
        c = (max(0, min(255, base_color[0] + shade)),
             max(0, min(255, base_color[1] + shade)),
             max(0, min(255, base_color[2] + shade)))
        x1, y1 = random.randint(0, size), random.randint(0, size)
        x2, y2 = x1 + random.randint(-10, 10), y1 + random.randint(-10, 10)
        pygame.draw.line(tile, c, (x1, y1), (x2, y2), 2)
        
    return tile

def generate_background_surface(width, height):
    """Creates a pre-tiled background surface."""
    bg = pygame.Surface((width, height))
    tile = generate_rock_tile()
    for y in range(0, height, 64):
        for x in range(0, width, 64):
            bg.blit(tile, (x, y))
    
    # Very subtle vignette (much lighter)
    overlay = pygame.Surface((width, height))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(40)  # Much lighter overlay
    bg.blit(overlay, (0, 0))
    
    return bg
class Tree:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 80) # Visual rect (approx)
        self.hitbox = pygame.Rect(x + 12, y + 68, 16, 12) # Collision base (smaller footprint)
        self.health = 3
        
        # States
        self.STATE_FULL = 0
        self.STATE_STUMP = 1
        self.STATE_SAPLING = 2
        self.state = self.STATE_FULL
        self.regrow_timer = 0
        
        self.image = None
        self.stump_image = None
        
        # Impact juice
        self.shake_timer = 0.0
        self.shake_duration = 0.2
        self.shake_amplitude = 3
        self.flash_frames = 0
        
        # Precise collision hitbox (bottom 20% of sprite, trunk only)
        # Precise collision hitbox (The Snap)
        # Hardcoded to Trunk/Stump (x+10, y+40, w20, h40)
        self.stump_rect = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 40,
            20,
            40
        )
        
        self._generate_images()
        
    def _generate_images(self):
        # Generate Pine Tree Image
        self.image = pygame.Surface((40, 80), pygame.SRCALPHA)
        self.stump_image = pygame.Surface((40, 80), pygame.SRCALPHA)
        
        # Colors
        trunk_color = (60, 40, 30)
        leaf_color = (30, 60, 30)
        highlight = (40, 70, 40)
        snow_color = (220, 230, 240)
        
        pixel_size = 4
        
        # === TRUNK ===
        pygame.draw.rect(self.image, trunk_color, (16, 60, 8, 20)) # Base
        pygame.draw.rect(self.image, trunk_color, (16, 20, 8, 40)) # Core
        
        # === LEAVES (Layers) ===
        # Bottom Layer
        pygame.draw.polygon(self.image, leaf_color, [(0, 60), (20, 30), (40, 60)])
        pygame.draw.polygon(self.image, snow_color, [(0, 60), (20, 30), (40, 60)], 2) # Snow edge
        
        # Middle Layer
        pygame.draw.polygon(self.image, leaf_color, [(4, 45), (20, 15), (36, 45)])
        
        # Top Layer
        pygame.draw.polygon(self.image, leaf_color, [(8, 30), (20, 0), (32, 30)])
        # Snow Cap
        pygame.draw.polygon(self.image, snow_color, [(14, 10), (20, 0), (26, 10)])

        # === STUMP IMAGE ===
        pygame.draw.rect(self.stump_image, trunk_color, (16, 60, 8, 12)) # Short trunk
        pygame.draw.ellipse(self.stump_image, (80, 60, 40), (16, 60, 8, 4)) # Cut top ring
        
    def take_impact(self):
        """Visual-only impact logic for exhausted resources."""
        self.shake_timer = self.shake_duration
        self.flash_frames = 1

    def take_damage(self):
        """Returns number of logs dropped (3 if felled, 0 otherwise)."""
        if self.state != self.STATE_FULL: return 0
        self.health -= 1
        
        # Trigger impact effects
        self.shake_timer = self.shake_duration
        self.flash_frames = 1
        
        if self.health <= 0:
            self.state = self.STATE_STUMP
            self.regrow_timer = 0
            return 3 # Drop 3 Logs
        return 0
    
    def update_tick(self):
        """Called by TickSystem to handle regrowth."""
        if self.state == self.STATE_STUMP:
            self.regrow_timer += 1
            if self.regrow_timer >= 50:
                self.state = self.STATE_SAPLING
                self.regrow_timer = 0
        elif self.state == self.STATE_SAPLING:
            self.regrow_timer += 1
            if self.regrow_timer >= 100:
                self.state = self.STATE_FULL
                self.regrow_timer = 0
                self.health = 3
    
    def update(self, dt):
        """Update tree animations (shake, flash)."""
        # Update shake timer
        if self.shake_timer > 0:
            self.shake_timer -= dt
        # Update flash
        if self.flash_frames > 0:
            self.flash_frames -= 1

    def render(self, surface):
        img = self.stump_image if self.state == self.STATE_STUMP else self.image
        
        # Determine source image and scaling
        if self.state == self.STATE_STUMP:
            img = self.stump_image
        elif self.state == self.STATE_SAPLING:
            orig_w, orig_h = self.image.get_size()
            img = pygame.transform.scale(self.image, (orig_w // 2, orig_h // 2))
        else:
            img = self.image
            
        shake_x = 0
        if self.shake_timer > 0:
            progress = 1.0 - (self.shake_timer / self.shake_duration)
            shake_x = math.sin(progress * math.pi * 8) * self.shake_amplitude * (self.shake_timer / self.shake_duration)
        
        render_pos = (self.rect.x + shake_x, self.rect.y)
        if self.state == self.STATE_SAPLING:
            render_pos = (self.rect.x + 10 + shake_x, self.rect.y + 40)
        
        # Update stump_rect to match current position
        trunk_height = int(self.rect.height * 0.2)
        trunk_width = int(self.rect.width * 0.5)
        self.stump_rect.x = self.rect.x + (self.rect.width - trunk_width) // 2
        self.stump_rect.y = self.rect.bottom - trunk_height
            
        if self.flash_frames > 0:
            flash_img = img.copy()
            flash_img.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_ADD)
            surface.blit(flash_img, render_pos)
        else:
            surface.blit(img, render_pos)

class Stick:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x-16, y-16, 32, 32) # Interaction area
        self.consumed = False
        self.angle = random.randint(0, 360)
        
    def render(self, surface):
        if self.consumed: return
        # Draw a small stick (line)
        length = 12
        rad = math.radians(self.angle)
        x2 = self.pos.x + length * math.cos(rad)
        y2 = self.pos.y + length * math.sin(rad)
        # Pixelated look (thick lines)
        pygame.draw.line(surface, (90, 60, 40), (self.pos.x, self.pos.y), (x2, y2), 4)
        # Highlight (inner line)
        pygame.draw.line(surface, (130, 100, 70), (self.pos.x + 1, self.pos.y + 1), (x2 - 1, y2 - 1), 2)

class DeadfallPile:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x-30, y-30, 60, 60) # Large interaction
        self.sticks_remaining = 5
        self.regrow_timer = 0
        
    def render(self, surface):
        # Draw a mulch/dirt patch
        pygame.draw.ellipse(surface, (45, 35, 25), (self.pos.x-24, self.pos.y-12, 48, 24))
        
        if self.sticks_remaining <= 0:
             return
             
        # Draw a pile of crossed sticks
        for i in range(self.sticks_remaining):
             angle = i * 45 + (i * 10)
             length = 24
             rad = math.radians(angle)
             x1 = self.pos.x - (length/2) * math.cos(rad)
             y1 = self.pos.y - (length/2) * math.sin(rad)
             x2 = self.pos.x + (length/2) * math.cos(rad)
             y2 = self.pos.y + (length/2) * math.sin(rad)
             pygame.draw.line(surface, (110, 80, 50), (x1, y1), (x2, y2), 4)
             pygame.draw.line(surface, (80, 50, 20), (x1, y1), (x2, y2), 1)

    def take_stick(self):
        if self.sticks_remaining > 0:
            self.sticks_remaining -= 1
            return True
        return False

    def update_tick(self):
        if self.sticks_remaining < 5:
            self.regrow_timer += 1
            if self.regrow_timer >= 120: # Regrow stick every 120 ticks
                self.sticks_remaining += 1
                self.regrow_timer = 0

class Particle:
    def __init__(self, x, y, color, size=4):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2) * 60
        self.vy = random.uniform(-4, -1) * 60 # Explode up
        self.life = random.uniform(0.3, 0.6)
        self.color = color
        self.gravity = 500
        self.size = size
        
    def update(self, dt, ground_y=720):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Bounce on ground
        if self.y >= ground_y - 5:
            self.y = ground_y - 5
            self.vy *= -0.5  # Bounce with energy loss
            self.vx *= 0.8   # Friction
            
            # Stop bouncing if too slow
            if abs(self.vy) < 50:
                self.vy = 0
        
        self.life -= dt
        return self.life > 0
        
    def render(self, surface, offset=(0,0)):
        if self.life > 0:
            rx = int(self.x + offset[0])
            ry = int(self.y + offset[1])
            pygame.draw.rect(surface, self.color, (rx, ry, self.size, self.size))

class LeafParticle(Particle):
    def __init__(self, x, y):
        # Green leaf colors
        color = random.choice([(34, 139, 34), (0, 100, 0), (50, 205, 50)])
        super().__init__(x, y, color)
        self.vx = random.uniform(-1, 1) * 30
        self.vy = random.uniform(40, 80)
        self.life = random.uniform(1.2, 2.5)
        import math
        self.timer = random.uniform(0, math.pi * 2)
        self.gravity = 0 # Drift slowly
        
    def update(self, dt, ground_y=720):
        import math
        self.timer += dt * 5
        self.x += (self.vx + math.sin(self.timer) * 60) * dt
        self.y += self.vy * dt
        
        self.life -= dt
        return self.life > 0

class DustParticle(Particle):
    def __init__(self, x, y):
        color = random.choice([(180, 180, 180, 150), (200, 200, 200, 150)]) # Dusty gray
        super().__init__(x, y, color)
        self.vx = random.uniform(-1, 1) * 30
        self.vy = random.uniform(-40, -20)
        self.life = random.uniform(0.3, 0.5)
        self.gravity = 150
        
    def update(self, dt, ground_y=720):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        return self.life > 0
    
    def render(self, surface):
        if self.life > 0:
            # Draw smaller and slightly transparent
            size = int(self.life * 10)
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill(self.color)
            surface.blit(s, (int(self.x), int(self.y)))

class Campfire:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32) # Fire center
        # Bigger Log Chest (To right of fire)
        self.box_rect = pygame.Rect(x + 40, y - 10, 42, 36) 
        self.fuel = 30.0 # Seconds of burn time
        self.max_fuel = 120.0
        self.anim_timer = 0.0
        self.frame = 0
        self.is_tutorial_fire = False  # Tutorial fires never extinguish
        
    def add_fuel(self, amount=30.0):
        self.fuel = min(self.max_fuel, self.fuel + amount)
        print(f"Fire fueled! Time: {self.fuel:.1f}s")
        
    def update(self, dt):
        # Tutorial fires never run out
        if self.is_tutorial_fire:
            self.fuel = 100.0
            self.anim_timer += dt
            if self.anim_timer > 0.1:
                self.anim_timer = 0
                self.frame = (self.frame + 1) % 4
            return True
            
        if self.fuel > 0:
            self.fuel -= dt
            self.anim_timer += dt
            if self.anim_timer > 0.1:
                self.anim_timer = 0
                self.frame = (self.frame + 1) % 4
            return True 
        return True 
        
    def render(self, surface):
        # Draw BIG Log Chest
        # Draw rear/inside
        pygame.draw.rect(surface, (60, 45, 30), self.box_rect) 
        pygame.draw.rect(surface, (50, 35, 20), self.box_rect, 3) 
        
        # Draw "logs" stacked inside based on fuel
        stack_height = 0
        if self.fuel > 10: stack_height = 1
        if self.fuel > 50: stack_height = 2
        if self.fuel > 90: stack_height = 3
        
        for i in range(stack_height):
            # Log visual
            ly = self.box_rect.bottom - 10 - (i * 8)
            pygame.draw.rect(surface, (140, 100, 60), (self.box_rect.x + 6, ly, 30, 6))
            pygame.draw.circle(surface, (160, 120, 80), (self.box_rect.x + 6, ly + 3), 3) # knot
            
        # Draw Fire Pit
        cx, cy = self.rect.centerx, self.rect.centery
        
        # Stones/Ash
        pygame.draw.circle(surface, (50, 50, 50), (cx, cy + 10), 14)
        pygame.draw.circle(surface, (20, 20, 20), (cx, cy + 10), 10) # inner ash
        
        # Fire Animation
        if self.fuel > 0:
            colors = [(255, 100, 0), (255, 180, 0), (255, 220, 100)]
            # Procedural flame shape based on frame
            offsets = [
                [(0, -10), (-6, 0), (6, 0)],
                [(0, -12), (-5, -2), (5, -2)],
                [(0, -8), (-7, 2), (7, 2)],
                [(-2, -14), (-4, -4), (4, -4)]
            ]
            pts = offsets[self.frame]
            
            # Central Flame
            pygame.draw.circle(surface, colors[1], (cx, cy), 8 + (self.frame % 2))
            pygame.draw.circle(surface, colors[2], (cx, cy + 2), 4)
            
            # Flickers
            for ox, oy in pts:
                pygame.draw.circle(surface, colors[0], (cx + ox, cy + oy), 4)
                
            # Light Glow (Subtle)
            # s = pygame.Surface((64, 64), pygame.SRCALPHA)
            # pygame.draw.circle(s, (255, 150, 50, 30), (32, 32), 30)
            # surface.blit(s, (cx-32, cy-32))

            # surface.blit(s, (cx-32, cy-32))

class ConstructionSite:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 120, 80)
        self.trigger_rect = pygame.Rect(x-20, y-20, 160, 120)
        self.pos = pygame.Vector2(x, y)
        
        self.linked_fire = None # Set by hub logic
        
    def update_state(self, run_state):
        logs = run_state.shack_progress["logs"]
        if logs < 10:
            run_state.shack_progress["state"] = 1 # Foundation
        elif logs < 30:
            run_state.shack_progress["state"] = 2 # Framing
        else:
            run_state.shack_progress["state"] = 3 # Complete

    def render(self, surface, run_state):
        progress = run_state.shack_progress
        state = progress["state"]
        
        # Stage 1: Foundation (0-10 Logs) - Always drawn if discovered
        pygame.draw.rect(surface, (60, 60, 65), self.rect) # Stone base
        pygame.draw.rect(surface, (50, 50, 55), self.rect, 2) # Outline
        
        if state >= 2:
            # Stage 2: Framing (10-30 Logs)
            # Vertical Beams
            beam_color = (130, 90, 50)
            # 4 Corners
            pygame.draw.rect(surface, beam_color, (self.rect.x, self.rect.y - 40, 8, 40))
            pygame.draw.rect(surface, beam_color, (self.rect.right - 8, self.rect.y - 40, 8, 40))
            pygame.draw.rect(surface, beam_color, (self.rect.x, self.rect.bottom - 40, 8, 40)) # Lower beams (depth)
            pygame.draw.rect(surface, beam_color, (self.rect.right - 8, self.rect.bottom - 40, 8, 40))
            
            # Cross beams
            pygame.draw.rect(surface, beam_color, (self.rect.x, self.rect.y - 40, 120, 6)) # Top frame
            
            # Construction Debris
            pygame.draw.rect(surface, (150, 150, 120), (self.rect.centerx + 10, self.rect.centery + 10, 20, 5)) # Plank
            
        if state >= 3:
            # Stage 3: Walls and Roof (30+ Logs)
            # Walls
            pygame.draw.rect(surface, (100, 80, 60), (self.rect.x, self.rect.y - 40, 120, 80))
            
            # Doorway
            door_rect = pygame.Rect(self.rect.centerx - 15, self.rect.bottom - 40, 30, 40)
            pygame.draw.rect(surface, (40, 30, 20), door_rect)
            
            # Roof
            pygame.draw.polygon(surface, (50, 40, 35), [
                (self.rect.x - 10, self.rect.y - 40),
                (self.rect.centerx, self.rect.y - 90),
                (self.rect.right + 10, self.rect.y - 40)
            ])
            
            # Chimney with Smoke
            pygame.draw.rect(surface, (70, 70, 70), (self.rect.right - 30, self.rect.y - 70, 15, 30))
            # Smoke handled by particle system elsewhere?
            
            # Window
            pygame.draw.rect(surface, (20, 20, 30), (self.rect.x + 10, self.rect.y - 20, 20, 20))
            pygame.draw.rect(surface, (120, 100, 80), (self.rect.x + 10, self.rect.y - 20, 20, 20), 2)

class SignalFire(Campfire):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.rect = pygame.Rect(x-40, y-40, 128, 96) # Massive
        self.box_rect = pygame.Rect(x-40, y+60, 128, 48) # Interaction box (unused, interact with fire main)
        self.fuel = 0 # Starts unlit
        self.is_lit = False
        
    def render(self, surface, run_state=None):
        cx, cy = self.rect.centerx, self.rect.centery
        
        # Massive structure base (Stone/Wood Pile)
        pygame.draw.circle(surface, (50, 50, 55), (cx, cy + 20), 40)
        
        # Unlit Wood Pile structure
        for i in range(5):
             rx = cx - 30 + (i * 12)
             pygame.draw.line(surface, (60, 45, 30), (rx, cy+20), (cx, cy-20), 6)
        
        # If Lit (Massive Fire)
        if self.is_lit or self.fuel > 0:
             # Huge Flames
             import random
             colors = [(255, 100, 0), (255, 200, 50), (255, 255, 200)]
             offsets = [(random.randint(-20, 20), random.randint(-40, 0)) for _ in range(10)]
             for ox, oy in offsets:
                 radius = random.randint(10, 25)
                 color = random.choice(colors)
                 pygame.draw.circle(surface, color, (cx+ox, cy+oy), radius)
                 
             # Core Light
             s = pygame.Surface((200, 200), pygame.SRCALPHA)
             pygame.draw.circle(s, (255, 150, 50, 50), (100, 100), 90)
             surface.blit(s, (cx-100, cy-100))
        else:
             # Ghost hint? No, just unlit pile.
             pass

class Stockpile:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 64, 48)
        self.box_rect = pygame.Rect(x + 8, y + 16, 48, 32)
        
    def render(self, surface, run_state):
        # Draw wooden crate
        pygame.draw.rect(surface, (70, 50, 35), self.box_rect)
        pygame.draw.rect(surface, (50, 35, 25), self.box_rect, 2)
        
        # Draw logs inside based on count
        if run_state:
            count = run_state.log_stash
            # Max visual logs is 5
            draw_count = min(5, (count // 4) + 1) if count > 0 else 0
            for i in range(draw_count):
                ly = self.box_rect.bottom - 8 - (i * 5)
                pygame.draw.rect(surface, (140, 100, 60), (self.box_rect.x + 10, ly, 28, 4))

class GuardianNPC:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x, y, 72, 96)
        self.dialogue_lines = []  # Set by zone/context
        
    def draw(self, surface):
        # Placeholder visual for NPC (Blue Gideon Variant)
        # Head
        pygame.draw.circle(surface, (230, 180, 150), (int(self.pos.x + 36), int(self.pos.y + 20)), 12)
        # Body (Blue Tunic)
        pygame.draw.rect(surface, (40, 60, 100), (self.pos.x + 24, self.pos.y + 32, 24, 40))
        # Blue Cloak
        pygame.draw.rect(surface, (30, 50, 80), (self.pos.x + 20, self.pos.y + 35, 32, 45), 0, 5)

class WindBreakRock:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 80, 60)
        self.hitbox = pygame.Rect(x + 10, y + 20, 60, 30) # Collision
        self.image = self._generate_image()
        
    def _generate_image(self):
        surf = pygame.Surface((80, 60), pygame.SRCALPHA)
        # Large grey rock
        pygame.draw.ellipse(surf, (70, 75, 80), (0, 0, 80, 60))
        pygame.draw.ellipse(surf, (60, 65, 70), (5, 5, 70, 50)) # Shading
        # Cracks
        pygame.draw.line(surf, (40, 40, 45), (20, 20), (40, 40), 3)
        return surf
        
    def render(self, surface, offset=(0,0)):
        surface.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))

class EnvironmentManager:
    def __init__(self):
        self.trees = []
        self.particles = []
        self.campfires = []
        self.bg_surface = None
        self.current_zone = None
        self.fog_alpha = 180
        self.stockpile = None
        self.construction_site = None
        self.npc = None
        self.sticks = []
        self.deadfalls = []
        
    def load_zone(self, zone_data, width, height, safe_pos=None):
        self.current_zone = zone_data
        self.bg_surface = generate_background_surface(width, height)
        self.trees = []
        self.campfires = []
        self.stockpile = None
        self.construction_site = None
        self.npc = None
        self.sticks = []
        self.deadfalls = []
        self.rocks = []
        
        spawn_safe_x, spawn_safe_y = safe_pos if safe_pos else (400, 300)
        
        # --- GUARANTEED SPAWNS (Balancing Harshness) ---
        if zone_data:
            if zone_data.id == 0:
                # Zone 0: Tutorial - The Homestead
                # Spawn 5 trees for practice (scattered around)
                for _ in range(5):
                    while True:
                        x = random.randint(200, 500)
                        y = random.randint(150, 450)
                        # Safe Zone around Player Start/Safe Pos
                        if math.hypot(x - spawn_safe_x, y - spawn_safe_y) > 100:
                            self.trees.append(Tree(x, y))
                            break
                
                # Spawn The Elder NPC handled by NPCManager
                
                # Spawn permanent tutorial fire next to Elder
                tutorial_fire = Campfire(550, 320)
                
                # Spawn permanent tutorial fire next to Elder
                tutorial_fire = Campfire(550, 320)
                tutorial_fire.fuel = 100.0
                tutorial_fire.is_tutorial_fire = True  # Mark as permanent
                self.campfires.append(tutorial_fire)
                
            elif zone_data.id == 1:
                # Zone 1: 15 Trees near start
                for _ in range(15):
                    while True:
                        x = random.randint(100, width - 200)
                        y = random.randint(100, height - 200)
                        dist_center = math.hypot(x-400, y-300)
                        dist_player = math.hypot(x-spawn_safe_x, y-spawn_safe_y)
                        
                        if 120 < dist_center < 450 and dist_player > 100:
                            self.trees.append(Tree(x, y))
                            break
            elif zone_data.id == 2:
                # Zone 2: INCREASED DENSITY & WIND BREAKS
                # "Old Growth" - More trees
                for _ in range(12): # Increased from 5
                    self.trees.append(Tree(random.randint(50, width-100), random.randint(50, height-100)))
                
                # Help: 5 Guaranteed Deadfalls (Stick Piles) near spawn
                for i in range(5):
                    # Scatter near left side (spawn)
                    dx = random.randint(100, 300)
                    dy = random.randint(100, height-100)
                    self.deadfalls.append(DeadfallPile(dx, dy))
                
                # Wind Breaks (Rocks)
                # Lane 1 (Top)
                self.rocks.append(WindBreakRock(300, 150))
                self.rocks.append(WindBreakRock(600, 150))
                self.rocks.append(WindBreakRock(900, 150))
                # Lane 2 (Bottom)
                self.rocks.append(WindBreakRock(600, 500))
                self.rocks.append(WindBreakRock(900, 500))
                
                # HUB ANCHOR: Campfire + Construction Site
                # Center of zone
                hub_x, hub_y = width // 2, height // 2
                
                # 1. Spawn Hub Campfire
                hub_fire = Campfire(hub_x, hub_y)
                self.campfires.append(hub_fire)
                
                # 2. Spawn Construction Site (100px North)
                # Adjusting coordinates: Campfire is at hub_y. Site should be 'above' it.
                # Screen Y increases downwards. So North is Y - 100.
                self.construction_site = ConstructionSite(hub_x, hub_y - 120)
                
                # 3. Link them
                self.construction_site.linked_fire = hub_fire
                
            elif zone_data.id == 3:
                # Zone 3: Builder's Ridge / Merged
                # Logic moved to Zone 2, keeping this for legacy safe-guard or if Z3 is distinct
                # Prompt implies Zone 2 is now the construction hub.
                # We'll leave Z3 as sparse or empty if Z2 is the main hub.
                pass
                
                # Old logic moved to Z2 above
                # self.construction_site = ConstructionSite(200, 250)
                # Some trees
                for _ in range(8):
                    x = random.randint(50, width-100)
                    y = random.randint(50, height-100)
                    if math.hypot(x-200, y-250) > 120: 
                        self.trees.append(Tree(x, y))
            elif zone_data.id == 4:
                # Zone 4: The Peak (Zone 3 ID in prompt, but let's assume valid ID)
                # Prompt says Zone 3 is Peak. Wait, previous zone was Zone 3 (Builder's Ridge).
                # Previous map: 0=Tutorial, 1=Woods, 2=Gap, 3=Ridge.
                # So Peak is Zone 4.
                
                # Terrain: Sparse Dead Trees
                for _ in range(4):
                     self.trees.append(Tree(random.randint(100, width-100), random.randint(200, height-100)))
                     # Mark as dead? Tree class handles snow.
                
                # Rocks guiding path (Narrow up center)
                for y_rock in range(200, height, 100):
                     # Left wall
                     self.rocks.append(WindBreakRock(width//2 - 150, y_rock))
                     # Right wall
                     self.rocks.append(WindBreakRock(width//2 + 150, y_rock))
                
                # Signal Fire at Top Center
                sf = SignalFire(width//2, 120)
                self.campfires.append(sf)
                
                # No construction site, no stockpile (final challenge)
                self.stockpile = None

        # Fill remaining slots from zone_data if any (keeping it consistent)
        count = zone_data.resource_count if zone_data else 15
        current_tree_count = len(self.trees)
        if current_tree_count < count:
            for _ in range(count - current_tree_count):
                while True:
                    x = random.randint(50, width - 100)
                    y = random.randint(50, height - 100)
                    if abs(x - 400) > 80 and abs(y - 300) > 80:
                        if math.hypot(x - spawn_safe_x, y - spawn_safe_y) > 80:
                            self.trees.append(Tree(x, y))
                            break

    def setup_haven(self):
        """Spawns safe-haven entities for stabilized Zone 1."""
        # Main fire position (fixed for haven)
        fx, fy = 400, 350
        self.campfires = [Campfire(fx, fy)]
        self.campfires[0].fuel = 100.0
        
        # NPC (Elder) handled by NPCManager
        
        # Stockpile nearby
        self.stockpile = Stockpile(fx - 100, fy + 20)
    
    def spawn_campfire(self, x, y):
        self.campfires.append(Campfire(x, y))
        return self.campfires[-1]

    def spawn_wood_chips(self, x, y, count=5):
        wood_colors = [(100, 70, 40), (140, 100, 60), (70, 50, 30)]
        for _ in range(count):
             # Ensure Particle is defined, assuming it is from previous edit
            p = Particle(x, y, random.choice(wood_colors))
            self.particles.append(p)
            
    def spawn_leaf_fall(self, x, y, count=3):
        for _ in range(count):
            self.particles.append(LeafParticle(x, y))

    def spawn_footstep_dust(self, x, y):
        for _ in range(1):
             # 2x2 grey pixel
            color = random.choice([(150, 150, 150), (120, 120, 120)])
            p = Particle(x, y, color, size=2)
            # Custom physics for footsteps (lighter, drift)
            p.vx = random.uniform(-10, 10)
            p.vy = random.uniform(-10, -5) # Slight puff up
            p.life = 0.3
            self.particles.append(p)
            
    def update_ticks(self):
        """Called by TickSystem to handle time-based resource regrowth."""
        for tree in self.trees:
            tree.update_tick()
            
            # STICK MECHANIC: 10% chance tree drops a stick nearby
            if tree.state == tree.STATE_FULL and random.random() < 0.10:
                sx = tree.rect.centerx + random.randint(-40, 40)
                sy = tree.rect.bottom + random.randint(5, 25)
                # Ensure within bounds
                self.sticks.append(Stick(sx, sy))
                
        for df in self.deadfalls:
            df.update_tick()

    def update(self, dt):
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]
        # Update Campfires
        for f in self.campfires:
            f.update(dt)
                    
    def render(self, surface, camera_y_sort=False, offset=(0,0)):
        # Draw BG
        if self.bg_surface:
            surface.blit(self.bg_surface, offset)
            
    def render_particles(self, surface, offset=(0,0)):
        for p in self.particles:
            p.render(surface, offset)
            
    # For campfire rendering, they should be Y-Sorted ideally.
    # We will expose them in main.py via env_manager.campfires

    def draw_border(self, screen, run_state, dt):
        """Draws the spatial boundary (fog wall)."""
        if run_state.current_zone_id == 1:
            if not run_state.zone_1_stabilized:
                self.fog_alpha = 180
            else:
                fade_speed = (180.0 / 3.0) # 3 seconds
                self.fog_alpha = max(0, self.fog_alpha - fade_speed * dt)
            
            if self.fog_alpha > 0:
                s_w, s_h = screen.get_size()
                # Draw along the right edge
                border_surface = pygame.Surface((100, s_h), pygame.SRCALPHA)
                
                # Base mist
                border_surface.fill((40, 40, 45, int(self.fog_alpha)))
                
                # Add some wispy circles for texture
                t = pygame.time.get_ticks() / 1000.0
                for i in range(15):
                    oy = (i * 60 + t * 40) % s_h
                    ox = 50 + (i % 3 - 1) * 20
                    alpha = int(self.fog_alpha * 0.6)
                    pygame.draw.circle(border_surface, (30, 30, 35, alpha), (int(ox), int(oy)), 40)
                
                # Warning icons or cracks if solid?
                if not run_state.zone_1_stabilized:
                    # Draw subtle "locked" glyphs or just more density
                    pygame.draw.rect(border_surface, (20, 20, 25, int(self.fog_alpha * 0.8)), (80, 0, 20, s_h))

                screen.blit(border_surface, (s_w - 100, 0))
