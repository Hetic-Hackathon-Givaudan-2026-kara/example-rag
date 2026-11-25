"""Schémas du brief : la demande du client, structurée en critères."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Metier(StrEnum):
    FLAVORS = "flavors"
    FRAGRANCES = "fragrances"


class Format(StrEnum):
    POUDRE = "poudre"
    LIQUIDE = "liquide"  # affiché « Prêt à boire » dans l'interface


class UniteVolume(StrEnum):
    G = "g"
    KG = "kg"
    T = "t"


class Volume(BaseModel):
    valeur: float = Field(gt=0)
    unite: UniteVolume


class BriefExtraction(BaseModel):
    """Ce que le modèle de langage remplit. None veut dire : le client ne l'a pas dit."""

    model_config = ConfigDict(extra="forbid")

    metier: Metier | None = None
    application: str | None = None
    format: Format | None = None
    profil_olfactif: list[str] | None = None
    naturel: bool | None = None
    volume: Volume | None = None
    contraintes: list[str] | None = None


class Brief(BriefExtraction):
    """Ce que l'API renvoie : l'extraction plus deux champs calculés par le code."""

    champs_manquants: list[str]
    completude: int = Field(ge=0, le=100)
