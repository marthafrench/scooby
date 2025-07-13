import redis
import json
import hashlib
from typing import Any, Optional
import structlog
from datetime import timedelta

logger = structlog.get_logger()


class CacheManager:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        logger.info("Connected to Redis", url=settings.REDIS_URL)

    def get_analysis_cache(self, app_id: str, log_hash: str, doc_hash: str) -> Optional[AIAnalysis]:
        """Get cached analysis result"""
        cache_key = self._generate_cache_key(app_id, log_hash, doc_hash)

        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                analysis_dict = json.loads(cached_data)
                logger.info("Cache hit", cache_key=cache_key)
                return AIAnalysis(**analysis_dict)

            logger.debug("Cache miss", cache_key=cache_key)
            return None

        except Exception as e:
            logger.error("Cache retrieval error", error=str(e), cache_key=cache_key)
            return None

    def set_analysis_cache(self, app_id: str, log_hash: str, doc_hash: str, analysis: AIAnalysis) -> None:
        """Cache analysis result"""
        cache_key = self._generate_cache_key(app_id, log_hash, doc_hash)

        try:
            # Convert to dict for JSON serialization
            analysis_dict = analysis.model_dump()
            # Handle datetime serialization
            analysis_dict['created_at'] = analysis_dict['created_at'].isoformat()

            self.redis_client.setex(
                cache_key,
                timedelta(seconds=settings.CACHE_TTL),
                json.dumps(analysis_dict, default=str)
            )

            logger.info("Cached analysis", cache_key=cache_key, ttl=settings.CACHE_TTL)

        except Exception as e:
            logger.error("Cache storage error", error=str(e), cache_key=cache_key)

    def _generate_cache_key(self, app_id: str, log_hash: str, doc_hash: str) -> str:
        """Generate cache key from inputs"""
        combined = f"{app_id}:{log_hash}:{doc_hash}"
        return f"scooby:analysis:{hashlib.md5(combined.encode()).hexdigest()}"

    def generate_content_hash(self, content: Any) -> str:
        """Generate hash for content (logs or docs)"""
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.md5(content_str.encode()).hexdigest()