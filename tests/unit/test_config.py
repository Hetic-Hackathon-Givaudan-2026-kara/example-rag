import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_defaults_match_documented_values() -> None:
    settings = Settings(_env_file=None)
    assert settings.llm_model == "qwen2.5:1.5b-instruct-q4_K_M"
    assert settings.max_references == 3
    assert settings.llm_mode == "real"


def test_environment_variable_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "qwen2.5:3b")
    assert Settings(_env_file=None).llm_model == "qwen2.5:3b"


def test_out_of_range_value_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_REFERENCES", "7")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_cors_origins_are_split_on_commas(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://a.test, http://b.test")
    assert Settings(_env_file=None).cors_origins_list == ["http://a.test", "http://b.test"]
