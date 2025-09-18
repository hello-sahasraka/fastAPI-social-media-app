from fastapi import FastAPI
from app.routers.routes_posts import router as posts_router


app = FastAPI()

app.include_router(posts_router)
