+++
gabarit = "suivi"
slug = "shadow-skill"
titre = "Shadow-skill : ranger les skills non indispensables hors du contexte, les trouver par CLI"
branche = "shadow-skill"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
execution = "direct"
plan = ".claude/implementation/done/2026-10-04-shadow-skill.plan.md"
brief = ".claude/implementation/done/2026-10-04-shadow-skill.brief.md"
audit = ".claude/implementation/done/2026-10-04-shadow-skill.audit.md"
skills = ["skill-convention"]
"créé" = 2026-10-04
maj = 2026-10-04
+++

## Objectif et périmètre

**Symptôme** : tous les skills globaux sont chargés en permanence dans le contexte ; il n'est pas
essentiel de les connaître en permanence, et il n'y a aucun moyen de rechercher les skills
pertinents pour un Chantier.

**But** : un système « shadow-skill » où ranger les skills non indispensables, hors du contexte,
que l'agent liste, recherche et charge par une CLI ; les skills pertinents pour un Chantier sont
recherchés au brief et au plan, et notés dans le Suivi.

**Critères de réussite** :
- La commande `shadow-skill`, exposée dans `bin/`, liste les shadow-skills globaux et locaux, les
  recherche (nom, description, tags) et affiche le fichier principal de l'un d'eux
- Une commande `shadow-skill` affiche les descriptions des skills que liste le tableau d'un Suivi
- `nvim-mini-test`, `emmylua-ls` et `skill-convention` sont des shadow-skills : leur `SKILL.md`
  passe `gabarit check <chemin> --filled`
- `skills/nvim-mini-test/` et `skills/emmylua-ls/` n'existent plus ; `skills/skill-convention/`
  garde sa description actuelle et renvoie vers son shadow-skill
- Un tag qu'aucun shadow-skill ne déclare dans le fichier des tags est signalé par une commande
- La Semence `suivi` porte le tableau des skills ; `intent-brief` et `implementation-tracker`
  disent de rechercher les shadow-skills au brief et au plan
- Le `CLAUDE.md` racine importe par `@` l'`instructions.md` qui explique les shadow-skills

**Hors-périmètre** :
- Déplacer `gabarit`, `list-dir` ou `lexique` : on en a besoin en permanence (dit)
- Le côté Neovim de l'intégration : le Chantier ne crée que les commandes qu'il appellera (dit)

**Signaux de dérive** :
- Le `SKILL.md` d'un shadow-skill n'est pas un Gabarit posé depuis une Semence (dit)
- Le diff touche `skills/gabarit/`, `skills/list-dir/` ou `skills/lexique/`, hors la Semence
  `skills/gabarit/gabarit/suivi/contract.toml` (dit)

## Étapes

- [x] 1. Semence `shadow-skill` — skills/shadow-skill/gabarit/shadow-skill/contract.toml — vérif: `SCRATCH=$(mktemp -d) && gabarit defs | grep -q shadow-skill && gabarit new shadow-skill $SCRATCH/x/SKILL.md && gabarit check $SCRATCH/x/SKILL.md && ! gabarit check $SCRATCH/x/SKILL.md --filled`
- [x] 2. Bibliothèque et CLI : `liste`, `cherche`, `charge`, `chemin` — skills/shadow-skill/scripts/{shadow_skill.py,shadow-skill-cli.py,tests/}, skills/shadow-skill/{ruff.toml,pyrightconfig.json}, bin/shadow-skill — vérif: `.venv/bin/python -m pytest skills/shadow-skill/scripts/tests && uvx ruff check skills/shadow-skill && (cd skills/shadow-skill && uvx --with pytest basedpyright) && command -v shadow-skill`
- [x] 3. CLI : `descriptions`, `tags`, `verifie` — skills/shadow-skill/scripts/{shadow_skill.py,shadow-skill-cli.py,tests/} — vérif: même commande qu'en 2
- [x] 4. Migrer `nvim-mini-test` et `emmylua-ls` — shadow-skills/{nvim-mini-test,emmylua-ls}/, shadow-skills/tags.toml — vérif: `shadow-skill verifie && shadow-skill cherche neovim | grep -c . | grep -qx 2 && test ! -e skills/nvim-mini-test && test ! -e skills/emmylua-ls`
- [x] 5. Migrer `skill-convention`, laisser son entrée dans `skills/` — shadow-skills/skill-convention/, skills/skill-convention/SKILL.md, rules/skill-prose.md, .claude/CLAUDE.md — vérif: `shadow-skill verifie && python3 scripts/check_pipeline.py`, comparaison du front matter à `master` et contrôle des liens (plan, Étape 4)
- [x] 6. Documentation et chargement en session — skills/shadow-skill/{SKILL.md,instructions.md}, CLAUDE.md, OUTILLAGE.md — vérif: `grep -qx '@skills/shadow-skill/instructions.md' CLAUDE.md && python3 scripts/check_pipeline.py && lexique liste >/dev/null`
- [x] 7. Brancher le pipeline — skills/gabarit/gabarit/suivi/contract.toml, skills/intent-brief/SKILL.md, skills/implementation-tracker/SKILL.md, ce Suivi — vérif: `.venv/bin/python -m pytest skills/gabarit skills/implementation-tracker skills/git-smart-commit scripts/tests && gabarit contract suivi | grep -q '^\[fields.skills\]' && gabarit check .claude/implementation/shadow-skill.md --filled && python3 scripts/check_pipeline.py`
- [x] 8. `cherche` ignore les accents — skills/shadow-skill/{SKILL.md,scripts/shadow_skill.py,scripts/shadow-skill-cli.py,scripts/tests/test_lire.py} — vérif: même commande qu'en 2, puis `shadow-skill cherche SYSTEME | cut -f2 | grep -qx emmylua-ls`
- [x] 9. Réduire le contexte permanent (réserve R1 de l'audit) — skills/shadow-skill/{SKILL.md,instructions.md} — vérif: `grep -qx '@skills/shadow-skill/instructions.md' CLAUDE.md && python3 scripts/check_pipeline.py && lexique liste >/dev/null`, puis octets ajoutés (instructions.md, description, ligne du lexique) < 1026
- [x] 10. Le lecteur de fiches accepte une liste de chaînes — skills/implementation-tracker/scripts/{fiche.py,tests/test_fiche.py}, skills/git-smart-commit/scripts/tests/test_commit_chantier.py — vérif: `.venv/bin/python -m pytest skills/implementation-tracker skills/git-smart-commit scripts/tests && python3 scripts/check_pipeline.py && commit-chantier cloture shadow-skill --message <fichier> --dry-run` ne refuse plus sur `skills`

## État courant

**Prochaine action** : reprendre la Clôture au dry-run d'aplatissement.

**Vérification** : la vérification de bout en bout du plan ; en dernier,
`git diff --stat master..shadow-skill -- skills/gabarit skills/list-dir skills/lexique` ne doit
rendre que la Semence `suivi`.

**Dernier audit** : 9d57deb — RÉSERVES — 2026-10-04

**Notes** : R1 traité à l'Étape 9 ; R2 levé par `/skills` en nouvelle session ; R3 à R9 et deux
constats de l'essai de la session 2 versés au Registre de dette.

## Journal de décisions

- **2026-10-04** — Le corps d'un Shadow-skill tient dans `## Instructions`, plus une section
  facultative `## Références`. *Pourquoi* : `check_sections` refuse les sections non déclarées.
  *Rejeté* : aucune section ; plusieurs sections fixes.
- **2026-10-04** — Le champ `skills` du Suivi est obligatoire, et les archives de `done/` restent
  intactes. *Pourquoi* : arbitrage de l'utilisateur. *Rejeté* : un champ facultatif ;
  `skills = []` ajouté aux archives.
- **2026-10-04** — Les entrées des registres qui citent des chemins déplacés ne sont pas
  retouchées. *Pourquoi* : le pipeline ne réécrit pas un Registre de lui-même ; l'écart est en dette.
- **2026-10-04** — Pour un skill migré, `description` garde ce qu'il couvre, `when-to-load` ses
  phrases de déclenchement. *Pourquoi* : `cherche` lit les deux champs. *Rejeté* : tout dans
  `description`.
- **2026-10-04** — « Shadow-skill » entre au lexique global, avec l'accord de l'utilisateur ;
  commande, Semence et chemins gardent `shadow-skill`.
- **2026-10-04** — `depuis-suivi SLUG` lit `.claude/implementation/<slug>.md`. *Pourquoi* : à la
  reprise, l'agent connaît le slug, pas le chemin. *Rejeté* : le chemin du Suivi en argument.
- **2026-10-04** — `liste` et `cherche` rendent `when-to-load` en quatrième colonne. *Pourquoi* :
  l'agent décide d'un `charge` sur ce champ. *Rejeté* : une sous-commande à part.
- **2026-10-04** — `cherche` plie casse et accents des deux côtés (Étape 8). *Rejeté* : plier la
  seule requête.
- **2026-10-04** — Réserve R1 : `instructions.md` ne garde que la recherche et le chargement, la
  description de `shadow-skill` que quoi, quand et sa limite (Étape 9). Le contexte permanent
  passe de +806 à −163 octets. *Rejeté* : redire la marche d'un Chantier, qu'implementation-tracker porte.
- **2026-10-04** — Clôture sans second audit après l'Étape 9, à la décision de l'utilisateur, qui
  a relu le diff lui-même.
- **2026-10-04** — `fiche.lire_front` rend les listes de chaînes dans `Front.listes`, à part des
  champs scalaires (Étape 10). *Pourquoi* : la clôture refusait tout Suivi portant `skills`.
  *Rejeté* : `skills` en chaîne, qui aurait changé Contrat, `depuis-suivi` et documentation.
