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
