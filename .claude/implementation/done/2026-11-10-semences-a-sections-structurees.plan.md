# Plan — semences-a-sections-structurees

Brief : `.claude/implementation/semences-a-sections-structurees.brief.md` (validé).

## Relecture

```
VERDICT : RÉSERVES
CRITÈRES :
C1 (Étape, Dettes écartées, critère/signal mal numéroté, puce de Références font échouer `gabarit check` qui nomme section et puce) → Étapes 2, 3, 4
C2 (`grep -nE 'COCHEE|NUMEROTEE|ECARTEE' …` ne rend rien ; `rapport_audit` lit par `section_values`) → Étapes 5, 6 (commande rejouée en 6 et 9)
C3 (`gabarit new suivi`, `brief`, `shadow-skill` posent au Marqueur de leur forme, `check` conforme) → Étapes 2, 3, 4
C4 (`check --filled` sur les quatre `shadow-skills/*/SKILL.md`, `check` sur `compaction-de-la-prose.brief.md`) → Étape 8 (et 4 pour les Shadow-skills)
C5 (`git diff --stat master -- .claude/implementation/done/` ne rend rien) → Étape 9
C6 (table facultative dont seul un label `text` est réécrit n'est plus tenue au Marqueur, `merge` ne l'omet plus ; cas ajouté à `test_squelette.py` et `test_structure.py`) → Étape 1
C7 (`pytest skills/ scripts/tests/` passe, tests de `rapport_audit` réécrits au format à motifs) → Étapes 5, 6, 9
HORS-PÉRIMÈTRE : RESPECTÉ
DÉRIVE : aucun — à lire avec Q5 (SOURCE et S3) et Q6 (S1 à la Clôture)
INCERTITUDES :
Quelles regex relèvent des motifs (SOURCE, COMMANDE) → tranchée en « Décisions prises au Plan » : les deux restent, comme jugement d'une capture
Motif ou labels pour chaque section (`Objectif et périmètre`) → tranchée en « Les formats déclarés » : des labels, dont trois portent les motifs du Brief
MODÈLE : opus → SOUTENU — un chantier en bonne part de prose (trois Contrats, intent-brief, contrat.md, execution.md) que la vérification ne juge pas ; dans le doute, Opus
QUALITÉ :
Q1 — `## Modèle` dit « sur dix Étapes » ; le plan en compte neuf. Le choix d'Opus n'en dépend pas, mais le chiffre est faux.
Q2 — L'Étape 7 déplace la raison d'un `[!]` vers `**Notes**`, mais `skills/implementation-tracker/references/execution.md:13` (« Passer l'étape en `[!]` + raison ») n'est pas visé : l'Étape ne cite d'`execution.md` que « Quand le périmètre change », et sa vérification `rg 'non abordé|Élargissement'` ne verrait pas ce reste.
Q3 — La vérification de l'Étape 4, `for f in shadow-skills/*/SKILL.md; do gabarit check "$f" --filled; done`, ne rend que le code du dernier fichier : un échec sur l'un des trois premiers passe inaperçu. Même boucle pour C4 à l'Étape 8, renvoyée à « la commande de C4 », que le Brief n'écrit pas comme une commande unique.
Q4 — L'Étape 3 affirme « le Suivi de ce Chantier passe `check` », et les Points d'attention disent que l'Étape 3 vérifie aussi le Brief, mais aucune commande de l'Étape n'exécute ce contrôle (vérif : `pytest test_semences.py` seul). Or ce Suivi est posé à l'ancien Contrat, et `rapport_audit` ne le lira plus sans repli.
Q5 — Le Brief, en « Existant », range `SOURCE` parmi « les regex de format de section ». Le plan le conserve en relisant S3 (« lu ainsi par S3 »), sur une réponse de l'utilisateur. Cette lecture d'un Signal de dérive est à ratifier explicitement, faute de quoi l'audit peut la relever comme S3. C2 n'inclut pas `SOURCE`, ce qui va dans le sens du plan.
Q6 — Les Points d'attention restreignent S1 au diff des Étapes, pour que le déplacement de deux Éléments `technical-debt/` vers `technical-debt-solde/` à la Clôture ne compte pas. S1 dit « le diff touche … un Élément de registre » sans cette restriction : lecture à ratifier par l'utilisateur.
Q7 — L'Étape 6 prévoit de supprimer `puces()` s'il n'a plus d'appelant, mais `puces()` est défini dans `rapport_audit/pose.py` (l. 80), que l'Étape 6 ne nomme pas.
Q8 — Le Brief dit que `modele.py` et `export.py` « nomment aussi ces sections » ; aucune Étape ne dit s'ils restent tels quels. Vérifié : ils ne portent qu'un commentaire et une étiquette « Symptôme », sans doute sans effet, mais le plan ne le tranche pas.
Q9 — Étape 2 : « un brief au format actuel — celui des fixtures » ne dit pas de quelles fixtures il s'agit (`conftest.py` d'implementation-tracker ou autres).
Q10 — Le Contrat proposé pour les Étapes ne dit pas si la capture `verif` est requise ; l'exemple de `format.md` la déclare `required = false`, et l'Étape 9 (« aucun fichier ») en dépend.
```

Corrigés sans arbitrage, défauts de rédaction : Q1 (neuf Étapes), Q2 (`execution.md:13` visé à
l'Étape 7, vérification élargie), Q3 (boucles qui cumulent le code de retour ; commande de C4
écrite à l'Étape 8), Q4 (contrôle du Brief et du Suivi de ce Chantier aux Étapes 2 et 3), Q7
(`pose.py` nommé à l'Étape 6), Q8 (`modele.py` et `export.py` inchangés, dit en « Fichiers
critiques »), Q9 (fixtures nommées), Q10 (`verif` requise, dit sous le tableau du Suivi).

Q5 — Réponse de l'utilisateur (2026-11-08) : S3 ne vise pas `SOURCE`, qui juge une valeur
capturée ; la lecture va au Journal du Suivi à sa création.

Q6 — Réponse de l'utilisateur (2026-11-08) : S1 ne vise que le diff des Étapes ; le solde des deux
dettes relève de la Clôture. La lecture va au Journal du Suivi à sa création.

## Contexte

f100580 a livré `type = "motif"` et `type = "label"`, mais les Semences `brief`, `suivi` et
`shadow-skill` n'en déclarent aucun : le format de leurs sections reste en prose dans les
`description`, et `rapport_audit` le redit dans ses regex (`COCHEE`, `NUMEROTEE`, `ECARTEE`, et
l'analyse ad hoc de `**Symptôme** :`). Une ligne d'Étape mal formée passe donc `gabarit check`.
Ce Chantier déclare ces formats dans les trois Contrats, fait lire `rapport_audit` par
`section_values`, met à niveau les Gabarits vivants et solde la dette
`squelette-ignore-un-label-text-reecrit`.

Rappel du Brief — critères C1 à C7, hors-périmètre (registres `road-map*` / `technical-debt*`,
archives de `done/`, dette `merge-aplatit-les-labels-title`), signaux S1 à S6.

## Décisions prises au Plan (réponses de l'utilisateur, 2026-11-08)

- **Source** : le suffixe `(dit)` / `(dépôt: …)` reste dans la capture de texte. `SOURCE`
  (`pose.py`) reste : il juge une valeur capturée, pas le format d'une ligne — lu ainsi par S3.
  `COMMANDE` reste au même titre : il dit si la capture `verif` est une commande ou de la prose.
- **Axe non abordé** : une puce conforme au motif de sa section — `- **C1** — non abordé`,
  `- **S1** — non abordé`, `- non abordé`, `- **Non abordé** : —`. intent-brief est réécrit.
- **Élargissement du périmètre** : un label facultatif `Élargissements` d'`Objectif et périmètre`,
  motif `{date: date} — {elargissement}`, une puce par élargissement. `execution.md` est réécrit.

## Les formats déclarés

Toutes les sections à motif prennent `fin = "\n"` : une puce Markdown ordinaire, sa suite en
retrait, la forme que `rumdl` donne déjà aux fichiers. Tous les labels sont en `forme = "bold"`.

**Brief** (`skills/gabarit/gabarit/brief/contract.toml`)

| Section | Structure |
|---|---|
| Intention | labels `Symptôme` (1), `But` (2), requis |
| Critères de réussite | motif `**C{n: int}** — {critere}`, `n` min 1, `sequence` |
| Hors-périmètre | motif `{exclusion}` |
| Signaux de dérive | motif `**S{n: int}** — {signal}`, `n` min 1, `sequence` |
| Contraintes connues de l'utilisateur | motif `**{nature}** : {contrainte}` |
| Incertitudes à lever en plan | prose, inchangée (`— aucune` y reste admis) |

**Suivi** (`skills/gabarit/gabarit/suivi/contract.toml`)

| Section | Structure |
|---|---|
| Objectif et périmètre | labels `Symptôme` (1), `But` (2), `Critères de réussite` (3), `Hors-périmètre` (4), `Signaux de dérive` (5), requis, les trois derniers aux motifs du Brief ; `Élargissements` (6), facultatif, motif `{date: date} — {elargissement}` |
| Étapes | motif `[{etat: enum}] {n: int}. {intitule} — {fichiers} — vérif: {verif}`, `etat` ∈ `" "`, `>`, `x`, `!`, `n` min 1, `sequence` |
| État courant | labels `Prochaine action` (1), `Vérification` (2), `Dernier audit` (3), requis ; `Notes` (4), facultatif ; tous en prose |
| Passation | table facultative, labels `Écrite` (1), `En cours` (2), `À savoir` (3), requis, en prose |
| Dettes écartées | motif `R{n: int} — {justificatif} — {date: date}`, `n` min 1 |
| Journal de décisions | motif `**{date: date}** — {decision}` |

`verif` est requise, comme toute capture sans table : chaque Étape porte sa vérification. La
dernière Étape d'un Chantier, sans fichier, écrit `aucun fichier` dans `fichiers`, non dans
`verif`.

La raison d'une Étape `[!]` s'écrit dans `**Notes**` de l'État courant : le motif n'a pas de place
pour elle après `vérif:`, où elle se lirait comme une vérification.

`Dernier audit` reste en prose : il vaut `<sha> — <VERDICT> — <date>` ou `aucun`, et un motif
n'a pas d'alternative.

**Shadow-skill** (`skills/shadow-skill/gabarit/shadow-skill/contract.toml`)

| Section | Structure |
|---|---|
| Instructions | prose, inchangée |
| Références | motif ``[`{chemin}`]({lien}) : {quand}`` |

**Descriptions allégées** : chaque `description` garde le sens de sa section, et ce qui ne se
vérifie pas (source exigée, natures usuelles, « observable et vérifiable ») ; le format d'une ligne
n'y est plus redit. `gabarit contract` rend le TOML brut, motifs compris, et `new` pose le Marqueur
qui porte le motif : l'agent qui remplit voit toujours la forme.

## Modèle

Opus — un tiers du Chantier est de la prose (trois Contrats allégés, intent-brief,
`contrat.md`, `execution.md`), que la vérification ne juge pas, sur neuf Étapes.

## Étapes

1. **Solder la dette du squelette** — `skills/gabarit/scripts/gabarit/structure.py`
   (`_squelette_au_marqueur`), `skills/gabarit/scripts/tests/test_squelette.py`,
   `skills/list-dir/scripts/tests/test_structure.py`, `skills/gabarit/references/format.md` —
   vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_squelette.py skills/list-dir/scripts/tests/test_structure.py`.
   Un label `text` dont le corps rogné diffère de son `text` entame la table ; le saut ne vaut
   plus que pour une `command`, limite nommée dans format.md, « Une table facultative laissée au
   squelette ». Tests : table `Annexe` facultative, `Outil` à `text = "pytest"` réécrit « nox » —
   `--filled` réclame `Source`, `merge` garde la section (C6).
2. **Semence `brief` structurée** — `brief/contract.toml`,
   `skills/gabarit/scripts/tests/test_semences.py` (nouveau) — vérif:
   `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_semences.py && gabarit check .claude/implementation/semences-a-sections-structurees.brief.md --filled`.
   Les tests résolvent la Semence réelle : `new` puis `check` conforme (C3) ; un critère sans
   numéro, un signal hors séquence, une contrainte sans nature font échouer `check` en nommant
   section et puce (C1) ; les sections du `BRIEF` de
   `skills/implementation-tracker/scripts/tests/conftest.py`, sous un front matter complet,
   passent `--filled`.
3. **Semence `suivi` structurée** — `suivi/contract.toml`, `test_semences.py` — vérif:
   `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_semences.py && gabarit check .claude/implementation/semences-a-sections-structurees.md --filled`.
   Étape mal formée, ligne de `Dettes écartées` sans date, entrée de Journal sans date :
   `check` échoue en nommant section et puce (C1) ; `new` puis `check` conforme (C3) ; le Suivi de
   ce Chantier, posé à l'ancien Contrat, passe `--filled` — sinon il se met à niveau dans l'Étape.
4. **Semence `shadow-skill` structurée** — `shadow-skill/contract.toml`, `test_semences.py` —
   vérif: `~/.claude/.venv/bin/python -m pytest skills/gabarit/scripts/tests/test_semences.py`,
   puis `rc=0; for f in shadow-skills/*/SKILL.md; do gabarit check "$f" --filled || rc=1; done; test $rc = 0`.
   Une puce de `Références` sans lien échoue (C1) ; `new` puis `check` conforme (C3).
5. **`pose.py` lit par `section_values`** — `rapport_audit/pose.py`,
   `skills/implementation-tracker/scripts/tests/conftest.py`, `tests/test_pose.py` — vérif:
   `~/.claude/.venv/bin/python -m pytest skills/implementation-tracker/scripts/tests/`.
   Le Contrat s'obtient par `trouver_semence(<estampille>, None)` (`gabarit/commandes.py`) ;
   `revue` lit `Intention`, critères, hors-périmètre et signaux par `section_values`, et
   `verifications` les captures `etat`, `n`, `verif` des Étapes. `NUMEROTEE`, `COCHEE`,
   `_numerotees`, `_symptome` disparaissent ; une section mal formée rend l'échec de
   `section_values`. Les fixtures portent une estampille et des sections conformes.
6. **`dettes.py` lit par `section_values`** — `rapport_audit/dettes.py`, `rapport_audit/pose.py`
   (`puces()`, l. 80), `tests/test_dettes.py` — vérif: idem, puis la commande de C2. `ECARTEE`
   disparaît, et `puces()` s'il n'a plus d'appelant.
7. **La prose du pipeline** — `skills/intent-brief/SKILL.md` (axe non abordé, l. 51, 64, 204),
   `skills/intent-brief/references/grille-questions.md` s'il cite le format,
   `skills/implementation-tracker/references/contrat.md` (« Format d'étape » renvoie à la Semence,
   raison d'un `[!]`), `references/execution.md` (l. 13, « `[!]` + raison » ; « Quand le périmètre
   change ») — vérif:
   `uvx rumdl fmt --check skills/intent-brief skills/implementation-tracker/references`, puis
   `rg -n 'non abordé|Élargissement|\[!\]' skills/intent-brief skills/implementation-tracker/references`
   relu : plus aucune forme hors motif, et la raison d'un `[!]` dite en `**Notes**`.
8. **Mettre à niveau les Gabarits vivants** — `shadow-skills/*/SKILL.md`,
   `.claude/implementation/compaction-de-la-prose.brief.md` — vérif, la commande de C4 :
   `rc=0; for f in shadow-skills/*/SKILL.md; do gabarit check "$f" --filled || rc=1; done; gabarit check .claude/implementation/compaction-de-la-prose.brief.md || rc=1; test $rc = 0`.
9. **Vérification d'ensemble contre la Base** — aucun fichier — vérif: C2, C5, C7, puis
   `uvx ruff check .`, `uvx ruff format --check .`, `uvx --with pytest basedpyright`,
   `uvx rumdl fmt --check .`, sur la branche et sur l'arbre extrait de `master` : aucune erreur
   ajoutée. `git -C ~/.config/nvim status --short` vide (S5).

## Fichiers critiques et réemploi

- `skills/gabarit/scripts/gabarit/structure.py` : `section_values`, `_squelette_au_marqueur`.
- `skills/gabarit/scripts/gabarit/commandes.py` : `trouver_semence`, `check`.
- `skills/gabarit/scripts/gabarit/items.py` : `read_item`, déjà employé par `pose.py`.
- `skills/implementation-tracker/scripts/rapport_audit/{pose,dettes}.py`. `modele.py` et
  `export.py` restent tels quels : ils ne nomment ces sections que dans un commentaire et une
  étiquette de rendu.
- Les trois `contract.toml` ; la syntaxe : `skills/gabarit/references/format.md`,
  « Les sections structurées ».

## Points d'attention pour la relecture

- **S1 et la Clôture** : solder `semences-sans-sections-structurees` et
  `squelette-ignore-un-label-text-reecrit` déplace deux Éléments de `technical-debt/` vers
  `technical-debt-solde/`. C'est la procédure de Clôture (`dette.md`), pas le diff des Étapes ;
  S1 vise une modification d'Élément pendant l'implémentation.
- **Ce Chantier s'audite lui-même au nouveau format** : son Brief et son Suivi, posés à l'ancien
  Contrat, doivent passer `check` après les Étapes 2 et 3 — c'est le cas à la lecture (puces
  `**C<n>** —`, `**<Nature>** :`, labels attendus) ; l'Étape 3 le vérifie.
- **C1 dit « nomme la section et la puce »** : c'est ce que `check` fait déjà (f100580) ; les
  tests de l'Étape 2 à 4 l'assertent sur le message.
