+++
id = "patterns-securite-debranches"
title = "Les patterns de sécurité de `git-pre-commit-audit` ne sont plus branchés"
date = 2026-08-14
source = "Identifié par `audit-integre`, hors-périmètre assumé au brief."
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

le skill a été débranché vers `archive/git-pre-commit-audit/` et n'est donc chargé ni
par le modèle ni par l'utilisateur. Ses neuf annexes sont intactes : `security-patterns.md` et huit
grilles par langage (`lang-js-ts`, `lang-python`, `lang-php`, `lang-go`, `lang-java-kotlin`,
`lang-sql`, `lang-infra`, `lang-lua-neovim`).

## Pourquoi c'est gênant

l'auditeur juge la conformité à l'intention et la qualité du code, mais
ne fait aucune détection de secrets ni de patterns de sécurité par langage. Cette capacité existe,
vérifiée, et n'est plus appelée par rien.

## Pour solder

reprendre les grilles dans un chantier dédié, soit comme axe supplémentaire de
l'auditeur, soit comme skill séparé de pré-commit.

## Assumé

le débranchement était le but du chantier — le skill ne lisait ni le brief ni les
critères de réussite, d'où son remplacement par `agents/implementation-auditor.md`. La reprise des
patterns était hors-périmètre, écrite au brief.
