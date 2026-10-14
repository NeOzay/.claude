+++
id = "deux-conventions-de-mode-de-defaillance"
title = "Deux conventions de rédaction du mode de défaillance coexistent sans règle"
date = "2026-09-05"
severite = "avertissement"
chantier = "decoupe-contrat-liste"
reference = "R6"
pin = true
source = "chantier `decoupe-contrat-liste`, réserve R6 de l'audit de clôture"
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Deux formes servent à écrire un mode de défaillance : un bloc cité à part
(`> *Mode de défaillance* — …`), ou une phrase intégrée au corps du texte. Le chantier
`decoupe-contrat-liste` a intégré au texte les treize blocs de `contrat-liste.md` ; les références
de `list-dir` n'en portent plus aucun.

Le 2026-09-17, le chantier `skill-convention` a tranché pour l'intégration au texte, dans
`shadow-skills/skill-convention/references/prose.md`, section « Chaque règle porte son motif, dans
la prose » : les blocs cités qui restent sont des écarts. On en comptait alors 44.

Le 2026-10-14, il en reste 45 ; `OUTILLAGE.md` en a gagné trois depuis que la règle est écrite :

| Fichier | 2026-09-17 | 2026-10-14 |
|---|---|---|
| `OUTILLAGE.md` | 6 | 9 |
| `skills/debt-review/` (`SKILL.md` 9, `categories.md` 7, `gabarit-rapport.md` 1) | 17 | 17 |
| `skills/implementation-tracker/references/` (`contrat.md` 11, `dette.md` 2, `road-map.md` 2) | 17 | 15 |
| `skills/git-smart-commit/references/` (un par référence) | 4 | 4 |

Établi par : `grep -rIn '^>.*Mode de défaillance' OUTILLAGE.md skills/ shadow-skills/ agents/ |
cut -d: -f1 | sort | uniq -c`.

## Pourquoi c'est gênant

Le prochain chantier qui touche une référence tranchera par imitation du fichier qu'il a sous les
yeux, ce qui fige l'écart au lieu de le résorber : chaque fichier garde sa forme, et la forme finit
par dépendre de qui a écrit en dernier. La règle écrite n'y a pas suffi : les trois blocs ajoutés à
`OUTILLAGE.md` l'ont été après elle.

Le coût n'est pas dans le fond, intégralement conservé de part et d'autre, mais dans la lecture :
un bloc cité se repère d'un coup d'œil et se compte au `grep`, un mode de défaillance fondu dans
la prose ne se retrouve qu'en lisant. Deux des treize de `list-dir` ne sont d'ailleurs plus
identifiables par leur formulation d'origine — l'audit a dû les retrouver par leur contenu.

## Pour solder

1. Ajouter à `scripts/check_pipeline.py` un contrôle qui compte les blocs cités de mode de
   défaillance et échoue au-delà d'un plafond, 45 au départ, abaissé à chaque réécriture : la
   dérive s'arrête avant que la réécriture ne soit finie.
2. Réécrire les 45 blocs en intégrant leur contenu au texte de la règle qu'ils accompagnent, sans
   rien perdre du fond, fichier par fichier.
3. Le plafond à 0, le contrôle refuse tout bloc cité ; la commande du Constat ne rend plus rien.

## Assumé

<OPTIONNEL>
