---
slug: recopies-hors-contrat
titre: Une règle, un endroit — pour les règles que le garde-fou ne protège pas
statut: validé
execution: direct
créé: 2026-09-01
---

## Intention

**Symptôme** : une même règle écrite cinq fois a fini par donner deux réponses
contradictoires — la preuve d'un `doublon` est l'`id` de l'entrée conservée selon
`dette.md` et `gabarit-rapport.md`, son intitulé selon `templates/review.md` et selon la
règle de preuve en tête de `categories.md`, qui se contredit lui-même à cinquante lignes d'écart (l. 17 et l. 71).
Le gabarit de fiche `templates/review.md` porte la mauvaise version — non pas recopiée
dans les fiches (`derive` ignore tout ce qui précède le premier `##`), mais lue par
l'agent qui y cherche quoi écrire sous chaque marqueur.

**But** : trancher cette contradiction, puis résorber les recopies qui l'ont produite, de
sorte que chaque règle reste définie à un seul endroit — y compris quand cet endroit n'est
pas `contrat.md`.

## Critères de réussite

Le chantier porte sur **les recopies nommées**, pas sur la détection des futures (dit) :

- la contradiction `doublon` est tranchée en faveur de l'`id`, et les deux écritures fautives
  (`categories.md` règle de preuve, `templates/review.md` « Verdict ») disent `id`
- chacune des six recopies du tableau ci-dessous est résorbée : une seule écriture définit la
  règle, les autres y renvoient — sans effacer la prose qui porte du jugement
- chaque autorité désignée est vérifiable par lecture : on peut pointer le fichier et la section
  qui définit la règle, et aucune autre ne la redéfinit
- `scripts/check_pipeline.py` reste vert

**Explicitement hors critère** : qu'une recopie *future* soit détectée automatiquement. Le
mécanisme (cf. incertitudes) reste possible, mais le chantier est livrable sans lui — auquel cas
le renoncement s'écrit et se motive.

## Hors-périmètre

- le **skill manuel de re-semis**, qui propagerait une amélioration de semence aux listes déjà
  amorcées : chantier dédié. Ici, la semence et sa copie se corrigent à la main une dernière
  fois, `diff` à l'appui — ce chantier sert de dernière démonstration du coût (dit)
- les `description = ""` des sections des quatre contrats : dette déjà ouverte,
  `sections-declarees-sans-description-redigee` (dit)
- les deux recopies qui relèvent du jugement et non de la définition — « le plus mal placé
  pour affirmer qu'il l'a fait » et « bonne solution au mauvais problème » : couvertes par
  l'arbitrage préservé (dit)
- la duplication des trois `agents/*.md`, voulue et déjà vérifiée par le contrôle 4 du
  garde-fou (dépôt: `scripts/check_pipeline.py`, `check_agents`)

## Signaux de dérive

**Arrêt sec** — le chantier s'arrête et on en reparle (dit) :

- une prose qui portait du **jugement** est remplacée par un renvoi. C'est l'arbitrage de
  `renvoi-contrat-des-categories`, rejeté d'emblée : un renvoi ne remplace pas un jugement
- une ligne de mécanisme (empreintes, marquage) est écrite **avant** que les six recopies du
  tableau soient soldées. Le mécanisme est hors critère : le construire d'abord, c'est prendre
  le chantier à l'envers

**Arrêt pour arbitrage** — signaler et demander, ne jamais corriger d'office (dit) :

- un fichier absent du tableau des recopies est touché — `contract.toml`, fiches déjà dérivées,
  `agents/*.md`. Recevable **si la correction est pertinente**, mais c'est l'utilisateur qui
  le dit
- une correction de rédaction s'ajoute « pendant qu'on y est », sans résorber de recopie. Même
  règle : recevable si pertinente, jamais décidée seule

C'est cette nuance qui impose `execution: direct` : une dérive qui se soumet au lieu de
s'arrêter suppose un interlocuteur, qu'un sous-agent isolé n'a pas.

## Contraintes connues de l'utilisateur

- **Rejeté d'emblée** : rouvrir l'arbitrage de `renvoi-contrat-des-categories` — « la prose
  porte du jugement, qu'un renvoi ne remplace pas » reste en vigueur (dit)
- **Réutiliser** : le mécanisme d'empreintes de `scripts/check_pipeline.py` — une phrase
  verbatim par section de `contrat.md`, qui doit apparaître exactement une fois dans
  `skills/`. Il ne couvre que les 9 sections de `contrat.md`, et sa règle « une empreinte par
  section » ne s'étend pas telle quelle : `dette.md` et `contrat-liste.md` mêlent règles
  d'autorité et prose locale (dépôt: `scripts/check_pipeline.py`, `EMPREINTES`)
- **Historique** : le chantier `renvoi-contrat-des-categories` (2026-08-30) a déjà mené ce
  travail sur les recopies voisines et écarté `categories.md` par arbitrage
  (dépôt: `.claude/implementation/todo/technical-debt/sections-de-categories-jamais-confrontees-au-contrat.md`)

- **Tranché** : l'autorité de l'`id` réside dans `list-dir`. Il est immuable et égal au nom
  de son fichier — la règle y est déjà écrite (dépôt: `skills/list-dir/references/contrat-liste.md`
  l. 179 « C'est la seule identité », reprise l. 195, 335, 401) et appliquée
  (dépôt: `skills/list-dir/scripts/listdir/store.py:163-167`) (dit)
- **Tranché** : la référence à un élément de liste se fait par son `id`, qui est immuable.
  L'intitulé n'est jamais une référence. Les deux occurrences « intitulé »
  (`debt-review/references/categories.md` règle de preuve, `technical-debt/templates/review.md`
  « Verdict ») sont donc les erreurs ; `dette.md` « Écarter », `categories.md` « Doublon » et
  `gabarit-rapport.md` portent déjà la bonne version (dit)

## Les six recopies retenues

Relues contre le critère de `contrat.md` — *défini* à plusieurs endroits, pas seulement
*appliqué* — et contre l'arbitrage préservé :

| Règle | Autorité | Recopiée dans |
|---|---|---|
| Renommage Git cassé par un commit mixte | `dette.md` « Solder » | `cloture.md` §2, `debt-review` Ét. 5 |
| `for c in $(cmd)` avale le code de retour | `contrat-liste.md` « Ce que `contract` vise » | `debt-review` Ét. 3 |
| Sections de la fiche de revue | `templates/review.md` | `gabarit-rapport.md` |
| Comptage `merge` / préambule « 16 — 16 » | à désigner | `debt-review` Ét. 3, `gabarit-rapport.md` |
| 3 modes de défaillance (sous-agent atomique, travail partiel, relire le suivi) | `contrat.md` | `tracker/SKILL.md` Ét. 4 |
| `id` = seule identité, égal au nom de fichier, ne change jamais | `contrat-liste.md` l. 179 | `dette.md` l. 127 |

## Incertitudes à lever en plan

- **le mécanisme est-il dans le périmètre, et sous quelle forme ?** Hors critère de réussite
  (tranché), donc optionnel : A — empreintes libres,
  indexées par `(fichier-autorité, ancre)`, sans exiger une par section ; B — sections
  marquées, qui garde la complétude au prix d'une convention. Ou : corrections seules,
  sans mécanisme. Non tranché
- « comptage `merge` » : laquelle des deux écritures est l'autorité, `gabarit-rapport.md`
  ou `debt-review/SKILL.md` ? Le raisonnement est développé des deux côtés, aucune ne se
  déclare source
