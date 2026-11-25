"""Repository du catalogue : le seul module qui parle à ChromaDB."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import chromadb
from chromadb.api import ClientAPI

from app.core.config import Settings, get_settings


class EmbeddingModelMismatchError(RuntimeError):
    """Le modèle d'embedding configuré n'est pas celui qui a servi à indexer la collection."""


@dataclass(frozen=True)
class SearchHit:
    id: str
    document: str
    metadata: dict[str, Any]
    distance: float

    @property
    def similarity(self) -> float:
        # En distance cosinus : distance = 1 - similarité
        return round(1 - self.distance, 4)


class CatalogRepository:
    def __init__(self, client: ClientAPI, collection_name: str, embed_model: str) -> None:
        self._client = client
        self._name = collection_name
        self._embed_model = embed_model
        self._collection = self._open()

    def _existing_names(self) -> set[str]:
        return {c.name for c in self._client.list_collections()}

    def _create(self) -> Any:
        return self._client.create_collection(
            name=self._name,
            metadata={"hnsw:space": "cosine", "embed_model": self._embed_model},
        )

    def _open(self) -> Any:
        if self._name not in self._existing_names():
            return self._create()
        collection = self._client.get_collection(self._name)
        stored = (collection.metadata or {}).get("embed_model")
        if stored != self._embed_model:
            raise EmbeddingModelMismatchError(
                f"La collection '{self._name}' a été indexée avec '{stored}', "
                f"mais la configuration demande '{self._embed_model}'. Réindexe avec reset()."
            )
        return collection

    def count(self) -> int:
        return int(self._collection.count())

    def upsert(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict[str, Any]],
        embeddings: list[list[float]],
    ) -> None:
        self._collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

    def reset(self) -> None:
        """Réindexation complète : supprime la collection puis la recrée vide."""
        self._client.delete_collection(self._name)
        self._collection = self._create()

    def search(
        self,
        query_embedding: list[float],
        n_results: int,
        where: dict[str, Any] | None = None,
    ) -> list[SearchHit]:
        total = self.count()
        if total == 0:
            return []
        result = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, total),
            where=where,
        )
        ids = result["ids"][0]
        documents = (result["documents"] or [[]])[0]
        metadatas = (result["metadatas"] or [[]])[0]
        distances = (result["distances"] or [[]])[0]
        return [
            SearchHit(id=i, document=d, metadata=dict(m or {}), distance=float(dist))
            for i, d, m, dist in zip(ids, documents, metadatas, distances, strict=True)
        ]


def build_catalog_repository(
    business_line: Literal["flavors", "fragrances"],
    settings: Settings | None = None,
) -> CatalogRepository:
    """Construit le repository d'un métier (une collection par métier, ADR-11)."""
    settings = settings or get_settings()
    name = settings.collection_flavors if business_line == "flavors" else settings.collection_fragrances
    client = chromadb.PersistentClient(path=str(settings.chroma_dir))
    return CatalogRepository(client, name, settings.embed_model)
