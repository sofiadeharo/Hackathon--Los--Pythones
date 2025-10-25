from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class NetworkLoad:
    """Represents network load at a specific hour"""
    hour: int
    load_kilowatts: float
    day_of_week: str
    day_number: int  # 0=Monday, 6=Sunday
    
    def to_dict(self):
        return {
            'hour': self.hour,
            'load_kilowatts': self.load_kilowatts,
            'day_of_week': self.day_of_week,
            'day_number': self.day_number
        }

@dataclass
class CrewMember:
    """Represents a crew member and their availability"""
    name: str
    available_hours: List[Tuple[int, int]]  # List of (start_hour, end_hour) tuples
    skill_level: int  # 1-5, where 5 is most skilled
    
    def is_available(self, hour: int) -> bool:
        """Check if crew member is available at a specific hour"""
        for start, end in self.available_hours:
            if start <= hour < end:
                return True
        return False
    
    def to_dict(self):
        return {
            'name': self.name,
            'available_hours': self.available_hours,
            'skill_level': self.skill_level
        }

@dataclass
class Patch:
    """Represents a system patch that needs to be scheduled"""
    id: int
    name: str
    duration: float  # Duration in hours
    priority: int  # 1-5, where 5 is highest priority
    min_crew: int  # Minimum number of crew members needed
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'duration': self.duration,
            'priority': self.priority,
            'min_crew': self.min_crew
        }

@dataclass
class ScheduledPatch:
    """Represents a patch that has been scheduled"""
    patch: Patch
    start_hour: int
    end_hour: float
    assigned_crew: List[str]
    network_load: int
    score: float
    
    def to_dict(self):
        return {
            'patch': self.patch.to_dict(),
            'start_hour': self.start_hour,
            'end_hour': self.end_hour,
            'assigned_crew': self.assigned_crew,
            'network_load': self.network_load,
            'score': self.score
        }

