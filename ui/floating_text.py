import pygame

class FloatingText:
    def __init__(self, x, y, text, color, duration=1.0):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.duration = duration
        self.life = duration
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        
    def update(self, dt):
        self.life -= dt
        self.y -= 40 * dt # Move upward
        return self.life > 0
        
    def render(self, surface):
        alpha = int((self.life / self.duration) * 255)
        text_surf = self.font.render(self.text, True, self.color)
        
        # Apply fade
        alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.fill((255, 255, 255, alpha))
        text_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Center text horizontally on x
        rect = text_surf.get_rect(centerx=self.x, bottom=self.y)
        surface.blit(text_surf, rect)
