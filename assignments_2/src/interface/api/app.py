from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import OutOfStockError, PaymentFailedError
from src.interface.api.routers import admin_router, kiosk_router

app = FastAPI(
    title="Cafe Mini Kiosk API",
    description="Clean Architecture 3-Tier Kiosk API Server",
    version="1.0.0",
)

# 라우터 등록
app.include_router(kiosk_router)
app.include_router(admin_router)


@app.exception_handler(OutOfStockError)
@app.exception_handler(PaymentFailedError)
@app.exception_handler(ValueError)
def domain_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )

@app.get("/")
def root():
    return {"message": "Cafe Mini Kiosk API에 오신 것을 환영합니다! /docs 로 이동하여 API를 확인하세요."}