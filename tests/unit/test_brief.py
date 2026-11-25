import pytest
from pydantic import ValidationError

from app.schemas.brief import BriefExtraction
from app.services.brief_service import build_brief


def test_empty_extraction_misses_every_core_field() -> None:
    brief = build_brief(BriefExtraction())
    assert brief.champs_manquants == ["application", "profil_olfactif", "format", "naturel"]
    assert brief.completude == 0


def test_demo_request_is_75_percent_complete() -> None:
    extraction = BriefExtraction(application="boisson protéinée", profil_olfactif=["fruits rouges"], naturel=True)
    brief = build_brief(extraction)
    assert brief.champs_manquants == ["format"]
    assert brief.completude == 75


def test_complete_brief_has_nothing_missing() -> None:
    extraction = BriefExtraction(
        application="boisson", profil_olfactif=["vanille"], format="poudre", naturel=False
    )
    brief = build_brief(extraction)
    assert brief.champs_manquants == []
    assert brief.completude == 100  # naturel=False est une réponse, pas une absence


def test_empty_list_or_text_counts_as_missing() -> None:
    brief = build_brief(BriefExtraction(application="", profil_olfactif=[], naturel=True))
    assert brief.champs_manquants == ["application", "profil_olfactif", "format"]
    assert brief.completude == 25


def test_optional_fields_do_not_change_completeness() -> None:
    extraction = BriefExtraction(volume={"valeur": 25, "unite": "kg"}, contraintes=["sans sucre"])
    assert build_brief(extraction).completude == 0


@pytest.mark.parametrize(
    "payload",
    [
        {"prix": 3},
        {"format": "gel"},
        {"volume": {"valeur": 5, "unite": "litre"}},
        {"volume": {"valeur": -1, "unite": "kg"}},
    ],
)
def test_invalid_payloads_are_rejected(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        BriefExtraction.model_validate(payload)


# --- Exemples et fichier JSON Schema ---------------------------------------------------------
import json  # noqa: E402
from pathlib import Path  # noqa: E402

from app.schemas.brief import Brief  # noqa: E402
from scripts.export_schemas import SCHEMA_PATH, render  # noqa: E402

EXAMPLES = sorted((Path(__file__).resolve().parents[2] / "schema" / "examples").glob("*.json"))


def test_examples_exist() -> None:
    assert len(EXAMPLES) >= 3


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.stem)
def test_example_is_valid_and_consistent(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    computed = {"champs_manquants", "completude"}
    expected = build_brief(BriefExtraction.model_validate({k: v for k, v in data.items() if k not in computed}))
    assert Brief.model_validate(data) == expected


def test_committed_schema_matches_models() -> None:
    assert SCHEMA_PATH.read_text(encoding="utf-8") == render()
