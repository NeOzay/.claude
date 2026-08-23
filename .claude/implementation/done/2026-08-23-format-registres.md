---
slug: format-registres
titre: Répertoires-listes — format de données manipulable par script
branche: format-registres
base: master
statut: terminé
session: 2
execution: direct
plan: .claude/implementation/done/2026-08-23-format-registres.plan.md
brief: .claude/implementation/done/2026-08-23-format-registres.brief.md
audit: .claude/implementation/done/2026-08-23-format-registres.audit.md
créé: 2026-08-20
maj: 2026-08-23
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : « les fichiers de suivi à long terme utilisent du Markdown (les dettes, par exemple).
Ce format ne convient pas à l'utilisation de scripts et est difficile à maintenir quand il
représente une liste ».

**But** : « un moyen de représenter des données qui soit facilement manipulable par script », dans
« la solution la plus généraliste ». Forme retenue : le **répertoire-liste** — un répertoire = une
liste, un fichier = un élément, « avec une interface commune pour les manipuler », portée par un
skill « pour pouvoir le déployer dans n'importe quelle situation ». Chaque répertoire-liste embarque
« un fichier qui servira de contrat sur la structure des données et le front matter ».

**Principe directeur** : « le modèle n'est plus responsable de la structure des données ; il fait
tout ce que les scripts ne sont pas capables de faire ».

**Critères de réussite** — cas d'usage de référence : les trois étapes de `debt-review`, un script
crée un répertoire-liste de revue, le modèle complète les fiches, un script agglomère.

- une revue complète des 17 entrées actives tourne sur ce flux, et le fichier aggloméré est archivé
  sous `done/revues/<date>-revue.md`
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
- `skills/debt-review/scripts/trier-revue.sh` est supprimé, ses garanties reprises par les commandes
  génériques
- les commandes n'importent que la stdlib
- `scripts/check-pipeline.sh` passe au vert

**Hors-périmètre** : la visualisation de la liste dans Neovim (sujet à part) ; `road-map.md`
(inexistante, rien à migrer) ; les autres registres du pipeline — briefs, suivis, rapports d'audit —
qui restent des documents.

**Élargissement du périmètre, 2026-08-22** — sur décision de l'utilisateur, l'étape 14 ne supprime
plus `technical-debt.md`, `technical-debt-solde.md` ni `scripts/migrate-dette.py` : ils servent à
l'audit du chantier, qui doit pouvoir confronter la migration à sa source. Leur suppression devient
un point de la clôture. `todo/README.md` les déclare **figés et périmés**, l'autorité passant aux
listes — sans quoi le dépôt porterait deux registres divergents, ce que le brief interdit.

**Élargissement du périmètre, ratifié le 2026-08-23** — sur décision de l'utilisateur, deux
fichiers de configuration hors de « `debt-review` et les registres » restent au chantier :
`pyrightconfig.json` à la racine (mode `recommended`, `include: skills`, `extraPaths` vers le
paquet) et trois lignes de `.gitignore` (`__pycache__/`, `.ruff_cache/`). R4 de l'audit
intermédiaire, qui relevait à juste titre que le signal de dérive s'était déclenché sans qu'on en
reparle. Motif : le chantier introduit le premier code Python versionné du dépôt, qui n'a de
vérification typée qu'à cette condition — et sans les deux lignes d'ignore, ses artefacts entrent
dans chaque `git status`.

**Écart au brief, ratifié le 2026-08-20** : l'archive réelle sous `done/revues/<date>-revue.md`
n'est pas produite par ce chantier. L'étape 16 démontre le flux et la conservation sur les 17
entrées avec un contenu de recette, sans rien commiter sous `done/revues/` ; le jugement, et donc
l'archive, appartiennent à la première revue post-clôture.

**Signaux de dérive** :

- si je crée, déplace ou renomme à la main un fichier d'un répertoire-liste, c'est raté — c'est le
  travail du script
- si un script se met à juger — choisir une catégorie, décider d'un solde — la ligne est franchie
  dans l'autre sens
- si un commit mêle le déplacement d'un élément et la réécriture de son contenu, la détection de
  renommage lâche et la traçabilité est perdue
- si une vue dérivée devient éditable, la source unique est perdue
- si le skill générique doit connaître la dette pour fonctionner, la généralité annoncée est perdue
- si le diff dépasse la réécriture de `debt-review` et des registres, s'arrêter et en reparler

## Étapes

- [x] 1. Squelette du skill et contrat de format — `skills/list-dir/SKILL.md`, `references/contrat-liste.md` — vérif: `bash scripts/check-pipeline.sh` + greps du plan
- [x] 2. `listdir/types.py` : `Result[T]`, `Item`, `Contract`, `Violation`, `PLACEHOLDER`, `OPTIONAL`, protocoles — vérif: construction d'un `Result`, unicité des deux marqueurs
- [x] 3. `listdir/items.py` et `contract.py` : front matter TOML, bloc brut, `render()`, sérialiseur borné — vérif: aller-retour octet pour octet, resérialisation après `with_fields`
- [x] 4. `listdir/store.py` et `__init__.py` : `open_list`, `items`, `get`, `where`, `create`, `write` — vérif: script du scratchpad amorcé par la forme canonique
- [x] 5. `listdir/loader.py` et `list-dir.py` : découverte, surcharges, `REQUIRES`, dispatch — vérif: injection d'un outil absent → code ≠ 0 le nommant
- [x] 6. `init`, `new`, `show` — `listdir/commands/` — vérif: 5 `<À REMPLIR>` et 2 `<OPTIONNEL>` sur le contrat d'exemple
- [x] 7. `validate` et `validate --filled` — vérif: champ requis retiré → code ≠ 0 ; l'optionnel jamais réclamé
- [x] 8. `list --where --sort` — vérif: champ inconnu → code ≠ 0 le nommant
- [x] 9. `move` — vérif: dépôt jetable, `R` au status puis `git log --follow` remonte au commit de création
- [x] 10. `derive` et `merge` — vérif: contrat posé, `from` reporté, conservation rompue → code ≠ 0
- [x] 11. `help` par `ast.parse` — vérif: 9 commandes, `(surchargée)`, module invalide sans effet
- [x] 12. `migrate` : remise en conformité quand le contrat change — vérif: contrat remanié → champ et sections posés au marqueur, ordre repris, rejeu sans écriture
- [x] 13. Les trois listes permanentes : migration des 24 entrées + `technical-debt-ecarte/` vide — vérif: 24/24, `validate` vert sur les trois
- [x] 14. Réécriture de `dette.md` et `todo/README.md` ; anciens `.md` et script **conservés pour l'audit** — vérif: `check-pipeline.sh` + commit de session
- [x] 15. Paire de gabarits `review.{toml,md}` — vérif: `derive --template review` rend une liste que `validate` accepte
- [x] 16. Refonte de `debt-review` (SKILL, gabarit-rapport, **categories, exemple-revue**), suppression de `trier-revue.sh` — vérif: `git ls-files` ne le contient plus
- [x] 17. **R7 de l'audit** — report des verdicts de la revue du 2026-08-17 sur les 11 entrées `pertinent` — vérif: 14 `reviewed` renseignés, 3 au marqueur, `validate --filled` vert, diff borné aux deux champs
- [x] 18. **R1 de l'audit** — la complétude d'une revue se contrôle contre le registre, pas contre `merge` — vérif: 16 fiches sur 17 → `merge` code 0, le contrôle rouge
- [x] 19. Revue à blanc de bout en bout sur les 17 entrées — vérif: 17 fiches, `--filled` rouge puis vert, aggloméré à 17 blocs
- [x] 20. `cloture.md` et `contrat.md` du tracker, **section _Dépendances_ créée** — vérif: `bash scripts/check-pipeline.sh`
- [x] 21. Contrôle 6 de `check-pipeline.sh` étendu aux appels `python3` — vérif: injection d'un appel non gardé → contrôle 6 rouge
- [x] 22. Passe de vérification d'ensemble, **contrôles du plan corrigés au passage** (R11) — vérif: section *Vérification* du plan, intégralement
- [x] 23. **R9 de l'audit de clôture** — `init` sérialise `--name` et `--description` au lieu de les interpoler — vérif: `--name 'ma "liste"'` → contrat valide, `validate` code 0
- [x] 25. **R19, bloquant** — `merge_text` recompte hors blocs de code, par la même règle que `parse_sections` — vérif: fiche portant une sortie de commande → `merge` code 0, préambule juste
- [x] 26. **R20** — `dump_value` échappe sauts de ligne et tabulations, refuse les autres caractères de contrôle — vérif: aller-retour `tomllib` sur 4 valeurs, `\x07` → `SerialiseError`
- [x] 27. **R21** — une clôture de bloc ne porte pas d'info string — vérif: ```` ```python ```` dans un bloc ouvert reste du contenu
- [x] 28. **Clôture** — R17 corrigée, R16 exécutée (anciens `.md` et `migrate-dette.py` supprimés), 6 constats versés au registre — vérif: `validate --filled` vert sur 24 entrées, `check-pipeline.sh` code 0
- [x] 24. **R6 de l'audit de clôture** — un `## ` dans un bloc de code n'ouvre plus de section — vérif: sortie de commande collée dans `Constat` → `validate` code 0, une seule section lue, round-trip exact

## État courant

**Chantier terminé.** Les 22 étapes du plan, plus 6 étapes correctives nées des audits.
**Dernier audit** : `b9ca3e6` — RÉSERVES — 2026-08-23 (clôture, 3e passe) — **aucun bloquant**.
**Vérification** : section *Vérification* du plan, 13 contrôles, tous verts.

**Constats versés au registre à la clôture** — R2, R5, R8, R10, R15, R22+R25 :
`revue-reelle-jamais-menee`, `marqueurs-recopies-dans-gabarits`, `source-verbatim-perd-italiques`,
`where-compare-textuellement`, `controle-completude-revue-sans-code-sortie`,
`fence-non-fermee-diagnostic-trompeur`. Plus `listdir-sans-suite-de-tests`, versée le 2026-08-23 sur
demande de l'utilisateur, hors du point 2. R17 a été corrigée dans ce fichier plutôt que versée :
c'était une phrase fausse, pas une dette.

**Reste hors périmètre, non versé** : 3 erreurs `ruff` dans `statusline-command.py`, fichier
étranger au chantier. Trois entrées anciennes du registre (`sortie-du-registre-jamais-exercee`,
`quatre-trous-procedure-debt-review`, `etape-corrective-cochee-avant-audit`) citent les `.md`
supprimés à cette clôture : leurs preuves ne se rejouent plus et sont à corriger **en revue**, pas
ici — c'est du contenu de registre.

## Journal de décisions

- **2026-08-23** — **R19** : `outside_fences` devient la **source unique** de la règle des blocs de
  code, dans `items.py` ; `parse_sections` et `merge_text` s'en servent tous deux. *Pourquoi* : les
  deux avaient divergé — le parsing savait, le recomptage non — et c'est cette divergence qui a
  produit un faux positif au message faux. *Rejeté* : recopier la boucle dans `store.py`, qui aurait
  reconduit exactement le défaut qu'on corrige.
- **2026-08-23** — **conséquence documentaire de R19** : `grep -c '^## '` **cesse d'être** une
  commande de contrôle de la conservation, et le compte qui fait foi est celui du préambule.
  *Pourquoi* : un grep à la main compte les `## ` d'une sortie collée, c'est-à-dire précisément le
  contenu que `debt-review` demande d'écrire. Corrigé dans `contrat-liste.md`, `gabarit-rapport.md`
  et le plan.
- **2026-08-23** — **R20** : `dump_value` échappe `\n`, `\r`, `\t`, `\b`, `\f` et **refuse** tout
  autre caractère de contrôle. *Pourquoi* : n'échapper que `\` et `"` laissait un saut de ligne
  fermer la chaîne, et `migrate` détruisait un élément valide en rendant 0. *Effet* : R9 n'avait
  traité que le symptôme (`init`) ; la cause était le sérialiseur.

- **2026-08-23** — une entrée de dette est versée **hors** du point 2 de la clôture, sur demande
  explicite de l'utilisateur : `listdir-sans-suite-de-tests`. *Pourquoi* : la question « existe-t-il
  une suite de tests » n'a pas de réponse dans le dépôt, et aucun audit ne l'avait relevée.
  *Conséquence* : le point 2 de la clôture ne doit **pas** la réécrire — le registre est un état,
  pas un journal.

- **2026-08-23** — **R9** : les deux valeurs libres d'`init` passent par `dump_value`, jamais par
  une interpolation. *Pourquoi* : `--name 'ma "liste"'` produisait un contrat que `tomllib` refuse,
  et `init` rendait **0** — un échec ouvert, ce que ce paquet existe pour supprimer. *Effet* : le
  sérialiseur borné devient le seul chemin d'écriture TOML du paquet, sans exception.
- **2026-08-23** — **R6** : `parse_sections` suit les fences au sens CommonMark et ignore les `## `
  qu'elles contiennent. *Pourquoi* : toute preuve exécutée colle une sortie de commande, où un `## `
  ouvrait une section fantôme que `validate` refusait — le format se retournait contre la règle de
  preuve qu'il sert. *Détail* : clôture par le même caractère répété au moins autant de fois, pour
  qu'un bloc puisse en contenir un plus court.

- **2026-08-23** — **R11** : les cinq contrôles faux du plan sont corrigés **dans le plan**, pas
  contournés à l'exécution. *Pourquoi* : un contrôle rouge sur du code conforme finit par faire
  corriger le code. *Détail* : allowlist stdlib complétée (`__future__`, `collections`) ; `open(`
  précisé pour ne plus attraper `utils.open(` ; le comptage de marqueurs porte sur la **définition**
  et non sur la prose ; `help` attend **10** commandes depuis `migrate` ; le script de recette perd
  son `IndexError` et le retrait de fiche se contrôle contre le registre (R1).

- **2026-08-23** — `typeCheckingMode` passe à **`all`** dans les deux configurations, sur demande de
  l'utilisateur ; les trois exemptions (`reportImplicitStringConcatenation`, `reportUnusedCallResult`,
  `reportImportCycles`) sont **maintenues**. *Pourquoi* : sous basedpyright la hiérarchie est
  `strict < recommended < all`, donc « strict » à la lettre aurait été une régression. *Mesuré* :
  0 erreur en `all` sur 19 fichiers ; 51 erreurs si les trois exemptions tombent, essentiellement
  du bruit stylistique.

- **2026-08-23** — **R4 ratifiée** : `pyrightconfig.json` et les deux lignes d'ignore restent au
  chantier, périmètre élargi en conséquence. *Pourquoi* : le chantier apporte le premier code Python
  versionné du dépôt, et sa vérification typée n'existe qu'à cette condition. *Rejeté* : les sortir
  du chantier, qui aurait laissé le paquet sans configuration d'outillage et les caches dans
  `git status`.

- **2026-08-23** — **R12** : la section *Dépendances* du contrat déclare `list-dir`, Python ≥ 3.12
  et `git`, avec le contrôle de chacun. *Pourquoi* : le pipeline dépendait d'un skill externe sans
  l'écrire nulle part, et le contrôle 1 du garde-fou exige qu'une section du contrat soit citée —
  le renvoi part de `dette.md`, qui en est le premier consommateur. *Effet* : `cloture.md` et
  `contrat.md` ne nomment plus aucun `technical-debt*.md`.

- **2026-08-23** — **R1** : la complétude d'une revue se contrôle **contre le registre**, avant
  `merge`, et non par le préambule de l'aggloméré. *Pourquoi* : `merge` compare les blocs rendus aux
  fichiers présents, deux comptes qu'une fiche supprimée réduit ensemble — mesuré, 16 sur 17 sort 0.
  *Rejeté* : une option `merge --expect <n>`, qui aurait fait porter au générique un compte que seul
  le consommateur connaît.
- **2026-08-23** — **R7** : les 11 entrées classées `pertinent` le 2026-08-17 reçoivent `reviewed`
  et `category` rétroactivement. *Pourquoi* : l'ancien format n'écrivait rien pour cette catégorie,
  si bien que la migration les laissait à `<OPTIONNEL>` — que `dette.md` lit comme « jamais
  confrontée au dépôt », l'inverse de la vérité. *Effet* : 14 entrées revues, 3 au marqueur — celles
  nées de cette revue même.

- **2026-08-23** — la refonte de `debt-review` a repris **quatre** fichiers, non deux : le plan ne
  citait que `SKILL.md` et `gabarit-rapport.md`, mais `categories.md` nommait encore
  `technical-debt-solde.md` en destination et le marqueur `(aggravée) <date>` sous le titre, et
  `exemple-revue.md` n'était que le jeu de test du script supprimé. *Pourquoi* : les laisser aurait
  livré un skill dont la moitié des références décrit un format qui n'existe plus. *Effet* :
  `exemple-revue.md` devient sept fiches instruites, une par catégorie, plus une fiche arbitrée.
- **2026-08-23** — l'ordre des piles du rapport est porté par **une énumération écrite dans le
  SKILL**, pas par `--sort category`. *Pourquoi* : `_key` compare les valeurs sous forme textuelle,
  donc un tri rendrait l'ordre alphabétique et non « ce qui sort du registre d'abord ».
  *Rejeté* : un ordre déclaré au contrat, qui aurait fait porter au skill générique une sémantique
  de la revue.
- **2026-08-23** — le SKILL **propose** le commit du déplacement, il ne le lance pas. *Pourquoi* :
  `CLAUDE.md` interdit tout commit sans accord explicite, et la traçabilité de `move` exige pourtant
  un commit du seul renommage. *Effet* : la contrainte se règle par un point d'arrêt, pas par une
  exception.

- **2026-08-23** — le corps d'une section de gabarit est **exactement** le marqueur ; les consignes
  de remplissage vivent dans le préambule du `.md`, que `derive` ignore. *Pourquoi* : `_check_sections`
  compare le corps strippé au marqueur, donc une consigne écrite sous lui ferait passer une fiche
  vierge pour instruite. *Effet* : la règle vaut pour tout gabarit futur, pas seulement `review`.
- **2026-08-23** — la fiche de revue nomme son verdict `category`, comme le champ du contrat de
  dette. *Pourquoi* : `debt-review` le reportera tel quel au registre, et un nom différent aurait
  demandé une table de correspondance. *Effet* : la section `Verdict` porte le raisonnement, le
  champ `category` la catégorie — deux choses distinctes sous deux noms distincts.

- **2026-08-22** — la ligne unique « Dernière vérification » disparaît, remplacée par les champs
  `reviewed` et `category` de **chaque** entrée. *Pourquoi* : il n'y a plus de fichier unique où la
  poser, et le per-entrée dit davantage — `list --sort reviewed` montre ce qui n'a jamais été
  confronté au dépôt. *Effet* : `debt-review` écrira deux champs au lieu d'une ligne de prose.

- **2026-08-22** — le jugement de la migration est **écrit dans le script** : table des 24 slugs,
  table des intitulés réels vers les sections du contrat, table des verdicts de revue. *Pourquoi* :
  aucune heuristique ne tire `filtres-listing-hook-rtk` d'un titre, ni ne sait que « Pourquoi
  c'était gênant » est la même section au passé. *Effet* : le script fait la structure, et ce qu'il
  ne pouvait pas décider est lisible en un endroit.
- **2026-08-22** — un intitulé hors table est **conservé verbatim et rattaché à la section ouverte
  au-dessus**. *Pourquoi* : un addendum daté (« Élargi le … », « Corrigé le … ») appartient à ce
  qu'il amende ; lui inventer une section serait le reclasser. *Effet* : 108 blocs sur 108 se
  retrouvent à l'octet près dans le `.md` d'origine.
- **2026-08-22** — les contrats des listes soldée et écartée rendent `Pourquoi c'est gênant` et
  `Pour solder` **facultatives**, et exigent `Soldé le` / `Écartée le`. *Pourquoi* : trois entrées
  soldées n'ont jamais porté l'une ou l'autre, et ce qu'une entrée sortie du registre doit prouver
  est son motif, pas son plan de solde. *Rejeté* : compléter les entrées au marqueur, qui aurait
  fabriqué de la dette à remplir sur du travail déjà fait.
- **2026-08-22** — deux champs non prévus au plan : `source` (la ligne *Identifié par …* verbatim)
  et `reviewed` (date du dernier verdict de revue, qui accompagnait `category`). *Pourquoi* : sans
  eux, ces textes n'avaient d'autre place qu'une section, où ils se seraient lus comme de la prose.
  *Rejeté* : le champ `refs` du plan — extraire « R8 à R11 » d'une phrase demande de juger.

- **2026-08-22** — **élargissement de périmètre** : une dixième commande générique, `migrate`,
  remet les éléments en conformité quand le contrat change. *Pourquoi* : rien ne couvrait le cas,
  et la seule issue restante — éditer les fichiers à la main — déclenche un signal de dérive du
  brief. Constaté par l'utilisateur avant l'étape des 24 entrées, qui en est le premier usage réel.
- **2026-08-22** — `migrate` complète, réordonne, et **ne renomme ni ne reporte rien** ; un champ
  hors contrat est conservé et signalé, `--drop` le retire sur ordre. *Pourquoi* : décider qu'un
  champ disparu est devenu un autre est un jugement, et supprimer une donnée non relue aussi.
  *Effet* : `migrate` rejoint `validate` et `help` dans `PROTECTED` — elle réécrit au nom du contrat.
- **2026-08-22** — une remarque (`applied=False`) ne déclenche aucune écriture, et `Item.realigned`
  remplace au lieu de fusionner. *Pourquoi* : sans la première, un rejeu réécrivait tout et perdait
  les `raw_front` pour rien ; sans la seconde, `with_fields` ne sait ni retirer ni réordonner.

- **2026-08-21** — `help` porte la mention `(surchargée)` sur la commande DE LA LISTE qui masque
  une générique, et non sur la générique masquée — qui disparaît de sa section. *Pourquoi* :
  c'est la commande réellement appelable qu'on lit, et la mention dit d'où vient la surprise.

- **2026-08-21** — `derive` construit tout en mémoire avant la moindre écriture, via
  `parse_contract` séparé de `load_contract`. *Pourquoi* : un gabarit incohérent laissait une
  destination à moitié bâtie, que la tentative suivante refusait comme « existe déjà » —
  l'utilisateur restait coincé. *Constaté à l'exécution*, pas prévu au plan.
- **2026-08-21** — le contrôle de conservation de `merge` recompte les `^## ` **sur le document
  rendu**. *Pourquoi* : comparer `len(blocs)` à `len(paths())` compare deux fois la même
  variable et ne peut jamais échouer. *Effet* : le contrôle attrape un `title` qui ouvrirait un
  faux élément — mesuré.

- **2026-08-21** — l'appel à git vit dans `listdir/gitcmd.py`, seul endroit du paquet.
  *Pourquoi* : `store.move` en a besoin et `Toolbox.git` l'expose ; deux implémentations de
  « lancer git et traduire son code retour » diffèreraient sur le traitement de stderr,
  c'est-à-dire sur ce qu'un échec dit. *Effet* : `utils.py` n'importe plus `subprocess`.
- **2026-08-21** — `ListStore.check_item` devient publique. *Pourquoi* : `move` doit rappeler
  ce que le contrat d'arrivée exige d'un élément écrit pour le contrat de départ, sans que le
  déplacement en dépende. *Rejeté* : refuser le déplacement, qui aurait fait de `move` un juge.

- **2026-08-21** — `list` refuse aussi un champ inconnu passé à `--sort`, et n'a qu'un seul
  contrôle pour `--where` : celui de `ListStore.where`. *Pourquoi* : deux définitions de la
  même règle finissent par diverger. *Effet* : le message de `--where` vient de la
  bibliothèque, celui de `--sort` de la commande.

- **2026-08-21** — `validate` traite un champ ou une section **non déclarés au contrat** comme
  un manquement. *Pourquoi* : le contrat est l'autorité, comme pour `where` qui refuse déjà un
  champ inconnu. *Effet* : un fichier enrichi à la main hors contrat est signalé, pas ignoré.
  **Ratifié par l'utilisateur le 2026-08-22**, question close : la migration des 24 entrées devra
  faire tenir chaque champ existant dans le contrat, ou l'écarter par `migrate --drop`.
- **2026-08-21** — `check_value` et `is_marker` vivent dans `contract.py`, hors de `__all__`.
  *Pourquoi* : confronter une valeur à un `Field` est de la sémantique de contrat ; un script
  qui veut reconnaître un vide compare aux constantes déjà exportées.

- **2026-08-21** — le contrat squelette d'`init` reste écrit en dur dans `store.py`.
  *Pourquoi* : un gabarit vit dans `.list/templates/` d'une liste existante, or `init` sert
  précisément le cas où aucune liste n'existe. *Rejeté* : un fichier de gabarit dans le skill,
  qui aurait ajouté un chemin à résoudre pour un contenu de trois champs.
- **2026-08-21** — `Utils.open` rend un `Result[ListStore]`, via un import `TYPE_CHECKING`.
  *Pourquoi* : le `Result[object]` d'origine évitait le cycle mais n'apprenait rien à une
  commande sur ce qu'elle reçoit. *Rejeté* : déplacer `ListStore` dans `types.py`.
- **2026-08-21** — les modules de commande importent en absolu (`from listdir.types import`).
  *Pourquoi* : le chargeur les importe par chemin de fichier, hors de tout paquet ; un import
  relatif lèverait `ImportError`. *Contrainte* : vaut pour les commandes d'une liste comme
  pour les génériques.

- **2026-08-20** — `listdir` est une bibliothèque, la CLI n'en est qu'une façade. *Pourquoi* : un
  script tiers doit avoir les mêmes moyens que la CLI sans `subprocess`. *Rejeté* : un script
  unique, qui aurait forcé à reparser du texte.
- **2026-08-20** — front matter TOML, `render()` reconduisant le bloc brut, sérialiseur borné aux
  types du contrat. *Pourquoi* : `tomllib` lit mais n'écrit pas ; borner l'écriture évite le
  parsing artisanal que le chantier supprime. *Rejeté* : `tomli-w` (hors stdlib).
- **2026-08-20** — deux marqueurs, `<À REMPLIR>` (requis) et `<OPTIONNEL>` (facultatif), pour les
  champs comme pour les sections. *Pourquoi* : `new` pose tout le contrat pour guider le modèle,
  mais `--filled` ne doit pas réclamer du facultatif.
- **2026-08-20** — commits de chantier autorisés explicitement par l'utilisateur. *Pourquoi* : sans
  commits, `move` n'est pas éprouvable et le critère `git log --follow` est hors d'atteinte.
- **2026-08-20** — `DESCRIPTION` dans les modules `.py`, pas dans `contract.toml`. *Pourquoi* : une
  commande vit dans un fichier, sa description doit vivre avec elle. *Rejeté* : le contrat, qui
  l'aurait répliquée.

## Preuves d'exécution

**Étape 5 — dépendance déclarée absente, éprouvée par injection** (à reprendre au rapport d'audit,
le brief l'exige). Commande jetable déclarant `REQUIRES = ["outil-absent-xyz"]`, code de sortie 1 :

```
« probe » exige outil-absent-xyz — introuvable dans le PATH. Déclaré par REQUIRES dans
<liste>/.list/commands/probe.py.
```

La même commande avec `REQUIRES = ["git"]` s'exécute et sort 0 — l'échec vient bien du contrôle de
dépendance, pas d'ailleurs.

**Étape 5 — surcharge d'une commande protégée**, code 1 :

```
<liste>/.list/commands/validate.py: « validate » ne se surcharge pas — elle porte le contrat de
toutes les listes
```

**Étape 13 — migration des 24 entrées.** `python3 scripts/migrate-dette.py` → `24/24`.

```
todo/technical-debt       : 17 élément(s) conformes au contrat        code=0
todo/technical-debt-solde :  7 élément(s) conformes au contrat        code=0
todo/technical-debt-ecarte:  0 élément(s) conformes au contrat        code=0
```

**Conservation de la prose, dans les deux sens** — 108 blocs migrés sur 108 retrouvés à l'identique
dans le `.md` d'origine ; et réciproquement, aucun paragraphe d'origine absent des listes. Le seul
écart signalé par le contrôle inverse est une ligne *Identifié par …* enroulée sur deux lignes dans
la source et rendue sur une seule dans le champ `source` — le texte est entier.

**Étape 12 — migration après remaniement du contrat.** Contrat gagnant un champ requis, deux
sections, et un ordre différent :

```
essai/alpha.md: champ « gravite » — ajouté, <À REMPLIR>
essai/alpha.md: section « Contexte » — ajoutée, <À REMPLIR>
essai/alpha.md: section « Suite » — ajoutée, <OPTIONNEL>
essai/alpha.md: section « Note perso » — conservée — non déclarée au contrat (voir --drop)
```

La valeur déjà écrite dans `title` et le corps de `Constat` sont intacts. Rejeu immédiat :
`0 changement appliqué, 1 remarque sans écriture`, empreinte du fichier **inchangée**. Sur un
contrat dont seul l'ordre bouge : `champs réordonnés selon le contrat` et `sections réordonnées
selon le contrat`, rien d'autre. `--drop` retire la section hors contrat, `validate` passe au vert.
Surcharge refusée, code 1 :

```
essai/.list/commands/migrate.py: « migrate » ne se surcharge pas — elle porte le contrat de
toutes les listes
```

**Étape 15 — la paire `review.{toml,md}` sur les 17 entrées réelles**, dérivée vers le scratchpad :

```
$ list-dir.py derive $T/technical-debt $W/revue --template review  → 17 fiche(s) à instruire
$ test -f $W/revue/.list/contract.toml                             → contrat posé
$ list-dir.py validate $W/revue                                    → [0] 17 conformes
$ list-dir.py validate $W/revue --filled                           → [1] 85 manquements (17 × 5)
```

Les 5 par fiche sont `reviewed`, `category` et les trois sections requises : `title` et `date` sont
reportés par `from`, et `Arbitrage` — restée à `<OPTIONNEL>` — n'est jamais réclamée. Après
remplissage mécanique par le script de recette (une constante par type, aucun jugement) :
`validate --filled` vert, `merge` rend **17** blocs `^## `, **0** `<À REMPLIR>`, et **aucune**
section `Arbitrage` — l'optionnelle non remplie est bien omise de l'aggloméré.
`grep -ril 'dette\|debt' skills/list-dir/` reste sans sortie.

**Étape 16 — `trier-revue.sh` supprimé, ses garanties reprises par les commandes.** `git ls-files
skills/debt-review` rend quatre fichiers, tous des `.md` ; `scripts/` n'existe plus.
`grep -rn 'trier-revue' skills/` est muet — les seules occurrences restantes sont dans `done/` et
dans le plan, qui sont des archives. `SKILL.md` cite `derive` (5), `merge` (5) et `validate` (6).
La boucle des piles, éprouvée sur le registre réel :

```
aggravee         1
inverifiable     2
(les cinq autres à 0 ; 14 entrées n'ont jamais été revues)
```

Ce que le script faisait et qui est désormais dans les commandes : le découpage en blocs (`derive`
crée un fichier par entrée), le comptage de conservation (`merge` recompte les blocs rendus face
aux fichiers présents), le refus d'un bloc mal formé (`validate` contre le contrat), et la
détection d'une fiche non instruite (`validate --filled`).

**Étapes 17 et 18 — les deux réserves traitées.**

R7, après report : `reviewed` renseigné sur **14** entrées, au marqueur sur **3** — exactement les
trois nées de la revue du 2026-08-17, qui ne pouvait donc pas les instruire. `category` : 11
`pertinent`, 1 `aggravee`, 2 `inverifiable`, 3 au marqueur. Le diff porte sur 11 fichiers, 22
lignes changées, **toutes des lignes `reviewed` ou `category`** — aucune prose touchée.

R1, le trou mesuré puis fermé :

```
$ rm une-fiche.md   # 16 fiches pour 17 entrées
$ list-dir.py merge $R --out ko.md            → code=0
  2026-08-23 — 16 élément(s) aggloméré(s), 16 fichier(s) dans le répertoire.
$ test $(list-dir.py list $R | wc -l) -eq $(list-dir.py list $T/technical-debt | wc -l)
                                              → ÉCHEC détecté
```

**Étape 19 — revue à blanc de bout en bout, sur les 17 entrées réelles.** `derive` vers
`$SCRATCHPAD/revue-a-blanc/`, jamais sous `done/revues/`.

```
$ derive $T/technical-debt $R --template review   → 17 fiche(s) à instruire, contrat posé
$ validate $R                                      → 0
$ validate $R --filled                             → 1
$ merge $R --out ko.md                             → 1  (« à compléter avant d'agglomérer »)
$ recette-revue.py $R                              → 17 fiche(s) remplies, 0 marqueur résiduel
$ validate $R --filled                             → 0
$ merge $R --out rapport.md                        → 17 blocs, 0 marqueur, 0 « Arbitrage »
  préambule : 2026-08-23 — 17 élément(s) aggloméré(s), 17 fichier(s) dans le répertoire.
```

**Les 17 titres du registre se retrouvent un à un dans le rapport** — 0 manquant, contrôlé par
`grep -F` sur chaque `title`, et pas seulement par un comptage. La source est intacte
(`git status --short` sur la liste : vide) et **rien n'a fui dans le dépôt** : `git status --short`
ne montre que `settings.json`, étranger au chantier ; rien sous `done/`.

Le script de recette **ne juge pas** : une constante par type déclaré (`values[0]` pour un enum),
d'où les 17 fiches en `a-solder` — un artefact de recette, jamais un verdict. Il ne pose jamais de
marqueur, sans quoi rempli et non rempli cesseraient de se distinguer.

**Écart au plan, déjà acté en étape 18** : le plan attendait qu'une fiche retirée avant `merge`
fasse échouer `merge`. Mesuré : `merge` sort **0**, et c'est le contrôle contre le registre qui
détecte le trou.

**Étape 20 — le pipeline n'ordonne plus d'écrire dans un fichier mort.**
`grep -rn 'technical-debt.*\.md' skills/implementation-tracker/ skills/debt-review/` ne rend plus
aucun registre : `cloture.md` crée les entrées par `new` et les solde par `move`, `contrat.md`
décrit trois répertoires-listes. Le contrôle 1 du garde-fou a **refusé** la section *Dépendances*
tant qu'aucun fichier ne la citait — une section de contrat que personne ne suit n'est pas une
règle. Renvoi posé depuis `dette.md`, pipeline conforme.

**Étape 21 — le contrôle 6 couvre les deux interpréteurs**, éprouvé par injection dans
`skills/list-dir/SKILL.md`, quatre cas :

```
bash scripts/injecte.sh                          → ✗ appel relatif non gardé (déjà couvert)
python3 scripts/list-dir.py help                 → ✗ appel relatif non gardé  (nouveau), code 1
python3 "$HOME/.claude/…/list-dir.py" help       → ✓
[ -f scripts/list-dir.py ] && python3 scripts/…  → ✓ relatif mais gardé
```

Ne sont pas concernés, et c'est écrit dans le script : `python3 -c`, `python3 - <<'PY'` et
`python3 "$L"` — aucun ne porte de chemin `.py` en clair, et c'est la **définition** de la variable
qui doit être absolue, pas son usage.

**Outillage — `all` sur les deux configurations** : `uvx basedpyright` → `0 errors, 0 warnings,
0 notes` sur 19 fichiers, depuis la racine comme depuis `skills/list-dir/` ;
`uvx ruff check skills/list-dir` → *All checks passed!*. **Corrigé après R17 de l'audit** : la
première rédaction disait `uvx ruff check .`, qui rend 3 erreurs — toutes dans
`statusline-command.py`, fichier étranger au chantier. Les deux linters ne sont **pas dans le `PATH`** — d'où leur non-exécution à
l'audit — et la section *Dépendances* porte désormais leur lanceur.

**Étape 22 — les 13 contrôles du plan, exécutés d'un bout à l'autre.**

```
 1. check-pipeline.sh                                   code=0
 2. contrat présent + validate sur les 3 listes         ok
 3. aucun marqueur résiduel ; --filled vert sur les 3   ok
 4. conservation                                        24
 5. grep dette|debt dans skills/list-dir/               aucune sortie
 6. formes d'import couvertes ; stdlib seule            ok
 7. API : 17 éléments ; « /inexistant: répertoire introuvable »
 8. aucune logique métier dans commands/                aucune sortie
 9. <À REMPLIR> : 1 définition ; <OPTIONNEL> : 1        ok
10. help                                                10 commandes
11. dépendance absente par injection                    code=1, nomme outil-absent-xyz
12. derive 17 → filled rouge → rempli → merge 17 blocs, 0 marqueur ; done/ vide
13. move + git log --follow → 2 commits, remonte à « étape 13 les trois listes »
```

**Le critère du brief sur la traçabilité est servi sur le dépôt réel** : `git status` montre `R`,
`git diff --cached -M --stat` compte **0 ligne changée**, et après commit `git log --follow` sur le
fichier d'arrivée remonte au commit de création dans la liste de départ. `move` refuse de se taire
au passage — il rappelle que le contrat d'arrivée exige `Soldé le` et **que le compléter demande un
second commit**. Aller-retour neutre : `git diff --stat HEAD~2` est vide. Deux commits de test
restent sur la branche, à aplatir à la clôture.

**Étapes 23 et 24 — les deux réserves de clôture.**

R9, avant : `init --name 'ma "liste"'` → code 0 puis `name = "ma "liste""`, que `validate` refuse.
Après : `name = "ma \"liste\""`, `validate` code 0. Éprouvé aussi sur un antislash et sur les deux
à la fois : `name = "c:\\dette"`, `description = "guillemet \" et \\ dedans"`.

R6, avant : un `## ` collé dans une sortie de commande ouvrait une section que `validate` refusait
comme « non déclarée au contrat ». Après, sur un `Constat` portant un bloc à trois backticks **et**
un bloc à quatre contenant une clôture plus courte :

```
sections lues : ['Constat']
le bloc de code est intact : True     (## un titre dans la sortie)
les 4-backticks aussi     : True     (## encore un)
validate                  : code 0
render identique          : True
```

**Non-régression, après les deux correctifs** : `validate` et `--filled` verts sur les trois listes ;
**24 éléments réels relus et rendus, 0 écart octet pour octet** ; `help` → 10 ; API → 17 éléments ;
`uvx ruff check skills/list-dir` → *All checks passed!* ; `uvx basedpyright` → 0 erreur ;
`check-pipeline.sh` → code 0.

**Étapes 25 à 27 — les trois défauts de la 2e passe.**

R19, le flux de référence avec une **vraie preuve exécutée** collée dans `Vérifié par` (bloc de code
contenant `## un titre dans la sortie`) :

```
avant : validate --filled code 0, puis merge code 1
        « 20 élément(s) dans le document pour 18 fichier(s) — un élément a été perdu »
après : validate --filled code 0, merge code 0
        2026-08-23 — 18 élément(s) aggloméré(s), 18 fichier(s) dans le répertoire.
```

R20, aller-retour `tomllib` sur les valeurs qui cassaient :

```
'ligne1\nligne2'           → "ligne1\nligne2"        relu identique : True
'guillemet " et \ dedans'  → …                        relu identique : True
'tab\tici', 'retour\rchariot'                        relu identique : True
'avec \x07 cloche'         → REFUS : caractère de contrôle U+0007
```

R21 : ```` ```python ```` à l'intérieur d'un bloc ouvert par ```` ``` ```` ne le referme plus, et une
info string contenant un backtick n'ouvre pas de bloc.

**Non-régression** : `validate` et `--filled` verts sur les trois listes ; **25 éléments réels
relus et rendus, 0 écart octet pour octet** ; `uvx ruff check skills/list-dir` → *All checks
passed!* ; `uvx basedpyright` → 0 erreur ; `check-pipeline.sh` → code 0.

**Étape 5 — garde de version**, éprouvée en portant le seuil à 99.0, code 2 :

```
list-dir exige Python >= 3.12, trouvé 3.14.7 (/home/linuxbrew/.linuxbrew/opt/python@3.14/bin/python3.14).
```
- **2026-08-21** — ruff et basedpyright en mode `recommended` sur le paquet, configuration dans
  `skills/list-dir/` **et** à la racine (qui exclut `plugins/`, du code tiers). *Pourquoi* : le mode strict a révélé que `load_contract` prenait pour
  argent comptant tout ce que `tomllib` rend — un contrat où `sections` est une chaîne levait
  un `AttributeError` nu au lieu d'un échec nommé. *Rejeté* : le mode `standard`, qui passait
  au vert sans rien voir.
- **2026-08-21** — `FieldType` (`Literal`) et `FieldValue` remplacent `str` et `object` dans la
  surface publique ; `FIELD_TYPES` en dérive par `get_args`. *Pourquoi* : la liste des types
  était écrite deux fois, et `where`/`create` acceptaient des valeurs que le sérialiseur ne
  sait pas réécrire. *Effet* : `__all__` passe de 18 à 21 noms.
- **2026-08-21** — `CommandSpec.load()` rend un `Command[object]` et non un `ModuleType`.
  *Pourquoi* : sans ce cast, l'appel `module.command(...)` est de type `Any` et le protocole
  ne sert que la documentation. *Rejeté* : laisser le dispatch non typé.

### Étape 6 — comptes de marqueurs sur le contrat d'exemple

Contrat : `title` et `date` requis, `category` facultatif, sections requises `Constat`,
`Analyse`, `Décision`, section optionnelle `Notes`.

```
$ list-dir.py new ./revue premiere-entree
revue/premiere-entree.md
$ grep -cF '<À REMPLIR>' revue/premiere-entree.md   → 5   (attendu 5)
$ grep -cF '<OPTIONNEL>' revue/premiere-entree.md   → 2   (attendu 2)
```

Échecs fermés : `init` sur liste existante → 1 ; `new` sur id existant → 1 ; `new` sur
répertoire inconnu → 1 ; `show` sur élément absent → 1 ; argument manquant → 2.

### Étape 7 — les deux verdicts sur l'élément prérempli par l'étape 6

```
$ list-dir.py validate ./revue            → [0] revue : 1 élément(s) conformes au contrat
$ list-dir.py validate ./revue --filled   → [1] 5 manquements
     champ « title » — à remplir
     champ « date » — à remplir
     section « Constat » — à remplir
     section « Analyse » — à remplir
     section « Décision » — à remplir
```

Les 5 manquements sont exactement les 5 `<À REMPLIR>` de l'étape 6. Ni `category` (champ
facultatif) ni `Notes` (section optionnelle) ne sont réclamés.

Autres cas : champ requis retiré → 1, nommant le champ et le fichier ; `id` ≠ nom de fichier,
date non ISO et valeur hors enum → 3 manquements distincts ; `date = "<À REMPLIR>"` passe la
structure et n'est signalé qu'en `--filled`, comme *à remplir* et jamais comme type invalide ;
champ et section hors contrat → 2 ; surcharge de `validate` par une liste → refusée, code 1.

### Étape 8 — filtre et tri

```
$ list-dir.py list ./revue --sort category,date
mu actif 2025-12-31
zeta actif 2026-01-15
alpha doublon 2026-08-01
beta obsolete 2026-08-01
```

Égalité sur `date` entre `alpha` et `beta` : départagée par l'id. `--where` répété cumule les
critères. Un filtre sans résultat rend **zéro octet et le code 0**.

Refus : `--where categorie=actif` → 1, « champ « categorie » non déclaré au contrat ; connus :
id, title, date, category » ; `--sort inconnu` → 1 ; `--where malforme` → 1, la forme attendue
étant CHAMP=VALEUR.

### Étape 9 — traçabilité Git, dépôt jetable

```
$ git status --short
R  dette/filtres-listing.md -> dette-soldee/filtres-listing.md
$ git diff --cached -M --stat
 {dette => dette-soldee}/filtres-listing.md | 0
 1 file changed, 0 insertions(+), 0 deletions(-)

$ git commit -m "solde: déplacement de filtres-listing"
$ git log --follow --oneline -- dette-soldee/filtres-listing.md
f5622f5 solde: déplacement de filtres-listing
6bacba1 création de filtres-listing dans dette      ← le commit de création
```

**Contre-épreuve du signal de dérive du brief.** Dans un second dépôt jetable, déplacement et
réécriture du contenu dans le MÊME commit :

```
$ git log --follow --oneline -- b/sujet.md
03c1155 déplacement ET réécriture dans le même commit
```

Le commit de création a disparu de l'historique suivi. Le signal de dérive n'est donc pas une
précaution théorique : il est mesuré.

Échecs fermés : même liste → 1 ; élément absent → 1 ; cible sans contrat → 1 ; cible inexistante
→ 1 ; homonyme à l'arrivée → 1, « rien n'est déplacé » ; fichier non suivi par git → 1, portant
le message de git.

**Surcharge décorative éprouvée** : un `close.py` de liste qui appelle `utils.git` puis
`utils.run("move", …)` déplace l'élément sans réimplémenter `git mv`.

### Étape 10 — projection puis agglomération

Gabarit `review.toml` / `review.md` dans `source/.list/templates/`, `title` portant
`from = "title"`, `verdict` sans `from`.

```
$ list-dir.py derive ./source ./revue --template review   → revue — 3 fiche(s) à instruire
```

La fiche engendrée porte `id` et `title` reportés, `verdict` à `<À REMPLIR>`, `note` à
`<OPTIONNEL>`, et **les sections du gabarit, jamais celles de la source** — aucune trace du
« Constat » de l'élément d'origine. La source est inchangée.

```
$ list-dir.py validate ./revue            → 0   (structure)
$ list-dir.py validate ./revue --filled   → 1   (9 manquements : les fiches sont vierges)
$ list-dir.py merge ./revue --out ko.md   → 1   « à compléter avant d'agglomérer »
```

Après remplissage à la main :

```
$ list-dir.py validate ./revue --filled   → 0
$ list-dir.py merge ./revue --out rapport.md
$ grep -c '^## ' rapport.md      → 3      (le compte des éléments, et rien d'autre)
$ grep -cF '<À REMPLIR>' rapport.md → 0
$ grep -c 'Remarques' rapport.md → 0      (section restée facultative, omise)
```

Échecs fermés : destination existante → 1 ; `.md` du gabarit manquant → 1 le nommant ; `.toml`
manquant → 1 ; `--template` inconnu → 1 ; liste source vide → 1 ; `merge` sur liste vide → 1 ;
`from` nommant un champ absent du contrat source → 1, **sans laisser de destination derrière** ;
gabarit au TOML invalide → 1, idem ; `title` contenant une ligne « ## » → 1, « 3 élément(s) dans
le document pour 2 fichier(s) ».

**Écart au plan, assumé** : le plan attendait qu'un élément retiré entre `derive` et `merge` fasse
échouer `merge`. C'est impossible par construction — les deux comptes se réduisent ensemble, et la
liste amputée est simplement plus courte. Le contrôle de conservation a été redressé pour porter
sur ce qu'il peut réellement prouver (le document rendu contre les fichiers présents).

### Étape 11 — l'interface se découvre, sans rien exécuter

`help` sans argument liste les **9** commandes génériques. Avec une liste, les génériques
tombent à 8 et une section « Commandes de <liste> » apparaît :

```
  close     solde un élément : move plus la trace  [exige git]
  show      affichage maison, avec le contexte  (surchargée)
```

`move` affiche `[exige git]` : `REQUIRES` est lu sans importer le module.

**Rien n'est exécuté.** Un module déposé dans la liste qui écrit sur stderr à l'import :

```
$ list-dir.py help ./ma-liste | grep -c 'A ÉTÉ EXÉCUTÉ'   → 0
  piege     ne doit jamais s'exécuter à l'affichage
```

Sa description s'affiche, son effet ne se produit pas.

Module au Python cassé → `casse  INUTILISABLE — illisible — '(' was never closed`, les autres
restent listés, code 0 ; l'appeler directement → code 1. Surcharge de `help` → code 1.
Argument qui n'est pas une liste → code 1.
