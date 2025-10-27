# 📊 How Scores Are Calculated (Rosy's Version)

## Overview

The Electro-call scheduler uses a **simplified 3-factor scoring system** to determine the optimal time for patches. Scores range from **0-100**, where higher is better.

---

## 🎯 Score Components (Simple & Direct)

Each scheduling time slot receives a score based on **3 key factors**:

### **1. Network Load at That Hour (40 points max) - Most Important!**

The network load **at the specific hour** determines the base score.

**Lower kW = Higher Score**

| Network Load (kW) | Points | Grade |
|-------------------|--------|-------|
| < 20 kW | 40 | ⭐⭐⭐ Excellent |
| 20-30 kW | 30 | ⭐⭐ Good |
| 30-40 kW | 20 | ⭐ Fair |
| 40-50 kW | 10 | ⚠️ Poor |
| > 50 kW | 5 | ❌ Very Poor |

**Why it matters:**
- Lower load = less system impact
- Uses actual load at that specific hour
- Minimizes risk of service disruption

**Example:**
```
Saturday 2am: 15 kW → 40 points ✅
Monday 2pm: 55 kW → 5 points ❌
```

---

### **2. Crew Available (30 points max)**

The number of available crew members at that hour affects the score.

**More Crew = Higher Score**

| Crew Available | Points | Status |
|----------------|--------|--------|
| 2× needed or more | 30 | ⭐⭐⭐ Plenty of crew |
| Needed + 2 | 25 | ⭐⭐ Good availability |
| Needed + 1 | 20 | ⭐ Extra crew available |
| Exactly needed | 15 | ⚠️ Just enough |
| Less than needed | 0 | ❌ Cannot schedule |

**Why it matters:**
- More crew = better flexibility
- Extra crew = backup if issues arise
- Just enough = risky if someone unavailable

**Example:**
```
Patch needs 2 crew:
- 5 crew available: 30 points ✅
- 2 crew available: 15 points ⚠️
- 1 crew available: 0 points ❌ (cannot schedule)
```

---

### **3. Patch Priority (30 points max)**

Higher priority patches get higher scores to ensure they get optimal time slots.

**Higher Priority = Higher Score**

| Priority | Points | Type |
|----------|--------|------|
| 5/5 | 30 | 🚨 Critical |
| 4/5 | 24 | ⚠️ High |
| 3/5 | 18 | 📋 Medium |
| 2/5 | 12 | 📝 Low |
| 1/5 | 6 | 💤 Very Low |

**Formula:** `(priority / 5) × 30`

**Why it matters:**
- Critical patches get best time slots
- Lower priority accepts sub-optimal times
- Fair distribution based on urgency

**Example:**
```
Database Security (Priority 5): 30 points ✅
Backup System (Priority 2): 12 points
UI Update (Priority 1): 6 points
```

---

## 📊 Score Calculation Examples

### **Example 1: Perfect Score (100/100)**

**Scenario:** Critical Database Patch on Saturday at 2:00 AM

```
Patch Details:
- Priority: 5/5 (Critical)
- Duration: 2 hours
- Required Crew: 2

Time Slot: Saturday, 02:00
- Network Load: 15 kW (at that hour)
- Crew Available: 5 members

Score Breakdown:
✅ Network Load (15 kW):     40 points (< 20 kW)
✅ Crew Available (5/2):     30 points (2× needed)
✅ Priority (5/5):           30 points (critical)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TOTAL SCORE:            100/100 ⭐⭐⭐
```

**Recommendation:** Perfect conditions! Schedule immediately.

---

### **Example 2: Excellent Score (95/100)**

**Scenario:** High Priority Server Update on Sunday at 11:00 PM

```
Patch Details:
- Priority: 5/5 (Critical)
- Duration: 1.5 hours
- Required Crew: 3

Time Slot: Sunday, 23:00
- Network Load: 18 kW (at that hour)
- Crew Available: 4 members

Score Breakdown:
✅ Network Load (18 kW):     40 points (< 20 kW)
✅ Crew Available (4/3):     25 points (needed + 1)
✅ Priority (5/5):           30 points (critical)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TOTAL SCORE:             95/100 ⭐⭐⭐
```

**Recommendation:** Excellent time window! Highly recommended.

---

### **Example 3: Good Score (70/100)**

**Scenario:** Medium Priority App Update on Friday at 8:00 PM

```
Patch Details:
- Priority: 3/5 (Medium)
- Duration: 1 hour
- Required Crew: 2

Time Slot: Friday, 20:00
- Network Load: 32 kW (at that hour)
- Crew Available: 4 members

Score Breakdown:
⭐ Network Load (32 kW):     20 points (30-40 kW)
✅ Crew Available (4/2):     30 points (2× needed)
⭐ Priority (3/5):           18 points (medium)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TOTAL SCORE:             68/100 ⭐⭐
```

**Recommendation:** Good time window, acceptable for medium priority.

---

### **Example 4: Fair Score (52/100)**

**Scenario:** Low Priority Backup Patch on Tuesday at 6:00 PM

```
Patch Details:
- Priority: 2/5 (Low)
- Duration: 2 hours
- Required Crew: 1

Time Slot: Tuesday, 18:00
- Network Load: 45 kW (at that hour)
- Crew Available: 2 members

Score Breakdown:
⚠️ Network Load (45 kW):     10 points (40-50 kW)
✅ Crew Available (2/1):     30 points (2× needed)
⚠️ Priority (2/5):           12 points (low)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TOTAL SCORE:             52/100 ⚠️
```

**Recommendation:** Fair for low priority patch, consider better window.

---

### **Example 5: Poor Score (35/100)**

**Scenario:** Critical Patch on Monday at 2:00 PM

```
Patch Details:
- Priority: 5/5 (Critical)
- Duration: 3 hours
- Required Crew: 3

Time Slot: Monday, 14:00
- Network Load: 58 kW (at that hour)
- Crew Available: 3 members (exactly needed)

Score Breakdown:
❌ Network Load (58 kW):      5 points (> 50 kW)
⚠️ Crew Available (3/3):     15 points (just enough)
✅ Priority (5/5):           30 points (critical)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TOTAL SCORE:             50/100 ❌
```

**Recommendation:** Poor time window, find better alternative.

---

## 🎯 Score Interpretation

### **Score Ranges:**

| Score | Grade | Recommendation |
|-------|-------|----------------|
| 90-100 | ⭐⭐⭐ Excellent | **Schedule immediately** - Perfect conditions |
| 75-89 | ⭐⭐ Good | **Highly recommended** - Great time window |
| 60-74 | ⭐ Fair | **Acceptable** - Reasonable choice |
| 40-59 | ⚠️ Poor | **Not ideal** - Consider alternatives |
| 0-39 | ❌ Very Poor | **Avoid** - High risk |

---

## 🧮 Quick Score Calculator

### **Simple Formula:**

```python
score = (
    network_load_points +    # 5-40 points (40% weight)
    crew_available_points +  # 0-30 points (30% weight)
    priority_points          # 6-30 points (30% weight)
)

# Network Load Points:
if kw < 20:  → 40 points
elif kw < 30: → 30 points
elif kw < 40: → 20 points
elif kw < 50: → 10 points
else: → 5 points

# Crew Available Points:
if crew >= needed × 2: → 30 points
elif crew >= needed + 2: → 25 points
elif crew >= needed + 1: → 20 points
elif crew >= needed: → 15 points
else: → 0 points

# Priority Points:
(priority / 5) × 30
```

---

## 💡 Optimization Tips

### **To Get Higher Scores:**

1. **Target Low Network Load Times**
   - Look for hours with <20 kW
   - Automatic 40 points

2. **Ensure Plenty of Crew**
   - Aim for 2× the required crew
   - Gets you 30 points

3. **Prioritize Critical Patches**
   - Priority 5 = 30 points
   - Priority 1 = 6 points

4. **Quick Rule of Thumb:**
   - Low load + plenty of crew + high priority = 95-100 points ✅
   - Moderate load + enough crew + medium priority = 60-75 points ⚠️
   - High load + minimal crew + low priority = 20-40 points ❌

---

## 📈 Real Score Distribution

Based on typical weekly patterns:

```
Excellent (90-100):  ~10%  - Weekend nights, low load, plenty crew
Good (75-89):        ~15%  - Weekend/night hours, good conditions
Fair (60-74):        ~25%  - Evening hours, moderate conditions
Poor (40-59):        ~30%  - Weekday evenings, higher load
Very Poor (0-39):    ~20%  - Business hours, high load
```

**Sweet Spot:** Weekend nights with <20 kW load = Consistent 90+ scores

---

## 📊 Comparison Table

### **How Each Factor Contributes:**

| Scenario | Load (kW) | Load Pts | Crew | Crew Pts | Priority | Pri Pts | Total |
|----------|-----------|----------|------|----------|----------|---------|-------|
| Perfect | 15 | 40 | 6/2 | 30 | 5 | 30 | **100** ⭐⭐⭐ |
| Excellent | 18 | 40 | 4/3 | 25 | 5 | 30 | **95** ⭐⭐⭐ |
| Good | 25 | 30 | 5/2 | 30 | 4 | 24 | **84** ⭐⭐ |
| Fair | 35 | 20 | 3/2 | 30 | 3 | 18 | **68** ⭐ |
| Poor | 48 | 10 | 2/2 | 15 | 2 | 12 | **37** ❌ |

---

## ✅ Summary

**Scoring is based on 3 simple factors:**

1. **Network Load (40 pts)** - Lower kW at that hour = higher score
2. **Crew Available (30 pts)** - More crew available = higher score
3. **Priority (30 pts)** - Higher priority = higher score

**Higher scores mean:**
- ✅ Lower system risk
- ✅ Minimal user impact
- ✅ Better success probability
- ✅ Safer maintenance window

**The algorithm prioritizes:**
- 🎯 90+ scores when possible
- ⚠️ 70+ minimum for critical patches
- 📊 Highest score for each patch

---

**Simple, transparent, and effective scheduling! 📊**
