"""
Rate limiting middleware to prevent abuse and runaway costs
"""
from fastapi import Request, HTTPException
from typing import Dict
from datetime import datetime, timedelta
import threading

# Simple in-memory rate limiter (use Redis in production)
_rate_limit_store: Dict[str, Dict[str, any]] = {}
_rate_limit_lock = threading.Lock()

# Rate limits (requests per time window)
RATE_LIMITS = {
    '/optimize': {'max_requests': 10, 'window_seconds': 60},  # 10 per minute
    '/analyze': {'max_requests': 20, 'window_seconds': 60},  # 20 per minute
    '/generate-roads': {'max_requests': 20, 'window_seconds': 60},
    '/upload': {'max_requests': 5, 'window_seconds': 60},  # 5 per minute
}


def check_rate_limit(request: Request) -> bool:
    """
    Check if request is within rate limit
    
    Returns:
        True if allowed, False if rate limited
    """
    path = request.url.path
    client_ip = request.client.host if request.client else 'unknown'
    
    # Get rate limit config for this endpoint
    limit_config = None
    for endpoint, config in RATE_LIMITS.items():
        if endpoint in path:
            limit_config = config
            break
    
    if not limit_config:
        return True  # No rate limit for this endpoint
    
    max_requests = limit_config['max_requests']
    window_seconds = limit_config['window_seconds']
    
    # Get or create rate limit entry
    key = f"{client_ip}:{path}"
    
    with _rate_limit_lock:
        now = datetime.now()
        
        if key not in _rate_limit_store:
            _rate_limit_store[key] = {
                'requests': [],
                'window_start': now
            }
        
        entry = _rate_limit_store[key]
        
        # Remove requests outside the window
        window_start = now - timedelta(seconds=window_seconds)
        entry['requests'] = [
            req_time for req_time in entry['requests']
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(entry['requests']) >= max_requests:
            return False
        
        # Add current request
        entry['requests'].append(now)
        return True


def get_rate_limit_info(request: Request) -> Dict[str, any]:
    """Get rate limit information for debugging"""
    path = request.url.path
    client_ip = request.client.host if request.client else 'unknown'
    key = f"{client_ip}:{path}"
    
    limit_config = None
    for endpoint, config in RATE_LIMITS.items():
        if endpoint in path:
            limit_config = config
            break
    
    if not limit_config:
        return {'limited': False}
    
    with _rate_limit_lock:
        if key not in _rate_limit_store:
            return {
                'limited': False,
                'remaining': limit_config['max_requests'],
                'limit': limit_config['max_requests']
            }
        
        entry = _rate_limit_store[key]
        now = datetime.now()
        window_start = now - timedelta(seconds=limit_config['window_seconds'])
        entry['requests'] = [
            req_time for req_time in entry['requests']
            if req_time > window_start
        ]
        
        remaining = limit_config['max_requests'] - len(entry['requests'])
        
        return {
            'limited': remaining <= 0,
            'remaining': max(0, remaining),
            'limit': limit_config['max_requests'],
            'reset_in_seconds': limit_config['window_seconds']
        }

