"""Faux modèle de langage : comprend quelques mots-clés, ne contacte jamais Ollama.

Il sert à développer le front et à lancer les tests sans Ollama. Ses réponses sont déterministes.
Ce n'est pas de l'intelligence artificielle : l'API le signale par l'en-tête `X-LLM-Mode: fake`.
"""

from __future__ import annotations

import re
from typing import Any

from app.schemas.brief import BriefExtraction, Format, Metier, UniteVolume, Volume

FLAVOR_WORDS = ("arôme", "arome", "boisson", "saveur", "goût", "gout", "yaourt", "biscuit")
FRAGRANCE_WORDS = ("parfum", "senteur", "savon", "fragrance")
# Du plus précis au plus général : la première correspondance gagne
APPLICATIONS = (
    ("boisson protéinée", "boisson protéinée"),
    ("boisson", "boisson"),
    ("yaourt", "yaourt"),
    ("biscuit", "biscuit"),
    ("savon", "gamme de savons"),
)
NOTES = (
    "fruits rouges",
    "fraise",
    "framboise",
    "cassis",
    "vanille",
    "citron",
    "chocolat",
    "caramel",
    "menthe",
    "coco",
    "basilic",
)
CONSTRAINTS = ("sans sucre", "premium", "édition limitée")
LIQUID_WORDS = ("prêt à boire", "pret a boire", "liquide")
VOLUME_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(kg|g|t)\b")


def _metier(text: str) -> Metier | None:
    if any(word in text for word in FLAVOR_WORDS):
        return Metier.FLAVORS
    if any(word in text for word in FRAGRANCE_WORDS):
        return Metier.FRAGRANCES
    return None


def _application(text: str) -> str | None:
    for keyword, label in APPLICATIONS:
        if keyword in text:
            return label
    return None


def _format(text: str) -> Format | None:
    if "poudre" in text:
        return Format.POUDRE
    if any(word in text for word in LIQUID_WORDS):
        return Format.LIQUIDE
    return None


def _volume(text: str) -> Volume | None:
    match = VOLUME_RE.search(text)
    if match is None:
        return None
    value = float(match.group(1).replace(",", "."))
    if value <= 0:
        return None
    return Volume(valeur=value, unite=UniteVolume(match.group(2)))


class FakeChatClient:
    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        schema: dict[str, Any] | None = None,
        max_tokens: int | None = None,
    ) -> str:
        text = messages[-1]["content"].lower()
        extraction = BriefExtraction(
            metier=_metier(text),
            application=_application(text),
            format=_format(text),
            profil_olfactif=[note for note in NOTES if note in text] or None,
            naturel=True if "naturel" in text else None,
            volume=_volume(text),
            contraintes=[item for item in CONSTRAINTS if item in text] or None,
        )
        return extraction.model_dump_json()

    def warm_up(self) -> None:
        return None
