+++
id = "source-verbatim-perd-italiques"
title = "Le champ `source` est déclaré « verbatim » et perd les délimiteurs d'italique"
date = 2026-08-23
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n "verbatim" .claude/implementation/todo/technical-debt/.list/contract.toml
25:description = "le chantier qui l'a identifiée et où il l'a écrit, verbatim"

$ list-dir show .claude/implementation/todo/technical-debt source-verbatim-perd-italiques | grep '^source'
source = "chantier `format-registres`, R8 des audits de clôture"

$ grep -h '^source = ' .claude/implementation/todo/technical-debt/*.md | grep -c '^source = "\*'
0
$ grep -h '^source = ' .claude/implementation/todo/technical-debt/*.md | wc -l
51
```

## Verdict

Le contrat promet toujours « verbatim » et **aucune** valeur du champ `source`, sur les 51 entrées
du registre actif, ne porte de délimiteur d'italique : la mise en forme est absente partout, comme
au constat. Aucune des deux voies du `Pour solder` n'a été prise — ni la description alignée sur ce
qui est réellement conservé, ni la migration refaite.

Le constat est vrai et l'entrée est bien une dette : c'est le contrat qui fait foi pour qui lit la
liste, et il promet plus qu'il ne tient. Ce n'est donc pas `pas-une-dette`, malgré le caractère
mineur de l'écart.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
