---
slug: shadow-skill
---

## 2026-10-04 — clôture — `9d57deb`

**Verdict** : RÉSERVES

Brief présent et lu ; Suivi, Plan (`.claude/plans/cuddly-humming-salamander.md`) et
`git diff master...shadow-skill` (40 fichiers, +1815 −120) lus. Aucune divergence entre Brief et
Suivi sur les critères, le Hors-périmètre et les Signaux de dérive.

### Vérifications exécutées

- Étape 1 — `gabarit defs | grep -q shadow-skill && gabarit new shadow-skill $SCRATCH/x/SKILL.md && gabarit check … && ! gabarit check … --filled` → rc 0 ; le fichier posé est « conforme », puis 5 manquements sous `--filled`, comme attendu.
- Étapes 2, 3, 8 — `.venv/bin/python -m pytest skills/shadow-skill/scripts/tests` → 43 passés, rc 0.
- `uvx ruff check skills/shadow-skill` → « All checks passed! », rc 0.
- `(cd skills/shadow-skill && uvx --with pytest basedpyright)` → « 0 errors, 0 warnings, 0 notes », rc 0.
- `command -v shadow-skill` → `/home/debian/.claude/bin/shadow-skill`, lien vers `../skills/shadow-skill/scripts/shadow-skill-cli.py`.
- Étape 8 — `shadow-skill cherche SYSTEME | cut -f2 | grep -qx emmylua-ls` → rc 0 (« système » trouvé sans accent ni casse).
- Étape 4 — `shadow-skill verifie` → rc 0, aucun constat ; `shadow-skill cherche neovim | grep -c .` → 2 ; `test ! -e skills/nvim-mini-test` et `test ! -e skills/emmylua-ls` → rc 0.
- `gabarit check shadow-skills/{emmylua-ls,nvim-mini-test,skill-convention}/SKILL.md --filled` → « rempli et conforme à la semence « shadow-skill » » pour les trois.
- Étape 5 — `python3 scripts/check_pipeline.py` → « Pipeline conforme. », rc 0 ; comparaison du front matter de `skills/skill-convention/SKILL.md` à `master` → aucune différence ; contrôle de liens du Plan sur `shadow-skills/` → aucune cible manquante, rc 0.
- Étape 6 — `grep -qx '@skills/shadow-skill/instructions.md' CLAUDE.md` → rc 0 ; `lexique liste` → rc 0.
- Étape 7 — `.venv/bin/python -m pytest skills/gabarit skills/implementation-tracker skills/git-smart-commit scripts/tests` → 222 passés ; `gabarit contract suivi | grep -q '^\[fields.skills\]'` → rc 0 ; `gabarit check .claude/implementation/shadow-skill.md --filled` → « rempli et conforme ».
- Bout en bout, point 1 — `shadow-skill liste` → les trois skills au niveau `global` ; `shadow-skill cherche mini.test` → `nvim-mini-test` seul.
- Point 2 — `shadow-skill charge emmylua-ls` → `Répertoire : /home/debian/.claude/shadow-skills/emmylua-ls` puis le fichier ; `shadow-skill depuis-suivi shadow-skill` → la ligne de `skill-convention`, rc 0.
- Point 3 — projet jetable (`git init`) avec un skill local portant un tag inventé : `verifie` → « tag « inventé » absent du registre (tags.toml) », rc 1. Tag local `lua` → « déjà déclaré au registre global », rc 1. Même nom aux deux niveaux : `charge` et `chemin` → rc 1, les deux chemins nommés.
- Point 5 — `git diff --stat master...shadow-skill -- skills/gabarit skills/list-dir skills/lexique` → seule `skills/gabarit/gabarit/suivi/contract.toml` (+7).
- Point 4 — nouvelle session sans `nvim-mini-test` ni `emmylua-ls` dans la liste des skills → NON EXÉCUTÉE : un sous-agent n'ouvre pas de session Claude Code. Le Suivi la laisse aussi en « Prochaine action ».
- Hors dépôt git, slug `../x`, slug absent, description multiligne avec tabulation → comportements nommés et rc attendus ; la tabulation est réduite à une espace, et la sortie reste à quatre colonnes.
- `impl-list` → rc 0 ; `python3 scripts/sante_skills.py` → rc 0.
- Archives `done/` estampillées `suivi` → 4 sur 4 en « 1 manquement » sous `gabarit check --filled` : c'est l'écart arbitré (Q5) et documenté dans `references/contrat.md`.

### Conformité à l'intention

- Critère « `shadow-skill` dans `bin/`, liste global et local, recherche (nom, description, tags), affiche le fichier principal » : atteint, vérifié (`liste`, `cherche`, `charge`, `chemin`, aux deux niveaux sur projet jetable).
- Critère « une commande affiche les descriptions des skills du tableau d'un Suivi » : atteint, vérifié (`depuis-suivi`, qui prend un slug au lieu d'un fichier ; décision datée au journal).
- Critère « les trois skills migrés passent `gabarit check --filled` » : atteint, vérifié.
- Critère « `skills/nvim-mini-test/` et `skills/emmylua-ls/` n'existent plus ; `skills/skill-convention/` garde sa description et renvoie à son Shadow-skill » : atteint, vérifié (front matter identique à `master`, corps qui renvoie à `shadow-skill charge skill-convention`).
- Critère « un tag non déclaré est signalé par une commande » : atteint, vérifié (`verifie` rc 1).
- Critère « la Semence `suivi` porte le tableau ; `intent-brief` et `implementation-tracker` disent de chercher au brief et au plan » : atteint, vérifié (`[fields.skills]` ; puces ajoutées à `intent-brief` Étape 1, au tracker Étape 2 points 2 et 7, et à la reprise).
- Critère « le `CLAUDE.md` racine importe par `@` l'`instructions.md` » : atteint, vérifié.
- Hors-périmètre : respecté. `gabarit`, `list-dir` et `lexique` restent dans `skills/`, et rien n'est écrit dans `~/.config/nvim/` (aucune occurrence de `shadow-skill`).
- Signaux de dérive : aucun ne s'est matérialisé. Les trois `SKILL.md` portent l'Estampille et passent le check, ce qui vaut Gabarit selon l'arbitrage Q9. Sous `skills/gabarit/`, `skills/list-dir/` et `skills/lexique/`, le diff ne touche que la Semence `suivi`, l'exception autorisée.
- Symptôme d'origine : la moitié « aucun moyen de rechercher » a disparu. L'autre moitié, « tous les skills chargés en permanence », ne recule pas encore, voir R1.

- **R1** — Le contexte permanent est plus gros qu'avant le Chantier, pas plus petit. Retiré :
  les descriptions de `nvim-mini-test` (620 octets) et d'`emmylua-ls` (406 octets). Ajouté à
  chaque session : `instructions.md` (1089 octets), la ligne `Shadow-skill` du lexique global
  (210 octets) et la description du nouveau skill `shadow-skill` (533 octets). Le solde est
  d'environ +800 octets. `skill-convention` garde sa description, par décision. Le Brief
  n'avait fixé aucun critère de taille, donc ce n'est pas un échec : le gain du mécanisme ne
  viendra qu'avec les migrations suivantes. Le constat doit être connu avant la Clôture, puisque
  le symptôme parle précisément de cette charge.
- **R2** — Le point 4 de la vérification de bout en bout (une nouvelle session ne liste plus les
  deux skills migrés) n'a pas été vérifié : un sous-agent ne peut pas l'exécuter, et le Suivi le
  laisse en prochaine action. Le mécanisme le rend très probable (les répertoires ont quitté
  `skills/`), mais l'effet visible du Chantier n'est pas établi en session.

### Qualité du code

Le code suit le style de `lexique` et `list-dir` : docstrings en français, principes en
majuscules, collecte séparée du jugement, `Result`/`fail`/`ok` de gabarit, une CLI sans logique
métier. Les erreurs sont nommées sur stderr, et aucun chemin d'échec n'est silencieux parmi ceux
que j'ai exercés. Les cas limites sont couverts par 43 tests : niveau absent, `SKILL.md` mal
formé, local confondu avec le global, ambiguïté, registre invalide, ensemble vide.

- **R3** — `skills/shadow-skill/scripts/shadow_skill.py`, `noms_du_suivi` : les noms du champ
  `skills` du Suivi sont validés par `_tags`, dont la docstring parle d'« une liste de chaînes »
  mais dont le nom dit « tags ». Le comportement est juste ; c'est le nom qui trompe le lecteur
  de `noms_du_suivi`. Défaut mineur.
- **R4** — `shadow-skills/skill-convention/references/prose.md` : la réécriture des liens
  (`../../` → `../../../skills/`) a allongé plusieurs lignes au-delà de la largeur de leurs
  voisines, sans les rejustifier. Défaut de forme, sans effet sur le rendu.

### Dette induite

- **R5** — La découverte du paquet gabarit par `bin/gabarit` (`shadow_skill.py`, en tête de
  module) et la ré-exécution dans le venv (`shadow-skill-cli.py`) sont des copies de
  `skills/list-dir/scripts/listdir/__init__.py` et de `list-dir.py` / `gabarit-cli.py`. Les
  commentaires renvoient à l'original, et le Plan l'a voulu ainsi. Ce bloc d'amorçage existe
  maintenant en trois exemplaires : il faudra modifier les trois ensemble au prochain changement
  de résolution du venv ou de `bin/`.
- **R6** — Les liens de `shadow-skills/` échappent au contrôle 8 de `check_pipeline.py`, avec
  leurs ancres (`#frontmatter`, `#dates-et-listing` dans `prose.md`). `prose.md` affirme pourtant
  que « `check_pipeline.py` les contrôle ». Le Journal la reconnaît déjà pour la Dette ; je la
  confirme.
- **R7** — `step-implementer` ne reçoit pas les Shadow-skills du Suivi. Le Journal la reconnaît
  déjà pour la Dette.
- **R8** — Des entrées vivantes citent des chemins déplacés. Dans le Registre de dette :
  `nvim-mini-test-redigee-en-anglais`, `emmylua-ls-description-sans-limite`, ainsi que
  `criteres-de-brief-bornes-a-une-extension`, `deux-conventions-de-mode-de-defaillance`,
  `intent-brief-description-sans-limite` et `list-dir-codes-de-sortie-non-dits`, qui citent
  `skills/skill-convention/references/prose.md`. La décision du Journal couvre ces entrées. Elle
  ne nomme pas l'entrée de road-map `todo/road-map/lexique-des-sous-agents.md`, qui cite
  `skills/skill-convention/references/{prose,commandes-locales}.md` : à faire figurer dans le même
  versement à la Dette, ou à trancher.
- **R9** — Le champ `skills` obligatoire fait échouer `gabarit check --filled` sur les quatre
  Suivis archivés estampillés `suivi`. Cet écart a été arbitré (Q5) et documenté ; je le
  rappelle pour qu'il ne surprenne pas un futur contrôle global de `done/`.

### Bloquants

Aucun. Tous les critères du Brief sont atteints et vérifiés, le Hors-périmètre est respecté et
aucun Signal de dérive ne s'est matérialisé. Je retiens RÉSERVES plutôt que FAVORABLE pour deux
raisons : R1 (le symptôme de charge permanente n'a pas encore reculé) et R2 (l'effet en session
n'est pas vérifié). L'utilisateur doit les connaître avant de clore.
