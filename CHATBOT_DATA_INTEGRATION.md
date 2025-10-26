# 🤖 Chatbot Data Integration Guide

## Overview

The **Electro-call AI Chatbot** is powered by **OpenAI GPT-3.5-turbo** and is trained with **real-time data** from your Supabase database every time you ask a question. This ensures the AI always has the most up-to-date information about your system.

---

## Data Sources

### 1. Network Load Data (in Kilowatts)

**Source:** `network_loads` table in Supabase

**Data Fetched:**
- **168 data points** (7 days × 24 hours)
- Day of week (Monday through Sunday)
- Day number (0-6, where 0 = Monday)
- Hour (0-23)
- Load in kilowatts (measured as whole numbers)

**Example Data:**
```
Monday at 3:00 AM - 15.2 kW (Low - ideal for patching)
Monday at 2:00 PM - 72.5 kW (High - avoid patching)
Saturday at 1:00 AM - 8.3 kW (Very Low - excellent for patching)
```

**How the AI Uses This:**
- Identifies the **top 5 lowest load hours** across the week
- Calculates the **average load** to understand typical patterns
- Recommends maintenance windows during low-load periods
- Warns against patching during high-load hours

---

### 2. Crew Availability Data

**Source:** `crew_members` table in Supabase

**Data Fetched:**
- Crew member names
- Available time slots (array of [start_hour, end_hour] pairs)
- Skill levels (1-5 rating)

**Example Data:**
```
Alex Chen
- Skill Level: 5/5 (Expert)
- Available: 0:00-8:00, 20:00-24:00 (night shifts)

Sarah Miller
- Skill Level: 4/5 (Advanced)
- Available: 6:00-14:00, 22:00-24:00 (morning + late night)
```

**How the AI Uses This:**
- Matches crew availability with low network load windows
- Considers skill levels for high-priority patches
- Ensures minimum crew requirements are met
- Optimizes crew assignment based on expertise

---

### 3. Patch Data

**Source:** `patches` table in Supabase + custom user-created patches

**Data Fetched:**
- Patch ID and name
- Duration (in hours)
- Priority level (1-5, where 5 = critical)
- Minimum crew required

**Example Data:**
```
Database Security Update
- Duration: 2 hours
- Priority: 5/5 (Critical)
- Minimum Crew: 2 people

Web Server Patch
- Duration: 1 hour
- Priority: 3/5 (Medium)
- Minimum Crew: 1 person
```

**How the AI Uses This:**
- Prioritizes high-priority patches
- Ensures sufficient time windows for patch duration
- Verifies crew availability matches minimum requirements
- Suggests scheduling order based on priority + duration

---

## Real-Time Context Building

### Every Chat Query Triggers:

1. **Data Fetch** (from Supabase)
   - Latest network load predictions
   - Current crew availability
   - All pending patches (including user-added ones)

2. **Data Processing**
   - Calculate average network load
   - Sort hours by load (lowest to highest)
   - Count total crew hours available
   - Identify high-priority patches

3. **Context Generation**
   - Build a comprehensive prompt for OpenAI
   - Include all relevant statistics
   - Format data for AI understanding

4. **AI Query**
   - Send user question + context to OpenAI
   - Receive intelligent recommendation
   - Return formatted response to user

---

## Example AI Context Prompt

Here's what the AI sees when you ask a question:

```
You are an AI assistant for the Electro-call patch scheduling system. 
You have access to real-time data:

**Network Load Data (Weekly - measured in kilowatts):**
- Average load across week: 42.35 kW
- Total data points: 168 (7 days × 24 hours)
- Lowest load hours:
  - Saturday at 3:00 - 8.2 kW
  - Sunday at 2:00 - 9.1 kW
  - Saturday at 4:00 - 9.8 kW
  - Saturday at 1:00 - 10.5 kW
  - Sunday at 3:00 - 11.2 kW

**Crew Availability:**
  - Alex Chen (Skill: 5, Available: 2 time slots)
  - Sarah Miller (Skill: 4, Available: 2 time slots)
  - Mike Johnson (Skill: 5, Available: 1 time slot)
  - Emily Davis (Skill: 3, Available: 2 time slots)
  - David Wilson (Skill: 4, Available: 2 time slots)
Total crew members: 5

**Pending Patches:**
  - Database Security Update (Duration: 2h, Priority: 5/5, Min Crew: 2)
  - Web Server Patch (Duration: 1h, Priority: 3/5, Min Crew: 1)
  - Core Network Firmware (Duration: 3h, Priority: 5/5, Min Crew: 3)
  - Application Server Update (Duration: 1.5h, Priority: 4/5, Min Crew: 2)
  - Backup System Patch (Duration: 2h, Priority: 2/5, Min Crew: 1)
Total patches: 5

Your role is to:
1. Analyze network load patterns to recommend optimal maintenance windows
2. Consider crew availability and skill levels for patch assignments
3. Prioritize patches based on their priority level and duration
4. Provide clear, actionable scheduling recommendations
5. Explain your reasoning based on the data

Always base your recommendations on minimizing network load impact 
and ensuring proper crew availability.
```

Then your question: **"What's the best time to schedule the database patch?"**

---

## Sample Chatbot Responses

### Question: "What's the best time to schedule the database patch?"

**AI Response:**
> Based on the current network load data, I recommend scheduling the Database Security Update patch on **Saturday between 2:00 AM - 4:00 AM** for the following reasons:
> 
> 1. **Network Load:** This window shows the lowest network activity (8.2-9.8 kW), minimizing impact on users
> 2. **Duration Match:** The 2-hour patch fits perfectly in this low-load period
> 3. **Crew Availability:** Alex Chen (Skill: 5) and Sarah Miller (Skill: 4) are both available during these hours, exceeding the minimum crew requirement of 2
> 4. **Priority:** As a critical (5/5) security patch, scheduling it during the absolute lowest load is essential
>
> **Backup Window:** Sunday 2:00 AM - 4:00 AM offers similar conditions if Saturday is unavailable.

### Question: "Do I have enough crew for all patches?"

**AI Response:**
> Yes, you have adequate crew coverage for all pending patches. Here's the breakdown:
>
> **Current Resources:**
> - 5 crew members available
> - 2 experts (Skill Level 5)
> - 2 advanced (Skill Level 4)
> - 1 intermediate (Skill Level 3)
>
> **Patch Requirements:**
> - Total crew needed across all patches: 9 person-slots
> - Your available crew hours: 20+ person-hours
>
> **Recommendation:**
> - Assign high-skill crew (Alex, Mike) to critical patches (Database Security, Core Network)
> - Medium-skill crew can handle the Web Server and Application Server patches
> - Emily can manage the low-priority Backup System patch
>
> You have sufficient resources, but schedule strategically to avoid overlap.

### Question: "When is network load lowest?"

**AI Response:**
> The network load is consistently lowest during **early morning hours on weekends**:
>
> **Top 5 Lowest Load Windows:**
> 1. **Saturday 3:00 AM** - 8.2 kW ⭐ Best overall
> 2. **Sunday 2:00 AM** - 9.1 kW
> 3. **Saturday 4:00 AM** - 9.8 kW
> 4. **Saturday 1:00 AM** - 10.5 kW
> 5. **Sunday 3:00 AM** - 11.2 kW
>
> **Pattern Analysis:**
> - Weekday nights (Mon-Fri 2-5 AM): 15-25 kW
> - Weekend nights: 8-12 kW (30-40% lower!)
> - Weekday business hours (9 AM-5 PM): 45-85 kW
>
> **Recommendation:** Schedule all critical patches during weekend early morning hours (1-5 AM) for minimal user impact.

---

## Data Update Frequency

### Real-Time (Every Query):
- ✅ Network load data
- ✅ Crew availability
- ✅ Pending patches
- ✅ Custom user-created patches

### On Supabase Update:
The chatbot will automatically see new data when you:
- Add new patches to the database
- Update crew schedules
- Modify network load predictions
- Change patch priorities

**No manual refresh needed!** The AI always uses the latest data.

---

## Data Flow Diagram

```
User asks question
       ↓
[Backend receives query]
       ↓
Fetch from Supabase:
  ├─ network_loads table → 168 load points
  ├─ crew_members table → All crew data
  └─ patches table → All patches
       ↓
Process & aggregate data:
  ├─ Calculate averages
  ├─ Find lowest loads
  └─ Build context string
       ↓
[Send to OpenAI API]
  ├─ System prompt (with all data)
  └─ User question
       ↓
[OpenAI processes with context]
       ↓
[Return intelligent answer]
       ↓
Display to user in chat
```

---

## Training vs. Context

### Important Distinction:

**The chatbot is NOT "trained" in the traditional ML sense.**

Instead, it uses **contextual prompting**:
- Base Model: GPT-3.5-turbo (pre-trained by OpenAI)
- Your Data: Sent as **context** with every question
- Result: AI "sees" your data and responds accordingly

**Advantages:**
- ✅ Always uses real-time data
- ✅ No model retraining needed
- ✅ Instant updates when data changes
- ✅ Works with any data structure

**How It Works:**
1. Your question: "What's the best patch time?"
2. Backend grabs all current data from Supabase
3. Formats data into a prompt
4. Sends: Prompt + Your Question → OpenAI
5. OpenAI responds based on the data context
6. You get a data-driven answer!

---

## Customization Options

### Modify AI Behavior

**In `BackENd/app.py`, line 276-299**, you can customize the system prompt:

```python
context = f"""You are an AI assistant for the Electro-call patch scheduling system.

[YOUR CUSTOM INSTRUCTIONS HERE]

Your role is to:
1. [Custom role 1]
2. [Custom role 2]
...
"""
```

### Adjust AI Parameters

**Line 304-312:**
```python
response = openai_client.chat.completions.create(
    model="gpt-3.5-turbo",  # or "gpt-4" for smarter responses
    temperature=0.7,         # 0.0 = focused, 1.0 = creative
    max_tokens=500           # response length
)
```

---

## Privacy & Security

### Data Sent to OpenAI:
- ✅ Network load statistics (aggregated)
- ✅ Crew names and availability
- ✅ Patch names and details
- ✅ User questions

### Data NOT Sent:
- ❌ Raw database credentials
- ❌ Supabase API keys
- ❌ System passwords
- ❌ User authentication info

### Best Practices:
1. **Don't include sensitive data** in patch names
2. **Use generic crew names** if privacy is a concern
3. **Monitor API usage** to prevent abuse
4. **Set rate limits** for production use

---

## Cost Estimation

### Per Query:
- **Input tokens:** ~500-800 (your data context)
- **Output tokens:** ~200-500 (AI response)
- **Cost:** ~$0.001-0.002 per question

### Monthly Usage (Example):
- 500 questions/month → ~$0.50-1.00/month
- 5,000 questions/month → ~$5-10/month

**Very affordable for real-time AI recommendations!**

---

## Troubleshooting

### "AI responses don't match my data"
→ Check that your Supabase tables are populated correctly
→ Verify API keys are set properly
→ Restart the backend after data changes

### "AI is giving generic answers"
→ Ensure OPENAI_API_KEY is set
→ Check that data is being fetched (look at backend logs)
→ Verify Supabase connection is working

### "Responses are too short/long"
→ Adjust `max_tokens` in `app.py` (line 311)
→ 500 tokens ≈ 375 words (default)
→ Increase for more detailed responses

---

## Future Enhancements

Potential improvements:
- [ ] **Conversation Memory:** Remember previous questions in the same session
- [ ] **Historical Analysis:** Include past patch success/failure data
- [ ] **Outage Predictions:** Integrate outage history for risk assessment
- [ ] **Multi-Model Support:** Allow switching between GPT-3.5 and GPT-4
- [ ] **Custom Training:** Fine-tune a model on your specific data patterns
- [ ] **Voice Interface:** Add speech-to-text for hands-free operation

---

## Summary

✅ **Real-Time Data:** Always uses latest Supabase data
✅ **Comprehensive Context:** Network loads, crew, and patches
✅ **Intelligent Recommendations:** AI analyzes all factors
✅ **Data-Driven Decisions:** Based on actual kW measurements
✅ **Flexible & Adaptable:** Updates automatically with your data

**The chatbot is your AI scheduling assistant, trained with YOUR specific network data, crew availability, and patch priorities!** ⚡🤖

---

*For more information, see:*
- [AI_CHATBOT_SETUP.md](./AI_CHATBOT_SETUP.md) - Setup instructions
- [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) - Database configuration
- [README.md](./README.md) - General documentation

**Los Pythones Team** 🐍⚡

