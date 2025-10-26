# 🤖 AI Chatbot - Time Window Recommendations

## Overview

The Electro-call AI chatbot is now trained to provide **specific time window recommendations** using data from **3 ML models**.

---

## 🎯 What the Chatbot Can Do

### ✅ **Trained Capabilities:**

1. **Recommend Specific Time Windows**
   - Provides exact day and time (e.g., "Saturday, 02:00 - 04:00")
   - Shows network load prediction for that window
   - Includes optimization score (0-100)

2. **ML-Backed Recommendations**
   - Uses Linear Regression for load predictions
   - Uses Random Forest for patch classifications
   - Analyzes 168 hours across the week

3. **Patch-Specific Advice**
   - Customizes recommendations per patch
   - Considers priority, duration, and requirements
   - Provides alternative time slots

4. **Strategy Guidance**
   - Explains why certain times are better
   - Considers crew availability
   - Balances urgency vs. optimal conditions

---

## 💬 Example Questions to Ask

### **General Scheduling:**
```
❓ "When is the best time to patch the system?"

🤖 Response:
"Based on ML predictions, the best time windows are:

1. Saturday, 02:00 - 04:00
   • Network Load: 14.0 kW
   • Score: 95/100
   • Excellent window - Weekend night, minimal load

2. Sunday, 01:00 - 03:00
   • Network Load: 14.3 kW
   • Score: 93/100
   • Great alternative - Sunday early morning

3. Saturday, 23:00 - 01:00
   • Network Load: 16.8 kW
   • Score: 90/100
   • Good option - Late Saturday night

All three are weekend off-peak hours with predicted load under 20 kW."
```

### **Specific Patch:**
```
❓ "When should I schedule the Database Security Update?"

🤖 Response:
"For the Database Security Update (Priority 5/5, 2 hours):

ML Classification: Manual (82.7% confidence)

Recommended Windows:
1. Saturday, 02:00 - 04:00
   • Load: 14.0 kW, Score: 100/100
   • Perfect: Weekend + night + lowest predicted load
   • Crew: Alex Chen, Sarah Miller (both available)

2. Saturday, 05:00 - 07:00
   • Load: 17.1 kW, Score: 97/100
   • Excellent: Still weekend early morning
   • Lower crew competition

3. Friday, 23:00 - 01:00
   • Load: 18.5 kW, Score: 88/100
   • Good: Late night, entering weekend

The ML model classifies this as a Manual patch requiring careful crew coordination, so I recommend using Window 1 with your most skilled crew."
```

### **Multiple Patches:**
```
❓ "What's the optimal schedule for all my patches this week?"

🤖 Response:
"Here's the ML-optimized schedule for all 5 patches:

🔧 Database Security Update (Priority 5)
   • Saturday, 02:00 - 04:00 (Score: 100)
   • Load: 14.0 kW [Manual]

🔧 Core Network Firmware (Priority 5)
   • Saturday, 05:00 - 08:00 (Score: 97)
   • Load: 17.1 kW [Manual]

🔧 Application Server Update (Priority 4)
   • Sunday, 02:00 - 03:30 (Score: 95)
   • Load: 14.3 kW [Manual]

🔧 Web Server Patch (Priority 3)
   • Sunday, 22:00 - 23:00 (Score: 90)
   • Load: 16.5 kW [Manual]

🔧 Backup System Patch (Priority 2)
   • Monday, 03:00 - 05:00 (Score: 85)
   • Load: 22.1 kW [Automated]

All patches scheduled during off-peak hours with average score of 93/100."
```

### **Alternative Times:**
```
❓ "What if Saturday morning doesn't work? Give me alternatives."

🤖 Response:
"Alternative windows with similar quality:

Weekend Options:
• Sunday, 01:00 - 04:00 (Load: 14.3 kW, Score: 93/100)
• Saturday, 23:00 - 02:00 (Load: 16.8 kW, Score: 90/100)

Weeknight Options:
• Tuesday, 02:00 - 04:00 (Load: 19.2 kW, Score: 85/100)
• Wednesday, 01:00 - 03:00 (Load: 20.1 kW, Score: 82/100)

I recommend the Sunday option as it maintains weekend benefits with similar low load (14.3 kW vs 14.0 kW)."
```

### **Emergency Patches:**
```
❓ "I have an emergency security patch. When can I do it?"

🤖 Response:
"For emergency patches, ML recommends immediate scheduling regardless of network load.

Current Best Options (Next 6 Hours):
1. Now (if during off-peak)
2. In 2 hours (transitioning to lower load)
3. Wait until tonight 22:00 for optimal conditions

Emergency Classification: Immediate action required
Current Load: 35 kW (moderate)
Tonight's Predicted Load: 18 kW (low)

Recommendation: If truly critical, schedule immediately. If you can wait 5 hours until tonight, you'll get 50% lower network impact."
```

---

## 🧠 What Data the Chatbot Has

### **1. Optimal Time Windows:**
```
EXCELLENT WINDOWS (Load <20 kW):
✅ Saturday 00:00 - 13.96 kW
✅ Sunday 00:00 - 14.02 kW
✅ Saturday 01:00 - 14.33 kW

GOOD WINDOWS (Load 20-30 kW):
✔️ Monday 02:00 - 22.17 kW
✔️ Tuesday 03:00 - 23.45 kW
```

### **2. Patch-Specific Recommendations:**
```
For each patch, the chatbot knows:
- Top 3 optimal time windows
- Scores for each window
- Network load predictions
- ML classification
```

### **3. ML Classifications:**
```
Database Security Update: Manual (82.7% confidence)
Core Network Firmware: Manual (82.3% confidence)
Backup System Patch: Automated (86.4% confidence)
```

### **4. Strategy Tips:**
```
• Weekend nights (Sat/Sun 0-6am) = lowest load
• Avoid weekday business hours (Mon-Fri 9am-5pm)
• Emergency patches: Schedule ASAP
• Manual patches: Use optimal windows with skilled crew
• Automated patches: Any low-load window works
```

---

## 🎯 Best Practices

### **Ask Specific Questions:**
✅ "When should I schedule the database update?"  
✅ "What are the best times this weekend?"  
✅ "Give me 3 alternative windows for high-priority patches"

❌ "Tell me about patches"  
❌ "What do you think?"  
❌ "Help"

### **Request Multiple Options:**
"Give me the top 3 time windows for [patch name]"

### **Ask for Reasoning:**
"Why is Saturday better than Sunday?"

### **Compare Options:**
"Should I do this patch now or wait until tonight?"

---

## 🚀 How to Use

### **1. Open the App:**
```
http://localhost:8000
```

### **2. Click the Chat Button:**
- Purple floating button in bottom-right corner
- Chat icon

### **3. Type Your Question:**
```
Examples:
- "When is the best time for Database Security Update?"
- "Show me all optimal time windows this week"
- "What if I need to schedule an emergency patch?"
```

### **4. Review the Response:**
- Specific days and times
- Network load predictions
- Optimization scores
- Reasoning and alternatives

### **5. Ask Follow-ups:**
```
- "What about alternatives?"
- "Can you explain why that time is best?"
- "What about weekdays instead?"
```

---

## 📊 Technical Details

### **ML Models Used:**
1. **Linear Regression** (84.44% accuracy)
   - Predicts network load for any day/time
   - Features: day, hour, minute, weekend, business hours

2. **Random Forest Classifier** (100% training accuracy)
   - Classifies patches as Emergency/Manual/Automated
   - 22 engineered features

3. **Random Forest Regressor**
   - Analyzes network load patterns
   - Identifies feature importance

### **Context Provided to AI:**
- 168 hours of network load data
- 8 crew members with availability
- 5 pending patches with details
- Top 10 optimal time windows (ML-predicted)
- Top 3 windows per patch
- ML classifications for each patch
- Scheduling strategy tips

### **AI Model:**
- GPT-3.5-turbo
- Temperature: 0.7 (balanced creativity/accuracy)
- Max tokens: 800 (detailed responses)

---

## 💡 Example Conversation Flow

```
You: "When should I schedule patches this week?"

AI: "Based on ML predictions across 168 hours, here are the optimal windows:

BEST TIMES (Score 90-100):
• Saturday 02:00-04:00 (14.0 kW) - Perfect
• Sunday 01:00-03:00 (14.3 kW) - Excellent
• Saturday 23:00-01:00 (16.8 kW) - Great

All weekend off-peak hours with loads under 20 kW."

---

You: "Tell me more about Saturday 2am"

AI: "Saturday 02:00-04:00 is the #1 recommended window because:

✅ Weekend (minimal business impact)
✅ Night hours (natural low usage)
✅ Predicted load: 14.0 kW (lowest of week)
✅ Score: 100/100
✅ Crew available: 4 members (Alex, Sarah, James, Lisa)

This window is perfect for:
- Database Security Update (2h, Priority 5)
- Core Network Firmware (can start at 05:00)
- Any high-priority manual patches

Would you like me to suggest a schedule using this window?"

---

You: "Yes, suggest a schedule"

AI: "Here's an optimized schedule starting Saturday 02:00:

🔧 02:00-04:00: Database Security Update
   Crew: Alex Chen, Sarah Miller
   Load: 14.0 kW, Score: 100/100

🔧 05:00-08:00: Core Network Firmware  
   Crew: Mike Johnson, Emily Davis, David Wilson
   Load: 17.1 kW, Score: 97/100

🔧 Sunday 02:00-03:30: Application Server
   Crew: Alex Chen, Sarah Miller
   Load: 14.3 kW, Score: 95/100

All critical patches done in optimal windows with average score of 97/100!"
```

---

## 🎨 Visual Cues in Responses

The AI uses formatting to make responses clearer:

- **Windows:** "Saturday, 02:00 - 04:00"
- **Scores:** "Score: 95/100"
- **Load:** "Load: 14.0 kW"
- **Classifications:** "[Manual]" or "[Emergency]"
- **Bullets:** • for lists
- **Emojis:** ✅ ✔️ ⚠️ 🔧 for visual clarity

---

## ✨ Key Features

✅ **Specific Time Windows** - Not vague advice  
✅ **ML-Backed** - Real predictions, not guesses  
✅ **Alternative Options** - Always 2-3 backups  
✅ **Reasoning** - Explains why each window is good  
✅ **Patch-Specific** - Customized per patch  
✅ **Score-Based** - Quantified recommendations  
✅ **Strategy Tips** - General best practices  
✅ **Conversational** - Natural language Q&A  

---

**Try it now! Ask the chatbot: "When is the best time to patch the system?" 🚀**

