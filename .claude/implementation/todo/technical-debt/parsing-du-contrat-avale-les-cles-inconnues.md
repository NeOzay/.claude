+++
id = "parsing-du-contrat-avale-les-cles-inconnues"
title = "Le parsing du contrat accepte en silence ce qu'il ne comprend pas"
date = 2026-08-31
severite = "avertissement"
chantier = "sections-en-forme-longue"
reference = "R2, R3"
pin = false
source = "chantier sections-en-forme-longue, audit R2 et R3"
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

Deux laxismes distincts dans la construction des `Section` et des `Field`, `listdir/contract.py`,
vérifiés par sondage sur le dépôt à `752449e` :

- une **clé inconnue est ignorée sans un mot**. `[sections."A"]` portant `require = true` — la
  faute de frappe la plus probable sur ce nom — rend `Section(name='A', required=False,
  description='')`. La section devient facultative, aucune commande n'échoue.
- une **valeur de mauvais type est coercée**. `required = "false"`, la chaîne, passe par
  `bool(body.get("required", False))` et rend `required=True` : l'exact contraire de ce qui est
  écrit.

Le second défaut est hérité tel quel des `Field`, où la même expression est employée ; le premier
y existe aussi. Le chantier `sections-en-forme-longue` ne les a pas créés — il a calqué la boucle
des sections sur celle des champs, y compris sur ce point.

**Complété le 2026-10-07** (chantier `socle-contrat-evolutif`, audit de clôture `d5be681`, R3) — la
première clé optionnelle réelle vient d'arriver : `deprecated`, sur les champs et les sections.
C'est l'échéance que l'Assumé annonçait. Sa valeur est contrôlée (chaîne non vide, refusée avec
`required`, `text` ou `command`), mais sa clé ne l'est pas : `deprecaed = "…"` est accepté sans un
mot, code 0, le champ n'est alors pas déprécié et le contrat continue de le poser et de le
réclamer.

## Pourquoi c'est gênant

Le format des sections a été introduit « ouvert à d'autres clés plus tard ». C'est précisément ce
qui rend la première clé optionnelle réelle dangereuse : le jour où une clé est ajoutée, tous les
contrats qui l'orthographient mal continueront de valider, avec un comportement par défaut
silencieux, et rien ne distinguera « pas déclarée » de « déclarée de travers ».

Le chantier vient par ailleurs de rendre `description` obligatoire pour que l'absence de
documentation soit **visible**. Une clé avalée en silence rouvre exactement le trou que cette
décision fermait, un cran plus bas.

## Pour solder

Trancher d'abord la question de fond, qui n'est pas technique : le contrat est-il **fermé** — toute
clé non reconnue est une erreur nommant le fichier, la section et la clé — ou volontairement
extensible ? Les deux se défendent, mais « extensible » n'est tenable que si les clés inconnues
sont au moins **signalées**, sinon l'extensibilité n'est qu'un nom donné à l'absence de contrôle.

Le typage suit la même décision : remplacer `bool(...)` par un contrôle qui refuse ce qui n'est pas
un booléen TOML, en nommant la valeur fautive — comme le fait déjà le contrôle des jetons de
`values`. **Traiter les sections et les champs dans la même passe** : les corriger séparément
laisserait deux règles là où le lecteur en attend une.

## Assumé

Rien n'oblige à le faire maintenant : aucune clé optionnelle n'existe encore, et le format n'a
qu'un mois. C'est le moment de la première extension qui est la vraie échéance — pas celui-ci.
