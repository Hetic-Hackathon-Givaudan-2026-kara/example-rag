import importlib


def test_app_package_imports() -> None:
    assert importlib.import_module("app") is not None


def test_legacy_api_still_imports() -> None:
    # Filet de sécurité pendant la réorganisation : à supprimer quand api.py aura disparu.
    assert importlib.import_module("api") is not None
