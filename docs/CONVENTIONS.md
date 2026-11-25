# Conventions de travail (zone `ia/`)

## Branches
- `main` : version stable. `develop` : intégration. Une tâche = une branche `feature/nom-court` créée depuis `develop`.
- Une branche = une documentation dans `docs/branches/NN-nom.md`.

## Commits (format `type: description`)
`feat` nouvelle fonction · `fix` correction · `refactor` réorganisation sans changer le comportement
`test` tests · `docs` documentation · `chore` outillage et configuration
Un commit exprime une seule idée. Après chaque commit, `ruff check .`, `mypy` et `pytest` passent.

## Pull requests
- Ouvrir une Draft PR dès le premier commit, vers `develop`.
- Passer en « Ready for review » quand la CI est verte et la doc de branche écrite.
- Contrat d'API (`openapi.yaml`) : toute modification est validée par Data et Dev.

## Secrets
Aucun secret dans le code. `.env` est ignoré par Git ; `.env.example` documente les variables.
