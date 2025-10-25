# 🤖 AI Chatbot Setup Guide

## Overview
The Patch Scheduler now includes an AI-powered chatbot that provides intelligent recommendations based on your real-time network data, crew availability, and patch information.

## Features
- **Real-time Context**: AI knows your current network loads, patches, and crew
- **Smart Recommendations**: Get scheduling advice based on actual data
- **Natural Conversation**: Ask questions in plain English
- **Electrical Aesthetic**: Beautiful chat interface matching the app theme

---

## Setup Instructions

### Step 1: Install OpenAI Package

Run in your terminal:
```bash
cd Hackathon--Los--Pythones/BackENd
pip install openai
```

### Step 2: Get OpenAI API Key

1. Go to [https://platform.openai.com/](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy the API key (starts with `sk-...`)

### Step 3: Set API Key (Choose One Method)

#### **Option A: Environment Variable (Recommended)**

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

#### **Option B: Direct in Code**

Edit `BackENd/app.py` line 22:
```python
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', 'sk-your-actual-key-here'))
```

Replace `'sk-your-actual-key-here'` with your actual key.

⚠️ **Warning:** Don't commit your API key to Git!

### Step 4: Restart Backend

After setting the API key, restart your Flask server:
```bash
python app.py
```

---

## How to Use

1. **Click the floating robot button** (🤖) in the bottom-right corner
2. **Type your question** in the chat input
3. **Press Enter** or click the ⚡ button to send
4. **Get AI recommendations** based on your real data!

### Example Questions to Ask:

- "What's the best time to schedule the database patch?"
- "Which patches should I prioritize this week?"
- "Do I have enough crew for all pending patches?"
- "When is the network load lowest?"
- "Can you recommend a schedule for high-priority patches?"
- "What day has the best maintenance window?"

---

## How It Works

### Context Sent to AI:
The AI receives:
- Total patches pending
- High priority patch count
- Available crew members and their schedules
- Top 5 lowest network load hours
- Details of each patch (duration, priority, crew needs)
- Crew availability windows and skill levels

### AI Model:
- **Model:** GPT-3.5-turbo
- **Max Response:** 500 tokens
- **Temperature:** 0.7 (balanced creativity)

### Fallback Mode:
If OpenAI is unavailable, the chatbot will:
- Show helpful fallback messages
- Provide general best practices
- Still work without internet connection

---

## Troubleshooting

### "OpenAI not configured" Error
- Install openai: `pip install openai`
- Set your API key (see Step 3)
- Restart the backend server

### "Unable to connect to AI service"
- Check your internet connection
- Verify API key is correct
- Ensure you have API credits on OpenAI account
- Check OpenAI service status

### Chat Button Not Appearing
- Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
- Clear browser cache
- Check browser console for errors

### API Key Security
✅ **DO:**
- Use environment variables
- Keep API key secret
- Add `.env` to `.gitignore`

❌ **DON'T:**
- Commit API keys to Git
- Share your API key
- Use keys in frontend code

---

## Cost Information

### OpenAI Pricing (GPT-3.5-turbo):
- **Input:** ~$0.0015 per 1K tokens
- **Output:** ~$0.002 per 1K tokens

### Estimated Usage:
- Each conversation: ~300-800 tokens
- Cost per question: ~$0.001-0.002 (very cheap!)
- 1000 questions ≈ $1-2

**Free Tier:**
- New accounts get $5 free credits
- ~2,500-5,000 questions included

---

## Advanced Configuration

### Change AI Model

In `BackENd/app.py`, line 247:
```python
model="gpt-3.5-turbo",  # Fast and cheap
# model="gpt-4",        # More intelligent, more expensive
```

### Adjust Response Length

Line 253:
```python
max_tokens=500,  # Longer responses
```

### Modify AI Personality

Edit the `system_context` variable (line 228-244) to change how the AI responds.

---

## Integration with Real Data

To integrate with your actual systems:

1. **Replace sample data** in `BackENd/app.py`:
   - `generate_sample_network_loads()` → Connect to your monitoring system
   - `generate_sample_crew()` → Connect to your HR/scheduling system
   - `generate_sample_patches()` → Connect to your patch management system

2. **Add historical data**:
   ```python
   # Add to context
   "Historical Outages: ..."
   "Past Patch Success Rates: ..."
   ```

3. **Real-time updates**:
   - Cache system data
   - Refresh every N minutes
   - Include current system status

---

## Security Best Practices

1. **API Key Protection:**
   - Never commit to version control
   - Use environment variables
   - Rotate keys regularly

2. **Input Validation:**
   - Already implemented in backend
   - Prevents injection attacks
   - Limits message length

3. **Rate Limiting:**
   - Consider adding rate limits
   - Prevent API abuse
   - Monitor usage

---

## Feature Roadmap

Future enhancements:
- [ ] Conversation history persistence
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Suggested questions
- [ ] Export chat to PDF
- [ ] Integration with Slack/Teams
- [ ] Custom AI training on your data

---

⚡ **Enjoy your AI-powered patch scheduling assistant!** 🤖

*For support, contact Los Pythones team*

