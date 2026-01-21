class ZoneData:
    def __init__(self, id, name, decay_rate, resource_count, wind_chill, goals, is_stabilized=False):
        self.id = id
        self.name = name
        self.decay_rate = decay_rate
        self.resource_count = resource_count
        self.wind_chill = wind_chill
        self.goals = goals
        self.is_stabilized = is_stabilized

class ZoneManager:
    def __init__(self):
        self.zones = {
            0: ZoneData(
                id=0,
                name="The Homestead",
                decay_rate=0.0,  # No freezing in tutorial
                resource_count=5,  # Just a few trees to practice
                wind_chill=0,
                goals={"tutorial": True},
                is_stabilized=True  # Always safe
            ),
            1: ZoneData(
                id=1, 
                name="The Quiet Woods", 
                decay_rate=1.0, 
                resource_count=15, 
                wind_chill=0, 
                goals={"survive_time": 60},
                is_stabilized=False  # Can be stabilized by player
            ),
            2: ZoneData(
                id=2, 
                name="The Wind Gap", 
                decay_rate=3.0, # Harder
                resource_count=5, # Scarce
                wind_chill=1, 
                goals={"survive_time": 120},
                is_stabilized=False
            ),
            3: ZoneData(
                id=3, 
                name="Builder's Ridge", 
                decay_rate=2.0, 
                resource_count=10, 
                wind_chill=1, 
                goals={"build": True},
                is_stabilized=False
            )
        }
        self.stabilized_zones = []  # Track which zones player has stabilized
    
    def get_zone(self, zone_id):
        zone = self.zones.get(zone_id, self.zones[1])
        # Update stabilization status
        zone.is_stabilized = zone_id in self.stabilized_zones
        return zone
    
    def stabilize_zone(self, zone_id):
        """Mark a zone as stabilized."""
        if zone_id not in self.stabilized_zones:
            self.stabilized_zones.append(zone_id)
            print(f"Zone {zone_id} STABILIZED!")
            return True
        return False
        
    def get_next_zone(self, current_id):
        # Linear progression for now
        next_id = current_id + 1
        return next_id if next_id in self.zones else 1 # Loop back
    
    def load_stabilized_zones(self, stabilized_list):
        """Load stabilized zones from save data."""
        self.stabilized_zones = stabilized_list if stabilized_list else []

    def reset(self):
        """Reset progression for new game."""
        self.stabilized_zones = []
        # Potentially reset internal ZoneData if needed, but get_zone handles overwrite
