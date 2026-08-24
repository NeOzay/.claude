+++
id = "table-empreintes-a-la-main"
title = "La table d'empreintes du garde-fou est maintenue à la main"
date = 2026-08-14
source = "Identifié par `contrat-pipeline`, R9 du rapport d'audit."
reviewed = 2026-08-17
category = "pertinent"
+++

## Constat

le contrôle 2 de `check-pipeline.sh` repose sur une liste `fingerprints` de huit
motifs, une par section du contrat. Rien ne vérifie qu'elle reste complète : une huitième règle
ajoutée au contrat sans son empreinte n'est protégée par rien, et le contrôle « section jamais
citée » ne détecte que l'absence de renvoi, pas l'absence d'empreinte.

## Soldé le

**Soldé le 2026-08-24 par le chantier `check-pipeline-python`** — la liste plate est devenue une
table `{ancre-de-section: (empreintes…)}`. Trois nouvelles issues rouges : une section du contrat
sans empreinte, une empreinte dont la section a disparu, et une empreinte trouvée **hors de la
section qu'elle protège**. `## Dépendances`, seule section non couverte à ce jour, a reçu son
empreinte (« elle ne se suppose pas », `contrat.md:238`).

Le **Pour solder** avertissait qu'« une règle par section n'est pas la réalité du fichier » :
`#arborescence-et-nommage` en porte bien deux, et la table est un `dict` de tuples pour cette
raison.

Établi par : `python3 scripts/check_pipeline.py` → contrôle 2, **9 empreintes vertes pour 8
sections** ; `test_section_sans_empreinte`, `test_empreinte_orpheline`,
`test_motif_hors_de_sa_section`.

## Pourquoi c'est gênant

le journal du chantier pose la règle (« toute règle ajoutée au contrat
doit recevoir son empreinte »), mais une règle qui repose sur la mémoire de son auteur est
précisément ce que ce chantier existe pour supprimer.

## Pour solder

un contrôle qui rattache **chaque empreinte à la section qu'elle protège**, et qui
échoue sur une section sans empreinte. Une règle par section n'est pas la réalité du fichier :
plusieurs sections en portent deux.

**Corrigé le 2026-08-17 par `revue-dette`** — le **Pour solder** disait « autant d'empreintes que de
sections `##` dans le contrat ». Ce contrôle aurait échoué à son premier lancement, sur un dépôt
sain, et le correctif consistait alors à **retirer** une empreinte légitime.
Établi par : `sed -n '/^fingerprints=(/,/^)/p' scripts/check-pipeline.sh | grep -c "^  '"` → 8, et
`grep -c '^## ' skills/implementation-tracker/references/contrat.md` → 7.

## Assumé

<OPTIONNEL>
