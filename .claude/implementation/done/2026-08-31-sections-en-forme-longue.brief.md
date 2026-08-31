---
slug: sections-en-forme-longue
titre: Sections du contrat list-dir en forme longue
statut: validé
execution: délégué
créé: 2026-08-30
---

## Intention

**Symptôme** : rien ne documente ce qu'il faut écrire dans les sections d'un élément.
`list-dir contract` sert une `description` par champ, mais `[sections]` n'est que deux listes de
noms — le corps, c'est-à-dire l'essentiel, n'a aucune doc là où l'outil la lit. « Il faudrait que
la documentation soit dans le "contract" » (dit).

**But** : étendre le format `[sections]` en une table par section, sur le modèle de `[fields.*]`,
portant `required` et `description`, et ouverte à d'autres clés plus tard (dit).

## Critères de réussite

- `list-dir contract <liste>` rend une description pour chaque section déclarée
- un contrat à l'ancien format (`required = [...]` / `optional = [...]`) échoue avec un message
  qui nomme la migration à faire (dit)
- une section sans clé `description` échoue ; `description = ""` passe (dit)
- le message d'erreur de l'ancien format renvoie à la semence de la liste pour savoir comment
  mettre à jour le contrat ; la réécriture est manuelle (dit)
- `list-dir validate` passe sur les trois registres de dette et sur la liste de revue
- la suite `scripts/tests/` passe

## Hors-périmètre

- pas de nouvelle clé de section au-delà de `required` et `description` — le format doit
  seulement les rendre possibles (dit)
- pas de nouvelle option de `contract` (pas de `--sections` en pendant de `--values`) — non abordé
- aucun outil de réécriture de contrat : ni `migrate --contract`, ni commande dédiée (dit)
- la prose d'en-tête de `templates/review.md` reste où elle est : la déplacer serait de la
  rédaction, elle appartient au chantier de description (tranché)
- pas de rédaction du contenu des descriptions : toutes les sections migrent avec
  `description = ""`, la rédaction se fera dans son propre chantier (dit)

## Signaux de dérive

- si les deux formats coexistent, même transitoirement, c'est raté : l'ancien lève une erreur (dit)
- si une commande hors `contract`/`types` se met à connaître la forme du TOML, s'arrêter

## Contraintes connues de l'utilisateur

- **Ordre** : l'ordre du TOML ordonne les sections — il remplace le « requises d'abord »
  d'aujourd'hui (dit ; dépôt: skills/list-dir/scripts/listdir/types.py:134-136)
- **Renvoi du message** : il suggère `list-dir contract --def <name>`, `<name>` tiré du contrat
  fautif, et mentionne `list-dir defs` ; il ne vérifie pas qu'une définition de ce nom existe
  (tranché)
- **Description obligatoire, valeur libre** : la clé doit être présente, sa valeur peut être vide
  (dit)
- **Contrats à migrer** : 3 définitions sous `skills/implementation-tracker/list-dir/`, leurs
  3 copies en vigueur sous `.claude/implementation/todo/`, et `templates/review.toml`
  (dépôt: 7 fichiers portant `[sections]`)
- **Une liste amorcée est détachée de sa semence** : migrer la définition ne migre pas la copie
  en vigueur (dépôt: skills/list-dir/references/contrat-liste.md:106-116)

## Incertitudes à lever en plan

Aucune : les deux ambiguïtés ouvertes pendant le cadrage — le renvoi du message d'erreur, le sort
de la prose d'en-tête de `templates/review.md` — ont été tranchées et écrites plus haut.
