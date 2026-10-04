+++
gabarit = "brief"
slug = "shadow-skill"
titre = "Shadow-skill : ranger les skills non indispensables hors du contexte, les trouver par CLI"
statut = "validé"
execution = "direct"
"créé" = 2026-10-04
+++

## Intention

**Symptôme** : tous les skills globaux sont chargés en permanence dans le contexte ; il n'est pas
essentiel de les connaître en permanence, et il n'y a aucun moyen de rechercher les skills
pertinents pour un Chantier.

**But** : un système « shadow-skill » où ranger les skills non indispensables, hors du contexte,
que l'agent liste, recherche et charge par une CLI ; les skills pertinents pour un Chantier sont
recherchés au brief et au plan, et notés dans le Suivi.

## Critères de réussite

- La commande `shadow-skill`, exposée dans `bin/`, liste les shadow-skills globaux et locaux, les
  recherche (nom, description, tags) et affiche le fichier principal de l'un d'eux
- Une commande `shadow-skill` affiche les descriptions des skills que liste le tableau d'un Suivi
- `nvim-mini-test`, `emmylua-ls` et `skill-convention` sont des shadow-skills : leur `SKILL.md`
  passe `gabarit check <chemin> --filled`
- `skills/nvim-mini-test/` et `skills/emmylua-ls/` n'existent plus ; `skills/skill-convention/`
  garde sa description actuelle et renvoie vers son shadow-skill
- Un tag qu'aucun shadow-skill ne déclare dans le fichier des tags est signalé par une commande
- La Semence `suivi` porte le tableau des skills ; `intent-brief` et `implementation-tracker`
  disent de rechercher les shadow-skills au brief et au plan
- Le `CLAUDE.md` racine importe par `@` l'`instructions.md` qui explique les shadow-skills

## Hors-périmètre

- Déplacer `gabarit`, `list-dir` ou `lexique` : on en a besoin en permanence (dit)
- Le côté Neovim de l'intégration : le Chantier ne crée que les commandes qu'il appellera (dit)

## Signaux de dérive

- Le `SKILL.md` d'un shadow-skill n'est pas un Gabarit posé depuis une Semence (dit)
- Le diff touche `skills/gabarit/`, `skills/list-dir/` ou `skills/lexique/`, hors la Semence
  `skills/gabarit/gabarit/suivi/contract.toml` (dit)

## Contraintes connues de l'utilisateur

- **Décision** : le système s'appelle « shadow-skill » (dit)
- **Décision** : la CLI liste, recherche et charge le fichier principal d'un shadow-skill (dit)
- **Décision** : front matter TOML, champs `name`, `description`, `when-to-load`, `tags` ;
  d'autres champs peuvent être proposés (dit)
- **Décision** : shadow-skills globaux dans `./shadow-skills/`, locaux à un projet dans
  `./.claude/shadow-skills/` (dit)
- **Décision** : `nvim-mini-test`, `emmylua-ls` et `skill-convention` migrent en shadow-skills
  dans ce Chantier (dit)
- **Décision** : `skill-convention` garde une entrée dans `skills/`, avec sa description
  actuelle, qui renvoie vers son shadow-skill (dit)
- **Décision** : la CLI fournit les commandes que la future intégration Neovim appellera, à
  sortie stable comme celles de `lexique` (dit)
- **Réutiliser** : comme `lexique`, un `instructions.md` importé par `@` dans le `CLAUDE.md`
  racine, et deux niveaux, global et local (dit ; dépôt: skills/lexique/instructions.md)
- **Décision** : exception au signal sur `skills/gabarit/` : la Semence
  `skills/gabarit/gabarit/suivi/contract.toml` peut être modifiée (dit)
- **Décision** : le `CLAUDE.md` racine explique les shadow-skills (dit)
- **Décision** : les tags sont enregistrés dans un fichier TOML plat qui dit lesquels existent,
  pour éviter les doublons, et donne à chacun une courte description (dit)
- **Décision** : les skills pertinents pour un Chantier sont indiqués dans le TOML du Suivi, en
  tableau, et recherchés lors du brief et du plan (dit)
- **Décision** : une commande `shadow-skill` charge dans le contexte les descriptions des skills
  que liste le Suivi (dit)
- **Existant** : `disable-model-invocation: true` retire déjà un skill de la liste vue par le
  modèle, mais il n'est alors plus invocable que par `/` (dépôt: skills/implementation-tracker/SKILL.md)
- **Existant** : un exécutable de skill s'expose par un lien dans `bin/` (dépôt: OUTILLAGE.md)
- **Existant** : la Semence `suivi` déclare les champs du Suivi, et le type `list` existe
  (dépôt: skills/gabarit/gabarit/suivi/contract.toml, skills/gabarit/references/format.md)

## Incertitudes à lever en plan

- Quelles commandes, et sous quelle forme de sortie, la future intégration Neovim appellera-t-elle ?
