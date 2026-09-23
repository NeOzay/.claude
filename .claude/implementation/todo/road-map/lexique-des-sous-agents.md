+++
id = "lexique-des-sous-agents"
title = "Donner les lexiques et leurs règles aux sous-agents"
date = 2026-09-23
source = "chantier `lexique`, vérification de l'étape 3 — choix de l'utilisateur : road-map plutôt que dette"
+++

## À faire

Un sous-agent ne reçoit aucun lexique : ni `CLAUDE.md` et ses imports (instructions du lexique,
lexique global), ni la sortie du hook `SessionStart` (lexique local). Constaté le 2026-09-23 avec un
`Explore` lancé dans une session neuve : il ignorait le terme local et ne connaissait des règles que
ce que dit la description de la skill `lexique`. Un sous-agent peut donc employer un terme hors de
sa définition sans le savoir. À discuter avant tout chantier : vérifier si un événement
`SubagentStart` existe dans la version installée et peut injecter du contexte ; sinon, recopier les
règles dans `agents/*.md`, selon « Un sous-agent recopie ses règles » ; délimiter quels agents
reçoivent `CLAUDE.md` (general-purpose, agents de `agents/`) et lesquels non (`Explore`, `Plan`).

## Références

- `skills/lexique/instructions.md`, `LEXIQUE.md`, `skills/lexique/scripts/lexique-cli.py` (`session`)
- `settings.json`, hooks `SessionStart`
- `hooks/outillage-rappel.sh`, en-tête : les sous-agents ne reçoivent pas `SessionStart`
- `skills/skill-convention/references/prose.md`, section « Un sous-agent recopie ses règles »
- `skills/skill-convention/references/commandes-locales.md`, « Portée du mécanisme » : les
  sous-agents trouvent les commandes du `PATH`, donc `lexique liste`
- chantier `lexique` (suivi, journal du 2026-09-23)
