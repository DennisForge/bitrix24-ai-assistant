/**
 * Bitrix24 AI Assistant - Frontend Application
 * 
 * This file contains the main JavaScript functionality for the web interface
 * of the Bitrix24 AI Assistant application.
 */

// Global variables
let currentUser = null;
let currentSection = 'dashboard';
let tasks = [];
let events = [];

// API Configuration
const API_BASE_URL = '/api/v1';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
async function initializeApp() {
    try {
        // Check authentication
        await checkAuthentication();
        
        // Load initial data
        await loadDashboardData();
        
        // Set up event listeners
        setupEventListeners();
        
        // Initialize navigation
        setupNavigation();
        
        console.log('Application initialized successfully');
    } catch (error) {
        console.error('Error initializing application:', error);
        handleError(error);
    }
}

/**
 * Check if user is authenticated
 */
async function checkAuthentication() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            updateUserInfo();
        } else {
            // Redirect to login if not authenticated
            window.location.href = '/login.html';
        }
    } catch (error) {
        console.error('Authentication check failed:', error);
        window.location.href = '/login.html';
    }
}

/**
 * Update user information in the UI
 */
function updateUserInfo() {
    if (currentUser) {
        document.getElementById('user-name').textContent = currentUser.full_name;
    }
}

/**
 * Load dashboard data
 */
async function loadDashboardData() {
    try {
        await Promise.all([
            loadTasks(),
            loadEvents(),
            loadStatistics()
        ]);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

/**
 * Load tasks from the API
 */
async function loadTasks() {
    try {
        const response = await apiRequest('GET', '/tasks');
        tasks = response.data || [];
        
        updateTaskStatistics();
        updateRecentTasks();
        updateTasksTable();
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

/**
 * Load events from the API
 */
async function loadEvents() {
    try {
        const response = await apiRequest('GET', '/calendar/events');
        events = response.data || [];
        
        updateEventStatistics();
        updateUpcomingEvents();
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

/**
 * Load statistics
 */
async function loadStatistics() {
    try {
        const response = await apiRequest('GET', '/dashboard/statistics');
        const stats = response.data || {};
        
        document.getElementById('total-tasks').textContent = stats.total_tasks || 0;
        document.getElementById('pending-tasks').textContent = stats.pending_tasks || 0;
        document.getElementById('completed-tasks').textContent = stats.completed_tasks || 0;
        document.getElementById('today-events').textContent = stats.today_events || 0;
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

/**
 * Update task statistics
 */
function updateTaskStatistics() {
    const totalTasks = tasks.length;
    const pendingTasks = tasks.filter(task => task.status === 'pending').length;
    const completedTasks = tasks.filter(task => task.status === 'completed').length;
    
    document.getElementById('total-tasks').textContent = totalTasks;
    document.getElementById('pending-tasks').textContent = pendingTasks;
    document.getElementById('completed-tasks').textContent = completedTasks;
}

/**
 * Update event statistics
 */
function updateEventStatistics() {
    const today = new Date().toISOString().split('T')[0];
    const todayEvents = events.filter(event => 
        event.start_time.startsWith(today)
    ).length;
    
    document.getElementById('today-events').textContent = todayEvents;
}

/**
 * Update recent tasks display
 */
function updateRecentTasks() {
    const container = document.getElementById('recent-tasks');
    
    if (tasks.length === 0) {
        container.innerHTML = '<p class="text-muted text-center py-4">No tasks found</p>';
        return;
    }
    
    const recentTasks = tasks.slice(0, 5);
    let html = '';
    
    recentTasks.forEach(task => {
        const priorityClass = getPriorityClass(task.priority);
        const statusClass = getStatusClass(task.status);
        
        html += `
            <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                <div>
                    <h6 class="mb-1">${task.title}</h6>
                    <small class="text-muted">${task.description || 'No description'}</small>
                </div>
                <div class="text-end">
                    <span class="badge ${priorityClass}">${task.priority}</span>
                    <span class="badge ${statusClass}">${task.status}</span>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Update upcoming events display
 */
function updateUpcomingEvents() {
    const container = document.getElementById('upcoming-events');
    
    if (events.length === 0) {
        container.innerHTML = '<p class="text-muted text-center py-4">No upcoming events</p>';
        return;
    }
    
    const upcomingEvents = events
        .filter(event => new Date(event.start_time) > new Date())
        .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
        .slice(0, 5);
    
    let html = '';
    
    upcomingEvents.forEach(event => {
        const startTime = new Date(event.start_time);
        const formattedTime = startTime.toLocaleString();
        
        html += `
            <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                <div>
                    <h6 class="mb-1">${event.title}</h6>
                    <small class="text-muted">${event.location || 'No location'}</small>
                </div>
                <div class="text-end">
                    <small class="text-muted">${formattedTime}</small>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Update tasks table
 */
function updateTasksTable() {
    const tbody = document.getElementById('tasks-table-body');
    
    if (tasks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">No tasks found</td></tr>';
        return;
    }
    
    let html = '';
    
    tasks.forEach(task => {
        const priorityClass = getPriorityClass(task.priority);
        const statusClass = getStatusClass(task.status);
        const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date';
        
        html += `
            <tr>
                <td>${task.title}</td>
                <td><span class="badge ${priorityClass}">${task.priority}</span></td>
                <td><span class="badge ${statusClass}">${task.status}</span></td>
                <td>${dueDate}</td>
                <td>${task.assigned_to || 'Unassigned'}</td>
                <td>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar" role="progressbar" style="width: ${task.progress_percentage}%">
                            ${task.progress_percentage}%
                        </div>
                    </div>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editTask('${task.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteTask('${task.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Task form submission
    document.getElementById('taskForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveTask();
    });
    
    // Chat input
    document.getElementById('chat-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Task filters
    document.getElementById('task-status-filter').addEventListener('change', filterTasks);
    document.getElementById('task-priority-filter').addEventListener('change', filterTasks);
    document.getElementById('task-search').addEventListener('input', filterTasks);
}

/**
 * Setup navigation
 */
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                showSection(href.substring(1));
            }
        });
    });
}

/**
 * Show specific section
 */
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.main-content').forEach(section => {
        section.style.display = 'none';
    });
    
    // Show selected section
    const section = document.getElementById(sectionId);
    if (section) {
        section.style.display = 'block';
        currentSection = sectionId;
        
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[href="#${sectionId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        // Load section-specific data
        loadSectionData(sectionId);
    }
}

/**
 * Load section-specific data
 */
async function loadSectionData(sectionId) {
    switch (sectionId) {
        case 'dashboard':
            await loadDashboardData();
            break;
        case 'tasks':
            await loadTasks();
            break;
        case 'calendar':
            await loadCalendar();
            break;
        case 'ai-assistant':
            await loadAISuggestions();
            break;
    }
}

/**
 * Create new task
 */
function createTask() {
    // Clear form
    document.getElementById('taskForm').reset();
    document.getElementById('taskModalTitle').textContent = 'Create New Task';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('taskModal'));
    modal.show();
}

/**
 * Save task
 */
async function saveTask() {
    const form = document.getElementById('taskForm');
    const formData = new FormData(form);
    
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        priority: document.getElementById('taskPriority').value,
        status: document.getElementById('taskStatus').value,
        due_date: document.getElementById('taskDueDate').value
    };
    
    try {
        const response = await apiRequest('POST', '/tasks', taskData);
        
        if (response.success) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('taskModal'));
            modal.hide();
            
            // Reload tasks
            await loadTasks();
            
            showNotification('Task created successfully!', 'success');
        } else {
            showNotification('Error creating task: ' + response.message, 'error');
        }
    } catch (error) {
        console.error('Error saving task:', error);
        showNotification('Error saving task', 'error');
    }
}

/**
 * Edit task
 */
async function editTask(taskId) {
    try {
        const response = await apiRequest('GET', `/tasks/${taskId}`);
        const task = response.data;
        
        // Populate form
        document.getElementById('taskTitle').value = task.title;
        document.getElementById('taskDescription').value = task.description || '';
        document.getElementById('taskPriority').value = task.priority;
        document.getElementById('taskStatus').value = task.status;
        document.getElementById('taskDueDate').value = task.due_date || '';
        
        document.getElementById('taskModalTitle').textContent = 'Edit Task';
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('taskModal'));
        modal.show();
        
        // Store task ID for updating
        document.getElementById('taskForm').setAttribute('data-task-id', taskId);
    } catch (error) {
        console.error('Error loading task:', error);
        showNotification('Error loading task', 'error');
    }
}

/**
 * Delete task
 */
async function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        try {
            const response = await apiRequest('DELETE', `/tasks/${taskId}`);
            
            if (response.success) {
                await loadTasks();
                showNotification('Task deleted successfully!', 'success');
            } else {
                showNotification('Error deleting task: ' + response.message, 'error');
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            showNotification('Error deleting task', 'error');
        }
    }
}

/**
 * Filter tasks
 */
function filterTasks() {
    const statusFilter = document.getElementById('task-status-filter').value;
    const priorityFilter = document.getElementById('task-priority-filter').value;
    const searchFilter = document.getElementById('task-search').value.toLowerCase();
    
    let filteredTasks = tasks;
    
    if (statusFilter) {
        filteredTasks = filteredTasks.filter(task => task.status === statusFilter);
    }
    
    if (priorityFilter) {
        filteredTasks = filteredTasks.filter(task => task.priority === priorityFilter);
    }
    
    if (searchFilter) {
        filteredTasks = filteredTasks.filter(task => 
            task.title.toLowerCase().includes(searchFilter) ||
            (task.description && task.description.toLowerCase().includes(searchFilter))
        );
    }
    
    // Update tasks display with filtered results
    const originalTasks = tasks;
    tasks = filteredTasks;
    updateTasksTable();
    tasks = originalTasks;
}

/**
 * Clear task filters
 */
function clearTaskFilters() {
    document.getElementById('task-status-filter').value = '';
    document.getElementById('task-priority-filter').value = '';
    document.getElementById('task-search').value = '';
    updateTasksTable();
}

/**
 * Create new event
 */
function createEvent() {
    // Implementation for creating events
    showNotification('Event creation feature coming soon!', 'info');
}

/**
 * Sync data with Bitrix24
 */
async function syncData() {
    try {
        showNotification('Syncing with Bitrix24...', 'info');
        
        const response = await apiRequest('POST', '/bitrix24/sync');
        
        if (response.success) {
            await loadDashboardData();
            showNotification('Data synchronized successfully!', 'success');
        } else {
            showNotification('Sync failed: ' + response.message, 'error');
        }
    } catch (error) {
        console.error('Error syncing data:', error);
        showNotification('Error syncing data', 'error');
    }
}

/**
 * Open AI Assistant
 */
function openAIAssistant() {
    showSection('ai-assistant');
}

/**
 * Send message to AI Assistant
 */
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    
    // Clear input
    input.value = '';
    
    try {
        const response = await apiRequest('POST', '/ai/chat', { message });
        
        if (response.success) {
            addMessageToChat(response.data.response, 'assistant');
        } else {
            addMessageToChat('Sorry, I encountered an error. Please try again.', 'assistant');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        addMessageToChat('Sorry, I encountered an error. Please try again.', 'assistant');
    }
}

/**
 * Add message to chat
 */
function addMessageToChat(message, sender) {
    const container = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    
    messageElement.className = `mb-3 ${sender === 'user' ? 'text-end' : 'text-start'}`;
    messageElement.innerHTML = `
        <div class="d-inline-block p-3 rounded ${sender === 'user' ? 'bg-primary text-white' : 'bg-light'}">
            ${message}
        </div>
    `;
    
    container.appendChild(messageElement);
    container.scrollTop = container.scrollHeight;
}

/**
 * Load calendar
 */
async function loadCalendar() {
    // Implementation for loading calendar
    const container = document.getElementById('calendar-container');
    container.innerHTML = '<p class="text-center text-muted">Calendar loading...</p>';
}

/**
 * Load AI suggestions
 */
async function loadAISuggestions() {
    try {
        const response = await apiRequest('GET', '/ai/suggestions');
        
        if (response.success) {
            const container = document.getElementById('ai-suggestions');
            let html = '';
            
            response.data.forEach(suggestion => {
                html += `
                    <div class="card mb-2">
                        <div class="card-body">
                            <h6 class="card-title">${suggestion.title}</h6>
                            <p class="card-text">${suggestion.description}</p>
                            <button class="btn btn-sm btn-outline-primary" onclick="applySuggestion('${suggestion.id}')">
                                Apply
                            </button>
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html || '<p class="text-muted">No suggestions available</p>';
        }
    } catch (error) {
        console.error('Error loading AI suggestions:', error);
    }
}

/**
 * Apply AI suggestion
 */
async function applySuggestion(suggestionId) {
    try {
        const response = await apiRequest('POST', `/ai/suggestions/${suggestionId}/apply`);
        
        if (response.success) {
            showNotification('Suggestion applied successfully!', 'success');
            await loadAISuggestions();
        } else {
            showNotification('Error applying suggestion: ' + response.message, 'error');
        }
    } catch (error) {
        console.error('Error applying suggestion:', error);
        showNotification('Error applying suggestion', 'error');
    }
}

/**
 * Logout user
 */
function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/login.html';
}

/**
 * Get priority CSS class
 */
function getPriorityClass(priority) {
    switch (priority) {
        case 'urgent': return 'bg-danger';
        case 'high': return 'bg-warning';
        case 'medium': return 'bg-info';
        case 'low': return 'bg-secondary';
        default: return 'bg-secondary';
    }
}

/**
 * Get status CSS class
 */
function getStatusClass(status) {
    switch (status) {
        case 'completed': return 'bg-success';
        case 'in_progress': return 'bg-primary';
        case 'pending': return 'bg-warning';
        case 'cancelled': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

/**
 * Make API request
 */
async function apiRequest(method, endpoint, data = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = localStorage.getItem('access_token');
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

/**
 * Handle errors
 */
function handleError(error) {
    console.error('Application error:', error);
    showNotification('An error occurred. Please try again.', 'error');
}
