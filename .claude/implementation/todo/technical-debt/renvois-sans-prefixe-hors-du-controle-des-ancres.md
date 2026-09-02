+++
id = "renvois-sans-prefixe-hors-du-controle-des-ancres"
title = "Les renvois sans préfixe ../ échappent au contrôle des ancres mortes"
date = "2026-09-02"
source = "chantier `recopies-hors-contrat`, réserve de forme de l'audit de clôture"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le contrôle 8 de `check_pipeline.py` vérifie que tout renvoi entre skills résout — chemin et ancre.
Son motif `RENVOI_INTER_SKILL` n'accepte que les liens dont le chemin commence par `../`. Deux
formes lui échappent donc entièrement :

- les renvois **intra-fichier**, `[Un titre](#ancre)` — le chantier `recopies-hors-contrat` en a
  introduit trois, dans `dette.md` et `contrat-liste.md` ;
- les renvois vers un **fichier voisin**, `[Solder](dette.md#solder)` sans préfixe — `cloture.md` en
  portait déjà un avant ce chantier.

Vérifiées à la main lors de la clôture, ces ancres résolvent aujourd'hui.

## Pourquoi c'est gênant

Le contrôle 8 existe pour une raison écrite dans son propre code : un lien vers une section
renommée « reste vert et dépose le lecteur en tête d'une référence de 400 lignes ». Cette raison
vaut exactement autant pour un renvoi interne, et le nombre de ces renvois vient d'augmenter — c'est
la forme que prend la résorption d'une recopie quand l'autorité est dans le même fichier.

Le mode de défaillance est silencieux : renommer une section ne casse rien de visible, et le
garde-fou reste vert.

## Pour solder

Élargir `RENVOI_INTER_SKILL` aux deux formes, en distinguant la cible : un renvoi intra-fichier se
vérifie contre les ancres du fichier lui-même, un renvoi voisin contre celles de la cible résolue
depuis son répertoire. `ancres_markdown()` fournit déjà le nécessaire.

Attention au compte du contrôle : il rendrait bien plus de renvois, et un `cites == 0` ne serait
plus le signal qu'il est aujourd'hui.

## Assumé

<OPTIONNEL>
