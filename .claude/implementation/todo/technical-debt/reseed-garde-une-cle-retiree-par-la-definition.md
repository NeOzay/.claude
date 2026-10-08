+++
id = "reseed-garde-une-cle-retiree-par-la-definition"
title = "Une clé qu'une définition retire ne quitte jamais une liste semée, et `reseed` réémet alors le contrat sans le dire"
date = 2026-10-08
severite = "avertissement"
chantier = "registre-de-dette-severite-chantier-pin"
reference = "journal du Suivi"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

La version 3 de `technical-debt` retirait `required = false` de `[fields.source]`. Sur une copie du
registre, `reseed` a gardé la clé — la fusion à trois points garde une clé absente de la semence,
même quand le local ne l'a pas touchée — puis, le contrat fusionné ne valant plus la semence, l'a
réémis au lieu de la recopier. Ses 17 changements rapportés ne nommaient pas la clé gardée ; la
docstring de `provenance.fusionner` la dit « signalée ».

## Pourquoi c'est gênant

Une définition ne peut pas retirer une clé : chaque liste semée la garde, sans que `reseed` le dise.
Le contrat réémis perd ses commentaires et sa mise en forme, et ne vaut plus jamais sa semence. Le
Chantier l'a contourné en remettant la clé dans la définition.

## Pour solder

Une clé que la définition retire et que le local n'a pas modifiée quitte la liste au `reseed`, et le
rapport le nomme ; un test le vérifie, et la docstring dit ce que fait le code.

## Assumé

<OPTIONNEL>
