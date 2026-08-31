+++
id = "sections-declarees-sans-description-redigee"
title = "Toutes les descriptions de section du dépôt sont vides"
date = 2026-08-31
source = "chantier sections-en-forme-longue, hors-périmètre assumé au brief"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le chantier `sections-en-forme-longue` a donné aux sections d'un contrat une clé `description`, et
l'a rendue obligatoire, pour que `list-dir contract` documente le **corps** d'un élément et plus
seulement son front matter. C'était le symptôme d'origine : « rien ne documente ce qu'il faut
écrire dans les sections d'un élément ».

Les huit contrats du dépôt — quatre semences sous `skills/implementation-tracker/list-dir/`, quatre
copies en vigueur sous `.claude/implementation/todo/` — portent tous `description = ""`. La
migration a été mécanique, comme le brief le prévoyait explicitement au hors-périmètre : « pas de
rédaction du contenu des descriptions […] la rédaction se fera dans son propre chantier ».

Le mécanisme est donc en place et vérifié ; ce qu'il devait servir n'existe pas encore.

## Pourquoi c'est gênant

En l'état, `list-dir contract` rend une ligne `description = ""` par section — soit exactement
l'information dont l'absence a motivé le chantier, désormais présente sous forme vide. Le
symptôme d'origine n'a pas disparu : il est devenu visible et adressable, ce qui était le but de
cette étape, mais il n'est pas soldé.

Le risque propre à cet état est qu'il se lise comme un achèvement. Un contrat qui répond à la
question sans y répondre est plus trompeur qu'un contrat qui ne dit rien : la commande a l'air de
documenter.

## Pour solder

Rédiger les descriptions, contrat par contrat, en commençant par les trois registres de dette dont
les sections portent déjà leur doctrine ailleurs — `dette.md` dit ce qu'un `Constat` doit contenir,
ce qui distingue « Pourquoi c'est gênant » de « Pour solder », et pourquoi `Constat` reste requis
dans les listes soldée et écartée. C'est cette prose-là qui a vocation à descendre dans les
`description`, là où l'outil la lit.

Écrire dans la **semence** et la copie en vigueur dans la même passe : rien ne les resynchronise
(voir `semence-et-copie-divergent-sans-controle`).

## Assumé

Le découpage est délibéré et documenté au brief : séparer le format de son contenu permettait de
livrer un mécanisme vérifiable sans arbitrer en même temps la rédaction de huit fichiers de
doctrine. C'est le report qui est assumé, pas l'absence.
