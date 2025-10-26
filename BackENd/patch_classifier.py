"""
Patch Emergency Status and Priority Classifier
Uses Random Forest to predict patch type: Emergency, Manual, or Automated
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class PatchClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=1000, random_state=0)
        self.is_trained = False
        self.feature_names = [
            'risk_indicator', 'tasks_count', 'personnel_involved',
            'average_load_MW', 'average_active_users', 'duration_minutes',
            'hour', 'assigned_crew_id', 'load_per_task', 'users_per_personnel',
            'tasks_per_personnel', 'load_per_personnel', 'load_per_minute',
            'users_per_minute', 'is_night', 'hour_sin', 'hour_cos',
            'risk_load_ratio', 'risk_task_ratio', 'risk_personnel_ratio',
            'efficiency_index', 'crew_task_density'
        ]
        
        # Label mapping
        self.label_map = {
            0: 'Automated',
            1: 'Manual',
            2: 'Emergency'
        }
        
        self.reverse_label_map = {
            'Automated': 0,
            'Manual': 1,
            'Emergency': 2
        }
    
    def generate_synthetic_training_data(self, n_samples=1000):
        """Generate synthetic training data based on realistic patterns"""
        np.random.seed(0)
        
        data = {
            'risk_indicator': np.random.randint(1, 6, n_samples),
            'tasks_count': np.random.randint(1, 21, n_samples),
            'personnel_involved': np.random.randint(1, 11, n_samples),
            'average_load_MW': np.random.normal(45, 20, n_samples).clip(5, 85),
            'average_active_users': np.random.normal(150, 50, n_samples).clip(10, 300),
            'duration_minutes': np.random.randint(15, 241, n_samples),
            'hour': np.random.randint(0, 24, n_samples),
            'assigned_crew_id': np.random.randint(1, 6, n_samples)
        }
        
        # Generate patch_type based on risk_indicator and duration (logical bias)
        conditions = [
            (data['risk_indicator'] >= 4) & (data['duration_minutes'] <= 60),
            (data['risk_indicator'] == 3) | ((data['risk_indicator'] >= 4) & (data['duration_minutes'] > 60)),
            (data['risk_indicator'] <= 2)
        ]
        choices = [2, 1, 0]  # Emergency, Manual, Automated
        data['patch_type'] = np.select(conditions, choices, default=1)
        
        # Add engineered features
        data['load_per_task'] = data['average_load_MW'] / np.maximum(data['tasks_count'], 1)
        data['users_per_personnel'] = data['average_active_users'] / np.maximum(data['personnel_involved'], 1)
        data['tasks_per_personnel'] = data['tasks_count'] / np.maximum(data['personnel_involved'], 1)
        data['load_per_personnel'] = data['average_load_MW'] / np.maximum(data['personnel_involved'], 1)
        data['load_per_minute'] = data['average_load_MW'] / np.maximum(data['duration_minutes'], 1)
        data['users_per_minute'] = data['average_active_users'] / np.maximum(data['duration_minutes'], 1)
        data['is_night'] = np.where((data['hour'] < 6) | (data['hour'] >= 18), 1, 0)
        data['hour_sin'] = np.sin(2 * np.pi * data['hour'] / 24)
        data['hour_cos'] = np.cos(2 * np.pi * data['hour'] / 24)
        data['risk_load_ratio'] = data['risk_indicator'] / np.maximum(data['average_load_MW'], 1)
        data['risk_task_ratio'] = data['risk_indicator'] / np.maximum(data['tasks_count'], 1)
        data['risk_personnel_ratio'] = data['risk_indicator'] / np.maximum(data['personnel_involved'], 1)
        data['efficiency_index'] = (
            (data['tasks_count'] / np.maximum(data['duration_minutes'], 1)) *
            (data['average_load_MW'] / np.maximum(data['average_active_users'], 1))
        )
        data['crew_task_density'] = data['tasks_count'] / np.maximum(data['assigned_crew_id'], 1)
        
        # Clean up invalid values
        for key in data:
            data[key] = np.nan_to_num(data[key], nan=0.0, posinf=0.0, neginf=0.0)
        
        return data
    
    def train(self, n_samples=1000):
        """Train the patch classifier with synthetic data"""
        print("Training Patch Emergency Classifier...")
        
        # Generate synthetic training data
        data = self.generate_synthetic_training_data(n_samples)
        
        # Prepare features and labels
        X = np.column_stack([data[feature] for feature in self.feature_names])
        y = data['patch_type']
        
        # Train model
        self.model.fit(X, y)
        self.is_trained = True
        
        # Calculate accuracy on training data (for monitoring)
        accuracy = self.model.score(X, y) * 100
        print(f"Patch Classifier trained successfully!")
        print(f"Training accuracy: {accuracy:.2f}%")
        
        return accuracy
    
    def extract_features(self, patch, network_load, crew_available, hour):
        """Extract features from patch, network load, and crew data"""
        # Base features
        risk_indicator = patch.priority  # Use priority as risk indicator
        tasks_count = max(int(patch.duration * 2), 1)  # Estimate tasks from duration
        personnel_involved = patch.min_crew
        average_load_MW = network_load
        average_active_users = max(int(network_load * 3), 10)  # Estimate users from load
        duration_minutes = int(patch.duration * 60)
        assigned_crew_id = min(crew_available, 5)
        
        # Engineered features
        load_per_task = average_load_MW / max(tasks_count, 1)
        users_per_personnel = average_active_users / max(personnel_involved, 1)
        tasks_per_personnel = tasks_count / max(personnel_involved, 1)
        load_per_personnel = average_load_MW / max(personnel_involved, 1)
        load_per_minute = average_load_MW / max(duration_minutes, 1)
        users_per_minute = average_active_users / max(duration_minutes, 1)
        is_night = 1 if (hour < 6 or hour >= 18) else 0
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        risk_load_ratio = risk_indicator / max(average_load_MW, 1)
        risk_task_ratio = risk_indicator / max(tasks_count, 1)
        risk_personnel_ratio = risk_indicator / max(personnel_involved, 1)
        efficiency_index = (tasks_count / max(duration_minutes, 1)) * (average_load_MW / max(average_active_users, 1))
        crew_task_density = tasks_count / max(assigned_crew_id, 1)
        
        # Return feature vector
        features = [
            risk_indicator, tasks_count, personnel_involved, average_load_MW,
            average_active_users, duration_minutes, hour, assigned_crew_id,
            load_per_task, users_per_personnel, tasks_per_personnel,
            load_per_personnel, load_per_minute, users_per_minute,
            is_night, hour_sin, hour_cos, risk_load_ratio,
            risk_task_ratio, risk_personnel_ratio, efficiency_index,
            crew_task_density
        ]
        
        return np.array(features).reshape(1, -1)
    
    def predict(self, patch, network_load, crew_available, hour):
        """
        Predict patch type (Emergency, Manual, or Automated)
        
        Args:
            patch: Patch object with priority, duration, min_crew
            network_load: Current network load in kW (converted to MW internally)
            crew_available: Number of available crew members
            hour: Hour of the day (0-23)
        
        Returns:
            dict with prediction, confidence, and reasoning
        """
        if not self.is_trained:
            self.train()
        
        # Convert kW to MW for model
        network_load_mw = network_load / 1000
        
        # Extract features
        X = self.extract_features(patch, network_load_mw, crew_available, hour)
        
        # Make prediction
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Get label
        predicted_label = self.label_map[prediction]
        confidence = probabilities[prediction] * 100
        
        # Generate reasoning
        reasoning = self._generate_reasoning(patch, network_load, crew_available, hour, predicted_label)
        
        return {
            'patch_type': predicted_label,
            'confidence': round(float(confidence), 2),
            'probabilities': {
                'Automated': round(float(probabilities[0]) * 100, 2),
                'Manual': round(float(probabilities[1]) * 100, 2),
                'Emergency': round(float(probabilities[2]) * 100, 2)
            },
            'reasoning': reasoning,
            'recommended_priority': int(prediction) + 3  # Convert to priority scale (3-5)
        }
    
    def _generate_reasoning(self, patch, network_load, crew_available, hour, prediction):
        """Generate human-readable reasoning for the prediction"""
        reasons = []
        
        if prediction == 'Emergency':
            if patch.priority >= 4:
                reasons.append(f"High priority level ({patch.priority}/5)")
            if patch.duration <= 1:
                reasons.append(f"Short duration ({patch.duration}h) suitable for emergency")
            if network_load > 60:
                reasons.append(f"High network load ({network_load:.1f} kW) requires immediate attention")
            reasons.append("Requires immediate crew response and minimal planning")
        
        elif prediction == 'Manual':
            reasons.append(f"Moderate priority ({patch.priority}/5)")
            reasons.append(f"Standard duration ({patch.duration}h)")
            reasons.append(f"Network load ({network_load:.1f} kW) is manageable")
            reasons.append("Benefits from manual crew coordination and planning")
        
        else:  # Automated
            reasons.append(f"Low priority ({patch.priority}/5)")
            reasons.append(f"Low network load ({network_load:.1f} kW)")
            if hour < 6 or hour >= 18:
                reasons.append("Off-peak hours ideal for automation")
            reasons.append("Can be safely automated with minimal supervision")
        
        return reasons
    
    def get_model_stats(self):
        """Return model statistics"""
        if not self.is_trained:
            return {'trained': False}
        
        return {
            'trained': True,
            'model_type': 'Random Forest Classifier',
            'n_estimators': self.model.n_estimators,
            'n_features': len(self.feature_names),
            'classes': list(self.label_map.values()),
            'feature_names': self.feature_names[:10]  # First 10 for brevity
        }


# Global classifier instance
patch_classifier = PatchClassifier()

