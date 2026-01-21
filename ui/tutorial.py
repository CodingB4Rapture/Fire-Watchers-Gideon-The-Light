import pygame

def draw_tutorial_ui(surface, run_state, width, height):
    """Draw tutorial prompts based on current step."""
    if run_state.tutorial_completed or run_state.current_zone_id != 0:
        return
    
    # Tutorial prompt box
    box_height = 80
    box_y = height - box_height - 20
    
    # Semi-transparent background
    overlay = pygame.Surface((width - 40, box_height), pygame.SRCALPHA)
    overlay.fill((20, 20, 30, 200))
    surface.blit(overlay, (20, box_y))
    
    # Border
    pygame.draw.rect(surface, (200, 180, 100), (20, box_y, width - 40, box_height), 3)
    
    # Tutorial text based on step
    font_large = pygame.font.SysFont("Arial", 28, bold=True)
    font_small = pygame.font.SysFont("Arial", 20)
    
    if run_state.tutorial_step == 0:
        # Step 0: Movement
        title = font_large.render("LEARN TO MOVE", True, (255, 220, 100))
        prompt = font_small.render("Use WASD or Arrow Keys to walk around", True, (220, 220, 220))
        progress = font_small.render(f"Distance: {int(run_state.distance_moved)}/100", True, (150, 200, 255))
        
        surface.blit(title, (width // 2 - title.get_width() // 2, box_y + 10))
        surface.blit(prompt, (width // 2 - prompt.get_width() // 2, box_y + 40))
        surface.blit(progress, (width // 2 - progress.get_width() // 2, box_y + 60))
        
    elif run_state.tutorial_step == 1:
        # Step 1: Gathering
        title = font_large.render("GATHER WOOD", True, (255, 220, 100))
        prompt = font_small.render("Press SPACE near a tree to chop it", True, (220, 220, 220))
        progress = font_small.render(f"Logs: {run_state.inventory['logs']}/1", True, (150, 200, 255))
        
        surface.blit(title, (width // 2 - title.get_width() // 2, box_y + 10))
        surface.blit(prompt, (width // 2 - prompt.get_width() // 2, box_y + 40))
        surface.blit(progress, (width // 2 - progress.get_width() // 2, box_y + 60))
        
    elif run_state.tutorial_step == 2:
        # Step 2: Fueling
        title = font_large.render("STOKE THE FIRE", True, (255, 220, 100))
        prompt = font_small.render("Press E near the Elder's fire to add fuel", True, (220, 220, 220))
        hint = font_small.render("The fire keeps you warm in the cold", True, (180, 180, 180))
        
        surface.blit(title, (width // 2 - title.get_width() // 2, box_y + 10))
        surface.blit(prompt, (width // 2 - prompt.get_width() // 2, box_y + 35))
        surface.blit(hint, (width // 2 - hint.get_width() // 2, box_y + 58))
        
    elif run_state.tutorial_step == 3:
        # Step 3: Departure
        title = font_large.render("THE ELDER SPEAKS", True, (255, 220, 100))
        quote = font_small.render('"The woods are turning... Go."', True, (220, 220, 220))
        prompt = font_small.render("Walk to the right edge to enter The Quiet Woods", True, (150, 200, 255))
        
        surface.blit(title, (width // 2 - title.get_width() // 2, box_y + 10))
        surface.blit(quote, (width // 2 - quote.get_width() // 2, box_y + 35))
        surface.blit(prompt, (width // 2 - prompt.get_width() // 2, box_y + 58))
