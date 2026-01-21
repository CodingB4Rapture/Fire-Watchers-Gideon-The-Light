import pygame

class TutorialManager:
    def __init__(self):
        self.device = "keyboard" # keyboard, controller
        
    def set_device(self, device):
        self.device = device
        
    def get_control_string(self, action):
        if self.device == "keyboard":
            if action == "MOVE": return "WASD"
            if action == "SWITCH": return "TAB"
            if action == "ACTION": return "LEFT CLICK" # Prompt says Click
            if action == "INTERACT": return "E" 
        else:
            if action == "MOVE": return "Left Stick"
            if action == "SWITCH": return "Y Button" # Triangle
            if action == "ACTION": return "A Button" # Cross/A
            if action == "INTERACT": return "A Button"
        return "?"

    def update(self, dt, run_state, player):
        if run_state.tutorial_completed: return
        if run_state.current_zone_id != 0: return
        
        step = run_state.tutorial_step
        
        # Step 0: Move
        if step == 0:
            # Accumulate movement
            if player.is_moving:
                run_state.distance_moved += player.speed * dt
            
            if run_state.distance_moved >= 100:
                run_state.tutorial_step = 1
                
        # Step 1: Equip Axe
        elif step == 1:
            if player.active_tool == "AXE":
                run_state.tutorial_step = 2
        
        # Step 2: Chop (Gather Wood)
        elif step == 2:
            if run_state.inventory["logs"] >= 1:
                run_state.tutorial_step = 3
                
        # Step 3: Equip Torch
        elif step == 3:
            if player.active_tool == "TORCH":
                run_state.tutorial_step = 4
                
        # Step 4: Stoke Fire
        # Handled by Player interaction in player.py
        # because it requires a specific event action.
        pass
            
        # Step 5: Depart
        # Completion handled by zone transition

    def render(self, screen, run_state, width, height):
        if run_state.tutorial_completed or run_state.current_zone_id != 0: return

        # Toast UI
        # Top Center
        toast_w, toast_h = 420, 50
        x = (width - toast_w) // 2
        y = 50 # Top
        
        rect = pygame.Rect(x, y, toast_w, toast_h)
        
        # Bg
        s = pygame.Surface((toast_w, toast_h), pygame.SRCALPHA)
        pygame.draw.rect(s, (20, 20, 25, 200), s.get_rect(), border_radius=15)
        screen.blit(s, (x, y))
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=15)
        
        # Text Generation
        step = run_state.tutorial_step
        text = ""
        
        move_key = self.get_control_string("MOVE")
        switch_key = self.get_control_string("SWITCH")
        action_key = self.get_control_string("ACTION")
        
        if step == 0:
            text = f"Use {move_key} to Move."
        elif step == 1:
            text = f"Press {switch_key} to equip Axe."
        elif step == 2:
            text = f"Press {action_key} to Chop Tree."
        elif step == 3:
            text = f"Press {switch_key} to equip Torch."
        elif step == 4:
            text = f"Press {action_key} on Fire to Stoke."
        elif step >= 5:
             text = "Walk to the Right Edge to Leave."
             
        font = pygame.font.SysFont("Consolas", 18, bold=True)
        t_surf = font.render(text, True, (255, 255, 255))
        screen.blit(t_surf, (x + (toast_w - t_surf.get_width())//2, y + (toast_h - t_surf.get_height())//2))
