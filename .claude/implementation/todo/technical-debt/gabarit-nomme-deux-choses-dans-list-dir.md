+++
id = "gabarit-nomme-deux-choses-dans-list-dir"
title = "« gabarit » nomme à la fois les modèles de `derive` et le paquet dont list-dir dépend"
date = 2026-09-15
source = "chantier fichier-seme, audit de clôture R8 (`5123a3d`) — clos avec"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

La documentation de list-dir appelle « gabarit » les paires `.list/templates/<nom>.{toml,md}`
projetées par `derive` (`references/operations.md`, section de `derive` ; `--template` ; les noms
composites `mère/dérivée`). Le chantier `fichier-seme` a donné le même nom au skill et au paquet
Python dont list-dir dépend désormais (`skills/gabarit/`).

## Pourquoi c'est gênant

Tant que list-dir ne documente pas sa dépendance, les deux sens ne se croisent pas. Le jour où
elle le fera (`list-dir-depend-de-gabarit-sans-le-dire`), un lecteur trouvera « gabarit » pour deux
choses sans rapport direct, dans la même documentation — et le code de list-dir emploie aussi
`gabarit` comme nom de variable pour un modèle de `derive`.

## Pour solder

Trancher avec l'utilisateur : renommer l'un des deux sens (par exemple « modèle de dérivation »
pour `templates/`), ou poser dans `references/operations.md` une phrase qui distingue explicitement
les deux. Vérifier par `grep -rn 'gabarit' skills/list-dir/references skills/list-dir/SKILL.md` que
chaque occurrence restante désigne sans ambiguïté l'un des deux.

## Assumé

Le nom a été choisi par l'utilisateur au cadrage (« je penche pour gabarit »). Clos avec, le
2026-09-15 : pas un défaut du chantier, une collision à régler quand la documentation de list-dir
bougera.
