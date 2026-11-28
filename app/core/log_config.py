"""Configuration de la journalisation (module logging uniquement, pas de print)."""

import logging


def configure_logging(level: str) -> None:
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s : %(message)s")
