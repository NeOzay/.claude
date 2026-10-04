+++
id = "trois-lignes-au-dela-de-100-colonnes"
title = "Trois lignes du corpus dépassent l'enroulement à 100 colonnes"
date = 2026-08-14
source = "Identifié par `contrat-pipeline`, R8 puis R17 du rapport d'audit."
reviewed = 2026-09-06
category = "aggravee"
+++

## Constat

**Mesuré le 2026-09-06 : 157 lignes** du corpus versionné dépassent 100 caractères. Les trois
lignes que l'intitulé nomme sont les plus longues du seul répertoire
`skills/implementation-tracker/references/` — 121, 131 et 140 caractères — mais seize lignes de ce
répertoire dépassent 100. **L'intitulé est donc faux** ; il est conservé tel quel parce qu'il sert
de clé de référence.

Établi par : comptage **en caractères** sur `git ls-files -- skills scripts hooks` filtré
`.md`/`.sh`, via `python3` (`len(l) > 100`) → **157**. En octets, `awk length` en rendrait une
centaine de plus, sur du texte accentué.

**Historique de la mesure** — le Constat d'origine annonçait « trois lignes […] que le reste du
corpus respecte », description sous-mesurée **d'un facteur 44** dès son écriture ; corrigée à
**133** le 2026-08-17 par `revue-dette`. Le passage de 133 à 157, lui, est une **aggravation
réelle** : même corpus, même commande, même unité, **24 lignes de plus** en trois semaines. C'est
l'absence de la seconde décision réclamée ci-dessous qui la produit.

## Soldé le

**2026-10-04, hors chantier** — les deux gestes que **Pour solder** réclamait sont faits. Les trois
lignes nommées sont réenroulées : dans `skills/implementation-tracker/references/`, aucune ligne de
prose ne dépasse plus 100 caractères. Et la seconde décision est prise : l'enroulement à 100
colonnes est une convention, écrite dans `OUTILLAGE.md` (« Formater le Markdown ») et tenue par
`rumdl fmt`, qui réenroule tout paragraphe dont une ligne dépasse (`.rumdl.toml`, section
`[MD013]`). Elle n'est pas tenue par le garde-fou mais par `uvx rumdl fmt --check .`.

La convention exempte délibérément les tableaux, les blocs de code et les titres, qu'on ne coupe
pas sans en changer le sens. Ce qui dépasse encore est de cet ordre, et non un écart à corriger.

Établi par le comptage d'origine, en caractères, sur `git ls-files -- skills scripts hooks` filtré
`.md`/`.sh`, avec chaque ligne classée selon ce qui la porte :

```
$ python3 (len(ligne) > 100, par nature de ligne)
total 50   {'tableau': 40, 'prose': 6, 'front matter': 2, 'bloc de code': 1, '.sh': 1}
implementation-tracker/references : 0 ligne(s) de prose > 100, 3 ligne(s) de tableau > 100

$ uvx rumdl fmt --check .                                    code 0
```

157 lignes le 2026-09-06, 50 aujourd'hui. Les 6 lignes de prose restantes sont chacune un lien
Markdown seul sur sa ligne (`skills/list-dir/references/provenance.md`, « La définition n'est
autorité que le temps de l'`init` », par exemple), qu'on ne peut pas couper sans le casser. La ligne
`.sh` est la condition `find` de `hooks/intent-brief-gate.sh` : le shell n'est couvert par aucun
formateur du dépôt.

## Pourquoi c'est gênant

le respect du style des fichiers voisins est un axe de jugement de
l'auditeur, et le contrat est le fichier destiné à être le plus relu du pipeline. Mais à 133 lignes,
ce n'est plus une anomalie ponctuelle : c'est l'absence de convention outillée.

## Pour solder

ré-enrouler les trois lignes nommées, qui est le geste d'origine ; puis décider
séparément si le reste du corpus relève d'une convention à écrire — et à faire tenir par le
garde-fou — ou d'un état accepté. Sans cette seconde décision, l'entrée reviendra.

## Assumé

<OPTIONNEL>
