# The-Memory-Forecaster-An-LRU-Weather-Engine
This project demonstrates a highly efficient, custom-built Least Recently Used (LRU) Cache integrated into a weather search application. It validates incoming requests using Pydantic and visualizes the cache memory in real-time.

## 📂 Project Structure & File Assignments

We are dividing this project into distinct files to avoid Git merge conflicts. Please only work in your assigned files!

```text
memory_forecaster/
├── backend/
│   ├── main.py              # (Person 2 & 4) API endpoints and server setup
│   ├── lru_cache.py         # (Person 1) Core LRU algorithm
│   ├── schemas.py           # (Person 2) Pydantic validation models
│   ├── store.py             # (Person 2) Mock database/dictionary of weather data
├── frontend/
│   ├── index.html           # (Person 3) Webpage layout
│   ├── style.css            # (Person 3) Visual styling
│   ├── app.js               # (Person 4) JavaScript fetch calls & UI updates
├── tests/
│   ├── test_cache.py        # (Person 1 & 4) Unit and integration tests
├── README.md                
├── requirements.txt         # Python dependencies (FastAPI, Uvicorn, Pydantic)

```

## 👨‍💻 Team Responsibilities

### Person 1: Core Algorithm Engineer

**Your Files:** `backend/lru_cache.py` and `tests/test_cache.py`

* Build the `Node` and `LRUCache` classes.
* Implement a Hash Map + Doubly Linked List for $O(1)$ operations.
* Methods required: `get(key)`, `put(key, value)`, `delete(key)`, and `get_cache_state()`.
* Ensure capacity limits correctly evict the least recently used item.

### Person 2: Backend API & Data Engineer

**Your Files:** `backend/main.py`, `backend/schemas.py`, and `backend/store.py`

* **`store.py`:** Create a static dictionary of 15-20 cities with mock weather data (temp, condition).
* **`schemas.py`:** Build Pydantic classes to validate city search requests and format the outgoing JSON responses.
* **`main.py`:** Initialize the FastAPI/Flask app, import Person 1's cache, and build the `GET /weather/{city}` route featuring the "Read-Through" cache logic.

### Person 3: Frontend UI Developer

**Your Files:** `frontend/index.html` and `frontend/style.css`

* Build a clean, modern search interface.
* Create a central "Weather Card" to display temperature and conditions.
* Create a "Cache Memory Sidebar" to visually list the cities currently held in the backend's LRU cache.
* Create visual badges for "⚡ Cache Hit" and "☁️ Cache Miss".

### Person 4: Integration & QA Engineer

**Your Files:** `frontend/app.js`, `backend/main.py` (assisting), and `tests/test_cache.py`

* **`app.js`:** Write the JavaScript to connect Person 3's UI to Person 2's API.
* Handle form submissions, fetch weather data, and update the DOM.
* Ensure the UI gracefully handles API error codes (e.g., 404 City Not Found, 422 Validation Error).
* Write integration tests simulating full user flows.

## 🚀 Setup Instructions

1. Clone the repository: `git clone <repo-url>`
2. Navigate to the folder: `cd memory_forecaster`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the backend server: `uvicorn backend.main:app --reload`
5. Open `frontend/index.html` in your web browser.

```

```
