import pygame
import random
from data.matrices import IDLE_CYCLE, WALK_CYCLE_DOWN, WALK_CYCLE_UP, WALK_CYCLE_SIDE

# NPC Palette (Red/Orange theme vs Player's Green)
# NPC Palettes
PALETTE_SABOTEUR = {
    0: (0, 0, 0, 0),       # Transparent
    1: (240, 190, 160),    # Skin
    2: (85, 25, 15),       # Tunic Dark (Deep Red)
    3: (180, 60, 40),      # Tunic Light (Red-Orange)
    4: (70, 45, 30),       # Brown (Hair/Boots)
    5: (110, 75, 45),      # Light Brown (Highlight)
    6: (35, 35, 40),       # Outline / Dark Charcoal
    7: (160, 170, 180),    # Steel (Tool)
    8: (60, 60, 70),       # Pants (Dark Gray)
    9: (255, 180, 80),     # Glow Core (Orange)
    10: (255, 100, 40),    # Glow Edge (Red-Orange)
}

PALETTE_ELDER = PALETTE_SABOTEUR.copy()
PALETTE_ELDER.update({
    2: (50, 50, 60),      # Robes Dark
    3: (100, 100, 120),   # Robes Light
    4: (220, 220, 220),   # White Hair/Beard
    9: (200, 220, 255),   # Blue Spirit Glow
    10: (100, 150, 255)
})

PALETTE_BUILDER = PALETTE_SABOTEUR.copy()
PALETTE_BUILDER.update({
    2: (60, 40, 20),      # Leather Dark
    3: (160, 120, 60),     # Tan Fabric
    4: (200, 50, 50),     # Red Bandana
})

class NPC:
    def __init__(self, x, y, npc_type="saboteur", npc_id="GENERIC"):
        self.pos = pygame.Vector2(x, y)
        self.speed = 60  # Slower than player
        self.pixel_size = 4
        self.grid_width = 18
        self.grid_height = 24
        
        # State
        self.facing = "DOWN"
        self.is_moving = False
        self.is_working = False
        self.flip_h = False
        self.flip_h = False
        self.npc_type = npc_type  # "saboteur" or "keeper"
        self.npc_id = npc_id # "ELDER", "BUILDER", etc
        
        # Determine Palette
        if self.npc_id == "ELDER":
            self.palette = PALETTE_ELDER
        elif self.npc_id == "BUILDER":
            self.palette = PALETTE_BUILDER
        else:
            self.palette = PALETTE_SABOTEUR
        
        # Behavior
        self.target_fire = None
        self.action_cooldown = 0.0
        self.wander_timer = 0.0
        self.wander_direction = pygame.Vector2(0, 0)
        
        # Animation
        self.frame_index = 0
        self.animation_timer = 0.0
        self.animation_interval = 0.2
        
        self.current_cycle = IDLE_CYCLE
        self.current_grid = self.current_cycle[self.frame_index]
        
        # Dialogue
        self.dialogue_lines = []  # Set by zone/context
        
        self.image = None
        self.render_cache()
    
    def render_cache(self, palette=None):
        """Render NPC sprite using assigned palette."""
        if palette is None:
            palette = self.palette
            
        from data.matrices import build_hero_grid
        self.current_grid = build_hero_grid(
            self.frame_index, 
            self.facing, 
            "TORCH",  # NPCs carry torches
            self.is_working,    # is_chopping (used for hammering)
            self.is_moving, 
            False,    # is_lighting
            False     # is_igniting
        )
        
        width = self.grid_width * self.pixel_size
        height = self.grid_height * self.pixel_size
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                sample_x = (self.grid_width - 1 - x) if self.flip_h else x
                val = self.current_grid[y][sample_x]
                if val in palette:
                    color = palette[val]
                    if color[3] if len(color) > 3 else True:
                        rect = (x * self.pixel_size, y * self.pixel_size, 
                               self.pixel_size, self.pixel_size)
                        pygame.draw.rect(self.image, color, rect)
    
    def update(self, dt, run_state, env_manager):
        """Update NPC behavior based on type and zone state."""
        self.action_cooldown -= dt
        
        campfires = env_manager.campfires if env_manager else []
        site = env_manager.construction_site if env_manager else None
        zone_stabilized = run_state.zone_1_stabilized if run_state else False

        # Choose behavior based on zone state
        if site and self.npc_id == "BUILDER":
             self._builder_behavior(dt, run_state, env_manager)
        elif self.npc_id == "ELDER" or (zone_stabilized and self.npc_type == "keeper"):
             self._keeper_behavior(dt, campfires)
        else:
             self._saboteur_behavior(dt, campfires)
        
        # Animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_interval:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % 4
            self.render_cache()
    
    def _saboteur_behavior(self, dt, campfires):
        """Move toward fires and steal fuel."""
        # Find nearest active fire
        if not self.target_fire or self.target_fire.fuel <= 0:
            self.target_fire = None
            min_dist = 999999
            for fire in campfires:
                if fire.fuel > 0:
                    dist = (pygame.Vector2(fire.rect.center) - self.pos).length()
                    if dist < min_dist:
                        min_dist = dist
                        self.target_fire = fire
        
        if self.target_fire:
            # Move toward target
            target_pos = pygame.Vector2(self.target_fire.rect.center)
            direction = target_pos - self.pos
            dist = direction.length()
            
            if dist > 40:  # Not at fire yet
                self.is_moving = True
                direction = direction.normalize()
                self.pos += direction * self.speed * dt
                
                # Update facing
                if abs(direction.y) > abs(direction.x):
                    self.facing = "DOWN" if direction.y > 0 else "UP"
                    self.flip_h = False
                else:
                    self.facing = "SIDE"
                    self.flip_h = direction.x < 0
            else:
                # At fire - sabotage it!
                self.is_moving = False
                if self.action_cooldown <= 0:
                    stolen = min(10.0, self.target_fire.fuel)
                    self.target_fire.fuel -= stolen
                    print(f"[SABOTEUR] Stole {stolen:.1f} fuel from fire!")
                    self.action_cooldown = 2.0  # Cooldown before next steal
                    self.target_fire = None  # Find new target
        else:
            # Wander
            self._wander(dt)
    
    def _keeper_behavior(self, dt, campfires):
        """Stay near fires and maintain them."""
        # Find fire that needs fuel
        if not self.target_fire:
            for fire in campfires:
                if fire.fuel < 50.0:  # Needs maintenance
                    self.target_fire = fire
                    break
        
        if self.target_fire:
            # Move toward fire
            target_pos = pygame.Vector2(self.target_fire.rect.center)
            direction = target_pos - self.pos
            dist = direction.length()
            
            if dist > 60:  # Not near fire
                self.is_moving = True
                direction = direction.normalize()
                self.pos += direction * self.speed * dt
                
                # Update facing
                if abs(direction.y) > abs(direction.x):
                    self.facing = "DOWN" if direction.y > 0 else "UP"
                    self.flip_h = False
                else:
                    self.facing = "SIDE"
                    self.flip_h = direction.x < 0
            else:
                # Near fire - maintain it
                self.is_moving = False
                if self.action_cooldown <= 0 and self.target_fire.fuel < 50.0:
                    added = 20.0
                    self.target_fire.fuel = min(100.0, self.target_fire.fuel + added)
                    print(f"[KEEPER] Added {added:.1f} fuel to fire!")
                    self.action_cooldown = 3.0
                    
                # If fire is full, find another
                if self.target_fire.fuel >= 50.0:
                    self.target_fire = None
        else:
            # Wander near spawn
            self._wander(dt)
    
    def _wander(self, dt):
        """Random wandering behavior."""
        self.wander_timer -= dt
        if self.wander_timer <= 0:
            # Pick new random direction
            self.wander_direction = pygame.Vector2(
                random.choice([-1, 0, 1]),
                random.choice([-1, 0, 1])
            )
            if self.wander_direction.length() > 0:
                self.wander_direction = self.wander_direction.normalize()
            self.wander_timer = random.uniform(1.0, 3.0)
        
        if self.wander_direction.length() > 0:
            self.is_moving = True
            self.pos += self.wander_direction * self.speed * 0.5 * dt
            
            # Update facing
            if abs(self.wander_direction.y) > abs(self.wander_direction.x):
                self.facing = "DOWN" if self.wander_direction.y > 0 else "UP"
                self.flip_h = False
            else:
                self.facing = "SIDE"
                self.flip_h = self.wander_direction.x < 0
        else:
            self.is_moving = False
        
        # Clamp to screen
        self.pos.x = max(50, min(1200, self.pos.x))
        self.pos.y = max(50, min(650, self.pos.y))
    
    def _builder_behavior(self, dt, run_state, env_manager):
        """Stand near construction site and hammer."""
        site = env_manager.construction_site
        logs = run_state.shack_progress["logs"]
        state = run_state.shack_progress["state"]
        
        if logs > 0 and state < 3:
            # ACTIVE BUILDING
            if self.action_cooldown <= 0:
                # Pick new random task (Move or Hammer)
                if random.random() < 0.6: # 60% chance to move
                    # Pick random spot on site
                    rx = random.randint(site.rect.x, site.rect.right)
                    ry = random.randint(site.rect.y, site.rect.bottom)
                    self.wander_direction = pygame.Vector2(rx, ry) # Using as Target Pos
                    self.is_moving = True
                    self.is_working = False
                    self.action_cooldown = 2.0 # Time to move?
                else: 
                   # Hammer here
                   self.is_moving = False
                   self.is_working = True
                   self.action_cooldown = 3.0 # Hammer for 3s
            
            if self.is_moving:
                # Move to target
                 target = self.wander_direction
                 direction = target - self.pos
                 if direction.length() < 5:
                     self.is_moving = False
                     self.is_working = True # Arrived, start hammering
                 else:
                     self.pos += direction.normalize() * self.speed * dt
                     # Update facing
                     if abs(direction.y) > abs(direction.x):
                        self.facing = "DOWN" if direction.y > 0 else "UP"
                        self.flip_h = False
                     else:
                        self.facing = "SIDE"
                        self.flip_h = direction.x < 0
            
            if self.is_working:
                # Spawn dust
                 if random.random() < 0.1:
                     env_manager.spawn_footstep_dust(self.pos.x + 10, self.pos.y + 30)
                 # Hammer anim is handled by render_cache (is_working=True)
                 
        else:
            # Idle / Stand near start
            pass

    def draw(self, screen):
        """Draw NPC sprite."""
        screen.blit(self.image, (self.pos.x, self.pos.y))
