"""Génère openapi.yaml à partir de l'application FastAPI (contrat d'API, ADR-10)."""

from pathlib import Path

import yaml

from app.main import app

OPENAPI_PATH = Path(__file__).resolve().parent.parent / "openapi.yaml"


def render() -> str:
    return yaml.safe_dump(app.openapi(), sort_keys=False, allow_unicode=True)


if __name__ == "__main__":
    OPENAPI_PATH.write_text(render(), encoding="utf-8")
    print(f"Écrit : {OPENAPI_PATH}")
