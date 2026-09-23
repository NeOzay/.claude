---
name: skill-convention
description: >
  Conventions de maintien de ma configuration Claude Code, globale (~/.claude) comme locale à un
  projet : prose d'une skill, code Python, documents posés depuis un gabarit, mémoire tenue en
  registres, commandes mises à la disposition d'un agent. Se déclenche à l'écriture ou à la
  relecture d'un `SKILL.md`, d'un fichier de `references/` ou de tout autre fichier d'une skill,
  à la pose d'un document ou d'un registre, et dès qu'un projet doit fournir une nouvelle commande à un
  agent. Ne corrige aucune skill.
---

# skill-convention — les conventions de ma configuration

Ce skill énonce les conventions de maintien de la configuration globale (`~/.claude`) et des
configurations locales à un projet.

**Principe directeur : réduire au maximum le non-déterminisme du modèle.** Toutes les conventions
qui suivent y servent ; trois le portent directement.

- **Un document se pose depuis un gabarit** — [gabarit](../gabarit/SKILL.md) construit le fichier
  depuis un contrat, le modèle le remplit. Un modèle qui invente aussi la structure produit deux
  fichiers différents pour le même besoin.
- **Une mémoire se tient en registre** — [list-dir](../list-dir/SKILL.md) : un répertoire est une
  liste, un fichier un élément, un contrat déclare la structure et `validate` la vérifie. Une
  mémoire en prose libre ne se filtre pas, ne se compte pas, et se relit à chaque consultation.
- **Le frontmatter porte les données mutables**, séparées de la prose. Ce qui change au fil d'un
  chantier — statut, session, branche, dates — se lit et s'écrit là, sans relire le texte ni
  risquer de le réécrire.

**Ce skill décrit, il ne corrige pas.** Un écart constaté dans une skill existante va au registre
de dette ([Registre de dette](../implementation-tracker/references/dette.md)) : réaligner une skill
est un chantier à part entière, avec son brief.

**Il renvoie plutôt qu'il ne recopie.** Une règle qui a déjà son autorité ailleurs y reste, et ce
skill y mène.

## Où est chaque convention

| Sujet | Autorité | Lire quand |
|---|---|---|
| Prose d'une skill | [`references/prose.md`](references/prose.md), vers lequel `rules/skill-prose.md` renvoie au contact d'un fichier de skill | on écrit ou relit un `SKILL.md` ou une référence |
| Code Python | `rules/claude-python-style.md`, chargé au contact d'un `*.py` — par chemin relatif sur ce dépôt-ci, par `**/.claude/**` ailleurs | on écrit du Python |
| Poser un document depuis un contrat | [gabarit](../gabarit/SKILL.md) | on crée un fichier structuré à remplir |
| Tenir un registre | [list-dir](../list-dir/SKILL.md) | on crée, valide, filtre ou migre une liste de fichiers |
| Commandes à la disposition d'un agent | [`references/commandes-locales.md`](references/commandes-locales.md) | une skill ou un projet doit fournir une commande |
| Lancer les outils du dépôt, exposer un exécutable | [Outillage du dépôt](../../OUTILLAGE.md) | on lance un linter, on ajoute un lien dans `bin/` |
| Dates, nommage, frontmatter du pipeline | [Contrat du pipeline](../implementation-tracker/references/contrat.md) | on écrit un brief, un suivi, une archive |
| Sens des mots | `LEXIQUE.md` à la racine, et la skill [lexique](../lexique/SKILL.md) pour le tenir | on emploie, propose ou définit un terme |

Les fichiers de `rules/` ne sont pas cités par lien : ils vivent hors de `skills/`, et Claude Code
les charge seul, d'après leur champ `paths`.
