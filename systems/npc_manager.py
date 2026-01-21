from entities.npc import NPC
import random

class NPCManager:
    def __init__(self):
        self.npcs = []
        self.spawn_timer = 0.0
        self.spawn_interval = 15.0  # Spawn NPC every 15 seconds
    
    def spawn_npc_for_zone(self, zone_data, run_state, screen_width=1280, screen_height=720):
        """Spawn appropriate NPC based on zone state and narrative."""
        zone_id = zone_data.id
        
        # ZONE 0: THE ELDER (Tutorial)
        if zone_id == 0:
            print("Spawning ELDER in Zone 0")
            npc = NPC(600, 300, npc_type="keeper", npc_id="ELDER")
            npc.dialogue_lines = [
                "Welcome, traveler.",
                "The cold is coming. You must learn to survive.",
                "Gather wood. Keep the fire burning.",
            ]
            self.npcs.append(npc)
            return npc
            
        # ZONE 1: THE WOODS
        elif zone_id == 1:
            if run_state.zone_1_stabilized:
                # Elder takes over the fire
                print("Spawning ELDER in Stabilized Zone 1")
                # Position near haven fire (400, 350 -> +60, -40)
                npc = NPC(460, 310, npc_type="keeper", npc_id="ELDER")
                npc.dialogue_lines = [
                    "The wind is worse in the Gap.",
                    "Stockpile here. I will keep the fire."
                ]
                self.npcs.append(npc)
                return npc
            else:
                # Saboteurs
                print("Spawning SABOTEUR in Unstable Zone 1")
                # Random edge spawn
                edge = random.choice(["top", "bottom", "left", "right"])
                if edge == "top": x, y = random.randint(100, screen_width-100), 50
                elif edge == "bottom": x, y = random.randint(100, screen_width-100), screen_height-100
                elif edge == "left": x, y = 50, random.randint(100, screen_height-100)
                else: x, y = screen_width-100, random.randint(100, screen_height-100)
                
                npc = NPC(x, y, npc_type="saboteur", npc_id="GENERIC")
                self.npcs.append(npc)
                return npc
                
        # ZONE 2: THE GAP
        elif zone_id == 2:
            # Builder appears here if not already at Zone 3?
            # Prompt: "When load_zone(2) triggers: Spawn Builder... Dialogue..."
            if run_state.builder_location == 2:
                print("Spawning BUILDER in Zone 2")
                # Spawn near entrance (Left side)
                npc = NPC(150, 300, npc_type="keeper", npc_id="BUILDER")
                npc.dialogue_lines = [
                    "I made it ahead of you.",
                    "It's brutal out here.",
                    "Help me get these walls up, and we'll have a warm place to trade."
                ]
                self.npcs.append(npc)
                return npc
            else:
                # Just saboteurs or empty?
                # Saboteurs active in Zone 2?
                if not run_state.zone_2_redeemed:
                     # Spawning logic for saboteurs
                     pass
        
        # ZONE 3: BUILDER'S RIDGE
        elif zone_id == 3:
            print("Spawning BUILDER in Zone 3")
            npc = NPC(260, 250, npc_type="keeper", npc_id="BUILDER")
            npc.dialogue_lines = ["Check the shop update."] # Dynamic
            self.npcs.append(npc)
            return npc

        return None
    
    def update(self, dt, run_state, env_manager):
        """Update all NPCs."""
        # Update existing NPCs
        for npc in self.npcs:
            npc.update(dt, run_state, env_manager)
        
        # Spawn timer (for automatic spawning)
        self.spawn_timer += dt
    
    def clear_npcs(self):
        """Remove all NPCs (for zone transitions)."""
        self.npcs.clear()
        print("All NPCs cleared")
    
    def get_npc_count(self):
        """Return current NPC count."""
        return len(self.npcs)
