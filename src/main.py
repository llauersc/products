from contextlib import asynccontextmanager

import inject
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from infrastructure.repositories.orders import OrdersRepository
from routers.main import setup_routers
from settings import settings
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from utils.db import SessionMaker


def config(binder: inject.Binder):
    engine: AsyncEngine = create_async_engine(url=settings.url)
    binder.bind(AsyncEngine, engine)

    session_maker = SessionMaker(engine)
    binder.bind(SessionMaker, session_maker)

    orders_repository = OrdersRepository(session_maker=session_maker)
    binder.bind(OrdersRepository, orders_repository)


@asynccontextmanager
async def lifespan(_: FastAPI):
    inject.configure(config)

    yield


app = FastAPI(default_response_class=ORJSONResponse, lifespan=lifespan)
setup_routers(app)
