from typing import List, Dict
from models import NetworkLoad, CrewMember, Patch, ScheduledPatch
import math

class PatchScheduler:
    """Optimizes patch scheduling based on network load, crew availability, and patch requirements"""
    
    def __init__(self):
        self.network_load_weight = 0.4
        self.crew_availability_weight = 0.3
        self.priority_weight = 0.3
    
    def calculate_score(self, patch: Patch, start_hour: int, network_loads: List[NetworkLoad], 
                       available_crew: List[CrewMember]) -> float:
        """Calculate a score for scheduling a patch at a specific time
        
        Higher score = better scheduling window
        Score is based on:
        - Lower network load (better)
        - More available crew (better)
        - Higher priority patches get bonus
        """
        # Get average network load during patch window (in kilowatts)
        patch_duration_hours = int(math.ceil(patch.duration))
        load_sum = 0
        max_possible_load = 90  # Maximum expected load in kW
        
        for i in range(patch_duration_hours):
            hour = (start_hour + i) % 24
            load = next((l.load_kilowatts for l in network_loads if l.hour == hour), 50)
            load_sum += load
        avg_load = load_sum / patch_duration_hours
        
        # Network load score (inverted - lower load is better)
        network_score = (max_possible_load - avg_load) / max_possible_load
        
        # Crew availability score
        crew_count = len(available_crew)
        crew_score = min(crew_count / (patch.min_crew * 2), 1.0)  # Ideal is 2x minimum crew
        
        # Priority bonus
        priority_score = patch.priority / 5.0
        
        # Calculate weighted total
        total_score = (
            network_score * self.network_load_weight +
            crew_score * self.crew_availability_weight +
            priority_score * self.priority_weight
        )
        
        return total_score * 100  # Scale to 0-100
    
    def get_available_crew_at_hour(self, hour: int, crew: List[CrewMember], 
                                   already_scheduled: Dict[int, List[str]]) -> List[CrewMember]:
        """Get crew members available at a specific hour who aren't already scheduled"""
        scheduled_names = already_scheduled.get(hour, [])
        return [
            member for member in crew 
            if member.is_available(hour) and member.name not in scheduled_names
        ]
    
    def optimize(self, network_loads: List[NetworkLoad], crew: List[CrewMember], 
                patches: List[Patch]) -> List[Dict]:
        """Find optimal schedule for all patches
        
        Uses a greedy algorithm:
        1. Sort patches by priority (highest first)
        2. For each patch, find the best time window
        3. Schedule it and mark crew as busy
        """
        scheduled_patches = []
        already_scheduled = {}  # hour -> list of crew names
        
        # Sort patches by priority (highest first)
        sorted_patches = sorted(patches, key=lambda p: p.priority, reverse=True)
        
        for patch in sorted_patches:
            best_score = -1
            best_hour = None
            best_crew = None
            
            # Try each hour of the day
            for start_hour in range(24):
                # Check if enough crew available for entire patch duration
                patch_duration_hours = int(math.ceil(patch.duration))
                crew_available = True
                min_crew_count = float('inf')
                
                for i in range(patch_duration_hours):
                    hour = (start_hour + i) % 24
                    available = self.get_available_crew_at_hour(hour, crew, already_scheduled)
                    if len(available) < patch.min_crew:
                        crew_available = False
                        break
                    min_crew_count = min(min_crew_count, len(available))
                
                if not crew_available:
                    continue
                
                # Get available crew for scoring
                available = self.get_available_crew_at_hour(start_hour, crew, already_scheduled)
                
                # Calculate score for this time slot
                score = self.calculate_score(patch, start_hour, network_loads, available)
                
                if score > best_score:
                    best_score = score
                    best_hour = start_hour
                    best_crew = available[:patch.min_crew]  # Assign minimum needed crew
            
            if best_hour is not None and best_crew:
                # Schedule the patch
                end_hour = best_hour + patch.duration
                
                # Get network load at start hour
                network_load = next(
                    (l.load_kilowatts for l in network_loads if l.hour == best_hour), 
                    50
                )
                
                scheduled = ScheduledPatch(
                    patch=patch,
                    start_hour=best_hour,
                    end_hour=end_hour,
                    assigned_crew=[member.name for member in best_crew],
                    network_load=network_load,
                    score=best_score
                )
                
                scheduled_patches.append(scheduled.to_dict())
                
                # Mark crew as busy for the duration
                patch_duration_hours = int(math.ceil(patch.duration))
                for i in range(patch_duration_hours):
                    hour = (best_hour + i) % 24
                    if hour not in already_scheduled:
                        already_scheduled[hour] = []
                    already_scheduled[hour].extend([member.name for member in best_crew])
            else:
                # Could not schedule this patch
                unscheduled = {
                    'patch': patch.to_dict(),
                    'status': 'unscheduled',
                    'reason': 'Insufficient crew availability'
                }
                scheduled_patches.append(unscheduled)
        
        return scheduled_patches

