---
name: implementation-tracker
description: >
  Définit et suit une implémentation en cours sur plusieurs discussions. Maintient un fichier
  de suivi versionné par feature (objectif, périmètre, étapes, état courant, journal de décisions)
  dans .claude/implementation/. Skill exclusivement manuelle : elle s'invoque uniquement via
  /implementation-tracker, typiquement en début de discussion.
disable-model-invocation: true
argument-hint: "[@chemin/vers/suivi.md | close]"
---

# Implementation Tracker

Fichier de suivi **par feature**, versionné dans le repo, qui survit aux discussions.
Source de vérité de l'implémentation en cours : objectif, périmètre, étapes, état, décisions.

Invocation manuelle uniquement :

- `/implementation-tracker` → liste les implémentations, propose reprise ou création
- `/implementation-tracker @chemin/vers/fichier.md` → charge directement ce fichier de suivi
- `/implementation-tracker close` → clôture l'implémentation en cours (Phase 5)
- `/implementation-tracker abandon` → abandonne un chantier sans le livrer (Phase 6)

---

## Emplacement

Arborescence, nommage des fichiers et règle du slug :
[Arborescence et nommage](references/contrat.md#arborescence-et-nommage).

Ce qui s'y joue pour ce skill : `done/` porte des archives figées, `todo/` des registres vivants
que le pipeline **alimente sans jamais les lire de lui-même**.

---

## Phase 0 — Vérifications préalables

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "NON_GIT"
git branch --show-current
git status --short
impl-list .claude/implementation
```

Le script ne remonte que les fichiers de suivi. **Ne jamais réécrire ce filtre en ligne** —
pourquoi :
[Dates et listing](references/contrat.md#dates-et-listing).

**Ne rien créer sans confirmation** dans ces deux cas :

- `NON_GIT` → demander à l'utilisateur s'il veut quand même un fichier de suivi (il ne sera pas
  versionné).
- `.claude/implementation/` absent → demander confirmation avant de créer l'arborescence.

Dans les deux cas : poser la question, attendre la réponse, ne pas supposer.

---

## Phase 1 — Router

### Cas A : l'argument est `close` ou `abandon`

Lister les implémentations comme au Cas C et **faire choisir, même s'il n'y en a qu'une** : ces
deux opérations suppriment une branche, elles ne se déclenchent pas sur une déduction. Aller
ensuite à la Phase 5 (`close`) ou 6 (`abandon`). Aucune implémentation en cours → le dire et
s'arrêter.

### Cas B : un chemin est passé en argument

Lire ce fichier, aller directement à la Phase 3 (reprise).

### Cas C : aucun argument

Lire **uniquement les frontmatters** des fichiers de suivi (pas les fichiers entiers).

```bash
impl-list .claude/implementation
```

Compter ensuite les cases cochées de la section `## Étapes`. Afficher :

```
Implémentations en cours :

  1. auth-refactor    3/7 étapes   branche auth-refactor
  2. cache-layer      1/5 étapes   BLOQUÉ
  n. Nouvelle implémentation
```

Toujours proposer le choix. **Ne jamais deviner** l'implémentation active, même si une seule existe,
même si la branche correspond.

Aucun fichier existant → proposer directement la création.

---

## Phase 2 — Création (nouvelle implémentation)

Lire [`references/creation.md`](references/creation.md) au moment de créer, et le suivre.

---

## Phase 3 — Reprise (implémentation existante)

Lire le fichier en entier, puis restituer en quelques lignes — pas de récitation intégrale :

- l'objectif,
- l'étape en cours et la prochaine action concrète,
- les blocages éventuels,
- les commandes de vérification à rejouer,
- la section `## Passation`, si elle est à jour : ce que la session précédente avait en cours et
  ce qu'elle a appris.

**La section `## Passation` est à jour** quand son commit de Passation est le dernier de la
branche et que `git status --short` (Phase 0) ne montre rien d'autre que `<slug>.audit.md` — le
rapport d'audit n'est committé qu'à l'aplatissement, il ne dit aucun travail fait après la
Passation :

```bash
git log -1 --format=%s   # attendu : <slug>: passation — …
```

Sinon, du travail a eu lieu depuis sans nouvelle Passation : la dire périmée, avec ce que porte son
bloc `**Écrite** :`, et ne pas la restituer comme actuelle. Ni la session ni l'Étape ne suffisent à
le voir : une session qui continue après sa Passation garde le même numéro.

Comparer le champ `branche` du front matter à la branche git courante. **Divergence → le signaler**,
ne pas corriger le fichier d'office (l'utilisateur peut avoir volontairement changé de branche).

Incrémenter `session` de 1 dans le frontmatter — c'est ce compteur qui sert aux messages de commit
de session (voir Phase 4).

Remettre au contexte les Shadow-skills du Chantier : `shadow-skill depuis-suivi <slug>`, puis
`shadow-skill charge <nom>` pour ceux dont l'étape en cours a besoin. Un champ `skills` vide n'a
rien à rendre ; une erreur sur un nom se signale, sans bloquer la reprise.

**Modifications non commitées détectées** (`git status --short` non vide, Phase 0) → le signaler en
tout début de conversation et **proposer** un commit de session avant de continuer, par
`git-smart-commit`, type 2 : [Commit rapide de chantier](../git-smart-commit/references/etape.md).

La reprise faite, passer à la Phase 4 : sa référence porte la mesure du contexte et la
Passation.

---

## Phase 4 — Maintenir le fichier pendant la session

Lire [`references/execution.md`](references/execution.md) au début de l'exécution — après le
commit de l'état initial ou après la reprise —, et le suivre.

---

## Phase 5 — Clôture

Sur `/implementation-tracker close` ou quand l'utilisateur déclare l'implémentation terminée : lire
`references/cloture.md`, section « Clôture », et suivre la procédure —
**audit par `implementation-auditor`**, contrôle des étapes, finalisation du suivi, puis
aplatissement et archivage en `done/` par `git-smart-commit`, type 3.
**Pas de résumé prêt à coller** en fin de clôture.

**Une clôture sans avis favorable ne va pas au bout** : l'audit est le premier point de la
procédure, pas une formalité de fin (`references/audit.md`).

## Phase 6 — Abandon

Sur `/implementation-tracker abandon`, ou quand l'utilisateur renonce au chantier : lire
`references/cloture.md`, section « Abandon ». Un chantier abandonné n'est **jamais** aplati dans
`base` ; il est archivé avec sa raison, et le sort de sa branche se décide avec l'utilisateur.
