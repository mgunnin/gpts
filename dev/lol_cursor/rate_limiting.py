import time
from typing import Dict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests to the FastAPI application.
    """
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.rate_limit = calls
        self.period = period
        self.requests: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Filter out requests outside of the current period
        self.requests[client_ip] = [req_time for req_time in self.requests[client_ip] if current_time - req_time < self.period]

        if len(self.requests[client_ip]) < self.rate_limit:
            self.requests[client_ip].append(current_time)
            response = await call_next(request)
        else:
            # Too many requests
            response = Response(content="Rate limit exceeded. Try again later.", status_code=429)

        return response

def setup_rate_limiting(app):
    """
    Function to add the rate limiting middleware to the FastAPI application.
    """
    # You can adjust the calls and period parameters based on your needs or make them configurable
    app.add_middleware(RateLimiter, calls=100, period=60)
