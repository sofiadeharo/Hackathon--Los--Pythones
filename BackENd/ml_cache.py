"""
ML Predictions Cache
Pre-calculates and caches ML predictions to speed up chatbot responses
"""

import time
from datetime import datetime, timedelta
from network_load_predictor import network_load_predictor
from patch_classifier import patch_classifier
from ml_optimizer import ml_optimizer

class MLCache:
    def __init__(self):
        self.cache = {}
        self.cache_time = None
        self.cache_duration = 300  # Cache for 5 minutes
    
    def is_cache_valid(self):
        """Check if cache is still valid"""
        if self.cache_time is None:
            return False
        elapsed = time.time() - self.cache_time
        return elapsed < self.cache_duration
    
    def get_cached_predictions(self, patches, crew, avg_load):
        """Get cached ML predictions or calculate if needed"""
        if self.is_cache_valid() and self.cache:
            return self.cache
        
        # Recalculate predictions
        print("🔄 Calculating ML predictions for chatbot...")
        start_time = time.time()
        
        predictions = {}
        
        # 1. Get optimal time windows (fast - only top 10)
        try:
            optimal_times = network_load_predictor.find_optimal_patch_times(duration_hours=2, top_n=10)
            
            # Group by quality
            predictions['excellent'] = [t for t in optimal_times if t['predicted_load_kw'] < 20][:3]
            predictions['good'] = [t for t in optimal_times if 20 <= t['predicted_load_kw'] < 30][:3]
            predictions['fair'] = [t for t in optimal_times if 30 <= t['predicted_load_kw'] < 40][:2]
        except Exception as e:
            print(f"Error getting optimal times: {e}")
            predictions['excellent'] = []
            predictions['good'] = []
            predictions['fair'] = []
        
        # 2. Get patch-specific windows (only top 3 patches)
        predictions['patch_windows'] = {}
        try:
            for patch in patches[:3]:  # Only top 3 to save time
                patch_optimal = ml_optimizer.find_optimal_hours_for_patch(patch, len(crew), top_n=3)
                predictions['patch_windows'][patch.name] = patch_optimal
        except Exception as e:
            print(f"Error getting patch windows: {e}")
        
        # 3. Get patch classifications (quick for all patches)
        predictions['classifications'] = {}
        try:
            for patch in patches[:5]:  # Top 5 patches
                classification = patch_classifier.predict(patch, avg_load, len(crew), hour=2)
                predictions['classifications'][patch.name] = {
                    'type': classification['patch_type'],
                    'confidence': classification['confidence'],
                    'reason': classification['reasoning'][0] if classification['reasoning'] else "Standard patch"
                }
        except Exception as e:
            print(f"Error classifying patches: {e}")
        
        # Cache the results
        self.cache = predictions
        self.cache_time = time.time()
        
        elapsed = time.time() - start_time
        print(f"✅ ML predictions cached in {elapsed:.2f}s")
        
        return predictions
    
    def clear_cache(self):
        """Clear the cache (call when patches change)"""
        self.cache = {}
        self.cache_time = None
        print("🗑️ ML cache cleared")


# Global cache instance
ml_cache = MLCache()

