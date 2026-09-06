+++
id = "remontee-sarrete-au-premier-claude"
title = "La racine de projet retenue par list-dir est le premier .claude trouvé, pas forcément le bon"
date = 2026-08-30
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n -A12 "def project_root" skills/list-dir/scripts/listdir/definitions.py
84:def project_root(start: Path) -> Path | None:
85-    """Le `.claude` du premier projet trouvé en remontant depuis `start`, ou None.
87-    Un projet est un répertoire qui CONTIENT un `.claude`. La remontée s'arrête au
88-    premier, qui n'est pas nécessairement celui qu'on aurait choisi : `defs`
89-    l'imprime pour que le choix soit visible plutôt que deviné.
94-    here = start.resolve()
95-    for candidate in (here, *here.parents):
96-        if (candidate / CLAUDE).is_dir():

$ grep -n "marqueur\|rev-parse\|REQUIRES" skills/list-dir/scripts/listdir/definitions.py
(aucun résultat)
```

## Verdict

La règle est inchangée : premier `.claude` rencontré en remontant, et la seule atténuation reste
que `defs` imprime la racine retenue — la docstring le dit en toutes lettres. Aucune des trois
issues du `Pour solder` n'a été prise : ni marqueur explicite, ni racine git déclarée aux
`REQUIRES`, ni limite écrite dans `definitions.md`.

L'`Assumé` de l'entrée reste exact — l'arbitrage Q3 a choisi de rendre le point visible plutôt que
de le trancher — et l'entrée existe pour que la décision reste réversible. Elle est donc à sa
place, et pas `pas-une-dette` : ce n'est pas une préférence de style, c'est un choix laissé
explicitement ouvert.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
