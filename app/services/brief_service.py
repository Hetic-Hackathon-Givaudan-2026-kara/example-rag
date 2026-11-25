"""Logique du brief : champs manquants et jauge de complétude, calculés par le code."""

from app.schemas.brief import Brief, BriefExtraction

# Critères nécessaires pour recommander. volume et contraintes sont facultatifs et ne comptent pas.
CORE_FIELDS = ("application", "profil_olfactif", "format", "naturel")


def _is_filled(value: object) -> bool:
    # Un petit modèle renvoie parfois [] ou "" au lieu de null : on les traite comme « non dit ».
    return value is not None and value != [] and value != ""


def build_brief(extraction: BriefExtraction) -> Brief:
    missing = [name for name in CORE_FIELDS if not _is_filled(getattr(extraction, name))]
    completude = round(100 * (len(CORE_FIELDS) - len(missing)) / len(CORE_FIELDS))
    return Brief(**extraction.model_dump(), champs_manquants=missing, completude=completude)
