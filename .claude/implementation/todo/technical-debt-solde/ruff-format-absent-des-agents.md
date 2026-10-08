+++
id = "ruff-format-absent-des-agents"
title = "Aucun agent du pipeline ne lance `ruff format`"
date = 2026-10-04
severite = "<OPTIONNEL>"
chantier = "<OPTIONNEL>"
reference = "<OPTIONNEL>"
pin = "<OPTIONNEL bool>"
source = "hors chantier, au solde de `ruff-format-jamais-applique` (2026-10-04)"
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

Le formatage est entré au contrat du dépôt le 2026-10-04 : `OUTILLAGE.md` déclare
`uvx ruff format --check .` dans son tableau de dépendances, et pose dans « Vérifier le code
Python » la règle « Le formatage fait partie du contrat : `uvx ruff format .` avant de commiter du
Python ». Le rappel de session (`hooks/outillage-rappel.sh`) la répète.

Les deux sous-agents du pipeline n'en disent rien. Ils portent leurs commandes de vérification en
dur, par choix (`OUTILLAGE.md`, « Les sous-agents portent ces règles en dur ») :
`implementation-auditor.md` à son paragraphe « Les linters de ce dépôt sont `ruff` et
`basedpyright`, et eux seuls », `plan-reviewer.md` à la ligne qui cite les mêmes lanceurs. Aucun
des deux ne mentionne `ruff format`.

Établi par : `grep -c 'ruff format' agents/*.md` → `0` pour chacun des deux fichiers (2026-10-05).
Le constat d'origine portait aussi sur `step-implementer.md`, retiré depuis par le Chantier
`retouches-et-modele-du-chantier`.

## Soldé le

**2026-10-06, chantier `mods-a-la-racine-des-skills`** — soldée à l'inverse du « Pour solder »,
comme le Brief le décide : les agents ne portent plus aucune règle d'outillage, et le mod
`outillage` verse à chaque sous-agent lancé sur ce dépôt un rappel qui porte `ruff format`.

Établi par :

- `grep -c 'ruff format' .claude/skills/outillage/scripts/rappel.sh` → `1`.
- transcription du sous-agent de l'audit de clôture,
  `projects/-home-debian--claude/f070f2ee-801b-4077-b292-6ac880d212b8/subagents/agent-acd0ea04bce624ddc.jsonl`
  → premier message ouvert sur « Outillage de ce dépôt (/home/debian/.claude/OUTILLAGE.md) : », et
  la ligne « `uvx ruff format <chemins>` avant de commiter du Python ».

Non repris : le rappel est une consigne d'auteur, et rien ne fait compter à l'auditeur un fichier
hors format comme un écart ; il n'arrive pas non plus depuis un sous-dossier du dépôt. Restent au
registre : `ruff-format-non-juge-par-l-auditeur`,
`rappel-d-outillage-absent-depuis-un-sous-dossier`.

## Pourquoi c'est gênant

C'est le mode de défaillance que `ruff-format-jamais-applique` a documenté avant son solde, et que
le solde ne ferme qu'à moitié : la règle est écrite, mais ceux qui jugent le code ne la lisent pas.
`implementation-auditor` juge le Chantier sans lancer `ruff format --check`, et ne peut donc pas
signaler l'écart. `plan-reviewer` accepte un Plan dont la vérification d'Étape l'omet.

Les fichiers hors format reviennent alors en silence, Chantier après Chantier : 5 fichiers de
`list-dir` le 2026-08-30, 8 le 2026-09-06, 21 sur le dépôt entier au premier formatage. Le
prochain `ruff format .` reformaterait du code étranger au travail en cours, et son diff
couvrirait ce travail.

## Pour solder

Ajouter `ruff format` aux deux agents, là où chacun cite déjà ses lanceurs :

- `implementation-auditor.md` : lancer `uvx ruff format --check <chemins>` à côté de
  `uvx ruff check <chemins>`, et compter un fichier hors format comme un écart ;
- `plan-reviewer.md` : citer `ruff format --check` parmi les vérifications qu'une commande d'Étape
  sur du Python doit porter.

Puis relancer le garde-fou, qui contrôle le contenu des agents : `scripts/check_pipeline.py` doit
rendre « Pipeline conforme. ». Solde établi par `grep -c 'ruff format' agents/*.md` → au moins `1`
pour chacun des deux fichiers.

## Assumé

<OPTIONNEL>
