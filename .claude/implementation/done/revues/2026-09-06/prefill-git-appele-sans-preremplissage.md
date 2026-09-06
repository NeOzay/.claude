+++
id = "prefill-git-appele-sans-preremplissage"
title = "create, migrate et derive lancent git même quand aucun champ n'est prérempli"
date = 2026-08-31
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n "prefill_context(" skills/list-dir/scripts/listdir/store.py
226:        ctx = prefill_context(self.path, self.contract)      # create
281:        ctx = prefill_context(self.path, self.contract)      # migrate
521:        ctx = prefill_context(target, derived.contract)      # derive

$ grep -n -A3 "^def context" skills/list-dir/scripts/listdir/prefill.py
65:def context(list_dir: Path, contract: Contract) -> PrefillContext:
73:    resolved = git("rev-parse", "--show-toplevel", cwd=cwd)
75:    return PrefillContext(list_dir=list_dir, cwd=cwd, contract_name=contract.name, root=root)
```

## Verdict

Les trois opérations construisent toujours leur `PrefillContext` **en tête**, et `context()`
résout toujours la racine par un `git rev-parse` **inconditionnel** : il reçoit bien le contrat en
paramètre, mais ne s'en sert que pour `contract.name`, jamais pour décider s'il y a lieu de
résoudre quoi que ce soit. Aucune paresse n'a été introduite — ni cache interne au premier `_run`,
ni court-circuit quand aucune déclaration ne porte `command`.

Un `fork`/`exec` reste donc payé à chaque `new`, `migrate` et `derive`, y compris sur les listes
qui n'utilisent pas le préremplissage.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
