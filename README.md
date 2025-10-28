# ⚡ ELECTRO-CALL

**AI-Powered System Maintenance Optimization Platform**

Electro-call is an intelligent patch scheduling application that uses Machine Learning to predict optimal maintenance windows based on network load patterns, crew availability, and patch priorities.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.2.5-green.svg)
![scikit--learn](https://img.shields.io/badge/scikit--learn-1.0.2-orange.svg)


---

## 🌟 Features

### 📊 **Network Load Visualization**
- Weekly network load monitoring (168 hours of data)
- Interactive day-by-day slider for detailed analysis
- Real-time visualization in kilowatts (kW)
- Color-coded bars for quick identification of optimal patching windows

### 🤖 **Machine Learning Intelligence**
- **Random Forest Regression** model for load prediction
- Offline, privacy-friendly predictions (no external API needed)
- Trained on historical network patterns
- Predicts optimal maintenance windows with confidence scores

### 🔧 **Smart Patch Management**
- Create, view, and edit patch details
- Priority-based scheduling (1-5 scale)
- Duration and crew requirement tracking
- Urgent patch flagging



### 💬 **AI Chatbot Assistant**
- Natural language queries about optimal patch times
- Network load predictions for any day/hour
- Crew availability analysis
- Model performance insights

### 🎨 **Electrical Aesthetic UI**
- Neon-glowing interface with circuit-board animations
- Smooth transitions and hover effects
- Responsive design for all screen sizes
- Dark theme optimized for 24/7 operations centers

---

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/sofiadeharo/Hackathon--Los--Pythones.git
cd Hackathon--Los--Pythones
```

2. **Install Python dependencies**
```bash
cd BackENd
pip install -r requirements.txt
```

3. **Start the backend server**
```bash
python app.py
```
The Flask API will start on `http://localhost:5000`

4. **Start the frontend server** (in a new terminal)
```bash
cd ../frontend
python -m http.server 8000
```
The web app will be available at `http://localhost:8000`

5. **Open your browser**
Navigate to `http://localhost:8000` and start optimizing! ⚡

---

## 📁 Project Structure

```
Hackathon--Los--Pythones/
├── BackENd/
│   ├── app.py              # Flask REST API
│   ├── models.py           # Data models (NetworkLoad, Patch, Crew)
│   ├── scheduler.py        # Optimization algorithm
│   ├── ml_predictor.py     # Machine Learning model
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main UI structure
│   ├── styles.css          # Electrical aesthetic styling
│   └── app.js              # Frontend logic & API calls
├── AI_CHATBOT_SETUP.md     # AI setup documentation
├── ML_MODEL_INFO.md        # ML model details
└── README.md               # This file
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/network-load` | GET | Weekly network load data (168 hours) |
| `/api/patches` | GET | List all patches |
| `/api/patches` | POST | Create new patch |
| `/api/crew` | GET | Crew availability data |
| `/api/optimize-schedule` | POST | Generate optimal schedule |
| `/api/stats` | GET | System statistics |
| `/api/best-hours` | GET | Top 10 lowest-load hours |
| `/api/chat` | POST | AI chatbot interaction |
| `/api/ml-stats` | GET | ML model statistics |

---


### Training Features:
- Hour of day (0-23)
- Day of week (0-6, Monday-Sunday)
- Weekend indicator (binary)
- Business hours indicator (binary)

### Model Performance:
- Trained on 168 data points (1 week of hourly data)
- Automatically retrains on server startup
- Feature importance analysis available via API

**See [ML_MODEL_INFO.md](ML_MODEL_INFO.md) for detailed documentation**

---

## 🎮 Usage Guide

### Creating a Patch
1. Click the **"+ Add Patch"** button in the Pending Patches panel
2. Fill in patch details:
   - Name (e.g., "Database Security Update")
   - Duration in hours
   - Priority (1-5, where 5 is critical)
   - Minimum crew required
   - Optional notes
3. Click **"Save Details"**

### Optimizing the Schedule
1. Review your pending patches and crew availability
2. Click **"⚡ OPTIMIZE SCHEDULE ⚡"**
3. The AI will calculate the best time for each patch
4. Review the schedule with assigned crew and scores

### Using the AI Chatbot
1. Click the 🤖 floating button (bottom-right)
2. Ask questions like:
   - "What's the best time to patch?"
   - "Predict network loads for this week"
   - "Analyze crew availability"
3. Get instant AI-powered recommendations

### Viewing Network Loads by Day
1. Use the day slider below the chart
2. Select any day (Monday - Sunday)
3. View 24-hour breakdown for that specific day
4. Green bars indicate optimal patching windows (< 25 kW)

---

## 🛠️ Technology Stack

**Backend:**
- Python 3.7+
- Flask 2.2.5 (REST API)
- Flask-CORS (Cross-origin support)
- scikit-learn 1.0.2 (Machine Learning)
- NumPy 1.21.6 (Numerical computing)

**Frontend:**
- Vanilla JavaScript (ES6+)
- HTML5
- CSS3 (with animations & gradients)
- Fetch API for AJAX calls

**Machine Learning:**
- Random Forest Regression
- Feature engineering
- Model persistence across sessions

---

## 🎯 Score Interpretation

Scores range from 0-100, where higher is better:

| Score Range | Interpretation |
|-------------|----------------|
| 90-100 | 🟢 Excellent - Ideal maintenance window |
| 70-89 | 🟡 Good - Acceptable for scheduling |
| 50-69 | 🟠 Fair - Consider alternatives if possible |
| < 50 | 🔴 Poor - Avoid unless urgent |
---

## 👥 Team: Los Pythones

Built with ⚡ by Los Pythones for the Hackathon

---

