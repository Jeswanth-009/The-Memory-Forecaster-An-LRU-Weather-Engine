import pytest
from backend.lru_cache import LRUCache
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# ─────────────────────────────────────────────
# Unit Tests — LRUCache
# ─────────────────────────────────────────────

class TestLRUCacheBasics:
    def test_get_nonexistent_key_returns_none(self):
        cache = LRUCache(capacity=3)
        assert cache.get("mumbai") is None

    def test_put_and_get(self):
        cache = LRUCache(capacity=3)
        cache.put("mumbai", {"temperature": 31, "condition": "Humid"})
        result = cache.get("mumbai")
        assert result == {"temperature": 31, "condition": "Humid"}

    def test_update_existing_key(self):
        cache = LRUCache(capacity=3)
        cache.put("delhi", {"temperature": 30, "condition": "Haze"})
        cache.put("delhi", {"temperature": 25, "condition": "Clear"})
        result = cache.get("delhi")
        assert result["temperature"] == 25
        assert result["condition"] == "Clear"

    def test_cache_state_is_ordered_newest_to_oldest(self):
        cache = LRUCache(capacity=3)
        cache.put("chennai", {"temperature": 34, "condition": "Sunny"})
        cache.put("bangalore", {"temperature": 28, "condition": "Cloudy"})
        cache.put("mumbai", {"temperature": 31, "condition": "Humid"})
        assert cache.get_cache_state() == ["mumbai", "bangalore", "chennai"]

    def test_access_moves_node_to_front(self):
        cache = LRUCache(capacity=3)
        cache.put("chennai", {"temperature": 34, "condition": "Sunny"})
        cache.put("bangalore", {"temperature": 28, "condition": "Cloudy"})
        cache.put("mumbai", {"temperature": 31, "condition": "Humid"})
        # Access the oldest — it should move to front
        cache.get("chennai")
        assert cache.get_cache_state()[0] == "chennai"


class TestLRUCacheEviction:
    def test_evicts_least_recently_used_when_over_capacity(self):
        cache = LRUCache(capacity=3)
        cache.put("a", {"temperature": 20, "condition": "Clear"})
        cache.put("b", {"temperature": 21, "condition": "Clear"})
        cache.put("c", {"temperature": 22, "condition": "Clear"})
        cache.put("d", {"temperature": 23, "condition": "Clear"})  # should evict "a"
        assert cache.get("a") is None
        assert cache.get("d") is not None

    def test_evicts_correct_item_after_recent_access(self):
        cache = LRUCache(capacity=3)
        cache.put("a", {"temperature": 20, "condition": "Clear"})
        cache.put("b", {"temperature": 21, "condition": "Clear"})
        cache.put("c", {"temperature": 22, "condition": "Clear"})
        cache.get("a")  # "a" is now most recently used; "b" is now LRU
        cache.put("d", {"temperature": 23, "condition": "Clear"})  # should evict "b"
        assert cache.get("b") is None
        assert cache.get("a") is not None

    def test_capacity_never_exceeded(self):
        cache = LRUCache(capacity=5)
        cities = ["a", "b", "c", "d", "e", "f", "g"]
        for city in cities:
            cache.put(city, {"temperature": 30, "condition": "Clear"})
        assert len(cache.get_cache_state()) == 5


class TestLRUCacheDelete:
    def test_delete_existing_key(self):
        cache = LRUCache(capacity=3)
        cache.put("mumbai", {"temperature": 31, "condition": "Humid"})
        result = cache.delete("mumbai")
        assert result is True
        assert cache.get("mumbai") is None

    def test_delete_nonexistent_key_returns_false(self):
        cache = LRUCache(capacity=3)
        result = cache.delete("nonexistent")
        assert result is False

    def test_delete_updates_cache_state(self):
        cache = LRUCache(capacity=3)
        cache.put("chennai", {"temperature": 34, "condition": "Sunny"})
        cache.put("mumbai", {"temperature": 31, "condition": "Humid"})
        cache.delete("chennai")
        assert "chennai" not in cache.get_cache_state()
        assert "mumbai" in cache.get_cache_state()


class TestLRUCacheEdgeCases:
    def test_capacity_of_one(self):
        cache = LRUCache(capacity=1)
        cache.put("a", {"temperature": 20, "condition": "Clear"})
        cache.put("b", {"temperature": 21, "condition": "Clear"})
        assert cache.get("a") is None
        assert cache.get("b") is not None

    def test_empty_cache_state(self):
        cache = LRUCache(capacity=3)
        assert cache.get_cache_state() == []

    def test_put_same_key_does_not_grow_cache(self):
        cache = LRUCache(capacity=3)
        cache.put("mumbai", {"temperature": 31, "condition": "Humid"})
        cache.put("mumbai", {"temperature": 32, "condition": "Sunny"})
        cache.put("mumbai", {"temperature": 33, "condition": "Clear"})
        assert len(cache.get_cache_state()) == 1


# ─────────────────────────────────────────────
# Integration Tests — API Endpoints
# ─────────────────────────────────────────────

class TestAPIHealth:
    def test_home_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "Memory Forecaster" in response.json()["message"]

    def test_cache_endpoint_returns_list(self):
        response = client.get("/cache")
        assert response.status_code == 200
        assert "cache" in response.json()
        assert isinstance(response.json()["cache"], list)


class TestWeatherEndpoint:
    def test_valid_city_returns_200(self):
        response = client.get("/weather/mumbai")
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "mumbai"
        assert "temperature" in data
        assert "condition" in data
        assert data["source"] in ("cache", "store")

    def test_invalid_city_returns_404(self):
        response = client.get("/weather/atlantis")
        assert response.status_code == 404

    def test_city_is_case_insensitive(self):
        response1 = client.get("/weather/Mumbai")
        response2 = client.get("/weather/MUMBAI")
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["city"] == "mumbai"

    def test_first_request_comes_from_store(self):
        # Clear cache first to ensure a miss
        client.delete("/cache")
        response = client.get("/weather/chennai")
        assert response.json()["source"] == "store"

    def test_second_request_comes_from_cache(self):
        client.delete("/cache")
        client.get("/weather/bangalore")          # populates cache
        response = client.get("/weather/bangalore")  # should hit cache
        assert response.json()["source"] == "cache"

    def test_response_schema_has_all_fields(self):
        response = client.get("/weather/delhi")
        data = response.json()
        assert all(k in data for k in ["city", "temperature", "condition", "source"])


class TestCacheEndpoints:
    def test_delete_city_from_cache(self):
        client.get("/weather/kolkata")  # ensure it's cached
        response = client.delete("/cache/kolkata")
        assert response.status_code == 200

    def test_delete_nonexistent_city_from_cache_returns_404(self):
        client.delete("/cache")  # clear all
        response = client.delete("/cache/atlantis")
        assert response.status_code == 404

    def test_clear_entire_cache(self):
        client.get("/weather/mumbai")
        client.get("/weather/delhi")
        client.delete("/cache")
        response = client.get("/cache")
        assert response.json()["cache"] == []


class TestLRUEvictionViaAPI:
    def test_cache_evicts_lru_after_5_unique_cities(self):
        client.delete("/cache")
        cities = ["chennai", "bangalore", "mumbai", "delhi", "kolkata", "hyderabad"]
        for city in cities:
            client.get(f"/weather/{city}")
        cache_state = client.get("/cache").json()["cache"]
        assert len(cache_state) == 5
        assert "chennai" not in cache_state  # first in = first evicted