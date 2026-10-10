# Plan — enchainement-du-chantier

Brief : `.claude/implementation/enchainement-du-chantier.brief.md` (validé). Entrée de road-map :
`enchainement-du-chantier`.

## Relecture

Verdict de `plan-reviewer` : **NON CONFORME**, sur C9 seul ; les huit autres critères sont servis,
hors-périmètre respecté, aucun signal déclenché, modèle soutenu.

- **C9** — non servi tel que le Brief l'écrit. *Tranché* : formater les 6 fichiers, Étape E6.
- **Q1** — le motif de C9 citait 13 fichiers ; la commande échoue sur 6. Corrigé.
- **Q2** — la reprise : les écarts bloquent-ils la proposition, ou se signalent-ils sans bloquer
  comme l'écart de modèle aujourd'hui ? *Tranché* : signalés sans bloquer, comme aujourd'hui.
- **Q3** — vérifications d'E2 et d'E4 inopérantes. Corrigées.
- **Q4** — E5 ne dit pas ce que déclenche « Valider le Brief et passer au Plan » face à la Phase 7
  d'intent-brief, « sortie unique » qui renvoie à `/implementation-tracker`. *Tranché* : selon
  l'appel — lancé par le tracker, le Plan commence ; lancé seul, la Phase 7 propose le tracker.
- **Q5** — `contrat.md`, « Modèle d'implémentation », suppose une Passation après la création ;
  avec le choix 2 de `<L>E0`, l'Étape 1 tourne sur le modèle de la session de création.
  *Tranché* : la proposition de `<L>E0` signale l'écart en une ligne, sans bloquer ; `contrat.md`
  s'ajuste, E3.
- **Q6** — la vérification `rumdl` d'ensemble, sans `--diff-filter=d` ni `xargs -r`. Corrigée.

## Contexte

Près de la moitié des messages de l'utilisateur sont procéduraux : « oui », « 1 », « Commit et
continue », « Commit et fait la Passation » puis « 1 ». Le Chantier fait tenir chaque passage obligé
— validation du Brief et du Plan, commit `<L>E0` et Passation, fin d'Étape, reprise — en un seul
tour.

Cadre rappelé du Brief :

- **Critères** : C1 relecture du Plan puis `AskUserQuestion` avant `ExitPlanMode` ; C2 deux choix
  sur `<L>E0` ; C3 trois choix sur une Étape ou une Retouche, plus la Passation au-delà de
  300 000 tokens, plus l'audit de Clôture après la dernière ; C4 `contexte` avant la proposition ;
  C5 une seule exception à « un accord, un commit » ; C6 reprise en un court message ; C7 semence
  `brief` numérotée ; C8 validation du Brief par un message dédié ; C9 `rumdl`.
- **Hors-périmètre** : règle `ask` et commit sans proposition ; forme des messages ; fond de
  l'audit.
- **Incertitudes** : aucune.

## Modèle

**Opus** : le Chantier est fait de prose, que rien ne vérifie au-delà des `grep` des critères.

## Décisions de conception

- **Partage des rôles.** `git-smart-commit` (`etape.md`) énumère les choix qui terminent une
  proposition et committe ; ce qui suit le commit — démarrer l'Étape, écrire la Passation, lancer
  l'audit — revient à `implementation-tracker` (`execution.md`, `creation.md`). Une même règle,
  un seul endroit.
- **Passation après une Étape : deux accords.** C5 borne l'exception au choix « Valider et faire
  la Passation » de `<L>E0`. Après une Étape, « Valider et commencer la Passation » couvre le
  commit d'Étape seulement ; la section `## Passation`, qui porte alors ce que la session a
  appris, se propose à son propre commit. Motif de la différence, tiré du Brief : à `<L>E0`, rien
  n'a commencé et la section ne porte rien à relire.
- **Mesure indisponible** : la proposition le dit et n'ajoute pas le choix de Passation, comme
  aujourd'hui. Mesure sous le seuil : rien ne se dit.
- **Dernière Étape** : le premier choix devient « Valider et lancer l'audit de Clôture », pour un
  commit d'Étape comme pour une Retouche de la dernière Étape ; il déclenche la Phase 5. La SKILL
  ajoute ce déclencheur à `close`.
- **Relecture du Plan** : section `## Relecture` en tête du Plan, qui reprend le bloc de sortie de
  `plan-reviewer` tel quel ; chaque constat tranché par `AskUserQuestion` y reçoit sa réponse. Un
  verdict `CONFORME` sans constat ne pose aucune question. Les défauts de rédaction de `QUALITÉ` se
  corrigent sans arbitrage, comme aujourd'hui, et se notent dans la section.
- **Reprise** : les écarts (branche, modèle, arbre sale, Passation périmée) se signalent dans le
  même message, avant la proposition, sans la bloquer ; l'arbre sale garde sa proposition de
  commit avant de continuer. Ensuite, le message dit
  l'Étape en cours, la prochaine action, les blocages, et demande s'il faut commencer l'Étape X. La
  Passation à jour se lit, elle ne se restitue plus.
- **C9** : `uvx rumdl fmt --check .` sort aujourd'hui en code 1 sur 6 fichiers hors Chantier, tous
  sous `.claude/implementation/` : 5 entrées de registre et `lexique-local-tronque.audit.md`. Ils
  se formatent en E6, changement mécanique.
- **Modèle au choix 2 de `<L>E0`** : la proposition signale en une ligne l'écart entre le modèle
  de la session et le champ `modèle`, sans bloquer.
- **Validation du Brief selon l'appel** : lancé par `implementation-tracker` à la création, le
  Plan suit la validation ; lancé seul, la Phase 7 propose `/implementation-tracker`.

## Étapes

### E1 — Choix de fin de commit, côté git-smart-commit

- `skills/git-smart-commit/references/etape.md`, point 4 :
  - `<L>E0` : accord sans titre, deux choix — 1. Valider et faire la Passation ; 2. Valider et
    passer à l'Étape suivante ;
  - Étape et Retouche : la forme actuelle, puis trois choix — 1. Valider et passer à l'Étape
    suivante ; 2. Valider et attendre ; 3. Autre chose. Un quatrième, « Valider et commencer la
    Passation », quand l'appelant le demande ; après la dernière Étape, le choix 1 devient
    « Valider et lancer l'audit de Clôture » ;
  - ce qui suit le commit revient à l'appelant.
- `skills/git-smart-commit/references/confirmation.md` : les deux réponses génériques restent pour
  les autres commits, avec un renvoi aux choix d'`etape.md` ; « Ce qui compte comme accord » gagne
  l'exception du choix « Valider et faire la Passation », avec son motif.

Vérification :

```bash
grep -n "Valider et faire la Passation\|Valider et attendre\|Valider et commencer la Passation\|Valider et lancer l'audit de Clôture" skills/git-smart-commit/references/etape.md
grep -n "Valider et faire la Passation" skills/git-smart-commit/references/confirmation.md
python3 scripts/check_pipeline.py
```

### E2 — Fin d'Étape et Passation, côté tracker

- `skills/implementation-tracker/references/execution.md` :
  - tableau des déclencheurs : Étape terminée → cocher, `contexte`, proposer le commit avec ses
    choix ; même ordre pour la Retouche ;
  - section « Passation » réécrite : le choix 1 de `<L>E0` ; le choix ajouté au-delà de 300 000
    tokens, sans quoi rien ne se propose, l'utilisateur tenant le plafond de 400 000 ;
  - ce que fait chaque choix : passer l'Étape suivante en `[>]` et la commencer ; rendre la main ;
    écrire la Passation puis proposer son commit (deux accords, voir Décisions) ; lancer la Phase 5.
- `skills/implementation-tracker/SKILL.md`, Phase 5 : le choix « Valider et lancer l'audit de
  Clôture » déclenche la Clôture.

Vérification :

```bash
awk '/Étape terminée/ { exit !(index($0,"contexte") < index($0,"propos")) }' skills/implementation-tracker/references/execution.md
grep -n "Valider et lancer l'audit de Clôture" skills/implementation-tracker/SKILL.md
python3 scripts/check_pipeline.py
```

### E3 — Création : relecture du Plan, `<L>E0` et Passation

- `skills/implementation-tracker/references/creation.md` :
  - point 3 : `plan-reviewer` lancé une fois, section `## Relecture` en tête du Plan,
    `AskUserQuestion` sur ce qui reste à trancher, Plan corrigé selon les réponses, `ExitPlanMode`.
    La règle « ne jamais corriger d'office » reste : seule une réponse corrige le Plan ;
  - points 9 et 10 fusionnés : commit `<L>E0` avec ses deux choix ; choix 1 → Passation écrite et
    commitée dans la foulée, puis `/clear`, `/model <modèle>` et `/implementation-tracker @<suivi>`
    ; choix 2 → l'Étape 1 commence, l'écart de modèle signalé s'il y en a un.
- `skills/implementation-tracker/references/contrat.md`, « Modèle d'implémentation » : la session
  vierge et son `/model` ne valent que si la Passation suit la création ; au choix 2, l'écart se
  signale à la proposition de `<L>E0`. L'empreinte « Au moindre doute, Opus » reste en place.

Vérification :

```bash
grep -n "## Relecture\|AskUserQuestion\|Valider et faire la Passation" skills/implementation-tracker/references/creation.md
python3 scripts/check_pipeline.py
```

### E4 — Reprise en un court message

- `skills/implementation-tracker/SKILL.md`, Phase 3 : la restitution se réduit à l'Étape en
  cours, la prochaine action et les blocages, puis la proposition de commencer l'Étape X ; les
  écarts se signalent dans le même message, avant la proposition, sans la bloquer.

Vérification :

```bash
! grep -n "commandes de vérification à rejouer" skills/implementation-tracker/SKILL.md
grep -n "commencer l'Étape" skills/implementation-tracker/SKILL.md
python3 scripts/check_pipeline.py
```

### E5 — Brief : numérotation et validation

- `skills/gabarit/gabarit/brief/contract.toml` : sections « Critères de réussite » et « Signaux de
  dérive » — une puce par critère, `- **C1** — …` ; par signal, `- **S1** — …`.
- `skills/intent-brief/SKILL.md`, Phase 6 : point 2 nouveau, la proposition dédiée — chemin, rien
  ne sera plus ajouté, deux choix « Valider le Brief et passer au Plan », « Autre chose » ; seule
  une réponse à cette proposition vaut validation, avec son motif ; une correction renvoie à la
  Phase 4. La Phase 7 distingue l'appel : lancé par le tracker, le Plan commence ; lancé seul, elle
  propose `/implementation-tracker`.

Vérification :

```bash
gabarit contract brief | grep -n "C1\|S1"
gabarit check .claude/implementation/enchainement-du-chantier.brief.md --filled
grep -n "Valider le Brief et passer au Plan" skills/intent-brief/SKILL.md
```

### E6 — Formatage des six fichiers hors Chantier

- `uvx rumdl fmt` sur les 6 fichiers que `uvx rumdl fmt --check .` refuse, sous
  `.claude/implementation/` ; aucun autre changement.

Vérification :

```bash
uvx rumdl fmt --check .
```

## Vérification d'ensemble

```bash
python3 scripts/check_pipeline.py
~/.claude/.venv/bin/python -m pytest scripts/tests/ -q
uvx rumdl fmt --check .
! git diff master --stat -- settings.json CLAUDE.md agents/implementation-auditor.md | grep .
```
