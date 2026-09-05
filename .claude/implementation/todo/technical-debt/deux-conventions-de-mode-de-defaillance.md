+++
id = "deux-conventions-de-mode-de-defaillance"
title = "Deux conventions de rédaction du mode de défaillance coexistent sans règle"
date = "2026-09-05"
source = "chantier `decoupe-contrat-liste`, réserve R6 de l'audit de clôture"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Les références du dépôt signalaient jusqu'ici un mode de défaillance par un bloc cité en propre :

```markdown
> *Mode de défaillance* — choisir en silence ferait dépendre le contrat d'une liste de l'ordre de
> parcours d'un répertoire.
```

Le chantier `decoupe-contrat-liste` a **intégré au corps du texte** les treize blocs de
`contrat-liste.md`, sur décision explicite du brief (« condenser et intégrer les modes de
défaillance aux exemples et à l'utilisation des fonctionnalités »). Les cinq références de
`list-dir` n'en portent donc plus aucun — vérifié à la clôture : 13 → 0.

La convention reste vivante ailleurs, et nombreuse : `skills/debt-review/SKILL.md`,
`skills/implementation-tracker/references/dette.md`, `references/contrat.md`, `cloture.md`.

Aucune règle n'a été écrite pour dire laquelle des deux formes s'applique où.

## Pourquoi c'est gênant

Le prochain chantier qui touche une référence hésitera, et tranchera par imitation du fichier
qu'il a sous les yeux — ce qui fige l'écart au lieu de le résorber. Deux conventions non arbitrées
divergent toujours dans le même sens : chaque fichier garde la sienne, et la forme finit par
dépendre de qui a écrit en dernier.

Le coût n'est pas dans le fond, intégralement conservé de part et d'autre, mais dans la lecture :
un bloc cité se repère d'un coup d'œil et se compte au `grep`, un mode de défaillance fondu dans
la prose ne se retrouve qu'en lisant. Deux des treize de `list-dir` ne sont d'ailleurs plus
identifiables par leur formulation d'origine — l'audit a dû les retrouver par leur contenu.

## Pour solder

Trancher, puis appliquer partout :

- **généraliser l'intégration au texte** — cohérent avec ce que le chantier vient de faire, et avec
  l'argument qui l'a motivé (un bloc cité isolé se lit comme un aparté, pas comme une règle). Coût :
  réécrire les blocs de `dette.md`, `contrat.md`, `cloture.md`, `debt-review/SKILL.md`, et perdre
  le repérage mécanique ;
- **restaurer les blocs cités dans `list-dir`** — non cassant pour le reste du dépôt, mais annule
  une décision de brief prise en connaissance de cause.

Une troisième voie existe : écrire que les deux formes sont admises et dire **à quoi** chacune
sert — le bloc cité pour un mode de défaillance qui ne se rattache à aucun exemple, l'intégration
quand il en illustre un. C'est la seule qui n'impose aucune réécriture.

Quelle que soit la voie, l'écrire dans `skills/implementation-tracker/references/contrat.md`, qui
porte déjà les conventions de rédaction communes.

## Assumé

<OPTIONNEL>
