"""Schéma de la réponse de GET /health."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    llm_mode: str
    llm_model: str
    embed_model: str
