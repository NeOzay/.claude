---
slug: revue-plan-deleguee
titre: Déléguer la revue de plan à un sous-agent
branche: revue-plan-deleguee
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-08-16-revue-plan-deleguee.plan.md
brief: .claude/implementation/done/2026-08-16-revue-plan-deleguee.brief.md
audit: .claude/implementation/done/2026-08-16-revue-plan-deleguee.audit.md
créé: 2026-08-16
maj: 2026-08-16
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : `intent-brief` et `implementation-tracker` savent tous deux faire le plan et la
confrontation plan ↔ brief. Le tracker duplique le flux avec une clause d'exception
(`SKILL.md:126-127`), arbitrée par une condition que le modèle doit détecter lui-même.

**But** : couper `## Étape 6 — Passage au plan` d'`intent-brief` pour passer directement dans
`implementation-tracker` et créer le plan à l'intérieur. Migrer la comparaison brief ↔ plan dans le
tracker, réalisée par un sous-agent qui vérifie aussi la qualité du plan.

**Critères de réussite** :

- une seule voie mène au plan : `intent-brief` → `implementation-tracker` → plan
- la comparaison brief ↔ plan est exécutée par un sous-agent, pas par le modèle de cadrage
- le sous-agent juge aussi la qualité du plan
- pas de brief → le sous-agent juge la qualité du plan seulement
- la revue a lieu **avant** que le plan soit présenté à l'utilisateur ; verdict et plan arrivent
  dans le même `ExitPlanMode`

**Périmètre élargi le 2026-08-16** : `scripts/check-pipeline.sh` s'ajoute aux quatre fichiers
d'origine, sur décision explicite de l'utilisateur à la clôture (voir journal). Le brief n'est pas
modifié : [Autorité et divergence](../../skills/implementation-tracker/references/contrat.md#autorité-et-divergence).

**Hors-périmètre** : quatre fichiers, pas un de plus — `skills/intent-brief/SKILL.md`,
`skills/implementation-tracker/SKILL.md`, `agents/plan-reviewer.md` (nouveau) et
`skills/implementation-tracker/references/contrat.md`.

- `gabarit-brief.md`, `gabarit-suivi.md`, `audit.md`, `dette.md`, `cloture.md` ne sont pas touchés
- `agents/implementation-auditor.md` et `agents/step-implementer.md` ne sont pas touchés
- pas d'alignement général des renvois du pipeline : ce n'est pas ce chantier

**Signaux de dérive** :

- si `intent-brief` conserve la moindre mécanique de plan ou de confrontation après la coupe,
  c'est raté — la duplication supprimée serait seulement déplacée
- si le prompt de `plan-reviewer` l'amène à proposer des alternatives de conception plutôt qu'à
  contrôler un contrat, c'est raté
- si une règle est dupliquée dans un `SKILL.md` au lieu d'être définie dans `contrat.md` avec un
  renvoi ancré, s'arrêter — ça défait le commit `3ebf3fe`

## Étapes

- [x] 1. Créer l'agent de revue de plan — `agents/plan-reviewer.md` — vérif: `grep -c '^## ' agents/plan-reviewer.md` = 5
- [x] 2. Porter le compte des agents à trois — `skills/implementation-tracker/references/contrat.md` — vérif: `grep -c 'plan-reviewer' skills/implementation-tracker/references/contrat.md` ≥ 1
- [x] 3. Réécrire l'Étape 2 du tracker, points 2-3 — `skills/implementation-tracker/SKILL.md` — vérif: `grep -c 'Étapes 6 et 7' skills/implementation-tracker/SKILL.md` = 0
- [x] 4. Couper les Étapes 6-7 d'intent-brief et réécrire sa sortie — `skills/intent-brief/SKILL.md` — vérif: `grep -c 'EnterPlanMode\|ExitPlanMode\|Confrontation plan' skills/intent-brief/SKILL.md` = 0

## État courant

**Prochaine action** : aucune — chantier clos le 2026-08-16.

**Vérification** : `git diff --stat master...revue-plan-deleguee` — sept fichiers : les quatre du
périmètre de production (`agents/plan-reviewer.md`, les deux `SKILL.md`, `contrat.md`) et les trois
artefacts de traçabilité que le tracker impose de versionner (brief, suivi, plan).

**Dernier audit** : `1adfb84` — RÉSERVES — 2026-08-16   (aucun bloquant)

**Notes** : le plan de ce chantier a lui-même été relu par un sous-agent avant présentation, en
appliquant par anticipation le dispositif à construire. Verdict `RÉSERVES`, six constats de qualité
corrigés avant validation.

**Registre de dette** — une entrée versée à la clôture : la prémisse de harness sans repli écrit
(`R4`). Deux entrées **soldées** : « La confrontation plan ↔ brief reste auto-jugée et sans trace »,
dont ce chantier retient l'option « regard extérieur » ; et « Le contrôle 1 du garde-fou de pipeline
n'a jamais rien testé », corrigé sur décision de l'utilisateur (voir journal).

## Journal de décisions

- **2026-08-16** — `plan-reviewer` reçoit **trois chemins absolus** (racine, plan, brief) et lit
  tout lui-même ; aucune exception n'est ajoutée au contrat des sous-agents. *Pourquoi* : le
  harness assigne le fichier de plan dès l'entrée en plan mode et autorise son écriture — la
  prémisse du brief (« le plan n'existe sur aucun disque avant `ExitPlanMode` ») est fausse,
  constaté sur ce chantier même. *Rejeté* : transmettre le plan en clair dans le prompt avec une
  exception nommée au contrat, décision `(dit)` du brief que l'utilisateur a explicitement
  ratifiée en validant le plan.
- **2026-08-16** — périmètre élargi à `scripts/check-pipeline.sh` pour corriger le contrôle 1 du
  garde-fou, mort depuis toujours sur un range de collation invalide. *Pourquoi* : décision
  explicite de l'utilisateur à la clôture, `cloture.md` exigeant de traiter une sortie ≠ 0 avant de
  clore. *Rejeté* : le correctif évident `[a-z0-9-]`, qui tronquait les ancres accentuées du
  contrat et aurait transformé un contrôle mort en faux positif — `[^)]` retenu à la place.
- **2026-08-16** — la règle « ne jamais corriger le plan d'office » reçoit une exception : les
  défauts purement rédactionnels relevés en `QUALITÉ` (citation fausse, commande de vérification
  inopérante) se corrigent sans arbitrage, mais se disent quand même. *Pourquoi* : sans elle, un
  verdict `RÉSERVES` portant sur une coquille imposerait un aller-retour à l'utilisateur pour
  chaque erreur de frappe. *Rejeté* : la règle absolue du brief, qui n'anticipait pas la
  distinction entre écart d'intention et défaut de rédaction. Écart relevé en `R2` de l'audit du
  2026-08-16.
- **2026-08-16** — le rapport de revue de plan n'est persisté dans aucun fichier, contrairement aux
  rapports d'`implementation-auditor`. *Pourquoi* : un plan pas encore accepté peut changer
  plusieurs fois ; un historique de verdicts sur des versions mortes n'a pas de valeur.
  *Rejeté* : un `<slug>.plan-review.md` sur le modèle de `<slug>.audit.md`.
