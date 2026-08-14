---
slug: audit-integre
titre: Audit intègre du pipeline de skills
branche: audit-integre
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/plans/linked-toasting-graham.md
brief: .claude/implementation/audit-integre.brief.md
créé: 2026-08-14
maj: 2026-08-14
audit: .claude/implementation/audit-integre.audit.md
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : tous les points de contrôle du pipeline sont confiés au modèle qui vient de produire
le travail — confrontation plan ↔ brief (`intent-brief` Étape 7), bloc `VÉRIFICATION` auto-déclaré
par `step-implementer`, confrontation aux critères à la clôture (`cloture.md:8`). Aucun ne laisse de
trace versionnée. Le seul audit outillé, `git-pre-commit-audit`, ne lit ni le brief ni les critères.

**But** : un audit réalisé par un sous-agent indépendant, tracé dans le fichier de suivi, et dont
l'avis favorable conditionne la clôture.

**Critères de réussite** :
- `git-pre-commit-audit` n'est plus appelable, ni par le modèle ni par l'utilisateur
- un audit tourne systématiquement avant toute clôture d'implémentation
- l'audit est exécuté par un sous-agent, pas par la session de cadrage
- le fichier de suivi porte le commit audité (SHA) et le verdict
- une clôture sans avis favorable ne va pas au bout

**Hors-périmètre** : pas de remplacement de `git-pre-commit-audit` par un équivalent — il est
débranché, et la reprise de ses fonctionnalités (secrets, patterns de sécurité) fera l'objet d'un
prochain chantier.

**Signaux de dérive** :
- si l'auditeur se met à corriger le code au lieu de le juger, c'est raté
- si le skill d'audit déborde d'une page, c'est raté
- si le dispositif rallonge la clôture au point qu'on l'esquive, c'est raté

## Étapes

- [x] 1. Débrancher `git-pre-commit-audit` — `skills/git-pre-commit-audit/` → `archive/` — vérif: `ls skills/ | grep -c git-pre-commit-audit` → 0
- [x] 2. Créer l'agent auditeur — `agents/implementation-auditor.md` — vérif: `head -6 agents/implementation-auditor.md` (frontmatter `model: opus`, tools sans Edit)
- [x] 3. Procédure d'audit et gabarit du rapport — `skills/implementation-tracker/references/audit.md` — vérif: `grep -c "400\|DÉFAVORABLE\|étapes restantes" skills/implementation-tracker/references/audit.md`
- [x] 4. Brancher l'audit dans le tracker — `skills/implementation-tracker/SKILL.md` — vérif: `grep -n "audit.md\|\.audit\.md" skills/implementation-tracker/SKILL.md`
- [x] 5. Audit obligatoire à la clôture — `skills/implementation-tracker/references/cloture.md` — vérif: `grep -n "audit" skills/implementation-tracker/references/cloture.md`
- [x] 6. Gabarit du suivi — `skills/implementation-tracker/references/gabarit-suivi.md` — vérif: `grep -n "audit:" skills/implementation-tracker/references/gabarit-suivi.md`
- [x] 7. Rodage : auditer ce chantier avec le nouvel agent — `.claude/implementation/audit-integre.audit.md` — vérif: le rapport existe et porte des sorties de commande réelles
- [x] 8. Traiter les réserves R1, R3, R4, R5, R6 de l'audit — `agents/implementation-auditor.md`, `skills/implementation-tracker/references/audit.md` — vérif: nouvel audit complet FAVORABLE

## État courant

**Prochaine action** : aucune — chantier clos le 2026-08-14.
**Vérification** : `ls skills/` et ouverture d'une session neuve (le skill ne doit plus apparaître).
**Dernier audit** : `4c5bd98` — FAVORABLE — 2026-08-14 (rapport : `audit-integre.audit.md`)
**Notes** : `execution: direct` — les étapes produisent du markdown de prompt, sans commande de
vérification exécutable au sens d'un test. `archive/README.md` ajouté au passage pour que le
dossier créé à l'étape 1 dise pourquoi il existe.

## Journal de décisions

- **2026-08-14** — Agent `implementation-auditor` + `references/audit.md`, pas de sixième skill.
  *Pourquoi* : l'audit est un moment du chantier, pas un outil séparé ; évite de dupliquer le
  routage du tracker. *Rejeté* : skill autonome `/implementation-audit`.
- **2026-08-14** — Auditeur en Opus, là où `step-implementer` est en Sonnet. *Pourquoi* : il juge
  au lieu d'exécuter, et tourne une à deux fois par chantier. *Rejeté* : Sonnet (un juge plus
  faible que l'auteur valide ce qu'il ne comprend pas).
- **2026-08-14** — Blocage de la clôture par discipline écrite dans `cloture.md`, pas par hook.
  *Pourquoi* : régime de tous les autres contrôles du tracker, rien à maintenir. *Rejeté* : hook
  `PreToolUse` sur `git merge --squash` (faux positifs sur tout squash manuel).
- **2026-08-14** — Rapport dans `<slug>.audit.md`, écrit par l'agent lui-même ; le suivi ne porte
  que SHA, verdict et renvoi. *Pourquoi* : garde le détail hors du contexte de session, comme la
  délégation d'étape garde les diffs. *Rejeté* : section `## Audits` dans le fichier de suivi.
- **2026-08-14** — Verdict défavorable → `statut: bloqué` + journal, **étapes intactes**.
  *Pourquoi* : le traitement des remarques se décide au cas par cas. *Rejeté* : génération
  automatique d'étapes correctives.
- **2026-08-14** — Audit `fe80476` : RÉSERVES, aucun bloquant. Signal de dérive « une page » jugé
  **non déclenché** par l'utilisateur : il se compte **par fichier**, pas sur le cumul du
  dispositif. *Pourquoi* : prompt d'agent et procédure d'appelant sont deux artefacts distincts.
- **2026-08-14** — Étape 8 ajoutée hors plan pour traiter cinq réserves de l'audit (R1 champ
  `audit:` orphelin, R3 racine du dépôt absente du contrat, R4 `..` contre `...` sur le seuil,
  R5 coquille, R6 constats non numérotés). *Pourquoi* : R3 et R4 sont des défauts fonctionnels,
  et R6 a rendu le premier rapport partiellement illisible.
- **2026-08-14** — Audit `4c5bd98` : FAVORABLE, réserves levées et vérifiées. Trois constats
  reportés au chantier suivant, aucun bloquant : asymétrie de rédaction sur la racine du dépôt
  entre les deux contrats ; la confrontation plan ↔ brief d'`intent-brief` reste auto-jugée et sans
  trace (hors critères de ce chantier) ; une étape corrective née d'un audit doit porter une
  vérification sur son correctif, pas sur le verdict à venir, sous peine de circularité avec le
  point 1 de `cloture.md`.
- **2026-08-14** — Les filtres `ls … | grep -vE '\.(brief|audit)\.md$'` du tracker ne filtrent
  rien tant que le hook `rtk` réécrit `ls` en y ajoutant une colonne de taille : l'ancre `$` ne
  matche plus. *Pourquoi le noter* : les `*.brief.md` et `*.audit.md` remontent dans les listings
  d'implémentations. À corriger au chantier suivant (filtrer sur le nom, pas sur la fin de ligne).
