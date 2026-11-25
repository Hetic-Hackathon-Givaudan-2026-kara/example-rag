# Branche 2 : schéma du brief (carte #14)

## Objectif et périmètre
Définir le contrat entre le modèle, l'API, le front et le catalogue : la demande du client structurée en critères.
Couches touchées : `schemas` (modèles), `services` (calcul de la jauge). Aucune route pour l'instant.

## Décisions : « j'ai pris X parce que Y »
- Critères principaux : application, format, profil_olfactif, naturel. Facultatifs : volume, contraintes.
  Parce que le Figma validé demande « poudre ou prêt à boire ? » en premier.
- Deux niveaux : `BriefExtraction` (rempli par le modèle) et `Brief` (plus `champs_manquants` et `completude`,
  calculés par le code). Un petit modèle se trompe sur les listes et les pourcentages.
- `metier` ajouté (flavors / fragrances) : sans lui, une demande « savons » ne peut pas être routée ni relayée.
- Listes fermées pour `metier` et `format`, texte libre pour le reste, tant que le catalogue n'est pas figé.
- `format` = `poudre` ou `liquide` ; le libellé affiché « Prêt à boire » est géré par le front.
- `volume` garde l'unité dite par le client (g, kg, t) ; la conversion est faite par le code.
- Pas de prix : un prix n'est jamais affiché ni promis (FR-08).
- `null` = « non dit » ; `[]` et `""` sont aussi traités comme « non dit ».
- Jauge = 100 × critères principaux remplis / 4. Exemple de la démo : 75 %.

## Comment tester
`ruff check .` · `mypy` · `pytest` · régénérer le schéma : `python -m scripts.export_schemas`

## Points à confirmer avec le front (Imane)
- La valeur `liquide` correspond-elle à « Prêt à boire » dans le catalogue ?
- Le Figma affiche 60 % ; avec 4 critères, la démo donne 75 % (workbook de jeudi).

## Limites connues
Pas de route `/brief` (branche suivante) ; listes de `application` et `contraintes` encore libres.
