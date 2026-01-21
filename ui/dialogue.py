import pygame
import math

class DialogueBox:
    def __init__(self):
        self.active = False
        self.lines = []
        self.current_line_index = 0
        self.current_text = ""
        self.full_text = ""
        self.char_index = 0
        self.char_timer = 0.0
        self.char_delay = 0.05  # 50ms per character (typewriter speed)
        self.text_complete = False
        self.blink_timer = 0.0
        
    def start_dialogue(self, lines):
        """Start a new dialogue sequence."""
        self.active = True
        self.lines = lines
        self.current_line_index = 0
        self.current_text = ""
        self.full_text = lines[0] if lines else ""
        self.char_index = 0
        self.text_complete = False
        self.blink_timer = 0.0
        
    def update(self, dt):
        """Update typewriter effect and blink animation."""
        if not self.active:
            return
            
        # Typewriter effect
        if not self.text_complete:
            self.char_timer += dt
            if self.char_timer >= self.char_delay:
                self.char_timer = 0.0
                if self.char_index < len(self.full_text):
                    self.current_text = self.full_text[:self.char_index + 1]
                    self.char_index += 1
                else:
                    self.text_complete = True
        
        # Blink animation for "press to continue"
        if self.text_complete:
            self.blink_timer += dt
            
    def advance(self):
        """Advance to next line or close dialogue."""
        if not self.text_complete:
            # Skip typewriter effect - show full text immediately
            self.current_text = self.full_text
            self.char_index = len(self.full_text)
            self.text_complete = True
            return
            
        # Move to next line
        self.current_line_index += 1
        if self.current_line_index < len(self.lines):
            self.full_text = self.lines[self.current_line_index]
            self.current_text = ""
            self.char_index = 0
            self.text_complete = False
            self.char_timer = 0.0
        else:
            # End of dialogue
            self.active = False
            
    def render(self, surface, width, height):
        """Draw the dialogue box with typewriter text."""
        if not self.active:
            return
            
        # Box dimensions
        box_height = 120
        box_y = height - box_height - 10
        padding = 20
        
        # Box dimensions
        box_height = 120
        box_y = height - box_height - 10
        
        # Rustic Panel Background
        from ui import draw_rustic_panel
        box_rect = pygame.Rect(20, box_y, width - 40, box_height)
        draw_rustic_panel(surface, box_rect)
        
        # Render text with word wrapping
        font = pygame.font.SysFont("Arial", 22)
        text_color = (240, 240, 240)
        
        # Simple word wrap
        words = self.current_text.split(' ')
        lines = []
        current_line = ""
        max_width = width - 80
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word + " "
        if current_line:
            lines.append(current_line)
        
        # Draw wrapped text
        y_offset = box_y + padding
        for line in lines:
            text_surf = font.render(line, True, text_color)
            surface.blit(text_surf, (40, y_offset))
            y_offset += 28
        
        # "Press SPACE to continue" indicator (blinking)
        if self.text_complete:
            blink_visible = (self.blink_timer % 1.0) < 0.5
            if blink_visible:
                prompt_font = pygame.font.SysFont("Arial", 18, bold=True)
                prompt_text = "▼ SPACE"
                prompt_surf = prompt_font.render(prompt_text, True, (255, 215, 0))
                prompt_x = width - 100
                prompt_y = box_y + box_height - 30
                surface.blit(prompt_surf, (prompt_x, prompt_y))

def draw_dialogue_box(surface, dialogue_box, width, height):
    """Wrapper function for rendering dialogue box."""
    dialogue_box.render(surface, width, height)
