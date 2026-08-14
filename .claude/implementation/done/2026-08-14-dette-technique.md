---
slug: dette-technique
titre: Registre de dette technique normalisé
branche: dette-technique
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-08-14-dette-technique.plan.md
brief: .claude/implementation/done/2026-08-14-dette-technique.brief.md
audit: .claude/implementation/done/2026-08-14-dette-technique.audit.md
créé: 2026-08-14
maj: 2026-08-14
---

## Objectif et périmètre

Repris du brief (`brief:`).

**Symptôme** : « Il faudrait un moyen normalisé pour tracer les dettes pour de futurs chantiers ».
Les constats de dette produits par l'audit finissent dans `<slug>.audit.md`, archivé en
`.claude/implementation/done/` à la clôture — un fichier que personne ne relit. Les six dettes du
chantier `audit-integre` clos le 2026-08-14 n'existent nulle part ailleurs.

**But** : un document de dette normalisé, alimenté par le pipeline, sur le modèle de
`/home/Benoit/projects/ebook-translator/docs/TECHNICAL_DEBT.md`.

**Critères de réussite** :

- `.claude/implementation/todo/technical-debt.md` existe et porte les six dettes connues du chantier
  `audit-integre`, chacune datée, ordonnée de la plus ancienne à la plus récente, avec son chantier
  d'origine.
- La procédure de clôture porte une étape d'alimentation **située après l'audit et avant
  l'archivage**.
- L'auditeur n'a toujours qu'un seul fichier en écriture, et aucune mention de `todo/` dans
  `agents/implementation-auditor.md`.
- L'abandon propose l'alimentation au lieu de l'imposer.

**Hors-périmètre** :

- Pas de lecture automatique du répertoire par le pipeline — `intent-brief` ne consulte pas `todo/`
  au cadrage. Le registre est lu quand l'utilisateur le demande.
- Pas de `road-map.md` dans ce chantier : l'emplacement doit seulement pouvoir l'accueillir.

**Signaux de dérive** :

- **Si le même constat peut être écrit deux fois dans `todo/`, c'est raté.** Un chantier subit
  plusieurs audits, chacun rejugeant le diff entier : les mêmes constats ressortent par
  construction. Le rapport est un journal, le registre est un état.
- Si l'auditeur gagne un droit d'écriture sur `todo/`, s'arrêter.

## Étapes

- [x] 1. Fichier de référence du registre — `skills/implementation-tracker/references/dette.md` — vérif: `test -f skills/implementation-tracker/references/dette.md`
- [x] 2. README du répertoire — `.claude/implementation/todo/README.md` — vérif: `test -f .claude/implementation/todo/README.md`
- [x] 3. Amorcer le registre avec les six dettes d'`audit-integre` — `.claude/implementation/todo/technical-debt.md` — vérif: `grep -c '^## 2026-' .claude/implementation/todo/technical-debt.md`
- [x] 4. Emplacement et déclencheur au tableau de l'Étape 4 — `skills/implementation-tracker/SKILL.md` — vérif: `grep -n 'todo/' skills/implementation-tracker/SKILL.md`
- [x] 5. Étape d'alimentation à la clôture, proposition à l'abandon — `skills/implementation-tracker/references/cloture.md` — vérif: `grep -n 'dette.md' skills/implementation-tracker/references/cloture.md`
- [x] 6. Pas d'écriture au retour d'audit — `skills/implementation-tracker/references/audit.md` — vérif: `grep -n 'registre' skills/implementation-tracker/references/audit.md`
- [x] 7. Traiter R1 (mise en index du registre) et R2 (ligne « Dernière vérification ») — `references/cloture.md`, `references/dette.md`, `todo/technical-debt.md` — vérif: `grep -n 'index' skills/implementation-tracker/references/cloture.md && grep -c 'Dernière vérification' skills/implementation-tracker/references/dette.md .claude/implementation/todo/technical-debt.md`
- [x] 8. Traiter R3 à R7 du second audit — `references/cloture.md`, `SKILL.md`, `todo/technical-debt-solde.md` — vérif: `test -e .claude/implementation/todo/technical-debt-solde.md && grep -n 'git add .claude/implementation/todo' skills/implementation-tracker/references/cloture.md && grep -n 'README.md' skills/implementation-tracker/SKILL.md`
- [x] 9. Traiter R8 à R11 du troisième audit — `references/dette.md`, `references/cloture.md`, `references/audit.md` — vérif: `grep -n 'en entier' skills/implementation-tracker/references/dette.md && grep -n 'Les \*\*deux\*\* branches' skills/implementation-tracker/references/cloture.md`

## État courant

**Prochaine action** : chantier clos. Le registre vit en `.claude/implementation/todo/`, alimenté
par le point 2 de `references/cloture.md`.
**Vérification** : bloc « Vérification d'ensemble » du plan, **corrigé** — `grep '^## ' … | sort -c`
triait la ligne entière, titres inclus, et échouait à tort ; la bonne commande est
`grep '^## ' .claude/implementation/todo/technical-debt.md | cut -d' ' -f2 | sort -c`.
**Dernier audit** : `343f180` — RÉSERVES — 2026-08-14 (R3 à R7 traités, R5 partiellement ; nouveaux
R8 « dernier rapport » vs rapport entier, R9 abandon *garder la branche*, R10 note périmée,
R11 mise en forme)
**Notes** : `todo/technical-debt-solde.md` a été créé à l'étape 8 (R3) — l'écart au brief signalé en
cours de chantier est refermé, le répertoire porte bien les deux fichiers annoncés.

## Journal de décisions

- **2026-08-14** — L'orchestrateur écrit le registre, une seule fois, à la clôture ; l'auditeur n'y
  touche pas. *Pourquoi* : trois audits passent sur un chantier et rejugent chacun le diff entier —
  un auditeur en contexte isolé ne peut ni dédupliquer ni retirer ce qu'un correctif a soldé.
  *Rejeté* : écriture par l'auditeur (doublons garantis).
- **2026-08-14** — Entrées horodatées, sans numéro, ordonnées de la plus ancienne à la plus récente.
  *Pourquoi* : la numérotation oblige à réindexer à chaque retrait. *Rejeté* : le `## N.` du modèle
  `ebook-translator`.
- **2026-08-14** — Le registre est mis à l'index dès son écriture (`git add
  .claude/implementation/todo/`), au point 2 de la clôture. *Pourquoi* : R1 — au premier usage les
  fichiers ne sont pas suivis, l'aplatissement ne reprend que le commité, et l'écriture serait
  perdue sans une seule erreur. *Rejeté* : compter sur le commit du point 3, qui ne stage que le
  suivi.
- **2026-08-14** — L'alimentation relit le rapport d'audit **entier**, pas sa dernière section.
  *Pourquoi* : R8 — rien n'oblige un auditeur à reprendre les réserves des passages précédents ;
  une réserve non traitée de la première section disparaîtrait sans erreur. *Rejeté* : imposer la
  reprise au gabarit du rapport, ce qui élargirait le contrat de l'agent.
- **2026-08-14** — Clôture prononcée sur un verdict `RÉSERVES` (`343f180`), R8 à R11 traités mais
  **non rejugés**, par décision explicite de l'utilisateur. *Pourquoi* : trois audits sans bloquant,
  constats de plus en plus fins. *Rejeté* : le quatrième audit complet qu'exige `audit.md:80`.
- **2026-08-14** — À l'abandon, la décision de verser au registre se prend avant le sort du travail,
  mais l'écriture se fait une fois sur `base:`. *Pourquoi* : R5 — la branche abandonnée n'est jamais
  aplatie, une entrée écrite dessus n'atteindrait donc jamais `base:`. *Rejeté* : écrire sur
  `<slug>` comme le reste de l'abandon.
- **2026-08-14** — Un solde exige la commande exécutée qui l'établit et sa sortie réelle, sinon
  l'entrée reste. *Pourquoi* : c'est l'auteur du travail qui juge son propre solde ; même principe
  que le point d'intégrité de l'auditeur. *Rejeté* : constat du solde confié à l'auditeur (élargit
  son mandat).
