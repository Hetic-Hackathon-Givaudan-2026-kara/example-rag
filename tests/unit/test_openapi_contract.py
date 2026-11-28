from scripts.export_openapi import OPENAPI_PATH, render


def test_committed_openapi_matches_the_application() -> None:
    # Si ce test échoue : relancer `python -m scripts.export_openapi` et valider le contrat avec Dev (ADR-10)
    assert OPENAPI_PATH.read_text(encoding="utf-8") == render()
