"""
Machine Learning Model for Network Load Prediction and Schedule Optimization
Uses scikit-learn regression models to predict optimal patch windows
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
import json

class NetworkLoadPredictor:
    """Predicts network load patterns and recommends optimal patch schedules"""
    
    def __init__(self):
        self.load_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.feature_names = ['day_of_week', 'hour', 'is_weekend', 'is_business_hours']
        
    def prepare_features(self, day_of_week, hour):
        """
        Prepare features for prediction
        day_of_week: 0=Monday, 6=Sunday
        hour: 0-23
        """
        is_weekend = 1 if day_of_week >= 5 else 0
        is_business_hours = 1 if 9 <= hour <= 17 else 0
        
        return np.array([[day_of_week, hour, is_weekend, is_business_hours]])
    
    def train(self, network_loads):
        """
        Train the model on historical network load data
        network_loads: list of NetworkLoad objects
        """
        if len(network_loads) == 0:
            return False
        
        # Prepare training data
        X = []
        y = []
        
        for load in network_loads:
            features = self.prepare_features(load.day_number, load.hour)
            X.append(features[0])
            y.append(load.load_kilowatts)
        
        X = np.array(X)
        y = np.array(y)
        
        # Train the model
        self.load_model.fit(X, y)
        self.is_trained = True
        
        return True
    
    def predict_load(self, day_of_week, hour):
        """
        Predict network load for a specific day and hour
        Returns predicted load in kW
        """
        if not self.is_trained:
            return None
        
        features = self.prepare_features(day_of_week, hour)
        predicted_load = self.load_model.predict(features)[0]
        
        return round(predicted_load, 2)
    
    def find_optimal_windows(self, duration_hours, network_loads):
        """
        Find the best time windows for patching based on predicted loads
        duration_hours: how long the patch will take
        Returns: list of optimal windows with scores
        """
        windows = []
        
        # Check all possible windows across the week
        for day in range(7):
            for hour in range(24 - int(duration_hours) + 1):
                # Calculate average load for this window
                total_load = 0
                for h in range(int(duration_hours)):
                    predicted = self.predict_load(day, hour + h)
                    if predicted is not None:
                        total_load += predicted
                
                avg_load = total_load / duration_hours
                
                # Score: lower load = better (invert for ranking)
                score = 100 - (avg_load / 90 * 100)  # Normalize to 0-100
                
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                windows.append({
                    'day': day_names[day],
                    'day_number': day,
                    'start_hour': hour,
                    'end_hour': hour + duration_hours,
                    'avg_load_kw': round(avg_load, 2),
                    'score': round(score, 2)
                })
        
        # Sort by score (best first)
        windows.sort(key=lambda x: x['score'], reverse=True)
        
        return windows[:10]  # Return top 10
    
    def get_recommendations(self, patches, crew, network_loads):
        """
        Generate AI-like recommendations based on ML predictions
        """
        recommendations = []
        
        # Overall load analysis
        if self.is_trained:
            recommendations.append("📊 **Network Load Analysis:**")
            
            # Find lowest load periods
            lowest_loads = []
            for day in range(7):
                for hour in range(24):
                    load = self.predict_load(day, hour)
                    if load is not None:
                        lowest_loads.append({
                            'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][day],
                            'hour': hour,
                            'load': load
                        })
            
            lowest_loads.sort(key=lambda x: x['load'])
            top_5 = lowest_loads[:5]
            
            recommendations.append(f"Best maintenance windows (lowest predicted load):")
            for item in top_5:
                recommendations.append(f"  • {item['day']} {item['hour']}:00 - Predicted {item['load']:.1f} kW")
        
        # Patch-specific recommendations
        if patches:
            recommendations.append("\n🔧 **Patch Recommendations:**")
            high_priority = [p for p in patches if p.priority >= 4]
            
            if high_priority:
                recommendations.append(f"You have {len(high_priority)} high-priority patches that should be scheduled first:")
                for patch in high_priority[:3]:
                    windows = self.find_optimal_windows(patch.duration, network_loads)
                    if windows:
                        best = windows[0]
                        recommendations.append(f"  • {patch.name}: Best window is {best['day']} {best['start_hour']}:00 ({best['avg_load_kw']} kW avg)")
        
        # Crew availability insights
        if crew:
            recommendations.append("\n👥 **Crew Availability:**")
            total_hours = sum(sum(end - start for start, end in member.available_hours) for member in crew)
            recommendations.append(f"Total crew availability: {total_hours} hours across {len(crew)} members")
            
            # Check if enough crew for patches
            if patches:
                total_patch_hours = sum(p.duration for p in patches)
                if total_hours >= total_patch_hours * 1.5:
                    recommendations.append("✅ You have sufficient crew capacity for all patches")
                else:
                    recommendations.append("⚠️ Consider scheduling some patches in parallel or extending the maintenance window")
        
        # Strategic advice
        recommendations.append("\n💡 **Strategic Advice:**")
        recommendations.append("• Weekend nights have the lowest predicted network load")
        recommendations.append("• Schedule critical patches during 2-6 AM for minimal user impact")
        recommendations.append("• Group similar patches together to optimize crew utilization")
        
        return "\n".join(recommendations)
    
    def get_model_stats(self):
        """Get statistics about the trained model"""
        if not self.is_trained:
            return {"trained": False}
        
        # Get feature importance
        feature_importance = dict(zip(self.feature_names, self.load_model.feature_importances_))
        
        return {
            "trained": True,
            "model_type": "Random Forest Regressor",
            "n_estimators": self.load_model.n_estimators,
            "feature_importance": {k: round(float(v), 4) for k, v in feature_importance.items()}
        }

# Global predictor instance
predictor = NetworkLoadPredictor()

