+++
id = "amorcage-puis-reprise-aboutit-a-un-arret"
title = "« Amorcer puis reprendre l'étape » aboutit toujours à un arrêt, sans que la puce le dise"
date = 2026-08-30
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ sed -n '112,115p' skills/debt-review/SKILL.md
- **`ABSENT` sur les trois** → les registres n'existent pas encore dans ce projet. Les amorcer,
  puis reprendre l'étape : [Registre de dette](../implementation-tracker/references/dette.md) en
  porte la procédure. Ne pas la recopier ici, et ne créer aucun répertoire à la main — l'amorçage
  est une commande.
```

## Verdict

La puce dit toujours « les amorcer, puis reprendre l'étape » et **ne dit toujours pas** que la
reprise rendra `VIDE` sur les trois, ni que c'est la fin normale d'un premier passage. La
demi-phrase que le `Pour solder` demandait n'a pas été écrite.

La puce `VIDE` sur `technical-debt`, trois lignes plus bas, précise bien que « ce n'est pas une
anomalie » — mais elle parle d'un registre soldé jusqu'à la dernière entrée, pas d'un registre qui
vient d'être amorcé. Le lecteur qui suit l'enchaînement n'est donc toujours pas prévenu.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
