from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.http_client import close_http_client
from app.api.routes import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_http_client()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="CareLens AI Backend API - EHR Insight Engine for Synthetic Patient Records",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure explicit CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API v{settings.API_VERSION}",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", settings.PORT))
    is_dev = settings.APP_ENV == "development"
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=is_dev)
