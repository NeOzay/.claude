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
- `/implementation-tracker close` → clôture l'implémentation en cours (Étape 5)
- `/implementation-tracker abandon` → abandonne un chantier sans le livrer (Étape 6)

---

## Emplacement

```
<repo>/.claude/implementation/
  <slug>.md                      # suivi actif — commité avec le code
  <slug>.brief.md                # brief d'intention (skill intent-brief), figé après validation
  <slug>.audit.md                # rapports d'audit successifs (agent implementation-auditor)
  done/
    <AAAA-MM-DD>-<slug>.md          # archivés à la clôture
    <AAAA-MM-DD>-<slug>.brief.md
    <AAAA-MM-DD>-<slug>.audit.md
  todo/
    README.md                      # ce que le répertoire recueille
    technical-debt.md              # registre de dette, alimenté à la clôture (references/dette.md)
    technical-debt-solde.md        # ce qui a été soldé, avec la commande qui l'établit
```

`todo/` est l'inverse de `done/` : ses fichiers sont **vivants** — relus, complétés, élagués — et
ne sont jamais archivés. Le pipeline les alimente sans jamais les lire de lui-même.

---

## Étape 0 — Vérifications préalables

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "NON_GIT"
git branch --show-current
git status --short
ls .claude/implementation/*.md 2>/dev/null | grep -vE '\.(brief|audit)\.md$'
```

Les `*.brief.md` (skill `intent-brief`) et les `*.audit.md` (agent `implementation-auditor`) ne
sont **pas** des fichiers de suivi : les exclure partout où l'on énumère les implémentations.

**Ne rien créer sans confirmation** dans ces deux cas :

- `NON_GIT` → demander à l'utilisateur s'il veut quand même un fichier de suivi (il ne sera pas versionné).
- `.claude/implementation/` absent → demander confirmation avant de créer l'arborescence.

Dans les deux cas : poser la question, attendre la réponse, ne pas supposer.

---

## Étape 1 — Router

### Cas A : l'argument est `close` ou `abandon`

Lister les implémentations comme au Cas C et **faire choisir, même s'il n'y en a qu'une** : ces
deux opérations suppriment une branche, elles ne se déclenchent pas sur une déduction. Aller
ensuite à l'Étape 5 (`close`) ou 6 (`abandon`). Aucune implémentation en cours → le dire et
s'arrêter.

### Cas B : un chemin est passé en argument

Lire ce fichier, aller directement à l'Étape 3 (reprise).

### Cas C : aucun argument

Lire **uniquement les frontmatters** des fichiers de suivi (pas les fichiers entiers). Les
`*.brief.md` et `*.audit.md` ne sont **pas** des fichiers de suivi : les exclure du listing.

```bash
ls .claude/implementation/*.md 2>/dev/null | grep -vE '\.(brief|audit)\.md$'
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

   **Pas de brief** (cadrage jugé inutile, cf. « Quand ne pas cadrer » d'`intent-brief`) →
   `brief:` omis et **`execution: direct` imposé** : sans hors-périmètre ni signaux de dérive
   écrits, un exécutant isolé n'a aucune borne. Remplir `## Objectif et périmètre` avec
   l'utilisateur, en une passe.

2. **Entrer en plan mode** (`EnterPlanMode`), avec le brief comme cadre : rappeler
   explicitement au plan les critères de réussite, le hors-périmètre et les incertitudes à
   lever. Explorer le code et construire le plan normalement — c'est le flux natif qui fait
   le travail.
3. À la validation (`ExitPlanMode`), **confronter le plan au brief** (Étape 7 d'`intent-brief`)
   avant toute écriture : critères servis, hors-périmètre respecté, signaux de dérive non
   déclenchés, incertitudes tranchées. Tout écart se dit ; il se règle avec l'utilisateur, pas
   en silence.

   **Le chantier arrive d'`intent-brief`** (cas normal : c'est lui qui renvoie ici) → ses Étapes
   6 et 7 ont déjà fait le plan et la confrontation. Ne pas les refaire : passer au point 4.

   Le plan est persisté dans `.claude/plans/<slug>-<mots>.md` (voir `plansDirectory`). **Prendre
   son chemin dans la sortie d'`ExitPlanMode`**, pas par `ls -t` : dès qu'un second plan existe,
   la date de modification désigne le mauvais fichier.

   **Le plan doit être versionné.** C'est lui qui porte le contenu des étapes — le suivi n'en a
   que les intitulés, et `step-implementer` va y lire la description de son étape. Vérifier qu'il
   n'est pas ignoré :

   ```bash
   git check-ignore -q .claude/plans/<fichier>.md && echo "IGNORÉ — le signaler"
   ```

   S'il est ignoré, le dire à l'utilisateur : sans lui, la reprise en session 3 et toute
   délégation perdent la description des étapes. Sinon, le committer avec le fichier de suivi.

4. **Figer le plan** dans le fichier de suivi (gabarit : `references/gabarit-suivi.md`) : les étapes
   du plan deviennent la section `## Étapes`, et le chemin du plan va dans le champ `plan:` du
   frontmatter.

   Chaque étape porte **le ou les fichiers visés et sa commande de vérification** :

   ```
   - [ ] 2. Brancher le middleware — `src/mw/auth.rs` — vérif: `cargo test mw::auth`
   ```

   Une étape sans vérification n'est pas délégable. C'est tout ce que l'appelant transmettra de
   l'étape à `step-implementer` — le reste, l'exécutant va le chercher dans le plan : le suivi ne
   porte que l'intitulé et l'état, **le contenu de l'étape reste dans le plan**.

   Chaque étape doit tenir en **un seul tour d'exécution**. Une étape qui déborderait sur
   plusieurs sessions se découpe ici, pas en cours de route : un appel de sous-agent est
   atomique et ne se reprend pas.
5. Slug = titre en kebab-case, court (`auth-refactor`, pas `refonte-complete-du-systeme-dauth`).
   **Reprendre exactement le slug du brief** — c'est lui qui apparie les deux fichiers.
6. **Reprendre `## Objectif et périmètre` du brief**, ne pas le réinventer : symptôme, but,
   critères de réussite, hors-périmètre **et signaux de dérive** viennent du brief, tels qu'ils
   ont été validés. Renseigner `brief:` dans le frontmatter, ainsi que `execution:` — repris tel
   quel du frontmatter du brief. **`direct` à défaut d'indication** : une valeur absente signifie
   que la délégabilité n'a pas été jugée, pas qu'elle est acquise.

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
| Étape passée en `[>]` | Si `execution: délégué` et l'étape est substantielle : déléguer à `step-implementer` (voir ci-dessous) |
| Étape terminée | Cocher `[x]`, passer la suivante en `[>]`, **proposer un commit** (voir ci-dessous) |
| Blocage | Passer l'étape en `[!]` + raison, `statut: bloqué` |
| Déblocage | Repasser en `[>]`, `statut: en-cours` |
| Décision d'architecture arrêtée | Ligne dans le journal (voir règle ci-dessous) |
| Le plan ne colle plus au réel | **Modifier les étapes** et le dire. Ne jamais bricoler en silence |
| **Signal de dérive du brief déclenché** | **S'arrêter**, le nommer, en reparler avant de continuer |
| Diff `base:`↔`<slug>` au-delà de 400 lignes | **Proposer** un audit intermédiaire, étapes restantes à l'appui (`references/audit.md`) |
| Demande hors-périmètre | Le signaler, proposer soit d'élargir le périmètre (voir ci-dessous), soit une nouvelle impl |
| Problème constaté hors du périmètre | Le noter au journal — il ira au registre de dette à la clôture (`references/dette.md`) |

### Quand le périmètre change

Le brief est figé, le suivi vit : **en cas de divergence, le suivi fait foi**, le brief reste le
témoin de l'intention d'origine. Un élargissement accepté par l'utilisateur s'écrit donc dans
`## Objectif et périmètre` du suivi — daté, avec une entrée au journal — et non dans le brief.
C'est la seule exception au « repris du brief, pas reformulé » ; sans elle, un chantier qui évolue
n'a plus de périmètre écrit nulle part, et l'exécutant refuse en `ÉCART` un travail pourtant validé.

### Délégation d'étape

Quand `execution: délégué` et que l'étape passée en `[>]` est substantielle, elle **est** confiée
au sous-agent `step-implementer` (Sonnet, contexte isolé). Deux bénéfices distincts : les lectures
de fichiers et les diffs restent dans l'agent au lieu de gonfler la session, et l'exécution sort
du modèle de cadrage.

Lui transmettre : chemins du suivi et du brief, numéro et intitulé de l'étape, commande de
vérification de l'étape. **Ne rien recopier d'autre** — il lit lui-même le suivi, le plan (via
`plan:`) et le brief.

**Ne pas déléguer** :

- une étape qui tient en un ou deux fichiers évidents — l'amorçage d'un agent froid coûte alors
  plus que le travail lui-même ;
- une étape exploratoire, ou qui dépend d'un arbitrage encore ouvert ;
- une étape **sans commande de vérification** — l'exécutant n'aurait aucun moyen de conclure ;
- une étape **déjà entamée** et interrompue par une fin de session : la terminer en direct. Un
  appel d'agent est atomique ; ré-déléguer enverrait un agent froid sur un travail à moitié fait,
  qu'il rapporterait en `ÉCART`. Si le cas se répète, les étapes sont trop grosses : les découper.

Dans le doute sur un chantier entier, basculer `execution:` à `direct` et le noter au journal.

**L'appelant reste responsable au retour.** L'agent ne commit pas et ne touche à aucun fichier
de suivi. Relire le fichier de suivi avant d'y écrire — il a pu vieillir pendant l'exécution.

**Premier réflexe, quel que soit le `RÉSULTAT` : regarder le diff.** Le travail a été produit hors
session — ni `git-smart-commit` (court-circuité pour les commits d'étape) ni l'utilisateur ne l'ont
vu passer. Afficher `git status --short` et `git diff --stat`, les confronter à `FICHIERS` : un
fichier touché qui n'y figure pas est un écart, pas un oubli. C'est le seul regard porté sur ce
diff, et il vient **avant** toute autre action.

| `RÉSULTAT` | Action |
|---|---|
| `TERMINÉ` | Cocher `[x]`, actualiser `maj:`, consigner les `DÉCISIONS`, proposer le commit |
| `ÉCART` | Remonter à l'utilisateur sans rien corriger d'office, comme toute divergence plan/réel |
| `DÉRIVE` | S'arrêter, nommer le signal déclenché, en reparler avant de continuer |
| `BLOQUÉ` | Passer l'étape en `[!]` + raison, `statut: bloqué` |

**Sur `ÉCART`, `DÉRIVE` ou `BLOQUÉ`, l'agent a laissé du travail partiel dans l'arbre** — c'est
voulu, il n'a pas les commandes pour revenir en arrière. Trancher son sort avec l'utilisateur
**avant de faire quoi que ce soit d'autre** : garder en l'état, ou annuler (`git restore`). Sans
cet arbitrage, le prochain commit de session le ramasserait en silence — exactement ce que ce
dispositif existe pour empêcher.

Dans tous les cas : **`À SIGNALER` non vide se remonte à l'utilisateur**, sans rien corriger
d'office ; si l'anomalie relève du périmètre, elle devient une étape.

Ne jamais cocher une étape sur la seule foi du rapport si `VÉRIFICATION` n'a pas de verdict
réel : relancer la commande soi-même.

**Rendre la main après chaque étape déléguée.** Ne pas enchaîner la suivante sans accord : c'est
le point de contrôle de l'utilisateur sur une exécution qu'il n'a pas vue, et la coupure naturelle
entre deux sessions.

### Commits de session

Une étape peut se retrouver **à cheval sur deux sessions** — interruption, ou exécution en `direct`.
Le compteur de commit se cale donc sur la **session**, pas sur l'étape :

- Le frontmatter porte un champ `session: N`, incrémenté à chaque reprise (Étape 3).
- Message de commit : `<slug>: session N — <étape en cours>`.
- **Quand une étape passe en `[x]`** : proposer un commit dédié, même si un commit de session a déjà
  été fait juste avant.
- Commit simple et direct, pas besoin de `git-smart-commit` pour ces commits de suivi — ils ont un
  message prédéterminé, pas d'analyse de diff nécessaire. **Stager les chemins, jamais `-A` :**
  `git add <chemins> && git commit -m "..."` — les fichiers de `FICHIERS` pour une étape déléguée,
  le fichier de suivi, et rien d'autre. `-A` ramasserait ce qui traîne dans l'arbre ; `-u` raterait
  les fichiers créés.
- **Toujours proposer, jamais committer sans confirmation explicite** (règle globale, `CLAUDE.md`).

### Règle du journal de décisions

N'y consigner que ce qui **contraint le futur** : choix d'architecture, trade-offs, dépendances
retenues. Pas les micro-choix (nommage, style, refacto local).

**Être concis** : une entrée = 2 à 3 lignes maximum. Une phrase pour la décision, une pour le
pourquoi, une pour l'alternative rejetée. Pas de contexte narratif, pas de rappel du code, pas de
paragraphe. Si une entrée déborde, c'est qu'elle contient plusieurs décisions : les séparer, ou
n'en garder que celle qui contraint réellement la suite.

Format : `- **date** — décision. *Pourquoi* : … *Rejeté* : …`

---

## Étape 5 — Clôture

Sur `/implementation-tracker close` ou quand l'utilisateur déclare l'implémentation terminée :
lire `references/cloture.md`, section « Clôture », et suivre la procédure — **audit par
`implementation-auditor`**, contrôle des étapes, finalisation du suivi, aplatissement via
`git-smart-commit`, archivage en `done/`. **Pas de résumé prêt à coller** en fin de clôture.

**Une clôture sans avis favorable ne va pas au bout** : l'audit est le premier point de la
procédure, pas une formalité de fin (`references/audit.md`).

## Étape 6 — Abandon

Sur `/implementation-tracker abandon`, ou quand l'utilisateur renonce au chantier : lire
`references/cloture.md`, section « Abandon ». Un chantier abandonné n'est **jamais** aplati dans
`base:` ; il est archivé avec sa raison, et le sort de sa branche se décide avec l'utilisateur.

---

## Gabarit du fichier de suivi

Voir `references/gabarit-suivi.md` — à lire au moment de créer le fichier (Étape 2), pas avant.

Légende des cases : `[ ]` à faire · `[>]` en cours · `[x]` fait · `[!]` bloqué
