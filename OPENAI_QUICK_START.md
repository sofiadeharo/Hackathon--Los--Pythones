# ⚡ OpenAI Chatbot - Quick Start Guide

## 🎉 What's New

Your **Electro-call** chatbot is now powered by **OpenAI GPT-3.5-turbo** and trained with real-time data from your Supabase database!

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Get Your OpenAI API Key

1. Visit: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click **"Create new secret key"**
4. Copy your key (starts with `sk-...`)

💡 **New accounts get $5 free credits** (~2,500-5,000 questions!)

---

### Step 2: Set the API Key

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-your-key-here"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-your-key-here
```

**Mac/Linux:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

---

### Step 3: Restart the Backend

```bash
cd Hackathon--Los--Pythones/BackENd
python app.py
```

You should see:
```
OpenAI client initialized successfully ✅
```

---

## ✨ How to Use

1. **Open the app** in your browser: http://localhost:5000
2. **Click the robot button** 🤖 in the bottom-right corner
3. **Ask questions** like:
   - "What's the best time to schedule patches?"
   - "When is network load lowest?"
   - "Do I have enough crew for all patches?"
   - "Which patches should I prioritize?"

---

## 🔥 What Data the AI Sees

Every time you ask a question, the AI receives:

### Network Load Data
- **168 data points** (7 days × 24 hours)
- Measured in **kilowatts (kW)**
- Real-time from your Supabase `network_loads` table

### Crew Availability
- All crew members with names
- Available time slots
- Skill levels (1-5)
- From Supabase `crew_members` table

### Pending Patches
- Patch names and details
- Duration (hours)
- Priority (1-5)
- Minimum crew requirements
- From Supabase `patches` table + custom patches

---

## 💰 Cost

**Per Question:** ~$0.001-0.002 (less than a penny!)

**Monthly:**
- 500 questions: ~$0.50-1.00
- 5,000 questions: ~$5-10

**Very affordable for AI-powered recommendations!**

---

## 🛠️ Troubleshooting

### "OpenAI client not initialized"
→ Set your API key using Step 2 above
→ Restart the backend

### "Unable to connect to AI service"
→ Check your internet connection
→ Verify API key is correct (no extra spaces)
→ Ensure you have credits on your OpenAI account

### Chatbot button not appearing
→ Clear browser cache
→ Hard refresh (Ctrl+Shift+R)

---

## 📚 More Information

- **[CHATBOT_DATA_INTEGRATION.md](./CHATBOT_DATA_INTEGRATION.md)** - Detailed data integration guide
- **[AI_CHATBOT_SETUP.md](./AI_CHATBOT_SETUP.md)** - Complete setup documentation
- **[SUPABASE_SETUP.md](./SUPABASE_SETUP.md)** - Database configuration

---

## ⚠️ Important Notes

1. **Never commit your API key to Git!**
2. Always use environment variables
3. Monitor your API usage at: [https://platform.openai.com/usage](https://platform.openai.com/usage)
4. The chatbot uses real-time data - no need to retrain!

---

## ✅ Success Checklist

- [ ] Got OpenAI API key from platform.openai.com
- [ ] Set OPENAI_API_KEY environment variable
- [ ] Restarted backend (`python app.py`)
- [ ] Saw "OpenAI client initialized successfully" message
- [ ] Opened frontend in browser
- [ ] Clicked chatbot button (🤖)
- [ ] Asked a question and got a response!

---

**🎉 Enjoy your AI-powered patch scheduling assistant!** ⚡🤖

*Los Pythones Team* 🐍

