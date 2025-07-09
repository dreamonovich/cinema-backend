from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from starlette.middleware.cors import CORSMiddleware

from app.cinema.routers.cinema_router import cinema_router
from app.db import init_db
from app.film.routers.film_router import film_router
from app.film.routers.film_screening_router import screening_router
from app.minio import minio_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    minio_handler.create_bucket_if_not_exists()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(cinema_router)
app.include_router(film_router)
app.include_router(screening_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или ["*"] для всех источников
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )
