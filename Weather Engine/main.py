
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List

from lru_cache import LRUCache
from store import MOCK_WEATHER_DATA
from schemas import WeatherResponse, WeatherData, TodoItem, TodoCreate, TodoUpdate

# --- App and Cache Initialization ---

app = FastAPI(
    title="The Memory Forecaster",
    description="A weather app demonstrating a custom LRU Cache.",
    version="1.0.0",
)

# Allow CORS for the frontend to communicate with the backend.
# In a production environment, you would restrict this to your frontend's domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the LRU Cache with a capacity of 5.
# This small size is for demonstration purposes to easily see evictions.
weather_cache = LRUCache(capacity=5)

# In-memory todo list
todos = {}
next_id = 1


# --- API Endpoints ---

@app.get("/weather/{city}", response_model=WeatherResponse)
async def get_weather(city: str):
    """
    Retrieves weather data for a given city.

    This endpoint implements a "Read-Through" caching strategy:
    1. It first checks the LRU cache for the city's weather data.
    2. If it's a **Cache Hit**, it returns the data from the cache.
    3. If it's a **Cache Miss**, it fetches the data from the mock store,
       adds it to the cache, and then returns it.
    """
    normalized_city = city.lower().strip()
    cache_hit = True

    # 1. Check the cache first
    weather_data = weather_cache.get(normalized_city)

    # 2. Cache Miss: Fetch from the "database" (mock store)
    if weather_data is None:
        cache_hit = False
        if normalized_city not in MOCK_WEATHER_DATA:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found.")

        data_from_store = MOCK_WEATHER_DATA[normalized_city]
        weather_data = WeatherData(**data_from_store)

        # 3. Put the newly fetched data into the cache
        weather_cache.put(normalized_city, weather_data)

    # 4. Prepare and return the response including the full cache state
    return WeatherResponse(
        city=normalized_city.title(),
        weather=weather_data,
        cache_hit=cache_hit,
        cache_state=weather_cache.get_cache_state(),
    )

@app.post("/weather", response_model=WeatherResponse)
async def add_weather(city: str, weather: WeatherData):
    """
    Adds or updates weather data for a city in the store and cache.
    """
    normalized_city = city.lower().strip()
    cache_hit = normalized_city in [item[0] for item in weather_cache.get_cache_state()]

    # Update the store
    MOCK_WEATHER_DATA[normalized_city] = weather.dict()

    # Update the cache
    weather_cache.put(normalized_city, weather)

    return WeatherResponse(
        city=normalized_city.title(),
        weather=weather,
        cache_hit=cache_hit,
        cache_state=weather_cache.get_cache_state(),
    )

# --- Todo API Endpoints ---

@app.get("/todos", response_model=List[TodoItem])
async def get_todos():
    """Get all todos."""
    return list(todos.values())

@app.post("/todos", response_model=TodoItem)
async def create_todo(todo: TodoCreate):
    """Create a new todo."""
    global next_id
    item = TodoItem(id=next_id, title=todo.title)
    todos[next_id] = item
    next_id += 1
    return item

@app.put("/todos/{todo_id}", response_model=TodoItem)
async def update_todo(todo_id: int, todo: TodoUpdate):
    """Update a todo."""
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    item = todos[todo_id]
    if todo.title is not None:
        item.title = todo.title
    if todo.completed is not None:
        item.completed = todo.completed
    return item

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """Delete a todo."""
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    del todos[todo_id]
    return {"message": "Todo deleted"}

# Serve static files (HTML, CSS, JS)
app.mount("/", StaticFiles(directory=".", html=True), name="static")