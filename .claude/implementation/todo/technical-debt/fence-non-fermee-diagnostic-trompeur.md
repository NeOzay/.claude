+++
id = "fence-non-fermee-diagnostic-trompeur"
title = "Une fence non refermée avale les sections suivantes, et les deux messages qui en découlent sont faux"
date = 2026-08-23
source = "chantier `format-registres`, R22 et R25 des audits de clôture"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Un bloc de code ouvert et jamais refermé fait disparaître tout `## ` postérieur — comportement
conforme à CommonMark, et l'aller-retour reste exact. Mais il produit deux diagnostics faux, et
aucun ne mentionne la fence.

**Versant `validate`** : si la section avalée est requise, le message est « section manquante » sur
une section qui est pourtant écrite dans le fichier, sous les yeux du lecteur.

**Versant `merge`**, mesuré sur trois éléments dont le premier porte une fence ouverte :

```
$ list-dir.py validate t25 --filled
t25 : 3 élément(s) remplis et conformes au contrat        code 0
$ list-dir.py merge t25 --out o.md
t25: 1 élément(s) dans le document pour 3 fichier(s) dans le répertoire
     — un élément a été perdu ou dédoublé en route        code 1
```

Rien n'est perdu : le bloc ouvert absorbe les `## ` des éléments suivants.

**Mise à jour du 2026-08-24, chantier `tests-listdir`** — le versant décrit ci-dessus est traité :
`outside_fences` repose désormais sur un `_scan_fences` unique qui expose le bloc encore ouvert, et
`validate` nomme la fence à sa source. Sur le cas exact mesuré plus haut :

```
$ list-dir.py validate t25 --filled
t25/a.md: section « Constat » — bloc de code ouvert par « ``` » et jamais refermé
          — les sections suivantes y sont absorbées                      code 1
```

**Ce qui reste**, et pour quoi cette entrée demeure au registre : le correctif ne voit que les
fences ouvertes **dans** une section. Une fence ouverte **avant le premier `## `** reproduit le
diagnostic faux à l'identique, parce que `parse_sections` ignore ce qui précède le premier titre et
qu'un `Item` ne conserve pas ce préambule :

```
corps = "```\ndu code jamais refermé\n\n## Constat\n\nx\n"
→ item.sections == {}
→ validate : « section « Constat » — manquante »   sur une section écrite dans le fichier
```

Établi par exécution le 2026-08-24 ; `fence_ouverte(corps)` rend bien ``` sur ce même texte, donc
l'information existe — c'est `_check_sections` qui ne la consulte que section par section.

## Pourquoi c'est gênant

L'échec est **fermé** — code ≠ 0, rien d'écrit — et le déclencheur est étroit : du Markdown
malformé, pas ce que le gabarit prescrit. Le coût n'est donc pas la perte de données, c'est le
temps passé à chercher une entrée disparue qui n'a jamais disparu. C'est le même défaut de
diagnostic que R19, corrigée pendant le chantier, sur un déclencheur plus rare.

La cause est structurelle : la règle des fences est appliquée **deux fois** sur le même contenu — à
la lecture de l'élément, puis sur le document aggloméré. C'est voulu (recompter sur le texte rendu
est ce qui permet d'attraper un titre injecté), mais tout contenu qui trompe la règle la trompe
deux fois, en deux endroits aux messages sans rapport.

## Pour solder

Le versant « fence dans une section » est fait (voir la mise à jour du Constat). Reste à couvrir le
**préambule** : `validate` doit voir le corps entier, et non les seules sections découpées. Deux
voies, aucune tranchée :

- `Item` conserve son corps brut, comme il conserve déjà `raw_front` pour la règle 1 — et
  `_check_sections` y applique `fence_ouverte` avant de juger les sections ;
- ou `parse_sections` rend le préambule sous une clé réservée, que `validate` examine sans que le
  contrat ait à le déclarer.

La première touche `types.py`, `items.py` et `store.py` ; la seconde change le contrat d'une
fonction dont deux appelants dépendent. C'est ce coût qui a fait verser le reste au registre plutôt
que le traiter en clôture de `tests-listdir`.

Solde établi par : le corps du Constat ci-dessus (fence en préambule) → `validate` code ≠ 0 avec un
message **nommant la fence**, et non « section manquante ».

## Assumé

<OPTIONNEL>
