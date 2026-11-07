"""SUPPLYMIND FastAPI application."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import agent as agent_api
from .api import alerts as alerts_api
from .api import auth as auth_api
from .api import dashboard as dashboard_api
from .api import crises as crises_api
from .api import impacts as impacts_api
from .api import lab as lab_api
from .api import memory as memory_api
from .api import orders as orders_api
from .api import settings as settings_api
from .api import simulations as simulations_api
from .api import suppliers as suppliers_api
from .config import get_settings
from .db import SessionLocal
from .services import monitoring

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("supplymind")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("SUPPLYMIND starting (env=%s)", settings.app_env)
    if settings.seed_demo_on_startup:
        try:
            from .services.seed import seed_demo

            db = SessionLocal()
            try:
                result = seed_demo(db, force=False, retain_memories=True)
                logger.info("startup seed result: %s", result)
            finally:
                db.close()
        except Exception:  # noqa: BLE001
            logger.exception("startup seed failed")
    if settings.scheduler_enabled:
        monitoring.start_scheduler(settings.scheduler_interval_seconds)
    yield
    if settings.scheduler_enabled:
        monitoring.stop_scheduler()
    logger.info("SUPPLYMIND stopped")


app = FastAPI(
    title="SUPPLYMIND API",
    version="1.0.0",
    description=(
        "Supply-chain intelligence with genuine Hindsight organizational memory. "
        "All demo business records are synthetic and labeled."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    auth_api.router,
    dashboard_api.router,
    suppliers_api.router,
    orders_api.router,
    memory_api.router,
    agent_api.router,
    lab_api.router,
    alerts_api.router,
    simulations_api.router,
    settings_api.router,
):
    app.include_router(router, prefix=settings.api_prefix)


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "api": settings.api_prefix,
        "docs": "/docs",
        "memory_engine": "Hindsight (self-hosted)",
        "demo_data": "synthetic and labeled",
    }
