class TickSystem:
    def __init__(self, tick_interval=1.2):
        self.tick_interval = tick_interval
        self.time_since_last_tick = 0.0
        
    def update(self, dt, run_state, env_manager, player, floating_texts=None, event_manager=None):
        """Update tick timer and process tick events."""
        self.time_since_last_tick += dt
        
        if self.time_since_last_tick >= self.tick_interval:
            self.time_since_last_tick -= self.tick_interval
            self.process_tick(run_state, env_manager, player, floating_texts, event_manager)
    
    def process_tick(self, run_state, env_manager, player, floating_texts=None, event_manager=None):
        """Execute all survival and environmental updates on tick."""
        if not run_state:
            return
            
        # Increment global tick counter
        run_state.tick_count += 1
        
        # Check for Random Events
        if event_manager:
            event_manager.check_trigger(run_state)
            
        print(f"--- SURVIVAL TICK #{run_state.tick_count} ---")
        
        # 1. Update Campfires (consume fuel, decay)
        if env_manager:
            # Haven Logic: If Zone 1 stabilized, keep fires at 100%
            if run_state.current_zone_id == 1 and run_state.zone_1_stabilized:
                for fire in env_manager.campfires:
                    fire.fuel = 100.0
            else:
                fuel_multiplier = 2.0 if (event_manager and event_manager.active_event == "COLD_SNAP") else 1.0
                for fire in env_manager.campfires:
                    fire.update(self.tick_interval * fuel_multiplier)
            
            # Update resources (regrowth cycle)
            env_manager.update_ticks()
        
        # 2. Apply Temperature Decay
        self._apply_temperature_decay(run_state, env_manager, player, floating_texts, event_manager)
        
        # 3. Death is handled by main.py
    
    def _apply_temperature_decay(self, run_state, env_manager, player, floating_texts=None, event_manager=None):
        """Apply zone-based temperature changes."""
        # --- HAVEN LOGIC ---
        if run_state.current_zone_id == 1 and run_state.zone_1_stabilized:
            # No decay in stabilized Zone 1
            if run_state.body_temp < 37.0:
                 run_state.body_temp = min(37.0, run_state.body_temp + 2.0)
                 print(f"[TICK] Zone 1 Haven: Warming... {run_state.body_temp}°C")
            return

        # Check if player is near an active fire
        is_warmed = False
        if env_manager and player:
            for fire in env_manager.campfires:
                if fire.fuel > 0:
                    import pygame
                    dist = (pygame.Vector2(fire.rect.center) - player.pos).length()
                    if dist < 200:  # Heat radius
                        is_warmed = True
                        break
        
        if is_warmed:
            # Warming
            run_state.body_temp = min(37.0, run_state.body_temp + 2.0)
            print(f"[TICK] Warming... {run_state.body_temp}°C")
        else:
            # Freezing - Apply zone decay rate
            decay = 1.0
            wind_chill = 0
            
            if env_manager and env_manager.current_zone:
                decay = env_manager.current_zone.decay_rate
                
                # Wind Chill Calculation (Check Shelter)
                is_sheltered = False
                if env_manager and hasattr(env_manager, 'rocks'):
                    for rock in env_manager.rocks:
                        # Simple "Behind Rock" logic
                        # Assuming wind blows LEFT to RIGHT (or based on weather?)
                        # Let's say wind is consistently from WEST (Left)
                        # So standing to the RIGHT of a rock is sheltered.
                        rock_center = rock.rect.center
                        if (player.pos.x > rock_center[0] and player.pos.x < rock_center[0] + 100) and \
                           abs(player.pos.y - rock_center[1]) < 50:
                            is_sheltered = True
                            run_state.is_sheltered = True # Flag for UI
                            break
                
                wind_chill = 0 if is_sheltered else env_manager.current_zone.wind_chill
                if not is_sheltered: run_state.is_sheltered = False
            
            # Cold Snap Difficulty Spike
            multiplier = 2.0 if (event_manager and event_manager.active_event == "COLD_SNAP") else 1.0
            total_decay = (decay + wind_chill) * multiplier
            
            # Fur Lining Upgrade
            if run_state.fur_lining:
                total_decay *= 0.8
            
            run_state.body_temp -= total_decay
            
            # Spawn Floating Text for Freeze
            if floating_texts is not None and player:
                from ui.floating_text import FloatingText
                msg = f"-{total_decay:.1f} TEMP"
                floating_texts.append(FloatingText(player.pos.x + 36, player.pos.y, msg, (100, 150, 255))) # Light blue
                
            print(f"[TICK] Freezing (-{total_decay})... {run_state.body_temp}°C")
