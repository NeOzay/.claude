+++
id = "hook-sante-chemin-home"
title = "Le hook SessionStart porte la dernière constante ancrée sur le HOME, sans être déclarée comme exception"
date = 2026-08-29
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n 'sante_skills' settings.json
51:            "command": "python3 $HOME/.claude/scripts/sante_skills.py"

$ grep -n "sante_skills\|amorçage" skills/implementation-tracker/references/contrat.md
237:gagne dans le `PATH` sont vérifiés **une fois par session** par `scripts/sante_skills.py`, branché
250:`scripts/sante_skills.py` le dit au démarrage de la session suivante, en nommant la ligne à

$ grep -n "sante_skills\|ne couvre pas" .claude/implementation/todo/technical-debt-solde/chemin-skill-code-en-dur.md
65:- `python3 scripts/sante_skills.py` → **code 0** : chaque lien de `bin/` est relatif, résout, est
68:Ce que le solde ne couvre pas : un `.md` reste libre de **citer** un chemin relatif à la racine du
```

## Verdict

La ligne 51 de `settings.json` porte toujours `$HOME/.claude/`. Les deux mentions de
`sante_skills.py` dans `contrat.md#dépendances` décrivent **ce que le hook vérifie**, jamais le
fait que son propre chemin soit l'exception assumée à la règle « aucun chemin ancré sur le
`HOME` ». Et la liste « ce que le solde ne couvre pas » de la fiche `chemin-skill-code-en-dur`
(ligne 68) parle de citations dans les `.md` — elle ne mentionne pas ce hook.

Les deux gestes du `Pour solder` restent donc à faire. L'exception est toujours indistinguable
d'un oubli, ce qui est exactement le coût décrit.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
