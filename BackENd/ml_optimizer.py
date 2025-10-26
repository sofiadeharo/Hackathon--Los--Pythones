"""
ML-Powered Patch Optimizer
Combines all three ML models to provide comprehensive patch scheduling recommendations
"""

from network_load_predictor import network_load_predictor
from patch_classifier import patch_classifier
from ml_predictor import predictor

class MLOptimizer:
    def __init__(self):
        self.network_predictor = network_load_predictor
        self.patch_classifier_model = patch_classifier
        self.rf_predictor = predictor
    
    def calculate_patch_score(self, patch, hour, day_num, network_load, available_crew):
        """
        Calculate a comprehensive score for scheduling a patch at a specific time
        Score range: 0-100 (higher is better)
        """
        score = 100  # Start with perfect score
        
        # 1. Network Load Factor (40% weight)
        # Lower load = higher score
        if network_load < 20:
            load_score = 40
        elif network_load < 30:
            load_score = 30
        elif network_load < 40:
            load_score = 20
        elif network_load < 50:
            load_score = 10
        else:
            load_score = 0
        
        score = load_score
        
        # 2. Time of Day Factor (20% weight)
        if 0 <= hour < 6:  # Night - ideal
            time_score = 20
        elif 6 <= hour < 9:  # Morning - acceptable
            time_score = 15
        elif 9 <= hour < 17:  # Business hours - avoid
            time_score = 5
        elif 17 <= hour < 22:  # Evening - acceptable
            time_score = 12
        else:  # Late night - good
            time_score = 18
        
        score += time_score
        
        # 3. Crew Availability Factor (15% weight)
        crew_needed = patch.min_crew
        if available_crew >= crew_needed + 2:
            crew_score = 15  # Plenty of crew
        elif available_crew >= crew_needed + 1:
            crew_score = 12  # Extra crew available
        elif available_crew >= crew_needed:
            crew_score = 8   # Just enough
        else:
            crew_score = 0   # Not enough crew
        
        score += crew_score
        
        # 4. Patch Priority Factor (15% weight)
        # Higher priority should be scheduled sooner (during optimal times)
        priority_score = (patch.priority / 5) * 15
        score += priority_score
        
        # 5. Weekend Factor (10% weight)
        is_weekend = day_num >= 5
        if is_weekend:
            score += 10  # Weekends are better for maintenance
        
        return round(min(100, max(0, score)), 2)
    
    def find_optimal_hours_for_patch(self, patch, crew_available, top_n=5):
        """
        Find the best hours to schedule a specific patch using all ML models
        """
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        recommendations = []
        
        # Get predictions for entire week
        for day_num, day in enumerate(days):
            for hour in range(24):
                # Predict network load (Linear Regression)
                predicted_load = self.network_predictor.predict(day_num, hour, 0)
                
                # Calculate score
                score = self.calculate_patch_score(
                    patch, hour, day_num, predicted_load, crew_available
                )
                
                # Get patch classification at this time
                classification = self.patch_classifier_model.predict(
                    patch, predicted_load, crew_available, hour
                )
                
                recommendations.append({
                    'day': day,
                    'day_num': day_num,
                    'hour': hour,
                    'time_display': f"{day} {hour:02d}:00",
                    'predicted_load_kw': predicted_load,
                    'score': score,
                    'patch_type': classification['patch_type'],
                    'confidence': classification['confidence'],
                    'recommended_priority': classification['recommended_priority']
                })
        
        # Sort by score (descending)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:top_n]
    
    def recommend_crew_for_patch(self, patch, crew_list, hour, network_load):
        """
        Recommend the best crew members for a patch based on skills and availability
        """
        available_crew = [c for c in crew_list if hour in c.available_hours]
        
        # Sort by skill level (descending)
        available_crew.sort(key=lambda x: x.skill_level, reverse=True)
        
        # Get the required number of crew
        needed = patch.min_crew
        recommended = available_crew[:needed]
        
        # Calculate crew score
        if len(recommended) >= needed:
            avg_skill = sum(c.skill_level for c in recommended) / len(recommended)
            crew_score = round((avg_skill / 5) * 100, 2)
        else:
            crew_score = 0
        
        return {
            'recommended_crew': [
                {
                    'name': c.name,
                    'skill_level': c.skill_level,
                    'available_hours': len(c.available_hours)
                }
                for c in recommended
            ],
            'crew_score': crew_score,
            'crew_needed': needed,
            'crew_available': len(available_crew),
            'sufficient': len(recommended) >= needed
        }
    
    def get_comprehensive_recommendation(self, patch, crew_list, day=None, hour=None):
        """
        Get a comprehensive recommendation for a single patch
        If day/hour not provided, find optimal time automatically
        """
        crew_available = len(crew_list)
        
        # If no specific time provided, find optimal time
        if day is None or hour is None:
            optimal_times = self.find_optimal_hours_for_patch(patch, crew_available, top_n=5)
            best_time = optimal_times[0]
            day = best_time['day']
            hour = best_time['hour']
            day_num = best_time['day_num']
            predicted_load = best_time['predicted_load_kw']
            score = best_time['score']
        else:
            # Calculate for specific time
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_num = days.index(day) if day in days else 0
            predicted_load = self.network_predictor.predict(day_num, hour, 0)
            score = self.calculate_patch_score(patch, hour, day_num, predicted_load, crew_available)
        
        # Get patch classification
        classification = self.patch_classifier_model.predict(
            patch, predicted_load, crew_available, hour
        )
        
        # Get crew recommendations
        crew_rec = self.recommend_crew_for_patch(patch, crew_list, hour, predicted_load)
        
        # Find alternative optimal times
        all_optimal = self.find_optimal_hours_for_patch(patch, crew_available, top_n=5)
        
        return {
            'patch_id': patch.id,
            'patch_name': patch.name,
            'patch_priority': patch.priority,
            'patch_duration': patch.duration,
            'optimal_time': {
                'day': day,
                'hour': hour,
                'time_display': f"{day} {hour:02d}:00",
                'predicted_load_kw': predicted_load,
                'score': score
            },
            'ml_classification': {
                'type': classification['patch_type'],
                'confidence': classification['confidence'],
                'recommended_priority': classification['recommended_priority'],
                'reasoning': classification['reasoning']
            },
            'crew_recommendation': crew_rec,
            'alternative_times': all_optimal[1:],  # Skip first (it's the recommended one)
            'overall_score': round((score + crew_rec['crew_score']) / 2, 2)
        }
    
    def optimize_all_patches(self, patches, crew_list):
        """
        Optimize schedule for all patches using ML models
        Returns comprehensive recommendations for each patch
        """
        recommendations = []
        scheduled_times = {}  # Track which times are used
        
        for patch in patches:
            # Get optimal times for this patch
            optimal_times = self.find_optimal_hours_for_patch(patch, len(crew_list), top_n=10)
            
            # Find first time slot that's not already used
            selected_time = None
            for time_slot in optimal_times:
                time_key = f"{time_slot['day']}_{time_slot['hour']}"
                if time_key not in scheduled_times:
                    selected_time = time_slot
                    scheduled_times[time_key] = patch.id
                    break
            
            if selected_time:
                # Get comprehensive recommendation
                rec = self.get_comprehensive_recommendation(
                    patch, crew_list, 
                    day=selected_time['day'], 
                    hour=selected_time['hour']
                )
                recommendations.append(rec)
            else:
                # No available slot found (shouldn't happen with 168 hours)
                # Use the best slot anyway
                rec = self.get_comprehensive_recommendation(patch, crew_list)
                recommendations.append(rec)
        
        # Sort by overall score (descending)
        recommendations.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return {
            'total_patches': len(patches),
            'successfully_scheduled': len(recommendations),
            'recommendations': recommendations,
            'ml_models_used': [
                'Linear Regression (Network Load Prediction)',
                'Random Forest Classifier (Patch Classification)',
                'Random Forest Regressor (Pattern Analysis)'
            ]
        }
    
    def get_score_at_time(self, patch, crew_list, day, hour):
        """
        Get the score for scheduling a patch at a specific time
        """
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_num = days.index(day) if day in days else 0
        
        # Predict network load
        predicted_load = self.network_predictor.predict(day_num, hour, 0)
        
        # Calculate score
        score = self.calculate_patch_score(
            patch, hour, day_num, predicted_load, len(crew_list)
        )
        
        # Get classification
        classification = self.patch_classifier_model.predict(
            patch, predicted_load, len(crew_list), hour
        )
        
        # Get crew recommendation
        crew_rec = self.recommend_crew_for_patch(patch, crew_list, hour, predicted_load)
        
        return {
            'day': day,
            'hour': hour,
            'time_display': f"{day} {hour:02d}:00",
            'predicted_load_kw': predicted_load,
            'score': score,
            'patch_type': classification['patch_type'],
            'confidence': classification['confidence'],
            'crew_recommendation': crew_rec,
            'overall_score': round((score + crew_rec['crew_score']) / 2, 2),
            'recommendation': self._get_recommendation_text(score, classification['patch_type'])
        }
    
    def _get_recommendation_text(self, score, patch_type):
        """Generate recommendation text based on score and patch type"""
        if score >= 80:
            quality = "Excellent"
        elif score >= 60:
            quality = "Good"
        elif score >= 40:
            quality = "Fair"
        else:
            quality = "Poor"
        
        return f"{quality} time for {patch_type} patch (Score: {score}/100)"


# Global optimizer instance
ml_optimizer = MLOptimizer()

