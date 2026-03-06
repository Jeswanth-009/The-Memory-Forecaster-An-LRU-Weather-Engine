from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .store import weather_store
from .schemas import WeatherResponse
from .lru_cache import LRUCache


app = FastAPI(title="Memory Forecaster API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = LRUCache(capacity=5)


@app.get("/cache")
def get_cache():
    return {"cache": cache.get_cache_state()}


@app.get("/cache/{city}")
def get_from_cache(city: str):
    city = city.lower()
    data = cache.get(city)
    if data is None:
        raise HTTPException(status_code=404, detail=f"'{city}' is not in the cache")
    return {"city": city, "temperature": data["temperature"], "condition": data["condition"], "source": "cache"}


@app.delete("/cache/{city}")
def delete_from_cache(city: str):
    city = city.lower()
    removed = cache.delete(city)
    if not removed:
        raise HTTPException(status_code=404, detail=f"'{city}' is not in the cache")
    return {"message": f"'{city}' removed from cache"}


@app.delete("/cache")
def flush_cache():
    keys = cache.get_cache_state()
    for key in keys:
        cache.delete(key)
    return {"message": "Cache cleared", "removed": keys}


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