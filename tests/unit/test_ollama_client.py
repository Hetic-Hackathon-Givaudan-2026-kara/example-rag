from typing import Any

from app.clients.ollama_client import OllamaClient
from app.core.config import Settings


class FakeOllama:
    def __init__(self) -> None:
        self.embed_inputs: list[str] = []
        self.chat_options: dict[str, Any] = {}

    def embed(self, model: str, input: list[str]) -> dict[str, Any]:
        self.embed_inputs = input
        return {"embeddings": [[0.1, 0.2] for _ in input]}

    def chat(self, model: str, messages: list[dict[str, str]], options: dict[str, Any]) -> dict[str, Any]:
        self.chat_options = options
        return {"message": {"content": "bonjour"}}


def make_client(**overrides: Any) -> tuple[OllamaClient, FakeOllama]:
    fake = FakeOllama()
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
    assert fake.chat_options == {"temperature": 0.5}
