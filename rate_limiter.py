import time
from typing import Optional
import structlog

logger = structlog.get_logger()


class RateLimiter:
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager.redis_client

    def is_allowed(self, identifier: str, max_requests: int = None, window_seconds: int = None) -> bool:
        """Check if request is within rate limits"""
        max_requests = max_requests or settings.RATE_LIMIT_REQUESTS
        window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW

        key = f"rate_limit:{identifier}"
        current_time = int(time.time())
        window_start = current_time - window_seconds

        try:
            # Remove expired entries
            self.cache.zremrangebyscore(key, 0, window_start)

            # Count current requests in window
            current_count = self.cache.zcard(key)

            if current_count >= max_requests:
                logger.warning("Rate limit exceeded", identifier=identifier, count=current_count)
                return False

            # Add current request
            self.cache.zadd(key, {str(current_time): current_time})
            self.cache.expire(key, window_seconds)

            return True

        except Exception as e:
            logger.error("Rate limiter error", error=str(e))
            return True  # Fail open

    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for identifier"""
        key = f"rate_limit:{identifier}"
        window_seconds = settings.RATE_LIMIT_WINDOW
        current_time = int(time.time())
        window_start = current_time - window_seconds

        try:
            # Clean expired entries
            self.cache.zremrangebyscore(key, 0, window_start)
            current_count = self.cache.zcard(key)

            return max(0, settings.RATE_LIMIT_REQUESTS - current_count)

        except Exception as e:
            logger.error("Error getting remaining requests", error=str(e))
            return settings.RATE_LIMIT_REQUESTS
