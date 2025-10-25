# 🗄️ Supabase Integration Setup Guide

This guide will help you set up Supabase to provide real-time data for crew availability, network activity predictions, and patch management.

## 📋 Prerequisites

1. A Supabase account (sign up at https://supabase.com)
2. Python 3.7 or higher
3. The Electro-call backend running

## 🚀 Quick Setup

### Step 1: Create a Supabase Project

1. Go to https://app.supabase.com
2. Click "New Project"
3. Fill in your project details:
   - **Name**: `electro-call-patches`
   - **Database Password**: (choose a strong password)
   - **Region**: (select closest to your location)

### Step 2: Create Database Tables

Navigate to your project's SQL Editor and run these commands:

#### Table 1: Network Loads
```sql
CREATE TABLE network_loads (
  id BIGSERIAL PRIMARY KEY,
  day_of_week TEXT NOT NULL,
  day_number INTEGER NOT NULL CHECK (day_number >= 0 AND day_number <= 6),
  hour INTEGER NOT NULL CHECK (hour >= 0 AND hour <= 23),
  load_kilowatts DECIMAL(10, 2) NOT NULL,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX idx_network_loads_day_hour ON network_loads(day_number, hour);
```

#### Table 2: Crew Members
```sql
CREATE TABLE crew_members (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  available_hours JSONB NOT NULL DEFAULT '[]'::jsonb,
  skills JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Example: available_hours format: [[8, 16], [18, 22]]
-- This means available from 8:00-16:00 and 18:00-22:00
```

#### Table 3: Patches
```sql
CREATE TABLE patches (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  duration DECIMAL(10, 2) NOT NULL,
  priority INTEGER NOT NULL CHECK (priority >= 1 AND priority <= 5),
  min_crew INTEGER NOT NULL DEFAULT 1,
  status TEXT DEFAULT 'pending',
  notes TEXT,
  is_urgent BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_patches_updated_at BEFORE UPDATE ON patches
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Step 3: Insert Sample Data

#### Sample Network Loads (Weekly Pattern)
```sql
INSERT INTO network_loads (day_of_week, day_number, hour, load_kilowatts) VALUES
-- Monday
('Monday', 0, 0, 15.5), ('Monday', 0, 1, 12.3), ('Monday', 0, 2, 10.8),
('Monday', 0, 3, 8.2), ('Monday', 0, 4, 9.5), ('Monday', 0, 5, 12.7),
('Monday', 0, 6, 22.4), ('Monday', 0, 7, 35.6), ('Monday', 0, 8, 48.9),
('Monday', 0, 9, 65.3), ('Monday', 0, 10, 72.1), ('Monday', 0, 11, 75.8),
('Monday', 0, 12, 78.5), ('Monday', 0, 13, 76.2), ('Monday', 0, 14, 74.9),
('Monday', 0, 15, 73.1), ('Monday', 0, 16, 71.5), ('Monday', 0, 17, 68.2),
('Monday', 0, 18, 52.3), ('Monday', 0, 19, 45.1), ('Monday', 0, 20, 38.7),
('Monday', 0, 21, 32.5), ('Monday', 0, 22, 25.8), ('Monday', 0, 23, 19.2),
-- Tuesday
('Tuesday', 1, 0, 14.8), ('Tuesday', 1, 1, 11.5), ('Tuesday', 1, 2, 10.2),
('Tuesday', 1, 3, 7.9), ('Tuesday', 1, 4, 9.1), ('Tuesday', 1, 5, 12.3),
('Tuesday', 1, 6, 21.7), ('Tuesday', 1, 7, 34.9), ('Tuesday', 1, 8, 47.5),
('Tuesday', 1, 9, 64.1), ('Tuesday', 1, 10, 71.3), ('Tuesday', 1, 11, 74.9),
('Tuesday', 1, 12, 77.8), ('Tuesday', 1, 13, 75.5), ('Tuesday', 1, 14, 73.8),
('Tuesday', 1, 15, 72.3), ('Tuesday', 1, 16, 70.8), ('Tuesday', 1, 17, 67.4),
('Tuesday', 1, 18, 51.6), ('Tuesday', 1, 19, 44.3), ('Tuesday', 1, 20, 37.9),
('Tuesday', 1, 21, 31.8), ('Tuesday', 1, 22, 25.1), ('Tuesday', 1, 23, 18.5);

-- Continue for Wednesday through Sunday...
-- (For brevity, showing pattern. In production, fill all 168 hours)
```

#### Sample Crew Members
```sql
INSERT INTO crew_members (name, role, available_hours, skills) VALUES
('Alex Chen', 'Senior Engineer', '[[8, 16], [18, 22]]', '["Security", "Database"]'),
('Sarah Miller', 'Systems Admin', '[[9, 17]]', '["Networking", "Cloud"]'),
('Mike Johnson', 'DevOps Engineer', '[[10, 18]]', '["Automation", "Security"]'),
('Emily Davis', 'Network Specialist', '[[7, 15], [20, 23]]', '["Networking", "Monitoring"]'),
('David Wilson', 'Security Analyst', '[[13, 21]]', '["Security", "Compliance"]');
```

#### Sample Patches
```sql
INSERT INTO patches (name, duration, priority, min_crew, status, is_urgent, notes) VALUES
('Security Update CVE-2024', 3, 5, 2, 'pending', true, 'Critical security patch'),
('Database Migration', 4, 4, 3, 'pending', false, 'Migrate to new schema'),
('API Gateway Update', 2, 3, 2, 'pending', false, 'Version upgrade'),
('Monitoring System Upgrade', 2, 3, 1, 'pending', false, 'Update to latest'),
('Load Balancer Config', 1, 2, 1, 'pending', false, 'Performance tuning');
```

### Step 4: Get Your Supabase Credentials

1. In your Supabase project, go to **Settings** → **API**
2. You'll find:
   - **Project URL**: `https://your-project.supabase.co`
   - **anon (public) key**: `eyJ...` (long string)

### Step 5: Set Environment Variables

#### On Windows (PowerShell):
```powershell
$env:SUPABASE_URL="https://your-project.supabase.co"
$env:SUPABASE_KEY="your-anon-key-here"
```

#### On Windows (CMD):
```cmd
set SUPABASE_URL=https://your-project.supabase.co
set SUPABASE_KEY=your-anon-key-here
```

#### On Linux/Mac:
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key-here"
```

#### Or create a `.env` file (Recommended):
Create a file named `.env` in the `BackENd` directory:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

And add to the top of `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Step 6: Install Supabase Client

```bash
cd BackENd
pip install supabase==1.0.3
```

### Step 7: Test the Connection

Restart your Flask server:
```bash
python app.py
```

You should see:
```
Initializing Supabase connection...
Supabase client initialized successfully
Fetched X network load records from Supabase
Fetched X crew members from Supabase
Fetched X patches from Supabase
```

## 📊 Data Schema Reference

### Network Loads Table
| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL | Primary key |
| day_of_week | TEXT | 'Monday', 'Tuesday', etc. |
| day_number | INTEGER | 0-6 (0=Monday, 6=Sunday) |
| hour | INTEGER | 0-23 |
| load_kilowatts | DECIMAL | Network load in kW |
| timestamp | TIMESTAMPTZ | When record was created |

### Crew Members Table
| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL | Primary key |
| name | TEXT | Crew member name |
| role | TEXT | Job title/role |
| available_hours | JSONB | Array of [start, end] hour pairs |
| skills | JSONB | Array of skill strings |
| created_at | TIMESTAMPTZ | When record was created |

### Patches Table
| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL | Primary key |
| name | TEXT | Patch name |
| duration | DECIMAL | Duration in hours |
| priority | INTEGER | 1-5 (5 is highest) |
| min_crew | INTEGER | Minimum crew members needed |
| status | TEXT | 'pending', 'scheduled', 'completed' |
| notes | TEXT | Additional notes |
| is_urgent | BOOLEAN | Urgent flag |
| created_at | TIMESTAMPTZ | When record was created |
| updated_at | TIMESTAMPTZ | Last update time |

## 🔄 Fallback Behavior

If Supabase connection fails or credentials are missing, the app automatically falls back to generated sample data. This ensures the app works even without Supabase.

## 🔒 Security Tips

1. **Never commit credentials** to Git. Add `.env` to your `.gitignore`
2. Use **Row Level Security (RLS)** in Supabase for production
3. Consider using the **service_role key** for backend operations (not exposed to frontend)
4. Rotate your API keys regularly

## 🐛 Troubleshooting

### "Supabase not installed"
```bash
pip install supabase
```

### "ModuleNotFoundError: No module named 'supabase'"
Make sure you're in the correct virtual environment and have run `pip install -r requirements.txt`

### "Supabase credentials not found"
Check that your environment variables are set correctly. Restart your terminal/IDE after setting them.

### Connection timeout
1. Check your project URL is correct
2. Verify your internet connection
3. Check if Supabase service is up at https://status.supabase.com

## 📝 Next Steps

1. Set up Supabase Row Level Security policies
2. Create API endpoints for updating data
3. Set up real-time subscriptions for live updates
4. Implement data validation and sanitization
5. Add user authentication and authorization

## 🎉 Success!

Your Electro-call app is now connected to Supabase! The app will fetch real-time data for:
- ⚡ Network activity predictions
- 👥 Crew availability schedules  
- 🔧 Patch priorities and requirements

All data updates in Supabase will be reflected immediately in your app!

