"""Client Ollama : le seul module qui parle à Ollama (embeddings et génération)."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import httpx
import ollama

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

NOMIC_DOCUMENT_PREFIX = "search_document: "
NOMIC_QUERY_PREFIX = "search_query: "


class OllamaUnavailableError(RuntimeError):
    """Ollama n'a pas répondu correctement, même après les nouveaux essais."""


class OllamaClient:
    def __init__(self, settings: Settings | None = None, client: Any = None) -> None:
        self._settings = settings or get_settings()
        # `client` permet d'injecter un faux Ollama dans les tests
        self._client = client or ollama.Client(
            host=self._settings.ollama_host,
            timeout=self._settings.ollama_timeout_s,
        )

    def _with_retries(self, action: str, call: Callable[[], Any]) -> Any:
        attempts = self._settings.ollama_max_retries + 1
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                return call()
            except (ollama.ResponseError, httpx.HTTPError, OSError) as exc:
                last_error = exc
                logger.warning("Ollama %s : essai %d/%d échoué (%s)", action, attempt, attempts, exc)
        raise OllamaUnavailableError(
            f"Ollama n'a pas répondu ({action}) après {attempts} essai(s) : {last_error}"
        ) from last_error

    @property
    def _uses_nomic_prefixes(self) -> bool:
        # nomic-embed-text distingue les requêtes des documents par un préfixe
        return "nomic" in self._settings.embed_model

    def _embed(self, texts: list[str], prefix: str) -> list[list[float]]:
        response = self._with_retries(
            "embed",
            lambda: self._client.embed(
                model=self._settings.embed_model,
                input=[prefix + t for t in texts],
                keep_alive=self._settings.ollama_keep_alive,
            ),
        )
        return [list(vector) for vector in response["embeddings"]]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts, NOMIC_DOCUMENT_PREFIX if self._uses_nomic_prefixes else "")

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], NOMIC_QUERY_PREFIX if self._uses_nomic_prefixes else "")[0]

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        schema: dict[str, Any] | None = None,
        max_tokens: int | None = None,
    ) -> str:
        options: dict[str, Any] = {"temperature": self._settings.llm_temperature}
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        response = self._with_retries(
            "chat",
            lambda: self._client.chat(
                model=self._settings.llm_model,
                messages=messages,
                options=options,
                format=schema,
                keep_alive=self._settings.ollama_keep_alive,
            ),
        )
        content = response["message"]["content"]
        return content if isinstance(content, str) else ""

    def warm_up(self) -> None:
        """Charge les deux modèles en mémoire (le premier appel à froid a pris 85 à 111 s)."""
        self.chat([{"role": "user", "content": "ok"}], max_tokens=1)
        self.embed_query("ok")
