from fastapi import FastAPI, HTTPException
from backend.store import weather_store
from backend.schemas import WeatherResponse
from backend.lru_cache import LRUCache


app = FastAPI()

cache = LRUCache(capacity=5)
# TODO: integrate LRU cache when lru_cache.py is completed

app = FastAPI(title="Memory Forecaster API")


@app.get("/cache")
def get_cache():
    return {"cache": cache.get_cache_state()}


@app.get("/")
def home():
    return {"message": "Memory Forecaster Weather API is running"}

@app.get("/weather/{city}", response_model=WeatherResponse)
def get_weather(city: str):

    city = city.lower()

    # Check cache first
    cached_data = cache.get(city)

    if cached_data:
        return WeatherResponse(
            city=city,
            temperature=cached_data["temperature"],
            condition=cached_data["condition"],
            source="cache"
        )

    # If not in cache → check store
    if city not in weather_store:
        raise HTTPException(status_code=404, detail="City not found")

    data = weather_store[city]

    # Save result in cache
    cache.put(city, data)

    return WeatherResponse(
        city=city,
        temperature=data["temperature"],
        condition=data["condition"],
        source="store"
    )