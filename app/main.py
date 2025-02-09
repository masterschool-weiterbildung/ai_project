from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from pydantic import BaseModel

from app.routers import user
from app.routers import auth
from app.routers import protected


async def startup_event():
    print("Application is starting up ")


async def shutdown_event():
    print("Application is shutting down ")


app = FastAPI(on_startup=[startup_event], on_shutdown=[shutdown_event])

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(protected.router, prefix="/api", tags=["Protected"])


@app.get("/")
async def root():
    return {"message": "Hello Fastapi"}
