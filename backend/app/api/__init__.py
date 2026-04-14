from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.news import router as news_router
from app.api.matches import router as matches_router
from app.api.rankings import router as rankings_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(news_router)
api_router.include_router(matches_router)
api_router.include_router(rankings_router)
