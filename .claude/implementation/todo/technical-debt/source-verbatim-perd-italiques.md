+++
id = "source-verbatim-perd-italiques"
title = "Le champ `source` est déclaré « verbatim » et perd les délimiteurs d'italique"
date = 2026-08-23
source = "chantier `format-registres`, R8 des audits de clôture"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le contrat de `technical-debt` décrit `source` comme « le chantier qui l'a identifiée et où il l'a
écrit, **verbatim** ». La migration a transformé la ligne source

    *Identifié par `contrat-pipeline`, R15 et R19 du rapport d'audit.*

en `source = "Identifié par \`contrat-pipeline\`, R15 et R19 du rapport d'audit."` — les astérisques
d'italique sont tombés. Le texte est entier ; seule la mise en forme disparaît.

## Pourquoi c'est gênant

Le mot « verbatim » du contrat promet plus que ce qui est livré, et c'est le contrat qui fait foi
pour qui lit la liste sans connaître son histoire. Un écart voisin est consigné dans le suivi du
chantier (un retour à la ligne absorbé) sans que celui-ci le soit — deux petites entorses à la même
promesse, dont une seule est tracée.

## Pour solder

Choisir laquelle des deux est vraie, et aligner l'autre :

- soit la description du champ cesse de dire « verbatim » et dit ce qui est réellement conservé —
  le texte, pas sa mise en forme ;
- soit la migration est refaite en conservant les délimiteurs, ce qui n'a d'intérêt que si quelqu'un
  relit ces valeurs comme du Markdown.

La première voie est probablement la bonne : le champ sert à retrouver l'origine, pas à être rendu.

## Assumé

<OPTIONNEL>
