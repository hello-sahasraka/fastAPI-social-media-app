import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import database
from app.routers.routes_posts import router as posts_router
from app.logging_conf import configure_logging


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting up...")
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(posts_router)
