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
from patch_classifier import patch_classifier
from network_load_predictor import network_load_predictor
from ml_optimizer import ml_optimizer
from multi_strategy_scheduler import multi_strategy_scheduler
from mock_scheduler import mock_scheduler
from ml_cache import ml_cache

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
            
            # Clear ML cache when patches change
            ml_cache.clear_cache()
            
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
    """Calculate optimal patch schedule using ML-powered Mock Scheduler"""
    global custom_patches
    try:
        # Get patches (use custom + fallback patches)
        patches = supabase_fetcher.fetch_patches() + custom_patches
        
        # Use mock scheduler with Random Forest predictions
        schedule = mock_scheduler.generate_mock_schedule(patches)
        
        return jsonify({
            'success': True,
            'schedule': schedule,
            'message': 'Schedule optimized successfully with ML predictions'
        })
    except Exception as e:
        print(f"Optimization error: {e}")
        import traceback
        traceback.print_exc()
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
    
    # Handle empty data gracefully
    avg_load = sum(load.load_kilowatts for load in network_loads) / len(network_loads) if network_loads else 0
    
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
        
        # Get CACHED ML predictions (much faster!)
        ml_context_parts = []
        try:
            # Get cached predictions (recalculates every 5 min if needed)
            predictions = ml_cache.get_cached_predictions(patches, crew, avg_load)
            
            # 1. Optimal time windows
            ml_context_parts.append("\n**🕐 OPTIMAL TIME WINDOWS FOR PATCHING:**")
            
            if predictions.get('excellent'):
                ml_context_parts.append("\n  **EXCELLENT WINDOWS (Load <20 kW):**")
                for time_slot in predictions['excellent']:
                    ml_context_parts.append(f"    ✅ {time_slot['time_display']} - {time_slot['predicted_load_kw']:.1f} kW")
            
            if predictions.get('good'):
                ml_context_parts.append("\n  **GOOD WINDOWS (Load 20-30 kW):**")
                for time_slot in predictions['good']:
                    ml_context_parts.append(f"    ✔️ {time_slot['time_display']} - {time_slot['predicted_load_kw']:.1f} kW")
            
            if predictions.get('fair'):
                ml_context_parts.append("\n  **FAIR WINDOWS (Load 30-40 kW):**")
                for time_slot in predictions['fair']:
                    ml_context_parts.append(f"    ⚠️ {time_slot['time_display']} - {time_slot['predicted_load_kw']:.1f} kW")
            
            # 2. Patch-specific windows (from cache)
            if predictions.get('patch_windows'):
                ml_context_parts.append("\n**🎯 PATCH-SPECIFIC TIME WINDOW RECOMMENDATIONS:**")
                for patch_name, windows in list(predictions['patch_windows'].items())[:3]:  # Top 3
                    patch = next((p for p in patches if p.name == patch_name), None)
                    if patch:
                        ml_context_parts.append(f"\n  **{patch.name}** (Priority: {patch.priority}/5, Duration: {patch.duration}h):")
                        for i, window in enumerate(windows[:3], 1):
                            classification = window.get('patch_type', 'Manual')
                            ml_context_parts.append(f"    {i}. {window['time_display']} - Score: {window['score']}/100, Load: {window['predicted_load_kw']:.1f} kW [{classification}]")
            
            # 3. Patch classifications (from cache)
            if predictions.get('classifications'):
                ml_context_parts.append("\n**🤖 ML PATCH CLASSIFICATIONS:**")
                for patch_name, classification in list(predictions['classifications'].items())[:5]:
                    ml_context_parts.append(f"  - {patch_name}: {classification['type']} ({classification['confidence']:.1f}% confidence) - {classification['reason']}")
            
            # 4. Strategy tips
            ml_context_parts.append("\n**💡 SCHEDULING STRATEGY TIPS:**")
            ml_context_parts.append("  • Weekend nights (Sat/Sun 0-6am) typically have lowest load")
            ml_context_parts.append("  • Avoid weekday business hours (Mon-Fri 9am-5pm)")
            ml_context_parts.append("  • Emergency patches: Schedule ASAP regardless of load")
            ml_context_parts.append("  • Manual patches: Use optimal windows with skilled crew")
            ml_context_parts.append("  • Automated patches: Any low-load window works")
            
        except Exception as ml_error:
            print(f"ML prediction error in chat: {ml_error}")
            import traceback
            traceback.print_exc()
            ml_context_parts = ["\n**ML predictions temporarily unavailable**"]
        
        ml_context = chr(10).join(ml_context_parts) if ml_context_parts else ""
        
        # Build context string
        context = f"""You are an AI assistant for the Electro-call patch scheduling system. You have access to real-time data AND THREE trained ML models:

**ML Models Available:**
1. Random Forest Regressor - network load pattern analysis
2. Random Forest Classifier - patch emergency classification (Emergency/Manual/Automated)
3. Linear Regression - precise network load predictions

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
{ml_context}

Your role is to:
1. **Provide SPECIFIC TIME WINDOWS** - Always recommend exact days and times (e.g., "Saturday 2:00 AM - 4:00 AM")
2. Analyze network load patterns using ML predictions to find optimal maintenance windows
3. Consider ML patch classifications (Emergency/Manual/Automated) when prioritizing
4. Factor in crew availability and skill levels for patch assignments
5. Provide clear, actionable scheduling recommendations backed by ML insights
6. Explain your reasoning based on real-time data AND ML model predictions

**IMPORTANT - Always recommend specific time windows:**
- Format: "DAY, START_TIME - END_TIME (Network Load: X kW, Score: Y/100)"
- Example: "Saturday, 02:00 - 04:00 (Network Load: 15 kW, Score: 95/100)"
- Provide 2-3 alternative windows if the user asks
- Explain WHY each window is good (low load, off-peak, weekend, etc.)

Always base your recommendations on:
- ML-predicted optimal time windows (shown above)
- ML-classified patch emergency status
- Patch-specific time recommendations (shown above)
- Crew availability and skills
- Minimizing network load impact

When answering questions about scheduling:
1. Look at the "OPTIMAL TIME WINDOWS" section above
2. Look at "PATCH-SPECIFIC TIME WINDOW RECOMMENDATIONS" for that specific patch
3. Recommend the best 1-3 time windows with specific days/times
4. Explain the score and network load for each window
5. Mention any relevant ML classifications or strategy tips"""

        # Call OpenAI API
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": context},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.5,  # Lower = faster, more focused
                    max_tokens=600    # Reduced for faster responses while still detailed
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

@app.route('/api/classify-patch', methods=['POST'])
def classify_patch():
    """Classify a patch as Emergency, Manual, or Automated using ML"""
    try:
        data = request.json
        
        # Get patch details
        patch_id = data.get('patch_id')
        network_load = data.get('network_load', 40.0)  # Default average load
        crew_available = data.get('crew_available', 3)
        hour = data.get('hour', 2)  # Default to 2 AM
        
        # Get the patch
        patches = supabase_fetcher.fetch_patches() + custom_patches
        patch = next((p for p in patches if p.id == patch_id), None)
        
        if not patch:
            return jsonify({'success': False, 'error': 'Patch not found'}), 404
        
        # Classify the patch
        result = patch_classifier.predict(patch, network_load, crew_available, hour)
        
        return jsonify({
            'success': True,
            'patch_id': patch_id,
            'patch_name': patch.name,
            'classification': result
        })
        
    except Exception as e:
        print(f"Classification error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/classify-all-patches', methods=['GET'])
def classify_all_patches():
    """Classify all patches and return emergency status predictions"""
    try:
        # Get data
        network_loads = supabase_fetcher.fetch_network_loads()
        crew = supabase_fetcher.fetch_crew_members()
        patches = supabase_fetcher.fetch_patches() + custom_patches
        
        # Calculate average network load
        avg_load = sum(l.load_kilowatts for l in network_loads) / len(network_loads) if network_loads else 40.0
        
        # Classify each patch
        classifications = []
        for patch in patches:
            # Use optimal low-load hour (e.g., 2 AM)
            result = patch_classifier.predict(patch, avg_load, len(crew), hour=2)
            classifications.append({
                'patch_id': patch.id,
                'patch_name': patch.name,
                'patch_priority': patch.priority,
                'predicted_type': result['patch_type'],
                'confidence': result['confidence'],
                'probabilities': result['probabilities'],
                'recommended_priority': result['recommended_priority'],
                'reasoning': result['reasoning']
            })
        
        return jsonify({
            'success': True,
            'total_patches': len(patches),
            'classifications': classifications,
            'model_stats': patch_classifier.get_model_stats()
        })
        
    except Exception as e:
        print(f"Bulk classification error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/predict-load', methods=['POST'])
def predict_load():
    """Predict network load for a specific day and time using Linear Regression"""
    try:
        data = request.json
        day = data.get('day', 'Monday')  # Day name or number (0-6)
        hour = data.get('hour', 2)
        minute = data.get('minute', 0)
        
        # Predict load
        predicted_load = network_load_predictor.predict(day, hour, minute)
        
        return jsonify({
            'success': True,
            'day': day,
            'hour': hour,
            'minute': minute,
            'predicted_load_kw': predicted_load,
            'model_type': 'Linear Regression'
        })
        
    except Exception as e:
        print(f"Load prediction error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/predict-week-load', methods=['GET'])
def predict_week_load():
    """Predict network load for the entire week using Linear Regression"""
    try:
        week_predictions = network_load_predictor.predict_week()
        
        return jsonify({
            'success': True,
            'total_predictions': len(week_predictions),
            'predictions': week_predictions,
            'model_stats': network_load_predictor.get_model_stats()
        })
        
    except Exception as e:
        print(f"Week prediction error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/optimal-patch-times', methods=['GET'])
def get_optimal_patch_times():
    """Get optimal patch times based on predicted network load"""
    try:
        duration = request.args.get('duration', default=2, type=int)
        top_n = request.args.get('top_n', default=5, type=int)
        
        optimal_times = network_load_predictor.find_optimal_patch_times(
            duration_hours=duration, 
            top_n=top_n
        )
        
        return jsonify({
            'success': True,
            'duration_hours': duration,
            'optimal_times': optimal_times,
            'model_stats': network_load_predictor.get_model_stats()
        })
        
    except Exception as e:
        print(f"Optimal times error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/all-ml-models', methods=['GET'])
def get_all_ml_models():
    """Get statistics from all ML models"""
    try:
        return jsonify({
            'success': True,
            'models': {
                'random_forest_predictor': predictor.get_model_stats(),
                'patch_classifier': patch_classifier.get_model_stats(),
                'linear_regression_predictor': network_load_predictor.get_model_stats()
            }
        })
        
    except Exception as e:
        print(f"Model stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ml-optimize-patch', methods=['POST'])
def ml_optimize_patch():
    """Get ML-powered optimization for a single patch"""
    try:
        data = request.json
        patch_id = data.get('patch_id')
        day = data.get('day')  # Optional - if not provided, find optimal
        hour = data.get('hour')  # Optional - if not provided, find optimal
        
        # Get data
        crew = supabase_fetcher.fetch_crew_members()
        patches = supabase_fetcher.fetch_patches() + custom_patches
        patch = next((p for p in patches if p.id == patch_id), None)
        
        if not patch:
            return jsonify({'success': False, 'error': 'Patch not found'}), 404
        
        # Get comprehensive recommendation
        recommendation = ml_optimizer.get_comprehensive_recommendation(patch, crew, day, hour)
        
        return jsonify({
            'success': True,
            'recommendation': recommendation
        })
        
    except Exception as e:
        print(f"ML optimization error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ml-optimize-all', methods=['GET'])
def ml_optimize_all():
    """Get ML-powered optimization for all patches"""
    try:
        # Get data
        crew = supabase_fetcher.fetch_crew_members()
        patches = supabase_fetcher.fetch_patches() + custom_patches
        
        # Optimize all patches
        result = ml_optimizer.optimize_all_patches(patches, crew)
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        print(f"ML bulk optimization error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/optimal-hours-for-patch', methods=['POST'])
def get_optimal_hours_for_patch():
    """Get optimal hours for scheduling a specific patch"""
    try:
        data = request.json
        patch_id = data.get('patch_id')
        top_n = data.get('top_n', 5)
        
        # Get data
        crew = supabase_fetcher.fetch_crew_members()
        patches = supabase_fetcher.fetch_patches() + custom_patches
        patch = next((p for p in patches if p.id == patch_id), None)
        
        if not patch:
            return jsonify({'success': False, 'error': 'Patch not found'}), 404
        
        # Find optimal hours
        optimal_hours = ml_optimizer.find_optimal_hours_for_patch(patch, len(crew), top_n)
        
        return jsonify({
            'success': True,
            'patch_id': patch_id,
            'patch_name': patch.name,
            'optimal_hours': optimal_hours
        })
        
    except Exception as e:
        print(f"Optimal hours error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/score-at-time', methods=['POST'])
def get_score_at_time():
    """Get the score for scheduling a patch at a specific time"""
    try:
        data = request.json
        patch_id = data.get('patch_id')
        day = data.get('day', 'Monday')
        hour = data.get('hour', 2)
        
        # Get data
        crew = supabase_fetcher.fetch_crew_members()
        patches = supabase_fetcher.fetch_patches() + custom_patches
        patch = next((p for p in patches if p.id == patch_id), None)
        
        if not patch:
            return jsonify({'success': False, 'error': 'Patch not found'}), 404
        
        # Get score at time
        score_info = ml_optimizer.get_score_at_time(patch, crew, day, hour)
        
        return jsonify({
            'success': True,
            'patch_id': patch_id,
            'patch_name': patch.name,
            **score_info
        })
        
    except Exception as e:
        print(f"Score calculation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recommend-crew', methods=['POST'])
def recommend_crew():
    """Get crew recommendation for a patch at a specific time"""
    try:
        data = request.json
        patch_id = data.get('patch_id')
        hour = data.get('hour', 2)
        network_load = data.get('network_load', 40.0)
        
        # Get data
        crew = supabase_fetcher.fetch_crew_members()
        patches = supabase_fetcher.fetch_patches() + custom_patches
        patch = next((p for p in patches if p.id == patch_id), None)
        
        if not patch:
            return jsonify({'success': False, 'error': 'Patch not found'}), 404
        
        # Get crew recommendation
        crew_rec = ml_optimizer.recommend_crew_for_patch(patch, crew, hour, network_load)
        
        return jsonify({
            'success': True,
            'patch_id': patch_id,
            'patch_name': patch.name,
            'hour': hour,
            **crew_rec
        })
        
    except Exception as e:
        print(f"Crew recommendation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/multi-strategy-schedule', methods=['POST'])
def multi_strategy_schedule():
    """
    Get multiple scheduling strategies based on different priorities
    Returns 3 options: Network-Optimized, Urgency-First, and Balanced
    """
    try:
        # Get data
        network_loads = supabase_fetcher.fetch_network_loads()
        crew = supabase_fetcher.fetch_crew_members()
        patches = supabase_fetcher.fetch_patches() + custom_patches
        
        # Generate multiple strategies
        strategies = multi_strategy_scheduler.generate_multiple_schedules(patches, crew, network_loads)
        
        return jsonify({
            'success': True,
            'strategies': strategies,
            'total_patches': len(patches),
            'crew_available': len(crew)
        })
        
    except Exception as e:
        print(f"Multi-strategy scheduling error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/alternative-times', methods=['POST'])
def get_alternative_times():
    """Get alternative scheduling times for a specific patch"""
    try:
        data = request.json
        patch_id = data.get('patch_id')
        top_n = data.get('top_n', 5)
        
        # Get data
        network_loads = supabase_fetcher.fetch_network_loads()
        crew = supabase_fetcher.fetch_crew_members()
        patches = supabase_fetcher.fetch_patches() + custom_patches
        patch = next((p for p in patches if p.id == patch_id), None)
        
        if not patch:
            return jsonify({'success': False, 'error': 'Patch not found'}), 404
        
        # Get alternative times
        alternatives = multi_strategy_scheduler.get_alternative_times_for_patch(
            patch, crew, network_loads, top_n
        )
        
        return jsonify({
            'success': True,
            'patch_id': patch_id,
            'patch_name': patch.name,
            'alternatives': alternatives
        })
        
    except Exception as e:
        print(f"Alternative times error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Train ML models on startup
    print("Initializing ML-powered patch advisor...")
    
    # 1. Train Random Forest Network Load Predictor
    initial_loads = supabase_fetcher.fetch_network_loads()
    predictor.train(initial_loads)
    print(f"Random Forest Predictor trained on {len(initial_loads)} data points")
    print(f"RF Predictor stats: {predictor.get_model_stats()}")
    
    # 2. Train Patch Emergency Classifier
    patch_classifier.train(n_samples=1000)
    print(f"Patch Classifier stats: {patch_classifier.get_model_stats()}")
    
    # 3. Train Linear Regression Network Load Predictor
    network_load_predictor.train(n_samples=1000)
    print(f"Linear Regression Predictor stats: {network_load_predictor.get_model_stats()}")
    
    print("\n=== All ML Models Ready ===")
    print("Server starting on http://127.0.0.1:8000")
    
    app.run(debug=True, port=8000)

