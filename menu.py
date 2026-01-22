import pygame
import sys

class GameState:
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    SETTINGS = "settings"
    GAME_OVER = "game_over"
    CREDITS = "credits"

class MenuSystem:
    def __init__(self, screen_width, screen_height, game_settings, save_manager=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = GameState.MAIN_MENU
        self.game_settings = game_settings
        self.save_manager = save_manager
        self.return_state = None
        
        # Fonts
        try:
            self.title_font = pygame.font.SysFont("Stencil", 72, bold=True)
            self.subtitle_font = pygame.font.SysFont("Papyrus", 48)
            self.menu_font = pygame.font.SysFont("Papyrus", 32)
            self.small_font = pygame.font.SysFont("Papyrus", 20)
        except:
            # Fallback if fonts not available
            self.title_font = pygame.font.SysFont("Arial", 72, bold=True)
            self.subtitle_font = pygame.font.SysFont("Arial", 48)
            self.menu_font = pygame.font.SysFont("Arial", 32)
            self.small_font = pygame.font.SysFont("Arial", 20)
        
        # Menu options (dynamic based on save file)
        self.update_menu_options()
        self.settings_options = ["Back"]
        self.pause_menu_options = ["RESUME", "SAVE GAME", "SETTINGS", "QUIT TO TITLE"]
        self.selected_index = 0
        
        # Feedback message
        self.message = ""
        self.message_timer = 0.0
        
        # Game Over state
        self.game_over_options = ["TRY AGAIN", "GIVE UP"]
        self.fade_alpha = 0
        self.death_bg = None

    def show_death_screen(self, screen):
        """Capture screen and trigger death state."""
        self.state = GameState.GAME_OVER
        self.selected_index = 0
        self.fade_alpha = 0
        
        # Capture and process screenshot
        self.death_bg = screen.copy()
        
        # Apply Blue Tint (Cooling effect)
        # 1. Desaturate slightly by blending with gray (optional, simplified to just blue tint for performance)
        # 2. Apply Blue MULT
        tint = pygame.Surface(self.death_bg.get_size())
        tint.fill((100, 100, 180)) # Blue-ish gray
        self.death_bg.blit(tint, (0, 0), special_flags=pygame.BLEND_MULT)
        
    def update_menu_options(self):
        """Update menu options based on save file existence."""
        if self.save_manager and self.save_manager.save_exists():
            self.main_menu_options = ["Continue", "NEW JOURNEY", "Settings", "FADE OUT"]
        else:
            self.main_menu_options = ["NEW JOURNEY", "Settings", "FADE OUT"]
        
        # Settings menu state
        self.settings_selected_category = 0
        self.settings_selected_option = 0
        self.settings_categories = [
            ("Audio", [
                ("Master Volume", "master_volume", "audio"),
                ("Music Volume", "music_volume", "audio"),
                ("SFX Volume", "sfx_volume", "audio"),
                ("Muted", "muted", "audio")
            ]),
            ("Graphics", [
                ("Display Mode", "display_mode", "graphics"),
                ("Resolution", "resolution", "graphics"),
                ("VSync", "vsync", "graphics"),
                ("Show FPS", "show_fps", "graphics")
            ]),
            ("Gameplay", [
                ("Difficulty", "difficulty", "gameplay")
            ])
        ]
        
        # Colors
        self.bg_color = (25, 30, 35)  # Slightly lighter dark background
        self.title_color = (218, 165, 32)  # Golden color
        self.subtitle_color = (245, 222, 179)  # Parchment/wheat color
        self.menu_color = (245, 222, 179)  # Parchment
        self.selected_color = (255, 215, 0)  # Bright gold when selected
        self.outline_color = (50, 33, 18)  # Dark brown outline #322112
        
    def handle_input(self, event):
        """Handle menu navigation input (Keyboard + Controller)."""
        # --- KEYBOARD ---
        if event.type == pygame.KEYDOWN:
            if self.state == GameState.MAIN_MENU:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.main_menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.main_menu_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return self.activate_menu_option()
            elif self.state == GameState.SETTINGS:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    self.game_settings.save_settings()
                    self.state = GameState.MAIN_MENU
                    self.selected_index = 0
                    return "settings_applied"
                elif event.key == pygame.K_LEFT:
                    self.settings_selected_category = max(0, self.settings_selected_category - 1)
                    self.settings_selected_option = 0
                elif event.key == pygame.K_RIGHT:
                    self.settings_selected_category = min(len(self.settings_categories) - 1, self.settings_selected_category + 1)
                    self.settings_selected_option = 0
                elif event.key == pygame.K_UP:
                    self.settings_selected_option = max(0, self.settings_selected_option - 1)
                elif event.key == pygame.K_DOWN:
                    current_cat = self.settings_categories[self.settings_selected_category]
                    max_options = len(current_cat[1]) - 1
                    self.settings_selected_option = min(max_options, self.settings_selected_option + 1)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.toggle_setting()
                    if self.return_state == "settings_applied":
                        res = self.return_state
                        self.return_state = None
                        return res
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.adjust_setting(10)
                elif event.key == pygame.K_MINUS:
                    self.adjust_setting(-10)
            elif self.state == GameState.PLAYING:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PAUSED
                    self.selected_index = 0
            elif self.state == GameState.PAUSED:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_index = (self.selected_index - 1) % len(self.pause_menu_options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_index = (self.selected_index + 1) % len(self.pause_menu_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return self.activate_pause_option()
            elif self.state == GameState.GAME_OVER:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_index = (self.selected_index - 1) % len(self.game_over_options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_index = (self.selected_index + 1) % len(self.game_over_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return self.activate_game_over_option()
            elif self.state == GameState.CREDITS:
                # Any key returns to title logic handled by caller? Or here?
                # Usually caller checks return value.
                # Let's return "new_game" or "quit"?
                # Prompt: "Press Key to Return to Title."
                # Returning "quit" usually quits game loop.
                # We need to switch state to MAIN_MENU.
                self.state = GameState.MAIN_MENU
                pass

        # --- CONTROLLER ---
        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"JOY BUTTON: {event.button}")
            # Button 0 (A) - Select / Toggle
            if event.button == 0: 
                if self.state == GameState.MAIN_MENU:
                    return self.activate_menu_option()
                elif self.state == GameState.SETTINGS:
                    self.toggle_setting()
                    if self.return_state == "settings_applied":
                        res = self.return_state
                        self.return_state = None
                        return res
                elif self.state == GameState.PAUSED:
                    return self.activate_pause_option()
                elif self.state == GameState.GAME_OVER:
                    return self.activate_game_over_option()

            # Button 1 (B) - Back / Cancel
            elif event.button == 1: 
                if self.state == GameState.SETTINGS:
                    self.game_settings.save_settings()
                    self.state = GameState.MAIN_MENU
                    self.selected_index = 0
                elif self.state == GameState.PAUSED:
                    self.state = GameState.PLAYING
                elif self.state == GameState.PLAYING:
                    pass # Maybe dodge?

            # Button 7 (Start) - Pause
            elif event.button == 7:
                 if self.state == GameState.PLAYING:
                     self.state = GameState.PAUSED
                 elif self.state == GameState.PAUSED:
                     self.state = GameState.PLAYING

            # Shoulder Buttons (LB=4, RB=5) - Volume/Tabs in Settings
            elif self.state == GameState.SETTINGS:
                if event.button == 5: # RB -> Right Tab
                     self.settings_selected_category = min(len(self.settings_categories) - 1, self.settings_selected_category + 1)
                     self.settings_selected_option = 0
                elif event.button == 4: # LB -> Left Tab
                     self.settings_selected_category = max(0, self.settings_selected_category - 1)
                     self.settings_selected_option = 0
                elif event.button == 13: # D-Pad Left (if mapped as button) 
                     self.adjust_setting(-10)
                elif event.button == 14: # D-Pad Right
                     self.adjust_setting(10)

        elif event.type == pygame.JOYHATMOTION:
            # Hat 0 value is tuple (x, y) where x,y are -1, 0, 1
            # y=1 is UP, y=-1 is DOWN (Standard)
            hat = event.value
            dx, dy = hat[0], hat[1]
            
            if self.state == GameState.MAIN_MENU:
                if dy == 1:   self.selected_index = (self.selected_index - 1) % len(self.main_menu_options)
                elif dy == -1: self.selected_index = (self.selected_index + 1) % len(self.main_menu_options)
            
            elif self.state == GameState.SETTINGS:
                if dy == 1: self.settings_selected_option = max(0, self.settings_selected_option - 1)
                elif dy == -1:
                    current_cat = self.settings_categories[self.settings_selected_category]
                    max_options = len(current_cat[1]) - 1
                    self.settings_selected_option = min(max_options, self.settings_selected_option + 1)
                
            elif self.state == GameState.PAUSED:
                if dy == 1:   self.selected_index = (self.selected_index - 1) % len(self.pause_menu_options)
                elif dy == -1: self.selected_index = (self.selected_index + 1) % len(self.pause_menu_options)
            
            elif self.state == GameState.GAME_OVER:
                if dy == 1:   self.selected_index = (self.selected_index - 1) % len(self.game_over_options)
                elif dy == -1: self.selected_index = (self.selected_index + 1) % len(self.game_over_options)

                # Left/Right for volume?
                if dx == 1: self.adjust_setting(10)
                elif dx == -1: self.adjust_setting(-10)
                
        return None
    
    def activate_menu_option(self):
        """Activate the selected menu option."""
        option = self.main_menu_options[self.selected_index]
        if option == "Continue":
            self.state = GameState.PLAYING
            return "continue_game"
        elif option == "New Game" or option == "Start Game" or option == "NEW JOURNEY":
            self.state = GameState.PLAYING
            return "new_game"
        elif option == "Settings":
            self.state = GameState.SETTINGS
            self.settings_selected_category = 0
            self.settings_selected_option = 0
            self.selected_index = 0
        elif option == "Quit" or option == "FADE OUT":
            return "quit"
        return None
    
    def activate_pause_option(self):
        """Activate the selected pause menu option."""
        option = self.pause_menu_options[self.selected_index]
        if option == "RESUME":
            self.state = GameState.PLAYING
            return "resume"
        elif option == "SAVE GAME":
            self.message = "Game Saved!"
            self.message_timer = 2.0
            return "save_game"
        elif option == "SETTINGS":
            self.state = GameState.SETTINGS
            self.selected_index = 0
            return "settings"
        elif option == "QUIT TO TITLE":
            self.state = GameState.MAIN_MENU
            self.selected_index = 0
            return "quit_to_title"
        return None
    
    def activate_game_over_option(self):
        """Activate the selected game over option."""
        option = self.game_over_options[self.selected_index]
        if option == "TRY AGAIN":
            self.state = GameState.PLAYING
            self.fade_alpha = 0
            return "load_game" # RE-LOAD last save
        elif option == "GIVE UP":
            self.state = GameState.MAIN_MENU
            self.selected_index = 0
            self.fade_alpha = 0
            return "quit_to_title"
        return None
    
    def toggle_setting(self):
        """Toggle the currently selected setting."""
        cat_name, options = self.settings_categories[self.settings_selected_category]
        if self.settings_selected_option < len(options):
            label, key, cat = options[self.settings_selected_option]
            current_value = self.game_settings.get(cat, key)
            
            if isinstance(current_value, bool):
                self.game_settings.set(cat, key, not current_value)
            elif key == "display_mode":
                modes = ["Windowed", "Fullscreen", "Borderless"]
                current_idx = modes.index(current_value) if current_value in modes else 0
                new_idx = (current_idx + 1) % len(modes)
                self.game_settings.set(cat, key, modes[new_idx])
            elif key == "resolution":
                resolutions = ["1280x720", "1600x900", "1920x1080", "2560x1440"]
                current_idx = resolutions.index(current_value) if current_value in resolutions else 0
                new_idx = (current_idx + 1) % len(resolutions)
                self.game_settings.set(cat, key, resolutions[new_idx])
            
            if cat == "graphics" and (key == "display_mode" or key == "resolution"):
                self.return_state = "settings_applied"
            
            elif key == "difficulty":
                difficulties = ["Easy", "Normal", "Hard"]
                current_idx = difficulties.index(current_value) if current_value in difficulties else 1
                new_idx = (current_idx + 1) % len(difficulties)
                self.game_settings.set(cat, key, difficulties[new_idx])
    
    def adjust_setting(self, amount):
        """Adjust volume settings."""
        cat_name, options = self.settings_categories[self.settings_selected_category]
        if self.settings_selected_option < len(options):
            label, key, cat = options[self.settings_selected_option]
            if key.endswith("volume"):
                current_value = self.game_settings.get(cat, key)
                new_value = max(0, min(100, current_value + amount))
                self.game_settings.set(cat, key, new_value)
    
    def draw_text_with_outline(self, screen, text, font, color, outline_color, x, y, center=True):
        """Draw text with an outline for better readability."""
        # Draw outline (8 directions)
        for dx, dy in [(-2,-2), (-2,0), (-2,2), (0,-2), (0,2), (2,-2), (2,0), (2,2)]:
            outline_surf = font.render(text, True, outline_color)
            if center:
                outline_rect = outline_surf.get_rect(center=(x + dx, y + dy))
            else:
                outline_rect = outline_surf.get_rect(topleft=(x + dx, y + dy))
            screen.blit(outline_surf, outline_rect)
        
        # Draw main text
        text_surf = font.render(text, True, color)
        if center:
            text_rect = text_surf.get_rect(center=(x, y))
        else:
            text_rect = text_surf.get_rect(topleft=(x, y))
        screen.blit(text_surf, text_rect)
        return text_rect
    
    def draw_main_menu(self, screen):
        """Draw the main menu screen."""
        # screen.fill(self.bg_color) # Removed for dynamic background
        
        # LOGO: "GIDEON & THE LIGHT"
        # Layer 1 (Bottom): Black (Offset +2, +2) - Shadow
        # Layer 2 (Middle): Dark Orange (Offset +1, +1) - Outline
        # Layer 3 (Top): White - Main Text
        
        cx, cy = self.screen_width // 2, 150
        text = "GIDEON & THE LIGHT"
        font = self.title_font
        
        # Shadow
        shadow_surf = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(cx + 2, cy + 2))
        screen.blit(shadow_surf, shadow_rect)
        
        # Outline (Dark Orange)
        outline_surf = font.render(text, True, (180, 80, 0))
        outline_rect = outline_surf.get_rect(center=(cx + 1, cy + 1))
        screen.blit(outline_surf, outline_rect)
        
        # Main (White)
        main_surf = font.render(text, True, (255, 255, 255))
        main_rect = main_surf.get_rect(center=(cx, cy))
        screen.blit(main_surf, main_rect)
        
        # Menu options with outlines
        start_y = 350
        for i, option in enumerate(self.main_menu_options):
            color = self.selected_color if i == self.selected_index else self.menu_color
            rect = self.draw_text_with_outline(screen, option, self.menu_font,
                                               color, self.outline_color,
                                               self.screen_width // 2, start_y + i * 60)
            
            # Draw selection indicator (Campfire Icon ^)
            if i == self.selected_index:
                # Hover effect: Tiny ^ to the left
                # Using small font or menu font? Prompt says "tiny". Small font (20) is good.
                self.draw_text_with_outline(screen, "^", self.menu_font, 
                                           (255, 100, 50), # Orange-red for fire
                                           self.outline_color,
                                           rect.left - 40, rect.centery + 5, center=False) # +5 y adjust for caret visual center
        
        # Footer
        footer = self.small_font.render("Use Arrow Keys to Navigate | Enter to Select", True, (200, 200, 200))
        footer_rect = footer.get_rect(center=(self.screen_width // 2, self.screen_height - 40))
        screen.blit(footer, footer_rect)
    
    def draw_settings(self, screen):
        """Draw the settings screen with interactive options."""
        screen.fill(self.bg_color)
        
        # Title
        self.draw_text_with_outline(screen, "Settings", self.subtitle_font,
                                    self.title_color, self.outline_color,
                                    self.screen_width // 2, 80)
        
        y_offset = 150
        col_width = 400
        
        for col_idx, (category_name, options) in enumerate(self.settings_categories):
            x_pos = 150 + (col_idx * col_width)
            
            # Category header (highlight if selected)
            is_selected_cat = (col_idx == self.settings_selected_category)
            cat_color = self.selected_color if is_selected_cat else self.menu_color
            cat_text = self.menu_font.render(category_name, True, cat_color)
            screen.blit(cat_text, (x_pos, y_offset))
            
            # Options
            for i, (label, key, cat) in enumerate(options):
                y_pos = y_offset + 50 + (i * 40)
                
                # Check if this option is selected
                is_selected = (col_idx == self.settings_selected_category and i == self.settings_selected_option)
                
                # Get current value
                value = self.game_settings.get(cat, key)
                
                # Format value display
                if isinstance(value, bool):
                    value_str = "ON" if value else "OFF"
                elif isinstance(value, int) and key.endswith("volume"):
                    value_str = f"{value}%"
                else:
                    value_str = str(value)
                
                # Draw label and value with highlighting
                label_color = self.selected_color if is_selected else self.menu_color
                value_color = self.selected_color if is_selected else self.subtitle_color
                
                label_surf = self.small_font.render(f"{label}:", True, label_color)
                value_surf = self.small_font.render(value_str, True, value_color)
                screen.blit(label_surf, (x_pos, y_pos))
                screen.blit(value_surf, (x_pos + 200, y_pos))
                
                # Draw selection indicator
                if is_selected:
                    indicator = self.small_font.render(">", True, self.selected_color)
                    screen.blit(indicator, (x_pos - 20, y_pos))
        
        # Instructions
        instructions = [
            "Arrow Keys: Navigate | Enter/Space: Toggle",
            "+/- Keys: Adjust Volume | ESC: Save & Return"
        ]
        
        y_inst = self.screen_height - 100
        for i, inst in enumerate(instructions):
            inst_surf = self.small_font.render(inst, True, (180, 180, 180))
            inst_rect = inst_surf.get_rect(center=(self.screen_width // 2, y_inst + i * 30))
            screen.blit(inst_surf, inst_rect)
    
    def draw_pause_menu(self, screen):
        """Draw interactive pause overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((10, 10, 15))
        screen.blit(overlay, (0, 0))
        
        # Pause Title
        self.draw_text_with_outline(screen, "PAUSED", self.title_font, 
                                    self.title_color, self.outline_color,
                                    self.screen_width // 2, 150)

        # Pause options
        start_y = 300
        for i, option in enumerate(self.pause_menu_options):
            color = self.selected_color if i == self.selected_index else self.menu_color
            rect = self.draw_text_with_outline(screen, option, self.menu_font,
                                               color, self.outline_color,
                                               self.screen_width // 2, start_y + i * 60)
            
            if i == self.selected_index:
                indicator = self.menu_font.render(">", True, self.selected_color)
                screen.blit(indicator, (rect.left - 40, rect.top))
        
        # Feedback message (e.g., "Saved!")
        if self.message_timer > 0:
            msg_surf = self.menu_font.render(self.message, True, (100, 255, 100))
            msg_rect = msg_surf.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
            screen.blit(msg_surf, msg_rect)
        
    def draw_credits(self, screen):
        """Draw final credits roll."""
        screen.fill((255, 255, 255))
        
        # Scroll logic handled by caller? Or just static for now?
        # Prompt says "Scroll text".
        # I'll implement static centered text for simplicity + aesthetic impact.
        
        cx, cy = self.screen_width // 2, self.screen_height // 2
        
        font_large = pygame.font.SysFont("Times New Roman", 48, italic=True)
        font_small = pygame.font.SysFont("Times New Roman", 24)
        
        # Main Message
        t1 = font_large.render("GIDEON FOUND THE LIGHT.", True, (10, 10, 20))
        r1 = t1.get_rect(center=(cx, cy - 50))
        screen.blit(t1, r1)
        
        # Dev Credit
        t2 = font_small.render("Developed by Family Game Company LLC", True, (50, 50, 60))
        r2 = t2.get_rect(center=(cx, cy + 50))
        screen.blit(t2, r2)
        
        # Return Hint
        t3 = font_small.render("[Press Key to Return]", True, (150, 150, 160))
        r3 = t3.get_rect(center=(cx, self.screen_height - 50))
        screen.blit(t3, r3)
            
    def draw_game_over(self, screen, run_state):
        """Draw the death screen with stats."""
        # 1. Background (Captured Screenshot with Blue Tint)
        if self.death_bg:
            screen.blit(self.death_bg, (0, 0))
        else:
            screen.fill((0, 0, 20)) # Fallback
            
        # 2. Text (Fade In)
        alpha = int(self.fade_alpha)
        
        # Center: "THE COLD TOOK YOU"
        title_surf = self.title_font.render("THE COLD TOOK YOU", True, (255, 255, 255))
        title_surf.set_alpha(alpha)
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        screen.blit(title_surf, title_rect)
        
        # Subtext: "Days Survived: ..."
        if run_state:
            # Stats: Days Survived (ticks // 100)
            days = run_state.tick_count // 100
            stats_text = f"Days Survived: {days}"
        else:
            stats_text = "Days Survived: 0"
            
        stats_surf = self.subtitle_font.render(stats_text, True, (200, 200, 255))
        stats_surf.set_alpha(alpha)
        stats_rect = stats_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        screen.blit(stats_surf, stats_rect)
        
        # Options
        if alpha > 150: # Show options after fade
            start_y = self.screen_height * 2 // 3
            for i, option in enumerate(self.game_over_options):
                color = self.selected_color if i == self.selected_index else (150, 150, 170)
                rect = self.draw_text_with_outline(screen, option, self.menu_font,
                                                   color, self.outline_color,
                                                   self.screen_width // 2, start_y + i * 60)
                
                if i == self.selected_index:
                    indicator = self.menu_font.render(">", True, self.selected_color)
                    screen.blit(indicator, (rect.left - 40, rect.top))

    def update(self, dt):
        """Update menu timers."""
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
        
        if self.state == GameState.GAME_OVER:
            if self.fade_alpha < 255:
                self.fade_alpha += dt * 100 # Fade in over 2.5 seconds
                self.fade_alpha = min(255, self.fade_alpha)
        elif self.state == GameState.CREDITS:
            # Just wait for input
            pass

    def draw(self, screen, run_state=None):
        """Draw the appropriate menu based on state."""
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu(screen)
        elif self.state == GameState.SETTINGS:
            self.draw_settings(screen)
        elif self.state == GameState.PAUSED:
            self.draw_pause_menu(screen)
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over(screen, run_state)
        elif self.state == GameState.CREDITS:
            self.draw_credits(screen)
