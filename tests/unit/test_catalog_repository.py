from pathlib import Path

import chromadb
import pytest

from app.repositories.catalog_repository import CatalogRepository, EmbeddingModelMismatchError

COLLECTION = "catalog_test"


def make_client(tmp_path: Path) -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=str(tmp_path))


def filled_repo(client: chromadb.ClientAPI) -> CatalogRepository:
    repo = CatalogRepository(client, COLLECTION, "nomic-embed-text")
    repo.upsert(
        ids=["A", "B", "C"],
        documents=["fruits rouges", "vanille", "fraise"],
        metadatas=[{"famille": "Fruité"}, {"famille": "Gourmand"}, {"famille": "Fruité"}],
        embeddings=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.9, 0.1, 0.0]],
    )
    return repo


def test_search_orders_hits_by_similarity(tmp_path: Path) -> None:
    repo = filled_repo(make_client(tmp_path))
    hits = repo.search([1.0, 0.0, 0.0], n_results=3)
    assert [h.id for h in hits] == ["A", "C", "B"]
    assert hits[0].similarity == pytest.approx(1.0, abs=1e-3)


def test_cosine_distance_ignores_vector_length(tmp_path: Path) -> None:
    # Avec une distance euclidienne, [5, 0, 0] serait très loin de [1, 0, 0]
    repo = filled_repo(make_client(tmp_path))
    top = repo.search([5.0, 0.0, 0.0], n_results=1)[0]
    assert top.id == "A"
    assert top.similarity == pytest.approx(1.0, abs=1e-3)


def test_search_can_filter_on_metadata(tmp_path: Path) -> None:
    repo = filled_repo(make_client(tmp_path))
    hits = repo.search([1.0, 0.0, 0.0], n_results=2, where={"famille": "Fruité"})
    assert {h.id for h in hits} == {"A", "C"}


def test_empty_collection_returns_no_hits(tmp_path: Path) -> None:
    repo = CatalogRepository(make_client(tmp_path), COLLECTION, "nomic-embed-text")
    assert repo.search([1.0, 0.0, 0.0], n_results=3) == []


def test_reset_removes_everything(tmp_path: Path) -> None:
    repo = filled_repo(make_client(tmp_path))
    assert repo.count() == 3
    repo.reset()
    assert repo.count() == 0


def test_reopening_with_same_model_keeps_data(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    filled_repo(client)
    assert CatalogRepository(client, COLLECTION, "nomic-embed-text").count() == 3


def test_other_embedding_model_is_refused(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    filled_repo(client)
    with pytest.raises(EmbeddingModelMismatchError):
        CatalogRepository(client, COLLECTION, "bge-m3")
