from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Response, Request


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 5):
        super().__init__(app)
        self.limit = limit
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        self.requests[client_ip] = self.requests.get(client_ip, 0) + 1

        if self.requests[client_ip] > self.limit:
            return Response("Too Many Requests", status_code=429)

        response = await call_next(request)
        return response
