"""Configuration du service IA, lue depuis les variables d'environnement et le fichier .env."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Modèles ---
    llm_model: str = "qwen2.5:1.5b-instruct-q4_K_M"
    embed_model: str = "nomic-embed-text"
    ollama_host: str = "http://localhost:11434"
    ollama_timeout_s: float = Field(default=120, gt=0)
    ollama_max_retries: int = Field(default=1, ge=0)
    ollama_keep_alive: str = "60m"
    llm_temperature: float = Field(default=0, ge=0, le=2)
    llm_mode: Literal["real", "fake"] = "real"

    # --- Données ---
    catalog_path: Path = Path("data/raw_catalog.json")
    chroma_dir: Path = Path("chroma_db")
    collection_flavors: str = "catalog_flavors"
    collection_fragrances: str = "catalog_fragrances"

    # --- Garde-fous ---
    similarity_threshold: float = Field(default=0.0, ge=0, le=1)
    max_references: int = Field(default=3, ge=1, le=3)
    max_questions: int = Field(default=3, ge=1, le=3)

    # --- API ---
    cors_origins: str = "http://localhost:5173"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
