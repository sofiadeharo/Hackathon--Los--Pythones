// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// State management
let appState = {
    networkLoads: [],
    crew: [],
    patches: [],
    schedule: [],
    selectedDay: 0, // 0 = Monday
    selectedPatch: null,
    isCreatingPatch: false // Track if we're creating or editing
};

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Electro-call initializing...');
    await loadData();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    const optimizeBtn = document.getElementById('optimizeBtn');
    optimizeBtn.addEventListener('click', optimizeSchedule);
    
    // Day slider
    const daySlider = document.getElementById('daySlider');
    daySlider.addEventListener('input', (e) => {
        appState.selectedDay = parseInt(e.target.value);
        updateDayLabel();
        renderNetworkLoadChart(appState.networkLoads);
    });
    
    // Add patch button
    const addPatchBtn = document.getElementById('addPatchBtn');
    addPatchBtn.addEventListener('click', openCreatePatchModal);
    
    // Modal controls
    const modal = document.getElementById('patchModal');
    const closeModal = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelBtn');
    const patchForm = document.getElementById('patchForm');
    
    closeModal.addEventListener('click', closePatchModal);
    cancelBtn.addEventListener('click', closePatchModal);
    
    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closePatchModal();
        }
    });
    
    // Form submission
    patchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        savePatchDetails();
    });
    
    // Chatbot controls
    const chatFab = document.getElementById('chatFab');
    const chatModal = document.getElementById('chatModal');
    const closeChatModal = document.getElementById('closeChatModal');
    const chatSendBtn = document.getElementById('chatSendBtn');
    const chatInput = document.getElementById('chatInput');
    
    chatFab.addEventListener('click', openChatModal);
    closeChatModal.addEventListener('click', closeChatModalFn);
    chatSendBtn.addEventListener('click', sendChatMessage);
    
    // Close chat modal when clicking outside
    chatModal.addEventListener('click', (e) => {
        if (e.target === chatModal) {
            closeChatModalFn();
        }
    });
    
    // Send message on Enter key
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });
    
    // Recommendations modal
    const recommendationsModal = document.getElementById('recommendationsModal');
    const closeRecommendationsModal = document.getElementById('closeRecommendationsModal');
    closeRecommendationsModal.addEventListener('click', () => {
        recommendationsModal.classList.remove('active');
    });
    recommendationsModal.addEventListener('click', (e) => {
        if (e.target === recommendationsModal) {
            recommendationsModal.classList.remove('active');
        }
    });
}

// Update day label
function updateDayLabel() {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    document.getElementById('dayLabel').textContent = days[appState.selectedDay];
}

// Load all data
async function loadData() {
    try {
        // Load stats
        await loadStats();
        
        // Load network load
        await loadNetworkLoad();
        
        // Load crew
        await loadCrew();
        
        // Load patches
        await loadPatches();
        
        console.log('✅ All data loaded successfully');
    } catch (error) {
        console.error('❌ Error loading data:', error);
        showError('Failed to load data. Please ensure the backend server is running on port 5000.');
    }
}

// Load stats
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const stats = await response.json();
        
        // Display lowest load hours
        const lowLoadHtml = stats.low_load_hours.map(hour => 
            `<div style="color: var(--neon-green); font-weight: bold;">
                ${hour.label} <span style="color: var(--text-secondary);">(${hour.load_kw} kW)</span>
            </div>`
        ).join('');
        document.getElementById('lowLoadHours').innerHTML = lowLoadHtml;
        
        document.getElementById('totalCrew').textContent = stats.total_crew_members;
        document.getElementById('totalPatches').textContent = stats.total_patches;
        
        // Load and display best hour
        loadBestHours();
        
        // Animate stat values
        animateStatValues();
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load best hours for patching
async function loadBestHours() {
    try {
        const response = await fetch(`${API_BASE_URL}/best-hours`);
        const data = await response.json();
        
        const bestHour = data.optimal_hour;
        document.getElementById('bestHourDisplay').innerHTML = 
            `🎯 Best patch time: <strong style="color: var(--neon-green);">${bestHour.time_label}</strong> (${Math.round(bestHour.load_kw)} kW)`;
    } catch (error) {
        console.error('Error loading best hours:', error);
    }
}

// Load network load data
async function loadNetworkLoad() {
    try {
        const response = await fetch(`${API_BASE_URL}/network-load`);
        const data = await response.json();
        appState.networkLoads = data;
        
        renderNetworkLoadChart(data);
    } catch (error) {
        console.error('Error loading network load:', error);
        throw error;
    }
}

// Load crew data
async function loadCrew() {
    try {
        const response = await fetch(`${API_BASE_URL}/crew`);
        const data = await response.json();
        appState.crew = data;
        
        renderCrewList(data);
    } catch (error) {
        console.error('Error loading crew:', error);
        throw error;
    }
}

// Load patches data
async function loadPatches() {
    try {
        const response = await fetch(`${API_BASE_URL}/patches`);
        const data = await response.json();
        appState.patches = data;
        
        renderPatchList(data);
    } catch (error) {
        console.error('Error loading patches:', error);
        throw error;
    }
}

// Render network load chart (filtered by selected day)
function renderNetworkLoadChart(loads) {
    const container = document.getElementById('networkLoadChart');
    container.innerHTML = '';
    
    // Filter loads for selected day
    const dayLoads = loads.filter(load => load.day_number === appState.selectedDay);
    
    if (dayLoads.length === 0) return;
    
    const maxLoad = Math.max(...dayLoads.map(l => l.load_kilowatts));
    const scaleFactor = 100 / maxLoad; // Scale to fit chart height
    
    dayLoads.forEach((load, index) => {
        const bar = document.createElement('div');
        bar.className = 'chart-bar';
        const heightPercent = load.load_kilowatts * scaleFactor;
        bar.style.height = `${heightPercent}%`;
        
        // Highlight low load hours (good for patches)
        if (load.load_kilowatts < 25) {
            bar.style.background = 'linear-gradient(to top, var(--neon-green), var(--electric-cyan))';
            bar.style.boxShadow = '0 0 10px rgba(57, 255, 20, 0.5)';
        }
        
        bar.title = `${load.day_of_week} ${load.hour}:00 - ${Math.round(load.load_kilowatts)} kW`;
        
        const label = document.createElement('div');
        label.className = 'chart-bar-label';
        // Show hour for each bar
        label.textContent = `${load.hour}h`;
        
        const value = document.createElement('div');
        value.className = 'chart-bar-value';
        value.textContent = `${Math.round(load.load_kilowatts)} kW`;
        value.style.display = 'none'; // Only show on hover
        
        bar.addEventListener('mouseenter', () => {
            value.style.display = 'block';
            bar.style.transform = 'scale(1.05)';
            bar.style.zIndex = '10';
        });
        bar.addEventListener('mouseleave', () => {
            value.style.display = 'none';
            bar.style.transform = 'scale(1)';
            bar.style.zIndex = '1';
        });
        
        bar.appendChild(label);
        bar.appendChild(value);
        container.appendChild(bar);
        
        // Animate bars on load
        setTimeout(() => {
            bar.style.opacity = '0';
            bar.style.height = '0';
            setTimeout(() => {
                bar.style.transition = 'all 0.4s ease';
                bar.style.opacity = '1';
                bar.style.height = `${heightPercent}%`;
            }, 50);
        }, index * 30); // Smooth animation for 24 bars
    });
}

// Render crew list
function renderCrewList(crew) {
    const container = document.getElementById('crewList');
    container.innerHTML = '';
    
    crew.forEach((member, index) => {
        const crewDiv = document.createElement('div');
        crewDiv.className = 'crew-member';
        
        const hoursText = member.available_hours
            .map(([start, end]) => `${start}:00-${end}:00`)
            .join(', ');
        
        crewDiv.innerHTML = `
            <div>
                <div class="crew-name">${member.name}</div>
                <div class="crew-hours">Available: ${hoursText}</div>
            </div>
        `;
        
        container.appendChild(crewDiv);
        
        // Animate entry
        setTimeout(() => {
            crewDiv.style.opacity = '0';
            crewDiv.style.transform = 'translateX(-20px)';
            setTimeout(() => {
                crewDiv.style.transition = 'all 0.3s ease';
                crewDiv.style.opacity = '1';
                crewDiv.style.transform = 'translateX(0)';
            }, 50);
        }, index * 100);
    });
}

// Render patch list
function renderPatchList(patches) {
    const container = document.getElementById('patchList');
    container.innerHTML = '';
    
    patches.forEach((patch, index) => {
        const patchDiv = document.createElement('div');
        patchDiv.className = 'patch-item';
        patchDiv.style.cursor = 'pointer';
        
        patchDiv.innerHTML = `
            <div class="patch-header">
                <div class="patch-name">${patch.name}</div>
                <div class="patch-priority priority-${patch.priority}">
                    Priority ${patch.priority}
                </div>
            </div>
            <div class="patch-details">
                <span>⏱️ ${patch.duration}h</span>
                <span>👥 ${patch.min_crew} crew min</span>
            </div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-top: 8px;">
                📝 Click to view/edit details
            </div>
        `;
        
        // Click event to open modal
        patchDiv.addEventListener('click', () => {
            openPatchModal(patch);
        });
        
        container.appendChild(patchDiv);
        
        // Animate entry
        setTimeout(() => {
            patchDiv.style.opacity = '0';
            patchDiv.style.transform = 'translateY(20px)';
            setTimeout(() => {
                patchDiv.style.transition = 'all 0.3s ease';
                patchDiv.style.opacity = '1';
                patchDiv.style.transform = 'translateY(0)';
            }, 50);
        }, index * 100);
    });
}

// Open patch modal for creating new patch
function openCreatePatchModal() {
    appState.isCreatingPatch = true;
    appState.selectedPatch = null;
    
    // Clear and enable form fields
    document.getElementById('patchName').value = '';
    document.getElementById('patchDuration').value = '';
    document.getElementById('patchPriority').value = '';
    document.getElementById('patchMinCrew').value = '';
    document.getElementById('patchNotes').value = '';
    document.getElementById('patchUrgent').checked = false;
    
    // Update modal title
    document.querySelector('#patchModal .modal-header h2').textContent = '⚡ Create New Patch';
    
    // Show modal
    const modal = document.getElementById('patchModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// Open patch modal for editing existing patch
function openPatchModal(patch) {
    appState.isCreatingPatch = false;
    appState.selectedPatch = patch;
    
    // Populate form fields
    document.getElementById('patchName').value = patch.name;
    document.getElementById('patchDuration').value = patch.duration;
    document.getElementById('patchPriority').value = patch.priority;
    document.getElementById('patchMinCrew').value = patch.min_crew;
    document.getElementById('patchNotes').value = '';
    document.getElementById('patchUrgent').checked = patch.priority >= 5;
    
    // Update modal title
    document.querySelector('#patchModal .modal-header h2').textContent = '⚡ Patch Details';
    
    // Show modal
    const modal = document.getElementById('patchModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

// Close patch modal
function closePatchModal() {
    const modal = document.getElementById('patchModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
    appState.selectedPatch = null;
    appState.isCreatingPatch = false;
}

// Save patch details
async function savePatchDetails() {
    const name = document.getElementById('patchName').value;
    const duration = parseFloat(document.getElementById('patchDuration').value);
    const priority = parseInt(document.getElementById('patchPriority').value);
    const minCrew = parseInt(document.getElementById('patchMinCrew').value);
    const notes = document.getElementById('patchNotes').value;
    const urgent = document.getElementById('patchUrgent').checked;
    
    if (appState.isCreatingPatch) {
        // Create new patch
        const newPatch = {
            name: name,
            duration: duration,
            priority: urgent ? 5 : priority,
            min_crew: minCrew,
            notes: notes,
            urgent: urgent
        };
        
        console.log('💾 Creating new patch:', newPatch);
        
        try {
            const response = await fetch(`${API_BASE_URL}/patches`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newPatch)
            });
            
            if (response.ok) {
                alert(`✅ New patch created: ${name}\n\nDuration: ${duration}h\nPriority: ${newPatch.priority}\nNotes: ${notes || 'None'}`);
                
                // Reload patches
                await loadPatches();
                await loadStats();
            } else {
                alert('❌ Failed to create patch. Please try again.');
            }
        } catch (error) {
            console.error('Error creating patch:', error);
            alert('❌ Error creating patch. Please ensure the backend is running.');
        }
    } else {
        // Edit existing patch
        console.log('💾 Saving patch details:', {
            patch: appState.selectedPatch,
            notes: notes,
            urgent: urgent
        });
        
        alert(`✅ Details saved for: ${appState.selectedPatch.name}\n\nNotes: ${notes || 'None'}\nUrgent: ${urgent ? 'Yes' : 'No'}`);
    }
    
    // Close modal
    closePatchModal();
}

// Optimize schedule
async function optimizeSchedule() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.classList.add('active');
    
    try {
        // Simulate calculation time for dramatic effect
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Use original scheduler
        const response = await fetch(`${API_BASE_URL}/optimize-schedule`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            appState.schedule = data.schedule;
            // Show recommendations modal
            showRecommendationsModal(data.schedule);
        } else {
            throw new Error(data.error || 'Optimization failed');
        }
    } catch (error) {
        console.error('Error optimizing schedule:', error);
        showError('Failed to optimize schedule: ' + error.message);
    } finally {
        loadingOverlay.classList.remove('active');
    }
}

// Render schedule
function renderSchedule(schedule) {
    const container = document.getElementById('scheduleList');
    container.innerHTML = '';
    
    if (schedule.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No patches scheduled</p>';
        return;
    }
    
    schedule.forEach((item, index) => {
        if (item.status === 'unscheduled') {
            const unscheduledDiv = document.createElement('div');
            unscheduledDiv.className = 'schedule-item';
            unscheduledDiv.style.borderColor = 'var(--electric-pink)';
            unscheduledDiv.innerHTML = `
                <div class="schedule-header">
                    <div class="schedule-patch-name">${item.patch.name}</div>
                    <div class="schedule-score" style="background: var(--electric-pink);">UNSCHEDULED</div>
                </div>
                <div style="color: var(--text-secondary); margin-top: 10px;">
                    ⚠️ ${item.reason}
                </div>
            `;
            container.appendChild(unscheduledDiv);
        } else {
            const scheduleDiv = document.createElement('div');
            scheduleDiv.className = 'schedule-item';
            
            const startTime = formatTime(item.start_hour);
            const endTime = formatTime(item.end_hour);
            
            scheduleDiv.innerHTML = `
                <div class="schedule-header">
                    <div class="schedule-patch-name">${item.patch.name}</div>
                    <div class="schedule-score">Score: ${Math.round(item.score)}</div>
                </div>
                <div class="schedule-time">
                    🕐 ${startTime} - ${endTime}
                </div>
                <div class="schedule-details">
                    <div class="schedule-detail-item">
                        📊 Network Load: ${Math.round(item.network_load)} kW
                    </div>
                    <div class="schedule-detail-item">
                        ⏱️ Duration: ${item.patch.duration}h
                    </div>
                    <div class="schedule-detail-item">
                        🎯 Priority: ${item.patch.priority}/5
                    </div>
                </div>
                <div class="schedule-crew">
                    <div style="color: var(--text-secondary); font-size: 12px; margin-bottom: 8px;">
                        Assigned Crew:
                    </div>
                    <div class="crew-tags">
                        ${item.assigned_crew.map(name => `<div class="crew-tag">${name}</div>`).join('')}
                    </div>
                </div>
            `;
            
            container.appendChild(scheduleDiv);
        }
        
        // Animate entry
        const items = container.children;
        setTimeout(() => {
            items[index].style.opacity = '0';
            items[index].style.transform = 'translateX(50px)';
            setTimeout(() => {
                items[index].style.transition = 'all 0.5s ease';
                items[index].style.opacity = '1';
                items[index].style.transform = 'translateX(0)';
            }, 50);
        }, index * 150);
    });
}

// Helper function to format time
function formatTime(hour) {
    const h = Math.floor(hour);
    const m = Math.round((hour - h) * 60);
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
}

// Show recommendations modal
function showRecommendationsModal(schedule) {
    const modal = document.getElementById('recommendationsModal');
    const content = document.getElementById('recommendationsContent');
    
    // Calculate summary statistics
    const scheduled = schedule.filter(item => item.status === 'scheduled');
    const unscheduled = schedule.filter(item => item.status === 'unscheduled');
    const totalPatches = schedule.length;
    const avgScore = scheduled.length > 0 
        ? Math.round(scheduled.reduce((sum, item) => sum + item.score, 0) / scheduled.length)
        : 0;
    
    // Build summary section
    const successRate = totalPatches > 0 ? Math.round((scheduled.length / totalPatches) * 100) : 0;
    
    let html = `
        <div class="recommendation-summary">
            <h3>📊 Schedule Optimization Results</h3>
            <div class="summary-stats">
                <div class="summary-stat">
                    <div class="summary-stat-value" style="color: var(--sunset-orange);">${scheduled.length}</div>
                    <div class="summary-stat-label">✅ Scheduled</div>
                </div>
                <div class="summary-stat">
                    <div class="summary-stat-value" style="color: ${unscheduled.length > 0 ? 'var(--sunset-coral)' : 'var(--sunset-pink)'};">${unscheduled.length}</div>
                    <div class="summary-stat-label">⚠️ Unscheduled</div>
                </div>
                <div class="summary-stat">
                    <div class="summary-stat-value" style="color: var(--sunset-orange);">${avgScore}</div>
                    <div class="summary-stat-label">📈 Avg Score</div>
                </div>
                <div class="summary-stat">
                    <div class="summary-stat-value" style="color: var(--sunset-pink);">${successRate}%</div>
                    <div class="summary-stat-label">🎯 Success Rate</div>
                </div>
            </div>
        </div>
    `;
    
    // Scheduled patches section
    if (scheduled.length > 0) {
        html += `
            <div class="recommendation-section">
                <h3>✅ Recommended Schedule</h3>
        `;
        
        scheduled.forEach(item => {
            const startTime = formatTime(item.start_hour);
            const endTime = formatTime(item.end_hour);
            const roundedScore = Math.round(item.score);
            const networkLoad = item.network_load || 0;
            const dayInfo = item.day ? `${item.day}, ` : '';
            const classification = item.classification ? `<span style="background: linear-gradient(135deg, var(--sunset-orange), var(--sunset-pink)); padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">${item.classification}</span>` : '';
            
            html += `
                <div class="recommendation-item">
                    <div class="recommendation-item-header">
                        <div class="recommendation-item-title">${item.patch.name} ${classification}</div>
                        <div class="recommendation-badge">Score: ${roundedScore}/100</div>
                    </div>
                    <div class="recommendation-details">
                        <div class="recommendation-detail">
                            <strong>📅 Time:</strong> ${dayInfo}${startTime} - ${endTime}
                        </div>
                        <div class="recommendation-detail">
                            <strong>⚡ Network Load:</strong> ${networkLoad} kW
                        </div>
                        <div class="recommendation-detail">
                            <strong>⏱️ Duration:</strong> ${item.patch.duration}h
                        </div>
                        <div class="recommendation-detail">
                            <strong>🎯 Priority:</strong> ${item.patch.priority}/5
                        </div>
                    </div>
                    <div class="recommendation-details" style="margin-top: 10px;">
                        <div class="recommendation-detail">
                            <strong>👥 Crew:</strong> ${item.assigned_crew.join(', ')}
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    // Unscheduled patches section
    if (unscheduled.length > 0) {
        html += `
            <div class="recommendation-section">
                <h3>⚠️ Unable to Schedule</h3>
        `;
        
        unscheduled.forEach(item => {
            html += `
                <div class="recommendation-item" style="border-left-color: var(--sunset-coral);">
                    <div class="recommendation-item-header">
                        <div class="recommendation-item-title">${item.patch.name}</div>
                        <div class="recommendation-badge" style="background: linear-gradient(135deg, #ff6b6b, #ee5a6f);">UNSCHEDULED</div>
                    </div>
                    <div class="recommendation-details">
                        <div class="recommendation-detail">
                            <strong>⚠️ Reason:</strong> ${item.reason || 'No suitable time window found'}
                        </div>
                        <div class="recommendation-detail">
                            <strong>⏱️ Duration:</strong> ${item.patch.duration}h
                        </div>
                        <div class="recommendation-detail">
                            <strong>🎯 Priority:</strong> ${item.patch.priority}/5
                        </div>
                        <div class="recommendation-detail">
                            <strong>👥 Requires:</strong> ${item.patch.min_crew} crew members
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    // No schedule message
    if (schedule.length === 0) {
        html = `
            <div class="no-schedule">
                <p style="text-align: center; font-size: 18px; color: var(--text-secondary);">
                    No patches available to schedule.<br>
                    <small style="font-size: 14px; color: var(--text-secondary);">Add patches using the + button to get started.</small>
                </p>
            </div>
        `;
    } else if (scheduled.length === 0) {
        html += `
            <div class="no-schedule">
                <p style="text-align: center; font-size: 18px; color: var(--sunset-coral);">
                    ⚠️ Unable to schedule any patches at this time.<br>
                    <small style="font-size: 14px;">Please check crew availability or adjust patch requirements.</small>
                </p>
            </div>
        `;
    }
    
    content.innerHTML = html;
    modal.classList.add('active');
}

// Animate stat values
function animateStatValues() {
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach((element, index) => {
        setTimeout(() => {
            element.style.transform = 'scale(1.2)';
            setTimeout(() => {
                element.style.transition = 'transform 0.3s ease';
                element.style.transform = 'scale(1)';
            }, 100);
        }, index * 100);
    });
}

// Show error message
function showError(message) {
    alert('⚠️ ' + message);
}

// Chatbot functions
function openChatModal() {
    const modal = document.getElementById('chatModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    document.getElementById('chatInput').focus();
}

function closeChatModalFn() {
    const modal = document.getElementById('chatModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    input.value = '';
    
    // Disable send button
    const sendBtn = document.getElementById('chatSendBtn');
    sendBtn.disabled = true;
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        if (data.success) {
            addMessageToChat(data.message, 'bot');
        } else {
            const fallbackMsg = data.fallback_message || 
                'I apologize, but I\'m having trouble connecting right now. Please try again later or contact support.';
            addMessageToChat(fallbackMsg, 'bot');
        }
    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator(typingId);
        addMessageToChat('⚠️ Connection error. Please ensure the backend server is running on port 5000.', 'bot');
    } finally {
        sendBtn.disabled = false;
        input.focus();
    }
}

function addMessageToChat(message, type) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}-message`;
    
    const avatar = type === 'user' ? '👤' : '🤖';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            ${message.replace(/\n/g, '<br>')}
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addTypingIndicator() {
    const messagesContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    const id = 'typing-' + Date.now();
    typingDiv.id = id;
    typingDiv.className = 'chat-message bot-message';
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const typingDiv = document.getElementById(id);
    if (typingDiv) {
        typingDiv.remove();
    }
}

// Show multi-strategy modal
function showMultiStrategyModal(strategies, totalPatches) {
    const modal = document.getElementById('recommendationsModal');
    const content = document.getElementById('recommendationsContent');
    
    let html = `
        <div class="recommendation-summary">
            <h3>📊 Multiple Scheduling Strategies</h3>
            <p style="color: var(--text-secondary); margin-bottom: 20px;">
                Choose the strategy that best fits your needs. Total patches: ${totalPatches}
            </p>
        </div>
    `;
    
    // Add each strategy
    const strategyOrder = ['network_optimized', 'urgency_first', 'balanced'];
    strategyOrder.forEach(strategyKey => {
        const strategy = strategies[strategyKey];
        if (!strategy) return;
        
        const scheduled = strategy.schedule.filter(item => item.status === 'scheduled');
        const unscheduled = strategy.schedule.filter(item => item.status === 'unscheduled');
        const successRate = totalPatches > 0 ? Math.round((scheduled.length / totalPatches) * 100) : 0;
        const avgScore = scheduled.length > 0 
            ? Math.round(scheduled.reduce((sum, item) => sum + item.score, 0) / scheduled.length)
            : 0;
        
        html += `
            <div class="recommendation-section" style="border: 2px solid var(--sunset-orange); margin: 20px 0; padding: 20px; border-radius: 10px;">
                <h3>${strategy.icon} ${strategy.strategy}</h3>
                <p style="color: var(--text-secondary); margin-bottom: 15px;">${strategy.description}</p>
                
                <div class="summary-stats" style="margin-bottom: 20px;">
                    <div class="summary-stat">
                        <div class="summary-stat-value" style="color: var(--sunset-orange);">${scheduled.length}</div>
                        <div class="summary-stat-label">✅ Scheduled</div>
                    </div>
                    <div class="summary-stat">
                        <div class="summary-stat-value" style="color: var(--sunset-coral);">${unscheduled.length}</div>
                        <div class="summary-stat-label">⚠️ Unscheduled</div>
                    </div>
                    <div class="summary-stat">
                        <div class="summary-stat-value" style="color: var(--sunset-pink);">${avgScore}</div>
                        <div class="summary-stat-label">📈 Avg Score</div>
                    </div>
                    <div class="summary-stat">
                        <div class="summary-stat-value" style="color: var(--sunset-orange);">${successRate}%</div>
                        <div class="summary-stat-label">🎯 Success</div>
                    </div>
                </div>
                
                <details open>
                    <summary style="cursor: pointer; font-weight: bold; margin-bottom: 10px;">View Schedule</summary>
        `;
        
        // Show scheduled patches
        scheduled.forEach(item => {
            const startTime = formatTime(item.start_hour);
            const endTime = formatTime(item.end_hour);
            const roundedScore = Math.round(item.score);
            const networkLoad = item.network_load || 0;
            const dayInfo = item.day ? `${item.day}, ` : '';
            
            html += `
                <div class="recommendation-item" style="margin: 10px 0;">
                    <div class="recommendation-item-header">
                        <div class="recommendation-item-title">${item.patch.name}</div>
                        <div class="recommendation-badge">Score: ${roundedScore}/100</div>
                    </div>
                    <div class="recommendation-details">
                        <div class="recommendation-detail">
                            <strong>🕐 Time:</strong> ${dayInfo}${startTime} - ${endTime}
                        </div>
                        <div class="recommendation-detail">
                            <strong>⚡ Network Load:</strong> ${networkLoad} kW
                        </div>
                        <div class="recommendation-detail">
                            <strong>👥 Crew:</strong> ${item.assigned_crew.join(', ')}
                        </div>
                        ${item.reason ? `<div class="recommendation-detail"><strong>💡 Reason:</strong> ${item.reason}</div>` : ''}
                    </div>
                </div>
            `;
        });
        
        // Show unscheduled patches
        if (unscheduled.length > 0) {
            html += '<div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--electric-pink);">';
            html += '<h4 style="color: var(--sunset-coral); margin-bottom: 10px;">⚠️ Unscheduled Patches</h4>';
            unscheduled.forEach(item => {
                html += `
                    <div style="background: rgba(255, 107, 107, 0.1); padding: 10px; margin: 5px 0; border-radius: 5px;">
                        <strong>${item.patch.name}</strong> - ${item.reason}
                    </div>
                `;
            });
            html += '</div>';
        }
        
        html += '</details></div>';
    });
    
    content.innerHTML = html;
    modal.classList.add('active');
}

// Console art
console.log(`
⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡
     PATCH SCHEDULER v1.0
     Powered by Los Pythones
     ⚡ Electrical Aesthetic Edition ⚡
     🤖 Now with AI Recommendations!
⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡
`);

