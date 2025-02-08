from fastapi import FastAPI, Response

from app.routers import user


async def startup_event():
    print("Application is starting up ")


async def shutdown_event():
    print("Application is shutting down ")

app = FastAPI(on_startup=[startup_event], on_shutdown=[shutdown_event])

app.include_router(user.router)

@app.get("/")
async def root():
    return {"message": "Hello Fastapi"}
