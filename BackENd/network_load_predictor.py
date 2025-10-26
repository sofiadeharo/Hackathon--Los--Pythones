"""
Network Load Predictor using Linear Regression
Predicts network load (kW) based on day and time
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class NetworkLoadPredictor:
    def __init__(self):
        self.model = LinearRegression()
        self.is_trained = False
        self.feature_names = ['day_num', 'hour', 'minute', 'is_weekend', 'is_business_hours']
        self.accuracy = 0
        self.r2_score = 0
        self.mae = 0
        self.rmse = 0
        
    def generate_synthetic_training_data(self, n_samples=1000):
        """Generate synthetic network load training data"""
        np.random.seed(42)
        
        # Generate time-series data for a week
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = list(range(24))
        minutes = [0, 15, 30, 45]
        
        data_rows = []
        
        for day in days:
            for hour in hours:
                for minute in minutes:
                    # Base load pattern
                    base_load = 30  # kW
                    
                    # Time-of-day pattern
                    if 0 <= hour < 6:  # Night (low load)
                        time_factor = 0.7 + np.random.uniform(-0.1, 0.1)
                    elif 6 <= hour < 9:  # Morning ramp-up
                        time_factor = 0.9 + np.random.uniform(-0.1, 0.1)
                    elif 9 <= hour < 17:  # Business hours (high load)
                        time_factor = 1.3 + np.random.uniform(-0.1, 0.1)
                    elif 17 <= hour < 22:  # Evening (moderate load)
                        time_factor = 1.1 + np.random.uniform(-0.1, 0.1)
                    else:  # Late evening
                        time_factor = 0.8 + np.random.uniform(-0.1, 0.1)
                    
                    # Day-of-week pattern
                    if day in ['Saturday', 'Sunday']:
                        day_factor = 0.6 + np.random.uniform(-0.1, 0.1)
                    else:
                        day_factor = 1.0
                    
                    # Calculate load
                    load_kw = base_load * time_factor * day_factor
                    load_kw = max(5, load_kw)  # Minimum 5 kW
                    
                    data_rows.append({
                        'day': day,
                        'time': f"{hour:02d}:{minute:02d}",
                        'load_kw': round(load_kw, 2)
                    })
        
        # Create DataFrame
        df = pd.DataFrame(data_rows)
        
        # Add some random samples to reach n_samples
        if len(df) < n_samples:
            extra_samples = n_samples - len(df)
            extra_rows = []
            for _ in range(extra_samples):
                day = np.random.choice(days)
                hour = np.random.randint(0, 24)
                minute = np.random.choice(minutes)
                
                # Similar logic as above
                base_load = 30
                if 0 <= hour < 6:
                    time_factor = 0.7 + np.random.uniform(-0.1, 0.1)
                elif 6 <= hour < 9:
                    time_factor = 0.9 + np.random.uniform(-0.1, 0.1)
                elif 9 <= hour < 17:
                    time_factor = 1.3 + np.random.uniform(-0.1, 0.1)
                elif 17 <= hour < 22:
                    time_factor = 1.1 + np.random.uniform(-0.1, 0.1)
                else:
                    time_factor = 0.8 + np.random.uniform(-0.1, 0.1)
                
                if day in ['Saturday', 'Sunday']:
                    day_factor = 0.6 + np.random.uniform(-0.1, 0.1)
                else:
                    day_factor = 1.0
                
                load_kw = base_load * time_factor * day_factor
                load_kw = max(5, load_kw)
                
                extra_rows.append({
                    'day': day,
                    'time': f"{hour:02d}:{minute:02d}",
                    'load_kw': round(load_kw, 2)
                })
            
            df = pd.concat([df, pd.DataFrame(extra_rows)], ignore_index=True)
        
        return df
    
    def preprocess_data(self, df):
        """Preprocess the data for training"""
        # Create a copy
        df_processed = df.copy()
        
        # Process 'day' column - convert to numeric (0=Monday, 6=Sunday)
        day_mapping = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        
        # Handle both formats: "day_Monday" and "Monday"
        if df_processed['day'].str.contains('_').any():
            df_processed['day'] = df_processed['day'].str[4:]  # Remove "day_" prefix
        
        df_processed['day_num'] = df_processed['day'].map(day_mapping)
        
        # Process 'time' column - extract hour and minute
        df_processed['time'] = df_processed['time'].str.strip().str.replace('.', ':')
        time_split = df_processed['time'].str.split(':', expand=True)
        df_processed['hour'] = time_split[0].astype(float)
        df_processed['minute'] = time_split[1].astype(float)
        
        # Add engineered features
        df_processed['is_weekend'] = (df_processed['day_num'] >= 5).astype(int)
        df_processed['is_business_hours'] = (
            (df_processed['hour'] >= 9) & (df_processed['hour'] < 17) & 
            (df_processed['day_num'] < 5)
        ).astype(int)
        
        return df_processed
    
    def train(self, df=None, n_samples=1000):
        """Train the Linear Regression model"""
        print("Training Network Load Linear Regression model...")
        
        # Generate or use provided data
        if df is None:
            df = self.generate_synthetic_training_data(n_samples)
        
        # Preprocess
        df_processed = self.preprocess_data(df)
        
        # Prepare features and target
        X = df_processed[self.feature_names]
        y = df_processed['load_kw']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=1234
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Calculate metrics
        y_pred = self.model.predict(X_test)
        self.r2_score = r2_score(y_test, y_pred)
        self.mae = mean_absolute_error(y_test, y_pred)
        self.rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        self.accuracy = self.r2_score * 100  # Convert R² to percentage
        
        print(f"Network Load Predictor trained successfully!")
        print(f"R² Score: {self.r2_score:.4f} ({self.accuracy:.2f}%)")
        print(f"MAE: {self.mae:.2f} kW")
        print(f"RMSE: {self.rmse:.2f} kW")
        
        return self.accuracy
    
    def predict(self, day, hour, minute=0):
        """
        Predict network load for a specific day and time
        
        Args:
            day: Day of week (0=Monday, 6=Sunday) or day name
            hour: Hour of day (0-23)
            minute: Minute (0-59)
        
        Returns:
            Predicted load in kW
        """
        if not self.is_trained:
            self.train()
        
        # Convert day name to number if needed
        if isinstance(day, str):
            day_mapping = {
                'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                'Friday': 4, 'Saturday': 5, 'Sunday': 6
            }
            day_num = day_mapping.get(day, 0)
        else:
            day_num = day
        
        # Create features
        is_weekend = 1 if day_num >= 5 else 0
        is_business_hours = 1 if (9 <= hour < 17 and day_num < 5) else 0
        
        X = np.array([[day_num, hour, minute, is_weekend, is_business_hours]])
        
        # Predict
        prediction = self.model.predict(X)[0]
        
        return max(5, round(prediction, 2))  # Minimum 5 kW
    
    def predict_week(self):
        """Predict network load for an entire week (168 hours)"""
        predictions = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day_idx, day in enumerate(days):
            for hour in range(24):
                load = self.predict(day_idx, hour, 0)
                predictions.append({
                    'day': day,
                    'day_num': day_idx,
                    'hour': hour,
                    'load_kw': load
                })
        
        return predictions
    
    def find_optimal_patch_times(self, duration_hours=2, top_n=5):
        """Find the best times to schedule patches based on lowest predicted load"""
        week_predictions = self.predict_week()
        
        # Sort by load (ascending) to find lowest load times
        sorted_predictions = sorted(week_predictions, key=lambda x: x['load_kw'])
        
        # Get top N optimal times
        optimal_times = []
        for pred in sorted_predictions[:top_n]:
            optimal_times.append({
                'day': pred['day'],
                'hour': pred['hour'],
                'predicted_load_kw': pred['load_kw'],
                'time_display': f"{pred['day']} {pred['hour']:02d}:00",
                'recommendation': self._get_recommendation(pred['load_kw'], pred['hour'])
            })
        
        return optimal_times
    
    def _get_recommendation(self, load, hour):
        """Generate recommendation based on load and time"""
        if load < 20:
            risk = "Low"
        elif load < 35:
            risk = "Moderate"
        else:
            risk = "High"
        
        if 0 <= hour < 6:
            time_desc = "Night (ideal for patches)"
        elif 6 <= hour < 9:
            time_desc = "Morning (moderate risk)"
        elif 9 <= hour < 17:
            time_desc = "Business hours (avoid if possible)"
        else:
            time_desc = "Evening (acceptable)"
        
        return f"{risk} risk - {time_desc}"
    
    def get_model_stats(self):
        """Return model statistics"""
        if not self.is_trained:
            return {'trained': False}
        
        return {
            'trained': True,
            'model_type': 'Linear Regression',
            'r2_score': round(self.r2_score, 4),
            'accuracy_percent': round(self.accuracy, 2),
            'mae_kw': round(self.mae, 2),
            'rmse_kw': round(self.rmse, 2),
            'feature_names': self.feature_names,
            'coefficients': {
                name: round(coef, 4) 
                for name, coef in zip(self.feature_names, self.model.coef_)
            },
            'intercept': round(self.model.intercept_, 4)
        }


# Global predictor instance
network_load_predictor = NetworkLoadPredictor()

