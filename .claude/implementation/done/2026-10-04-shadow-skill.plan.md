# Plan — shadow-skill

Brief : `.claude/implementation/shadow-skill.brief.md` (validé). Slug `shadow-skill`, exécution `direct`.

## Context

Tous les skills globaux sont chargés en permanence dans le contexte, et rien ne permet de chercher
ceux qui servent à un Chantier. On crée les shadow-skills : des skills rangés hors de `skills/`,
dans `shadow-skills/` (global) et `.claude/shadow-skills/` (local au projet), que l'agent liste,
recherche et charge par la commande `shadow-skill`. `nvim-mini-test`, `emmylua-ls` et
`skill-convention` y migrent. Au brief et au plan, on cherche les skills utiles au Chantier, et on
les note dans le tableau `skills` du Suivi ; à la reprise, une commande les remet au contexte.

**Rappel du brief** :
- *Critères* : commande `shadow-skill` dans `bin/` qui liste, recherche, charge ; descriptions
  des skills d'un Suivi ; les trois skills migrés passent `gabarit check --filled` ;
  `skills/nvim-mini-test/` et `skills/emmylua-ls/` disparaissent, `skills/skill-convention/`
  garde sa description et renvoie au shadow-skill ; tag hors registre signalé ; Semence `suivi`
  avec le tableau, `intent-brief` et le tracker qui disent de chercher ; `CLAUDE.md` racine qui
  importe un `instructions.md`.
- *Hors-périmètre* : déplacer `gabarit`, `list-dir`, `lexique` ; le côté Neovim (on ne crée que
  les commandes).
- *Signaux de dérive* : un `SKILL.md` de shadow-skill qui n'est pas un Gabarit ; un diff qui
  touche `skills/gabarit/`, `skills/list-dir/` ou `skills/lexique/`, hors
  `skills/gabarit/gabarit/suivi/contract.toml`.
- *Incertitude levée ici* : les commandes Neovim sont `liste`, `cherche` et `chemin`, à sortie
  tabulée stable (Étape 2).

## Décisions de conception

- **Le corps d'un shadow-skill** : une seule section obligatoire, `## Instructions` (arbitré par
  l'utilisateur). Les `##` d'origine passent en `###`, et ainsi de suite, **hors blocs de code**.
  Pourquoi : `check_sections` refuse toute section non déclarée
  (`skills/gabarit/scripts/gabarit/check.py:74`), et on n'assouplit pas gabarit.
- **Champs de la Semence** : `name` (slug), `description` (text), `when-to-load` (text), `tags`
  (list), tous obligatoires. Aucun champ ajouté : `verifie` contrôle que `name` est le nom du
  répertoire, et ça suffit.
- **La CLI importe la bibliothèque gabarit** (`read_item`, `commandes.check`, `prefill.racine_git`)
  par le même mécanisme que `skills/list-dir/scripts/listdir/__init__.py:35-54`. Elle se
  ré-exécute dans le venv comme `gabarit-cli.py` (le paquet importe tomlkit). On ne réécrit pas de
  lecteur de front matter.
- **Deux niveaux, comme lexique** : global = `<config>/shadow-skills/`, avec `<config>` déduit de
  la position du module (`parents[3]`, comme `lexique.racine_globale`) ; local =
  `<racine git>/.claude/shadow-skills/`. Si local et global désignent le même répertoire résolu,
  on ne le lit qu'une fois. Un même nom aux deux niveaux est un constat de `verifie`, et une
  ambiguïté pour `charge` et `chemin`, qui échouent en nommant les deux chemins.
- **Registre des tags** : `tags.toml` plat à la racine de chaque niveau (`tag = "description"`).
  Un tag local qui redéfinit un tag global est un constat, comme un terme local déjà réservé au
  global dans lexique.

## Étapes

### 1. Semence `shadow-skill`

Fichier : `skills/shadow-skill/gabarit/shadow-skill/contract.toml` (rang 4 de la recherche des
Semences, `skills/gabarit/references/semences.md`) : les quatre champs et la section
`Instructions`, chacun avec la `description` de ce qu'il attend. `when-to-load` : « dans quelle
situation charger ce skill, en une ou deux phrases — c'est ce que lit `cherche` ».

Vérif : `SCRATCH=$(mktemp -d) && gabarit defs | grep -q shadow-skill && gabarit new shadow-skill $SCRATCH/x/SKILL.md && gabarit check $SCRATCH/x/SKILL.md && ! gabarit check $SCRATCH/x/SKILL.md --filled` (posé avec ses Marqueurs, il passe sans `--filled` et échoue avec).

### 2. Bibliothèque, CLI, tests

Coupée en deux (arbitrage Q4) : **2a** la bibliothèque, la CLI, `liste`, `cherche`, `charge`,
`chemin`, leurs tests, les deux configurations et le lien `bin/` ; **2b** `descriptions`, `tags`,
`verifie` et leurs tests. Même commande de vérification pour les deux.

Fichiers : `skills/shadow-skill/scripts/shadow_skill.py` (logique),
`skills/shadow-skill/scripts/shadow-skill-cli.py` (arguments → codes de sortie, aucune logique),
`skills/shadow-skill/scripts/tests/`, `skills/shadow-skill/ruff.toml` (copié de `skills/lexique/`), `skills/shadow-skill/pyrightconfig.json`
(copié de `skills/list-dir/`, dont les `extraPaths` portent `../gabarit/scripts`), lien `bin/shadow-skill`.

Toutes les commandes acceptent `--projet DIR` ; sans lui, le projet est la racine git du
répertoire courant (comme lexique).

| Commande | Sortie | Codes |
|---|---|---|
| `liste` | `niveau\tnom\tdescription`, global puis local | 0 ; 1 si un niveau est illisible (l'autre est servi) |
| `cherche MOT…` | même format ; tous les mots, sans casse, dans le nom, la description, `when-to-load` ou les tags | 0 au moins un ; 1 aucun |
| `charge NOM` | ligne `Répertoire : <chemin absolu>` (pour résoudre les liens relatifs), puis le `SKILL.md` | 0 ; 1 inconnu (liste les noms connus) ou ambigu |
| `chemin NOM` | chemin absolu du `SKILL.md` (Neovim) | 0 ; 1 inconnu ou ambigu |
| `descriptions FICHIER` | `nom\tdescription\twhen-to-load` pour chaque nom du champ `skills` de FICHIER | 0 ; 1 champ absent ou nom inconnu (les autres sont servis) |
| `tags` | `niveau\ttag\tdescription` | 0 ; 1 registre illisible ou mal formé |
| `verifie` | constats sur stderr : `gabarit check --filled` de chaque `SKILL.md`, nom = répertoire, tag hors registre, tag local qui redéfinit un global, nom présent aux deux niveaux | 0 conforme ; 1 constat, **ou aucun shadow-skill examiné** |

Vérif : `.venv/bin/python -m pytest skills/shadow-skill/scripts/tests && uvx ruff check skills/shadow-skill && (cd skills/shadow-skill && uvx --with pytest basedpyright) && command -v shadow-skill`

### 3. Migrer `nvim-mini-test` et `emmylua-ls`

`git mv skills/<nom> shadow-skills/<nom>`. Dans chaque `SKILL.md` : le front matter YAML devient
un front matter TOML `+++` (Estampille `gabarit = "shadow-skill"`, `name`, `description` reprise
mot pour mot, `when-to-load` tiré de la partie « se déclencher quand… » de la description, `tags`).
Puis `## Instructions` sous le titre `#`, et les titres décalés d'un niveau hors blocs de code.
On pose `shadow-skills/tags.toml` avec les tags employés (proposés : `neovim`, `lua`, `tests`,
`lsp`) et leur description d'une ligne.

Vérif : `shadow-skill verifie && shadow-skill cherche neovim | grep -c . | grep -qx 2 && test ! -e skills/nvim-mini-test && test ! -e skills/emmylua-ls`

### 4. Migrer `skill-convention`, laisser son entrée dans `skills/`

- `git mv` de `SKILL.md`, `references/` et `modeles/` vers `shadow-skills/skill-convention/` ;
  même conversion qu'à l'Étape 3 (tag proposé : `conventions`).
- **On réécrit les liens relatifs qui sortent du skill**, puisqu'il ne vit plus dans `skills/` :
  `../<skill>/` devient `../../skills/<skill>/` dans `SKILL.md`, et `../../<skill>/` devient
  `../../../skills/<skill>/` dans `references/`. `../../OUTILLAGE.md`,
  `../../../OUTILLAGE.md` et `../../../scripts/…` ne changent pas.
- **Nouvelle entrée `skills/skill-convention/SKILL.md`** : le même front matter YAML (description
  identique), et un corps d'un paragraphe qui renvoie à `shadow-skill charge skill-convention`.
- `rules/skill-prose.md` : son lien vers `prose.md` pointe vers le nouveau chemin, et `paths`
  couvre aussi `shadow-skills/*/SKILL.md`, `shadow-skills/*/references/**/*.md` et leurs
  équivalents `**/.claude/shadow-skills/**`.
- `.claude/CLAUDE.md`, section Conventions : on y dit de charger par `shadow-skill charge skill-convention`.

Vérif : `shadow-skill verifie && python3 scripts/check_pipeline.py && diff <(git show master:skills/skill-convention/SKILL.md | awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{exit} f') <(awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{exit} f' skills/skill-convention/SKILL.md) && <contrôle de liens ci-dessous>`

```bash
.venv/bin/python - <<'EOF'
import re, pathlib, sys
bad = [f"{md}: {t}" for md in pathlib.Path("shadow-skills").rglob("*.md")
       for t in re.findall(r"\]\(([^)#\s]+)", md.read_text(encoding="utf-8"))
       if "://" not in t and not (md.parent / t).exists()]
print(*bad, sep="\n"); sys.exit(bool(bad))
EOF
```

### 5. Documentation et chargement en session

- `skills/shadow-skill/SKILL.md` (YAML, description courte) : poser un shadow-skill
  (`gabarit new shadow-skill shadow-skills/<nom>/SKILL.md`, enregistrer ses tags, `verifie`), et
  la référence des commandes avec leurs codes. On y signale que `liste`, `cherche` et `chemin`
  sont faites pour la future intégration Neovim.
- `skills/shadow-skill/instructions.md` (une quinzaine de lignes au plus, il se charge à chaque
  session) : ce que sont les shadow-skills, les deux niveaux, quand chercher
  (`shadow-skill tags`, puis `cherche`, puis `charge`).
- `CLAUDE.md` racine : ajouter `@skills/shadow-skill/instructions.md`, à côté de l'import de lexique.
- `OUTILLAGE.md` : ajouter une ligne `shadow-skill` au tableau des dépendances.
- **Lexique** : proposer à l'utilisateur une ligne `Shadow-skill` pour le global. Elle ne s'écrit
  que sur son accord.

Vérif : `grep -qx '@skills/shadow-skill/instructions.md' CLAUDE.md && python3 scripts/check_pipeline.py && lexique liste >/dev/null`

### 6. Brancher le pipeline

- `skills/gabarit/gabarit/suivi/contract.toml` (la seule exception du signal) : ajouter
  `[fields.skills]`, `type = "list"`, obligatoire, avec cette description : « les shadow-skills
  utiles au Chantier, retenus au plan par `shadow-skill cherche` ; `[]` si aucun ».
- `skills/intent-brief/SKILL.md`, Étape 1 : une puce qui dit de lancer `shadow-skill tags` et
  `shadow-skill cherche <mots du sujet>`, puis de charger les skills pertinents pour la
  reconnaissance.
- `skills/implementation-tracker/SKILL.md` :
  - Étape 2, point 2 : chercher et charger les shadow-skills pendant le plan ;
  - points 5 et 7 : remplir `skills` ;
  - Étape 3 (reprise) : `shadow-skill descriptions <suivi>`.
- Le Suivi de ce Chantier reçoit son champ `skills`.

Vérif : `.venv/bin/python -m pytest skills/gabarit skills/implementation-tracker skills/git-smart-commit scripts/tests && gabarit contract suivi | grep -q '^\[fields.skills\]' && gabarit check .claude/implementation/shadow-skill.md --filled && python3 scripts/check_pipeline.py`

## Vérification de bout en bout

1. `shadow-skill liste` montre les trois skills au niveau global ; `shadow-skill cherche mini.test`
   ne rend que `nvim-mini-test`.
2. `shadow-skill charge emmylua-ls` affiche le répertoire puis le fichier.
   `shadow-skill descriptions .claude/implementation/shadow-skill.md` rend la ligne de
   `skill-convention`.
3. `shadow-skill verifie` sort 0. Un tag inventé, ajouté dans une copie en `$SCRATCH`, le fait
   sortir 1.
4. Une nouvelle session ne montre plus `nvim-mini-test` ni `emmylua-ls` dans la liste des skills,
   et montre toujours `skill-convention`.
5. `git diff --stat master..shadow-skill -- skills/gabarit skills/list-dir skills/lexique` ne
   rend que `skills/gabarit/gabarit/suivi/contract.toml`.

## Risques

- **Les liens des shadow-skills échappent au garde-fou** : le contrôle 8 de `check_pipeline.py`
  ne lit que `skills/`. Le contrôle ponctuel de l'Étape 4 compense pour ce Chantier ; l'extension
  du garde-fou part en dette à la Clôture.
- **`step-implementer` ne reçoit pas les shadow-skills du Suivi** : les agents dupliquent leurs
  règles et ne sont pas dans le brief. Ce point part en dette.

## Verdict de plan-reviewer : NON CONFORME

Le plan couvre tous les critères, respecte le hors-périmètre, ne déclenche aucun signal de dérive
et tranche l'incertitude. Le verdict tient seulement à la qualité.

**Corrigé dans ce plan, parce que c'étaient des défauts de rédaction** :
- **Q1** : la vérification de l'Étape 6 était inopérante (`gabarit contract suivi skills` sort 2).
  Elle devient `gabarit contract suivi | grep -q '^\[fields.skills\]'`.
- **Q2** : `$SCRATCH` n'était défini nulle part. L'Étape 1 le définit (`mktemp -d`).
- **Q3** : le `pyrightconfig.json` est maintenant copié de `skills/list-dir/`, qui sait résoudre
  les imports gabarit.
- **Q6** : l'Étape 6 vérifie désormais le Suivi du Chantier par `gabarit check --filled`.
- **Q7** : l'Étape 4 compare le front matter de `skills/skill-convention/SKILL.md` à celui de `master`.
- **Q10** : la citation `__init__.py:35-53` devient `35-54`.

**Laissé à ton arbitrage** :
- **Q5** : `skills` obligatoire fait échouer `gabarit check --filled` sur les quatre Suivis
  archivés de `done/`, qui passent aujourd'hui. Trois issues possibles : le champ devient
  facultatif ; on accepte l'échec, puisque ces archives sont figées ; ou on ajoute `skills = []`
  à chacune.
- **Q4** : l'Étape 2 est grosse. Elle se coupe en deux si tu veux : 2a la bibliothèque, ses tests
  et `liste`, `cherche`, `charge`, `chemin` ; 2b `descriptions`, `tags`, `verifie`.
- **Q8** : des entrées vivantes du Registre de dette citent des chemins que le Chantier déplace
  (`nvim-mini-test-redigee-en-anglais`, `emmylua-ls-description-sans-limite`, et celles qui
  citent `skills/skill-convention/references/prose.md`). On les met à jour, ou on les laisse.
- **Q9** : les trois `SKILL.md` migrés sont convertis à la main, avec leur Estampille, sans être
  posés par `gabarit new`. Ils passent `check`. Reste à savoir si cela te suffit au regard du
  signal « un `SKILL.md` de shadow-skill qui n'est pas un Gabarit ».

## Arbitrages de l'utilisateur après relecture

- **Q5** : `skills` reste obligatoire, et les archives de `done/` restent intactes, même si elles ne passent plus le check.
- **Q4** : l'Étape 2 est coupée en 2a et 2b.
- **Q8** : on laisse les entrées du Registre de dette ; l'écart est noté au journal.
- **Q9** : la conversion à la main suffit, dès lors que le fichier passe `gabarit check --filled`.
