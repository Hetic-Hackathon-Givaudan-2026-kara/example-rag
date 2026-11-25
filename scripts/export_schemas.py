"""Génère schema/brief.schema.json à partir des modèles Pydantic."""

import json
from pathlib import Path

from app.schemas.brief import Brief

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "brief.schema.json"


def render() -> str:
    return json.dumps(Brief.model_json_schema(), indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    SCHEMA_PATH.parent.mkdir(exist_ok=True)
    SCHEMA_PATH.write_text(render(), encoding="utf-8")
    print(f"Écrit : {SCHEMA_PATH}")
