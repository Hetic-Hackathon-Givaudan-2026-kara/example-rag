# Branche 1 : Ollama, client renforcé et mesures (carte #13)

## Objectif et périmètre
Installer Ollama avec Qwen 2.5 1,5B, mesurer ses performances sur la machine de développement, et rendre le client
Ollama fiable (délai, nouvel essai, sortie contrainte par schéma, mise en route au démarrage).
Couches touchées : `clients`, `core` (configuration).

## Machine de mesure
Windows avec WSL2 (Ubuntu), 8 Go de RAM au total, 4 cœurs, sans GPU.
Réglage WSL de la 2e série : `memory=5GB`, `swap=4GB` (fichier `.wslconfig` du profil Windows).

## Modèles
- Génération : `qwen2.5:1.5b-instruct-q4_K_M` (986 Mo sur disque, 1,2 Go chargé, 100 % CPU, contexte 4096).
- Embeddings : `nomic-embed-text` (274 Mo).
- Le tag `qwen2.5:1.5b-instruct-q4`, cité dans le document de choix du modèle, n'existe pas dans la bibliothèque Ollama.

## Mesures
Demande : « boisson protéinée pour sportifs », sans consigne, en texte libre (`ollama run ... --verbose`).

| Série | Conditions | Chargement | Tokens générés | Vitesse | Durée totale |
| :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | à froid, WSL 3,7 Go | 1 min 25 | 261 | 6,7 tokens/s | 2 min 06 |
| 2 | à froid forcé, WSL 3,7 Go | 1 min 51 | 260 | 6,3 tokens/s | 2 min 34 |
| 3 | à froid forcé, WSL 4,8 Go | 1 min 45 | 428 | 5,2 tokens/s | 3 min 10 |
| 4 | à chaud, deux autres demandes | 0 s | 692 et 133 | 8,8 et 10,4 tokens/s | 1 min 19 et 14 s |

Mémoire pendant que le modèle est chargé :

| WSL | Total | Disponible | Swap utilisé |
| :-- | :-- | :-- | :-- |
| 3,7 Go | 3,7 Gi | 1,1 Gi | 331 Mi |
| 4,8 Go | 4,8 Gi | 2,1 Gi | 324 Ki |

Le processus du modèle occupe environ 1,15 Go ; les serveurs de VS Code, environ 0,85 Go.

## Ce que les mesures montrent
- Le premier appel à froid dure de 85 à 111 s (trois mesures) : c'est le chargement du modèle.
- Passer WSL de 3,7 à 4,8 Go supprime le swap et double la mémoire disponible, mais ne change ni le chargement ni la
  vitesse : la mémoire n'est pas le goulot, le processeur l'est (100 % CPU, 4 cœurs, 5 à 10 tokens/s).
- Le temps de réponse est presque proportionnel au nombre de tokens générés.
- Sans consigne ni schéma, le modèle écrit en texte libre, change de langue et invente des produits : il faut un prompt,
  un schéma JSON et des garde-fous. `ollama run` utilise une température par défaut ; notre client la fixe à 0.

## Critères de la carte
| Critère | Résultat |
| :-- | :-- |
| L'API Ollama répond en local | Oui |
| Temps mesuré sur 3 demandes (cible : moins de 3 s) | Mesuré ; cible non atteinte |
| Plus de 5 Go de RAM libres pendant la génération | Non atteint : 2,1 Go disponibles sur une machine de 8 Go |
| Tag exact dans le README | Oui |

## Décisions : « j'ai pris X parce que Y »
- Mise en route des modèles au démarrage de l'API (`warm_up`) : un client ne doit pas payer 85 à 111 s.
- `OLLAMA_KEEP_ALIVE=60m` : Ollama décharge sinon le modèle après 5 minutes.
- `OLLAMA_TIMEOUT_S=180` : plus long que le pire chargement mesuré (111 s).
- Sortie limitée (`max_tokens`) et contrainte par schéma : borne le temps de réponse et fiabilise le format.
- Un nouvel essai, puis `OllamaUnavailableError` : l'API ne plante pas quand Ollama est éteint.

## À décider avec Product
- Critère de latence réaliste (estimation : 10 à 25 s à chaud pour un brief JSON, à mesurer avec la route `/brief`).
- Machine de démo plus puissante, ou mode secours (carte #19).
- Test de `qwen2.5:0.5b` pour l'extraction si la vitesse reste insuffisante.

## Limites des mesures
Une seule machine ; texte libre au lieu du JSON de la route `/brief` ; vitesses variables d'environ 20 % d'une
exécution à l'autre.

## Comment tester
`ruff check .` · `mypy` · `pytest`
