from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
from pathlib import Path
from time import time
import os

from fastapi.responses import JSONResponse, HTMLResponse
from src.logger import setup_logging
from src.tasks import run_delivery_calculation
from src.routing.parcels import router as parcels_router

scheduler = AsyncIOScheduler()


# запуск расчёта доставки каждые 5 минут
@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("TESTING") != "1":
        scheduler.add_job(run_delivery_calculation, "interval", minutes=5)
        scheduler.start()
        yield
        scheduler.shutdown()
    else:
        yield


setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI(lifespan=lifespan)
app.include_router(parcels_router)


@app.get("/", response_class=HTMLResponse)
async def read_index():
    html_path = Path("src/templates/index.html")
    return html_path.read_text()


# перехват ошибок сервера для логирования
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "unhandled_exception"},
    )


# логирование всех запросов
# и указание времени их выполнения
if os.getenv("TESTING") != "1":

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time()
        response = await call_next(request)
        process_time = (time() - start_time) * 1000

        logger.info(
            f"Method: {request.method} Path: {request.url.path} "
            f"Status: {response.status_code} Time: {process_time:.2f}ms"
        )
        return response
