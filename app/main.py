import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi.exception_handlers import http_exception_handler
from app.database import database
from app.routers.routes_posts import router as posts_router
from app.routers.routes_users import router as users_router
from app.routers.routes_upload import router as upload_router
from app.logging_conf import configure_logging


logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting up...")
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(posts_router)
app.include_router(users_router)
app.include_router(upload_router)


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTP Exception: {exc.detail}")
    return await http_exception_handler(request, exc)
