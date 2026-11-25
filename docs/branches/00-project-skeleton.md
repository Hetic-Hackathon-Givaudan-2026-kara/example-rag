# Branche 0 : structure du projet, configuration et dépendances

## Objectif et périmètre
Poser le socle du service IA : couches, configuration typée, outils de qualité, dépendances figées.
Couches touchées : `core`, `clients`, `repositories` (le reste est vide).

## Décisions : « j'ai pris X parce que Y »
- Dépendances figées avec `==` : toute l'équipe a les mêmes versions.
- `pydantic-settings` : lit `.env` et valide les types dès le démarrage (`os.getenv` ne lit pas `.env`).
- mypy strict sur `app/` seulement : le code hérité sera supprimé, pas corrigé.
- Distance cosinus et modèle d'embedding vérifié à l'ouverture de la collection (ADR-11).
- Le client Ollama reçoit un faux client en test : les tests tournent sans Ollama.

## Comment tester
`ruff check .` · `mypy` · `pytest`

## Limites connues
Pas encore de timeout ni de nouvel essai Ollama (branche 1), pas de routes (branches suivantes).
