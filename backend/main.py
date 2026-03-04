from fastapi import FastAPI, HTTPException
from backend.store import weather_store
from backend.schemas import WeatherResponse

# TODO: integrate LRU cache when lru_cache.py is completed

app = FastAPI(title="Memory Forecaster API")


@app.get("/")
def home():
    return {"message": "Memory Forecaster Weather API is running"}

@app.get("/weather/{city}", response_model=WeatherResponse)
def get_weather(city: str):

    city = city.lower()

    # Check if city exists in our store
    if city not in weather_store:
        raise HTTPException(status_code=404, detail="City not found")

    data = weather_store[city]

    return WeatherResponse(
        city=city,
        temperature=data["temperature"],
        condition=data["condition"],
        source="store"
    )