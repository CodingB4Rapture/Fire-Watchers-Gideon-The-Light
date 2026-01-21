import pygame
import math
from constants import MAX_LOG_SLOTS, LOGICAL_WIDTH, LOGICAL_HEIGHT

# --- HELPER FUNCTIONS ---

# Font Cache
_font_cache = {}
_text_cache = {}

def get_font(name, size, bold=False, italic=False):
    key = (name, size, bold, italic)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(name, size, bold, italic)
    return _font_cache[key]

def get_text(font, text, color):
    key = (text, color)
    if key not in _text_cache:
        _text_cache[key] = font.render(text, True, color)
    return _text_cache[key]

def draw_rustic_panel(screen, rect):
    """
    Draws a rustic pixel-art panel.
    Fill: Dark Brown (40, 30, 20).
    Border Outer: Light Tan (160, 120, 80) (1 pixel).
    Border Inner: Darker Brown (20, 15, 10) (1 pixel).
    """
    # Fill
    pygame.draw.rect(screen, (40, 30, 20), rect)
    
    # Outer Border
    pygame.draw.rect(screen, (160, 120, 80), rect, 1)
    
    # Inner Border/Indentation
    inner_rect = rect.inflate(-2, -2)
    pygame.draw.rect(screen, (20, 15, 10), inner_rect, 1)

def draw_modern_panel(screen, rect):
    """
    Draws a modern rounded panel with transparency.
    """
    # Create surface for alpha
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, (30, 35, 45, 200), s.get_rect(), border_radius=15)
    screen.blit(s, rect.topleft)
    
    # Border: White outline (width 2)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=15)

def get_current_objective(run_state):
    """Returns (Title, Current, Max) based on zone."""
    zid = run_state.current_zone_id
    if zid == 0:
        return ("TUTORIAL", 0, 0) # Hidden
    elif zid == 1:
        return ("STABILIZE ZONE", run_state.logs_deposited_in_zone_1, 20)
    elif zid == 2:
        # Use shack progress explicitly
        return ("BUILD SHELTER", run_state.shack_progress["logs"], 30)
    elif zid == 3:
        return ("LIGHT BEACON", run_state.logs_deposited_in_zone_3, 50)
    return ("SURVIVE", 0, 0)

def draw_objective_panel(screen, run_state):
    """Draws the dynamic objective tracker."""
    title, current, max_val = get_current_objective(run_state)
    
    if max_val == 0: return # Hide if no objective (e.g. Tutorial)
    
    # Position: Top Left under Thermometer?
    # Thermometer is usually 20, 20, 16x150.
    # So Panel should be around x=50, y=20? Or Top Center?
    # Prompt: "Top Left (under the Temperature Bar)"
    # Bar bottom is y+height = 20+150 = 170.
    # So y=180.
    x, y = 20, 180
    width, height = 180, 50
    
    rect = pygame.Rect(x, y, width, height)
    
    # Draw Panel
    draw_modern_panel(screen, rect)
    
    # Flash Green Effect
    import time
    if time.time() - run_state.last_log_deposit_time < 0.5:
         flash_surf = pygame.Surface((width, height), pygame.SRCALPHA)
         flash_surf.fill((50, 200, 50, 100)) # Green overlay
         screen.blit(flash_surf, (x, y))
         pygame.draw.rect(screen, (100, 255, 100), rect, 2, border_radius=15) # Bright border
    
    # Content
    font_title = get_font("Verdana", 14, bold=True)
    font_small = get_font("Verdana", 12)
    
    # Title
    t_surf = get_text(font_title, title, (200, 200, 200))
    screen.blit(t_surf, (x + 10, y + 8))
    
    # Progress Bar
    bar_x = x + 10
    bar_y = y + 30
    bar_w = width - 20
    bar_h = 6
    
    # Bg Bar
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
    
    # Fill Bar
    pct = min(1.0, current / max_val)
    fill_w = int(bar_w * pct)
    if fill_w > 0:
        fill_color = (200, 150, 50) # Orange/Gold
        if pct >= 1.0: fill_color = (50, 200, 50) # Green
        pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_w, bar_h), border_radius=3)
        
    # Text Counter (Right aligned or next to title?)
    # "5 / 20 Logs"
    count_text = f"{current} / {max_val}"
    c_surf = get_text(font_small, count_text, (150, 150, 150))
    # Draw right aligned to bar
    screen.blit(c_surf, (bar_x + bar_w - c_surf.get_width(), y + 8))

# --- HUD ELEMENTS ---

def draw_face_icon(screen, x, y, temp):
    """Draws a face icon based on temperature."""
    cx, cy = x + 10, y + 10
    
    # Base Head
    color = (240, 190, 160) # Skin
    if temp < 5: color = (220, 230, 255) # Frozen/Skull
    elif temp < 10: color = (100, 150, 200) # Cold/Blue
    
    # Shiver Offset
    ox = 0
    if 5 <= temp < 10:
        import random
        ox = random.randint(-1, 1)
        
    pygame.draw.circle(screen, color, (cx + ox, cy), 10)
    
    # Face Features
    if temp < 5:
        # Skull Eyes
        pygame.draw.circle(screen, (20, 20, 30), (cx-4, cy-2), 3)
        pygame.draw.circle(screen, (20, 20, 30), (cx+4, cy-2), 3)
        # Teeth / Mouth
        pygame.draw.line(screen, (20, 20, 30), (cx-3, cy+5), (cx+3, cy+5), 1)
        pygame.draw.line(screen, (20, 20, 30), (cx-1, cy+3), (cx-1, cy+7), 1)
        pygame.draw.line(screen, (20, 20, 30), (cx+1, cy+3), (cx+1, cy+7), 1)
    else:
        # Normal Eyes
        pygame.draw.circle(screen, (20, 20, 20), (cx-3+ox, cy-2), 2)
        pygame.draw.circle(screen, (20, 20, 20), (cx+3+ox, cy-2), 2)
        # Mouth
        if temp < 10:
            # Chattering
            pygame.draw.line(screen, (20, 20, 20), (cx-2+ox, cy+4), (cx+2+ox, cy+4), 1)
        else:
            # Smile
            pygame.draw.arc(screen, (20, 20, 20), (cx-4, cy, 8, 8), 3.14, 6.28, 1)

def draw_thermometer(screen, body_temp, x, y, width=16, height=150, shake_offset=0):
    """
    Overhauled Thermometer with Danger Zones.
    """
    # Apply shake
    x += shake_offset
    
    # 1. Background Tube (Gradient Zones)
    tube_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, (20, 15, 10), tube_rect) # Dark base
    
    # Draw Zones (Background indicators)
    # Zone 3: Critical (Bottom 20%) - Purple
    crit_h = int(height * 0.2)
    pygame.draw.rect(screen, (40, 30, 60), (x+1, y + height - crit_h, width-2, crit_h))
    
    # Zone 2: Warning (Next 30%) - Blue
    warn_h = int(height * 0.3)
    pygame.draw.rect(screen, (30, 50, 70), (x+1, y + height - crit_h - warn_h, width-2, warn_h))
    
    # Zone 1: Safe (Top 50%) - Orange hint
    safe_h = height - crit_h - warn_h
    pygame.draw.rect(screen, (60, 40, 30), (x+1, y, width-2, safe_h))

    # Border
    border_color = (80, 60, 40)
    # Critical Flash
    if body_temp < 5:
        import time
        if int(time.time() * 5) % 2 == 0:
            border_color = (255, 50, 50)
            
    pygame.draw.rect(screen, border_color, tube_rect, 2)
    
    # 2. Hypothermia Line (Temp = 5)
    # Range: -32 to 37 (Total 69)
    # 5 degrees relative to -32 is (5 - (-32)) = 37 units up from bottom
    # Pct = 37 / 69 ~= 0.53 ?? Wait.
    # 37C is Max. -32C is Min.
    # Temp 5 is actually quite high relative to -32.
    # Wait, 37C is Body Temp. 
    # Hypothermia is < 35C IRL. In game, "5C" seems to be internal body temp unit?
    # Default starts at 37.0.
    # If "Temp = 5" is Danger Zone, that implies 5 units.
    # Let's map it accurately.
    min_temp, max_temp = -10, 37 # Visual range adjustment?
    # If min is -32, bar is mostly empty at 5.
    # Let's use user's request: Temp=5 is danger.
    total_range = max_temp - min_temp
    danger_val = 5
    danger_pct = (danger_val - min_temp) / total_range
    danger_y = y + height - int(height * danger_pct)
    
    # Draw Line
    pygame.draw.line(screen, (200, 50, 50), (x-4, danger_y), (x+width+4, danger_y), 2)
    
    # 3. Fill Level
    clamped_temp = max(min_temp, min(max_temp, body_temp))
    temp_pct = (clamped_temp - min_temp) / total_range
    fill_height = int(height * temp_pct)
    
    # 4. Fill Color
    if body_temp < 5:
        fill_color = (220, 220, 255) # White/Purple
    elif body_temp < 15:
        fill_color = (100, 150, 200) # Pale Blue
    else:
        fill_color = (200, 100, 50) # Warm Orange
        
    # Draw Fill
    fill_rect = pygame.Rect(x + 2, y + height - fill_height, width - 4, fill_height)
    pygame.draw.rect(screen, fill_color, fill_rect)
    
    # 5. Face Icon
    draw_face_icon(screen, x + width + 8, y + height - width - 10, body_temp)

def draw_tick_clock(screen, tick_progress, x, y, radius=10):
    """
    Draw a small circle explicitly like a pie chart.
    Visual rhythm for survival ticks.
    """
    center = (x + radius, y + radius)
    
    # Background
    pygame.draw.circle(screen, (40, 30, 20), center, radius)
    pygame.draw.circle(screen, (160, 120, 80), center, radius, 1)
    
    if tick_progress > 0:
        # Draw Pie Chart Fill
        # Create a surface to draw the pie segment on
        # Or use polygon points
        points = [center]
        max_angle = int(360 * tick_progress)
        
        # Start from top (270 deg)
        for angle in range(0, max_angle + 1, 10):
            rad = math.radians(angle - 90)
            px = center[0] + radius * 0.8 * math.cos(rad)
            py = center[1] + radius * 0.8 * math.sin(rad)
            points.append((px, py))
            
        # Ensure last point is accurate
        rad_final = math.radians(max_angle - 90)
        px_final = center[0] + radius * 0.8 * math.cos(rad_final)
        py_final = center[1] + radius * 0.8 * math.sin(rad_final)
        points.append((px_final, py_final))
        
        if len(points) > 2:
            pygame.draw.polygon(screen, (200, 180, 100), points)

def draw_log_icon(screen, rect):
    # Simple Pixel Log
    # Dark brown rect with lighter ends
    color_bark = (100, 60, 30)
    color_end = (160, 120, 80)
    
    # Log Body
    pygame.draw.rect(screen, color_bark, (rect.x + 8, rect.y + 12, 24, 16))
    
    # Log End
    pygame.draw.circle(screen, color_end, (rect.x + 32, rect.y + 20), 6)
    pygame.draw.circle(screen, color_bark, (rect.x + 32, rect.y + 20), 6, 1)

def draw_stick_icon(screen, rect):
    # Simple Stick
    # Diagonal line
    start = (rect.x + 10, rect.y + 30)
    end = (rect.x + 30, rect.y + 10)
    pygame.draw.line(screen, (180, 160, 120), start, end, 3)

def draw_axe_icon(screen, rect):
    # Pixel Axe
    center_x, center_y = rect.center
    
    # Handle
    pygame.draw.line(screen, (140, 140, 130), (center_x - 8, center_y + 8), (center_x + 8, center_y - 8), 3)
    
    # Head
    head_color = (200, 60, 60) # Rusty red/iron
    # Draw simple polygon for head
    points = [
        (center_x + 6, center_y - 8),
        (center_x + 12, center_y - 4),
        (center_x + 4, center_y + 4),
        (center_x + 0, center_y - 2)
    ]
    pygame.draw.polygon(screen, head_color, points)

def draw_inventory_ui(screen, run_state, screen_width, screen_height, active_tool="AXE"):
    """
    Modern Tool Belt and Resource Pouch.
    """
    font = get_font("Consolas", 14, bold=True)
    
    # === TOOLBELT (Left) ===
    belt_w, belt_h = 150, 80
    belt_x = 20
    belt_y = screen_height - belt_h - 20
    rect_belt = pygame.Rect(belt_x, belt_y, belt_w, belt_h)
    
    draw_modern_panel(screen, rect_belt)
    
    # Hint "TAB"
    hint_surf = get_text(font, "TAB", (200, 200, 200))
    screen.blit(hint_surf, (rect_belt.centerx - hint_surf.get_width()//2, rect_belt.top - 20))
    
    # Icons: AXE, TORCH
    axe_rect = pygame.Rect(rect_belt.x + 15, rect_belt.y + 15, 50, 50)
    torch_rect = pygame.Rect(rect_belt.x + 85, rect_belt.y + 15, 50, 50)
    
    # Helper to draw tool
    def draw_tool_slot(rect, name, is_active):
        tool_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        local_rect = pygame.Rect(0, 0, 50, 50)
        
        if name == "AXE":
            # Draw Axe Icon (Local coords)
            cx, cy = 25, 25
            pygame.draw.line(tool_surf, (140, 140, 130), (cx-8, cy+8), (cx+8, cy-8), 3)
            head_color = (200, 60, 60)
            points = [(cx+6, cy-8), (cx+12, cy-4), (cx+4, cy+4), (cx+0, cy-2)]
            pygame.draw.polygon(tool_surf, head_color, points)
            
        elif name == "TORCH":
            # Procedural Torch
            cx, cy = 25, 25
            pygame.draw.line(tool_surf, (140, 100, 60), (cx, cy+15), (cx, cy-5), 6) # Handle
            pygame.draw.circle(tool_surf, (255, 100, 0), (cx, cy-12), 8) # Flame core
            pygame.draw.circle(tool_surf, (255, 200, 50), (cx, cy-12), 4)
            
        if not is_active:
             tool_surf.set_alpha(100)
             
        screen.blit(tool_surf, rect.topleft)
        
        if is_active:
             # Orange Glow Border
             pygame.draw.rect(screen, (255, 140, 0), rect.inflate(6, 6), 3, border_radius=10)

    draw_tool_slot(axe_rect, "AXE", active_tool=="AXE")
    draw_tool_slot(torch_rect, "TORCH", active_tool=="TORCH")

    # === RESOURCE POUCH (Right) ===
    
    # Logs Panel
    logs_w, logs_h = 200, 70
    logs_rect = pygame.Rect(screen_width - logs_w - 20, screen_height - logs_h - 20, logs_w, logs_h)
    draw_modern_panel(screen, logs_rect)
    
    # Log Slots
    current_logs = run_state.inventory.get("logs", 0)
    slot_size = 20
    gap = 8
    start_x = logs_rect.x + 20
    start_y = logs_rect.centery - slot_size//2
    
    for i in range(6):
        r = pygame.Rect(start_x + i*(slot_size+gap), start_y, slot_size, slot_size)
        pygame.draw.rect(screen, (20, 20, 25), r, border_radius=4) # Slot BG
        pygame.draw.rect(screen, (60, 60, 70), r, 1, border_radius=4) # Outline
        
        if i < current_logs:
             # Log Icon
             pygame.draw.rect(screen, (139, 69, 19), r.inflate(-4, -4), border_radius=2)
             
    # Stick Box (Left of Logs)
    stick_w, stick_h = 80, 50
    stick_rect = pygame.Rect(logs_rect.x - stick_w - 10, logs_rect.bottom - stick_h, stick_w, stick_h)
    draw_modern_panel(screen, stick_rect)
    
    # Stick Icon (Bundle)
    sx, sy = stick_rect.x + 10, stick_rect.y + 10
    # Bundle of 3 lines
    pygame.draw.line(screen, (180, 160, 120), (sx, sy+20), (sx+20, sy), 3)
    pygame.draw.line(screen, (160, 140, 100), (sx+5, sy+20), (sx+25, sy), 3)
    pygame.draw.line(screen, (140, 120, 80), (sx+10, sy+20), (sx+30, sy), 3)
    
    # Count
    s_count = run_state.inventory.get("sticks", 0)
    stxt = get_text(font, str(s_count), (255, 255, 255))
    screen.blit(stxt, (stick_rect.x + 45, stick_rect.centery - stxt.get_height()//2))

def draw_survival_panel(screen, run_state, tick_system, screen_width, screen_height, event_manager=None):
    """
    Main HUD: Thermometer + Clock (Top Left), Inventory (Bottom Center).
    """
    # Shake effect for warning
    shake = 0
    if event_manager and event_manager.is_warning:
        import random
        shake = random.randint(-1, 1)
        
    # Thermometer
    draw_thermometer(screen, run_state.body_temp, 20, 20, shake_offset=shake)
    
    # Clock (Next to thermo)
    # Thermo width 12, x=20. Right edge = 32.
    # Gap 10px -> 42.
    tick_pct = tick_system.time_since_last_tick / tick_system.tick_interval
    draw_tick_clock(screen, tick_pct, 45, 20, radius=12)
    
    # Dynamic Objective Tracker
    draw_objective_panel(screen, run_state)
    
    # Inventory - MOVED to main loop
    pass

def draw_cold_overlay(screen, body_temp, screen_width, screen_height):
    """Draw blue tint that intensifies as player gets colder."""
    if body_temp >= 37:
        return
    
    temp_factor = 1 - ((body_temp - (-32)) / (37 - (-32)))
    temp_factor = max(0, min(1, temp_factor))
    opacity = int(temp_factor * 150)
    
    if opacity > 0:
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill((100, 150, 255))
        overlay.set_alpha(opacity)
        screen.blit(overlay, (0, 0))

def draw_stabilization_ui(screen, run_state, screen_width, screen_height):
    # Minimalistic stabilization text
    if not run_state or run_state.current_zone_id != 1 or run_state.zone_1_stabilized:
        return
        
    goal = 20
    current = run_state.logs_deposited_in_zone_1
    remaining = goal - current
    
    if remaining > 0:
        font = get_font("Consolas", 14, bold=True)
        text = get_text(font, f"LOGS NEEDED: {remaining}", (200, 200, 200))
        bg_rect = text.get_rect(center=(screen_width // 2, 40))
        bg_rect.inflate_ip(10, 6)
        
        draw_rustic_panel(screen, bg_rect)
        screen.blit(text, text.get_rect(center=bg_rect.center))

def draw_shop_menu(screen, run_state, selection_index, stash_count):
    """
    Draws the rustic shop menu for Builder's Ridge.
    """
    w, h = screen.get_size()
    
    # 1. Overlay
    overlay = pygame.Surface((w, h))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    screen.blit(overlay, (0, 0))
    
    # 2. Paper Sheet
    menu_w, menu_h = 600, 450
    cx, cy = w // 2, h // 2
    menu_rect = pygame.Rect(cx - menu_w//2, cy - menu_h//2, menu_w, menu_h)
    
    # Paper texture color
    pygame.draw.rect(screen, (225, 215, 190), menu_rect)
    # Border
    pygame.draw.rect(screen, (80, 60, 40), menu_rect, 4)
    pygame.draw.rect(screen, (60, 40, 20), menu_rect, 2)
    
    # 3. Header
    font_header = get_font("Courier New", 32, bold=True)
    title = get_text(font_header, "BUILDER'S SUPPLIES", (60, 40, 20))
    screen.blit(title, (cx - title.get_width()//2, menu_rect.y + 30))
    
    # 4. Logs Available
    font_res = get_font("Consolas", 20, bold=True)
    res_text = get_text(font_res, f"STASH: {stash_count} LOGS", (40, 40, 50))
    screen.blit(res_text, (menu_rect.right - res_text.get_width() - 20, menu_rect.y + 20))
    
    # 5. Items
    items = [
        {"id": "axe", "name": "REINFORCED AXE", "cost": 50, "desc": "+1 Log gained per tree."},
        {"id": "fur", "name": "FUR LINING", "cost": 30, "desc": "Reduces cold loss by 20%."},
        {"id": "bags", "name": "DEEP POCKETS", "cost": 40, "desc": "Carry +2 Logs."}
    ]
    
    start_y = menu_rect.y + 100
    row_height = 90
    font_item = get_font("Consolas", 24, bold=True)
    font_desc = get_font("Consolas", 18, italic=True)
    
    for i, item in enumerate(items):
        item_y = start_y + (i * row_height)
        
        # Selection Highlight
        if i == selection_index:
            highlight_rect = pygame.Rect(menu_rect.x + 20, item_y - 10, menu_w - 40, row_height - 10)
            pygame.draw.rect(screen, (200, 190, 160), highlight_rect)
            pygame.draw.rect(screen, (100, 80, 60), highlight_rect, 2)
        
        # Check Ownership
        owned = False
        if item["id"] == "axe" and run_state.axe_upgrade: owned = True
        if item["id"] == "fur" and run_state.fur_lining: owned = True
        if item["id"] == "bags" and run_state.deep_pockets: owned = True
        
        # Text Color
        name_color = (40, 30, 20)
        if owned: name_color = (100, 100, 100) # Grayed out
        
        # Name
        name_surf = font_item.render(item["name"], True, name_color)
        screen.blit(name_surf, (menu_rect.x + 40, item_y))
        
        # Description
        desc_surf = font_desc.render(item["desc"], True, (80, 70, 60))
        screen.blit(desc_surf, (menu_rect.x + 40, item_y + 30))
        
        # Cost / Status
        if owned:
            status = "SOLD"
            color = (50, 150, 50)
        else:
            status = f"{item['cost']} LOGS"
            color = (180, 50, 50) if stash_count < item['cost'] else (50, 100, 50)
            
        cost_surf = font_item.render(status, True, color)
        screen.blit(cost_surf, (menu_rect.right - 40 - cost_surf.get_width(), item_y + 10))
    
    # Footer Instructions
    font_foot = get_font("Arial", 16)
    foot = get_text(font_foot, "UP/DOWN: Select   ENTER/A: Buy   ESC/B: Close", (100, 90, 80))
    screen.blit(foot, (cx - foot.get_width()//2, menu_rect.bottom - 30))
