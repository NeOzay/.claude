+++
id = "gabarit-new-usage-ecrit-a-la-main"
title = "L'usage de `gabarit new` est une chaîne écrite à la main, que rien ne confronte à ses arguments"
date = 2026-09-15
source = "chantier fichier-seme, audit de clôture R7 (`5123a3d`) — clos avec"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Pour que le refus « nom ou --from, pas les deux » soit atteint quel que soit l'ordre des
arguments, `gabarit-cli.py` analyse `new` par un parseur autonome en mode entremêlé
(`parse_intermixed_args`, incompatible avec les sous-commandes). Ce parseur porte une chaîne
`usage="gabarit new <nom> <fichier> | --from <chemin> <fichier>"` écrite à la main, et le texte
d'aide du sous-parseur (« crée un fichier prérempli… ») n'apparaît pas dans `gabarit new --help`.

## Pourquoi c'est gênant

Ajouter une option à `new` sans retoucher la chaîne fait mentir l'aide, sans qu'aucun test ni
aucune commande n'échoue. Le coût est faible tant que `new` n'a qu'une option.

## Pour solder

Dériver l'usage des arguments déclarés (ou le tester) : un test qui lance `gabarit new --help` et
vérifie qu'il nomme chaque option déclarée par `_options_new`, ou supprimer `usage=` au profit de
l'usage généré. Vérifier : `.venv/bin/python -m pytest skills/gabarit/scripts/tests -q` avec ce test
présent.

## Assumé

Clos avec, le 2026-09-15, au second audit de clôture : défaut sans échec ouvert, toute erreur
d'appel sortant en code 2.
