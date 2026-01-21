import pygame
import random
import math
from data.matrices import IDLE_CYCLE, WALK_CYCLE_DOWN, WALK_CYCLE_UP, WALK_CYCLE_SIDE
from constants import MAX_LOG_SLOTS, MAX_STICKS

PALETTE = {
    0: (0, 0, 0, 0),       # Transparent
    1: (240, 190, 160),   # Skin
    2: (45, 85, 45),      # Tunic Dark (Green)
    3: (90, 130, 70),     # Tunic Light (Green)
    4: (70, 45, 30),      # Brown (Hair/Boots)
    5: (110, 75, 45),     # Light Brown (Highlight)
    6: (35, 35, 40),      # Outline / Dark Charcoal
    7: (160, 170, 180),   # Steel (Axe Head)
    8: (60, 60, 70),      # Pants (Dark Gray)
    9: (255, 230, 100),   # Torch Light Core
    10: (255, 120, 20),   # Torch Light Orange
    11: (150, 180, 220),  # Frozen Blue (light)
    12: (100, 140, 200),  # Frozen Blue (dark)
}

class Player:
    def __init__(self):
        self.pos = pygame.Vector2(400, 300)
        self.speed = 180 # Slightly slower for "weight"
        self.pixel_size = 4
        self.grid_width = 18
        self.grid_height = 24
        
        # State
        self.facing = "DOWN"
        self.is_moving = False
        self.flip_h = False
        self.body_temp = 0 # DEPRECATED (Kept for fallback if needed during transition, but logically handled by RunState)
        # Actually prompt says REMOVE.
        # So:
        self.is_frozen = False
        
        # Tools
        # Tools
        self.active_tool = "TORCH" # TORCH or AXE
        self.is_chopping = False
        self.chop_timer = 0.0
        self.tool_cooldown = 0.0
        self.is_lighting = False
        self.light_timer = 0.0
        self.is_igniting = False 
        self.ignite_progress = 0 
        
        # Action Tick (Responsive): Chopping, Fueling (0.6s)
        self.action_tick_timer = 0.0
        self.action_tick_interval = 0.6
        
        # Animation
        self.frame_index = 0
        self.animation_timer = 0.0
        self.animation_interval = 0.12
        
        # === PROCEDURAL ANIMATION ===
        # Bobbing
        self.bob_timer = 0.0
        self.bob_amplitude = 3  # Pixels
        
        # Tilt/Lean
        self.tilt_angle = 0.0
        self.target_tilt = 0.0
        self.tilt_speed = 10.0  # Degrees per second
        self.last_move_direction = pygame.Vector2(0, 0)
        
        # Squash & Stretch
        self.squash_frames_remaining = 0
        self.squash_scale_x = 1.0
        self.squash_scale_y = 1.0
        
        # Ghosting (afterimage)
        self.ghost_positions = []  # Store recent positions
        self.ghost_max_trail = 3
        
        # Interaction Juice
        self.hit_impact = False # Flag for hit-stop
        self.stabilization_event = False
        self.redemption_event = False
        self.swing_arc_frames = 0
        
        self.current_cycle = IDLE_CYCLE
        self.current_grid = self.current_cycle[self.frame_index]
        
        self.image = None
        self.render_cache()

    def change_temp(self, amount, run_state):
        run_state.body_temp += amount
        print(f"Body Temp: {run_state.body_temp}")

    def respawn(self, run_state):
        """Resets the player state (Zone Reset simulation)."""
        self.pos = pygame.Vector2(400, 300)
        run_state.body_temp = 37.0
        self.is_frozen = False
        self.render_cache(self.get_current_palette(run_state))

    def get_interaction_rect(self):
        """Mathematically calculate precise 32x32 square 16px in front."""
        cx, cy = self.pos.x + 36, self.pos.y + 48 # Center
        dist = 16
        size = 32
        
        if self.facing == "UP":
            return pygame.Rect(cx - size//2, cy - dist - size, size, size)
        elif self.facing == "DOWN":
             return pygame.Rect(cx - size//2, cy + dist, size, size)
        elif self.facing == "SIDE":
             if self.flip_h: # Left
                 return pygame.Rect(cx - dist - size, cy - size//2, size, size)
             else: # Right
                 return pygame.Rect(cx + dist, cy - size//2, size, size)
        return pygame.Rect(cx - size//2, cy + dist, size, size)

    def render_cache(self, palette=None):
        if palette is None:
            palette = PALETTE
            
        # Passing active_tool and is_chopping to the grid generator would be ideal, 
        # but for now matrices.py handles the drawing based on frame.
        # Let's ensure build_hero_grid is updated to accept these states.
        from data.matrices import build_hero_grid 
        self.current_grid = build_hero_grid(self.frame_index, self.facing, self.active_tool, self.is_chopping, self.is_moving, self.is_lighting, self.is_igniting)
        
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
                        rect = (x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size)
                        pygame.draw.rect(self.image, color, rect)

    def update(self, dt, trees=[], env_manager=None, controller=None, run_state=None, camera=None, floating_texts=None, audio_manager=None):
        if run_state and not run_state.is_alive:
            return 
            
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        
        # Helper to spawn floating text
        def spawn_text(text, color):
            if floating_texts is not None:
                from ui.floating_text import FloatingText
                floating_texts.append(FloatingText(self.pos.x + 36, self.pos.y, text, color))
        
        # === DUAL CLOCK UPDATES ===
        
        # Action Tick (0.6s) - For Interactions/Chopping
        self.action_tick_timer += dt
        action_triggered = False
        if self.action_tick_timer >= self.action_tick_interval:
            self.action_tick_timer -= self.action_tick_interval
            action_triggered = True
            
        # === INPUT ===
        # Consolidated Action Input (Mouse Click or SPACE or E)
        mouse_buttons = pygame.mouse.get_pressed()
        action_input = keys[pygame.K_SPACE] or mouse_buttons[0] or keys[pygame.K_e] or keys[pygame.K_f]
        
        # Determine Intent based on Tool
        # Both mechanisms use the same input, differentiated by Tool
        # But we maintain legacy flags to minimize logic rewrite, mapping action_input to them
        
        action_held = action_input # For Chopping (AXE)
        ignite_held = action_input # For Lighting (TORCH)
        
        swap_pressed = keys[pygame.K_TAB]
        
        # Controller Input
        if controller:
            c_x = controller.get_axis(0)
            c_y = controller.get_axis(1)
            if abs(c_x) > 0.2: move.x += c_x
            if abs(c_y) > 0.2: move.y += c_y
            if controller.get_button(0): action_held = True; ignite_held = True # A (Chop/Interact)
            if controller.get_button(1): ignite_held = True # B (Ignite)
            if controller.get_button(2) or controller.get_button(3): swap_pressed = True

        # Keyboard Movement
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        
        can_move = not self.is_igniting and not self.is_chopping

        # Precise Interaction Hitbox (30x30 projectile, 15px in front of player)
        interaction_size = 30
        projectile_distance = 15
        
        # Player center position
        center_x = self.pos.x + 36  # Player width/2
        center_y = self.pos.y + 48  # Player height/2
        
        # Project hitbox based on facing direction (The Snap)
        self.target_hitbox = self.get_interaction_rect()

        # Tool Swap (Instant, but cooldown to prevent spam)
        if self.tool_cooldown > 0: self.tool_cooldown -= dt
        if swap_pressed and self.tool_cooldown <= 0:
            self.active_tool = "AXE" if self.active_tool == "TORCH" else "TORCH"
            self.tool_cooldown = 0.4
            self.render_cache(self.get_current_palette())

        # === TICK BASED ACTIONS ===
        
        # 1. IGNITE / REFUEL (Must Hold)
        if ignite_held and self.active_tool == "TORCH":
            self.is_igniting = True # Crouch Anim
            
            if action_triggered:
                # Interaction First (Fuel)
                interaction_done = False
                if env_manager:
                    # Stockpile Interaction (Deposit/Withdraw)
                    if env_manager.stockpile:
                        dist = (pygame.Vector2(env_manager.stockpile.rect.center) - self.pos).length()
                        if dist < 80:
                            if run_state.inventory["logs"] > 0:
                                count = run_state.inventory["logs"]
                                run_state.log_stash += count
                                run_state.inventory["logs"] = 0
                                spawn_text(f"STASHED {count} LOGS", (200, 200, 200))
                                interaction_done = True
                            elif run_state.log_stash > 0:
                                # Withdraw 1 if empty inventory
                                run_state.log_stash -= 1
                                run_state.add_log(1)
                                spawn_text("WITHDREW 1 LOG", (255, 255, 255))
                                interaction_done = True

                    if not interaction_done:
                        for fire in env_manager.campfires:
                            dist = (pygame.Vector2(fire.box_rect.center) - self.pos).length()
                            if dist < 65: # Reachable
                                if run_state and run_state.inventory["logs"] > 0:
                                    fire.add_fuel(30.0)
                                    run_state.remove_log(1)
                                    
                                    # Objective Tracking
                                    import time
                                    run_state.last_log_deposit_time = time.time()
                                    
                                    if run_state.current_zone_id == 1:
                                        run_state.logs_deposited_in_zone_1 += 1
                                    elif run_state.current_zone_id == 3:
                                        run_state.logs_deposited_in_zone_3 += 1
                                        
                                    if audio_manager:
                                        audio_manager.play_sound("chop") # Reusing chop sound for wood thud
                                    
                                    # Tutorial progression (Zone 0)
                                    if run_state.current_zone_id == 0 and run_state.tutorial_step == 4:
                                        run_state.tutorial_step = 5
                                        spawn_text("THE ELDER SPEAKS", (255, 215, 0))
                                    
                                    # Stabilization Progress (Zone 1 & 2)
                                    if run_state.current_zone_id == 1:
                                        if run_state.deposit_log_zone_1():
                                            self.stabilization_event = True # Signal for main.py
                                    elif run_state.current_zone_id == 2:
                                        if run_state.deposit_log_zone_2():
                                            self.redemption_event = True # Signal for main.py
                                    
                                    env_manager.spawn_wood_chips(fire.box_rect.centerx, fire.box_rect.centery, 3)
                                    spawn_text("FIRE RESTORED", (255, 140, 20)) # Orange
                                    print(f"[TICK] Refueled Fire. Logs: {run_state.inventory['logs']}")
                                elif run_state and run_state.inventory.get("sticks", 0) > 0:
                                    # STICK REFUEL: +5 Fuel
                                    fire.add_fuel(5.0)
                                    run_state.inventory["sticks"] -= 1
                                    spawn_text("+5 FUEL", (255, 180, 50))
                                    print(f"[TICK] Refueled with stick. Remaining: {run_state.inventory['sticks']}")
                                else:
                                    print("[TICK] No logs or sticks for fuel.")
                                interaction_done = True
                                break
                
                # If not interacting, progress Lighting New Fire
                if not interaction_done:
                    # Constraint: Only 1 Fire
                    existing_fire_count = len(env_manager.campfires) if env_manager else 0
                    if existing_fire_count > 0:
                         print("[TICK] Cannot light new fire. One already exists.")
                    else:
                        if run_state and run_state.inventory["logs"] >= 3:
                            self.ignite_progress += 1
                            print(f"[TICK] Igniting... {self.ignite_progress}/3")
                            if self.ignite_progress >= 3:
                                # SUCCESS
                                run_state.remove_log(3)
                                # Target is mouse or hitbox
                                fx, fy = self.target_hitbox.centerx - 16, self.target_hitbox.centery - 16
                                if env_manager: env_manager.spawn_campfire(fx, fy)
                                print("[TICK] FIRE LIT!")
                                self.ignite_progress = 0
                                self.is_igniting = False # Reset state
                        else:
                            print("[TICK] Need 3 logs.")
        else:
            self.is_igniting = False
            self.ignite_progress = 0

        # --- INSTANT INTERACTIONS (Sticks/Deadfall) ---
        if env_manager:
            # Auto-collect loose sticks on ground
            for stick in env_manager.sticks:
                if not stick.consumed:
                    dist = (self.pos - stick.pos).length()
                    if dist < 30:
                        # Check Capacity
                        if run_state.inventory.get("sticks", 0) >= MAX_STICKS:
                            # Prompt user, but don't spam?
                            # Only spawn text if we haven't recently?
                            # Using action_tick implies we check constantly?
                            # This loop runs every frame.
                            # We should only trigger this if player is TRYING to interact?
                            # Auto-collect doesn't require input.
                            # So if we walk over it and full, we just ignore it?
                            # Prompt: "Show a small popup text: 'Need real wood (Logs).'"
                            # If we spam text every frame, it overlaps.
                            # We can check a timer or just chance?
                            if random.random() < 0.05: # Occasional reminder
                                 spawn_text("Need Logs", (200, 50, 50))
                            pass 
                        else:
                            stick.consumed = True
                            run_state.inventory["sticks"] += 1
                            spawn_text("+STICK", (150, 120, 80))
            
            # Deadfall Piles (Require Action Trigger)
            if action_triggered:
                for df in env_manager.deadfalls:
                    dist = (self.pos - df.pos).length()
                    if dist < 50:
                        if df.take_stick():
                            run_state.inventory["sticks"] += 1
                            spawn_text("+STICK", (150, 120, 80))
                            # Small visual impact
                            if camera: camera.shake(1)
                            break # Only one per trigger

        # 2. CHOPPING (Triggered by E or Held Button)
        if (action_held) and self.active_tool == "AXE" and not self.is_igniting:
            self.is_chopping = True
            
            # Hit on tick
            if action_triggered:
                print("[TICK] Chop Swing!")
                self.swing_arc_frames = 3
                hit_rect = self.target_hitbox
                
                # HIT LOGIC
                hit_something = False
                if env_manager:
                    for tree in trees:
                        if tree.state == tree.STATE_FULL and tree.stump_rect.colliderect(hit_rect):
                            hit_something = True
                            env_manager.spawn_wood_chips(tree.rect.centerx, tree.rect.bottom - 20, 5)
                            env_manager.spawn_leaf_fall(tree.rect.centerx, tree.rect.y + 20, 8)
                            
                            # Camera shake on impact
                            if camera:
                                camera.shake(2)
                            
                            self.squash_frames_remaining = 2
                            self.squash_scale_x = 1.1 
                            self.squash_scale_y = 0.9 
                            self.hit_impact = True 
                            
                            # RESOURCE EXHAUSTION CHECK
                            if run_state and run_state.current_zone_id == 1 and run_state.zone_1_resources_depleted:
                                tree.take_impact()
                                spawn_text("EXHAUSTED", (150, 150, 150))
                            else:
                                logs_dropped = tree.take_damage()
                                if logs_dropped > 0:
                                    spawn_text(f"+{logs_dropped} LOGS", (120, 80, 40)) 
                                    print(f"Timber! Dropped {logs_dropped} logs.")
                                    if run_state: 
                                        if run_state.axe_upgrade:
                                            logs_dropped += 1
                                            
                                        max_capacity = MAX_LOG_SLOTS + (2 if run_state.deep_pockets else 0)
                                        current_logs = run_state.inventory.get("logs", 0)
                                        
                                        # Clamp to capacity
                                        to_add = logs_dropped
                                        if current_logs + to_add > max_capacity:
                                             to_add = max(0, max_capacity - current_logs)
                                             
                                        if to_add > 0:
                                            run_state.add_log(to_add)
                                            spawn_text(f"+{to_add} LOGS", (120, 80, 40)) 
                                        
                                        if current_logs + logs_dropped > max_capacity:
                                            spawn_text("FULL", (200, 50, 50))
                                            
                                    if camera: camera.add_trauma(0.5)
                                else:
                                    # Chance for 1 log on hit if not felled
                                    if random.random() < 0.2: 
                                        if run_state:
                                             max_capacity = MAX_LOG_SLOTS + (2 if run_state.deep_pockets else 0)
                                             if run_state.inventory.get("logs", 0) < max_capacity:
                                                 amount = 1
                                                 if run_state.axe_upgrade: amount = 2
                                                 
                                                 run_state.add_log(amount)
                                                 spawn_text(f"+{amount} LOG", (120, 80, 40))
                                             else:
                                                 spawn_text("FULL", (200, 50, 50))
                            hit_something = True
                            break 
        else:
            self.is_chopping = False
            if not action_held: self.is_chopping = False

        # === MOVEMENT ===
        can_move = not self.is_igniting # Allow moving while chopping? Maybe slow?
        if self.is_chopping: can_move = False # lock movement
        
        self.is_moving = False
        if can_move and move.length() > 0:
             self.is_moving = True
             # Store move direction for procedural animation
             self.current_move_dir = move.copy()
             move = move.normalize() * self.speed * dt
             
             # Collision
             player_rect = pygame.Rect(self.pos.x + 20, self.pos.y + 70, 32, 16)
             
             # X
             self.pos.x += move.x
             player_rect.x = self.pos.x + 20
             for tree in trees:
                 if tree.state != tree.STATE_STUMP and tree.hitbox.colliderect(player_rect):
                     self.pos.x -= move.x # Revert
                     break
            
             # Y
             self.pos.y += move.y
             player_rect.y = self.pos.y + 70 # Update Y
             player_rect.x = self.pos.x + 20 # Keep X updated
             for tree in trees:
                 if tree.state != tree.STATE_STUMP and tree.hitbox.colliderect(player_rect):
                     self.pos.y -= move.y
                     break
                     
             # Facing Update
             if abs(move.y) > abs(move.x):
                 if move.y > 0: self.facing = "DOWN"; self.flip_h = False
                 elif move.y < 0: self.facing = "UP"; self.flip_h = False
             else:
                 if move.x > 0: self.facing = "SIDE"; self.flip_h = False
                 elif move.x < 0: self.facing = "SIDE"; self.flip_h = True

        # Clamp & Border Collision
        if run_state:
            # Physical limits
            left_limit = -80
            right_limit = 1200 # Logical width is 1280
            
            # If not stabilized in Zone 1, enforce right wall
            if run_state.current_zone_id == 1 and not run_state.zone_1_stabilized:
                self.pos.x = max(0, min(right_limit - 72, self.pos.x))
            else:
                # Transition allowed or in other zone
                self.pos.x = max(left_limit, min(1360, self.pos.x))
            
            self.pos.y = max(0, min(720 - 96, self.pos.y))

        # === PROCEDURAL ANIMATION UPDATES ===
        
        # 1. Bobbing (when moving)
        if self.is_moving:
            self.bob_timer += dt * 8  # Speed of bob
        else:
            self.bob_timer = 0
        
        # 2. Tilt/Lean (direction changes)
        if hasattr(self, 'current_move_dir'):
            if self.current_move_dir.length() > 0.1:
                # Check for direction change
                if self.last_move_direction.length() > 0.1:
                    dot = self.last_move_direction.normalize().dot(self.current_move_dir.normalize())
                    if dot < 0.5:  # Significant direction change
                        if self.current_move_dir.x > 0:
                            self.target_tilt = -3
                        elif self.current_move_dir.x < 0:
                            self.target_tilt = 3
                self.last_move_direction = self.current_move_dir.copy()
            else:
                self.target_tilt = 0
        
        # Smooth tilt transition
        tilt_diff = self.target_tilt - self.tilt_angle
        self.tilt_angle += tilt_diff * min(1.0, dt * self.tilt_speed)
        
        # 3. Squash & Stretch countdown
        if self.squash_frames_remaining > 0:
            self.squash_frames_remaining -= 1
            if self.squash_frames_remaining == 0:
                self.squash_scale_x = 1.0
                self.squash_scale_y = 1.0
        
        # 4. Ghosting trail
        if self.is_moving and self.image:
            self.ghost_positions.append((self.pos.x, self.pos.y, self.image.copy()))
            if len(self.ghost_positions) > self.ghost_max_trail:
                self.ghost_positions.pop(0)
        else:
            self.ghost_positions.clear()

        # Animation State
        self.animation_timer += dt
        interval = 0.12 if self.is_chopping else 0.18
        if self.animation_timer >= interval:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % 4
            
            # Spawn footstep dust on walk cycle (approx frames 0 and 2)
            if self.is_moving and (self.frame_index == 0 or self.frame_index == 2):
                if env_manager:
                    env_manager.spawn_footstep_dust(self.pos.x + 36, self.pos.y + 80)
            
            self.render_cache(self.get_current_palette(run_state))
        elif self.is_moving or self.is_igniting or self.is_chopping:
             pass
             
    def get_current_palette(self, run_state=None):
        if run_state and run_state.body_temp < 10:
            p = PALETTE.copy()
            p[1] = (120, 150, 200)  # Frozen Skin (blue-tinted)
            p[3] = (70, 100, 120)   # Frozen Tunic (icy green)
            p[2] = (40, 60, 80)     # Frozen Tunic Dark (darker ice)
            return p
        return PALETTE

    def run_death_animation(self):
        """Triggered upon death - freezes movement and tints palette grey/blue."""
        self.is_moving = False
        self.is_chopping = False
        self.is_lighting = False
        self.is_igniting = False
        
        death_p = PALETTE.copy()
        # Cold/Dead palette
        death_p[1] = (100, 100, 150)  # Frozen Skin
        death_p[3] = (60, 60, 100)    # Frozen Tunic
        death_p[2] = (40, 40, 80)     # Frozen Tunic Dark
        death_p[9] = (40, 40, 40)     # Extinguished torch core
        death_p[10] = (20, 20, 20)    # Extinguished torch orange
        
        from data.matrices import build_hero_grid
        # Use current frame/facing but new palette
        self.render_cache(death_p)


    def draw(self, screen):
        """Blit the cached surface at the center of current position."""
        rect = self.image.get_rect(center=(self.pos.x + 32, self.pos.y + 32)) 
        # Wait, pos is top-left usually? 
        # Previous draw code: rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        # If pos is top-left, drawing at center=pos puts it offset by half!
        # Standard pygame: blit at pos.
        screen.blit(self.image, (self.pos.x, self.pos.y))
        
        # Hit Arc Visualization
        if self.swing_arc_frames > 0:
            self.swing_arc_frames -= 1
            s = pygame.Surface((100, 100), pygame.SRCALPHA)
            rect = pygame.Rect(10, 10, 80, 80)
            
            start_angle = 0
            stop_angle = 0
            offset_pos = (self.pos.x - 14, self.pos.y - 12) # Center-ish adjustment
            
            if self.facing == "DOWN":
                start_angle = math.pi * 0.25
                stop_angle = math.pi * 0.75
                offset_pos = (self.pos.x - 14, self.pos.y + 10)
            elif self.facing == "UP":
                start_angle = math.pi * 1.25
                stop_angle = math.pi * 1.75
                offset_pos = (self.pos.x - 14, self.pos.y - 30)
            elif self.facing == "SIDE" and self.flip_h: # LEFT
                start_angle = math.pi * 0.75
                stop_angle = math.pi * 1.25
                offset_pos = (self.pos.x - 30, self.pos.y - 10)
            elif self.facing == "SIDE" and not self.flip_h: # RIGHT
                # Right side split
                pygame.draw.arc(s, (255, 255, 255, 180), rect, 0, math.pi * 0.25, 4)
                pygame.draw.arc(s, (255, 255, 255, 180), rect, math.pi * 1.75, math.pi * 2, 4)
                screen.blit(s, (self.pos.x + 10, self.pos.y - 10))
                return # Done for right

            if start_angle != 0 or stop_angle != 0:
                 pygame.draw.arc(s, (255, 255, 255, 180), rect, start_angle, stop_angle, 4)
                 screen.blit(s, offset_pos)


    def draw_light(self, screen):
        """Draws an opaque torch light circle - DISABLED per user request."""
        pass
        # is_active = (self.active_tool == "TORCH")
        # radius = 150 if is_active else 80
        # ...
