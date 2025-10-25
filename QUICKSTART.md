# ⚡ Quick Start Guide

## For Windows Users

### Option 1: Using Batch Scripts (Easiest)

1. **Start the Backend:**
   - Double-click `start_backend.bat`
   - Wait for message: "Running on http://127.0.0.1:5000"

2. **Start the Frontend:**
   - Double-click `start_frontend.bat`
   - Open browser to: http://localhost:8000

### Option 2: Manual Start

**Terminal 1 (Backend):**
```bash
cd Hackathon--Los--Pythones/BackENd
pip install -r requirements.txt
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd Hackathon--Los--Pythones/frontend
python -m http.server 8000
```

Then open: http://localhost:8000

---

## For Mac/Linux Users

**Terminal 1 (Backend):**
```bash
cd Hackathon--Los--Pythones/BackENd
pip3 install -r requirements.txt
python3 app.py
```

**Terminal 2 (Frontend):**
```bash
cd Hackathon--Los--Pythones/frontend
python3 -m http.server 8000
```

Then open: http://localhost:8000

---

## Using the App

1. **Dashboard loads automatically** - Shows network load, crew, and patches
2. **Click "⚡ OPTIMIZE SCHEDULE ⚡"** - Calculates best patch times
3. **Review the schedule** - See when each patch should run and who's assigned

---

## Troubleshooting

**"Connection refused" error?**
- Make sure backend is running first (Terminal 1)
- Check that port 5000 is available

**Can't install Flask?**
- Try: `pip install --user flask flask-cors`
- Or use virtual environment: `python -m venv venv` then activate it

**Browser shows blank page?**
- Make sure you're using http://localhost:8000 (not file://)
- Try a different browser
- Check browser console for errors

---

⚡ **Ready to optimize your patches!** ⚡

