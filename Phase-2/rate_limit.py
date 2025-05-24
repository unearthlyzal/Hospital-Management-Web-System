from flask import request, jsonify
from functools import wraps
import time
from collections import defaultdict
import threading

class RateLimiter:
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, key):
        """Check if request is allowed based on rate limit"""
        now = time.time()
        minute_ago = now - 60

        with self.lock:
            # Clean old requests
            self.requests[key] = [req_time for req_time in self.requests[key] 
                                if req_time > minute_ago]
            
            # Check if limit is reached
            if len(self.requests[key]) >= self.requests_per_minute:
                return False
            
            # Add new request
            self.requests[key].append(now)
            return True

# Create rate limiter instance
limiter = RateLimiter()

def rate_limit(f):
    """Decorator to apply rate limiting"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get client identifier (IP address or token)
        key = request.headers.get('Authorization') or request.remote_addr
        
        if not limiter.is_allowed(key):
            response = {
                'message': 'Rate limit exceeded. Please try again later.',
                'status': 'error'
            }
            return jsonify(response), 429
        
        return f(*args, **kwargs)
    return decorated 