import pygame
import math

class ModernNotification:
    """Modern notification with slide-in animation and auto-fade."""
    def __init__(self, text, duration=3.0, type="info"):
        self.text = text
        self.duration = duration
        self.timer = duration
        self.type = type  # "info", "success", "warning", "danger"
        self.slide_progress = 0.0
        self.alpha = 255
        
        # Colors based on type
        self.colors = {
            "info": ((88, 166, 255), (28, 28, 36)),
            "success": ((75, 192, 192), (28, 36, 32)),
            "warning": ((255, 205, 86), (36, 32, 28)),
            "danger": ((255, 99, 132), (36, 28, 28))
        }
        
    def update(self, dt):
        """Update animation and timer."""
        self.timer -= dt
        
        # Slide in animation (first 0.3s)
        if self.slide_progress < 1.0:
            self.slide_progress = min(1.0, self.slide_progress + dt * 4)
        
        # Fade out in last 0.5s
        if self.timer < 0.5:
            self.alpha = int(255 * (self.timer / 0.5))
        
        return self.timer > 0
    
    def render(self, surface, x, y, width):
        """Render the notification with rustic styling."""
        # Easing function for slide
        ease = self.slide_progress * self.slide_progress * (3 - 2 * self.slide_progress)
        offset_x = int((1 - ease) * width)
        
        # Get colors (for text)
        accent_color, _ = self.colors[self.type]
        
        # Rustic Panel
        height = 50
        panel_rect = pygame.Rect(x + offset_x, y, width, height)
        
        from ui import draw_rustic_panel
        draw_rustic_panel(surface, panel_rect)
        
        # Text
        font = pygame.font.SysFont("Consolas", 14, bold=True)
        # Use simple white or accent color for text?
        # User requested rustic style. "Dark Brown fill" is the panel.
        # Let's use accent color for text to differentiate types.
        text_surf = font.render(self.text, True, accent_color)
        
        # Center vertically, padding left
        text_rect = text_surf.get_rect(midleft=(panel_rect.x + 16, panel_rect.centery))
        surface.blit(text_surf, text_rect)

class NotificationManager:
    """Manages multiple notifications with stacking."""
    def __init__(self):
        self.notifications = []
        
    def add(self, text, duration=3.0, type="info"):
        """Add a new notification."""
        notif = ModernNotification(text, duration, type)
        self.notifications.append(notif)
        
    def update(self, dt):
        """Update all notifications."""
        self.notifications = [n for n in self.notifications if n.update(dt)]
        
    def render(self, surface, screen_width, screen_height):
        """Render all notifications stacked."""
        notif_width = 400
        notif_spacing = 10
        start_y = 150
        
        for i, notif in enumerate(self.notifications):
            x = screen_width - notif_width - 30
            y = start_y + i * (50 + notif_spacing)
            notif.render(surface, x, y, notif_width)
