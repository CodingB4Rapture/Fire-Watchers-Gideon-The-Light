import pygame
import sys
from player import Player
from environment import EnvironmentManager
from ui import draw_inventory_ui, draw_survival_panel, draw_stabilization_ui, draw_cold_overlay, draw_shop_menu
from menu import MenuSystem, GameState
from settings import GameSettings
from data.run_state import RunState
from systems.zone_manager import ZoneManager
from systems.tick_system import TickSystem
from data.save_manager import SaveManager
from systems.npc_manager import NPCManager
from systems.audio_manager import AudioManager
from utils.camera import Camera
from systems.lighting_engine import LightingEngine
from systems.weather import WeatherSystem
from systems.event_manager import EventManager
from constants import LOGICAL_WIDTH, LOGICAL_HEIGHT
from systems.tutorial_manager import TutorialManager

from environment import SignalFire
from ui.floating_text import FloatingText

def win_game(screen, menu, audio_manager):
    """Trigger win state visuals and transition."""
    # White Flash
    flash = pygame.Surface(screen.get_size())
    flash.fill((255, 255, 255))
    
    # Fade loop (Blocking for dramatic effect)
    alpha = 0
    t_start = pygame.time.get_ticks()
    
    # Simple loop to fade to white
    clock = pygame.time.Clock()
    while alpha < 255:
        dt = clock.tick(60) / 1000.0
        alpha += 100 * dt # 2.5s fade
        if alpha > 255: alpha = 255
        
        # Don't redraw game, just blit white over whatever was there
        flash.set_alpha(int(alpha))
        screen.blit(flash, (0,0))
        pygame.display.flip()
        
        # Pump events to prevent freezing
        pygame.event.pump()
        
    # Transition to Credits
    menu.state = GameState.CREDITS
    if audio_manager.music:
        audio_manager.music.stop() 
    
    print("WIN STATE TRIGGERED")

def main():
    pygame.init()
    
    # Load settings
    game_settings = GameSettings()
    
    # Backward compatibility
    SCREEN_WIDTH = LOGICAL_WIDTH
    SCREEN_HEIGHT = LOGICAL_HEIGHT
    FPS = 60
    
    def setup_display(settings):
        mode = settings.get("graphics", "display_mode")
        res_str = settings.get("graphics", "resolution")
        try:
            win_w, win_h = map(int, res_str.split('x'))
        except:
            win_w, win_h = LOGICAL_WIDTH, LOGICAL_HEIGHT
            
        # Get desktop info
        info = pygame.display.Info()
        native_w, native_h = info.current_w, info.current_h
        
        import os
        # Always clear positioning before calculating new one
        os.environ.pop('SDL_VIDEO_WINDOW_POS', None)
        os.environ.pop('SDL_VIDEO_CENTERED', None)
        
        if mode == "Fullscreen" or mode == "Borderless":
            # Modern 'Fullscreen' is borderless at native resolution
            # This prevents window rearranging and monitor flickering
            os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
            size = (native_w, native_h)
            flags = pygame.NOFRAME | pygame.DOUBLEBUF
        else: # Windowed
            # Center the window on the screen
            os.environ['SDL_VIDEO_CENTERED'] = '1'
            size = (win_w, win_h)
            flags = pygame.RESIZABLE  # Allow manual resizing and ensures title bar
            
        # DO NOT use pygame.display.quit() - it causes OS window shuffling
        # Simply calling set_mode again updates the existing window's flags/size
        screen = pygame.display.set_mode(size, flags)
        pygame.display.set_caption("Fire Watchers: Gideon & The Light")
        return screen

    screen = setup_display(game_settings)
    clock = pygame.time.Clock()
    
    # Controller Support
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    controller = None
    if joysticks:
        controller = joysticks[0]
        controller.init()
        print(f"Controller Connected: {controller.get_name()}")
    else:
        print("No Controller Detected - Keyboard Mode")
    
    # Audio System
    audio_manager = AudioManager()
    # Try to load audio files (will use placeholders if not found)
    audio_manager.load_sound("chop", "assets/sfx/chop.wav")
    audio_manager.load_sound("step", "assets/sfx/step.wav")
    audio_manager.load_sound("fire_crackle", "assets/sfx/fire.wav")
    audio_manager.load_sound("wind", "assets/sfx/wind.wav")
    # Generate placeholders if files don't exist
    audio_manager.generate_placeholder_sounds()
    
    # Save System
    save_manager = SaveManager()
    
    # Menu system
    menu = MenuSystem(SCREEN_WIDTH, SCREEN_HEIGHT, game_settings, save_manager)
    
    # Game objects
    player = None
    env_manager = EnvironmentManager()
    zone_manager = ZoneManager()
    tick_system = TickSystem(tick_interval=1.2)
    npc_manager = NPCManager()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    lighting_engine = LightingEngine(SCREEN_WIDTH, SCREEN_HEIGHT)
    weather_system = WeatherSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
    event_manager = EventManager()
    tutorial_manager = TutorialManager()
    run_state = None # Phase 2 Data Architecture
    
    # Hit-stop (freeze frames for impact)
    hitstop_frames = 0
    
    # Floating Text System
    floating_texts = []
    
    # Modern Notification System
    from ui.notifications import NotificationManager
    notification_manager = NotificationManager()
    
    # UI Font
    ui_font = pygame.font.SysFont("Papyrus", 18)
    
    # Dialogue System
    from ui.dialogue import DialogueBox
    dialogue_box = DialogueBox()
    
    # Debug Mode
    debug_mode = False

    # Shop State
    shop_active = False
    shop_selection = 0
    
    # Pre-load environment for Title Screen background
    bg_zone = zone_manager.get_zone(0)
    env_manager.load_zone(bg_zone, LOGICAL_WIDTH, LOGICAL_HEIGHT)
    
    running = True
    last_click_pos = None
    can_toggle_menu = True
    
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.1) # Clamp to prevent physics tunneling
        
        for event in pygame.event.get():
            # --- SHOP INPUT ---
            if shop_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                        shop_active = False
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        shop_selection = (shop_selection - 1) % 3
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        shop_selection = (shop_selection + 1) % 3
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_e:
                        items = [
                            {"id": "axe", "cost": 50},
                            {"id": "fur", "cost": 30},
                            {"id": "bags", "cost": 40}
                        ]
                        item = items[shop_selection]
                        cost = item["cost"]
                        
                        owned = False
                        if item["id"] == "axe" and run_state.axe_upgrade: owned = True
                        if item["id"] == "fur" and run_state.fur_lining: owned = True
                        if item["id"] == "bags" and run_state.deep_pockets: owned = True
                        
                        if not owned and run_state.log_stash >= cost:
                            run_state.log_stash -= cost
                            if item["id"] == "axe": run_state.axe_upgrade = True
                            if item["id"] == "fur": run_state.fur_lining = True
                            if item["id"] == "bags": run_state.deep_pockets = True
                            
                            audio_manager.play_sound("chop") 
                            notification_manager.add(f"PURCHASED UPGRADE!", 2.0, "success")
                        elif owned:
                            notification_manager.add("ALREADY OWNED", 1.0, "info")
                        else:
                            notification_manager.add("NOT ENOUGH LOGS IN STASH", 2.0, "warning")
                            
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 1: # B
                         shop_active = False
                continue

            # Input Detection for Tutorial
            if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]:
                tutorial_manager.set_device("keyboard")
            elif event.type in [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYHATMOTION]:
                tutorial_manager.set_device("controller")
            if event.type == pygame.QUIT:
                # Auto-save on quit if playing
                if menu.state == GameState.PLAYING and player and run_state:
                    save_manager.save_game(run_state, (player.pos.x, player.pos.y), zone_manager.stabilized_zones)
                running = False
            
            # --- MENU TOGGLE (ESC DEBOUNCE) ---
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    can_toggle_menu = True
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if can_toggle_menu:
                    can_toggle_menu = False
                    
                    if shop_active:
                        shop_active = False
                    elif menu.state == GameState.PLAYING:
                        menu.state = GameState.PAUSED
                        menu.selected_index = 0
                        menu.update_menu_options()
                    elif menu.state == GameState.PAUSED:
                        menu.state = GameState.PLAYING
                    elif menu.state == GameState.MAIN_MENU and player and run_state:
                        menu.state = GameState.PLAYING 
                continue # Skip other checks for this event
            
            # Menu input handling
            if menu.state != GameState.PLAYING:
                action = menu.handle_input(event)
                if action == "new_game":
                    # Delete old save to start fresh
                    save_manager.delete_save()
                    
                    zone_manager.reset()
                    run_state = RunState()
                    
                    initial_zone = zone_manager.get_zone(run_state.current_zone_id)
                    env_manager.load_zone(initial_zone, LOGICAL_WIDTH, LOGICAL_HEIGHT)
                    if run_state.zone_1_stabilized:
                        env_manager.setup_haven()
                    
                    player = Player()
                    # Zone 0 tutorial: spawn at specific position
                    if run_state.current_zone_id == 0:
                        player.pos.x, player.pos.y = 100, 300
                    weather_system.set_zone_weather(run_state.current_zone_id)
                    npc_manager.clear_npcs()
                    npc_manager.spawn_npc_for_zone(initial_zone, run_state, LOGICAL_WIDTH, LOGICAL_HEIGHT)
                    print("New game started")
                    if audio_manager.music:
                        audio_manager.music.start_theme()
                elif action == "continue_game" or action == "load_game":
                    save_data = save_manager.load_game()
                    if save_data:
                        run_state = save_data["run_state"]
                        player_pos = save_data["player_pos"]
                        stabilized_zones = save_data.get("stabilized_zones", [])
                        zone_manager.load_stabilized_zones(stabilized_zones)
                        zone = zone_manager.get_zone(run_state.current_zone_id)
                        env_manager.load_zone(zone, LOGICAL_WIDTH, LOGICAL_HEIGHT, safe_pos=player_pos)
                        if run_state.current_zone_id == 1 and run_state.zone_1_stabilized:
                            env_manager.setup_haven()
                        player = Player()
                        player.pos.x, player.pos.y = player_pos
                        weather_system.set_zone_weather(run_state.current_zone_id)
                        npc_manager.clear_npcs()
                        npc_manager.spawn_npc_for_zone(zone, run_state, LOGICAL_WIDTH, LOGICAL_HEIGHT)
                        if audio_manager.music:
                            audio_manager.music.start_theme()
                        print("Game continued")
                    else:
                        print("Failed to load save, starting new game")
                        run_state = RunState()
                        initial_zone = zone_manager.get_zone(run_state.current_zone_id)
                        env_manager.load_zone(initial_zone, LOGICAL_WIDTH, LOGICAL_HEIGHT)
                        player = Player()
                        weather_system.set_zone_weather(run_state.current_zone_id)
                        npc_manager.clear_npcs()
                        npc_manager.spawn_npc_for_zone(initial_zone, run_state, LOGICAL_WIDTH, LOGICAL_HEIGHT)
                elif action == "settings_applied":
                    screen = setup_display(game_settings)
                elif action == "quit":
                    running = False
                elif action == "save_game":
                    if player and run_state:
                         save_manager.save_game(run_state, (player.pos.x, player.pos.y), zone_manager.stabilized_zones)
                         menu.update_menu_options()  # Refresh menu to show Continue option
                elif action == "quit_to_title":
                    if audio_manager:
                        audio_manager.stop_sound("wind")
            else:
                # In-game input
                if event.type == pygame.KEYDOWN:
                    # Dialogue system input
                    if dialogue_box.active:
                        if event.key == pygame.K_SPACE:
                            dialogue_box.advance()
                    else:
                        # Normal gameplay input
                        if event.key == pygame.K_s and player and run_state:
                             save_manager.save_game(run_state, (player.pos.x, player.pos.y), zone_manager.stabilized_zones)
                             menu.update_menu_options()  # Refresh menu to show Continue option
                        elif event.key == pygame.K_F3:
                             debug_mode = not debug_mode
                             print(f"Debug Mode: {debug_mode}")
                        elif event.key == pygame.K_e and player and env_manager:
                            # Check for NPC interaction
                            npc_to_talk = None
                            if env_manager.npc:
                                dist = (player.pos - env_manager.npc.pos).length()
                                if dist < 80 and env_manager.npc.dialogue_lines:
                                    npc_to_talk = env_manager.npc
                            
                            # Check regular NPCs too
                            if not npc_to_talk:
                                for npc in npc_manager.npcs:
                                    dist = (player.pos - npc.pos).length()
                                    if dist < 80 and npc.dialogue_lines:
                                        npc_to_talk = npc
                                        break
                            
                            if npc_to_talk:
                                # Shop Trigger
                                is_builder_shop = False
                                if run_state.current_zone_id == 3 and env_manager.construction_site:
                                    if run_state.shack_progress["state"] >= 3:
                                         is_builder_shop = True
                                
                                if is_builder_shop:
                                    shop_active = True
                                    shop_selection = 0
                                else:
                                    dialogue_box.start_dialogue(npc_to_talk.dialogue_lines)
                            elif env_manager.construction_site:
                                dist = (pygame.Vector2(env_manager.construction_site.rect.center) - player.pos).length()
                                if dist < 100:
                                    prog = run_state.shack_progress
                                    
                                    # LINKED FIRE CHECK
                                    can_build = True
                                    site = env_manager.construction_site
                                    if hasattr(site, 'linked_fire') and site.linked_fire:
                                        if not site.linked_fire.is_lit:
                                            can_build = False
                                            floating_texts.append(FloatingText(site.rect.centerx, site.rect.y - 40, "LIGHT THE FIRE TO WORK", (255, 100, 100)))
                                    
                                    if can_build and prog["state"] < 3 and run_state.inventory["logs"] > 0:
                                        run_state.inventory["logs"] -= 1
                                        prog["logs"] += 1
                                        site.update_state(run_state)
                                        
                                        import time
                                        run_state.last_log_deposit_time = time.time()
                                        
                                        audio_manager.play_sound("chop")
                                        floating_texts.append(FloatingText(player.pos.x, player.pos.y - 40, "+ LOG", (200, 200, 200)))
                
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: # A Button
                         if dialogue_box.active:
                             dialogue_box.advance()
                         elif player and env_manager:
                             # Check for NPC interaction (Ported from Keyboard K_e)
                             npc_to_talk = None
                             if env_manager.npc:
                                 dist = (player.pos - env_manager.npc.pos).length()
                                 if dist < 80 and env_manager.npc.dialogue_lines:
                                     npc_to_talk = env_manager.npc
                             if not npc_to_talk:
                                 for npc in npc_manager.npcs:
                                     dist = (player.pos - npc.pos).length()
                                     if dist < 80 and npc.dialogue_lines:
                                         npc_to_talk = npc
                                         break
                             if npc_to_talk:
                                 dialogue_box.start_dialogue(npc_to_talk.dialogue_lines)
                             elif env_manager.construction_site:
                                dist = (pygame.Vector2(env_manager.construction_site.rect.center) - player.pos).length()
                                if dist < 100:
                                    prog = run_state.shack_progress
                                    
                                    # LINKED FIRE CHECK (Controller)
                                    can_build = True
                                    site = env_manager.construction_site
                                    if hasattr(site, 'linked_fire') and site.linked_fire:
                                        if site.linked_fire.fuel <= 0:
                                            can_build = False
                                            floating_texts.append(FloatingText(site.rect.centerx, site.rect.y - 40, "LIGHT THE FIRE TO WORK", (255, 100, 100)))

                                    if can_build and prog["state"] < 3 and run_state.inventory["logs"] > 0:
                                        run_state.inventory["logs"] -= 1
                                        prog["logs"] += 1
                                        site.update_state(run_state)
                                        
                                        import time
                                        run_state.last_log_deposit_time = time.time()
                                        
                                        audio_manager.play_sound("chop")
                                        floating_texts.append(FloatingText(player.pos.x, player.pos.y - 40, "+ LOG", (200, 200, 200)))

                    elif event.button == 7:
                        menu.state = GameState.PAUSED
                        menu.selected_index = 0
                        menu.update_menu_options()
        
        # Update Menu (Timers/Animations)
        menu.update(dt)
        
        # Update Dialogue System
        dialogue_box.update(dt)
        
        # Update game if playing
        if menu.state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER] and player and run_state:
            # Hit-stop (freeze frames)
            if hitstop_frames > 0:
                hitstop_frames -= 1
                # Skip all updates during hit-stop, only render
            elif menu.state == GameState.PLAYING and not dialogue_box.active:
                # Centralized Tick System (handles all survival logic)
                # PAUSED during dialogue to stop world
                tick_system.update(dt, run_state, env_manager, player, floating_texts, event_manager)
                
                # Death Trigger
                if run_state.body_temp <= 0 and run_state.is_alive:
                    run_state.is_alive = False
                    # Capture current screen for death background
                    menu.show_death_screen(pygame.display.get_surface())
                    if audio_manager:
                        audio_manager.play_sound("wind", volume=1.0) # Cold wind howl
                    print("[DEATH] Gideon has fallen to the cold.")
                
                # Event Update (warning, duration, logic)
                event_manager.update(dt, run_state, audio_manager, camera)
                
                # Environment updates (particles, animations)
                env_manager.update(dt)
                tutorial_manager.update(dt, run_state, player)
                
                # Update trees (shake, flash)
                for tree in env_manager.trees:
                    tree.update(dt)
                
                # Weather updates (snow, wind, gusting)
                weather_system.update(dt, audio_manager)
                
                # --- REDEMPTION EVENT LOGIC ---
                if player.redemption_event:
                    player.redemption_event = False
                    if not run_state.zone_2_redeemed:
                        event_manager.active_event = "REDEMPTION"
                        event_manager.redemption_stage = 0
                        if npc_manager.npcs:
                            event_manager.npc_ref = npc_manager.npcs[0]
                        else:
                            event_manager.npc_ref = npc_manager.spawn_npc_for_zone(env_manager.current_zone, False, LOGICAL_WIDTH, LOGICAL_HEIGHT)
                        
                        # Ensure Visuals
                        event_manager.npc_ref.npc_type = "saboteur"
                        event_manager.npc_ref.render_cache()

                if event_manager.active_event == "REDEMPTION":
                     # CUTSCENE CONTROL
                     npc = event_manager.npc_ref
                     if npc:
                         if event_manager.redemption_stage == 0:
                             # Move NPC to player
                             target = pygame.Vector2(player.pos.x, player.pos.y + 60)
                             diff = target - npc.pos
                             if diff.length() > 5:
                                 npc.pos += diff.normalize() * dt * 80
                                 npc.is_moving = True
                                 if abs(diff.y) > abs(diff.x): npc.facing = "UP" if diff.y < 0 else "DOWN"
                                 else: npc.facing = "SIDE"; npc.flip_h = diff.x < 0
                                 npc.render_cache()
                             else:
                                 npc.is_moving = False
                                 event_manager.redemption_stage = 1
                         
                         elif event_manager.redemption_stage == 1:
                             # Start Dialogue
                             lines = [
                                "Wait! Don't swing.",
                                "I've been looking for wood to build a shelter. I thought you were just passing through.",
                                "People usually don't stay to keep this valley warm.",
                                "I'm heading up the ridge. If you bring wood there... we can build something permanent."
                             ]
                             dialogue_box.start_dialogue(lines)
                             event_manager.redemption_stage = 2
                         
                         elif event_manager.redemption_stage == 2:
                             # Wait for Dialogue
                             if not dialogue_box.active:
                                 event_manager.redemption_stage = 3
                         
                         elif event_manager.redemption_stage == 3:
                             # Resolve
                             run_state.zone_2_redeemed = True
                             zone_manager.stabilize_zone(2)
                             if npc in npc_manager.npcs: npc_manager.npcs.remove(npc)
                             event_manager.active_event = None
                             notification_manager.add("THE WIND GAP IS STABILIZED", 4.0, "success")
                else:
                    # Normal Gameplay Updates
                    npc_manager.update(dt, run_state, env_manager)
                
                    old_pos = (player.pos.x, player.pos.y)
                    player.update(dt, env_manager.trees, env_manager, controller, run_state, camera, floating_texts, audio_manager)
                
                # Tutorial progression (Zone 0 only)
                if run_state.current_zone_id == 0 and not run_state.tutorial_completed:
                    # Track movement distance
                    if run_state.tutorial_step == 0:
                        dist = ((player.pos.x - old_pos[0])**2 + (player.pos.y - old_pos[1])**2)**0.5
                        run_state.distance_moved += dist
                        if run_state.distance_moved >= 100:
                            run_state.tutorial_step = 1
                            notification_manager.add("GOOD! NOW GATHER WOOD", 3.0, "success")
                    
                    # Check for log collection
                    elif run_state.tutorial_step == 1:
                        if run_state.inventory["logs"] >= 1:
                            run_state.tutorial_step = 2
                            notification_manager.add("EXCELLENT! FEED THE FIRE", 3.0, "success")
                    
                    # Tutorial step 2 is advanced by player interaction (see player.py)
                    # Step 3 is set when fire is fueled in tutorial zone
                
                # Update floating texts
                floating_texts = [ft for ft in floating_texts if ft.update(dt)]
            
            # Trigger hit-stop if player hit something
            if player.hit_impact:
                hitstop_frames = 3
                player.hit_impact = False # Reset flag
            
            # Stabilization Event Feedback
            if player.stabilization_event:
                player.stabilization_event = False
                audio_manager.play_sound("ice_crack")
                notification_manager.add("ZONE 1 STABILIZED - PATH TO THE WIND GAP OPEN", 5.0, "success")
                
                # Visual Flash
                flash_surf = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
                flash_surf.fill((255, 255, 255))
                game_surface.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_ADD)
                pygame.display.flip()
                pygame.time.delay(100) # Short freeze for impact
                
                if run_state.current_zone_id == 1:
                    env_manager.setup_haven()
                    # Respawn NPCs (Swaps Saboteurs for Elder)
                    npc_manager.clear_npcs()
                    npc_manager.spawn_npc_for_zone(env_manager.current_zone, run_state, LOGICAL_WIDTH, LOGICAL_HEIGHT)
                    
                    # Narrative: Builder moves to Zone 2
                    if run_state.builder_location == 1:
                        run_state.builder_location = 2
                        print("Builder moved to Zone 2")
                if audio_manager.music:
                    audio_manager.music.play_win_jingle()
            
            
            # Zone Transition Logic
            transition_zone = 0
            if player.pos.x >= LOGICAL_WIDTH - 20: # Right Edge
                if run_state.current_zone_id == 0:
                    # Tutorial -> Zone 1 (only if step 3 complete)
                    if run_state.tutorial_step >= 3:
                        transition_zone = 1
                        player.pos.x = 20
                        run_state.tutorial_completed = True
                        notification_manager.add("ENTERING THE QUIET WOODS", 4.0, "info")
                    else:
                        # Block exit if tutorial not complete
                        player.pos.x = LOGICAL_WIDTH - 30
                        
                elif run_state.current_zone_id == 1 and run_state.zone_1_stabilized:
                    # Resource Exhaustion
                    from constants import MAX_LOG_SLOTS
                    if run_state.inventory["logs"] >= MAX_LOG_SLOTS:
                         run_state.zone_1_resources_depleted = True
                    
                    # MANDATORY TALK CHECK (User Request)
                    # Block exit if player hasn't "talked" to Elder.
                    # We'll simulate this by requiring them to be near the Elder at least once?
                    # Or just allow it for now but spawn the text "DID YOU SPEAK TO THE ELDER?"
                    
                    transition_zone = 2
                    player.pos.x = 20 # Spawn on left side of Z2
                    notification_manager.add("ENTERING THE WIND GAP", 4.0, "info")
                    
                    # Auto-set Builder Location to 2 if moving
                    run_state.builder_location = 2
                elif run_state.current_zone_id == 2:
                     # Save Hub Fire State
                     if env_manager.construction_site and env_manager.construction_site.linked_fire:
                         run_state.zone_2_hub_fire_fuel = env_manager.construction_site.linked_fire.fuel

                     # Transition to Zone 3 (The Peak) logic
                     if run_state.logs_deposited_in_zone_2 >= 30: # Builder Quest
                         transition_zone = 3
                         player.pos.x = LOGICAL_WIDTH // 2
                         player.pos.y = LOGICAL_HEIGHT - 60
                         notification_manager.add("THE PEAK AWAITS", 4.0, "info")
                     else:
                         player.pos.x = LOGICAL_WIDTH - 30
                         notification_manager.add("FINISH THE SHELTER FIRST!", 3.0, "warning")
                         
                elif run_state.current_zone_id == 3:
                     # End of the world
                     player.pos.x = min(player.pos.x, LOGICAL_WIDTH - 20)
                         

            elif player.pos.x <= -60: # Left Edge (Back to Z1)
                if run_state.current_zone_id == 2:
                    # CONSTRAINT: Cannot retreat during Cold Snap
                    if event_manager.active_event == "COLD_SNAP":
                         player.pos.x = -50 # Bounce back
                         notification_manager.add("THE WIND IS TOO STRONG TO RETREAT!", 3.0, "danger")
                         audio_manager.play_sound("wind", volume=1.0)
                    else:
                        transition_zone = 1
                        player.pos.x = LOGICAL_WIDTH - 150 # Spawn on right side of Z1
                elif run_state.current_zone_id == 3:
                    transition_zone = 2
                    player.pos.x = LOGICAL_WIDTH - 150

            if transition_zone > 0:
                run_state.current_zone_id = transition_zone
                run_state.time_in_current_zone = 0.0  # Reset grace period timer
                new_zone = zone_manager.get_zone(transition_zone)
                print(f"Entering Zone {transition_zone}: {new_zone.name}")
                env_manager.load_zone(new_zone, LOGICAL_WIDTH, LOGICAL_HEIGHT, safe_pos=(player.pos.x, player.pos.y))
                
                # Haven Setup if returning to stabilized Zone 1
                if transition_zone == 1 and run_state.zone_1_stabilized:
                    env_manager.setup_haven()

                player.render_cache(player.get_current_palette(run_state))
                
                weather_system.clear()
                weather_system.set_zone_weather(transition_zone)
                
                npc_manager.clear_npcs()
                npc_manager.clear_npcs()
                npc_manager.spawn_npc_for_zone(new_zone, run_state, LOGICAL_WIDTH, LOGICAL_HEIGHT)
                
                # Restore Hub Fire Fuel if Z2
                if transition_zone == 2 and env_manager.construction_site and env_manager.construction_site.linked_fire:
                    fuel = getattr(run_state, "zone_2_hub_fire_fuel", 0.0)
                    env_manager.construction_site.linked_fire.fuel = fuel
                    env_manager.construction_site.linked_fire.is_lit = (fuel > 0)
            
            # Update camera (follows player with smoothing and look-ahead)
            player_velocity = (player.pos.x - getattr(player, 'last_x', player.pos.x),
                             player.pos.y - getattr(player, 'last_y', player.pos.y))
            player.last_x = player.pos.x
            player.last_y = player.pos.y
            camera.update(dt, player.pos.x, player.pos.y, player_velocity)
        
        # Rendering
        if menu.state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER] and player and run_state:
            # Create render surface at logical resolution
            game_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            
            # Game rendering
            env_manager.render(game_surface) 
            env_manager.draw_border(game_surface, run_state, dt)
            
            # Y-Sort Entities (Player, NPCs, Trees, Fires)
            render_list = []
            render_list.append((player.pos.y, player, "PLAYER"))
            
            for npc in npc_manager.npcs:
                render_list.append((npc.pos.y, npc, "NPC"))
            
            for tree in env_manager.trees:
                render_list.append((tree.rect.bottom, tree, "TREE"))
            for fire in env_manager.campfires:
                 render_list.append((fire.rect.bottom, fire, "CAMPFIRE"))
            
            # Stockpile and Haven NPC
            if env_manager.stockpile:
                render_list.append((env_manager.stockpile.rect.bottom, env_manager.stockpile, "STOCKPILE"))
            if env_manager.npc:
                render_list.append((env_manager.npc.rect.bottom, env_manager.npc, "HAVEN_NPC"))
            
            for stick in env_manager.sticks:
                if not stick.consumed:
                    render_list.append((stick.pos.y, stick, "STICK"))
            for df in env_manager.deadfalls:
                render_list.append((df.pos.y, df, "DEADFALL"))
            
            if env_manager.construction_site:
                site = env_manager.construction_site
                render_list.append((site.rect.bottom, site, "CONSTRUCTION_SITE"))
            
            render_list.sort(key=lambda x: x[0])
            
            for _, obj, type_ in render_list:
                if type_ == "PLAYER":
                    obj.draw_light(game_surface)
                    obj.draw(game_surface)
                elif type_ == "NPC" or type_ == "HAVEN_NPC":
                    obj.draw(game_surface)
                elif type_ == "STOCKPILE":
                    obj.render(game_surface, run_state)
                elif type_ == "STOCKPILE":
                    obj.render(game_surface, run_state)
                elif type_ == "CONSTRUCTION_SITE":
                    obj.render(game_surface, run_state)
                elif type_ == "SIGNAL_FIRE":
                    obj.render(game_surface, run_state)
                else:
                    obj.render(game_surface)
                    obj.render(game_surface)
            
            # DEBUG MODE: Hitbox Visualization
            if debug_mode:
                # Player interaction hitbox (BLUE)
                if hasattr(player, 'target_hitbox') and player.target_hitbox:
                    pygame.draw.rect(game_surface, (0, 100, 255), player.target_hitbox, 2)
                    # Fill with semi-transparent blue
                    debug_surf = pygame.Surface((player.target_hitbox.width, player.target_hitbox.height), pygame.SRCALPHA)
                    debug_surf.fill((0, 100, 255, 60))
                    game_surface.blit(debug_surf, player.target_hitbox.topleft)
                
                # Tree stump hitboxes (RED)
                for tree in env_manager.trees:
                    if tree.state == tree.STATE_FULL:
                        pygame.draw.rect(game_surface, (255, 50, 50), tree.stump_rect, 2)
                        # Fill with semi-transparent red
                        debug_surf = pygame.Surface((tree.stump_rect.width, tree.stump_rect.height), pygame.SRCALPHA)
                        debug_surf.fill((255, 50, 50, 60))
                        game_surface.blit(debug_surf, tree.stump_rect.topleft)
                
                # Debug text
                debug_font = pygame.font.SysFont("Consolas", 12)
                debug_text = debug_font.render("DEBUG MODE (F3 to toggle)", True, (255, 255, 0))
                game_surface.blit(debug_text, (10, LOGICAL_HEIGHT - 25))

            env_manager.render_particles(game_surface)
            weather_system.render(game_surface)
            
            lighting_engine.clear_lights()
            lighting_engine.add_player_light(player.pos.x + 36, player.pos.y + 48)
            for fire in env_manager.campfires:
                if fire.fuel > 0:
                    fuel_percent = fire.fuel / 100.0
                    lighting_engine.add_fire_light(fire.rect.centerx, fire.rect.centery - 10, fuel_percent)
            for npc in npc_manager.npcs:
                lighting_engine.add_torch_light(npc.pos.x + 36, npc.pos.y + 48)
            
            lighting_engine.update(dt)
            lighting_engine.render(game_surface)
            
            # UI Rendering
            event_manager.render(game_surface, LOGICAL_WIDTH, LOGICAL_HEIGHT)
            for ft in floating_texts:
                ft.render(game_surface)
            
            draw_cold_overlay(game_surface, run_state.body_temp, LOGICAL_WIDTH, LOGICAL_HEIGHT)
            draw_inventory_ui(game_surface, run_state, LOGICAL_WIDTH, LOGICAL_HEIGHT, active_tool=player.active_tool)
            draw_survival_panel(game_surface, run_state, tick_system, LOGICAL_WIDTH, LOGICAL_HEIGHT, event_manager)
            
            draw_stabilization_ui(game_surface, run_state, LOGICAL_WIDTH, LOGICAL_HEIGHT)
                
            # Tutorial UI (Zone 0 only)
            tutorial_manager.render(game_surface, run_state, LOGICAL_WIDTH, LOGICAL_HEIGHT, env_manager, player)
            
            # Dialogue Box (renders on top of everything)
            dialogue_box.render(game_surface, LOGICAL_WIDTH, LOGICAL_HEIGHT)
            
            # Shop Menu
            if shop_active:
                draw_shop_menu(game_surface, run_state, shop_selection, run_state.log_stash)

            # Modern Notifications
            notification_manager.update(dt)
            notification_manager.render(game_surface, LOGICAL_WIDTH, LOGICAL_HEIGHT)
            
            # Safe Visuals: Warm Tint in stabilized Zone 1
            if run_state.current_zone_id == 1 and run_state.zone_1_stabilized:
                warm_overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
                warm_overlay.fill((100, 50, 0, 30)) # Subtle orange
                game_surface.blit(warm_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # FINAL BLIT: Scale game_surface to fit screen
            screen_w, screen_h = screen.get_size()
            shake_offset = camera.get_shake_offset()
            
            scale = min(screen_w / LOGICAL_WIDTH, screen_h / LOGICAL_HEIGHT)
            new_w, new_h = int(LOGICAL_WIDTH * scale), int(LOGICAL_HEIGHT * scale)
            scaled_game = pygame.transform.scale(game_surface, (new_w, new_h))
            
            ox, oy = (screen_w - new_w) // 2, (screen_h - new_h) // 2
            sx, sy = int(shake_offset[0] * scale), int(shake_offset[1] * scale)
            
            screen.fill((0, 0, 0))
            screen.blit(scaled_game, (ox + sx, oy + sy))

            if menu.state != GameState.PLAYING:
                menu.screen_width, menu.screen_height = screen_w, screen_h
                menu.draw(screen, run_state)
        else:
            # Special dynamic background for Main Menu
            if menu.state == GameState.MAIN_MENU:
                 game_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
                 
                 # Camera Pan (Auto-scroll right)
                 camera.x += 0.5
                 
                 # Updates
                 env_manager.update(dt)
                 weather_system.snow_enabled = True
                 weather_system.update(dt, None) # No audio manager passed to avoid wind noise loop issues? Or pass it?
                 # If I pass audio_manager, wind might start playing. 
                 # User requested "Atmospheric". Wind sound is good.
                 # But previous crash was stop_sound wind.
                 # I'll pass audio_manager if safe.
                 
                 # Render World
                 offset = camera.get_offset()
                 env_manager.render(game_surface, offset=offset)
                 env_manager.render_particles(game_surface, offset=offset)
                 weather_system.render(game_surface)
                 
                 # Scaling & Blit
                 screen_w, screen_h = screen.get_size()
                 scale = min(screen_w / LOGICAL_WIDTH, screen_h / LOGICAL_HEIGHT)
                 new_w, new_h = int(LOGICAL_WIDTH * scale), int(LOGICAL_HEIGHT * scale)
                 scaled_game = pygame.transform.scale(game_surface, (new_w, new_h))
                 ox, oy = (screen_w - new_w) // 2, (screen_h - new_h) // 2
                 
                 screen.fill((10, 10, 15)) # Dark background behind viewport
                 screen.blit(scaled_game, (ox, oy))
                 
                 menu.screen_width, menu.screen_height = screen_w, screen_h
            else:
                 menu.screen_width, menu.screen_height = screen.get_size()
                 
            menu.draw(screen, run_state)
        
        pygame.display.flip()

    # pygame.quit() and sys.exit() moved to global finally block

def draw_game_ui(screen, run_state, font, screen_width, screen_height, game_settings=None, fps=0, debug_mode=False):
    """Draw minimal HUD (FPS and controls)."""
    # FPS counter (top-right) if enabled
    if game_settings and game_settings.get("graphics", "show_fps"):
        fps_text = font.render(f"FPS: {int(fps)}", True, (100, 255, 100))
        screen.blit(fps_text, (screen_width - 100, 20))
    
    # Controls hint (bottom-left)
    controls = font.render("F: Ignite | TAB: Tool | S: Save | ESC: Pause", True, (120, 120, 120))
    screen.blit(controls, (20, screen_height - 30))

if __name__ == "__main__":
    try:
        import os
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        main()
    except Exception as e:
        import traceback
        crash_msg = traceback.format_exc()
        
        # Log to file
        with open("crash_log.txt", "w") as f:
            f.write(crash_msg)
            
        # Print to console
        print("\n" + "!" * 50)
        print("CRITICAL GAME CRASH DETECTED")
        print("!" * 50)
        print(crash_msg)
        print("!" * 50)
        print("Crash details saved to crash_log.txt")
        
        # Show popup alert
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Fire Watchers - Critical Error", 
                                f"Gideon & The Light has encountered a critical error.\n\n"
                                f"Error: {str(e)}\n\n"
                                f"Full details have been saved to crash_log.txt")
            root.destroy()
        except:
            pass # Fallback to console if TK is not available
            
    finally:
        pygame.quit()
        sys.exit()
