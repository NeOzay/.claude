# Plan — messages-du-pipeline

Brief : `.claude/implementation/messages-du-pipeline.brief.md` (validé). Entrée de road-map :
`messages-du-pipeline`.

## Contexte

Les messages du pipeline redisent ce que l'utilisateur voit déjà : les fichiers et les diffs dans
Neovim, les tokens dans la ligne d'état. Le Chantier les réduit, et fait du cadrage du Brief des
échanges suivis d'un fichier que l'utilisateur corrige.

Cadre rappelé du Brief :

- **Critères** : aucune trace de « Voir le diff », « Ma lecture », « Qu'est-ce qui est faux »,
  « Chemins stagés » dans `skills` et `agents` ; staging de tout ce qui est en attente sauf les
  exclusions ; forme imposée du commit d'Étape ; accord sans titre pour `<L>E0`, session et
  Passation ; nouvel ordre d'intent-brief ; mesure du contexte tue sous le seuil ; audit en une
  ligne et un tableau ; règle contre les rappels ; mémoire `index-avant-commit` supprimée ;
  `rumdl fmt --check` passe sur les fichiers Markdown du diff.
- **Hors-périmètre** : les choix de fin d'Étape et le déroulement qu'ils entraînent
  (`enchainement-du-chantier`) ; le fond de l'audit (`refonte-de-l-audit`).
- **Incertitudes** : aucune.

## Modèle

**Opus** : le Chantier est fait de prose, que rien ne vérifie mécaniquement au-delà des `grep` des
critères.

## Décisions de conception

- **La règle des messages s'écrit une seule fois**, dans une section nouvelle
  `## Messages à l'utilisateur` de `skills/implementation-tracker/references/contrat.md`, contrat
  partagé du pipeline. Toute section du contrat doit porter une empreinte au garde-fou
  (`scripts/check_pipeline.py`, `EMPREINTES`, contrôle 2) : on en ajoute une. intent-brief,
  git-smart-commit et implementation-tracker y renvoient.
- **Staging** : `git add -A`, puis `git reset -q -- <exclus…>`, puis contrôle par
  `git diff --staged --name-only`. Le `reset` retire aussi un fichier exclu que l'utilisateur
  aurait indexé lui-même. Le contrôle après coup reste `git show --stat HEAD`.
- **Choix d'un commit d'Étape ou de Retouche** : ce Chantier ne les définit pas, puisqu'ils
  relèvent de `enchainement-du-chantier`. En attendant, ces commits gardent les deux choix
  génériques de `confirmation.md`, sans rien ajouter. `enchainement-du-chantier` les
  spécialisera. Ratifié par l'utilisateur à la relecture du Plan.
- **Critère `rumdl`** : borné aux fichiers Markdown du diff du Chantier. Six fichiers hors Chantier
  échouent déjà, et restent en l'état. Arbitré par l'utilisateur à la relecture du Plan.
- **Commit ordinaire découpé en plusieurs sujets** : le découpage reste. Pour chaque commit, les
  fichiers gardés pour les suivants comptent parmi ses exclusions.
- **Aplatissement** : la proposition donne le titre du message et, sur une ligne, les gestes
  irréversibles (branche et tags supprimés), avec « Réaliser la Clôture » et « Autre chose ». Le
  dry-run reste lancé, mais sa sortie n'est plus recopiée.
- **Registre des ambiguïtés d'intent-brief** : avant l'écriture, il n'y a pas encore de fichier.
  Chaque ambiguïté soulevée pendant les échanges entre aux incertitudes du Brief dès son
  écriture. La règle « disparaître silencieusement n'est pas un état » est conservée.
- **Mémoire `index-avant-commit`** : elle est hors versionnage (`.gitignore`, `projects/`). Sa
  suppression ne laisse donc aucune trace dans le diff ; elle se vérifie par `test ! -e`.

## Étapes

### E1 — Règle des messages, au contrat

- `skills/implementation-tracker/references/contrat.md` reçoit la section
  `## Messages à l'utilisateur`, qui pose trois règles :
  - un message ne redit pas ce que l'utilisateur voit ailleurs : fichiers et diffs dans son
    éditeur, tokens dans la ligne d'état ;
  - une mesure ou une inscription au Suivi ne se dit que si elle appelle une décision ;
  - pas de rappel qui revient à chaque message sans rien apprendre, par exemple « Je ne la lance
    pas sans votre feu vert » ou « Le suivi et le rapport d'audit restent non commités ».
- `scripts/check_pipeline.py` : une entrée `"messages-à-lutilisateur"` dans `EMPREINTES`, dont la
  phrase-empreinte vient de la section. Vérifier l'ancre exacte rendue par `sections()`.
- Renvois vers la section depuis `skills/implementation-tracker/SKILL.md`,
  `skills/intent-brief/SKILL.md` et `skills/git-smart-commit/SKILL.md`, rubrique « Ce qui vaut pour
  tous les types ».

Vérification :

```bash
python3 scripts/check_pipeline.py
~/.claude/.venv/bin/python -m pytest scripts/tests/ -q
uvx ruff check scripts && uvx ruff format --check scripts
```

### E2 — Commits : staging et confirmation

- `skills/git-smart-commit/references/staging.md` est réécrit selon la décision « Staging »
  ci-dessus. Le mode de défaillance devient l'exclusion oubliée : c'est pour cela que les
  exclusions sont la seule liste présentée. Le critère d'exclusion est un fichier sans rapport
  avec la tâche en cours, et c'est l'agent qui en juge.
- `confirmation.md` :
  - ce qui est présenté se réduit au message, au tag et aux exclusions, plus les gestes
    irréversibles pour l'aplatissement ;
  - deux choix : 1. « Valider », libellé ajusté au contexte ; 2. « Autre chose » ;
  - l'accord couvre toutes les modifications en attente, sauf les exclusions présentées ;
  - pour un commit mécanique, l'accord se demande sans le titre ;
  - « Ce qui compte comme accord » est inchangé.
- `skills/git-smart-commit/SKILL.md`, ligne de `staging.md` : « jamais `-A` » est remplacé.
- La mémoire `projects/-home-debian--claude/memory/index-avant-commit.md` est supprimée, avec sa
  ligne de `MEMORY.md`.

Vérification :

```bash
! grep -rn -e "Voir le diff" -e "jamais \`-A\`" skills agents
test ! -e projects/-home-debian--claude/memory/index-avant-commit.md
! grep -q index-avant-commit projects/-home-debian--claude/memory/MEMORY.md
python3 scripts/check_pipeline.py
```

### E3 — Commits : les trois procédures

- `etape.md` :
  - en tête, « l'appelant fournit […] les chemins à stager » devient « les exclusions » ;
  - au point 2, un fichier hors de la tâche devient une exclusion présentée, et non plus un
    signalement qui bloque ;
  - le point 4 distingue les commits mécaniques (`<L>E0`, session, Passation), dont l'accord se
    demande sans titre, des commits d'Étape et de Retouche, proposés sous la forme du Brief
    (`Commit d'Étape proposé :`, Message avec pied d'attribution, Tag) ;
  - le point 5 stage selon `staging.md`.
- `hors-chantier.md` : l'exemple du point 5 perd « Chemins stagés » et le décompte des fichiers, et
  ne garde que le message et les exclusions. Le découpage en plusieurs commits suit la décision
  ci-dessus.
- `aplatissement.md` : le point 3 suit la décision « Aplatissement ». Dans l'abandon, « stagés par
  chemins » s'aligne sur `staging.md` ; les `git add` explicites des blocs de commandes restent,
  puisqu'ils visent des fichiers que le script vient de déplacer.

Vérification :

```bash
! grep -rn -e "hemins stagés" -e "chemins à stager" skills agents
grep -n "Commit d'Étape proposé" skills/git-smart-commit/references/etape.md
python3 scripts/check_pipeline.py
```

### E4 — intent-brief : échanger, écrire, corriger, puis proposer

- `skills/intent-brief/SKILL.md`, phases réécrites :
  0. Prérequis : inchangé.
  1. Reconnaissance : inchangée.
  2. Échanges : questions ouvertes, regroupées par thème, deux au plus par tour, ancrées dans un
     fait du dépôt (la contrainte de vérification de l'ancienne Phase 2 passe ici). Aucun fichier
     n'est écrit à ce stade.
  3. Écriture : le slug se choisit, le Brief se pose par `gabarit new brief` avec tout ce qui est
     établi, et toutes les ambiguïtés soulevées entrent aux incertitudes. Le message donne le
     chemin et les incertitudes, rien d'autre. Jusqu'à la validation, le slug se renomme (fichier
     et `slug` du front matter).
  4. Corrections et arbitrages : l'utilisateur ajuste, résout, exige ; chaque message qui modifie le
     Brief redonne son chemin et les incertitudes, rien d'autre. Les incertitudes restantes à
     réponses fermées se tranchent par `AskUserQuestion`, en un seul appel.
  5. Critères et signaux : l'agent les propose, l'utilisateur les décide.
  6. Validation : `gabarit check --filled`, puis `statut = "validé"`.
  7. Passage au suivi : inchangé.

  La section « Ma lecture » et la question « Qu'est-ce qui est faux là-dedans ? » sont retirées.
  La Règle directrice (« explorer → restituer → questionner ») devient « explorer → questionner →
  écrire ». « Sortie anticipée », « Règle du sourçage » (qui cite la restitution comme
  supposition assumée) et « Registre des ambiguïtés » sont ajustés aux nouveaux numéros et au
  registre qui naît avec l'écriture.
- Slug renommable jusqu'à la validation : `skills/implementation-tracker/references/contrat.md`,
  paragraphe **Slug** (« Arrêté au brief, il ne change plus ») devient « arrêté à la validation du
  brief » ; même correction pour la description de `fields.slug` du contrat du brief.
- `skills/intent-brief/references/grille-questions.md` : « une question par tour » devient deux
  au plus, regroupées par thème. Les axes « Signaux de dérive » et « Critères de réussite »
  deviennent des propositions de fin, et les axes prioritaires sont ajustés en conséquence.
- `skills/gabarit/gabarit/brief/contract.toml` : le commentaire de tête, la description de
  `statut = brouillon` et celle de `fields.slug` suivent le nouveau déroulement.

Vérification :

```bash
! grep -rni -e "Ma lecture" -e "Qu'est-ce qui est faux" -e "question par tour" -e "explorer → restituer" skills agents
gabarit check .claude/implementation/messages-du-pipeline.brief.md --filled
python3 scripts/check_pipeline.py
```

### E5 — Contexte et audit

- `skills/implementation-tracker/references/execution.md`, tableau des mesures : à 300 000 tokens
  ou moins, rien, et la mesure ne se dit pas ; au-delà, la question de la Passation, mesure
  comprise.
- `skills/implementation-tracker/references/audit.md`, « Au retour » :
  - l'inscription au Suivi se fait sans être annoncée ;
  - la restitution tient en une ligne (verdict et chemin du rapport), puis, s'il y a des réserves,
    le tableau `# | Réserve | Gravité réelle`, avec un commentaire court par réserve ;
  - le modèle de restitution est celui du Brief.
- `skills/implementation-tracker/references/cloture.md`, point 1 : renvoi à cette forme, sans la
  redire.

Vérification :

```bash
grep -n "Gravité réelle" skills/implementation-tracker/references/audit.md
grep -n "la mesure ne se dit pas" skills/implementation-tracker/references/execution.md
python3 scripts/check_pipeline.py
```

## Vérification de bout en bout

```bash
! grep -rn -e "Voir le diff" -e "Ma lecture" -e "Qu'est-ce qui est faux" -e "hemins stagés" skills agents
python3 scripts/check_pipeline.py
~/.claude/.venv/bin/python -m pytest scripts/tests/ -q
uvx ruff check scripts && uvx ruff format --check scripts
git diff --name-only --diff-filter=d master...HEAD -- '*.md' | xargs uvx rumdl fmt --check
test ! -e projects/-home-debian--claude/memory/index-avant-commit.md
```

À l'usage, le Chantier suivant en fournit l'épreuve : un Brief cadré par échanges, puis des
commits d'Étape proposés sous la forme du Brief.

## Shadow-skills

`skill-convention`.
