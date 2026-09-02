---
slug: recopies-hors-contrat
titre: Une règle, un endroit — pour les règles que le garde-fou ne protège pas
branche: recopies-hors-contrat
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-09-02-recopies-hors-contrat.plan.md
brief: .claude/implementation/done/2026-09-02-recopies-hors-contrat.brief.md
audit: .claude/implementation/done/2026-09-02-recopies-hors-contrat.audit.md
créé: 2026-09-02
maj: 2026-09-02
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : une même règle écrite cinq fois a fini par donner deux réponses contradictoires —
la preuve d'un `doublon` est l'`id` de l'entrée conservée selon `dette.md` et `gabarit-rapport.md`,
son intitulé selon `templates/review.md` et selon la règle de preuve en tête de `categories.md`,
qui se contredit lui-même à cinquante lignes d'écart (l. 17 et l. 71). Le gabarit de fiche
`templates/review.md` porte la mauvaise version — non pas recopiée dans les fiches (`derive` ignore
tout ce qui précède le premier `##`), mais lue par l'agent qui y cherche quoi écrire sous chaque
marqueur.

**But** : trancher cette contradiction, puis résorber les recopies qui l'ont produite, de sorte que
chaque règle reste définie à un seul endroit — y compris quand cet endroit n'est pas `contrat.md`.

**Critères de réussite** — le chantier porte sur les recopies nommées, pas sur la détection des
futures :

- la contradiction `doublon` est tranchée en faveur de l'`id`, et les deux écritures fautives
  (`categories.md` règle de preuve, `templates/review.md` « Verdict ») disent `id`
- chacune des recopies du tableau du brief est résorbée : une seule écriture définit la règle, les
  autres y renvoient — sans effacer la prose qui porte du jugement
- chaque autorité désignée est vérifiable par lecture : on peut pointer le fichier et la section qui
  définit la règle, et aucune autre ne la redéfinit
- `scripts/check_pipeline.py` reste vert

Explicitement hors critère : qu'une recopie *future* soit détectée automatiquement.

**Hors-périmètre** :

- le skill manuel de re-semis (chantier dédié) ; ici la semence et sa copie se corrigent à la main
  une dernière fois, `diff` à l'appui
- les `description = ""` des sections des quatre contrats : dette déjà ouverte,
  `sections-declarees-sans-description-redigee`
- les deux recopies qui relèvent du jugement et non de la définition — « le plus mal placé pour
  affirmer qu'il l'a fait » et « bonne solution au mauvais problème »
- la duplication des trois `agents/*.md`, voulue et vérifiée par le contrôle 4 du garde-fou
- les docstrings de `listdir/commands/*.py` et des tests, qui énoncent les mêmes règles pour le code

**Signaux de dérive** :

- *arrêt sec* — une prose qui portait du **jugement** est remplacée par un renvoi
- *arrêt sec* — une ligne de mécanisme (empreintes, marquage) est écrite avant que les recopies
  soient soldées
- *arrêt pour arbitrage* — un fichier absent du tableau des recopies est touché ; recevable si la
  correction est pertinente, mais c'est l'utilisateur qui le dit
- *arrêt pour arbitrage* — une correction de rédaction s'ajoute sans résorber de recopie

### Élargissements de périmètre

- **2026-09-02** — l'autorité de « commit mixte / détection de renommage » bascule du brief
  (`dette.md` « Solder ») vers `contrat-liste.md` « L'API Python », où la règle était déjà écrite en
  meilleure forme. `dette.md` devient un renvoi. Admis par arbitrage à l'étape 3.

- **2026-09-02** — les deux redites internes de `dette.md` sur l'`id` (sections « Corriger une
  entrée » et « Marqueur d'une entrée relue ») entrent au périmètre : même règle que l'étape 2,
  découverte en la traitant, admise par arbitrage. Traitées à l'étape 2.

- **2026-09-02** — `skills/list-dir/references/contrat-liste.md:572` entre au périmètre : 7ᵉ écriture
  de la règle « commit mixte / détection de renommage », découverte en planification, admise par
  arbitrage. Traitée à l'étape 3.

## Étapes

- [x] 1. Contradiction `doublon` → `id` — `categories.md`, `templates/review.md` + sa copie amorcée — vérif: `grep -rn "intitulé de l'entrée conservée" skills/ .claude/implementation/todo/`
- [x] 2. Recopie « `id` = seule identité » → renvoi — `dette.md` — vérif: `grep -rn --include='*.md' "ne change jamais" skills/` → 0
- [x] 3. Recopie « commit mixte / renommage » → renvois — `cloture.md`, `debt-review/SKILL.md`, `contrat-liste.md`, `dette.md` — vérif: `grep -rn --include='*.md' "détection de renommage\|renommage pur" skills/` → 1 (`contrat-liste.md:445`)
- [x] 4. Recopie « substitution qui avale l'échec » → renvoi — `debt-review/SKILL.md` — vérif: `grep -rn --include='*.md' "avale" skills/` → 1
- [x] 5. Recopie « sections de la fiche de revue » → renvoi — `gabarit-rapport.md` — vérif: `grep -c "^- \*\*Vérifié par\*\*\|^- \*\*Verdict\*\*" skills/debt-review/references/gabarit-rapport.md` → 0
- [x] 6. Comptage `merge` : autorité à `debt-review/SKILL.md` Ét. 3 — `gabarit-rapport.md` — vérif: `grep -rn --include='*.md' "16 — 16" skills/` → 1
- [x] 7. Recopie « 3 modes de défaillance » → renvois — `implementation-tracker/SKILL.md` — vérif: `grep -rn --include='*.md' "atomique" skills/` → 1
- [x] 8. Consigner le renoncement au mécanisme — registre de dette — vérif: `list-dir validate .claude/implementation/todo/technical-debt --filled`

## État courant

**Prochaine action** : toutes les étapes sont faites — clôture (audit par
`implementation-auditor`, puis aplatissement sur `master`).
**Vérification** : `python3 scripts/check_pipeline.py` (8 contrôles verts)
**Dernier audit** : `a9189db` — RÉSERVES — 2026-09-02. Les deux réserves de fond sont corrigées
depuis (voir journal) ; les trois réserves de forme sont laissées en l'état.
**Notes** : le contrôle 8 du garde-fou ne capte que les renvois en lien markdown `](../…#ancre)` —
écrire les renvois sous cette forme est ce qui les rend vérifiables.

## Journal de décisions

- **2026-09-02** — l'autorité de l'`id` est `contrat-liste.md` « Un élément », pas `dette.md`.
  *Pourquoi* : la règle vaut pour tout élément de liste, et le contrat de `list-dir` l'énonce déjà
  (« C'est la seule identité »). *Rejeté* : laisser `dette.md` faire autorité, ce qui obligerait les
  autres listes à renvoyer vers le registre de dette.
- **2026-09-02** — la référence à un élément se fait par l'`id`, jamais par l'intitulé.
  *Pourquoi* : l'intitulé se réécrit (catégorie `aggravee`), l'`id` non — une preuve citant un
  intitulé devient non résoluble sans que rien ne le signale.
- **2026-09-02** — autorité du comptage `merge` : `debt-review/SKILL.md` Étape 3.
  *Pourquoi* : le geste s'y fait, et `gabarit-rapport.md` y renvoyait déjà. *Rejeté* :
  `gabarit-rapport.md`, qui aurait forcé le SKILL à renvoyer pour sa propre commande.
- **2026-09-02** — autorité de « preuve d'un `doublon` = l'`id` » : `categories.md` section
  « Doublon ». *Pourquoi* : la règle de preuve en tête du même fichier la redisait, c'est elle qui
  avait divergé. *Rejeté* : `dette.md` « Écarter », qui régit la ligne `Établi par` du registre —
  un autre artefact que le verdict de fiche.
- **2026-09-02** — ligne de partage retenue pour toutes les corrections : le fichier d'autorité
  porte le **motif**, le skill garde la **prescription**. *Pourquoi* : un skill privé de sa consigne
  opératoire obligerait à suivre un renvoi en cours d'exécution. *Rejeté* : remplacer la consigne
  elle-même par un renvoi.
- **2026-09-02** — autorité de « commit mixte » : `contrat-liste.md` « L'API Python », pas
  `dette.md` « Solder » comme le prévoyait le brief. *Pourquoi* : la règle porte sur `move` et
  `migrate`, commandes de `list-dir` ; l'inverse aurait fait renvoyer le skill générique vers un
  skill qui le consomme. *Rejeté* : garder `dette.md`, qui créait cette dépendance inversée.
- **2026-09-02** — une redite intra-fichier renvoie à la section d'autorité du même fichier, qui
  seule renvoie vers l'autre skill. *Pourquoi* : trois liens sortants pour une règle. *Rejeté* :
  autant de renvois directs que de redites.
- **2026-09-02** — le mécanisme anti-recopie reste hors chantier, renoncement écrit au registre.
  *Pourquoi* : hors critère de réussite, et son périmètre (empreintes libres ou sections marquées)
  n'est pas tranché. *Rejeté* : l'étendre maintenant, qui aurait doublé le chantier.
