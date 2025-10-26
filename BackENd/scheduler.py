from typing import List, Dict
from models import NetworkLoad, CrewMember, Patch, ScheduledPatch
import math

class PatchScheduler:
    """Optimizes patch scheduling based on network load, crew availability, and patch requirements"""
    
    def __init__(self):
        pass
    
    def calculate_score(self, patch: Patch, start_hour: int, network_loads: List[NetworkLoad], 
                       available_crew: List[CrewMember]) -> float:
        """Calculate a score for scheduling a patch at a specific time
        
        Higher score = better scheduling window
        Score is based on THREE key factors:
        1. Network Load (kW at that hour) - Lower is better (40 points max)
        2. Crew Available - More is better (30 points max)
        3. Priority - Higher priority gets higher score (30 points max)
        """
        score = 0
        
        # 1. NETWORK LOAD FACTOR (40 points max)
        # Get network load at the start hour (in kilowatts)
        load_kw = next((l.load_kilowatts for l in network_loads if l.hour == start_hour), 50)
        
        # Lower load = higher score
        if load_kw < 20:
            load_score = 40
        elif load_kw < 30:
            load_score = 30
        elif load_kw < 40:
            load_score = 20
        elif load_kw < 50:
            load_score = 10
        else:
            load_score = 5  # High load, not ideal
        
        score += load_score
        
        # 2. CREW AVAILABILITY FACTOR (30 points max)
        crew_count = len(available_crew)
        crew_needed = patch.min_crew
        
        if crew_count >= crew_needed * 2:
            crew_score = 30  # Plenty of crew available
        elif crew_count >= crew_needed + 2:
            crew_score = 25  # Good crew availability
        elif crew_count >= crew_needed + 1:
            crew_score = 20  # Extra crew available
        elif crew_count >= crew_needed:
            crew_score = 15  # Just enough crew
        else:
            crew_score = 0   # Not enough crew
        
        score += crew_score
        
        # 3. PRIORITY FACTOR (30 points max)
        # Higher priority = higher score
        priority_score = (patch.priority / 5.0) * 30
        
        score += priority_score
        
        # Return score (0-100 scale)
        return round(min(100, max(0, score)), 2)
    
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

