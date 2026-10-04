---
name: shadow-skill
description: >
  Tient les Shadow-skills et leurs registres de tags. Se déclenche pour créer, migrer ou vérifier
  un Shadow-skill, ou ajouter un tag. Ne sert ni à en chercher ni à en charger un : la commande
  `shadow-skill` y suffit.
---

# shadow-skill — des skills hors du contexte

Quand et comment chercher un Shadow-skill est dit dans [`instructions.md`](instructions.md), que
`CLAUDE.md` charge à chaque session : ces règles font autorité. Ce fichier dit comment tenir les
shadow-skills.

**Partage des rôles** : la commande lit, cherche, résout et vérifie. Le modèle rédige le skill et
choisit ses tags ; l'utilisateur décide de ce qui sort de `skills/`.

## Ce qu'est un Shadow-skill

Un répertoire `<niveau>/<nom>/` qui porte un `SKILL.md`, Gabarit de la Semence `shadow-skill`, et
ses éventuels `references/`. Claude Code ne le voit pas : rien de lui n'entre dans le contexte tant
qu'on ne l'a pas chargé. Ce que son front matter et ses sections attendent :

```bash
gabarit contract shadow-skill
```

Deux niveaux, lus global puis local :

- **global** : `shadow-skills/`, à la racine de la configuration ;
- **local** : `<projet>/.claude/shadow-skills/`, le projet étant la racine du dépôt git du
  répertoire courant, ou `--projet DIR`.

Un nom défini aux deux niveaux est une faute, que `verifie` signale, et sur laquelle `charge` et
`chemin` échouent en nommant les deux chemins : choisir en silence chargerait un skill que
personne n'a désigné.

## Poser un Shadow-skill

1. `shadow-skill tags` : choisir les tags parmi ceux qui existent. Un tag nouveau s'ajoute au
   `tags.toml` du niveau — une ligne `tag = "description"` —, et seulement s'il ne double pas un tag
   existant sous un autre nom : un doublon coupe la recherche en deux.
2. `gabarit new shadow-skill <niveau>/<nom>/SKILL.md`, puis remplir : `name` est le nom du
   répertoire, `when-to-load` dit dans quelle situation le charger. Le contenu va sous
   `## Instructions`, ses subdivisions en `###` ; les fichiers de référence se listent sous
   `## Références`.
3. `shadow-skill verifie` : **0** attendu.

**Migrer un skill de `skills/`** suit les mêmes étapes, sur le fichier existant : le front matter
YAML devient le front matter TOML de la Semence, le corps passe sous `## Instructions`, ses titres
descendent d'un niveau, et les liens qui sortent du skill se réécrivent depuis son nouvel
emplacement. Un skill qui doit continuer à se déclencher seul garde une entrée dans `skills/`, sa
description d'origine, et un corps qui renvoie à `shadow-skill charge <nom>`.

## La commande

```bash
shadow-skill liste [--projet DIR]                 # niveau, nom, description, when-to-load
shadow-skill cherche MOT… [--projet DIR]          # les skills où figure chaque mot
shadow-skill charge NOM [--projet DIR]            # le répertoire du skill, puis son SKILL.md
shadow-skill chemin NOM [--projet DIR]            # le chemin de son SKILL.md
shadow-skill depuis-suivi SLUG [--projet DIR]    # nom, description, when-to-load des skills d'un Suivi
shadow-skill tags [--projet DIR]                  # niveau, tag, description de chaque tag
shadow-skill verifie [--projet DIR]               # les constats sur les skills et les tags
```

`shadow-skill` est un lien de `bin/` vers `scripts/shadow-skill-cli.py`, résolu par le `PATH`. Une
sortie est une ligne par élément, ses champs séparés par une tabulation ; `liste` et `cherche`
rendent `niveau`, `nom`, `description` et `when-to-load`, de quoi décider d'un `charge` sans le
faire. `liste`, `cherche` et
`chemin` sont faites pour être appelées par Neovim : leur sortie est une interface.

- `liste` : **0**, même si un `SKILL.md` est mal formé — la faute sort sur stderr ; **1** un niveau
  illisible, l'autre servi quand même.
- `cherche` : **0** au moins un skill, où chaque mot figure, sans casse ni accents, dans le nom, la
  description, `when-to-load` ou les tags ; **1** aucun.
- `charge`, `chemin` : **0** ; **1** nom inconnu — les noms connus sont listés — ou défini aux deux
  niveaux.
- `depuis-suivi` : lit le Suivi actif `.claude/implementation/<slug>.md` du projet. **0** ; **1**
  aucun Suivi actif de ce slug, pas de champ `skills`, ou un nom inconnu — les autres sont servis
  quand même.
- `tags` : **0** ; **1** un registre illisible ou mal formé, l'autre servi quand même.
- `verifie` : **0** conforme ; **1** au moindre constat — `gabarit check --filled` d'un `SKILL.md`,
  Estampille, `name` différent du répertoire, tag absent du registre de son niveau et du global,
  tag local qui redéfinit un global, nom des deux niveaux —, **et quand aucun skill n'a été
  examiné**.
- Toutes : **2** erreur d'appel.
