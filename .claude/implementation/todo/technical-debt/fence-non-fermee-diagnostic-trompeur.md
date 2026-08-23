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

Signaler la fence **à sa source**, dans `validate` : une section dont un bloc de code reste ouvert
est un manquement nommé, détecté à l'écriture de l'élément plutôt qu'à l'agglomération.
`outside_fences` rend déjà l'information — il suffit qu'elle dise, en fin de parcours, si un bloc
est resté ouvert.

Solde établi par : un élément à fence ouverte → `validate` code ≠ 0 avec un message nommant la
section et la fence ; et le cas ci-dessus ne parvient plus jusqu'à `merge`.

## Assumé

<OPTIONNEL>
