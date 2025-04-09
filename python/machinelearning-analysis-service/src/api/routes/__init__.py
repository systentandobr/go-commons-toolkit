from fastapi import APIRouter

from .analyze import router as analyze_router
from .models import router as models_router

api_router = APIRouter()

api_router.include_router(analyze_router)
api_router.include_router(models_router)
