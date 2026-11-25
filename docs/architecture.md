# Architecture du service IA

Service Python / FastAPI en couches (ADR-05). Chaque dossier a un seul métier : on le reconnaît à ce qu'il touche.

| Dossier | Métier | Parle à | État |
| :-- | :-- | :-- | :-- |
| `app/core/` | Configuration (`.env`, variables d'environnement) | rien | présent |
| `app/clients/` | Appels à un programme externe (Ollama) | Ollama | présent |
| `app/repositories/` | Accès à la base vectorielle | ChromaDB | présent |
| `app/schemas/` | Forme des données qui entrent et sortent de l'API | rien | à venir (carte #14) |
| `app/services/` | Logique métier : enchaîner les étapes, garde-fous | clients, repositories | à venir |
| `app/api/routers/` | Routes HTTP : reçoit, appelle un service, renvoie | services | à venir |

## Règle de dépendance

`routers` → `services` → `clients` / `repositories` → `core`.
Une couche n'appelle jamais une couche située « au-dessus » d'elle. Un router n'appelle ni Chroma ni Ollama directement.

## Pourquoi cette séparation

- On teste une couche avec un faux à la place de la suivante (faux Ollama, base Chroma temporaire).
- Changer de modèle ne touche que `clients/`, changer de base ne touche que `repositories/`.
- Chaque personne travaille sur des fichiers différents, donc moins de conflits Git.

## Code hérité de l'exemple du professeur

`api.py`, `rag.py`, `config.py`, `ingest.py`, `clean.py`, `list.py`, `story.txt` parlent d'une histoire pour enfants.
Ils sont remplacés, pas portés : chaque fichier est supprimé quand son remplaçant existe.
