+++
id = "controle-1-garde-fou-jamais-teste"
title = "Le contrôle 1 du garde-fou de pipeline n'a jamais rien testé"
date = 2026-08-16
source = "Identifié par `revue-plan-deleguee`, constaté au point 1 de sa clôture. Anomalie préexistante, reproduite à l'identique sur `master`."
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`scripts/check-pipeline.sh:47` et `:65` comptaient les renvois vers le contrat avec la
classe `[a-zà-ÿ0-9-]`. Le range `à-ÿ` est une collation invalide : `/usr/bin/grep` échouait sur
`Invalid collation character`, `total` valait `0`, et le script concluait « aucun renvoi trouvé — le
contrat n'est cité nulle part », en sortant systématiquement en code 1.

## Soldé le

**Soldé le 2026-08-16 par le chantier `revue-plan-deleguee`** — range remplacé par `[^)]` aux deux
endroits. Le correctif évident `[a-z0-9-]` a été **écarté** : il tronquait les ancres accentuées du
contrat (`#format-détape-et-délégabilité`, `#autorité-et-divergence`), transformant un contrôle mort
en faux « ancre morte ». `[^)]` ne dépend d'aucune collation et capture l'ancre entière.
Établi par : `bash scripts/check-pipeline.sh` → « 1. Renvois vers le contrat ✓ 29 renvois, tous
résolvent », « Pipeline conforme. », `EXIT=0` ; les six contrôles passent.

## Pourquoi c'est gênant

le contrôle 1 détecte les ancres mortes vers `contrat.md`, soit la
dérive que la centralisation des règles existe pour empêcher. Il ne produisait pas un faux positif :
il rapportait une anomalie constante, indistinguable d'une vraie, et faisait échouer chaque clôture.
Un contrôle qui crie toujours ne se lit plus.

## Pour solder

<OPTIONNEL>

## Assumé

<OPTIONNEL>
