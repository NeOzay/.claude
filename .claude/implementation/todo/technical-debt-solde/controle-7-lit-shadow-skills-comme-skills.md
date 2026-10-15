+++
id = "controle-7-lit-shadow-skills-comme-skills"
title = "Le contrôle 7 lit shadow-skills/x/… comme le chemin de skill skills/x/…"
date = 2026-10-06
severite = "avertissement"
chantier = "mods-a-la-racine-des-skills"
reference = "journal du Suivi"
pin = true
source = "chantier `mods-a-la-racine-des-skills`, Journal de décisions du Suivi, 2026-10-06"
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Le motif `CHEMIN_SKILL` de `scripts/check_pipeline.py` n'exclut pas `-` de sa garde arrière
(`(?<![\w/.])`) : dans `shadow-skills/claude-code-mods/…`, il reconnaît le chemin de skill
`skills/claude-code-mods/…`, qui n'existe pas. Constaté le 2026-10-06 : un lien de
`skills/mod-commun/SKILL.md` vers `claude-code-mods` a été refusé par le contrôle 7.

## Pourquoi c'est gênant

Un renvoi correct vers un Shadow-skill fait échouer le garde-fou ; l'auteur le contourne en
retirant le lien, et la documentation perd un renvoi utile pour satisfaire un faux positif.

## Pour solder

Ajouter `-` à la garde arrière du motif, avec un test dans `scripts/tests/` qui fait passer un
lien vers `shadow-skills/<nom>/SKILL.md` ; `python3 scripts/check_pipeline.py` reste vert.

## Assumé

<OPTIONNEL>

## Soldé le

**2026-10-15, chantier `solder-sept-dettes`** — la garde arrière de `CHEMIN_SKILL` exclut aussi
`-` : `shadow-skills/x/…` ne se lit plus comme `skills/x/…`. Le lien vers `claude-code-mods` est
rétabli dans `skills/mod-commun/SKILL.md`. Une citation `shadow-skills/…` qui n'est pas un lien
`](../…)` n'est plus vérifiée par aucun contrôle, perte acceptée et dite dans le commentaire du
motif.

Établi par : avant le correctif, `python3 scripts/check_pipeline.py` → « ✗
skills/mod-commun/SKILL.md:16 → chemin de skill inexistant : skills/claude-code-mods/SKILL.md » ;
après → « ✓ 34 chemins de skill cités, tous existent ».
`~/.claude/.venv/bin/python -m pytest scripts/tests/test_controle_7.py -k shadow` → `2 passed`, les
deux tests échouant sur l'ancien motif.
