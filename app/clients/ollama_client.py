"""Client Ollama : le seul module qui parle à Ollama (embeddings et génération)."""

from __future__ import annotations

from typing import Any

import ollama

from app.core.config import Settings, get_settings

NOMIC_DOCUMENT_PREFIX = "search_document: "
NOMIC_QUERY_PREFIX = "search_query: "


class OllamaClient:
    def __init__(self, settings: Settings | None = None, client: Any = None) -> None:
        self._settings = settings or get_settings()
        # `client` permet d'injecter un faux Ollama dans les tests
        self._client = client or ollama.Client(host=self._settings.ollama_host)

    @property
    def _uses_nomic_prefixes(self) -> bool:
        # nomic-embed-text distingue les requêtes des documents par un préfixe
        return "nomic" in self._settings.embed_model

    def _embed(self, texts: list[str], prefix: str) -> list[list[float]]:
        response = self._client.embed(model=self._settings.embed_model, input=[prefix + t for t in texts])
        return [list(vector) for vector in response["embeddings"]]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts, NOMIC_DOCUMENT_PREFIX if self._uses_nomic_prefixes else "")

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], NOMIC_QUERY_PREFIX if self._uses_nomic_prefixes else "")[0]

    def chat(self, messages: list[dict[str, str]]) -> str:
        response = self._client.chat(
            model=self._settings.llm_model,
            messages=messages,
            options={"temperature": self._settings.llm_temperature},
        )
        content = response["message"]["content"]
        return content if isinstance(content, str) else ""
