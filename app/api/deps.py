"""Assemblage des dépendances : le seul endroit qui choisit entre le vrai modèle et le faux."""

from functools import lru_cache

from app.clients.fake_chat_client import FakeChatClient
from app.clients.ollama_client import OllamaClient
from app.clients.protocols import ChatClient
from app.core.config import get_settings


@lru_cache
def get_chat_client() -> ChatClient:
    settings = get_settings()
    if settings.llm_mode == "fake":
        return FakeChatClient()
    return OllamaClient(settings)
