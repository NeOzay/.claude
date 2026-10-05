+++
gabarit = "suivi"
slug = "retouches-et-modele-du-chantier"
titre = "Cadrer les retouches post-étape et choisir au Plan le modèle d'implémentation"
branche = "retouches-et-modele-du-chantier"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
"modèle" = "opus"
plan = ".claude/implementation/done/2026-10-05-retouches-et-modele-du-chantier.plan.md"
brief = ".claude/implementation/done/2026-10-05-retouches-et-modele-du-chantier.brief.md"
audit = ".claude/implementation/done/2026-10-05-retouches-et-modele-du-chantier.audit.md"
skills = ["skill-convention"]
"créé" = 2026-10-05
maj = 2026-10-05
+++

## Objectif et périmètre

**Symptôme** : « De nombreux commits de retouches post-étape ont dû être réalisés, mais rien dans
implementation-tracker ne cadre ce cas » ; et le modèle d'implémentation, Sonnet ou Opus, n'est
choisi nulle part.

**But** : une retouche d'Étape livrée a son nom de commit et son tag, `<slug>: E<N>.<k>` et
`<L>E<N>.<k>` ; le Plan choisit le modèle qui conduira toute l'implémentation, et le Suivi le
porte.

**Critères de réussite** :

- Le type 2 de `git-smart-commit` a un cas « Retouche » : message `<slug>: E<N>.<k> — …`, tag
  `<L>E<N>.<k>`
- La Clôture et l'Abandon suppriment aussi les tags `<L>E<N>.<k>`, et un test le montre :
  `.venv/bin/python -m pytest skills/git-smart-commit`
- Plus aucune trace vivante de la délégation :
  `git grep -n -e step-implementer -e délégu -e execution -- ':!.claude/implementation/done'
  ':!.claude/implementation/todo' ':!.claude/plans'` ne rend que ce qui ne parle pas du
  mécanisme supprimé
- `gabarit contract suivi` déclare le champ du modèle ; ni `suivi` ni `brief` ne déclarent
  `execution`
- `scripts/check_pipeline.py` passe, ainsi que ruff et basedpyright sur le Python touché

**Hors-périmètre** :

- Migrer les Suivis des Chantiers déjà ouverts (claude-translator compris) : le champ
  `execution` est supprimé, l'utilisateur corrige à la main si nécessaire

**Signaux de dérive** :

- Un mécanisme qui choisit ou change le modèle à la place de l'utilisateur : hook, script, appel
  à `/model`
- Un modèle choisi par Étape ou par session, et non pour tout le Chantier
- Une retouche qui crée une Étape au Suivi au lieu de rester rattachée à l'Étape N
- Une archive de `done/` modifiée pour en retirer `execution`

## Étapes

V-garde, V-tests et V-md sont définies au Plan (§ Vérifications communes).

- [x] 1. Tags de Retouche dans `commit-chantier` —
      `skills/git-smart-commit/scripts/commit_chantier.py`,
      `skills/git-smart-commit/scripts/tests/test_commit_chantier.py` — vérif: V-tests,
      `uvx ruff format --check skills/git-smart-commit/scripts`,
      `uvx ruff check skills/git-smart-commit/scripts`,
      `uvx --with pytest basedpyright skills/git-smart-commit/scripts`
- [x] 2. Cas « Retouche » du commit rapide de chantier —
      `skills/git-smart-commit/references/{etape,tags-etape,aplatissement}.md`, `LEXIQUE.md` —
      vérif: V-garde, V-md, `lexique liste | grep -F Retouche`
- [x] 3. La Retouche dans implementation-tracker —
      `skills/implementation-tracker/references/{execution,contrat}.md`,
      `skills/implementation-tracker/SKILL.md`, `skills/gabarit/gabarit/suivi/contract.toml` —
      vérif: V-garde, V-tests, V-md, `gabarit contract suivi | grep -F 'dernier tag'`
- [x] 4. Retirer `step-implementer` et la délégation du tracker — `agents/step-implementer.md`,
      `skills/implementation-tracker/references/{execution,creation,contrat}.md`,
      `scripts/check_pipeline.py`, `shadow-skills/skill-convention/references/prose.md`,
      `LEXIQUE.md` — vérif: V-garde, V-tests, V-md, `test ! -e agents/step-implementer.md`,
      `git grep -n -e step-implementer -e délégu -e délégab -- skills/implementation-tracker scripts/check_pipeline.py shadow-skills LEXIQUE.md agents`
      vide
- [x] 5. Retirer `execution` des Semences et d'intent-brief —
      `skills/gabarit/gabarit/{brief,suivi}/contract.toml`, `skills/intent-brief/SKILL.md`, ce Suivi
      — vérif: V-tests, V-garde, `gabarit contract brief | grep -c execution` → 0,
      `gabarit contract suivi | grep -c execution` → 0,
      `gabarit check .claude/implementation/retouches-et-modele-du-chantier.md --filled`
- [x] 6. Le modèle du Chantier : critères, Plan, Suivi, reprise —
      `skills/implementation-tracker/references/{contrat,creation,execution}.md`,
      `skills/implementation-tracker/SKILL.md`, `skills/gabarit/gabarit/suivi/contract.toml`,
      `scripts/check_pipeline.py`, ce Suivi — vérif: V-garde, V-tests, V-md,
      `gabarit contract suivi | grep -F 'modèle'`,
      `gabarit check .claude/implementation/retouches-et-modele-du-chantier.md --filled`
- [x] 7. `plan-reviewer` juge le modèle — `agents/plan-reviewer.md` — vérif: V-garde,
      `grep -c 'MODÈLE' agents/plan-reviewer.md` ≥ 2
- [x] 8. Registre de dette —
      `.claude/implementation/todo/technical-debt/{step-implementer-sans-shadow-skills,ruff-format-absent-des-agents}.md`
      — vérif: `list-dir validate .claude/implementation/todo/technical-debt --filled`,
      `list-dir validate .claude/implementation/todo/technical-debt-ecarte --filled`, V-garde

## État courant

**Prochaine action** : aucune — Chantier clos.

**Vérification** :
`.venv/bin/python scripts/check_pipeline.py && .venv/bin/python -m pytest -q skills/git-smart-commit/scripts/tests scripts/tests skills/gabarit/scripts/tests`

**Dernier audit** : e1d15c7 — RÉSERVES — 2026-10-05

**Notes** : Réserves R1, R3 à R6 de l'audit traitées en Retouche `AE8.1` ; R7 au registre de
dette (`retouche-sans-garde-sur-l-etape-commencee`) ; R2 se résout à l'archivage du brief en
`done/`.

## Passation

**Écrite** : session 1, après AE0

**En cours** : rien.

**À savoir** :

- Point de départ mesuré à AE0 : V-garde rend « Pipeline conforme. », V-tests 211 passés.
- Le contrôle 1 du garde-fou signale une section du contrat que rien ne cite : la section
  « Modèle d'implémentation » (Étape 6) doit recevoir un renvoi, depuis `creation.md`.
- Empreintes : « à chaque reprise » figure aussi dans `suivi/contract.toml`, « à cheval sur deux
  sessions » aussi dans `execution.md` ; ni l'une ni l'autre ne vaut pour la section Frontmatter.
- Avant chaque commit : `git reset -q`, indexer les chemins approuvés, contrôler
  `git diff --staged --name-only`.

## Journal de décisions

- **2026-10-05** — Plan validé par l'utilisateur sur un verdict `plan-reviewer` NON CONFORME
  (critère 5 servi à moitié), constats connus. *Pourquoi* : choix de l'utilisateur. *Rejeté* :
  corriger le Plan et le faire relire.
- **2026-10-05** — Seule correction d'office : la vérification de l'Étape 4, inopérante (Semences
  traitées à l'Étape 5, faux positif de `items.py:232`), bornée aux fichiers de l'Étape.
- **2026-10-05** — Clôture sans nouvel audit après la Retouche `AE8.1`, sur décision de
  l'utilisateur. *Pourquoi* : corrections textuelles des seules réserves de l'audit `e1d15c7`.
  *Rejeté* : audit complet du nouveau diff.
