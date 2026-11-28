"""Contrat commun des clients de génération : Ollama en vrai, faux modèle pour le développement."""

from typing import Any, Protocol


class ChatClient(Protocol):
    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        schema: dict[str, Any] | None = None,
        max_tokens: int | None = None,
    ) -> str: ...

    def warm_up(self) -> None: ...
