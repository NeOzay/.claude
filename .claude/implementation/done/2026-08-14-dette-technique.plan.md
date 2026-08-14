# Registre de dette technique — `.claude/implementation/todo/`

## Contexte

Le pipeline **produit** déjà des constats de dette : l'auditeur en fait un axe de jugement
(`agents/implementation-auditor.md:61`, « Dette technique induite ») et les rapporte en section
dédiée (`references/audit.md:118`). Mais il n'a **nulle part où les déposer**. Ces constats vivent
dans `<slug>.audit.md`, que la clôture déplace en `.claude/implementation/done/`
(`cloture.md:44-59`) — un fichier archivé que personne ne relit. La seule sortie vers l'utilisateur
est la ligne « points laissés de côté » du résumé de clôture (`cloture.md:68`), c'est-à-dire une
conversation, pas un fichier.

Démonstration : les six dettes du chantier `audit-integre`, clos le 2026-08-14, n'existent
aujourd'hui que dans `done/2026-08-14-audit-integre.md` et son rapport de 26 K.

Résultat attendu : un répertoire `todo/`, symétrique de `done/`, qui recueille durablement ce qui
reste à faire — alimenté à la clôture, consulté sur demande, extensible à `road-map.md` plus tard.

Cadre : `.claude/implementation/dette-technique.brief.md` (`statut: validé`).

## Décisions structurantes

| Point | Décision |
|---|---|
| Emplacement | `.claude/implementation/todo/`, à côté de `done/` — indépendant des conventions de doc du dépôt hôte |
| Fichiers | `technical-debt.md` et `technical-debt-solde.md` |
| Qui écrit | **L'orchestrateur, une seule fois, à la clôture.** L'auditeur n'y touche pas |
| Identification | Horodatage, **pas de numéro** — un retrait n'oblige à rien réindexer. Ordre du plus ancien au plus récent, donc ajout en fin |
| Ce qui entre | Tous les problèmes non résolus, pas seulement la section « Dette induite » du rapport. Élagage à la main de l'utilisateur |
| Solde | Déplacement vers `technical-debt-solde.md`, **avec la commande exécutée qui l'établit et sa sortie réelle** |
| Lecture | Aucune lecture automatique par le pipeline. `intent-brief` ne consulte pas `todo/` au cadrage |
| Abandon | Alimentation **proposée**, jamais imposée |

**Pourquoi l'orchestrateur et pas l'auditeur** — trois audits passent sur un même chantier
(intermédiaire, clôture, ré-audit complet après correctif imposé par `audit.md:80`), chacun
rejugeant le diff entier : les mêmes constats ressortent par construction. Le rapport encaisse la
répétition parce qu'il est un **journal** (`audit.md:87`) ; le registre est un **état**, la
répétition y serait un doublon. Et un auditeur en contexte isolé ne peut ni dédupliquer ni retirer
ce qu'un correctif a soldé entre-temps. L'orchestrateur, lui, a vu les trois audits et n'écrit
qu'une fois.

Contrepartie assumée : l'auteur du code reporte ses propres dettes. Ce qui la rend tenable est que
chaque constat du rapport porte son `R<n>` (`audit.md:130`) — la complétude est donc vérifiable
après coup par confrontation rapport ↔ registre.

## Étapes

### 1. Fichier de référence `skills/implementation-tracker/references/dette.md`

Nouveau, sur le modèle de `audit.md`. Il porte tout le contenu procédural ; `SKILL.md` et
`cloture.md` ne feront qu'y renvoyer.

Sections :

- **Ce qu'est le registre** — un état, pas un journal. Ce qui l'y distingue du rapport d'audit.
- **Ce qui entre** : tout problème non résolu à la clôture — constats de la section « Dette
  induite » du rapport, réserves que l'utilisateur a choisi de clore avec, hors-périmètre assumé au
  brief, étapes retirées en cours de route. **Ce qui n'entre pas** : les idées d'amélioration
  (elles iront dans `road-map.md`), et ce qui a été corrigé pendant le chantier.
- **Gabarit d'entrée** (horodatée, sans numéro, ajoutée en fin de fichier) :

  ```markdown
  ## 2026-08-14 — Les filtres de listing sont cassés par le hook rtk

  **Constat** — `ls .claude/implementation/*.md | grep -vE '\.(brief|audit)\.md$'` n'exclut plus
  rien : le hook `rtk` ajoute une colonne de taille en fin de ligne, l'ancre `$` ne matche jamais.

  **Assumé** : … *(facultatif — pourquoi c'était un choix, quand ç'en était un)*

  **Pourquoi c'est gênant** — les `*.brief.md` et `*.audit.md` remontent dans la liste des
  implémentations en cours, que l'Étape 0 du tracker existe pour tenir propre.

  **Pour solder** — filtrer sur le nom de fichier plutôt que sur la fin de ligne.

  *Identifié par `audit-integre`, R4 du rapport d'audit.*
  ```

- **Alimenter, à la clôture** — relire le dernier rapport d'audit, confronter ses `R<n>` à ce qui a
  été traité, écrire une entrée par constat qui survit. **Une seule passe** : si une entrée du
  registre porte déjà le même constat, ne pas la dupliquer — la compléter.
- **Solder** — couper l'entrée du registre, la coller en fin de `technical-debt-solde.md` en lui
  ajoutant :

  ```markdown
  **Soldé le 2026-09-02 par le chantier `listing-fix`** — les listings filtrent désormais sur le nom.
  Établi par : `ls .claude/implementation/*.md | grep -vE 'brief|audit'` → 2 lignes, aucun
  `.brief.md` ni `.audit.md`.
  ```

  **Sans commande exécutée et sa sortie réelle, l'entrée reste dans le registre.** C'est le même
  principe que le point d'intégrité de l'auditeur (`implementation-auditor.md:66-75`) : un solde
  affirmé par celui qui vient de faire le travail ne vaut que par sa vérification.
  `technical-debt-solde.md` est créé au premier solde, pas avant.

*Vérif* : `test -f skills/implementation-tracker/references/dette.md`

### 2. `.claude/implementation/todo/README.md`

Explique la nature du répertoire — registres **vivants**, par opposition à `done/` qui porte des
archives figées et datées — et le fait qu'il accueillera `road-map.md`. Sur le modèle de
`archive/README.md`, qui joue le même rôle.

*Vérif* : `test -f .claude/implementation/todo/README.md`

### 3. Amorcer `todo/technical-debt.md` avec les six dettes d'`audit-integre`

Relire `done/2026-08-14-audit-integre.audit.md` et `done/2026-08-14-audit-integre.md` pour tirer les
bons `R<n>` et les bons chemins — **ne pas écrire de mémoire**. Chaque entrée est vérifiée dans le
dépôt avant d'être écrite : le registre ne liste que du constaté.

1. Patterns de sécurité de `git-pre-commit-audit` à reprendre (`archive/`) — hors-périmètre assumé
   dès le brief.
2. La confrontation plan ↔ brief reste auto-jugée (`skills/intent-brief/SKILL.md`, Étape 7) —
   troisième point de contrôle du symptôme d'origine, laissé hors des critères.
3. Circularité de l'étape corrective : `cloture.md` exige toutes les étapes cochées avant d'auditer,
   or une étape née d'un audit ne peut pas l'être avant le nouvel audit.
4. Filtres de listing cassés par le hook `rtk`.
5. Asymétrie de rédaction sur la racine du dépôt (`audit.md:43-45` vs
   `implementation-auditor.md:21-23`) — sans mode de défaillance, mais c'est le type d'écart qui
   avait produit R3.
6. Champs `brief:` / `plan:` / `audit:` pointant vers des chemins disparus après archivage en
   `done/` — dette préexistante, non aggravée.

*Vérif* : `grep -c '^## 2026-' .claude/implementation/todo/technical-debt.md` → `6`

### 4. `skills/implementation-tracker/SKILL.md`

- Bloc « Emplacement » : ajouter `todo/` à l'arborescence, avec ses deux fichiers et une ligne
  disant que le répertoire n'est **pas** archivé, contrairement à `done/`.
- Tableau des déclencheurs de l'Étape 4 : une ligne pour que les constats rencontrés **en cours de
  chantier** ne se perdent pas avant la clôture.

  ```
  | Problème constaté hors du périmètre | Le noter au journal — il ira au registre de dette à la clôture (`references/dette.md`) |
  ```

*Vérif* : `grep -n 'todo/' skills/implementation-tracker/SKILL.md`

### 5. `skills/implementation-tracker/references/cloture.md`

- **Nouveau point 2, « Alimenter le registre de dette »**, inséré entre l'audit (point 1) et la
  finalisation du suivi. Position imposée par le brief : après l'audit — sinon on écrit sans
  connaître le verdict ni les arbitrages qu'il a provoqués — et avant l'archivage, pour que
  l'écriture entre dans l'aplatissement de la branche. Renuméroter 2→3, 3→4, 4→5.
- Point « Résumé » : les « points laissés de côté » renvoient au registre au lieu de vivre dans la
  seule conversation.
- Section « Abandon » : ajouter au point 3 la **proposition** d'alimenter le registre avec ce qui
  restait à faire, la raison de l'abandon à l'appui. Proposée, jamais imposée.

*Vérif* : `grep -n 'dette.md' skills/implementation-tracker/references/cloture.md`

### 6. `skills/implementation-tracker/references/audit.md`

Section « Au retour » : préciser qu'un constat de dette **ne part pas dans le registre au retour de
l'audit** — il y va à la clôture, en une seule passe. Sans cette ligne, un audit intermédiaire
suivi d'un audit de clôture écrit deux fois le même constat : exactement le signal de dérive du
brief.

*Vérif* : `grep -n 'registre' skills/implementation-tracker/references/audit.md`

## Ce que le plan ne fait pas

- Aucune modification de `agents/implementation-auditor.md` — c'est un critère de réussite du brief.
- Pas de `road-map.md` : seulement un emplacement qui puisse l'accueillir.
- Aucune lecture automatique de `todo/` par `intent-brief` ni par le tracker.

## Vérification d'ensemble

```bash
# le registre existe et porte les six dettes, sans numérotation
grep -c '^## 2026-' .claude/implementation/todo/technical-debt.md          # → 6
grep -c '^## [0-9]\+\.' .claude/implementation/todo/technical-debt.md      # → 0

# l'auditeur n'a pas bougé, et ne connaît pas todo/
git diff --stat master -- agents/implementation-auditor.md                 # → vide
grep -c 'todo/' agents/implementation-auditor.md                           # → 0

# la clôture alimente entre l'audit et l'archivage
grep -n '^### [0-9]\.' skills/implementation-tracker/references/cloture.md

# entrées ordonnées de la plus ancienne à la plus récente
grep '^## ' .claude/implementation/todo/technical-debt.md | sort -c
```

Relecture manuelle du chemin complet : dérouler `cloture.md` de bout en bout sur le chantier
`dette-technique` lui-même — l'audit de clôture jugera un chantier dont la procédure de clôture a
changé, et c'est le meilleur test qu'on puisse lui donner.
