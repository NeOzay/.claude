+++
id = "garde-version-jamais-executee"
title = "La garde de version de `list-dir.py` n'est vérifiée que par son rang, jamais exécutée"
date = 2026-08-24
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ sed -n '244,258p' skills/list-dir/scripts/tests/test_entree_cli.py
# ------------------------------------------------------------- garde de version
[…]
        if isinstance(node, ast.If) and "version_info" in ast.dump(node.test)

$ grep -n "runpy\|monkeypatch.*version_info\|SystemExit(2)" skills/list-dir/scripts/tests/test_entree_cli.py
(aucun résultat)
```

## Verdict

Le seul test de la garde reste celui du **rang** : il parcourt l'arbre `ast` pour vérifier que le
bloc `sys.version_info` précède le premier import de `listdir`. Rien n'exécute le corps de la
garde — ni `runpy.run_path`, ni un `sys.version_info` truqué, et aucune assertion ne porte sur le
message écrit sur stderr ou sur le code 2.

C'est la voie que le `Pour solder` décrivait, et elle n'a pas été prise. Le constat tient tel
quel, sans extension.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
