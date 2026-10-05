# Plan — retouches-et-modele-du-chantier

Brief : `.claude/implementation/retouches-et-modele-du-chantier.brief.md` (validé).

## Context

Deux manques d'implementation-tracker.

1. **Retouches.** Après un commit d'Étape, les reprises de l'Étape N partent en commit de session
   nommé d'après l'Étape suivante (claude-translator, `dad40e0`, `5a3b15d`) : rien ne dit quelle
   Étape est retouchée, et aucun tag ne la borne. On cadre la Retouche : tout commit pris après le
   tag `<L>E<N>` et avant que l'Étape N+1 ne commence se nomme `<slug>: E<N>.<k> — <objet>` et
   reçoit le tag `<L>E<N>.<k>`.
2. **Modèle.** La Passation coupe le Chantier en sessions ; celle qui suit le commit `<L>E0`
   démarre à vide, et l'utilisateur y fait `/model`. Le Plan choisit donc le modèle (Sonnet ou
   Opus) de toute l'implémentation, `plan-reviewer` juge ce choix, le Suivi le porte, et la reprise
   signale un écart. La Passation rendant le Subagent inutile pour le contexte, `step-implementer`
   et toute la délégation (valeur `délégué`, champ `execution`) disparaissent.

## Modèle

**Opus.** Le travail est surtout de la prose de skill (contrat du pipeline, références,
Semences, agent), plus difficile à contrôler que du code ; 8 Étapes, sous le seuil de 12 ; les
incertitudes du brief sont toutes tranchées ci-dessous.

## Incertitudes du brief, tranchées

- **Commit de Passation après un commit d'Étape** : il garde sa forme
  `<slug>: passation — session N, après <tag>`, hors numérotation des Retouches ; `<tag>` est le
  dernier tag posé, d'Étape ou de Retouche (Étapes 2 et 3).
- **Seuil du nombre d'Étapes** : plus de 12 Étapes fait pencher vers Opus (arbitrage de
  l'utilisateur ; Étape 6).
- **« Retouche » au Lexique global** : accordé par l'utilisateur, avec la ligne « Retouche |
  Modification d'une Étape livrée, faite avant que l'Étape suivante ne commence, commitée et taguée
  `<L>E<N>.<k>`. | [Commit rapide de chantier](skills/git-smart-commit/references/etape.md) » (Étape
  2). Le lien d'Étape passe à `#format-détape`, accordé aussi (Étape 4).

Autres arbitrages de l'utilisateur pendant le plan : message de Retouche avec objet fourni par
l'appelant ; `ruff-format-absent-des-agents` corrigée sur place (elle reste vraie pour
`implementation-auditor` et `plan-reviewer`), `step-implementer-sans-shadow-skills` écartée.

## Vérifications communes

- **V-garde** : `.venv/bin/python scripts/check_pipeline.py` rend « Pipeline conforme. »
- **V-tests** :
  `.venv/bin/python -m pytest -q skills/git-smart-commit/scripts/tests scripts/tests skills/gabarit/scripts/tests`
- **V-md** : `uvx rumdl fmt --check <fichiers .md de l'Étape>`

## Étapes

### Étape 1 — Tags de Retouche dans `commit-chantier`

Fichiers : `skills/git-smart-commit/scripts/commit_chantier.py`,
`skills/git-smart-commit/scripts/tests/test_commit_chantier.py`.

- `TAG_ETAPE` (`commit_chantier.py:70`) reconnaît `<L>E<n>` et `<L>E<n>.<k>`.
- Le tri des tags de la clôture (`key=lambda t: int(t[2:])`, dans `preparer`) planterait sur
  `AE1.1` : clé numérique `(n, k)`, `k = 0` pour un tag d'Étape.
- Sous-commande `retouche <L> <n>` : rend le prochain tag `<L>E<n>.<k>` (k = plus grand k
  existant + 1, ou 1). Refuse, sortie 1, si `<L>E<n>` n'existe pas, ou si `<L>E<n+1>` existe
  (l'Étape suivante est livrée : ce n'est plus une Retouche de n). Ne lit pas le Suivi, ne charge
  aucune bibliothèque, comme `lettre`.
- Docstring de tête : trois sous-commandes.
- Tests : la clôture supprime `AE1.1` et `AE1.2` et pas les tags d'une autre lettre ; tri de
  `AE1.10` après `AE1.2` ; `retouche` rend `AE1.1` puis `AE1.2` ; les deux refus.

Vérif : V-tests, `uvx ruff format --check skills/git-smart-commit/scripts`,
`uvx ruff check skills/git-smart-commit/scripts`,
`uvx --with pytest basedpyright skills/git-smart-commit/scripts`.

### Étape 2 — Cas « Retouche » du commit rapide de chantier

Fichiers : `skills/git-smart-commit/references/etape.md`,
`skills/git-smart-commit/references/tags-etape.md`,
`skills/git-smart-commit/references/aplatissement.md`, `LEXIQUE.md`.

- `etape.md` : un cinquième cas, **Retouche** — quand : un commit pris après le tag `<L>E<n>` et
  avant que l'Étape n+1 passe en `[>]` ; message `<slug>: E<n>.<k> — <objet>`, l'objet fourni par
  l'appelant en quelques mots ; tag `<L>E<n>.<k>`, rendu par `commit-chantier retouche <L> <n>`.
  Le cas **Session** ne vaut plus que pendant une Étape `[>]`. Le cas **Passation** : « après
  `<tag>` », le dernier tag posé. Procédure point 5 : poser aussi le tag de Retouche.
- `tags-etape.md` : tableau des tags (ligne `<L>E<n>.<k>`) ; plages — `AE2..AE3` contient
  l'Étape 3 et les Retouches de l'Étape 2 ; l'Étape 3 seule part du dernier tag de l'Étape 2
  (`AE2.<dernier k>..AE3`, sinon `AE2..AE3`) ; `AE2..AE2.<dernier k>` = les Retouches de l'Étape 2 ;
  la suppression couvre les deux formes.
- `aplatissement.md:99` : le glob `'<L>E[0-9]*'` couvre déjà `AE1.1` ; le dire en commentaire.
- `LEXIQUE.md` : ligne « Retouche », telle qu'accordée (ci-dessus), après « Étape ».

Vérif : V-garde, V-md, `lexique liste | grep -F Retouche`,
`grep -c 'E<n>.<k>' skills/git-smart-commit/references/etape.md` ≥ 1.

### Étape 3 — La Retouche dans implementation-tracker

Fichiers : `skills/implementation-tracker/references/execution.md`,
`skills/implementation-tracker/SKILL.md`, `skills/implementation-tracker/references/contrat.md`,
`skills/gabarit/gabarit/suivi/contract.toml`.

- `execution.md`, table des déclencheurs : « Étape terminée » coche `[x]` **sans** passer la
  suivante en `[>]` ; nouvelle ligne « Travail d'une Étape commencé » → `[>]` ; nouvelle ligne
  « Modification après le commit de l'Étape N, N+1 non commencée » → Retouche : proposer le commit
  de Retouche (type 2), puis mesurer le contexte. Section **Passation** : proposée après un commit
  d'Étape ou de Retouche. Le Suivi ne trace pas les Retouches ; une décision prise en Retouche va
  au journal comme toute autre.
- `SKILL.md`, Phase 3 : arbre modifié sans Étape `[>]` → proposer un commit de Retouche, non de
  session.
- `contrat.md`, Format d'étape : `[>]` se pose quand le travail de l'Étape commence.
- `suivi/contract.toml`, section Passation : `**Écrite** :` `session <N>, après <tag>`, le dernier
  tag posé, d'Étape ou de Retouche.

Vérif : V-garde, V-tests, V-md, `gabarit contract suivi | grep -F 'dernier tag'`.

### Étape 4 — Retirer `step-implementer` et la délégation du tracker

Fichiers : `agents/step-implementer.md` (supprimé),
`skills/implementation-tracker/references/execution.md`,
`skills/implementation-tracker/references/creation.md`,
`skills/implementation-tracker/references/contrat.md`, `scripts/check_pipeline.py`,
`shadow-skills/skill-convention/references/prose.md`, `LEXIQUE.md`.

- `execution.md` : section « Délégation d'étape », ligne `[>]`/délégation de la table, et la phrase
  « Propre à ce skill : pour une étape déléguée… » retirées.
- `creation.md` : point 1 (`execution = "direct"` imposé), point 3 (« `step-implementer` va y lire »
  → le plan porte le contenu des Étapes que la session lira), point 7 (« `brief` et `execution` »).
- `contrat.md` : en-tête (« deux sous-agents », « Les trois agents… `agents/step-implementer.md`
  ») ; Frontmatter, puce `execution` retirée ; section renommée **Format d'étape**, puces et mode de
  défaillance de la délégation retirés, « un seul tour » gardé ; mode de défaillance d'« Autorité et
  divergence » sans l'exécutant ; « Contrat des sous-agents » : « Vaut pour » les deux agents
  restants, mode de défaillance du travail partiel en `ÉCART` retiré.
- `check_pipeline.py` : en-tête (`step-implementer`) ; `EMPREINTES` — clé `format-détape`, et une
  nouvelle empreinte pour `frontmatter`, « Une valeur absente vaut » disparaissant avec `execution`
  (une phrase du corps de la section, présente une seule fois dans `skills/`).
- `prose.md:199` : « Pratiqué dans » cite `implementation-auditor.md`.
- `LEXIQUE.md` : lien d'Étape vers `#format-détape`.

Vérif : V-garde, V-tests, V-md, `test ! -e agents/step-implementer.md`,
`git grep -n -e step-implementer -e délégu -e délégab -- skills/implementation-tracker scripts/check_pipeline.py shadow-skills LEXIQUE.md agents`
vide.

### Étape 5 — Retirer `execution` des Semences et d'intent-brief

Fichiers : `skills/gabarit/gabarit/brief/contract.toml`,
`skills/gabarit/gabarit/suivi/contract.toml`, `skills/intent-brief/SKILL.md`.

- Champ `execution` retiré des deux Semences.
- `intent-brief/SKILL.md`, Phase 5 : point 1 (« Trancher la délégabilité ») retiré, la liste
  renumérotée.

Vérif : V-tests, V-garde, `gabarit contract brief | grep -c execution` → 0,
`gabarit contract suivi | grep -c execution` → 0,
`gabarit check .claude/implementation/retouches-et-modele-du-chantier.md --filled` (le Suivi de ce
Chantier, mis en conformité au même commit).

### Étape 6 — Le modèle du Chantier : critères, Plan, Suivi, reprise

Fichiers : `skills/implementation-tracker/references/contrat.md`,
`skills/implementation-tracker/references/creation.md`,
`skills/implementation-tracker/references/execution.md`, `skills/implementation-tracker/SKILL.md`,
`skills/gabarit/gabarit/suivi/contract.toml`, `scripts/check_pipeline.py`.

- `contrat.md`, nouvelle section **Modèle d'implémentation** (définie ici seulement) : un modèle
  pour tout le Chantier, choisi au Plan ; Sonnet pour un travail bien délimité, Opus pour un
  travail complexe et mal délimité ; ce qui le dit — la vérification (le code se contrôle bien
  plus facilement que la prose), les incertitudes du brief (Sonnet seulement si le Plan les
  tranche toutes), le nombre d'Étapes (plus de 12 : Opus) ; au moindre doute, Opus. Mode de
  défaillance : un Chantier de prose mené par Sonnet se paie en Retouches.
- `check_pipeline.py` : empreinte de la nouvelle section dans `EMPREINTES`.
- `suivi/contract.toml` : champ `"modèle"`, enum `sonnet` / `opus`, requis, « repris du Plan ».
- `creation.md` : point 2 — le Plan porte une section `## Modèle`, le choix et sa justification en
  une phrase, avec renvoi au contrat ; point 7 — `modèle` repris du Plan ; point 10 — la Passation
  après `<L>E0` dit à l'utilisateur de faire `/model <modèle>` dans la session vierge, avant
  `/implementation-tracker @<suivi>`. Rien ne change le modèle à sa place.
- `SKILL.md`, Phase 3 : comparer le modèle de la session, que le harness donne, au champ
  `modèle` ; un écart se signale, comme pour la branche, sans bloquer ni rien changer.
- `execution.md`, Passation point 3 : inchangé hors création (`/clear` garde le modèle).
- Le Suivi de ce Chantier reçoit `modèle = "opus"` au même commit : posé avant cette Étape, il ne
  pouvait pas porter un champ que sa Semence ne déclarait pas encore.

Vérif : V-garde, V-tests, V-md, `gabarit contract suivi | grep -F 'modèle'`,
`gabarit check .claude/implementation/retouches-et-modele-du-chantier.md --filled`.

### Étape 7 — `plan-reviewer` juge le modèle

Fichier : `agents/plan-reviewer.md`.

- Axe 2 : le Plan nomme-t-il un modèle et sa justification ? Les critères y sont recopiés en dur
  (agent isolé, contrôle 4 du garde-fou), sans renvoi au contrat.
- Rapport : ligne `MODÈLE : <sonnet|opus> → SOUTENU | NON SOUTENU — <critère en cause>` ; un modèle
  absent, ou que les critères ne soutiennent pas, vaut au moins `RÉSERVES`.
- `creation.md` ne change pas : sa table de verdicts couvre déjà `RÉSERVES`.

Vérif : V-garde (contrôle 4 : aucun renvoi au contrat), `grep -c 'MODÈLE' agents/plan-reviewer.md` ≥
2.

### Étape 8 — Registre de dette

Fichiers : `.claude/implementation/todo/technical-debt/step-implementer-sans-shadow-skills.md`
(déplacé vers `technical-debt-ecarte/`),
`.claude/implementation/todo/technical-debt/ruff-format-absent-des-agents.md`.

- `step-implementer-sans-shadow-skills` : `list-dir move` vers `technical-debt-ecarte/`, commit de
  session, puis sa section de mise à l'écart — motif **non pertinent**, établi par
  `test -e agents/step-implementer.md; echo $?` → `1` ([Écarter](dette.md#écarter)). Le
  déplacement et le motif ne partagent pas un commit.
- `ruff-format-absent-des-agents` : corrigée sur place
  ([Corriger une entrée](dette.md#corriger-une-entrée)) — Constat et Pour solder ne citent plus que
  les deux agents restants, preuve `grep -c 'ruff format' agents/*.md` relancée et citée ; `date` et
  `id` inchangés.

Vérif : `list-dir validate .claude/implementation/todo/technical-debt --filled`,
`list-dir validate .claude/implementation/todo/technical-debt-ecarte --filled`, V-garde.

## Vérification d'ensemble

V-garde, V-tests, puis les critères du brief :
`git grep -n -e step-implementer -e délégu -e execution -- ':!.claude/implementation/done' ':!.claude/implementation/todo' ':!.claude/plans'`
ne rend que ce qui ne parle pas du mécanisme supprimé ; `gabarit contract suivi` déclare `modèle` et
ni `suivi` ni `brief` ne déclarent `execution` ; ruff et basedpyright sur
`skills/git-smart-commit/scripts`.
