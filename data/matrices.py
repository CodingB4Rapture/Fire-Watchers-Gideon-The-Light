# CRITICAL: PROCEDURAL PIPELINE - DO NOT REPLACE WITH STATIC ASSETS
# This file generates the pixel-art character frames dynamically.
# Import generated sprite data
try:
    from data.sprite_data import IDLE_DOWN_FRAMES, IDLE_LEFT_FRAMES, IDLE_RIGHT_FRAMES, IDLE_UP_FRAMES, WALK_DOWN_FRAMES
except ImportError:
    print("Sprite data not found, using procedural generation.")
    IDLE_DOWN_FRAMES = None
    WALK_DOWN_FRAMES = None

def create_base_grid():
    return [[0 for _ in range(18)] for _ in range(24)]

def set_pixel(grid, x, y, val):
    """Set a single pixel safely."""
    if 0 <= y < 24 and 0 <= x < 18:
        grid[y][x] = val

def add_selective_outline(grid):
    """Add clean selective outlining."""
    temp = [row[:] for row in grid]
    for y in range(1, 23):
        for x in range(1, 17):
            if grid[y][x] != 0 and grid[y][x] != 6:
                # Check for edges
                for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < 24 and 0 <= nx < 18:
                        if grid[ny][nx] == 0:
                            temp[ny][nx] = 6
    return temp

# === PROPER 16x16 SPRITE (V11) ===
# Clean, refined pixel art with proper proportions

def build_hero_grid(f, facing="DOWN", tool="TORCH", is_chopping=False, is_moving=False, is_lighting=False, is_igniting=False):
    swing_f = f % 4 # Define swing frame for chopping/lighting logic
    
    # ... (Rest of function logic remains same until Tool section) ...
    # === CUSTOM IDLE SPRITES (DISABLED - REVERTING TO PROCEDURAL) ===
    # to re-enable, uncomment this block
    # if not is_moving and not is_chopping:
    #     if IDLE_DOWN_FRAMES:
    #         cycle_idx = f % len(IDLE_DOWN_FRAMES) 
    #         if facing == "DOWN":
    #             return IDLE_DOWN_FRAMES[cycle_idx] # Return directly, no post-processing
    #         elif facing == "UP" and IDLE_UP_FRAMES:
    #             return IDLE_UP_FRAMES[f % len(IDLE_UP_FRAMES)] # Return directly
    #         elif facing == "SIDE" and IDLE_RIGHT_FRAMES:
    #             return IDLE_RIGHT_FRAMES[f % len(IDLE_RIGHT_FRAMES)] # Return directly
            
    # === WALK ANIMATION (Procedural V12) ===
    # Fallback to procedural generation for Walking (until sprites provided)
    # OR if custom sprites are missing.
    
    grid = create_base_grid()
    state = facing # Map facing to old 'state' variable
    
    # ... (Rest of V12 Procedural Logic) ...
    
    # Idle bob
    bob = 0
    if not is_moving:
        bob = 1 if f % 2 == 0 else 0
    
    # Walk bob - Natural Cycle (High on Pass, Low on Contact)
    walk_bob = 0
    if is_moving and state in ["DOWN", "UP", "SIDE"]:
        cycle = f % 4
        if cycle == 1 or cycle == 3:
            walk_bob = -1 # Rise on passing frames
    
    # Base Y position (centered vertically with room for bob)
    base_y = 4
    
    # === LEGS (pixels 14-20 from base) - REFINED WALK CYCLE V12 ===
    render_y = bob + walk_bob
    
    if is_igniting:
        render_y += 3 # Crouch down
    lx, rx = 7, 9

    # Calculate leg top connection point to avoid gaps when body rises
    leg_top = 18 + render_y # Connects to body which is at 17+render_y

    # Default Leg Render (Standing)
    if not is_moving:
         for y in range(18, 22):
            set_pixel(grid, lx, y, 8)
            set_pixel(grid, rx, y, 8)
         set_pixel(grid, lx, 22, 4)
         set_pixel(grid, rx, 22, 4)
    else:
        # Movement logic (V12 Procedural Walk)
        
        # Absolute positioning logic for clarity
        # Base leg Y start is around 18 (body ends at 17)
        # Leg X positions
        
        if state == "SIDE":
            cycle = f % 4
            if cycle == 0:  # Right foot contact
                # Right leg (front) - straight down
                set_pixel(grid, 9, leg_top, 8); set_pixel(grid, 9, 19, 8); set_pixel(grid, 9, 20, 8); set_pixel(grid, 9, 21, 8); set_pixel(grid, 9, 22, 8)
                set_pixel(grid, 9, 23, 4) # Boot
                # Left leg (back) - bent, raised
                set_pixel(grid, 7, leg_top, 8); set_pixel(grid, 7, 19, 8); set_pixel(grid, 7, 20, 8)
                set_pixel(grid, 7, 21, 4)
            elif cycle == 1:  # Passing
                # Both legs
                for y in range(leg_top, 23): 
                    set_pixel(grid, 9, y, 8); set_pixel(grid, 7, y, 8)
                set_pixel(grid, 9, 23, 4); set_pixel(grid, 7, 23, 4)
            elif cycle == 2:  # Left foot contact
                # Left leg (front)
                set_pixel(grid, 7, leg_top, 8); set_pixel(grid, 7, 19, 8); set_pixel(grid, 7, 20, 8); set_pixel(grid, 7, 21, 8); set_pixel(grid, 7, 22, 8)
                set_pixel(grid, 7, 23, 4)
                # Right leg (back)
                set_pixel(grid, 9, leg_top, 8); set_pixel(grid, 9, 19, 8); set_pixel(grid, 9, 20, 8)
                set_pixel(grid, 9, 21, 4)
            else: # Passing
                for y in range(leg_top, 22):
                    set_pixel(grid, 9, y, 8); set_pixel(grid, 7, y, 8)
                set_pixel(grid, 9, 22, 4); set_pixel(grid, 7, 22, 4)

        elif state == "DOWN":
            cycle = f % 4
            # Natural Walk Down - Symmetric Steps
            if cycle == 0:  # Step Left Forward
                # Left leg (Front/Active) - Visual step down
                for y in range(leg_top, 22): set_pixel(grid, lx, y, 8)
                set_pixel(grid, lx, 22, 4) # Boot at 22 (Ground)
                
                # Right leg (Back/Passing) - Lifted slightly
                for y in range(leg_top, 21): set_pixel(grid, rx, y, 8)
                set_pixel(grid, rx, 21, 4) # Boot at 21 (Lifted)
                
            elif cycle == 2:  # Step Right Forward
                # Left leg (Back/Passing) - Lifted slightly
                for y in range(leg_top, 21): set_pixel(grid, lx, y, 8)
                set_pixel(grid, lx, 21, 4) # Boot at 21 (Lifted)

                # Right leg (Front/Active) - Visual step down
                for y in range(leg_top, 22): set_pixel(grid, rx, y, 8)
                set_pixel(grid, rx, 22, 4) # Boot at 22 (Ground)
                
            else: # Passing Frames (1 & 3) - Body is High (leg_top is 17)
                # Legs straight down to ground
                for y in range(leg_top, 22):
                    set_pixel(grid, lx, y, 8); set_pixel(grid, rx, y, 8)
                set_pixel(grid, lx, 22, 4); set_pixel(grid, rx, 22, 4)

        elif state == "UP":
            cycle = f % 4
            if cycle == 0:  # Lift Left
                for y in range(18, 21): set_pixel(grid, lx, y, 8) # Left raised
                set_pixel(grid, lx, 21, 4)
                for y in range(18, 22): set_pixel(grid, rx, y, 8) # Right planted
                set_pixel(grid, rx, 22, 4)
            elif cycle == 2:  # Lift Right
                for y in range(18, 22): set_pixel(grid, lx, y, 8) # Left planted
                set_pixel(grid, lx, 22, 4)
                for y in range(18, 21): set_pixel(grid, rx, y, 8) # Right raised
                set_pixel(grid, rx, 21, 4)
            else: # Stand
                for y in range(18, 22):
                    set_pixel(grid, lx, y, 8); set_pixel(grid, rx, y, 8)
                set_pixel(grid, lx, 22, 4); set_pixel(grid, rx, 22, 4)
        
        else: # Default/IDLE fallback moving
            for y in range(18, 22):
                set_pixel(grid, lx, y, 8); set_pixel(grid, rx, y, 8)
            set_pixel(grid, lx, 22, 4); set_pixel(grid, rx, 22, 4)

    # === BODY (pixels 7-13 from base) ===
    # Add explicit body heave for chopping
    chop_offset = 0
    if is_chopping:
        if swing_f == 0: chop_offset = -1 # Windup (Stretch up)
        elif swing_f == 1: chop_offset = 1 # Impact (Crunch down)
    
    body_y = base_y + 7 + render_y + chop_offset
    
    # Tunic
    set_pixel(grid, 7, body_y, 3); set_pixel(grid, 8, body_y, 3); set_pixel(grid, 9, body_y, 3) # Shoulders
    for x in range(6, 11):
        for y_offset in range(1, 5):
            set_pixel(grid, x, body_y + y_offset, 3)
    # Belt
    for x in range(6, 11): set_pixel(grid, x, body_y + 5, 2)
    # Lower tunic
    for x in range(6, 11): set_pixel(grid, x, body_y + 6, 3)
    
    # Shading
    set_pixel(grid, 6, body_y + 2, 2); set_pixel(grid, 6, body_y + 3, 2); set_pixel(grid, 6, body_y + 4, 2)
    set_pixel(grid, 10, body_y + 2, 2); set_pixel(grid, 10, body_y + 3, 2); set_pixel(grid, 10, body_y + 4, 2)
    
    # === HEAD (pixels 0-6 from base) ===
    head_y = base_y + render_y + chop_offset
    
    if state == "UP":
        set_pixel(grid, 8, head_y + 1, 4)
        for x in range(7, 10):
            set_pixel(grid, x, head_y + 2, 4); set_pixel(grid, x, head_y + 3, 4); set_pixel(grid, x, head_y + 4, 4)
        set_pixel(grid, 8, head_y + 5, 4)
        # Highlights
        set_pixel(grid, 7, head_y + 2, 5); set_pixel(grid, 8, head_y + 2, 5); set_pixel(grid, 9, head_y + 2, 5)
        
    elif state == "SIDE":
        set_pixel(grid, 8, head_y + 2, 1)
        for x in range(8, 10):
            set_pixel(grid, x, head_y + 3, 1); set_pixel(grid, x, head_y + 4, 1)
        set_pixel(grid, 8, head_y + 5, 1)
        # Hair
        set_pixel(grid, 7, head_y + 1, 5); set_pixel(grid, 7, head_y + 2, 4); set_pixel(grid, 7, head_y + 3, 4); set_pixel(grid, 7, head_y + 4, 4)
        set_pixel(grid, 8, head_y + 1, 5)
        # Face
        set_pixel(grid, 9, head_y + 3, 6); set_pixel(grid, 9, head_y + 4, 6) # Eye/Smile
        
    else: # DOWN - RUSTIC SURVIVOR STYLE
        # Hood/Hat Shape (Slightly more squared/practical)
        set_pixel(grid, 8, head_y + 1, 4) 
        for x in range(7, 10):
            set_pixel(grid, x, head_y + 2, 4) 
        
        # Face box (Skin) - Narrower, framed by gear
        for x in range(7, 10):
            set_pixel(grid, x, head_y + 3, 1) # Eyes level
        
        # Scarf/Collar covering lower face? Or just chin
        # Let's show a bit of face but framed tight
        set_pixel(grid, 7, head_y + 4, 1); set_pixel(grid, 8, head_y + 4, 1); set_pixel(grid, 9, head_y + 4, 1)
        set_pixel(grid, 8, head_y + 5, 1) # Chin
        
        # Hood sides/Framing
        set_pixel(grid, 6, head_y + 2, 4); set_pixel(grid, 10, head_y + 2, 4)
        set_pixel(grid, 6, head_y + 3, 4); set_pixel(grid, 10, head_y + 3, 4)
        # Tunic/Scarf rising up?
        set_pixel(grid, 6, head_y + 4, 2); set_pixel(grid, 10, head_y + 4, 2) # Gear hugging face
        
        # Highlights on Hood
        set_pixel(grid, 7, head_y + 1, 5); set_pixel(grid, 8, head_y + 1, 5); set_pixel(grid, 9, head_y + 1, 5)
        
        # === FACE DETAILS ===
        # Eyes - Simple, dark, determined
        set_pixel(grid, 7, head_y + 3, 6); set_pixel(grid, 9, head_y + 3, 6)
        
        # No blush.
        # Mouth - Serious/Neutral or Hidden by cold
        # A simple shading pixel for nose/mouth area is often enough in low-res
        set_pixel(grid, 8, head_y + 4, 5) # Slight shadow/nose, not a distinct smile

    # === BACKPACK ===
    if state == "UP":
        for y in range(body_y, body_y + 4):
            for x in range(7, 10): set_pixel(grid, x, y, 4)

    # === TOOLS (Dynamic Axe Chop) ===
    # Colors: 7 (Steel/Grey), 4 (Wood Brown), 10 (Rust/Highlight), 13 (White/Whoosh)
    if is_chopping:
        # Swing Frames: 0 (Windup), 1 (Swing/Impact), 2 (Recovery)
        
        if state == "SIDE":
            # Side Chop
            if swing_f == 0: # Windup (Behind/Up)
                set_pixel(grid, 5, head_y - 1, 7) # Head
                set_pixel(grid, 6, head_y - 2, 7)
                set_pixel(grid, 6, head_y, 4)     # Handle
            elif swing_f == 1: # Impact (Forward/Down)
                set_pixel(grid, 12, body_y + 2, 7) # Head
                set_pixel(grid, 12, body_y + 3, 7)
                set_pixel(grid, 11, body_y + 2, 4) # Handle
                # Whoosh
                if f % 2 == 0: set_pixel(grid, 11, body_y - 1, 12) # Blueish swing trail
                
        elif state == "UP":
            if swing_f == 0: # High
                set_pixel(grid, 11, head_y - 2, 7)
                set_pixel(grid, 11, head_y, 4)
            elif swing_f == 1: # Low
                set_pixel(grid, 12, head_y + 2, 7)
                
        else: # DOWN / Default
            # Overhead Chop Front
            if swing_f == 0: # Windup (High above head)
                # Handle
                set_pixel(grid, 11, head_y - 4, 4) 
                set_pixel(grid, 11, head_y - 3, 4)
                set_pixel(grid, 11, head_y - 2, 4)
                # Blade (Big/Heavy)
                set_pixel(grid, 10, head_y - 4, 7)
                set_pixel(grid, 10, head_y - 3, 7)
                set_pixel(grid, 12, head_y - 4, 7)
                
            elif swing_f == 1: # Impact (Low/Forward) - CRUNCH
                # Handle extended down
                set_pixel(grid, 11, body_y + 2, 4)
                set_pixel(grid, 11, body_y + 3, 4)
                # Blade buried low
                set_pixel(grid, 10, body_y + 4, 7)
                set_pixel(grid, 11, body_y + 4, 7)
                set_pixel(grid, 12, body_y + 4, 7)
                # WHOOSH visual effect (Motion blur)
                set_pixel(grid, 10, body_y + 1, 12) # Frozen blue trail
                set_pixel(grid, 12, body_y, 12)
                
            elif swing_f >= 2: # Recovery (Slight lift)
                 # Axe rests near ground for a split second
                set_pixel(grid, 11, body_y + 3, 4)
                set_pixel(grid, 11, body_y + 4, 7)

    elif tool == "TORCH":
         # Torch Animation
         # Colors: 4 (Wood), 10 (Orange), 9 (Yellow Core)
         
         if is_lighting:
             # "Lighting" Action - Thrust torch forward/down to ignite
             if swing_f == 0: # Windup (Back/High)
                 set_pixel(grid, 6, head_y, 10) # Flame
                 set_pixel(grid, 6, head_y+1, 4) # Handle
             elif swing_f == 1: # Thrust (Forward/Down)
                 set_pixel(grid, 12, body_y + 3, 10) # Flame tip
                 set_pixel(grid, 12, body_y + 4, 9)  # Flame core
                 set_pixel(grid, 11, body_y + 4, 4)  # Handle
                 # Sparks/Embers
                 set_pixel(grid, 13, body_y + 2, 10)
                 set_pixel(grid, 11, body_y + 5, 10)
             else: # Hold (Steady near ground)
                 set_pixel(grid, 12, body_y + 4, 10)
                 set_pixel(grid, 11, body_y + 5, 4)
                 
         else:
             # Idle Hold (Bobbing logic handled by render_y)
             # Simple Torch
             set_pixel(grid, 11, body_y + 1, 10) # Flame
             set_pixel(grid, 11, body_y + 2, 4)  # Handle
             
             # Idle Flicker
             if f % 2 == 0:
                 set_pixel(grid, 11, body_y + 0, 9) # Core flicker
             else:
                 set_pixel(grid, 12, body_y + 1, 10) # Side flicker

    return add_selective_outline(grid)

# Null cycles
IDLE_CYCLE = [None, None]
WALK_CYCLE_DOWN = [None] * 4
WALK_CYCLE_UP = [None] * 4
WALK_CYCLE_SIDE = [None] * 4
