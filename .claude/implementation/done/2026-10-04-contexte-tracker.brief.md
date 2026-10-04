+++
gabarit = "brief"
slug = "contexte-tracker"
titre = "Optimiser le contexte dans implementation-tracker"
statut = "validé"
execution = "direct"
"créé" = 2026-10-04
+++

## Intention

**Symptôme** : certains Chantiers dépassent largement les 400k de contexte.

**But** : rendre le passage à une nouvelle session le plus fluide possible, pour qu'un Chantier
tienne sous 400k sans payer de prefill inutile — coupures placées là où elles rapportent, un
message de passation qui porte ce que le Suivi ne dit pas, skill chargé par phase, et un agent
qui connaît son contexte.

## Critères de réussite

- `SKILL.md` du tracker ne porte plus les procédures de création ni d'exécution : il y renvoie
  vers deux fichiers de `references/`, et garde vérifications, routage et reprise.
- Chaque règle déplacée se retrouve à l'identique dans sa référence : `git diff --word-diff`
  sur le déplacement ne montre que titres et renvois.
- `grep -rn "Étape [0-6]" skills/implementation-tracker/SKILL.md` ne rend rien, et aucun
  renvoi aux anciens titres ne subsiste dans les fichiers qui les citaient.
- La procédure propose `/clear` puis la reprise après le commit `<L>E0`, et à un commit
  d'Étape seulement quand le contexte dépasse 300k tokens.
- La semence `suivi` déclare une section `## Passation` ; la procédure la réécrit avant le
  commit qui précède une coupure, et la reprise la restitue.
- L'agent lit la taille de son contexte courant par une commande ; la valeur concorde avec le
  dernier `usage` du transcript de la session.
- `uvx ruff check`, `uvx ruff format --check`, `uvx --with pytest basedpyright` et
  `uvx rumdl check` passent sur les fichiers touchés.

## Hors-périmètre

- Alléger la reprise : le Suivi reste lu en entier.
- Un hook `SessionStart` qui réinjecte l'état du Suivi après une compaction — l'utilisateur
  n'utilise pas la compaction.
- Modifier `intent-brief` au-delà de ses renvois aux titres renommés.
- Un hook d'alerte au-delà du seuil dans toute session, hors Chantier.
- Les trois sous-agents (`step-implementer`, `plan-reviewer`, `implementation-auditor`).

## Signaux de dérive

- Une règle de `SKILL.md` perdue ou réécrite en passant vers `references/` — le déplacement
  doit être un déplacement (dit)
- `statusline-command.py` fait plus que mesurer le contexte et écrire la valeur (dit)
- Une coupure proposée ailleurs qu'après `<L>E0` et au-delà du seuil à un commit d'Étape (dit)

## Contraintes connues de l'utilisateur

- **Rejeté d'emblée** : pas de coupure entre Brief et Plan — le plan a besoin de la discussion
  de cadrage (dit)
- **Rejeté d'emblée** : pas de coupure systématique à chaque Étape — prefill sans prompt
  caching (dit)
- **Décision** : coupure proposée après le commit `<L>E0`, puis à un commit d'Étape seulement
  au-delà d'un seuil de contexte (dit)
- **Existant** : l'utilisateur n'utilise pas la compaction (dit)
- **Existant** : l'utilisateur évite de dépasser 400k de contexte (dit)
- **Réutiliser** : la valeur du contexte s'extrait par `statusline-command.py` (dit), qui lit
  déjà `context_window.used_percentage` (dépôt: statusline-command.py) et reçoit aussi
  `session_id`, `context_window.total_input_tokens` et `context_window.total_output_tokens`
  (dit)
- **Décision** : la passation entre deux sessions — tâches en cours, informations utiles absentes
  du Suivi — vit dans une section `## Passation` du Suivi, réécrite à chaque coupure (dit)
- **Décision** : le seuil s'exprime en tokens et vaut 300k (dit)
- **Décision** : les titres « Étape 0…6 » de `SKILL.md` deviennent « Phase 0…6 » (dit)
- **Décision** : `SKILL.md` devient un routeur — création et exécution sortent vers
  `references/`, restent vérifications, routage et reprise (dit)
- **Existant** : les titres « Étape 0…6 » de `SKILL.md` emploient le terme Étape hors de sa
  définition au Lexique (dépôt: LEXIQUE.md) ; ils sont cités ailleurs (dépôt:
  skills/intent-brief/SKILL.md, references/contrat.md, references/dette.md,
  scripts/impl_list.py, skills/gabarit/gabarit/suivi/contract.toml,
  shadow-skills/skill-convention/references/prose.md)

## Incertitudes à lever en plan

- Quel champ mesure le contexte courant : `total_input_tokens` peut être un cumul de session
  plutôt que la taille du contexte — à vérifier sur une entrée réelle de la statusline.
- Comment l'agent lit la valeur écrite par la statusline : où elle l'écrit, et comment l'agent
  retrouve sa session (le nom du scratchpad porte l'identifiant de session — observé dans cette
  session, non garanti).
- Passation obligatoire ou optionnelle dans la semence `suivi`, et son effet sur
  `gabarit check --filled` pour les Suivis en cours et les archives de `done/`.
