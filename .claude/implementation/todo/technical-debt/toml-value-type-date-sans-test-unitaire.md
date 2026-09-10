+++
id = "toml-value-type-date-sans-test-unitaire"
title = "La branche date de toml_value n'a plus de test unitaire direct"
date = 2026-09-10
source = "chantier supprimer-dump-value, rapport d'audit R4 — réserve close plutôt que traitée"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

La suppression de `dump_value` a emporté ses tests, dont `test_dump_value_couvre_les_types_du_contrat`
— seule assertion directe sur la sérialisation d'une `datetime.date`. Le test qui l'a remplacée,
`test_toml_text_rend_le_membre_droit_du_egal` dans `tests/test_items.py`, couvre `str`, `bool` et
`list`, pas `date`.

La branche `isinstance(value, (int, datetime.date))` de `toml_value` n'est donc plus couverte que
par ricochet, via l'aller-retour d'un contrat dans `tests/test_store_ecriture.py`. Le cas
« `bool` avant `int` », lui, reste pinné directement.

Établi par : `git grep -n "datetime.date\|date(" -- skills/list-dir/scripts/tests/test_items.py`
→ aucune sortie.

## Pourquoi c'est gênant

Une branche couverte seulement par ricochet se casse sans que le test qui la couvre dise pourquoi.
Si l'écriture d'une date changeait — un `isoformat()` remplacé, un ordre d'`isinstance` déplacé —
c'est un test de contrat, à trois modules de là, qui échouerait sur un message parlant de contrat
et non de sérialisation. Le coût est le temps de diagnostic, pas la détection.

C'est aussi la seule régression de couverture du chantier : tout le reste de ce que `dump_value`
pinnait a été réimplanté sur `toml_value` ou rendu sans objet.

## Pour solder

Étendre `test_toml_text_rend_le_membre_droit_du_egal` aux deux types manquants :

```python
assert toml_text(datetime.date(2026, 8, 24), "k") == "2026-08-24"
assert toml_text(7, "k") == "7"
```

L'import `datetime` a été retiré du fichier en même temps que les tests supprimés : il faut le
remettre.

Vérification : `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/test_items.py`
reste vert.

## Assumé

Le report est délibéré : réserve d'audit que l'utilisateur a choisi de clore plutôt que de traiter,
le correctif imposant sinon une quatrième passe d'audit complète pour trois lignes de test.
