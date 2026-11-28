"""Erreurs partagées par toutes les couches."""


class LLMUnavailableError(RuntimeError):
    """Le modèle de langage ne répond pas (Ollama éteint, délai dépassé...)."""
