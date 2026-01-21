import json
import os
from data.run_state import RunState

class SaveManager:
    def __init__(self, save_file="savegame.json"):
        self.save_file = save_file
    
    def save_exists(self):
        """Check if a save file exists."""
        return os.path.exists(self.save_file)
    
    def save_game(self, run_state, player_pos=None, stabilized_zones=None):
        """Serialize RunState and game progress to JSON."""
        if not run_state:
            print("Cannot save: No RunState")
            return False
        
        save_data = {
            "run_state": {
                "body_temp": run_state.body_temp,
                "inventory": run_state.inventory,
                "tick_count": run_state.tick_count,
                "current_zone_id": run_state.current_zone_id,
                "is_alive": run_state.is_alive,
                "log_stash": getattr(run_state, "log_stash", 0),
                "zone_1_stabilized": getattr(run_state, "zone_1_stabilized", False),
                "zone_1_resources_depleted": getattr(run_state, "zone_1_resources_depleted", False),
                "logs_deposited_in_zone_1": getattr(run_state, "logs_deposited_in_zone_1", 0),
                "logs_deposited_in_zone_2": getattr(run_state, "logs_deposited_in_zone_2", 0),
                "zone_2_redeemed": getattr(run_state, "zone_2_redeemed", False),
                "shack_progress": getattr(run_state, "shack_progress", {"logs": 0, "sticks": 0, "state": 0}),
                "beacon_lit": getattr(run_state, "beacon_lit", False),
                "zone_2_hub": {
                     "fire_fuel": getattr(run_state, "zone_2_hub_fire_fuel", 0.0)
                }
            },
            "player": {
                "pos_x": player_pos[0] if player_pos else 400,
                "pos_y": player_pos[1] if player_pos else 300
            },
            "world": {
                "stabilized_zones": stabilized_zones if stabilized_zones else []
            }
        }
        
        try:
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            print(f"Game saved to {self.save_file}")
            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False
    
    def load_game(self):
        """Deserialize RunState from JSON."""
        if not self.save_exists():
            print("No save file found")
            return None
        
        try:
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            
            # Reconstruct RunState
            run_state = RunState()
            rs_data = save_data.get("run_state", {})
            run_state.body_temp = rs_data.get("body_temp", 37.0)
            # Ensure all expected keys exist in inventory (backward compatibility)
            loaded_inv = rs_data.get("inventory", {})
            run_state.inventory["logs"] = loaded_inv.get("logs", 0)
            run_state.inventory["sticks"] = loaded_inv.get("sticks", 0)
            run_state.tick_count = rs_data.get("tick_count", 0)
            run_state.current_zone_id = rs_data.get("current_zone_id", 1)
            run_state.is_alive = rs_data.get("is_alive", True)
            run_state.log_stash = rs_data.get("log_stash", 0)
            run_state.zone_1_stabilized = rs_data.get("zone_1_stabilized", False)
            run_state.zone_1_resources_depleted = rs_data.get("zone_1_resources_depleted", False)
            run_state.logs_deposited_in_zone_1 = rs_data.get("logs_deposited_in_zone_1", 0)
            run_state.logs_deposited_in_zone_2 = rs_data.get("logs_deposited_in_zone_2", 0)
            run_state.zone_2_redeemed = rs_data.get("zone_2_redeemed", False)
            run_state.shack_progress = rs_data.get("shack_progress", {"logs": 0, "sticks": 0, "state": 0})
            run_state.last_log_deposit_time = 0.0 # Don't persist UI flash
            run_state.beacon_lit = rs_data.get("beacon_lit", False)
            
            # Hub State (Zone 2)
            hub_data = rs_data.get("zone_2_hub", {})
            run_state.zone_2_hub_fire_fuel = hub_data.get("fire_fuel", 0.0)
            
            run_state.tutorial_step = rs_data.get("tutorial_step", 0)
            run_state.tutorial_completed = rs_data.get("tutorial_completed", False)
            run_state.time_in_current_zone = rs_data.get("time_in_current_zone", 0.0)
            
            # Extract additional data
            player_data = save_data.get("player", {})
            player_pos = (player_data.get("pos_x", 400), player_data.get("pos_y", 300))
            
            world_data = save_data.get("world", {})
            stabilized_zones = world_data.get("stabilized_zones", [])
            
            print(f"Game loaded from {self.save_file}")
            print(f"  Zone: {run_state.current_zone_id}, Temp: {run_state.body_temp}°C, Logs: {run_state.inventory['logs']}")
            
            return {
                "run_state": run_state,
                "player_pos": player_pos,
                "stabilized_zones": stabilized_zones
            }
            
        except Exception as e:
            print(f"Load failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def delete_save(self):
        """Delete the save file."""
        if self.save_exists():
            try:
                os.remove(self.save_file)
                print(f"Save file {self.save_file} deleted")
                return True
            except Exception as e:
                print(f"Delete failed: {e}")
                return False
        return False
