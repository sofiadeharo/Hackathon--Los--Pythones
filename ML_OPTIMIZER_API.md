# 🤖 ML Optimizer API Documentation

Complete guide to the ML-powered patch optimization endpoints in Electro-call.

---

## Overview

The ML Optimizer combines **3 trained machine learning models** to provide comprehensive patch scheduling recommendations:

1. **Linear Regression** - Predicts network load (kW) for any time
2. **Random Forest Classifier** - Classifies patches (Emergency/Manual/Automated)
3. **Random Forest Regressor** - Analyzes network load patterns

---

## Scoring System

### Score Range: 0-100 (higher is better)

**Score Breakdown:**
- **40% - Network Load Factor**
  - <20 kW: 40 points (Excellent)
  - 20-30 kW: 30 points (Good)
  - 30-40 kW: 20 points (Fair)
  - 40-50 kW: 10 points (Poor)
  - >50 kW: 0 points (Avoid)

- **20% - Time of Day Factor**
  - 0-6 (Night): 20 points (Ideal)
  - 6-9 (Morning): 15 points (Acceptable)
  - 9-17 (Business Hours): 5 points (Avoid)
  - 17-22 (Evening): 12 points (Acceptable)
  - 22-24 (Late Night): 18 points (Good)

- **15% - Crew Availability Factor**
  - Crew ≥ needed + 2: 15 points (Plenty)
  - Crew = needed + 1: 12 points (Extra)
  - Crew = needed: 8 points (Just enough)
  - Crew < needed: 0 points (Insufficient)

- **15% - Patch Priority Factor**
  - Scaled by priority (priority/5 * 15)

- **10% - Weekend Factor**
  - Weekend: +10 points bonus

---

## API Endpoints

### 1. Optimize All Patches

Get comprehensive ML-powered recommendations for all patches.

**Endpoint:**
```
GET /api/ml-optimize-all
```

**Response:**
```json
{
  "success": true,
  "total_patches": 5,
  "successfully_scheduled": 5,
  "ml_models_used": [
    "Linear Regression (Network Load Prediction)",
    "Random Forest Classifier (Patch Classification)",
    "Random Forest Regressor (Pattern Analysis)"
  ],
  "recommendations": [
    {
      "patch_id": 1,
      "patch_name": "Database Security Update",
      "patch_priority": 5,
      "patch_duration": 2,
      "optimal_time": {
        "day": "Saturday",
        "hour": 0,
        "time_display": "Saturday 00:00",
        "predicted_load_kw": 13.96,
        "score": 100
      },
      "ml_classification": {
        "type": "Manual",
        "confidence": 82.7,
        "recommended_priority": 4,
        "reasoning": [
          "Moderate priority (5/5)",
          "Standard duration (2h)",
          "Network load (14.0 kW) is manageable",
          "Benefits from manual crew coordination"
        ]
      },
      "crew_recommendation": {
        "recommended_crew": [
          {
            "name": "John Doe",
            "skill_level": 5,
            "available_hours": 24
          }
        ],
        "crew_score": 100,
        "crew_needed": 2,
        "crew_available": 3,
        "sufficient": true
      },
      "alternative_times": [
        {
          "day": "Saturday",
          "hour": 1,
          "time_display": "Saturday 01:00",
          "predicted_load_kw": 14.33,
          "score": 100,
          "patch_type": "Manual",
          "confidence": 82.5
        }
      ],
      "overall_score": 95.0
    }
  ]
}
```

**Use Case:** Get a complete optimized schedule for all patches at once.

---

### 2. Optimize Single Patch

Get comprehensive recommendation for one specific patch.

**Endpoint:**
```
POST /api/ml-optimize-patch
```

**Request Body:**
```json
{
  "patch_id": 1,
  "day": "Monday",     // Optional - if omitted, finds optimal time
  "hour": 14           // Optional - if omitted, finds optimal time
}
```

**Response:** Same structure as single recommendation from `/ml-optimize-all`

**Use Cases:**
- Get recommendation for specific patch
- Check if a specific time is good for a patch
- Find alternative optimal times

---

### 3. Get Score at Specific Time

Calculate the score for scheduling a patch at a particular day/hour.

**Endpoint:**
```
POST /api/score-at-time
```

**Request Body:**
```json
{
  "patch_id": 1,
  "day": "Monday",
  "hour": 14
}
```

**Response:**
```json
{
  "success": true,
  "patch_id": 1,
  "patch_name": "Database Security Update",
  "day": "Monday",
  "hour": 14,
  "time_display": "Monday 14:00",
  "predicted_load_kw": 39.12,
  "score": 55.0,
  "patch_type": "Manual",
  "confidence": 81.3,
  "crew_recommendation": {
    "crew_needed": 2,
    "crew_available": 0,
    "crew_score": 0,
    "sufficient": false
  },
  "overall_score": 27.5,
  "recommendation": "Fair time for Manual patch (Score: 55.0/100)"
}
```

**Use Cases:**
- Compare scores across different times
- Validate user-selected scheduling times
- Show real-time score as user adjusts time selector

---

### 4. Find Optimal Hours for Patch

Get the top N best times to schedule a specific patch.

**Endpoint:**
```
POST /api/optimal-hours-for-patch
```

**Request Body:**
```json
{
  "patch_id": 1,
  "top_n": 5
}
```

**Response:**
```json
{
  "success": true,
  "patch_id": 1,
  "patch_name": "Database Security Update",
  "optimal_hours": [
    {
      "day": "Saturday",
      "day_num": 5,
      "hour": 0,
      "time_display": "Saturday 00:00",
      "predicted_load_kw": 13.96,
      "score": 100,
      "patch_type": "Manual",
      "confidence": 82.7,
      "recommended_priority": 4
    },
    {
      "day": "Saturday",
      "hour": 1,
      "time_display": "Saturday 01:00",
      "predicted_load_kw": 14.33,
      "score": 100,
      "patch_type": "Manual",
      "confidence": 82.5,
      "recommended_priority": 4
    }
  ]
}
```

**Use Cases:**
- Show users multiple good time options
- Let users choose from top recommended times
- Display in a calendar/time picker UI

---

### 5. Recommend Crew

Get crew recommendations for a patch at a specific time.

**Endpoint:**
```
POST /api/recommend-crew
```

**Request Body:**
```json
{
  "patch_id": 1,
  "hour": 2,
  "network_load": 35.0
}
```

**Response:**
```json
{
  "success": true,
  "patch_id": 1,
  "patch_name": "Database Security Update",
  "hour": 2,
  "recommended_crew": [
    {
      "name": "John Doe",
      "skill_level": 5,
      "available_hours": 24
    },
    {
      "name": "Jane Smith",
      "skill_level": 4,
      "available_hours": 20
    }
  ],
  "crew_score": 90.0,
  "crew_needed": 2,
  "crew_available": 3,
  "sufficient": true
}
```

**Use Cases:**
- Auto-assign crew to patches
- Show crew availability when scheduling
- Calculate crew score for scheduling decisions

---

## Integration Examples

### JavaScript/Frontend

```javascript
// 1. Optimize all patches
async function optimizeAllPatches() {
  const response = await fetch('http://localhost:8000/api/ml-optimize-all');
  const data = await response.json();
  
  data.recommendations.forEach(rec => {
    console.log(`${rec.patch_name}: ${rec.optimal_time.time_display}`);
    console.log(`Score: ${rec.overall_score}/100`);
    console.log(`Load: ${rec.optimal_time.predicted_load_kw} kW`);
  });
}

// 2. Get score at specific time
async function getScore(patchId, day, hour) {
  const response = await fetch('http://localhost:8000/api/score-at-time', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ patch_id: patchId, day, hour })
  });
  const data = await response.json();
  return data.score;
}

// 3. Find optimal times
async function findOptimalTimes(patchId) {
  const response = await fetch('http://localhost:8000/api/optimal-hours-for-patch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ patch_id: patchId, top_n: 5 })
  });
  const data = await response.json();
  return data.optimal_hours;
}
```

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 1. Optimize all patches
response = requests.get(f"{BASE_URL}/ml-optimize-all")
data = response.json()
for rec in data['recommendations']:
    print(f"{rec['patch_name']}: {rec['optimal_time']['time_display']}")
    print(f"Score: {rec['overall_score']}/100")

# 2. Get score at time
payload = {"patch_id": 1, "day": "Monday", "hour": 14}
response = requests.post(f"{BASE_URL}/score-at-time", json=payload)
data = response.json()
print(f"Score: {data['score']}/100")

# 3. Find optimal times
payload = {"patch_id": 1, "top_n": 5}
response = requests.post(f"{BASE_URL}/optimal-hours-for-patch", json=payload)
data = response.json()
for time in data['optimal_hours']:
    print(f"{time['time_display']}: {time['score']}/100")
```

---

## Interpretation Guide

### Scores

| Score Range | Interpretation | Action |
|-------------|---------------|--------|
| 90-100 | Excellent | Schedule immediately |
| 70-89 | Good | Recommended |
| 50-69 | Fair | Acceptable if necessary |
| 30-49 | Poor | Avoid if possible |
| 0-29 | Very Poor | Do not schedule |

### Patch Types

| Type | Meaning | Scheduling |
|------|---------|-----------|
| **Emergency** | High priority, urgent | Schedule ASAP, regardless of load |
| **Manual** | Moderate priority | Schedule during optimal windows with crew |
| **Automated** | Low priority | Schedule during low-load times, minimal crew |

### Network Load

| Load (kW) | Classification | Impact |
|-----------|---------------|--------|
| 0-20 | Low | Minimal impact, ideal for patches |
| 20-35 | Moderate | Some impact, acceptable |
| 35-50 | High | Significant impact, caution |
| 50+ | Very High | Avoid patching |

---

## Best Practices

1. **Always check score before scheduling**
   - Score <50 = reconsider the time

2. **Use alternative times**
   - If optimal time unavailable, check alternatives

3. **Consider crew availability**
   - Insufficient crew = failed patch

4. **Prioritize Emergency patches**
   - Schedule immediately even with lower scores

5. **Batch low-priority patches**
   - Automated patches can share time slots

6. **Weekend scheduling preferred**
   - Automatic +10 point bonus
   - Lower network load

7. **Avoid business hours (9-17)**
   - Score penalty
   - Higher network load

---

## Troubleshooting

### Low Scores for All Times
- **Cause:** High network load throughout week
- **Solution:** Check network load predictions, consider maintenance window

### No Crew Recommended
- **Cause:** No crew available at that hour
- **Solution:** Adjust crew schedules or select different time

### All Patches Same Score
- **Cause:** Similar priorities/durations
- **Solution:** Adjust patch priorities or durations

---

## Quick Reference

| What You Want | Endpoint | Method |
|---------------|----------|--------|
| Optimize everything | `/api/ml-optimize-all` | GET |
| Check specific time | `/api/score-at-time` | POST |
| Find best times | `/api/optimal-hours-for-patch` | POST |
| Get crew assignment | `/api/recommend-crew` | POST |
| Single patch optimization | `/api/ml-optimize-patch` | POST |

---

**Built with ❤️ using Scikit-learn ML models**

