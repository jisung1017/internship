from fastapi import FastAPI
from src.interface.api.routers import router

app = FastAPI(
    title="Cafe Mini Kiosk API",
    description="Architecture 3-Tier Kiosk API Server",
    version="1.0.0",
)

app.include_router(router)