import sys
import os
from PIL import Image

# Define Palette from player.py
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
}

# Image Paths provided by user (COMPLETE WALK DOWN Frames)
USER_IMAGES = [
    "C:/Users/sethj/.gemini/antigravity/brain/c8c42f8d-d7ff-40c0-9c42-b21225e871de/uploaded_image_0_1768929804560.png", # WALK DOWN FRAME 1
    "C:/Users/sethj/.gemini/antigravity/brain/c8c42f8d-d7ff-40c0-9c42-b21225e871de/uploaded_image_1_1768929804560.png", # WALK DOWN FRAME 2
    "C:/Users/sethj/.gemini/antigravity/brain/c8c42f8d-d7ff-40c0-9c42-b21225e871de/uploaded_image_2_1768929804560.png", # WALK DOWN FRAME 3
    "C:/Users/sethj/.gemini/antigravity/brain/c8c42f8d-d7ff-40c0-9c42-b21225e871de/uploaded_image_3_1768929804560.png", # WALK DOWN FRAME 4
]

def closest_color_index(pixel):
    """Find closest palette index for a given RGB/RGBA pixel."""
    if len(pixel) == 4 and pixel[3] < 128:
        return 0  # Transparent
    
    min_dist = float('inf')
    best_idx = 0
    
    r, g, b = pixel[:3]
    
    for idx, color in PALETTE.items():
        if idx == 0: continue # Skip transparent check for solids
        if idx > 12: continue # Skip ignored colors
        
        pr, pg, pb = color[:3]
        dist = (r - pr)**2 + (g - pg)**2 + (b - pb)**2
        
        if dist < min_dist:
            min_dist = dist
            best_idx = idx
            
    return best_idx

def process_single_frame(img_path):
    if not os.path.exists(img_path):
        print(f"Error: Image not found {img_path}")
        return None

    try:
        img = Image.open(img_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening {img_path}: {e}")
        return None

    width, height = img.size
    
    # Center the sprite in the 18x24 grid
    grid = [[0 for _ in range(18)] for _ in range(24)]
    
    # Calculate offset to center (assuming 16x16 input)
    off_x = (18 - width) // 2
    off_y = (24 - height) // 2
    
    # Clamp offsets
    off_x = max(0, off_x)
    off_y = max(0, off_y)
    
    for y in range(min(height, 24)):
        for x in range(min(width, 18)):
            pixel = img.getpixel((x, y))
            idx = closest_color_index(pixel)
            
            # Apply to grid
            grid_y = y + off_y
            grid_x = x + off_x
            if 0 <= grid_y < 24 and 0 <= grid_x < 18:
                grid[grid_y][grid_x] = idx
                
    return grid

# Process specific frames for WALK_DOWN
frames = []
for path in USER_IMAGES:
    grid = process_single_frame(path)
    if grid:
        frames.append(grid)

# Append to file overwrite WALK_DOWN_FRAMES completely
with open("data/sprite_data.py", "a") as f:
    f.write("\n# COMPLETE WALK_DOWN_FRAMES Overwrite\n")
    f.write("WALK_DOWN_FRAMES = [\n")
    for i, grid in enumerate(frames):
        f.write(f"    # Frame {i}\n")
        f.write("    [\n")
        for row in grid:
            f.write(f"        {row},\n")
        f.write("    ],\n")
    f.write("]\n")
