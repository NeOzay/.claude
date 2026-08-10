---
name: implementation-tracker
description: >
  Définit et suit une implémentation en cours sur plusieurs discussions. Maintient un fichier
  de suivi versionné par feature (objectif, périmètre, étapes, état courant, journal de décisions)
  dans .claude/implementation/. Skill exclusivement manuelle : elle s'invoque uniquement via
  /implementation-tracker, typiquement en début de discussion.
disable-model-invocation: true
argument-hint: "[@chemin/vers/suivi.md]"
---

# Implementation Tracker

Fichier de suivi **par feature**, versionné dans le repo, qui survit aux discussions.
Source de vérité de l'implémentation en cours : objectif, périmètre, étapes, état, décisions.

Invocation manuelle uniquement :

- `/implementation-tracker` → liste les implémentations, propose reprise ou création
- `/implementation-tracker @chemin/vers/fichier.md` → charge directement ce fichier de suivi

---

## Emplacement

```
<repo>/.claude/implementation/
  <slug>.md                      # suivi actif — commité avec le code
  <slug>.brief.md                # brief d'intention (skill intent-brief), figé après validation
  done/
    <AAAA-MM-DD>-<slug>.md          # archivés à la clôture
    <AAAA-MM-DD>-<slug>.brief.md
```

---

## Étape 0 — Vérifications préalables

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "NON_GIT"
git branch --show-current
git status --short
ls .claude/implementation/*.md 2>/dev/null | grep -v '\.brief\.md$'
```

Les `*.brief.md` (skill `intent-brief`) ne sont **pas** des fichiers de suivi : les exclure
partout où l'on énumère les implémentations.

**Ne rien créer sans confirmation** dans ces deux cas :

- `NON_GIT` → demander à l'utilisateur s'il veut quand même un fichier de suivi (il ne sera pas versionné).
- `.claude/implementation/` absent → demander confirmation avant de créer l'arborescence.

Dans les deux cas : poser la question, attendre la réponse, ne pas supposer.

---

## Étape 1 — Router

### Cas A : un chemin est passé en argument

Lire ce fichier, aller directement à l'étape 3 (reprise).

### Cas B : aucun argument

Lire **uniquement les frontmatters** des fichiers de suivi (pas les fichiers entiers). Les
`*.brief.md` ne sont **pas** des fichiers de suivi : les exclure du listing.

```bash
ls .claude/implementation/*.md 2>/dev/null | grep -v '\.brief\.md$'
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

## Étape 2 — Création (nouvelle implémentation)

**Prérequis : arbre de travail propre.** Si `git status --short` (Étape 0) n'est pas vide, **ne pas
créer** de nouvelle implémentation. **Exception : les `*.brief.md`.** Un brief produit par
`intent-brief` avant l'appel au tracker apparaît en `??` sans être une modification étrangère au
chantier — l'ignorer dans ce contrôle. Arrêter et indiquer qu'il ne doit y avoir aucune modification en
cours avant de démarrer un nouveau chantier — sinon les premiers commits de session mélangeraient des
changements étrangers à l'implémentation. Laisser l'utilisateur traiter ces modifications (les
committer ou les mettre de côté) avant de relancer.

1. **Cadrer l'intention avant de planifier** — invoquer le skill `intent-brief`. Il produit
   `.claude/implementation/<slug>.brief.md` : intention réelle, critères de réussite,
   hors-périmètre, contraintes non devinables, signaux de dérive. C'est lui qui pose les
   questions ; ne pas réinventer un questionnaire ici.

   Un brief validé existe déjà pour ce chantier → le lire et passer directement au point 2.

2. **Entrer en plan mode** (`EnterPlanMode`), avec le brief comme cadre : rappeler
   explicitement au plan les critères de réussite, le hors-périmètre et les incertitudes à
   lever. Explorer le code et construire le plan normalement — c'est le flux natif qui fait
   le travail.
3. À la validation (`ExitPlanMode`), **confronter le plan au brief** (Étape 7 d'`intent-brief`)
   avant toute écriture : critères servis, hors-périmètre respecté, signaux de dérive non
   déclenchés, incertitudes tranchées. Tout écart se dit ; il se règle avec l'utilisateur, pas
   en silence.

   Le plan est persisté dans `.claude/plans/<slug>-<mots>.md` (voir `plansDirectory`).
   Récupérer ce chemin :

   ```bash
   ls -t .claude/plans/*.md | head -1
   ```

4. **Figer le plan** dans le fichier de suivi : les étapes du plan deviennent la section `## Étapes`,
   et le chemin du plan va dans le champ `plan:` du frontmatter.
5. Slug = titre en kebab-case, court (`auth-refactor`, pas `refonte-complete-du-systeme-dauth`).
   **Reprendre exactement le slug du brief** — c'est lui qui apparie les deux fichiers.
6. **Reprendre `## Objectif et périmètre` du brief**, ne pas le réinventer : symptôme, but,
   critères de réussite, hors-périmètre **et signaux de dérive** viennent du brief, tels qu'ils
   ont été validés. Renseigner `brief:` dans le frontmatter.

   Le **symptôme** est ce qui permet, trois sessions plus tard, de voir qu'on a construit la
   bonne solution au mauvais problème. Les **signaux de dérive** deviennent un déclencheur
   d'arrêt pendant l'implémentation (Étape 4). C'est ce point de jonction qui attache le chantier à
   l'intention initiale et empêche le scope creep entre deux discussions.

   Le brief n'est plus modifié ensuite. Si l'intention change réellement en cours de route, le
   noter dans le journal de décisions — la divergence entre brief et réel est une information,
   l'effacer la détruit.
7. **Créer la branche d'implémentation** nommée exactement `<slug>`, à partir de la branche courante.
   Cette branche courante est la **branche principale**, cible de l'aplatissement final : la noter dans
   le champ `base:` du frontmatter, et `<slug>` dans `branche:`.

   ```bash
   git checkout -b <slug>
   ```

   Tous les commits de session/étape se feront désormais sur `<slug>` ; ils seront aplatis en un seul
   commit sur `base:` à la clôture (Étape 5). Ne jamais committer sans accord explicite (règle globale).

---

## Étape 3 — Reprise (implémentation existante)

Lire le fichier en entier, puis restituer en quelques lignes — pas de récitation intégrale :

- l'objectif,
- l'étape en cours et la prochaine action concrète,
- les blocages éventuels,
- les commandes de vérification à rejouer.

Comparer `branche:` du frontmatter à la branche git courante. **Divergence → le signaler**, ne pas
corriger le fichier d'office (l'utilisateur peut avoir volontairement changé de branche).

Incrémenter `session:` de 1 dans le frontmatter — c'est ce compteur qui sert aux messages de commit
de session (voir Étape 4).

**Modifications non commitées détectées** (`git status --short` non vide, Étape 0) → le signaler en
tout début de conversation et proposer un commit de session avant de continuer (voir « Commits de
session », Étape 4, pour le format du message et la méthode : commit simple et direct, pas de passage
par `git-smart-commit`). Ne jamais committer sans accord explicite (règle globale, `CLAUDE.md`).

---

## Étape 4 — Maintenir le fichier pendant la session

Le fichier est mis à jour **en continu**, sans que l'utilisateur ait à le demander. Relire le fichier
avant chaque écriture. Toujours actualiser `maj:` en même temps que le contenu.

Déclencheurs d'écriture :

| Événement | Action |
|---|---|
| Étape terminée | Cocher `[x]`, passer la suivante en `[>]`, **proposer un commit** (voir ci-dessous) |
| Blocage | Passer l'étape en `[!]` + raison, `statut: bloqué` |
| Déblocage | Repasser en `[>]`, `statut: en-cours` |
| Décision d'architecture arrêtée | Ligne dans le journal (voir règle ci-dessous) |
| Le plan ne colle plus au réel | **Modifier les étapes** et le dire. Ne jamais bricoler en silence |
| **Signal de dérive du brief déclenché** | **S'arrêter**, le nommer, en reparler avant de continuer |
| Demande hors-périmètre | Le signaler, proposer soit d'élargir le périmètre, soit une nouvelle impl |

### Commits de session

Une étape peut s'étaler sur **plusieurs sessions** (plusieurs discussions successives). Le compteur
de commit se cale donc sur la **session**, pas sur l'étape :

- Le frontmatter porte un champ `session: N`, incrémenté à chaque reprise (Étape 3).
- Message de commit : `<slug>: session N — <étape en cours>`.
- **Quand une étape passe en `[x]`** : proposer un commit dédié (même si un commit de session a déjà
  été fait juste avant), et noter sa référence courte à côté de la case dans le fichier de suivi,
  par ex. `[x] 2. Brancher le middleware (commit: a1b2c3d)`.
- Commit simple et direct (`git add -u && git commit -m "..."`), pas besoin de `git-smart-commit`
  pour ces commits de suivi — ils ont un message prédéterminé, pas d'analyse de diff nécessaire.
- **Toujours proposer, jamais committer sans confirmation explicite** (règle globale, `CLAUDE.md`).

### Règle du journal de décisions

N'y consigner que ce qui **contraint le futur** : choix d'architecture, trade-offs, dépendances
retenues. Pas les micro-choix (nommage, style, refacto local).

**Être concis** : une entrée = 2 à 3 lignes maximum. Une phrase pour la décision, une pour le
pourquoi, une pour l'alternative rejetée. Pas de contexte narratif, pas de rappel du code, pas de
paragraphe. Si une entrée déborde, c'est qu'elle contient plusieurs décisions : les séparer, ou
n'en garder que celle qui contraint réellement la suite.

Format : `- **date** — décision. *Pourquoi* : … *Rejeté* : …`

**Compaction** : garder les **5 dernières** décisions en clair. Les plus anciennes sont condensées à
une ligne chacune sous `### Décisions antérieures`, en ne conservant que la décision et le pourquoi.

---

## Étape 5 — Clôture

Sur `/implementation-tracker close` ou quand l'utilisateur déclare l'implémentation terminée :

1. Vérifier que toutes les étapes sont cochées — sinon demander quoi faire des restantes.
2. **Sur la branche `<slug>`**, finaliser le fichier de suivi : `statut: terminé`, compacter le journal
   en entier. Le committer (commit de suivi direct) pour que ces derniers changements entrent dans
   l'aplatissement.
3. **Aplatir la branche d'implémentation dans la branche principale** : passer la main à
   `git-smart-commit` (cas « aplatissement d'une branche d'implémentation », voir ce skill). Tous les
   commits de la branche `<slug>` sont réunis en **un seul commit posé sur `base:`**, puis la branche
   `<slug>` est supprimée. Ce n'est **pas** un commit de suivi ordinaire — c'est une réécriture
   d'historique, donc elle suit le workflow de vérification et de confirmation complet de
   `git-smart-commit`, pas le commit direct utilisé pour les sessions/étapes.
   **Déplacement du fichier de suivi** : une fois placé sur `base:` avec le `git merge --squash`
   appliqué, mais **avant le commit unique**, déplacer le fichier vers `done/` pour que le renommage
   soit inclus dans l'aplatissement :
   `git mv .claude/implementation/<slug>.md .claude/implementation/done/<AAAA-MM-DD>-<slug>.md`

   **Archiver aussi le brief** au même moment, s'il existe — il documente l'intention d'origine et
   n'a d'intérêt qu'à côté de son suivi. Il peut ne pas être suivi par git (créé avant le premier
   commit du chantier) : `git mv` échouerait alors en plein squash. Replier sur `mv` :

   ```bash
   b=.claude/implementation/<slug>.brief.md
   d=.claude/implementation/done/<AAAA-MM-DD>-<slug>.brief.md
   [ -e "$b" ] && { git mv "$b" "$d" 2>/dev/null || mv "$b" "$d"; }
   ```
4. Produire un **résumé prêt à coller dans la PR** : objectif, ce qui a changé, décisions notables,
   points laissés de côté.

---

## Gabarit du fichier de suivi

```markdown
---
slug: auth-refactor
titre: Refonte de l'authentification
branche: auth-refactor      # branche d'implémentation = <slug>
base: main                  # branche principale, cible de l'aplatissement final (Étape 5)
statut: en-cours            # en-cours | bloqué | terminé
session: 3                  # incrémenté à chaque reprise (Étape 3)
plan: .claude/plans/refonte-auth-lucky-beaver.md
brief: .claude/implementation/auth-refactor.brief.md
créé: 2026-07-12
maj: 2026-07-12
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : … (ce qui était vécu à l'origine — sert à détecter la bonne solution au mauvais problème)
**But** : …
**Critères de réussite** : … (mesurables : tests qui passent, comportement observable)
**Hors-périmètre** : … (explicite — ce qu'on ne fait PAS dans ce chantier)
**Signaux de dérive** : … (déclencheurs d'arrêt pendant l'implémentation, cf. Étape 4)

## Étapes

- [x] 1. Extraire `TokenStore` — `src/auth/token.rs` (commit: a1b2c3d)
- [>] 2. Brancher le middleware — `src/mw/auth.rs`
- [ ] 3. Migrer les tests
- [!] 4. Rotation des clés — BLOQUÉ : attente décision infra

## État courant

**Prochaine action** : …
**Vérification** : `cargo test auth`
**Notes** : …

## Journal de décisions

- **2026-07-12** — JWT plutôt que sessions serveur. *Pourquoi* : scale horizontal sans état partagé.
  *Rejeté* : sessions Redis (dépendance d'infra supplémentaire).

### Décisions antérieures

- Argon2id pour le hash — résistance GPU.
```

Légende des cases : `[ ]` à faire · `[>]` en cours · `[x]` fait · `[!]` bloqué
