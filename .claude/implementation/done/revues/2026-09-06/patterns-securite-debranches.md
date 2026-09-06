+++
id = "patterns-securite-debranches"
title = "Les patterns de sécurité de `git-pre-commit-audit` ne sont plus branchés"
date = 2026-08-14
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ ls archive/git-pre-commit-audit/references/
lang-go.md  lang-infra.md  lang-java-kotlin.md  lang-js-ts.md  lang-lua-neovim.md
lang-php.md  lang-python.md  lang-sql.md  security-patterns.md

$ grep -rn "security-patterns\|lang-python\|grilles" agents/ skills/ | grep -v archive
(aucun résultat)
```

## Verdict

Les neuf annexes sont toujours dans `archive/`, intactes, et **rien** hors de l'archive ne les
appelle — ni `agents/implementation-auditor.md`, ni aucun skill. La capacité existe et reste
débranchée, exactement comme au constat. Le fait est vrai et l'entrée est bien une dette (une
capacité vérifiée et non appelée), donc ni `non-pertinent` ni `pas-une-dette`.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
