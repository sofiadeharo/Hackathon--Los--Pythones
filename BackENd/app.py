from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import os
from scheduler import PatchScheduler
from models import NetworkLoad, CrewMember, Patch
from ml_predictor import predictor
from supabase_client import supabase_fetcher
from openai import OpenAI

# Configure Flask to serve frontend files
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize scheduler
scheduler = PatchScheduler()

# Store custom patches in memory (will reset on server restart)
custom_patches = []
next_patch_id = 100  # Start from 100 to avoid conflicts with Supabase IDs

# Initialize OpenAI client
openai_api_key = os.environ.get('OPENAI_API_KEY')
openai_client = None
if openai_api_key:
    try:
        openai_client = OpenAI(api_key=openai_api_key)
        print("OpenAI client initialized successfully")
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
else:
    print("OPENAI_API_KEY not found. Chatbot will use fallback responses.")

# Train ML model on startup
print("Training ML model for network load prediction...")
print("Initializing Supabase connection...")

# Sample data generation
def generate_sample_network_loads():
    """Generate sample network load data for 7 days (weekly)"""
    loads = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day_num, day_name in enumerate(days):
        for hour in range(24):
            # Weekday pattern (Mon-Fri)
            if day_num < 5:
                if 9 <= hour <= 17:  # Business hours
                    load_kw = random.uniform(45, 85)
                elif 6 <= hour <= 8 or 18 <= hour <= 22:  # Peak home usage
                    load_kw = random.uniform(35, 55)
                else:  # Night time - best for patches
                    load_kw = random.uniform(8, 25)
            # Weekend pattern
            else:
                if 10 <= hour <= 20:  # Daytime weekend
                    load_kw = random.uniform(25, 45)
                else:  # Night time - excellent for patches
                    load_kw = random.uniform(5, 18)
            
            loads.append(NetworkLoad(
                hour=hour,
                load_kilowatts=round(load_kw, 2),
                day_of_week=day_name,
                day_number=day_num
            ))
    return loads

def generate_sample_crew():
    """Generate sample crew availability"""
    crew = [
        CrewMember(name="Alice Chen", available_hours=[(0, 8), (20, 24)], skill_level=5),
        CrewMember(name="Bob Martinez", available_hours=[(6, 14), (22, 24)], skill_level=4),
        CrewMember(name="Carol Davis", available_hours=[(18, 24)], skill_level=5),
        CrewMember(name="David Kim", available_hours=[(0, 6), (22, 24)], skill_level=3),
        CrewMember(name="Eve Thompson", available_hours=[(1, 9), (19, 24)], skill_level=4),
    ]
    return crew

def generate_sample_patches():
    """Generate sample patches to schedule"""
    patches = [
        Patch(id=1, name="Database Security Update", duration=2, priority=5, min_crew=2),
        Patch(id=2, name="Web Server Patch", duration=1, priority=3, min_crew=1),
        Patch(id=3, name="Core Network Firmware", duration=3, priority=5, min_crew=3),
        Patch(id=4, name="Application Server Update", duration=1.5, priority=4, min_crew=2),
        Patch(id=5, name="Backup System Patch", duration=2, priority=2, min_crew=1),
    ]
    return patches

# Serve frontend
@app.route('/')
def serve_frontend():
    """Serve the frontend HTML"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/network-load', methods=['GET'])
def get_network_load():
    """Get network load data for the week (7 days × 24 hours = 168 data points)"""
    loads = supabase_fetcher.fetch_network_loads()
    return jsonify([load.to_dict() for load in loads])

@app.route('/api/best-hours', methods=['GET'])
def get_best_hours():
    """Get the best hours for patching (lowest network load)"""
    loads = supabase_fetcher.fetch_network_loads()
    # Sort by load and get top 10 best hours
    sorted_loads = sorted(loads, key=lambda x: x.load_kilowatts)
    best_hours = sorted_loads[:10]
    
    return jsonify({
        'best_hours': [
            {
                'day': load.day_of_week,
                'hour': load.hour,
                'load_kw': load.load_kilowatts,
                'time_label': f"{load.day_of_week} {load.hour}:00"
            }
            for load in best_hours
        ],
        'optimal_hour': {
            'day': best_hours[0].day_of_week,
            'hour': best_hours[0].hour,
            'load_kw': best_hours[0].load_kilowatts,
            'time_label': f"{best_hours[0].day_of_week} {best_hours[0].hour}:00"
        }
    })

@app.route('/api/crew', methods=['GET'])
def get_crew():
    """Get crew availability from Supabase"""
    crew = supabase_fetcher.fetch_crew_members()
    return jsonify([member.to_dict() for member in crew])

@app.route('/api/patches', methods=['GET', 'POST'])
def handle_patches():
    """Get patches that need to be scheduled or create a new patch"""
    global custom_patches, next_patch_id
    
    if request.method == 'GET':
        # Return all patches (from Supabase + custom in-memory)
        patches = supabase_fetcher.fetch_patches() + custom_patches
        return jsonify([patch.to_dict() for patch in patches])
    
    elif request.method == 'POST':
        # Create new patch
        try:
            data = request.json
            new_patch = Patch(
                id=next_patch_id,
                name=data.get('name', 'Unnamed Patch'),
                duration=float(data.get('duration', 1)),
                priority=int(data.get('priority', 3)),
                min_crew=int(data.get('min_crew', 1))
            )
            custom_patches.append(new_patch)
            next_patch_id += 1
            
            print(f"New patch created: {new_patch.name} (ID: {new_patch.id})")
            
            return jsonify({
                'success': True,
                'patch': new_patch.to_dict()
            }), 201
        except Exception as e:
            print(f"Error creating patch: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

@app.route('/api/optimize-schedule', methods=['POST'])
def optimize_schedule():
    """Calculate optimal patch schedule"""
    global custom_patches
    try:
        # Get data from Supabase
        network_loads = supabase_fetcher.fetch_network_loads()
        crew = supabase_fetcher.fetch_crew_members()
        patches = supabase_fetcher.fetch_patches() + custom_patches  # Include custom patches
        
        # Run optimization
        schedule = scheduler.optimize(network_loads, crew, patches)
        
        return jsonify({
            'success': True,
            'schedule': schedule,
            'message': 'Schedule optimized successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/schedule-patch', methods=['POST'])
def schedule_patch():
    """Manually schedule a specific patch"""
    data = request.json
    patch_id = data.get('patch_id')
    start_hour = data.get('start_hour')
    
    if not patch_id or start_hour is None:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Here you would add logic to schedule the patch
    return jsonify({
        'success': True,
        'message': f'Patch {patch_id} scheduled at hour {start_hour}'
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall system statistics"""
    global custom_patches
    network_loads = supabase_fetcher.fetch_network_loads()
    crew = supabase_fetcher.fetch_crew_members()
    patches = supabase_fetcher.fetch_patches() + custom_patches  # Include custom patches
    
    avg_load = sum(load.load_kilowatts for load in network_loads) / len(network_loads)
    
    # Get the 5 hours with lowest network load
    sorted_loads = sorted(network_loads, key=lambda x: x.load_kilowatts)
    low_load_hours = [
        {
            'day': load.day_of_week[:3],  # Mon, Tue, etc.
            'hour': load.hour,
            'load_kw': round(load.load_kilowatts, 1),
            'label': f"{load.day_of_week[:3]} {load.hour}:00"
        }
        for load in sorted_loads[:5]
    ]
    
    total_crew_hours = sum(
        sum(end - start for start, end in member.available_hours) 
        for member in crew
    )
    
    total_patch_duration = sum(patch.duration for patch in patches)
    high_priority_patches = len([p for p in patches if p.priority >= 4])
    
    return jsonify({
        'avg_network_load': round(avg_load, 1),
        'low_load_hours': low_load_hours,
        'total_crew_hours': total_crew_hours,
        'total_crew_members': len(crew),
        'total_patches': len(patches),
        'total_patch_hours': total_patch_duration,
        'high_priority_patches': high_priority_patches
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """OpenAI-powered chatbot for patch scheduling recommendations"""
    global custom_patches
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400
        
        # Get current system context from Supabase
        network_loads = supabase_fetcher.fetch_network_loads()
        crew = supabase_fetcher.fetch_crew_members()
        patches = supabase_fetcher.fetch_patches() + custom_patches  # Include custom patches
        
        # Prepare context data for OpenAI
        # Network load summary
        avg_load = sum(l.load_kilowatts for l in network_loads) / len(network_loads)
        low_load_hours = sorted(network_loads, key=lambda x: x.load_kilowatts)[:10]
        
        # Crew summary
        crew_summary = [f"{c.name} (Skill: {c.skill_level}, Available: {len(c.available_hours)} time slots)" 
                       for c in crew]
        
        # Patches summary
        patches_summary = [f"{p.name} (Duration: {p.duration}h, Priority: {p.priority}/5, Min Crew: {p.min_crew})" 
                          for p in patches]
        
        # Build context string
        context = f"""You are an AI assistant for the Electro-call patch scheduling system. You have access to real-time data:

**Network Load Data (Weekly - measured in kilowatts):**
- Average load across week: {avg_load:.2f} kW
- Total data points: {len(network_loads)} (7 days × 24 hours)
- Lowest load hours:
{chr(10).join([f"  - {l.day_of_week} at {l.hour}:00 - {l.load_kilowatts} kW" for l in low_load_hours[:5]])}

**Crew Availability:**
{chr(10).join([f"  - {s}" for s in crew_summary])}
Total crew members: {len(crew)}

**Pending Patches:**
{chr(10).join([f"  - {s}" for s in patches_summary])}
Total patches: {len(patches)}

Your role is to:
1. Analyze network load patterns to recommend optimal maintenance windows
2. Consider crew availability and skill levels for patch assignments
3. Prioritize patches based on their priority level and duration
4. Provide clear, actionable scheduling recommendations
5. Explain your reasoning based on the data

Always base your recommendations on minimizing network load impact and ensuring proper crew availability."""

        # Call OpenAI API
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": context},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                response_text = response.choices[0].message.content
                
                return jsonify({
                    'success': True,
                    'message': response_text
                })
                
            except Exception as e:
                print(f"OpenAI API error: {e}")
                return jsonify({
                    'success': False,
                    'error': f"OpenAI API error: {str(e)}",
                    'fallback_message': "I'm having trouble connecting to the AI service. Please check your API key."
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'OpenAI client not initialized',
                'fallback_message': 'AI chatbot is not configured. Please set your OPENAI_API_KEY environment variable.'
            }), 503
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_message': "I'm having trouble processing your request. Please try again."
        }), 500

@app.route('/api/ml-stats', methods=['GET'])
def get_ml_stats():
    """Get ML model statistics and predictions"""
    try:
        network_loads = supabase_fetcher.fetch_network_loads()
        
        # Train if not already trained
        if not predictor.is_trained:
            predictor.train(network_loads)
        
        # Get model stats
        stats = predictor.get_model_stats()
        
        # Get optimal windows
        optimal_windows = predictor.find_optimal_windows(2, network_loads)
        
        return jsonify({
            'success': True,
            'model_stats': stats,
            'optimal_windows': optimal_windows[:5]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Train ML model on startup with data from Supabase
    print("Initializing ML-powered patch advisor...")
    initial_loads = supabase_fetcher.fetch_network_loads()
    predictor.train(initial_loads)
    print(f"Model trained successfully on {len(initial_loads)} data points")
    print(f"Model stats: {predictor.get_model_stats()}")
    
    app.run(debug=True, port=8000)

