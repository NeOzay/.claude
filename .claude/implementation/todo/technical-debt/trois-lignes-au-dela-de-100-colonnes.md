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
