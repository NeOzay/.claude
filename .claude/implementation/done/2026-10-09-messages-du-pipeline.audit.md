---
slug: messages-du-pipeline
---

## 2026-10-09 — clôture — `617de9f`

**Verdict** : DÉFAVORABLE

Le Brief est présent et validé. Le Suivi fait foi sur un point qu'il borne : le critère `rumdl`
est restreint aux fichiers Markdown du diff (journal, 2026-10-09). Le diff audité est
`git diff master...messages-du-pipeline` : 20 fichiers, +634 −111.

### Vérifications exécutées

- `grep -rn "Voir le diff\|Ma lecture\|Qu'est-ce qui est faux\|Chemins stagés" skills agents`
  (critère 1) → aucune sortie, code 1 : atteint.
- E2 : `! grep -rn -e "Voir le diff" -e "jamais \`-A\`" skills agents` → aucune sortie : passe.
- E2 : `test ! -e projects/-home-debian--claude/memory/index-avant-commit.md` → code 0 : passe.
  `grep index-avant-commit …/MEMORY.md` → code 1 : passe. `MEMORY.md` fait désormais 0 octet.
- E3 : `! grep -rn -e "hemins stagés" -e "chemins à stager" skills agents` → aucune sortie : passe.
  `grep -n "Commit d'Étape proposé" …/etape.md` → ligne 47 : passe.
- E4 : `! grep -rni -e "Ma lecture" -e "Qu'est-ce qui est faux" -e "question par tour" -e
  "explorer → restituer" skills agents` → aucune sortie : passe.
- E4 : `gabarit check .claude/implementation/messages-du-pipeline.brief.md --filled` → « rempli et
  conforme à la semence « brief » » : passe.
- E5 : `grep -n "Gravité réelle" …/audit.md` → lignes 68 et 74 ; `grep -n "la mesure ne se dit
  pas" …/execution.md` → ligne 59 : passe.
- `python3 scripts/check_pipeline.py` → 9 contrôles, tous ✓, dont la nouvelle empreinte
  « appelle une décision » (#messages-à-lutilisateur) ; « Pipeline conforme. », code 0.
- `/home/debian/.claude/.venv/bin/python -m pytest scripts/tests/ -q` → 140 passés, 0 échec.
- `uvx ruff check scripts` → « All checks passed! » ; `uvx ruff format --check scripts` → « 14
  files already formatted ».
- `git diff --name-only --diff-filter=d master...HEAD -- '*.md' | xargs uvx rumdl fmt --check` →
  « No issues found in 17 files » : passe (critère tel que le Suivi le borne).
- `uvx rumdl fmt --check .` (critère tel que le Brief l'écrit) → code 1, « 24/40 issues in 6
  files ». Les six fichiers sont hors du diff. Sur un arbre extrait de `master` (`git archive`), la
  même commande échoue sur les six mêmes fichiers (« 24/45 issues »).
- `gabarit check` du Suivi → conforme à la semence « suivi ».
- `list-dir validate .claude/implementation/todo/road-map` → 7 éléments conformes. L'entrée
  `enchainement-du-chantier` modifiée reste valide.
- `grep` des formules retirées sur tout le dépôt, hors archives : seuls le Brief, le Suivi et
  l'entrée de road-map `messages-du-pipeline` les citent, comme symptôme.

### Conformité à l'intention

- Critère 1 (`grep` des quatre formules) : atteint, vérifié.
- Critère 2 (`staging.md` et `confirmation.md`) : atteint. `staging.md` stage tout, sauf les
  exclusions, par `git add -A`, `git reset -q -- <exclu…>`, puis `git diff --staged --name-only`.
  `confirmation.md` présente le message, le tag et les exclusions, avec « Valider », libellé
  ajusté, et « Autre chose ». Il présente en plus les gestes irréversibles de l'aplatissement :
  c'est une décision du Plan, conforme à l'intention.
- Critère 3 (forme du commit d'Étape) : **non atteint à la lettre.**
  - **R1** — `skills/git-smart-commit/references/etape.md:46-50`. La forme imposée omet « avec le
    pied d'attribution ». Le Brief écrit `- Message : \`dump-sessions: E4 — Skill et
    branchement\`, avec le pied d'attribution.` et le Plan reprend « Message avec pied
    d'attribution ». Le fichier porte `- Message : \`<slug>: E<n> — <intitulé de l'étape>\`.`, et
    aucune entrée du journal ne justifie l'écart. Les commits du Chantier portent bien le pied ;
    c'est la proposition qui ne le dit plus. La seconde moitié du critère est atteinte : `<L>E0`,
    session et Passation demandent l'accord sans titre (lignes 42-43, et `confirmation.md`).
- Critère 4 (ordre d'intent-brief) : atteint, par lecture. Les phases suivent l'ordre demandé :
  - 1 Reconnaissance ;
  - 2 Échanges, deux questions au plus par tour, regroupées par thème ;
  - 3 Écriture, où se choisit le slug, renommable jusqu'à la validation ;
  - 4 Corrections et arbitrages fermés, par `AskUserQuestion` en un seul appel ;
  - 5 Critères et signaux, proposés ;
  - 6 Validation.

  Les phases 3 et 4 font redonner le chemin et les incertitudes. Le contrat du brief et
  `contrat.md`, paragraphe Slug, suivent. La grille de questions est alignée.
- Critère 5 (`execution.md`) : atteint. « Rien, et la mesure ne se dit pas » sous le seuil.
- Critère 6 (`audit.md`, Au retour) : atteint. Restitution en une ligne, puis le tableau
  `# | Réserve | Gravité réelle`, avec un exemple. L'inscription au Suivi se fait sans être
  annoncée, et `cloture.md` y renvoie.
- Critère 7 (règle contre les rappels) : atteint. La section `## Messages à l'utilisateur` de
  `contrat.md` est gardée par une empreinte de `check_pipeline.py`. Les trois skills y renvoient.
- Critère 8 (mémoire `index-avant-commit`) : atteint, vérifié par `test ! -e` et `grep`.
- Critère 9 (`rumdl`) : atteint, dans la forme bornée par le Suivi.
  - **R2** — La commande littérale du Brief échoue toujours. Les six fichiers fautifs préexistent
    sur `master` et l'utilisateur a arbitré au Plan. C'est un constat à connaître, pas un défaut
    du Chantier.
- Hors-périmètre : respecté.
  - Les choix de fin d'Étape ne sont pas définis. Les commits d'Étape et de Retouche gardent les
    deux choix génériques de `confirmation.md`, en attente de `enchainement-du-chantier`
    (journal, 2026-10-09).
  - Le fond de l'audit est intact : ni l'échelle du verdict, ni la relance, ni le gabarit du
    rapport, ni `agents/implementation-auditor.md` (diff vide sur `agents`).
- Signaux de dérive : aucun matérialisé.
  - Chaque type de commit demande encore l'accord : `etape.md` point 4, `confirmation.md`,
    `aplatissement.md` point 3 et Abandon, `hors-chantier.md`.
  - `CLAUDE.md` est inchangé.
  - intent-brief garde ses arbitrages fermés, et ses questions suivent la reconnaissance.
  - Les formules nouvelles — « Commit d'Étape proposé : », la ligne de verdict de l'audit — sont
    celles que le Brief a demandées.
- Symptôme d'origine : retiré du texte des procédures, ce qui est le levier que le Brief
  désignait.
  - **R3** — La disparition du symptôme dans les messages réels est invérifiable ici. Le Plan
    renvoie l'épreuve au Chantier suivant.

### Qualité du code

- **R4** — `skills/gabarit/gabarit/brief/contract.toml:4`. La ligne de commentaire réécrite fait
  111 colonnes, alors que tout le fichier, et le dépôt, se coupe à 100. Aucun linter ne la voit,
  puisque rumdl ne lit pas le TOML.
- **R5** — `skills/git-smart-commit/references/aplatissement.md:79-82` (Abandon). La phrase dit à
  la fois « stagés selon `staging.md` », c'est-à-dire `git add -A` puis exclusions, et que les
  blocs nomment leurs fichiers par des `git add` explicites. Le Plan a voulu garder les deux.
  Mais l'agent ne sait pas laquelle des deux règles s'applique au commit `<slug>: abandon` du
  point 1, qui n'a pas de bloc.
- **R6** — `.claude/implementation/messages-du-pipeline.md:66-67`. Le Suivi porte un fragment
  orphelin, « d'Étape. », sous la Prochaine action. L'Étape 3 y est aussi indentée à 6 espaces au
  lieu de 2. Le Suivi part tel quel en `done/` à la Clôture.
- **R7** — `skills/implementation-tracker/references/contrat.md:236`. Le reformatage `rumdl`
  (MD028) a fusionné deux encadrés « Mode de défaillance » distincts en un seul. C'est sans effet
  sur le sens, et hors de l'objet de l'Étape.

### Dette induite

- **R8** — `.rumdl.toml`. `per-file-ignores` désactive MD041 pour tout `.claude/implementation/*.md`,
  pas seulement pour les briefs et les suivis visés par le journal. Les rapports d'audit et les
  futurs fichiers de ce niveau en sont aussi exemptés. Le coût est faible : une règle de forme
  tue sur des fichiers qui n'en avaient pas besoin.

### Bloquants

- **R1** — La forme du commit d'Étape exigée par le critère 3 n'est pas reproduite : la mention
  « avec le pied d'attribution » manque. La correction tient en une ligne de `etape.md`. Sans
  elle, ou sans une décision datée au journal qui retire cette mention du critère, le critère
  n'est pas atteint. Entre `RÉSERVES` et `DÉFAVORABLE`, le doute penche vers le plus sévère : la
  forme a été dictée mot pour mot par l'utilisateur, et l'écart n'est tracé nulle part.
