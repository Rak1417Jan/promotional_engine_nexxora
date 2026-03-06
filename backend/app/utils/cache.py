"""
Redis Cache Utilities
"""
from typing import Optional, Any
import json
from app.database import get_redis
from app.config import settings


class Cache:
    """Cache utility class"""
    
    def __init__(self):
        self.redis = get_redis()
        if self.redis is None:
            print("Warning: Redis not available. Caching disabled.")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            # Log error but don't fail
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            serialized = json.dumps(value)
            return self.redis.setex(key, ttl, serialized)
        except Exception as e:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            return False


# Cache TTLs (in seconds)
CACHE_TTL = {
    "player_profile": 3600,  # 1 hour
    "recommendations": 900,  # 15 minutes
    "segment_membership": 1800,  # 30 minutes
    "campaign_template": 86400,  # 24 hours
    "attribution": 3600,  # 1 hour
}

