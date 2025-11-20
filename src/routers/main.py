from fastapi import APIRouter, FastAPI

from .orders import router as orders_router
from .reports import router as reports_router

v1 = APIRouter(prefix="/api/v1")
v1.include_router(reports_router)
v1.include_router(orders_router)

root_router = APIRouter()
root_router.include_router(v1)


def setup_routers(app: FastAPI) -> None:
    app.include_router(root_router)
