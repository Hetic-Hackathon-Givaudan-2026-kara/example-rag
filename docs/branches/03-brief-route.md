# Branche 3 : route POST /brief (carte #9)

## Objectif et périmètre
Exposer l'extraction du brief par une API FastAPI : `GET /health` et `POST /brief`, avec un mode `fake` pour développer le
front sans Ollama, et un contrat `openapi.yaml` généré et contrôlé par les tests.
Couches touchées : `api` (routers, deps), `services`, `clients`, `schemas`, `core`.

## Pour le front
- Lancer sans Ollama : `LLM_MODE=fake uvicorn app.main:app --port 8000` (Swagger : `http://localhost:8000/docs`).
- Requête : `POST /brief` avec `{"texte": "..."}` ; réponse : le schéma `Brief` (critères, `champs_manquants`, `completude`).
- L'en-tête `X-LLM-Mode` vaut `fake` ou `real` ; CORS autorise `http://localhost:5173` (réglable : `CORS_ORIGINS`).
- Erreur 503 si Ollama ne répond pas ; erreur 422 si le texte est vide ou dépasse 2000 caractères.
- Mode `real` : le chargement des modèles prend 85 à 111 s au démarrage (en arrière-plan), puis le modèle reste en mémoire 60 min.

## Décisions : « j'ai pris X parce que Y »
- Le schéma complet n'est pas recopié dans le prompt (la carte le suggère) : Ollama contraint déjà la sortie avec `format`, et
  la machine traite environ 20 tokens de prompt par seconde. Une description courte des champs suffit.
- Consignes fixes au début du prompt, texte du client à la fin : Ollama réutilise le début identique d'un appel à l'autre.
- Le texte du client est une donnée (message utilisateur) : défense de base contre l'injection de prompt, mesurée par l'évaluation.
- Sortie invalide : un deuxième essai, puis un brief vide (0 %) qui déclenche les questions : l'API ne plante pas.
- Ollama éteint : erreur `LLMUnavailableError` définie dans `core`, traduite en 503 par la route.
- Faux modèle déterministe signalé par `X-LLM-Mode: fake` : il comprend quelques mots-clés et ne se fait pas passer pour une IA.
- Mise en route des modèles dans un fil d'arrière-plan : l'API répond tout de suite, le premier appel réel attend le chargement.
- `openapi.yaml` est généré depuis l'application et vérifié par un test (ADR-10).

## Comment tester
`ruff check .` · `mypy` · `pytest` · régénérer le contrat : `python -m scripts.export_openapi`

## Limites connues
Latence réelle d'un brief à mesurer sur la machine de démo ; précision du modèle 1,5B mesurée par l'évaluation (branche suivante) ;
le faux modèle ne comprend que quelques mots-clés.
