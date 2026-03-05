// --- DOM Element Selectors ---
const weatherForm = document.getElementById('weather-form');
const cityInput = document.getElementById('city-input');
const statusBadgeContainer = document.getElementById('status-badge-container');
const cityNameEl = document.getElementById('city-name');
const weatherConditionEl = document.getElementById('weather-condition');
const temperatureEl = document.getElementById('temperature');
const errorMessageEl = document.getElementById('error-message');
const cacheListEl = document.getElementById('cache-list');

const API_BASE_URL = 'http://127.0.0.1:8000';

// --- Event Listeners ---
weatherForm.addEventListener('submit', handleWeatherSearch);

// --- Functions ---

/**
 * Handles the weather search form submission.
 * @param {Event} e - The form submission event.
 */
async function handleWeatherSearch(e) {
    e.preventDefault();
    const city = cityInput.value.trim();
    if (!city) return;

    // Reset UI for new search
    resetUIState();

    try {
        const response = await fetch(`${API_BASE_URL}/weather/${city}`);
        const data = await response.json();

        if (!response.ok) {
            // Handle HTTP errors like 404 (Not Found) or 422 (Validation Error)
            throw new Error(data.detail || `An error occurred: ${response.statusText}`);
        }

        // Update UI with successful response
        updateUI(data);

    } catch (error) {
        displayError(error.message);
    }
}

/**
 * Updates the entire UI based on the API response data.
 * @param {object} data - The weather data from the API.
 */
function updateUI(data) {
    // Update weather card
    cityNameEl.textContent = data.city;
    weatherConditionEl.textContent = data.weather.condition;
    temperatureEl.textContent = `${data.weather.temp}°C`;
    weatherConditionEl.classList.remove('subtle-text');

    // Update weather icon
    updateWeatherIcon(data.weather.condition);

    // Update cache status badge
    updateStatusBadge(data.cache_hit);

    // Update cache memory list
    updateCacheList(data.cache_state);

    // Update background based on weather condition
    updateBackground(data.weather.condition);
}

/**
 * Displays a cache hit or miss badge.
 * @param {boolean} isHit - Whether the request was a cache hit.
 */
function updateStatusBadge(isHit) {
    const badge = document.createElement('span');
    badge.classList.add('badge');

    if (isHit) {
        badge.textContent = '⚡ Cache Hit';
        badge.classList.add('cache-hit');
    } else {
        badge.textContent = '☁️ Cache Miss';
        badge.classList.add('cache-miss');
    }
    statusBadgeContainer.appendChild(badge);
}

/**
 * Renders the list of items currently in the cache.
 * @param {Array} cacheState - The array of [key, value] pairs from the cache.
 */
function updateCacheList(cacheState) {
    cacheListEl.innerHTML = ''; // Clear previous list

    if (cacheState.length === 0) {
        const placeholder = document.createElement('li');
        placeholder.className = 'cache-item-placeholder';
        placeholder.textContent = 'Cache is empty.';
        cacheListEl.appendChild(placeholder);
        return;
    }

    cacheState.forEach(item => {
        const [city, weather] = item;
        const li = document.createElement('li');
        li.textContent = `${city} (${weather.temp}°C, ${weather.condition})`;
        cacheListEl.appendChild(li);
    });
}

/**
 * Updates the background gradient based on the weather condition.
 * @param {string} condition - The weather condition (e.g., "Sunny", "Rainy").
 */
function updateBackground(condition) {
    // Remove previous theme classes
    document.body.className = document.body.className.replace(/\b\w+-theme\b/g, '').trim();
    
    // Add new theme class
    const themeClass = condition.toLowerCase().replace(/\s+/g, '-') + '-theme';
    document.body.classList.add(themeClass);
}

/**
 * Updates the weather icon based on the condition.
 * @param {string} condition - The weather condition.
 */
function updateWeatherIcon(condition) {
    const icons = {
        "Sunny": "☀️",
        "Clear": "🌞",
        "Partly Cloudy": "⛅",
        "Cloudy": "☁️",
        "Rainy": "🌧️",
        "Thunderstorms": "⛈️",
        "Snowing": "❄️",
        "Windy": "💨",
        "Hazy": "🌫️",
        "Monsoon": "🌦️",
        "Very Hot": "🔥",
        "Humid": "💧",
        "Mild": "🌤️"
    };
    const defaultIcon = "🌤️";
    const iconEl = document.getElementById('weather-icon');
    if (iconEl) {
        iconEl.textContent = icons[condition] || defaultIcon;
    }
}

/**
 * Displays an error message on the weather card and resets its content.
 * @param {string} message - The error message to display.
 */
function displayError(message) {
    cityNameEl.textContent = 'Error';
    weatherConditionEl.textContent = 'Could not retrieve data.';
    weatherConditionEl.classList.add('subtle-text');
    temperatureEl.textContent = '--°C';
    errorMessageEl.textContent = message;
}

/**
 * Resets the UI to its initial state before a new search.
 */
function resetUIState() {
    errorMessageEl.textContent = '';
    statusBadgeContainer.innerHTML = '';
}

// --- Todo Functionality ---
const todoForm = document.getElementById('todo-form');
const todoInput = document.getElementById('todo-input');
const todoList = document.getElementById('todo-list');

todoForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = todoInput.value.trim();
    if (!title) return;

    try {
        const response = await fetch(`${API_BASE_URL}/todos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title })
        });
        if (response.ok) {
            todoInput.value = '';
            loadTodos();
        }
    } catch (error) {
        console.error('Error adding todo:', error);
    }
});

async function loadTodos() {
    try {
        const response = await fetch(`${API_BASE_URL}/todos`);
        const todos = await response.json();
        renderTodos(todos);
    } catch (error) {
        console.error('Error loading todos:', error);
    }
}

function renderTodos(todos) {
    todoList.innerHTML = '';
    todos.forEach(todo => {
        const li = document.createElement('li');
        li.innerHTML = `
            <input type="checkbox" ${todo.completed ? 'checked' : ''} onchange="toggleTodo(${todo.id}, this.checked)">
            <span class="todo-text ${todo.completed ? 'completed' : ''}">${todo.title}</span>
            <button onclick="deleteTodo(${todo.id})">×</button>
        `;
        todoList.appendChild(li);
    });
}

async function toggleTodo(id, completed) {
    try {
        await fetch(`${API_BASE_URL}/todos/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed })
        });
        loadTodos();
    } catch (error) {
        console.error('Error updating todo:', error);
    }
}

async function deleteTodo(id) {
    try {
        await fetch(`${API_BASE_URL}/todos/${id}`, {
            method: 'DELETE'
        });
        loadTodos();
    } catch (error) {
        console.error('Error deleting todo:', error);
    }
}

// Load todos on page load
document.addEventListener('DOMContentLoaded', loadTodos);