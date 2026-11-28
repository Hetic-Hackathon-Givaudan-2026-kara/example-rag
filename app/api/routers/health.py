"""Route de santé : ne contacte pas Ollama, aucun effet de bord."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["système"])


@router.get("/health")
def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    """Indique que le service tourne et quels modèles il utilise."""
    return HealthResponse(
        status="ok",
        llm_mode=settings.llm_mode,
        llm_model=settings.llm_model,
        embed_model=settings.embed_model,
    )
