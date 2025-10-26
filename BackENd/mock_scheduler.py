"""
Mock Scheduler with Random Forest Model
Generates realistic scheduling data for demonstration purposes
"""

import random
from models import Patch
from network_load_predictor import network_load_predictor
from patch_classifier import patch_classifier

class MockScheduler:
    def __init__(self):
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.crew_names = [
            'Alex Chen', 'Sarah Miller', 'Mike Johnson', 'Emily Davis',
            'David Wilson', 'Rachel Torres', 'James Park', 'Lisa Wong'
        ]
    
    def generate_mock_schedule(self, patches):
        """
        Generate a complete mock schedule using Random Forest predictions
        """
        scheduled_patches = []
        used_times = set()
        
        # Sort patches by priority (descending)
        sorted_patches = sorted(patches, key=lambda p: -p.priority)
        
        for patch in sorted_patches:
            # Find optimal time using ML predictor
            best_time = self._find_best_time_with_ml(patch, used_times)
            
            if best_time:
                # Get ML classification
                classification = patch_classifier.predict(
                    patch, 
                    best_time['network_load'], 
                    4,  # Assume 4 crew available
                    best_time['hour']
                )
                
                # Assign random crew members
                num_crew = patch.min_crew
                assigned_crew = random.sample(self.crew_names, min(num_crew, len(self.crew_names)))
                
                scheduled_patch = {
                    'patch': patch.to_dict(),
                    'start_hour': best_time['hour'],
                    'end_hour': best_time['hour'] + patch.duration,
                    'day': best_time['day'],
                    'assigned_crew': assigned_crew,
                    'network_load': int(best_time['network_load']),
                    'score': best_time['score'],
                    'status': 'scheduled',
                    'classification': classification['patch_type'],
                    'confidence': classification['confidence']
                }
                
                scheduled_patches.append(scheduled_patch)
                
                # Mark time as used
                for i in range(int(patch.duration) + 1):
                    used_times.add((best_time['day'], (best_time['hour'] + i) % 24))
            else:
                # Couldn't schedule (rare with 168 hours available)
                scheduled_patches.append({
                    'patch': patch.to_dict(),
                    'status': 'unscheduled',
                    'reason': 'Could not find optimal time window'
                })
        
        return scheduled_patches
    
    def _find_best_time_with_ml(self, patch, used_times):
        """
        Use ML model to find best time for a patch
        """
        candidates = []
        
        # Check all days and hours
        for day_num, day in enumerate(self.days):
            for hour in range(24):
                # Skip if time is already used
                if (day, hour) in used_times:
                    continue
                
                # Check if patch duration fits
                duration_fits = True
                for i in range(int(patch.duration) + 1):
                    if (day, (hour + i) % 24) in used_times:
                        duration_fits = False
                        break
                
                if not duration_fits:
                    continue
                
                # Predict network load using Linear Regression
                network_load = network_load_predictor.predict(day_num, hour, 0)
                
                # Calculate score
                score = self._calculate_score(patch, hour, day_num, network_load)
                
                candidates.append({
                    'day': day,
                    'day_num': day_num,
                    'hour': hour,
                    'network_load': network_load,
                    'score': score
                })
        
        # Return best candidate
        if candidates:
            return max(candidates, key=lambda x: x['score'])
        return None
    
    def _calculate_score(self, patch, hour, day_num, network_load):
        """
        Calculate scheduling score (0-100)
        """
        score = 100
        
        # Network load factor (40 points max)
        if network_load < 20:
            load_score = 40
        elif network_load < 30:
            load_score = 30
        elif network_load < 40:
            load_score = 20
        else:
            load_score = 10
        
        # Time of day factor (20 points max)
        if 0 <= hour < 6:  # Night - ideal
            time_score = 20
        elif 6 <= hour < 9:  # Morning
            time_score = 15
        elif 9 <= hour < 17:  # Business hours - avoid
            time_score = 5
        elif 17 <= hour < 22:  # Evening
            time_score = 12
        else:  # Late night
            time_score = 18
        
        # Weekend bonus (10 points)
        weekend_score = 10 if day_num >= 5 else 0
        
        # Priority factor (15 points max)
        priority_score = (patch.priority / 5) * 15
        
        # Duration factor (15 points max) - shorter is better
        duration_score = max(0, 15 - (patch.duration * 3))
        
        total = load_score + time_score + weekend_score + priority_score + duration_score
        return round(min(100, max(0, total)), 2)


# Global instance
mock_scheduler = MockScheduler()

