import pygame
import math

# Modern color palette
COLORS = {
    'bg_dark': (18, 18, 24),
    'bg_medium': (28, 28, 36),
    'bg_light': (38, 38, 48),
    'accent_primary': (88, 166, 255),  # Modern blue
    'accent_secondary': (255, 159, 64),  # Warm orange
    'accent_success': (75, 192, 192),  # Teal
    'accent_danger': (255, 99, 132),  # Modern red
    'accent_warning': (255, 205, 86),  # Yellow
    'text_primary': (240, 240, 245),
    'text_secondary': (180, 180, 190),
    'text_muted': (120, 120, 130),
    'border': (60, 60, 75),
    'glow': (88, 166, 255, 80),
}

def draw_modern_panel(surface, x, y, width, height, alpha=220, glow=False):
    """Draw a modern glassmorphic panel with optional glow."""
    # Glow effect
    if glow:
        glow_surf = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
        for i in range(10):
            glow_alpha = 20 - i * 2
            pygame.draw.rect(glow_surf, (*COLORS['accent_primary'], glow_alpha), 
                           (10-i, 10-i, width+i*2, height+i*2), border_radius=12)
        surface.blit(glow_surf, (x - 10, y - 10))
    
    # Main panel with gradient
    panel = pygame.Surface((width, height), pygame.SRCALPHA)
    panel.fill((*COLORS['bg_medium'], alpha))
    
    # Subtle gradient overlay
    for i in range(height):
        alpha_gradient = int(alpha * (1 - i / height * 0.3))
        pygame.draw.line(panel, (*COLORS['bg_light'], alpha_gradient), 
                        (0, i), (width, i))
    
    # Border with subtle highlight
    pygame.draw.rect(panel, COLORS['border'], (0, 0, width, height), 2, border_radius=8)
    pygame.draw.line(panel, (*COLORS['text_muted'], 60), (2, 2), (width-2, 2), 1)
    
    surface.blit(panel, (x, y))
    return pygame.Rect(x, y, width, height)

def draw_modern_thermometer(screen, body_temp, x, y, width=50, height=220, shake_offset=0):
    """Ultra-modern thermometer with gradient fill and glow effects."""
    x += shake_offset
    
    # Outer glow
    glow_surf = pygame.Surface((width + 30, height + 30), pygame.SRCALPHA)
    for i in range(15):
        alpha = 30 - i * 2
        pygame.draw.rect(glow_surf, (*COLORS['accent_primary'], alpha),
                        (15-i, 15-i, width+i*2, height+i*2), border_radius=25)
    screen.blit(glow_surf, (x - 15, y - 15))
    
    # Background panel
    bg = pygame.Surface((width, height), pygame.SRCALPHA)
    bg.fill((*COLORS['bg_dark'], 240))
    pygame.draw.rect(bg, COLORS['border'], (0, 0, width, height), 2, border_radius=25)
    screen.blit(bg, (x, y))
    
    # Temperature calculations
    temp_range = 37 - (-32)
    temp_normalized = max(0, min(1, (body_temp - (-32)) / temp_range))
    fill_height = int((height - 10) * temp_normalized)
    
    # Dynamic color based on temperature
    if body_temp >= 30:
        color = COLORS['accent_success']
        glow_color = (75, 255, 192)
    elif body_temp >= 15:
        color = COLORS['accent_warning']
        glow_color = (255, 220, 100)
    elif body_temp >= 0:
        color = COLORS['accent_secondary']
        glow_color = (255, 180, 100)
    else:
        color = COLORS['accent_danger']
        glow_color = (255, 150, 200)
    
    # Gradient fill
    if fill_height > 0:
        fill_surf = pygame.Surface((width - 10, fill_height), pygame.SRCALPHA)
        for i in range(fill_height):
            gradient_factor = i / fill_height if fill_height > 0 else 0
            r = int(color[0] * (0.6 + 0.4 * gradient_factor))
            g = int(color[1] * (0.6 + 0.4 * gradient_factor))
            b = int(color[2] * (0.6 + 0.4 * gradient_factor))
            pygame.draw.line(fill_surf, (r, g, b), (0, fill_height - i - 1), 
                           (width - 10, fill_height - i - 1))
        
        # Inner glow
        glow_overlay = pygame.Surface((width - 10, fill_height), pygame.SRCALPHA)
        glow_overlay.fill((*glow_color, 40))
        fill_surf.blit(glow_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        screen.blit(fill_surf, (x + 5, y + height - fill_height - 5))
    
    # Modern tick marks
    for i in range(5):
        tick_y = y + int(height * (i / 4))
        tick_alpha = 150 if i % 2 == 0 else 80
        pygame.draw.line(screen, (*COLORS['text_muted'], tick_alpha), 
                        (x + width, tick_y), (x + width + 8, tick_y), 2)
    
    # Temperature display with modern font
    font = pygame.font.SysFont("Segoe UI", 20, bold=True)
    temp_text = font.render(f"{int(body_temp)}°", True, color)
    
    # Text background
    text_bg = pygame.Surface((60, 30), pygame.SRCALPHA)
    text_bg.fill((*COLORS['bg_dark'], 200))
    pygame.draw.rect(text_bg, color, (0, 0, 60, 30), 2, border_radius=6)
    screen.blit(text_bg, (x + width + 15, y + height // 2 - 15))
    screen.blit(temp_text, (x + width + 22, y + height // 2 - 12))
    
    # Label
    label_font = pygame.font.SysFont("Segoe UI", 11, bold=True)
    label = label_font.render("BODY TEMP", True, COLORS['text_secondary'])
    screen.blit(label, (x, y - 22))

def draw_modern_tick_clock(screen, tick_progress, x, y, radius=35):
    """Modern circular tick clock with smooth animations."""
    # Outer glow
    glow_surf = pygame.Surface((radius * 2 + 40, radius * 2 + 40), pygame.SRCALPHA)
    for i in range(20):
        alpha = 40 - i * 2
        pygame.draw.circle(glow_surf, (*COLORS['accent_secondary'], alpha),
                          (radius + 20, radius + 20), radius + i)
    screen.blit(glow_surf, (x - radius - 20, y - radius - 20))
    
    # Background circle
    pygame.draw.circle(screen, COLORS['bg_dark'], (x, y), radius)
    pygame.draw.circle(screen, COLORS['border'], (x, y), radius, 2)
    
    # Progress arc
    if tick_progress > 0:
        # Draw smooth arc
        angle = tick_progress * 360
        points = []
        segments = 60
        for i in range(segments + 1):
            segment_angle = (i / segments) * angle
            rad = math.radians(segment_angle - 90)
            px = x + math.cos(rad) * (radius - 5)
            py = y + math.sin(rad) * (radius - 5)
            points.append((px, py))
        
        if len(points) > 1:
            pygame.draw.lines(screen, COLORS['accent_secondary'], False, points, 4)
    
    # Center dot with pulse
    pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.3 + 0.7
    center_radius = int(8 * pulse)
    pygame.draw.circle(screen, COLORS['accent_secondary'], (x, y), center_radius)
    pygame.draw.circle(screen, (*COLORS['accent_secondary'], 100), (x, y), center_radius + 3)
    
    # Label
    label_font = pygame.font.SysFont("Segoe UI", 11, bold=True)
    label = label_font.render("TICK", True, COLORS['text_secondary'])
    label_rect = label.get_rect(center=(x, y + radius + 18))
    screen.blit(label, label_rect)

def draw_modern_survival_panel(screen, run_state, tick_system, screen_width, screen_height, event_manager=None):
    """Modern survival panel with glassmorphic design."""
    # Calculate shake
    shake_offset = 0
    if event_manager and event_manager.is_warning:
        time = pygame.time.get_ticks() / 1000.0
        shake_offset = int(math.sin(time * 20) * 3)
    
    # Draw instruments
    draw_modern_thermometer(screen, run_state.body_temp, 35, 90, shake_offset=shake_offset)
    
    tick_progress = tick_system.time_since_last_tick / tick_system.tick_interval
    draw_modern_tick_clock(screen, tick_progress, 60, 360)
    
    # Zone indicator with modern design
    zone_font = pygame.font.SysFont("Segoe UI", 28, bold=True)
    zone_text = zone_font.render(f"ZONE {run_state.current_zone_id}", True, COLORS['text_primary'])
    zone_rect = zone_text.get_rect(center=(screen_width // 2, 35))
    
    # Zone background
    zone_bg_width = zone_rect.width + 40
    zone_bg_x = zone_rect.centerx - zone_bg_width // 2
    draw_modern_panel(screen, zone_bg_x, 18, zone_bg_width, 34, alpha=200, glow=True)
    screen.blit(zone_text, zone_rect)

def draw_modern_inventory(screen, run_state, screen_width, screen_height):
    """Ultra-modern inventory with smooth animations."""
    from constants import MAX_LOG_SLOTS
    log_count = run_state.inventory.get("logs", 0)
    stick_count = run_state.inventory.get("sticks", 0)
    is_full = log_count >= MAX_LOG_SLOTS
    
    # Layout
    slot_size = 48
    padding = 8
    panel_width = (MAX_LOG_SLOTS * (slot_size + padding)) + padding * 2
    panel_height = 100
    panel_x = screen_width - panel_width - 25
    panel_y = 25
    
    # Modern panel
    draw_modern_panel(screen, panel_x, panel_y, panel_width, panel_height, alpha=230, glow=is_full)
    
    # Title with icon
    title_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
    title_color = COLORS['accent_danger'] if is_full else COLORS['text_primary']
    title_text = "BACKPACK FULL!" if is_full else "BACKPACK"
    title = title_font.render(title_text, True, title_color)
    screen.blit(title, (panel_x + 12, panel_y + 8))
    
    # Log slots
    for i in range(MAX_LOG_SLOTS):
        slot_x = panel_x + padding + (i * (slot_size + padding))
        slot_y = panel_y + 32
        
        # Slot background with depth
        slot_surf = pygame.Surface((slot_size, slot_size), pygame.SRCALPHA)
        slot_surf.fill((*COLORS['bg_dark'], 180))
        
        # Border
        border_color = COLORS['accent_primary'] if i < log_count else COLORS['border']
        pygame.draw.rect(slot_surf, border_color, (0, 0, slot_size, slot_size), 2, border_radius=6)
        
        # Inner glow for filled slots
        if i < log_count:
            glow = pygame.Surface((slot_size - 4, slot_size - 4), pygame.SRCALPHA)
            glow.fill((*COLORS['accent_secondary'], 30))
            slot_surf.blit(glow, (2, 2))
            
            # Modern log icon
            log_color = (180, 120, 70)
            pygame.draw.ellipse(slot_surf, log_color, (12, 16, 24, 16))
            pygame.draw.ellipse(slot_surf, (140, 90, 50), (12, 16, 24, 16), 2)
            # Rings
            pygame.draw.circle(slot_surf, (200, 150, 90), (18, 24), 3)
            pygame.draw.circle(slot_surf, (200, 150, 90), (30, 24), 3)
        
        screen.blit(slot_surf, (slot_x, slot_y))
    
    # Sticks counter
    if stick_count > 0:
        stick_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        stick_text = stick_font.render(f"🌿 {stick_count} STICKS", True, COLORS['accent_success'])
        stick_bg = pygame.Surface((stick_text.get_width() + 16, 22), pygame.SRCALPHA)
        stick_bg.fill((*COLORS['bg_dark'], 200))
        pygame.draw.rect(stick_bg, COLORS['accent_success'], (0, 0, stick_text.get_width() + 16, 22), 1, border_radius=4)
        screen.blit(stick_bg, (panel_x + 8, panel_y + panel_height - 28))
        screen.blit(stick_text, (panel_x + 16, panel_y + panel_height - 26))

def draw_modern_stabilization_ui(screen, run_state, screen_width, screen_height):
    """Modern progress bar for zone stabilization."""
    if not run_state or run_state.current_zone_id != 1 or run_state.zone_1_stabilized:
        return
    
    width, height = 280, 40
    x = screen_width // 2 - width // 2
    y = 70
    
    # Panel
    draw_modern_panel(screen, x, y, width, height, alpha=240, glow=False)
    
    # Progress
    goal = 20
    progress = min(1.0, run_state.logs_deposited_in_zone_1 / goal)
    
    if progress > 0:
        # Gradient progress bar
        prog_width = int((width - 12) * progress)
        prog_surf = pygame.Surface((prog_width, height - 12), pygame.SRCALPHA)
        
        for i in range(prog_width):
            gradient = i / prog_width if prog_width > 0 else 0
            color = (
                int(COLORS['accent_secondary'][0] * (0.7 + 0.3 * gradient)),
                int(COLORS['accent_secondary'][1] * (0.7 + 0.3 * gradient)),
                int(COLORS['accent_secondary'][2] * (0.7 + 0.3 * gradient))
            )
            pygame.draw.line(prog_surf, color, (i, 0), (i, height - 12))
        
        screen.blit(prog_surf, (x + 6, y + 6))
    
    # Text
    font = pygame.font.SysFont("Segoe UI", 13, bold=True)
    remaining = goal - run_state.logs_deposited_in_zone_1
    text = f"{remaining} LOGS TO STABILIZE" if remaining > 0 else "ZONE STABILIZED!"
    text_surf = font.render(text, True, COLORS['text_primary'])
    text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
    
    # Text shadow
    shadow = font.render(text, True, (0, 0, 0))
    screen.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
    screen.blit(text_surf, text_rect)

# Export functions
draw_thermometer = draw_modern_thermometer
draw_tick_clock = draw_modern_tick_clock
draw_survival_panel = draw_modern_survival_panel
draw_inventory_ui = draw_modern_inventory
draw_stabilization_ui = draw_modern_stabilization_ui
