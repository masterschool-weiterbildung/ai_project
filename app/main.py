import time
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, public
from app.routers import protected
from app.utility.logger import get_logger
from app.utility.middleware import RateLimitMiddleware


async def startup_event():
    print("Application is starting up ")


async def shutdown_event():
    print("Application is shutting down ")


app = FastAPI(on_startup=[startup_event], on_shutdown=[shutdown_event])

origins = [
    "http://localhost",
    "http://localhost:8080",
]

logger = get_logger()

# Logging Requests and Responses
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info({
        "method": request.method,
        "url": request.url.path,
        "status_code": response.status_code,
        "client": request.client.host,
    })

    return response


# GZip Middleware : Compresses responses to save bandwidth
app.add_middleware(GZipMiddleware,
                   minimum_size=1000)  # Compress responses > 1000 bytes

# CORS (Cross-Origin Resource Sharing) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"],
)

# Rate Limiting Middleware : Limits the number of requests per user/IP.
app.add_middleware(RateLimitMiddleware, limit=100)  # 10 requests per client


# Measures and adds the request processing time to the response headers
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Custom Header Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Custom-Header"] = "Hello from AI Backend"
    return response


app.include_router(auth.router)
app.include_router(protected.router, prefix="/api", tags=["Protected"])
app.include_router(public.router, prefix="/public", tags=["Public"])


@app.get("/")
async def root():
    return {"message": "Hello Fastapi"}
