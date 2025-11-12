"""
Caching utilities for expensive operations (AI calls, regulatory data, terrain analysis)
"""
import hashlib
import json
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import functools
import threading

# In-memory cache (for demo - use Redis in production)
_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.Lock()

# Cache TTLs (in seconds)
CACHE_TTL_AI = 3600  # 1 hour for AI responses
CACHE_TTL_REGULATORY = 86400  # 24 hours for regulatory data (changes rarely)
CACHE_TTL_TERRAIN = 86400  # 24 hours for terrain analysis


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key from arguments"""
    # Create a stable string representation
    key_data = {
        'prefix': prefix,
        'args': args,
        'kwargs': sorted(kwargs.items()) if kwargs else {}
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return f"{prefix}:{hashlib.sha256(key_str.encode()).hexdigest()[:16]}"


def get_cached(key: str) -> Optional[Any]:
    """Get value from cache if not expired"""
    with _cache_lock:
        if key in _cache:
            entry = _cache[key]
            if datetime.now() < entry['expires_at']:
                return entry['value']
            else:
                # Expired, remove it
                del _cache[key]
        return None


def set_cached(key: str, value: Any, ttl: int = CACHE_TTL_AI):
    """Set value in cache with TTL"""
    with _cache_lock:
        _cache[key] = {
            'value': value,
            'expires_at': datetime.now() + timedelta(seconds=ttl),
            'created_at': datetime.now()
        }


def clear_cache(prefix: Optional[str] = None):
    """Clear cache entries (optionally by prefix)"""
    with _cache_lock:
        if prefix:
            keys_to_remove = [k for k in _cache.keys() if k.startswith(prefix)]
            for k in keys_to_remove:
                del _cache[k]
        else:
            _cache.clear()


def cached(ttl: int = CACHE_TTL_AI, key_prefix: str = "cache"):
    """Decorator to cache function results"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = generate_cache_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )
            
            # Check cache
            cached_value = get_cached(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            set_cached(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    with _cache_lock:
        total_entries = len(_cache)
        expired_entries = sum(
            1 for entry in _cache.values()
            if datetime.now() >= entry['expires_at']
        )
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries
        }

