from fastapi import APIRouter
from app.routes.auth_routes import router as auth_router

router = APIRouter()

router.include_router(auth_router)

app_routes = router
