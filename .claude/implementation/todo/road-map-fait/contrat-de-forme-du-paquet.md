+++
id = "contrat-de-forme-du-paquet"
title = "Trancher si le formatage et l'enroulement font partie du contrat du paquet"
date = 2026-09-06
source = "revue de dette du 2026-09-06, question posée « quelles dettes méritent le plus mon attention »"
+++

## À faire

Répondre à une question, puis l'outiller : le formatage `ruff format` et l'enroulement à 100
colonnes font-ils partie du contrat du paquet, oui ou non ?

C'est **une seule décision**, et elle solde trois entrées de dette d'un coup. Laissée ouverte, elle
continue de coûter sans que personne ne l'ait choisi : les trois entrées sont classées `aggravee`,
c'est-à-dire que les chiffres ont empiré depuis leur constat — 133 → 157 lignes au-delà de 100
colonnes, 5 → 8 fichiers non formatés, 3 → 6 erreurs `ruff check`. Ces écarts ont été introduits
par des chantiers qui n'avaient aucun moyen de les voir.

Deux issues, et l'entrée ne préjuge pas de laquelle :

- **oui** → la forme entre dans le contrat, et quelque chose l'applique et la vérifie ;
- **non** → les trois entrées de dette partent en `technical-debt-ecarte/` avec ce motif, et
  `contrat.md` cesse de documenter une commande dont on ignore le verdict.

Le point à ne pas manquer : `ruff check .` — la commande que `contrat.md` documente — sort non
nulle sur un dépôt sain. Tant que c'est vrai, on apprend à ignorer son verdict, ce qui rend le
contrôle menteur bien au-delà des lignes qu'il signale.

## Fait le

**2026-10-04, hors chantier** — aucun Chantier n'a porté l'entrée, il n'y a donc pas d'archive
dans `done/`. La question reçoit la réponse **oui** sur ses deux volets, et chacun est outillé :

- **le formatage** : `ruff format`, configuré par un `ruff.toml` à la racine et un par skill,
  appliqué au dépôt et déclaré dans `OUTILLAGE.md` (`uvx ruff format --check .`). La dette
  `ruff-format-jamais-applique` est soldée ;
- **l'enroulement à 100 colonnes** : `rumdl fmt` réenroule la prose Markdown
  (`.rumdl.toml`, section `[MD013]`), déclaré dans `OUTILLAGE.md` (`uvx rumdl fmt --check .`). La
  dette `prose-lignes-allongees-par-la-migration` est soldée.

**Ce qui reste ouvert** : le point à ne pas manquer. `uvx ruff check .` sort toujours non nul, sur
5 erreurs (2 `E501` dans `test_fusion.py`, 3 dans `statusline-command.py`). Les dettes
`ruff-echoue-sur-les-tests-de-list-dir` et `statusline-hors-des-linters` les suivent. Il en va de
même de `trois-lignes-au-dela-de-100-colonnes`, que la convention désormais outillée rend soldable,
mais qui n'a pas encore été soldée. Ruff format est aussi absent des consignes des agents : la
dette `ruff-format-absent-des-agents` le suit.

## Références

- dette : `ruff-format-jamais-applique` — « Le formatage ruff n'a jamais été appliqué au paquet
  list-dir », `aggravee`
- dette : `trois-lignes-au-dela-de-100-colonnes` — « Trois lignes du corpus dépassent l'enroulement
  à 100 colonnes », `aggravee`
- dette : `statusline-hors-des-linters` — « `statusline-command.py` échoue à la commande de lint
  documentée », `aggravee`
- la commande documentée : `skills/implementation-tracker/references/contrat.md`, section
  « Dépendances »
- outillage existant : `skills/list-dir/ruff.toml`, `pyrightconfig.json` à la racine
- les trois entrées ont été relues le 2026-09-06 : `list-dir list
  .claude/implementation/todo/technical-debt --where category=aggravee`
