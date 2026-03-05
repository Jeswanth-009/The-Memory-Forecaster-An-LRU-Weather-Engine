from pydantic import BaseModel, Field
from typing import List, Tuple

class WeatherData(BaseModel):
    """Internal representation of weather data."""
    temp: int
    condition: str

class WeatherResponse(BaseModel):
    """
    The response model for a weather query.
    Includes the weather data and information about the cache hit/miss.
    """
    city: str
    weather: WeatherData
    cache_hit: bool = Field(..., description="True if the data was served from the cache.")
    cache_state: List[Tuple[str, WeatherData]] = Field(..., description="Current state of the LRU cache (most to least recent).")

class TodoItem(BaseModel):
    """A single todo item."""
    id: int
    title: str
    completed: bool = False

class TodoCreate(BaseModel):
    """Model for creating a new todo."""
    title: str

class TodoUpdate(BaseModel):
    """Model for updating a todo."""
    title: str = None
    completed: bool = None