+++
id = "garde-fou-borne-a-skills"
title = "Les contrôles de chemin ne regardent que skills/, alors qu'un point converti vit hors de skills/"
date = 2026-08-29
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n 'only="skills"' scripts/check_pipeline.py
305:  check_empreintes
493:  check_portabilite
581:  check_chemins_skill
643:  check_renvois_skill

$ grep -n "\.claude/implementation" scripts/check_pipeline.py
(aucun résultat)
```

## Verdict

Le périmètre est inchangé : les contrôles visés lisent toujours `markdown_files(root,
only="skills")`, et aucun d'eux ne connaît `.claude/implementation/`. Un `$HOME/.claude/skills/…`
réintroduit dans `todo/README.md` resterait invisible, exactement comme au constat.

L'entrée nomme « les contrôles 6, 7 et 8 » ; le fichier en compte aujourd'hui **quatre** bornés de
la même façon (`check_empreintes` s'y est ajouté). Ce n'est pas une aggravation du défaut décrit —
la surface non couverte est la même, `.claude/implementation/` — mais l'entrée désigne ses cibles
par un numéro qui a bougé.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

**Correction proposée à l'arbitrage** : remplacer « les contrôles 6, 7 et 8 » par les **noms** des
fonctions (`check_empreintes`, `check_portabilite`, `check_chemins_skill`, `check_renvois_skill`),
qui ne se périment pas avec l'ordre du fichier — même raison que l'interdiction des numéros de
ligne au registre.

## Arbitrage

**Correction appliquée le 2026-09-06.** Les contrôles sont désormais désignés par leurs noms de
fonction (`check_empreintes`, `check_portabilite`, `check_chemins_skill`, `check_renvois_skill`) au
lieu des rangs « 6, 7 et 8 », dans le Constat comme dans le Pour solder. La raison est écrite dans
l'entrée : un numéro de contrôle se périme comme un numéro de ligne.
