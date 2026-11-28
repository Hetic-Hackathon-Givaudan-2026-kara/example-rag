import pytest

from app.clients.fake_chat_client import FakeChatClient
from app.schemas.brief import BriefExtraction


def ask(text: str) -> BriefExtraction:
    raw = FakeChatClient().chat([{"role": "system", "content": "consignes"}, {"role": "user", "content": text}])
    return BriefExtraction.model_validate_json(raw)


def test_demo_request_is_understood() -> None:
    brief = ask("Un arôme fruits rouges naturel pour ma boisson protéinée")
    assert brief.metier == "flavors"
    assert brief.application == "boisson protéinée"
    assert brief.profil_olfactif == ["fruits rouges"]
    assert brief.naturel is True
    assert brief.format is None


def test_soap_request_is_a_fragrance() -> None:
    brief = ask("Je cherche une senteur premium pour une gamme de savons")
    assert brief.metier == "fragrances"
    assert brief.application == "gamme de savons"
    assert brief.contraintes == ["premium"]


@pytest.mark.parametrize(
    ("text", "expected"),
    [("en poudre", "poudre"), ("prêt à boire", "liquide"), ("rien de précis", None)],
)
def test_format_keywords(text: str, expected: str | None) -> None:
    assert ask(text).format == expected


def test_volume_is_read_with_its_unit() -> None:
    brief = ask("environ 2,5 t de vanille")
    assert brief.volume is not None
    assert brief.volume.valeur == 2.5
    assert brief.volume.unite == "t"


def test_unknown_text_leaves_everything_empty() -> None:
    assert ask("bonjour") == BriefExtraction()
