---
slug: format-registres
titre: Répertoires-listes — format de données manipulable par script
statut: validé
execution: direct
créé: 2026-08-19
---

## Intention

**Symptôme** : « les fichiers de suivi à long terme utilisent du Markdown (les dettes, par
exemple). Ce format ne convient pas à l'utilisation de scripts et est difficile à maintenir quand
il représente une liste » (dit).

**But** : « un moyen de représenter des données qui soit facilement manipulable par script » (dit),
dans « la solution la plus généraliste » (dit). Forme retenue : le **répertoire-liste** — un
répertoire = une liste, un fichier = un élément, « avec une interface commune pour les
manipuler » (dit), portée par un skill « pour pouvoir le déployer dans n'importe quelle
situation » (dit). Chaque répertoire-liste embarque « un fichier qui servira de contrat sur la
structure des données et le front matter » (dit).

**Principe directeur** : « le modèle n'est plus responsable de la structure des données ; il fait
tout ce que les scripts ne sont pas capables de faire » (dit). Les fichiers préstructurés sont le
moyen : « ce système doit limiter le risque de dérive » (dit).

## Critères de réussite

Cas d'usage de référence, à faire tenir de bout en bout — les trois étapes de `debt-review` telles
que dites : un script crée un répertoire-liste de revue dans `done/revues/`, fichiers préremplis à
sections préétablies ; le modèle lit les dettes et complète ces fichiers ; un script agglomère tous
les éléments dans un fichier final.

- une revue complète des 17 entrées actives tourne sur ce flux, et le fichier aggloméré est
  archivé sous `done/revues/<date>-revue.md`
- la commande de validation passe sur les quatre répertoires-listes (dette active, soldée, écartée,
  revue) et échoue sur un élément dont un champ du contrat manque
- un élément déplacé reste suivi : après un solde, `git log --follow` sur le fichier de la liste
  d'arrivée remonte jusqu'à son commit de création dans la liste de départ
- conservation vérifiée par commande : autant d'éléments agglomérés que d'éléments dans le
  répertoire, l'écart faisant échouer
- le skill générique ne connaît aucun de ses consommateurs :
  `grep -ril 'dette\|debt' skills/<skill>/` → aucun résultat
- un script dont un outil déclaré manque sort non nul en le nommant, éprouvé par injection et la
  sortie recopiée dans le rapport d'audit
- `skills/debt-review/scripts/trier-revue.sh` est supprimé, ses garanties reprises par les
  commandes génériques
- les commandes n'importent que la stdlib : aucun `import` d'un module tiers dans les fichiers
  livrés
- `scripts/check-pipeline.sh` passe au vert

## Hors-périmètre

- **La visualisation de la liste dans Neovim** : « ce sujet devra faire l'objet de sa propre
  discussion ; beaucoup d'options sont possibles » (dit). Ce chantier doit seulement ne pas la
  rendre impossible.
- **`road-map.md`** : annoncée dans `todo/README.md` mais inexistante (dépôt: fichier absent) —
  rien à migrer.
- **Les autres registres du pipeline** : briefs, suivis, rapports d'audit restent tels quels.

## Signaux de dérive

- si je crée, déplace ou renomme à la main un fichier d'un répertoire-liste, c'est raté — c'est le
  travail du script (dit)
- si un script se met à juger — choisir une catégorie, décider d'un solde — la ligne est franchie
  dans l'autre sens (dit)
- si un commit mêle le déplacement d'un élément et la réécriture de son contenu, la détection de
  renommage lâche et la traçabilité est perdue (dit)
- si une vue dérivée devient éditable, la source unique est perdue (dit)
- si le skill générique doit connaître la dette pour fonctionner, la généralité annoncée est perdue
  (dit)
- si le diff dépasse la réécriture de `debt-review` et des registres, s'arrêter et en reparler

## Contraintes connues de l'utilisateur

- **Partage des rôles, arrêté** : « les scripts font tout, sauf le jugement et la correction :
  créer, rechercher, déplacer, valider la structure ; le script doit vérifier que les arguments
  utilisés sont valides pour un répertoire-liste donné » (dit)
- **Correction de contenu à la main** : « le modèle peut directement écrire dans un fichier pour
  corriger le contenu d'une section ; utiliser un script ici serait trop contraignant » (dit)
- **Déplacement** : « c'est surtout un suivi Git » et « la traçabilité avec Git doit être
  conservée » (dit) — l'état d'un élément reste porté par son répertoire, pas par un champ, et
  l'historique doit montrer un renommage, jamais une suppression suivie d'une création
- **Source unique** : « il faut respecter le principe de la source unique » (dit)
- **Commandes spécifiques** : elles vivent dans le répertoire-liste, à côté du contrat (arbitré)
- **Noms de commandes en anglais** (dit) — les verbes cités en français au fil des échanges
  (`créer`, `dériver`, `déplacer`, `valider`, `filtrer`, `agglomérer`) sont des intentions, pas des
  noms ; le plan les nomme
- **Chaque commande porte une description**, affichée par `help` (dit) — donc déclarée quelque part
  que `help` sait lire sans exécuter la commande, y compris pour les commandes spécifiques d'un
  répertoire-liste
- **Dépendance déclarée absente → échec fermé**, sortie non nulle nommant l'outil (arbitré)
- **Langage des commandes : Python 3, stdlib seule** (arbitré) — disponible en 3.13 système et 3.14
  linuxbrew indépendamment (dépôt: mesuré le 2026-08-19). Les hooks restent en bash.
- **`yq`** : l'arbitrage subsiste mais son enjeu tombe — avec `tomllib`/`json` en stdlib, la charge
  de la preuve passe du côté de `yq`, qui doit démontrer ce qu'il apporte de plus (arbitré)
- **Outillage inconnu de l'utilisateur** : « je n'ai jamais utilisé yq/jq » — la solution doit rester
  lisible sans les connaître (dit)
- **État de l'outillage** : `yq`, `jq`, `PyYAML` absents ; `python3` 3.14 avec `json`, `tomllib`
  (lecture seule), `csv` (dépôt: mesuré le 2026-08-19)
- **Précédent de dépendance non déclarée** : `hooks/intent-brief-gate.sh` garde sur `jq`, absent —
  le hook sort 0 sans message et le gate n'a jamais bloqué (dépôt: hooks/intent-brief-gate.sh,
  ligne `if command -v jq`)
- **Volume à migrer** : 17 entrées actives, 7 soldées, `technical-debt-ecarte.md` inexistant
  (dépôt: mesuré le 2026-08-19)

## Incertitudes à lever en plan

- **L'écriture directe du modèle contourne la validation de structure** : à quel moment la
  validation repasse-t-elle, et est-elle assez bon marché pour être systématique.
- **Portée de `rechercher`** : filtrer sur les champs déclarés au contrat, ou recherche plein texte
  — le second referait un `grep` en moins bien.
- **Format du contrat embarqué** : lu par Python, donc `tomllib`, `json` ou un format plat sont
  tous ouverts — reste à choisir, en tenant compte qu'il doit aussi rester éditable à la main et
  porter les descriptions que `help` affiche.
- **Liste exhaustive des commandes génériques** : `créer`, `dériver`, `déplacer`, `valider`,
  `filtrer`, `agglomérer` et `help` sont acquises comme intentions ; le « etc. » reste à borner, et
  les noms anglais restent à choisir. `help` « liste les commandes disponibles » (dit) — donc les
  génériques **et** celles du répertoire-liste visé, avec leur description : c'est le seul point
  d'où l'interface complète se découvre.

