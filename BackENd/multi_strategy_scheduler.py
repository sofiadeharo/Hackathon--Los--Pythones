"""
Multi-Strategy Scheduler
Provides multiple scheduling strategies based on different priorities
"""

from scheduler import PatchScheduler
from ml_optimizer import ml_optimizer

class MultiStrategyScheduler:
    def __init__(self):
        self.basic_scheduler = PatchScheduler()
    
    def generate_multiple_schedules(self, patches, crew, network_loads):
        """
        Generate multiple schedule options with different strategies
        Returns 3 schedules: Network-Optimized, Urgency-First, and Balanced
        """
        strategies = {
            'network_optimized': self._network_optimized_schedule(patches, crew, network_loads),
            'urgency_first': self._urgency_first_schedule(patches, crew, network_loads),
            'balanced': self._balanced_schedule(patches, crew, network_loads)
        }
        
        return strategies
    
    def _network_optimized_schedule(self, patches, crew, network_loads):
        """
        Strategy 1: Prioritize lowest network load times
        Best for: Minimizing system impact
        """
        # Sort patches by priority (handle high priority first, but optimize for load)
        sorted_patches = sorted(patches, key=lambda p: -p.priority)
        
        scheduled = []
        already_scheduled = {}
        
        for patch in sorted_patches:
            # Use ML optimizer to find optimal time based on network load
            optimal_times = ml_optimizer.find_optimal_hours_for_patch(patch, len(crew), top_n=10)
            
            # Find first available time slot with sufficient crew
            scheduled_patch = None
            for time_slot in optimal_times:
                hour = time_slot['hour']
                
                # Check crew availability
                duration_hours = int(patch.duration)
                crew_available = True
                
                for i in range(duration_hours):
                    check_hour = (hour + i) % 24
                    if check_hour in already_scheduled:
                        busy_crew = already_scheduled[check_hour]
                        available_crew = [c for c in crew if c.name not in busy_crew]
                    else:
                        available_crew = crew
                    
                    if len(available_crew) < patch.min_crew:
                        crew_available = False
                        break
                
                if crew_available:
                    # Schedule here
                    available_crew_list = [c for c in crew if hour not in already_scheduled or c.name not in already_scheduled.get(hour, [])]
                    assigned_crew = available_crew_list[:patch.min_crew]
                    
                    scheduled_patch = {
                        'patch': patch.to_dict(),
                        'start_hour': hour,
                        'end_hour': hour + patch.duration,
                        'day': time_slot['day'],
                        'assigned_crew': [c.name for c in assigned_crew],
                        'network_load': time_slot['predicted_load_kw'],
                        'score': time_slot['score'],
                        'status': 'scheduled',
                        'reason': f"Optimal network load: {time_slot['predicted_load_kw']:.1f} kW"
                    }
                    
                    # Mark crew as busy
                    for i in range(duration_hours):
                        busy_hour = (hour + i) % 24
                        if busy_hour not in already_scheduled:
                            already_scheduled[busy_hour] = []
                        already_scheduled[busy_hour].extend([c.name for c in assigned_crew])
                    
                    break
            
            if scheduled_patch:
                scheduled.append(scheduled_patch)
            else:
                # Unscheduled
                scheduled.append({
                    'patch': patch.to_dict(),
                    'status': 'unscheduled',
                    'reason': 'No available time slot with sufficient crew'
                })
        
        return {
            'strategy': 'Network Optimized',
            'description': 'Prioritizes lowest network load times to minimize system impact',
            'icon': '📊',
            'schedule': scheduled
        }
    
    def _urgency_first_schedule(self, patches, crew, network_loads):
        """
        Strategy 2: Prioritize high-priority patches ASAP
        Best for: Critical patches that need immediate attention
        """
        # Sort by priority first, then by duration
        sorted_patches = sorted(patches, key=lambda p: (-p.priority, p.duration))
        
        scheduled = []
        already_scheduled = {}
        
        for patch in sorted_patches:
            # Find earliest possible time (prioritize urgency over network load)
            best_hour = None
            best_score = -1
            best_crew = None
            best_load = 0
            
            # Start from hour 0 and find first available slot
            for start_hour in range(24):
                duration_hours = int(patch.duration)
                crew_available = True
                
                # Check crew availability
                for i in range(duration_hours):
                    check_hour = (start_hour + i) % 24
                    if check_hour in already_scheduled:
                        busy_crew = already_scheduled[check_hour]
                        available_crew = [c for c in crew if c.name not in busy_crew and check_hour in [h for start, end in c.available_hours for h in range(start, end)]]
                    else:
                        available_crew = [c for c in crew if check_hour in [h for start, end in c.available_hours for h in range(start, end)]]
                    
                    if len(available_crew) < patch.min_crew:
                        crew_available = False
                        break
                
                if crew_available:
                    # Calculate score for this time
                    network_load = next(
                        (l.load_kilowatts for l in network_loads if l.hour == start_hour),
                        40
                    )
                    
                    # Score favors early hours for urgent patches
                    score = 100 - start_hour  # Earlier = higher score
                    
                    if score > best_score:
                        best_score = score
                        best_hour = start_hour
                        best_load = network_load
                        
                        available_crew_list = [c for c in crew if start_hour not in already_scheduled or c.name not in already_scheduled.get(start_hour, [])]
                        best_crew = available_crew_list[:patch.min_crew]
            
            if best_hour is not None and best_crew:
                scheduled_patch = {
                    'patch': patch.to_dict(),
                    'start_hour': best_hour,
                    'end_hour': best_hour + patch.duration,
                    'assigned_crew': [c.name for c in best_crew],
                    'network_load': best_load,
                    'score': best_score,
                    'status': 'scheduled',
                    'reason': f"Earliest available slot for priority {patch.priority}"
                }
                
                # Mark crew as busy
                duration_hours = int(patch.duration)
                for i in range(duration_hours):
                    busy_hour = (best_hour + i) % 24
                    if busy_hour not in already_scheduled:
                        already_scheduled[busy_hour] = []
                    already_scheduled[busy_hour].extend([c.name for c in best_crew])
                
                scheduled.append(scheduled_patch)
            else:
                scheduled.append({
                    'patch': patch.to_dict(),
                    'status': 'unscheduled',
                    'reason': 'No available time slot with sufficient crew'
                })
        
        return {
            'strategy': 'Urgency First',
            'description': 'Schedules high-priority patches as soon as possible',
            'icon': '🚨',
            'schedule': scheduled
        }
    
    def _balanced_schedule(self, patches, crew, network_loads):
        """
        Strategy 3: Balance between network load and urgency
        Best for: General use - considers both factors
        """
        # Use the basic scheduler (already balanced)
        schedule = self.basic_scheduler.schedule_patches(patches, crew, network_loads)
        
        return {
            'strategy': 'Balanced',
            'description': 'Balances network load optimization with patch priority',
            'icon': '⚖️',
            'schedule': schedule
        }
    
    def get_alternative_times_for_patch(self, patch, crew, network_loads, top_n=5):
        """
        Get alternative scheduling options for a specific patch
        """
        optimal_times = ml_optimizer.find_optimal_hours_for_patch(patch, len(crew), top_n=top_n)
        
        alternatives = []
        for time_slot in optimal_times:
            alternatives.append({
                'day': time_slot['day'],
                'hour': time_slot['hour'],
                'time_display': time_slot['time_display'],
                'network_load': time_slot['predicted_load_kw'],
                'score': time_slot['score'],
                'classification': time_slot['patch_type'],
                'confidence': time_slot['confidence']
            })
        
        return alternatives


# Global instance
multi_strategy_scheduler = MultiStrategyScheduler()

