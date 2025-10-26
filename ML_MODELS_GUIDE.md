# 🤖 Machine Learning Models Guide - Electro-call

This application uses **THREE trained ML models** to optimize patch scheduling and predict emergency status.

---

## 📊 Model 1: Random Forest Regressor (Network Load Pattern Analysis)

### Purpose
Analyzes historical network load patterns to predict future loads and identify optimal maintenance windows.

### Technical Details
- **Algorithm**: Random Forest Regressor
- **Estimators**: 100 decision trees
- **Features**: 4 (day_of_week, hour, is_weekend, is_business_hours)
- **Training**: Automatically trained on 168 data points (7 days × 24 hours)

### Feature Importance
```
is_business_hours: 77.4%  ← Most important!
day_of_week:       8.6%
hour:              8.5%
is_weekend:        5.5%
```

### What It Predicts
- Network load levels throughout the week
- Optimal maintenance windows
- Low-load time periods

### API Endpoint
```bash
GET /api/ml-stats
```

---

## 🚨 Model 2: Random Forest Classifier (Patch Emergency Classification)

### Purpose
Classifies patches as **Emergency**, **Manual**, or **Automated** based on 22 engineered features.

### Technical Details
- **Algorithm**: Random Forest Classifier
- **Estimators**: 1000 decision trees
- **Training Accuracy**: 100%
- **Features**: 22 engineered features
- **Training Data**: 1000 synthetic samples

### Key Features Used
1. **Base Features**:
   - `risk_indicator` (from priority)
   - `tasks_count`
   - `personnel_involved`
   - `average_load_MW`
   - `average_active_users`
   - `duration_minutes`
   - `hour`
   - `assigned_crew_id`

2. **Engineered Features**:
   - `load_per_task`
   - `users_per_personnel`
   - `tasks_per_personnel`
   - `load_per_personnel`
   - `load_per_minute`
   - `users_per_minute`
   - `is_night` (1 if hour < 6 or hour >= 18)
   - `hour_sin`, `hour_cos` (cyclic encoding)
   - `risk_load_ratio`
   - `risk_task_ratio`
   - `risk_personnel_ratio`
   - `efficiency_index`
   - `crew_task_density`

### Classification Logic
```python
Emergency:
  - High priority (≥4) AND short duration (≤1h)
  - High network load (>60 kW)
  - Requires immediate response

Manual:
  - Moderate priority (2-4)
  - Standard duration (1-3h)
  - Manageable network load
  - Benefits from crew coordination

Automated:
  - Low priority (1-2)
  - Low network load (<20 kW)
  - Off-peak hours
  - Can run with minimal supervision
```

### API Endpoints
```bash
# Classify a single patch
POST /api/classify-patch
{
  "patch_id": 1,
  "network_load": 40.0,
  "crew_available": 3,
  "hour": 2
}

# Classify all patches
GET /api/classify-all-patches
```

### Example Response
```json
{
  "patch_id": 1,
  "patch_name": "Database Security Update",
  "patch_priority": 5,
  "predicted_type": "Manual",
  "confidence": 82.6,
  "probabilities": {
    "Automated": 6.1,
    "Manual": 82.6,
    "Emergency": 11.3
  },
  "reasoning": [
    "Moderate priority (5/5)",
    "Standard duration (2h)",
    "Network load (40.6 kW) is manageable",
    "Benefits from manual crew coordination and planning"
  ],
  "recommended_priority": 4
}
```

---

## 📈 Model 3: Linear Regression (Precise Network Load Prediction)

### Purpose
Predicts exact network load (in kW) for any day and time using linear relationships between time features and load.

### Technical Details
- **Algorithm**: Linear Regression
- **R² Score**: 0.8444 (84.44% accuracy)
- **MAE**: 2.83 kW
- **RMSE**: 3.54 kW
- **Features**: 5 (day_num, hour, minute, is_weekend, is_business_hours)
- **Training Data**: 1000 samples with realistic time-of-day patterns

### Model Coefficients
```python
Intercept:        21.79 kW  ← Base load
is_business_hours: +12.08 kW  ← Biggest impact!
is_weekend:       -8.15 kW   ← Weekends are lower
hour:             +0.37 kW   ← Increases per hour
day_num:          +0.06 kW   ← Slight daily increase
minute:           +0.01 kW   ← Minimal minute effect
```

### Load Patterns Learned
```
Night (0-6):         70% of base load (low)
Morning (6-9):       90% of base load (ramp-up)
Business Hours (9-17): 130% of base load (HIGH)
Evening (17-22):     110% of base load (moderate)
Late Night (22-24):  80% of base load (low)

Weekends: 60% of weekday load
```

### API Endpoints
```bash
# Predict load for specific time
POST /api/predict-load
{
  "day": "Monday",
  "hour": 14,
  "minute": 30
}

# Get entire week predictions (168 hours)
GET /api/predict-week-load

# Find optimal patch times
GET /api/optimal-patch-times?duration=2&top_n=5
```

### Example Response - Optimal Times
```json
{
  "duration_hours": 2,
  "optimal_times": [
    {
      "day": "Saturday",
      "hour": 0,
      "predicted_load_kw": 13.96,
      "time_display": "Saturday 00:00",
      "recommendation": "Low risk - Night (ideal for patches)"
    },
    {
      "day": "Sunday",
      "hour": 0,
      "predicted_load_kw": 14.02,
      "time_display": "Sunday 00:00",
      "recommendation": "Low risk - Night (ideal for patches)"
    }
  ]
}
```

---

## 🔗 How Models Work Together

### In the Scheduler
1. **Linear Regression** predicts network load for each hour
2. **Random Forest Regressor** analyzes patterns and validates predictions
3. **Random Forest Classifier** determines patch emergency status
4. Scheduler combines all insights to create optimal schedule

### In the AI Chatbot
The OpenAI chatbot receives context from all three models:
```
ML-Predicted Optimal Patch Times (Linear Regression):
  1. Saturday 00:00 - 13.96 kW (Low risk - Night, ideal)
  2. Sunday 00:00 - 14.02 kW (Low risk - Night, ideal)

ML-Predicted Patch Classifications (Random Forest):
  - Database Security Update: Manual (82.6% confidence)
  - Web Server Patch: Manual (55.6% confidence)
  - Backup System Patch: Automated (86.4% confidence)
```

This allows the chatbot to provide **data-driven, ML-backed recommendations**!

---

## 📊 View All Model Stats

```bash
GET /api/all-ml-models
```

Returns comprehensive statistics for all three models:
- Training status
- Accuracy metrics
- Feature importance
- Coefficients
- Sample predictions

---

## 🎯 Best Practices

### When to Use Each Model

1. **Use Linear Regression** when you need:
   - Precise load predictions for specific times
   - Optimal patch scheduling windows
   - Week-long load forecasts

2. **Use Random Forest Classifier** when you need:
   - Patch priority recommendations
   - Emergency status classification
   - Risk assessment with confidence scores

3. **Use Random Forest Regressor** when you need:
   - Pattern analysis
   - Feature importance insights
   - Validation of Linear Regression predictions

### Recommended Workflow

1. **Predict optimal times** (Linear Regression)
   ```bash
   GET /api/optimal-patch-times
   ```

2. **Classify patches** (Random Forest Classifier)
   ```bash
   GET /api/classify-all-patches
   ```

3. **Schedule based on both**:
   - Emergency patches → Immediate scheduling
   - Manual patches → Optimal low-load windows
   - Automated patches → Any low-load time

4. **Ask the AI chatbot** for recommendations:
   ```
   "What's the best time to schedule the database update?"
   ```

---

## 🚀 Future Enhancements

### Potential Improvements
1. **Online Learning**: Update models with actual patch outcomes
2. **Ensemble Methods**: Combine predictions from multiple models
3. **Deep Learning**: LSTM for time-series predictions
4. **Real-time Adaptation**: Adjust to unexpected network spikes

### Adding Your Own Data
Replace synthetic training data with real network logs:

```python
# In network_load_predictor.py
df = pd.read_csv('your_real_network_data.csv')
network_load_predictor.train(df)

# In patch_classifier.py  
df = pd.read_csv('your_real_patch_data.csv')
patch_classifier.train_from_csv(df)
```

---

## 📖 References

- **Scikit-learn**: https://scikit-learn.org/
- **Random Forest**: https://en.wikipedia.org/wiki/Random_forest
- **Linear Regression**: https://en.wikipedia.org/wiki/Linear_regression
- **Feature Engineering**: https://en.wikipedia.org/wiki/Feature_engineering

---

## ❓ Troubleshooting

### Model Not Training
```python
# Check if data is loaded
print(f"Training data size: {len(training_data)}")

# Verify features are correct
print(f"Feature names: {model.feature_names}")
```

### Low Accuracy
- Increase n_estimators (Random Forest)
- Add more training data
- Engineer better features
- Tune hyperparameters

### Slow Predictions
- Reduce n_estimators
- Use simpler models for real-time predictions
- Cache common predictions

---

**Built with ❤️ using Scikit-learn, Flask, and OpenAI**

