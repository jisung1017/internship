from fastapi import FastAPI
from src.interface.api.routers import admin_router, kiosk_router

app = FastAPI(
    title="Cafe Mini Kiosk API",
    description="Clean Architecture 3-Tier Kiosk API Server",
    version="1.0.0",
)

# 라우터 등록
app.include_router(kiosk_router)
app.include_router(admin_router)