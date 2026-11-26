from typing import Any

import pytest

from app.clients.ollama_client import OllamaClient, OllamaUnavailableError
from app.core.config import Settings


class FakeOllama:
    def __init__(self, failures: int = 0) -> None:
        self.failures = failures
        self.calls = 0
        self.embed_inputs: list[str] = []
        self.chat_kwargs: dict[str, Any] = {}

    def _maybe_fail(self) -> None:
        self.calls += 1
        if self.calls <= self.failures:
            raise ConnectionError("Ollama éteint")

    def embed(self, model: str, input: list[str], keep_alive: str) -> dict[str, Any]:
        self._maybe_fail()
        self.embed_inputs = input
        return {"embeddings": [[0.1, 0.2] for _ in input]}

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        options: dict[str, Any],
        format: dict[str, Any] | None,
        keep_alive: str,
    ) -> dict[str, Any]:
        self._maybe_fail()
        self.chat_kwargs = {"options": options, "format": format, "keep_alive": keep_alive}
        return {"message": {"content": "bonjour"}}


def make_client(failures: int = 0, **overrides: Any) -> tuple[OllamaClient, FakeOllama]:
    fake = FakeOllama(failures)
    return OllamaClient(Settings(_env_file=None, **overrides), client=fake), fake


def test_nomic_adds_document_prefix() -> None:
    client, fake = make_client(embed_model="nomic-embed-text")
    client.embed_documents(["fruits rouges"])
    assert fake.embed_inputs == ["search_document: fruits rouges"]


def test_nomic_adds_query_prefix() -> None:
    client, fake = make_client(embed_model="nomic-embed-text")
    vector = client.embed_query("fruits rouges")
    assert fake.embed_inputs == ["search_query: fruits rouges"]
    assert vector == [0.1, 0.2]


def test_other_embedding_model_adds_no_prefix() -> None:
    client, fake = make_client(embed_model="bge-m3")
    client.embed_documents(["fruits rouges"])
    assert fake.embed_inputs == ["fruits rouges"]


def test_chat_uses_configured_temperature_and_returns_text() -> None:
    client, fake = make_client(llm_temperature=0.5)
    assert client.chat([{"role": "user", "content": "salut"}]) == "bonjour"
    assert fake.chat_kwargs["options"] == {"temperature": 0.5}
    assert fake.chat_kwargs["format"] is None


def test_chat_passes_schema_token_cap_and_keep_alive() -> None:
    client, fake = make_client(ollama_keep_alive="10m")
    schema = {"type": "object"}
    client.chat([{"role": "user", "content": "salut"}], schema=schema, max_tokens=80)
    assert fake.chat_kwargs["format"] == schema
    assert fake.chat_kwargs["options"]["num_predict"] == 80
    assert fake.chat_kwargs["keep_alive"] == "10m"


def test_a_failed_call_is_retried() -> None:
    client, fake = make_client(failures=1, ollama_max_retries=1)
    assert client.chat([{"role": "user", "content": "salut"}]) == "bonjour"
    assert fake.calls == 2


def test_error_is_raised_after_all_retries() -> None:
    client, fake = make_client(failures=5, ollama_max_retries=1)
    with pytest.raises(OllamaUnavailableError):
        client.chat([{"role": "user", "content": "salut"}])
    assert fake.calls == 2


def test_no_retry_when_retries_are_disabled() -> None:
    client, fake = make_client(failures=1, ollama_max_retries=0)
    with pytest.raises(OllamaUnavailableError):
        client.embed_query("fruits rouges")
    assert fake.calls == 1


def test_warm_up_loads_both_models() -> None:
    client, fake = make_client()
    client.warm_up()
    assert fake.calls == 2  # un appel de génération et un appel d'embedding
    assert fake.embed_inputs == ["search_query: ok"]
