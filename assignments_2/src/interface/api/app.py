from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.domain.exceptions import OutOfStockError, PaymentFailedError
from src.interface.api.routers import admin_router, kiosk_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Cafe Mini Kiosk API",
    description="Clean Architecture 3-Tier Kiosk API Server",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(kiosk_router)
app.include_router(admin_router)


@app.exception_handler(OutOfStockError)
def out_of_stock_exception_handler(request: Request, exc: OutOfStockError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )

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