from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router as api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="CareLens AI Backend API - EHR Insight Engine for Synthetic Patient Records",
    docs_url="/docs",
    redoc_url="/redoc"
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
