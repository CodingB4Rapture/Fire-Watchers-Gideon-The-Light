class RunState:
    def __init__(self):
        self.body_temp = 37.0
        self.inventory = {"logs": 0, "sticks": 0}
        self.tick_count = 0
        self.current_zone_id = 0  # Start in tutorial zone
        self.is_alive = True
        self.is_sheltered = False # For UI Feedback (Wind Break)
        self.total_logs_gathered = 0
        self.logs_deposited_in_zone_1 = 0
        self.zone_1_stabilized = False
        self.log_stash = 0
        self.zone_1_resources_depleted = False
        self.logs_deposited_in_zone_2 = 0
        self.zone_2_redeemed = False
        self.shack_progress = {"logs": 0, "sticks": 0, "state": 0}
        self.logs_deposited_in_zone_3 = 0
        self.last_log_deposit_time = 0.0 # For UI feedback
        self.beacon_lit = False
        self.zone_2_hub_fire_fuel = 0.0 # Track Zone 2 Fire Fuel
        self.builder_location = 1 # 1=Z1, 2=Z2 (Moved from main loop)
        
        # Upgrades (Barter System)
        self.axe_upgrade = False
        self.fur_lining = False
        self.deep_pockets = False
        
        # Tutorial tracking
        self.tutorial_step = 0  # 0=Move, 1=Gather, 2=Fuel, 3=Depart
        self.tutorial_completed = False
        self.distance_moved = 0.0  # Track movement for tutorial
        
        # NPC Tracking
        self.builder_location = 1 # Starts in Zone 1 (Conceptually) or 0? 
        # Actually in Zone 0 it's the Elder. Builder appears later.
        # Let's say Builder is in Zone 1 initially (unstable) or appearing there?
        # Prompt says: "When Zone 1 is done... Set builder_location = 2." implied he was in 1.
        self.builder_location = 1
        
        # Cold Snap balancing
        self.time_in_current_zone = 0.0  # Grace period tracking
        
    def add_log(self, count=1):
        from constants import MAX_LOG_SLOTS
        self.inventory["logs"] = min(MAX_LOG_SLOTS, self.inventory["logs"] + count)
        self.total_logs_gathered += count
        
    def remove_log(self, count=1):
        if self.inventory["logs"] >= count:
            self.inventory["logs"] -= count
            return True
        return False
        
    def deposit_log_zone_1(self):
        self.logs_deposited_in_zone_1 += 1
        if self.logs_deposited_in_zone_1 >= 20:
            if not self.zone_1_stabilized:
                self.zone_1_stabilized = True
                return True # Signal stabilization
        return False

    def deposit_log_zone_2(self):
        self.logs_deposited_in_zone_2 += 1
        if self.logs_deposited_in_zone_2 >= 30:
             # We return True to signal the "Redemption" event should start.
             # Actual stabilization happens after the event.
             return True
        return False

    def get_log_count(self):
        return self.inventory.get("logs", 0)
