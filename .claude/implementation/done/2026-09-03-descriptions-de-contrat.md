---
slug: descriptions-de-contrat
titre: Rédiger les descriptions des contrats de dette
branche: descriptions-de-contrat
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-09-03-descriptions-de-contrat.plan.md
brief: .claude/implementation/done/2026-09-03-descriptions-de-contrat.brief.md
audit: .claude/implementation/done/2026-09-03-descriptions-de-contrat.audit.md
créé: 2026-09-03
maj: 2026-09-03
---

## Objectif et périmètre

Repris du brief (`brief:`).

**Symptôme** : « Plusieurs contrats ont leurs champs remplis avec des descriptions vides. »
**But** : que le contrat d'une liste dise ce qu'est une dette — son contenu et sa structure —
champ par champ et section par section, et que `dette.md` renvoie à lui au lieu de le redire.
**Critères de réussite** :
- `grep -rn --include='*.toml' 'description = ""' skills/implementation-tracker/list-dir
  .claude/implementation/todo` ne rend rien, et aucune description de champ ne recopie celle de sa
  liste
- semence et copie restent identiques, gabarit `review.toml` compris (`diff` muet)
- `list-dir validate` passe sur les trois registres
- `list-dir contract "$T/technical-debt-solde"` n'affiche plus quatre fois la même phrase
- les règles de `dette.md` qui décrivent le contenu d'une section ont laissé place à un renvoi
  au contrat

**Hors-périmètre** :
- aucune modification de code
- pas de réécriture des entrées de dette existantes pour les conformer aux descriptions rédigées

**Signaux de dérive** :
- une `description` qui devient un paragraphe : le contrat déclare, il n'argumente pas
- `dette.md` qui cesse d'expliquer comment fonctionnent les dettes et comment les manipuler
- semence et copie qui divergent en fin de passe

## Étapes

- [x] 1. Sections de `technical-debt` — semence + copie — vérif: `grep -c 'description = ""'` → 0, `diff`, `list-dir validate`
- [x] 2. `technical-debt-solde` : 4 champs recopiés + 5 sections — vérif: `list-dir contract … | grep -c "Dette soldée"` → 1, `diff`, `validate`
- [x] 3. `technical-debt-ecarte` : 4 champs recopiés + 5 sections — vérif: `list-dir contract … | grep -c "Sorti du registre"` → 1, `diff`, `validate`
- [x] 4. Gabarit `review.toml` : 4 sections — vérif: `grep -c` → 0, `diff`, `derive` jetable + `contract`
- [x] 5. `dette.md` : les trois règles de contenu cèdent la place à un renvoi au contrat — vérif: `check_pipeline.py` exit 0, aucun titre `##` supprimé
- [x] 6. `templates/review.md` et `gabarit-rapport.md` : renvoi au contrat — vérif: `diff` muet, `check_pipeline.py` exit 0
- [x] 7. Contrôle d'ensemble — vérif: bloc de l'étape 5 du plan, puis relecture des trois `list-dir contract`
- [x] 8. Réserves R1-R3 de l'audit `54090d8` — `dette.md`, `technical-debt-ecarte`, `debt-review/SKILL.md` — vérif: `check_pipeline.py` exit 0, `diff -r` muet, `validate` ×3

## État courant

**Prochaine action** : aucune — chantier terminé.
**Vérification** : `python3 scripts/check_pipeline.py` et `list-dir validate` sur les trois
registres.
**Dernier audit** : `f2c64bf` — RÉSERVES — 2026-09-03 (R1-R3 levées ; R6 corrigée depuis)
**Notes** : le plan a été relu par `plan-reviewer` — verdict RÉSERVES, deux constats non corrigés
(voir journal).

## Journal de décisions

- **2026-09-03** — le contrat porte ce qu'est une dette, `dette.md` renvoie à lui. *Pourquoi* :
  « Le contract est la source de vérité d'une liste » ; `dette.md` garde le fonctionnement et la
  manipulation. *Rejeté* : coexistence des deux proses, qui divergent toujours.
- **2026-09-03** — rédiger dans la semence, copier vers la copie en vigueur, prouver par `diff`.
  *Pourquoi* : rien ne les resynchronise (`semence-et-copie-divergent-sans-controle`).
  *Rejeté* : rédiger deux fois.
- **2026-09-03** — une `description` déclare et décrit, elle ne motive pas : la justification
  d'une règle reste dans `dette.md`, qui renvoie au contrat pour le contenu. *Pourquoi* : une
  description qui argumente devient un paragraphe — signal de dérive du brief. *Rejeté* :
  descriptions TOML multi-lignes absorbant la prose de `templates/review.md`.
- **2026-09-03** — aucune entrée rétroactive au registre pour le second défaut (descriptions de
  champ recopiées, origine d8a06ac), trouvé et corrigé dans ce chantier. *Pourquoi* : le registre
  dit ce qui reste vrai aujourd'hui, pas un journal. *Rejeté* : entrée écrite puis soldée dans la
  foulée, qui entrerait et sortirait sans rien signaler.
- **2026-09-03** — audits de clôture `54090d8` puis `f2c64bf` : RÉSERVES, aucun bloquant. R1, R2,
  R3 et R6 corrigées ; R5 (le critère du brief se lit sans `--include='*.toml'`) consignée sans
  effet sur le verdict.
