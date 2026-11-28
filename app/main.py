"""Point d'entrée du service IA : `uvicorn app.main:app`."""

import logging
import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import get_chat_client
from app.api.routers import brief, health
from app.clients.protocols import ChatClient
from app.core.config import Settings, get_settings
from app.core.errors import LLMUnavailableError
from app.core.log_config import configure_logging

logger = logging.getLogger(__name__)


def _warm_up_in_background(client: ChatClient) -> None:
    """Charge les modèles sans bloquer le démarrage : le premier chargement dure 85 à 111 s."""

    def run() -> None:
        try:
            client.warm_up()
            logger.info("Modèles chargés en mémoire")
        except LLMUnavailableError:
            logger.warning("Mise en route impossible : Ollama ne répond pas")

    threading.Thread(target=run, name="llm-warm-up", daemon=True).start()


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()
    configure_logging(resolved.log_level)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if resolved.llm_mode == "real":
            _warm_up_in_background(get_chat_client())
        yield

    app = FastAPI(
        title="Service IA - commande intelligente",
        version="0.1.0",
        description=(
            "Extrait les critères d'une demande de client B2B (brief), pose des questions de précision et "
            "recommande des références du catalogue. Données fictives. L'en-tête X-LLM-Mode indique si la "
            "réponse vient du vrai modèle (real) ou d'un faux modèle de démonstration (fake)."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved.cors_origins_list,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-LLM-Mode"],
    )
    app.include_router(health.router)
    app.include_router(brief.router)
    return app


app = create_app()
