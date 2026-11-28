"""Route du brief : reçoit la demande du client, renvoie les critères extraits."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response

from app.api.deps import get_chat_client
from app.clients.protocols import ChatClient
from app.core.config import Settings, get_settings
from app.core.errors import LLMUnavailableError
from app.schemas.brief import Brief
from app.schemas.brief_request import BriefRequest
from app.services.brief_service import extract_brief

router = APIRouter(tags=["brief"])


@router.post(
    "/brief",
    responses={503: {"description": "Le service d'IA est momentanément indisponible"}},
)
def create_brief(
    request: BriefRequest,
    response: Response,
    llm: Annotated[ChatClient, Depends(get_chat_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Brief:
    """Extrait les critères de la demande du client. Ce que le client n'a pas dit vaut null."""
    try:
        brief = extract_brief(request.texte, llm, max_tokens=settings.brief_max_tokens)
    except LLMUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail="Le service d'IA est momentanément indisponible. Réessayez dans un instant.",
        ) from exc
    # Indique si la réponse vient du vrai modèle ou du faux (démonstration sans Ollama)
    response.headers["X-LLM-Mode"] = settings.llm_mode
    return brief
