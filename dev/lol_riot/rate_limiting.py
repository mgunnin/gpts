from fastapi import Request, Response
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time


class RateLimiter(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests to the FastAPI server.
    This simplistic version uses an in-memory store to track request counts.
    For production use, consider integrating with a more robust solution like Redis.
    """

    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.rate_limit = calls
        self.period = period
        self.access_records = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        # Initialize or update the request count and timestamp for the client IP
        if client_ip not in self.access_records:
            self.access_records[client_ip] = [1, current_time]
        else:
            requests, timestamp = self.access_records[client_ip]
            if current_time - timestamp < self.period:
                if requests < self.rate_limit:
                    self.access_records[client_ip][0] += 1
                else:
                    # When rate limit is exceeded, return 429 Too Many Requests
                    return PlainTextResponse("Too Many Requests", status_code=429)
            else:
                # Reset the count and timestamp since the period has passed
                self.access_records[client_ip] = [1, current_time]

        response = await call_next(request)
        return response


# Example usage in main.py:
# from rate_limiting import RateLimiter
# app.add_middleware(RateLimiter, calls=100, period=60)
