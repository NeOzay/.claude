+++
id = "description-obligatoire-sur-les-sections-seulement"
title = "« description » est obligatoire sur une section, facultative sur un champ"
date = "2026-09-05"
source = "chantier `decoupe-contrat-liste`, constat de l'utilisateur en cours d'étape 7"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Un contrat déclare ses champs et ses sections sur le même modèle — `[fields.<nom>]` et
`[sections."<titre>"]`, mêmes clés `required` et `description`. La lecture, elle, les traite
différemment :

- `skills/list-dir/scripts/listdir/contract.py:422` lit la description d'un champ par `_texte()`,
  qui rend `""` quand la clé est absente (l. 163) — aucun test de présence ;
- `skills/list-dir/scripts/listdir/contract.py:475` teste `if "description" not in body` pour une
  section, et refuse le contrat en la nommant.

Vérifié à l'exécution : un contrat sans `description` sur `[fields.title]` passe `validate` ; le
même sans `description` sur `[sections."S"]` sort « section « S » — « description » manquante ».
La `description` du contrat lui-même est facultative, par le même `_texte()`.

L'asymétrie n'est **pas voulue** — dit par l'utilisateur le 2026-09-05.

## Soldé le

**Soldé le 2026-09-05 par le chantier `description-obligatoire-partout`** — `description` est
désormais exigée aux trois endroits, champ, section et racine du contrat, sur le modèle du
contrôle qui existait déjà pour les sections. C'est la clé qui est exigée, pas son texte :
`description = ""` reste accepté partout, de sorte qu'un contrat à moitié documenté se voit à la
déclaration sans qu'il faille rédiger sur-le-champ. La règle est énoncée en un seul endroit,
`skills/list-dir/references/format.md`, où le tableau de l'asymétrie a disparu.
Établi par :

```
$ d=$(mktemp -d) && mkdir -p "$d/.list" \
    && printf 'name = "x"\ndescription = ""\n\n[fields.id]\ntype = "slug"\n' \
       > "$d/.list/contract.toml" \
    && list-dir validate "$d"
/tmp/tmp.4psAxG089H/.list/contract.toml: champ « id » — « description » manquante
$ echo $?
1
```

Le même contrat, `description = ""` ajoutée sous `[fields.id]`, passe. Les contrats produits par
l'outil restent valides sans intervention : `list-dir init` puis `validate` → « 0 élément(s)
conformes », `list-dir derive … --template review` puis `validate` → « 46 élément(s) conformes ».
Suite de tests : 444 passent, dont quatre neufs sur cette règle.

## Pourquoi c'est gênant

Deux tables présentées comme parallèles n'obéissent pas à la même règle, et rien ne le dit à
l'endroit où on écrit un contrat. Un auteur qui documente ses sections parce que l'outil l'y force
laissera ses champs muets sans jamais s'en apercevoir : `validate` ne le lui dira pas, et
`list-dir contract` servira une description vide sans distinguer « pas de texte » de « pas
documenté ». La règle des sections existe précisément pour que ce cas soit visible ; sur les
champs, elle est absente.

Le mode de défaillance est silencieux et durable : un contrat à moitié documenté reste vert
indéfiniment.

## Pour solder

Rendre les deux tables symétriques. Deux voies, à trancher :

- **`description` obligatoire partout** — cohérent avec la raison d'être de la règle des sections,
  mais **cassant** : tout contrat existant portant un champ sans description devient invalide, y
  compris les définitions du dépôt. Exige un passage sur chaque `contract.toml` et chaque semence,
  et une note de migration.
- **`description` facultative partout** — non cassant, immédiat, mais perd le garde-fou : plus
  rien ne rend visible une section non documentée, et la raison invoquée aujourd'hui pour
  l'exiger disparaît sans être remplacée.

Quelle que soit la voie retenue, l'écrire dans `skills/list-dir/references/format.md`, section
« Le contrat » — c'est là que la règle est énoncée aujourd'hui, dans le paragraphe des sections.

## Assumé

<OPTIONNEL>
