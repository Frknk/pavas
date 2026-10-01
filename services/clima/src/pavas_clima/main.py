"""Punto de entrada ASGI del servicio Clima."""

import logging
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from pavas_clima.config import Settings


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["clima"] = "clima"


def create_app() -> FastAPI:
    settings = Settings()
    logging.basicConfig(level=settings.log_level)
    app = FastAPI(title="Pavas · Clima", version="0.1.0")
    app.state.settings = settings

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    def health() -> HealthResponse:
        """Liveness del proceso; no comprueba dependencias externas."""
        return HealthResponse()

    return app
