---
slug: check-pipeline-python
titre: Réécriture du garde-fou de pipeline en Python
statut: validé
execution: direct
créé: 2026-08-23
---

## Intention

**Symptôme** : `scripts/check-pipeline.sh` est en bash, hors de portée du typage
statique qui couvre le reste du code du dépôt, et porte des dettes connues (dit).
**But** : réécrire le script en Python, le placer sous `pyrightconfig.json`, et
corriger dans le même mouvement les dettes existantes (dit).

## Critères de réussite

- `python3 scripts/check-pipeline.py` → code 0 sur l'arbre du chantier, tous contrôles verts
- une suite de tests rejouable : unitaires par contrôle **et** injection bout-en-bout
  d'un défaut par contrôle, chacun donnant rouge (dit, arbitrage du 2026-08-23)
- `basedpyright` en mode `all` → 0 erreur, le nouveau code étant couvert par
  `pyrightconfig.json` (dit)
- les cinq dettes retenues sont soldées ou explicitement assumées

## Hors-périmètre

- pas de résolution dynamique du chemin de skill : la cause de `chemin-skill-code-en-dur`
  reste ouverte au registre (dit)
- `listdir` n'est ni touché ni testé (dit)
- `hooks/intent-brief-gate.sh` n'est pas migré — pédagogique et échoue ouvert, autre
  nature que le garde-fou (dépôt: scripts/check-pipeline.sh:8-9)
- les règles portées par `contrat.md` ne sont pas amendées (dit)

## Signaux de dérive

- si le diff touche `contrat.md` ou un `SKILL.md` au-delà de la ligne d'appel
  `bash`→`python3`, c'est raté : chantier d'outillage, pas de contenu de règles (dit)
- si un paquet importable façon `listdir` apparaît (couches, `Result[T]`, modules par
  responsabilité), c'est raté : deux scripts, pas une bibliothèque (dit)
- si le comportement d'un contrôle change sans qu'une dette retenue le demande —
  réécrire n'est pas redéfinir ce que le garde-fou juge (dit)
- si les tests débordent sur `listdir` : sa dette de tests est un autre chantier (dit)
- si une dette hors des cinq retenues se met à être soldée (dit)

## Contraintes connues de l'utilisateur

- **Suivi par pyright** : le nouveau fichier doit entrer dans `pyrightconfig.json`,
  dont l'`include` ne couvre aujourd'hui que `skills/` (dit ; dépôt: pyrightconfig.json)
- **Emplacement tranché** : les scripts restent dans `scripts/`, l'`include` de
  `pyrightconfig.json` est élargi (arbitrage du 2026-08-23)
- **Tests tranchés** : unitaires `pytest` (via `uvx`, aucune installation permanente)
  **plus** injection bout-en-bout sur arborescence-jouet (arbitrage du 2026-08-23)
- **Outillage** : Python 3.14.7, `uv`/`uvx` présents, aucun `pyproject.toml`, aucun test
  dans le dépôt à ce jour (dépôt: `python3 -V`, `find … -name 'test_*.py'` → vide)
- **Réécriture**, pas transposition ligne à ligne (dit)
- **Dettes à corriger dans le même chantier** : les deux qui visent le script
  (`garde-fou-cinq-angles-morts`, `table-empreintes-a-la-main`) **et le voisinage**
  (`impl-list-extension-gnu-find`, `deux-renvois-non-navigables`,
  `chemin-skill-code-en-dur`) (dit)
- **`chemin-skill-code-en-dur` se solde par un contrôle 7** : le garde-fou vérifie que
  chaque chemin `$HOME/.claude/skills/…` cité dans un `.md` désigne un fichier existant.
  Résoudre le chemin à la source est écarté — autre chantier ; l'entrée de dette reste
  ouverte pour la cause (arbitrage du 2026-08-23)
- **Les deux `.sh` sont supprimés dans le chantier**, dès que leur équivalent Python
  passe les tests — pas de doublon (arbitrage du 2026-08-23)
- **`impl-list.sh` migre aussi en Python** (dit) — ses trois appels dans `skills/` sont
  à réécrire en `python3` (dépôt: implementation-tracker/SKILL.md:42,:75,
  references/contrat.md:202)
- **Réutiliser** : `skills/list-dir/scripts/listdir/` est le précédent Python du dépôt,
  Python ≥ 3.12 (dépôt: pyrightconfig.json, skills/list-dir/scripts/)
- **Précédent** : la migration était explicitement reportée comme « chantier à part »
  par `format-registres` (dépôt: .claude/implementation/done/2026-08-23-format-registres.plan.md:704)

## Incertitudes à lever en plan

- structure interne du garde-fou : la séparation « collecte / jugement » qui rend chaque
  contrôle testable unitairement reste à concevoir — mission du plan
- `deux-renvois-non-navigables`, second volet : **tranché le 2026-08-23** — le renvoi de
  `agents/implementation-auditor.md` vers `audit.md` est ancré en `#gabarit-du-rapport`
