# Plan — skill-convention

> **Relecture `plan-reviewer` : NON CONFORME**, puis arbitré par l'utilisateur (2026-09-17) :
>
> 1. docstrings Google prescrites sans être pratiquées : dérogation **ratifiée** ;
> 2. critère de citation **élargi au dépôt** : une convention cite au moins un site du dépôt
>    (skill, script, hook, agent) ;
> 3. mode de défaillance : **intégré à la prose** — les blocs cités `> *Mode de défaillance*`
>    deviennent un écart à consigner en dette ;
> 4. étape 6 **découpée** en 6 (prose) et 7 (code) ;
> 5. étape 1 : vérification déclarative, acceptée.
>
> Corrigé d'office (rédaction) : hook RTK cité (`rtk hook claude`) ; vérification « aucune skill
> éditée » qui voit les fichiers non suivis.

Brief : `.claude/implementation/skill-convention.brief.md` (validé). Exécution : `direct`.

## Contexte

Les pratiques de rédaction des skills et de code Python sont aujourd'hui implicites : elles se
lisent dans les skills, dans `OUTILLAGE.md`, dans quelques commits (`e9f6a81`) et sont vérifiées
en partie par `scripts/check_pipeline.py`. Le chantier crée `skills/skill-convention/` pour les
écrire. La skill **décrit** et ne corrige rien : les écarts des skills existantes vont au
registre de dette. Elle livre aussi la procédure des commandes locales à un projet, ce qui solde
l'entrée de road-map `commandes-locales-au-projet`.

Rappels du brief qui bornent le plan :

- **Critères** : `check_pipeline.py` passe ; chaque convention cite au moins un site du dépôt
  où elle est pratiquée (élargi le 2026-09-17, était « une skill ») ; une entrée de dette par skill en écart, conforme à `list-dir validate` ;
  l'entrée de road-map sort à la clôture.
- **Hors-périmètre** : aucune skill existante n'est éditée ; `OUTILLAGE.md` et
  `rules/lua-style.md` restent inchangés, la skill y renvoie.
- **Signaux de dérive** : la skill recopie une règle au lieu d'y renvoyer ; une skill existante
  est éditée.
- **Incertitudes à lever** : frontière `rules/` ↔ skill (tranchée ci-dessous) ; couverture des
  sous-agents par `CLAUDE_ENV_FILE` et cohabitation avec RTK (étape 1).

Arbitrages pris en plan mode (dit) :

- **Docstrings au format Google** : aucune occurrence de `Args:`/`Returns:` dans le dépôt. La
  convention est écrite comme **prescriptive, marquée « pas encore pratiquée »** — seule
  exception au critère de citation — et le code existant part en dette.
- **Commandes locales** : une référence de procédure **et** un script de hook modèle à copier.

## Frontière `rules/` ↔ skill

- `rules/python-style.md` (frontmatter `paths: ["**/*.py"]`, sur le modèle de
  `rules/lua-style.md`) **porte les règles de code** : c'est lui que Claude Code charge au
  contact d'un fichier Python. Il est l'autorité.
- La skill ne fait qu'**y renvoyer** : pas une règle de code recopiée dans `skills/`.
- La skill porte la prose des skills et les commandes locales.
- Lancer les linters : autorité `OUTILLAGE.md`, renvoi seulement.

## Arborescence livrée

```
skills/skill-convention/
  SKILL.md                      oriente : périmètre, table des références
  references/prose.md           conventions de prose d'une skill
  references/commandes-locales.md
  modeles/commandes-locales.sh  hook SessionStart modèle, à copier dans un projet
rules/python-style.md           conventions de code Python
```

Le modèle n'est invoqué par aucun `.md` : il n'a pas de lien dans `bin/`, conformément à
`OUTILLAGE.md` (« Un script qu'aucun .md n'invoque n'a pas besoin de lien »). La référence le
désigne par un lien Markdown relatif, pas par une commande à chemin — le contrôle de
portabilité de `check_pipeline.py` refuse l'appel relatif.

## Étapes

- [ ] 1. Vérifier `CLAUDE_ENV_FILE` : sous-agents et cohabitation RTK — suivi (journal) — vérif: résultat consigné au journal avec la commande rejouable
- [ ] 2. Poser `SKILL.md` — `skills/skill-convention/SKILL.md` — vérif: `.venv/bin/python scripts/check_pipeline.py`
- [ ] 3. Écrire les conventions de prose — `skills/skill-convention/references/prose.md` — vérif: `.venv/bin/python scripts/check_pipeline.py`
- [ ] 4. Écrire les conventions de code — `rules/python-style.md` — vérif: `head -5 rules/python-style.md` montre `paths` et `.venv/bin/python scripts/check_pipeline.py`
- [ ] 5. Écrire la procédure des commandes locales et son modèle — `references/commandes-locales.md`, `modeles/commandes-locales.sh` — vérif: `bash -n` puis essai du modèle (ci-dessous)
- [ ] 6. Consigner les écarts à la prose en dette — `.claude/implementation/todo/technical-debt/*.md` — vérif: `list-dir validate .claude/implementation/todo/technical-debt`
- [ ] 7. Consigner les écarts au code Python en dette — `.claude/implementation/todo/technical-debt/*.md` — vérif: `list-dir validate .claude/implementation/todo/technical-debt`
- [ ] 8. Contrôle final des bornes — aucun — vérif: commandes de la section Vérification

### 1. Vérifier `CLAUDE_ENV_FILE`

Lever l'incertitude reportée avant d'écrire la procédure. Dans un projet jetable du
scratchpad : un `.claude/settings.json` avec un hook `SessionStart` qui écrit
`export PATH="$CLAUDE_PROJECT_DIR/.claude/bin:$PATH"` avec `>>` dans `$CLAUDE_ENV_FILE`, et une
commande `.claude/bin/sonde`. Lancer `claude -p` qui appelle `sonde` en direct, puis via un
sous-agent. Consigner : la commande est-elle trouvée dans chaque cas ; le hook RTK
(`rtk hook claude`, `PreToolUse` de `settings.json`) laisse-t-il passer la commande ; le hook
`SessionStart` global (`scripts/sante_skills.py`) coexiste-t-il sans écraser `$CLAUDE_ENV_FILE`. Documentation Claude Code
consultée en complément (hooks `SessionStart`, `CLAUDE_ENV_FILE`). Un résultat négatif pour les
sous-agents ne bloque pas : il devient une limite écrite dans la procédure, avec le repli
(annonce dans `agents/*.md` ou chemin absolu), sur le modèle de `hooks/outillage-rappel.sh`.

### 2. `SKILL.md`

Frontmatter `name` + `description` avec déclencheurs (« Se déclenche dès que… ») et périmètre
négatif (« Ne corrige aucune skill »), comme `gabarit` et `list-dir`. Corps : un paragraphe
d'orientation, la table des références (prose, commandes locales, `rules/python-style.md`,
`OUTILLAGE.md`), et la règle « un écart constaté va en dette, jamais en correction d'office ».
Court : il oriente, les références détaillent — c'est la forme de `git-smart-commit/SKILL.md`.

### 3. `references/prose.md`

Une section `##` par convention. Chaque section : la règle, son motif (le mode de défaillance),
et une ligne **Pratiqué dans** qui cite au moins un site du dépôt. Candidats relevés à
la reconnaissance, à confirmer par lecture des skills :

- `SKILL.md` oriente, `references/` détaillent, lecture à la demande (`git-smart-commit`,
  `list-dir`, `implementation-tracker`) ;
- une règle définie à un seul endroit, les autres y renvoient (`e9f6a81`,
  `implementation-tracker/references/contrat.md`) — **renvoi** à ce contrat, pas de recopie ;
- les skills se citent par lien relatif `../<skill>/references/…` (`8b82930`) ;
- exécutable exposé dans `bin/`, appelé par son nom — **renvoi** à `OUTILLAGE.md` ;
- description du frontmatter : ce que fait la skill, quand elle se déclenche, ce qu'elle ne
  fait pas (`gabarit`, `list-dir`) ;
- codes de sortie 0/1/2, message sur stderr (`gabarit`, `list-dir`) ;
- échec fermé pour un outil de vérification, ouvert pour un rappel
  (`scripts/check_pipeline.py`, `hooks/outillage-rappel.sh`) ;
- dates par `date +%F`, jamais inventées — **renvoi** à `contrat.md#dates-et-listing` ;
- prose française, accents compris ; un sous-agent recopie volontairement ses règles
  (`agents/*.md`, exception documentée de `check_pipeline.py`).

**Forme du mode de défaillance** : intégrée à la prose (arbitrage du 2026-09-17), comme les
références de `list-dir`. La section cite la dette `deux-conventions-de-mode-de-defaillance`,
que cet arbitrage tranche : elle se solde à l'étape 6.

Ne jamais reprendre verbatim une phrase de `contrat.md` : le contrôle des empreintes exige
qu'elle n'apparaisse qu'une fois dans `skills/`.

### 4. `rules/python-style.md`

Même forme que `rules/lua-style.md`, chaque règle suivie de sa source. Candidats :

- Python ≥ 3.12, généricité PEP 695, garde de version dans le point d'entrée
  (`gabarit/scripts/gabarit/types.py`) ;
- basedpyright en `typeCheckingMode: "all"`, `pyrightconfig.json` et `ruff.toml` **par skill**,
  qui voyagent avec elle (`gabarit/ruff.toml`) — lancement : renvoi à `OUTILLAGE.md` ;
- `cast` commenté plutôt que `# type: ignore` (`types.py`, `Result.unwrap`) ;
- docstring de module avec des paragraphes-clés en capitales (`PORTÉE :`, `ÉCHEC FERMÉ :`)
  (`types.py`, `check_pipeline.py`) ;
- **docstrings compactes au format Google** (`Args:`, `Returns:`, `Raises:` seulement s'ils
  apportent) — *prescrite, pas encore pratiquée* ;
- collecte et jugement séparés, fonctions pures sans `print`/`exit` (`check_pipeline.py`) ;
- `Result[T]` plutôt qu'exception entre couches (`gabarit/types.py`) ;
- constantes définies à un seul endroit, avec le motif en commentaire (`PLACEHOLDER`) ;
- tests pytest sous `scripts/tests/` de la skill.

Les chemins cités dans `rules/` ne sont vus par aucun contrôle (dette
`garde-fou-borne-a-skills`) : les vérifier à la main par `ls` avant de clore l'étape.

### 5. Commandes locales

`references/commandes-locales.md` :

- **Global** : une commande globale n'est déclarée que par une skill de `~/.claude/skills`,
  exposée dans `bin/` — renvoi à `OUTILLAGE.md`.
- **Local** : `.claude/bin/` versionné dans le projet, un exécutable par commande ; hook
  `SessionStart` dans le `.claude/settings.json` **du projet** ; `export` ajouté par `>>` à
  `$CLAUDE_ENV_FILE` ; garde sur le répertoire, échec ouvert ; annonce des commandes par la
  sortie du hook.
- **Écartés**, avec leur motif : alias, fonctions shell, clé `env` des settings.
- **Limites** : résultats de l'étape 1.
- **Comment une skill s'en sert** : le modèle à copier, le bloc `settings.json` à ajouter.

`modeles/commandes-locales.sh` : bâti sur `hooks/outillage-rappel.sh` (en-tête qui dit la portée,
`set -uo pipefail`, garde, `exit 0` sur toute absence), qui liste les commandes de `.claude/bin/`.

Essai : dans un projet jetable du scratchpad, `CLAUDE_ENV_FILE=$(mktemp)` et
`CLAUDE_PROJECT_DIR=<projet>`, lancer le modèle deux fois — le fichier porte deux lignes
ajoutées, aucune écrasée ; hors du projet, sortie 0 et fichier inchangé.

### 6 et 7. Dettes

Étape 6 : confronter chaque skill de `skills/` (hors `skill-convention`) aux conventions de
l'étape 3 ; y compris les blocs `> *Mode de défaillance*` restants, à rattacher à la dette
`deux-conventions-de-mode-de-defaillance` (mise à jour de son constat et de « Pour solder »).
Étape 7 : même travail pour le Python, contre `rules/python-style.md`.
Une entrée par skill en écart, par `list-dir new` sur `.claude/implementation/todo/technical-debt`
(syntaxe exacte : `list-dir help new`), remplie selon `list-dir contract`. `source` = « chantier
`skill-convention` ». Le Python sans docstring Google fait partie des écarts de `gabarit` et
`list-dir`. Pas de doublon avec une entrée existante : `list-dir list` d'abord ; un écart déjà
consigné est cité, pas recréé.

### 8. Contrôle final

Voir Vérification. Tout écart relevé ici se remonte, ne se corrige pas en silence.

## Vérification

```bash
.venv/bin/python scripts/check_pipeline.py                     # « Pipeline conforme. »
{ git diff --name-only master -- skills OUTILLAGE.md rules/lua-style.md; \
  git ls-files --others --exclude-standard -- skills; } \
  | grep -v '^skills/skill-convention/'                        # vide : aucune skill existante éditée
list-dir validate .claude/implementation/todo/technical-debt   # conforme
grep -c 'Pratiqué dans' skills/skill-convention/references/prose.md  # = nombre de sections ##
bash -n skills/skill-convention/modeles/commandes-locales.sh
```

La sortie de l'entrée de road-map est faite par la clôture (`road-map:` du suivi), pas par une
étape.
