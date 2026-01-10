"""
cache_service.py - Redis caching service for performance optimization

Provides optional caching layer using Redis. If Redis is not available,
the system continues to work without caching (graceful degradation).

Cache Strategy:
- User Computations (30 min TTL): HR zones, readiness scores, overtraining risk
- Aggregations (1 hour TTL): Weekly/monthly statistics, trend calculations
- API Responses (5 min TTL): GET /api/v1/workouts, GET /api/v1/health-metrics
- Device Sync (2 hour TTL): Garmin availability status, last sync timestamp
"""

import json
import logging
from typing import Any, Optional, Callable
from functools import wraps

try:
    from redis import Redis
    from redis.exceptions import ConnectionError, RedisError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis caching service with graceful degradation."""

    def __init__(self):
        """Initialize Redis client if available."""
        self.client: Optional[Redis] = None
        self.enabled = False

        if not REDIS_AVAILABLE:
            logger.warning("Redis package not installed. Caching disabled.")
            return

        try:
            # Build Redis URL from config
            redis_url = settings.redis_url
            if not redis_url:
                redis_url = f"redis://{settings.redis_host}:{settings.redis_port}/1"
                # Use database 1 for caching (database 0 is for Celery)

            self.client = Redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.client.ping()
            self.enabled = True
            logger.info(f"Redis cache enabled: {redis_url}")
        except (ConnectionError, RedisError, Exception) as e:
            logger.warning(f"Redis connection failed. Caching disabled: {e}")
            self.client = None
            self.enabled = False

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists, None otherwise
        """
        if not self.enabled or not self.client:
            return None

        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except (json.JSONDecodeError, RedisError) as e:
            logger.warning(f"Error reading cache key {key}: {e}")
            return None

    def set(
        self, key: str, value: Any, ttl_seconds: int = 3600
    ) -> bool:
        """Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl_seconds: Time to live in seconds (default: 1 hour)

        Returns:
            True if cached successfully, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            serialized = json.dumps(value, default=str)  # default=str handles datetime
            self.client.setex(key, ttl_seconds, serialized)
            return True
        except (TypeError, RedisError) as e:
            logger.warning(f"Error caching key {key}: {e}")
            return False

    def invalidate(self, key: str) -> bool:
        """Invalidate a single cache key.

        Args:
            key: Cache key to invalidate

        Returns:
            True if invalidated successfully, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            self.client.delete(key)
            return True
        except RedisError as e:
            logger.warning(f"Error invalidating cache key {key}: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern.

        Args:
            pattern: Pattern to match (e.g., "user:123:*")

        Returns:
            Number of keys invalidated
        """
        if not self.enabled or not self.client:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except RedisError as e:
            logger.warning(f"Error invalidating cache pattern {pattern}: {e}")
            return 0

    def clear(self) -> bool:
        """Clear all cache (use with caution!).

        Returns:
            True if cleared successfully, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            self.client.flushdb()  # Only clear current database (1), not Celery (0)
            logger.warning("Cache cleared!")
            return True
        except RedisError as e:
            logger.error(f"Error clearing cache: {e}")
            return False


# Singleton instance
_cache_service_instance: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or create cache service singleton."""
    global _cache_service_instance
    if _cache_service_instance is None:
        _cache_service_instance = CacheService()
    return _cache_service_instance


def cache_result(
    key_prefix: str, ttl_seconds: int = 3600, key_builder: Optional[Callable] = None
):
    """Decorator to cache function results.

    Args:
        key_prefix: Prefix for cache key
        ttl_seconds: Time to live in seconds
        key_builder: Optional function to build cache key from function args

    Example:
        @cache_result("user_stats", ttl_seconds=1800)
        def get_user_stats(user_id: int):
            # Expensive computation
            return stats
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_service()

            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default: use function name and args
                key_parts = [key_prefix, func.__name__]
                if args:
                    key_parts.extend(str(arg) for arg in args)
                if kwargs:
                    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)

            # Try to get from cache
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached

            # Compute result
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, ttl_seconds)

            return result

        return wrapper
    return decorator
