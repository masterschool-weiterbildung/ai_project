import time
import logfire

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, public, protected_roles, protected_permissions, \
    protected_nurses
from app.routers import protected_user
from app.utility.logger import get_logger

app = FastAPI()

logfire.configure()

logfire.instrument_fastapi(app)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"],
)

logger = get_logger()

@app.middleware("http")
async def log_requests_and_add_process_time_header(request: Request,
                                                   call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    logger.info(
        "Handled {method} request to {url} with status {status_code} from {client} in {process_time:.2f}s",
        method=request.method,
        url=request.url.path,
        status_code=response.status_code,
        client=request.client.host,
        process_time=process_time
    )

    response.headers["X-Process-Time"] = str(process_time)

    return response


app.include_router(protected_user.router, prefix="/api",
                   tags=["Protected Users"])
app.include_router(protected_nurses.router, prefix="/api",
                   tags=["Protected Nurses"])
app.include_router(protected_roles.router, prefix="/api",
                   tags=["Protected Roles"])
app.include_router(auth.router,
                   tags=["Protected API Keys"])
app.include_router(protected_permissions.router, prefix="/api",
                   tags=["Protected Permissions"])
app.include_router(public.router, prefix="/public", tags=["Public"])
