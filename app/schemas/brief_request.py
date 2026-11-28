"""Schéma de la requête envoyée à POST /brief."""

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

Texte = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class BriefRequest(BaseModel):
    texte: Texte = Field(description="La demande du client, avec ses mots")
