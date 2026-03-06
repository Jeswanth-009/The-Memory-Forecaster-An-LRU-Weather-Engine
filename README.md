# The Memory Forecaster — LRU Weather Engine

A weather search application that demonstrates a custom-built **Least Recently Used (LRU) Cache**. Every city lookup either hits the in-memory cache (fast) or misses and fetches from the mock store (slow). The dashboard visualizes the cache state, hit/miss stats, and evictions in real time.

---

## 📂 Project Structure

```text
The-Memory-Forecaster-An-LRU-Weather-Engine/
├── backend/
│   ├── __init__.py          # Makes backend a proper Python package
│   ├── main.py              # FastAPI app — all API endpoints
│   ├── lru_cache.py         # Core LRU algorithm (HashMap + Doubly Linked List)
│   ├── schemas.py           # Pydantic response models
│   └── store.py             # Mock weather database (10 Indian cities)
├── frontend/
│   ├── index.html           # Main dashboard (requires login)
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── style.css            # Dashboard styles
│   ├── auth.css             # Login / register styles (JetBrains Mono + Bebas Neue)
│   └── app.js               # JS — API calls, live cache view, stats panel
├── static/                  # Mirror of frontend/ served by FastAPI (optional)
├── tests/
│   └── test_cache.py        # 26 unit + integration tests (pytest)
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🚀 Setup & Running

### 1. Clone & install

```bash
git clone https://github.com/Jeswanth-009/The-Memory-Forecaster-An-LRU-Weather-Engine.git
cd The-Memory-Forecaster-An-LRU-Weather-Engine
pip install -r requirements.txt
```

### 2. Start the backend

> **Run from the project root** (not from inside `backend/`):

```bash
uvicorn backend.main:app --reload
```

The API starts at `http://127.0.0.1:8000`.

### 3. Open the frontend

Open `frontend/login.html` in your browser.

**Demo credentials:** `admin` / `admin1234`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/weather/{city}` | Fetch weather — cache hit or miss |
| `GET` | `/cache` | Current LRU cache state (MRU → LRU order) |
| `DELETE` | `/cache/{city}` | Evict a single city from the cache |
| `DELETE` | `/cache` | Flush the entire cache |

### Cache Hit/Miss flow

```
GET /weather/mumbai
        │
   In LRU Cache?
   ┌────┴────┐
  YES        NO
   │          │
⚡ cache     ☁ miss → fetch from store
   │                  → insert into cache
   │                  → evict LRU if full (>5)
   └────┬────┘
  return WeatherResponse
  { city, temperature, condition, source }
```

---

## 🧠 LRU Cache — How It Works

Implemented in `backend/lru_cache.py` using a **HashMap + Doubly Linked List** for O(1) get, put, and delete.

- **Head** = Most Recently Used (MRU)
- **Tail** = Least Recently Used (LRU)
- Capacity: **5 cities**
- On every `get()` — the node is moved to the head
- On every `put()` — new node added at head; if over capacity, tail node is evicted

---

## 🖥️ Frontend Features

- **Auth guard** — session stored in `localStorage`; login/register with client-side user store
- **Search bar + quick-chips** — search any of the 10 cities
- **Weather result panel** — shows temperature, condition, and cache hit/miss badge
- **Live Cache View** — polls `GET /cache` every 5 seconds; shows MRU/LRU tags per slot
- **GET panel** — manually retrieve a city and see raw response
- **DELETE panel** — manually evict a city from the cache
- **Statistics panel** — total searches, cache hits, misses, evictions, hit rate %
- **Flush button** — clear the entire cache instantly

---

## 🧪 Running Tests

```bash
# From project root
python -m pytest tests/test_cache.py -v
```

**26 tests** covering:
- LRU basics: get, put, update
- Eviction order correctness
- Capacity limits
- Delete operations
- API endpoints: `/`, `/weather/{city}`, `/cache`, `DELETE /cache`, `DELETE /cache/{city}`
- Full cache hit → miss → eviction flows via API

---

## 🛠️ Bug Fixes Applied

| Area | Fix |
|------|-----|
| `backend/main.py` | Removed duplicate `app = FastAPI()` that was discarding the cache instance |
| `backend/main.py` | Added CORS middleware so the browser can call the API |
| `backend/main.py` | Added missing `DELETE /cache/{city}` and `DELETE /cache` endpoints |
| `backend/main.py` | Switched to relative imports (`.store`, `.schemas`, `.lru_cache`) so the server can be launched from the project root |
| `backend/__init__.py` | Created empty `__init__.py` to make `backend/` a proper Python package |
| `frontend/app.js` | Replaced `showWeatherModal()` (referenced non-existent `#modal` element) with `showWeatherResult()` that targets the actual `#weather-result-panel` |
| `frontend/app.js` | Added missing `closeWeatherResult()` function (called from HTML but was undefined) |
| `frontend/login.html` | Rewrote to use correct CSS class names matching `auth.css` (`.auth-card`, `.auth-wrapper`, `.btn-primary`, etc.) and correct Google Fonts |
| `frontend/register.html` | Same class name and font fixes as login; added eye-toggle buttons and proper strength bar structure |
| `requirements.txt` | Created with correct version pins to resolve `httpx` / `starlette` `TestClient` incompatibility |

