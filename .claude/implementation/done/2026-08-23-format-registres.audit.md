---
slug: format-registres
---

## 2026-08-23 — intermédiaire — `d803dae`

**Verdict** : RÉSERVES

Périmètre jugé : les étapes 1 à 16 du suivi, cochées `[x]`. L'étape 17 est `[>]`, les étapes 18 à
20 sont `[ ]` — elles ne sont pas reprochées ici. Brief lu (`format-registres.brief.md`), suivi lu,
plan lu (`.claude/plans/spicy-percolating-pelican.md`). Le suivi élargit le périmètre en deux points
datés (`migrate` le 2026-08-22 ; conservation des anciens `.md` pour l'audit le 2026-08-22) : ils
font foi sur le brief.

### Vérifications exécutées

Toutes lancées par l'auditeur depuis `/home/debian/.claude`, sorties réelles.

- `bash scripts/check-pipeline.sh` → `Pipeline conforme.`, code 0 (6 contrôles verts)
- `validate` sur les trois listes permanentes → `17`, `7`, `0` élément(s) conformes, code 0 chacune
- `validate --filled` sur les trois → `17`, `7`, `0` remplis et conformes, code 0 chacune
- Vérif #3 du plan (aucun `<À REMPLIR>` résiduel dans les éléments) → aucune sortie
- Vérif #4 (conservation) → `find … | wc -l` → **24**
- Vérif #5 (`grep -ril 'dette\|debt' skills/list-dir/`) → aucune sortie, code 1
- Vérif #6 (stdlib) → **ROUGE tel qu'écrit** : `__future__` et `collections` sortent de l'allowlist
  (voir R11)
- Vérif #7 (API publique) → `17 éléments` puis `/inexistant: répertoire introuvable`
- Vérif #8 (aucune logique métier dans `commands/`) → **ROUGE tel qu'écrit** : 9 occurrences, toutes
  des `utils.open(` (voir R11)
- Vérif #9 (marqueur défini une seule fois) → `À REMPLIR: 3`, `OPTIONNEL: 1` — **ROUGE tel qu'écrit**
  (voir R11)
- Vérif #10 (`help | grep -c '^  [a-z]'`) → **10**, attendu 9 (voir R11)
- Vérif #11 (dépendance déclarée absente, par injection) → code **1** :
  ```
  « probe » exige outil-absent-xyz — introuvable dans le PATH. Déclaré par REQUIRES dans
  .claude/implementation/todo/technical-debt/.list/commands/probe.py.
  ```
- Vérif #12 (flux de revue de bout en bout, sur les 17 entrées réelles, hors dépôt) :
  ```
  derive … --template review   → 17 fiche(s) à instruire
  test -f …/revue/.list/contract.toml → contrat posé
  validate                     → 17 élément(s) conformes            code 0
  validate --filled            → code 1  (avant remplissage)
  ls *.md | wc -l              → 17
  [remplissage mécanique, une constante par type, aucun jugement]
  validate --filled            → 17 élément(s) remplis et conformes  code 0
  merge --out revue.md         → grep -c '^## ' → 17 ; grep -cF '<À REMPLIR>' → 0 ;
                                 grep -c 'Arbitrage' → 0
  préambule : « 2026-08-23 — 17 élément(s) aggloméré(s), 17 fichier(s) dans le répertoire. »
  [une fiche retirée] merge    → code 0, 16 blocs  ← ROUGE tel qu'écrit au plan (voir R1)
  ```
- Vérif #13 (`git log --follow` après un `move` commité) → **NON EXÉCUTÉE** : elle exige deux commits
  dans le dépôt réel, et le contrat de l'auditeur interdit toute commande `git` d'écriture (voir R3)
- Échec fermé de `validate` sur un champ du contrat manquant (copie hors dépôt, `date` retiré) →
  code **1**, `champ « date » — manquant` ; puis section `Pour solder` retirée → code 1, `2 manquements`
- Aller-retour octet pour octet sur les 24 éléments réels (`item.render() == fichier`) → **aucun écart**
- Conservation de la prose migrée, sens listes → source : 76/80 et 32/38 blocs retrouvés verbatim
  dans les `.md` d'origine ; les 10 écarts sont **tous** des sections restées à `<OPTIONNEL>`, donc
  légitimes
- `python3 -m compileall skills/list-dir/scripts scripts/migrate-dette.py` → OK
- `migrate --dry-run` sur `technical-debt` → `déjà conforme au contrat, aucun fichier touché`, code 0
- `git ls-files skills/debt-review` → 4 fichiers, tous `.md`, `trier-revue.sh` absent ;
  `grep -rn 'trier-revue' skills/` → aucune sortie
- `ruff` / `basedpyright` → **NON EXÉCUTÉES** : absents du PATH et de `python3 -m` (voir R14)

### Conformité à l'intention

Critère par critère, tel que le brief les énonce.

- **« une revue complète des 17 entrées actives tourne sur ce flux, et le fichier aggloméré est
  archivé sous `done/revues/<date>-revue.md` »** — première moitié **atteinte et vérifiée** : le flux
  `derive` → remplir → `merge` tourne sur les 17 entrées réelles, 17 blocs, 0 marqueur.
  Seconde moitié **non servie**, écart assumé et ratifié le 2026-08-20 (plan, « Ce qui n'est pas
  fait » ; suivi, « Écart au brief »). **R2** — la procédure de `debt-review` écrit bien
  `"$R-revue.md"` avec `R=".claude/implementation/done/revues/$(date +%F)"`, donc le chemin exigé
  est produit *par construction* le jour où une vraie revue tourne ; mais rien dans ce chantier ne
  l'exécute, et aucune commande ne garantit que ce chemin est le bon. La lettre du critère reste
  invérifiable jusqu'à la première revue post-clôture.
- **« la commande de validation passe sur les quatre répertoires-listes … et échoue sur un élément
  dont un champ du contrat manque »** — **atteint et vérifié**. Les trois listes permanentes passent
  (17/7/0), la quatrième — la liste de revue — passe elle aussi après `derive`. Le retrait d'un champ
  requis rend code 1 en nommant le champ et le fichier ; le retrait d'une section aussi.
- **« un élément déplacé reste suivi : `git log --follow` … »** — **invérifiable par l'auditeur**.
  **R3** — le critère exige des commits dans le dépôt réel ; mon contrat n'autorise que des commandes
  `git` de lecture, et aucun `move` n'a encore été commité sur cette branche. Le suivi consigne la
  preuve obtenue en dépôt jetable à l'étape 9, contre-épreuve du signal de dérive comprise ; je l'ai
  lue, je ne l'ai pas rejouée. À servir en propre à l'étape 20 (Vérification #13).
- **« conservation vérifiée par commande : autant d'éléments agglomérés que d'éléments dans le
  répertoire, l'écart faisant échouer »** — **atteint dans la lettre du brief**, et je l'ai mesuré :
  `merge` recompte les `^## ` **sur le document rendu** face à `len(paths())`, et un `title` portant
  une ligne `##` fait bien échouer. **R1** — mais ce contrôle ne peut pas détecter un élément
  *retiré* : les deux comptes se réduisent ensemble. Mesuré : après suppression d'une fiche sur 17,
  `merge` sort **0** et rend 16 blocs. Le suivi assume cet écart (journal, étape 10) ; le brief est
  satisfait puisqu'il compare aggloméré et répertoire, pas aggloméré et compte initial. Ce qu'il faut
  savoir : **rien ne rattrape la perte d'un fichier entre `derive` et `merge`**, et le SKILL de
  `debt-review` s'appuie pourtant sur « le compte des fiches est celui du registre par construction ».
- **« le skill générique ne connaît aucun de ses consommateurs »** — **atteint et vérifié** :
  `grep -ril 'dette\|debt' skills/list-dir/` ne rend rien. Confirmé aussi côté conception : les
  sections préétablies de la fiche viennent de `review.md` posé dans la liste source, pas du skill.
- **« un script dont un outil déclaré manque sort non nul en le nommant, éprouvé par injection et la
  sortie recopiée dans le rapport d'audit »** — **atteint et vérifié**, sortie recopiée ci-dessus.
- **« `skills/debt-review/scripts/trier-revue.sh` est supprimé, ses garanties reprises par les
  commandes génériques »** — **atteint et vérifié**. Les quatre garanties du script sont reprises :
  découpage (`derive`), comptage (`merge`), refus d'un bloc mal formé (`validate`), détection d'une
  fiche non instruite (`validate --filled`).
- **« les commandes n'importent que la stdlib »** — **atteint**. Les seuls noms importés dans
  `skills/list-dir/scripts/` sont `argparse ast collections dataclasses datetime importlib os
  pathlib shutil subprocess sys tomllib types typing __future__ listdir`. Aucun tiers.
- **« `scripts/check-pipeline.sh` passe au vert »** — **atteint et vérifié**, 6 contrôles verts.

**Hors-périmètre** — respecté sur les trois points nommés : aucune trace de Neovim, `road-map.md`
toujours inexistante (`todo/README.md` la mentionne comme perspective, sans la créer), briefs, suivis
et rapports d'audit restent des documents.

**Signaux de dérive** — aucun matérialisé sur les six, sauf le sixième, partiellement :

- fichiers créés/déplacés à la main : non — tout passe par `list-dir`, et `todo/README.md` comme le
  SKILL de `debt-review` l'écrivent noir sur blanc.
- un script qui juge : non — le jugement de la migration est isolé dans des tables de
  `scripts/migrate-dette.py`, et `derive`/`migrate` refusent explicitement de reporter ou renommer.
- commit mêlant déplacement et réécriture : non — `move` est un `git mv` pur, le SKILL exige un
  second commit, et le message de rappel de `move` le redit à l'exécution.
- vue dérivée éditable : non — la fiche de revue ne porte aucune prose de la source.
- skill générique connaissant la dette : non.
- **R4 — « si le diff dépasse la réécriture de `debt-review` et des registres, s'arrêter et en
  reparler » : le diff le dépasse en trois points.** `pyrightconfig.json` **à la racine du dépôt**
  (nouveau fichier, `include: ["skills"]`, donc portant sur tout le dépôt), `.gitignore` (+3 lignes)
  et `scripts/migrate-dette.py`. Le journal du suivi date et motive l'outillage le 2026-08-21, mais —
  contrairement à `migrate`, dont le journal note « constaté par l'utilisateur » — rien n'établit que
  l'élargissement à la racine ait été reparlé, comme le signal l'exige. Réserve, pas défaut : la
  décision est écrite et traçable, seule sa ratification manque.

**Symptôme d'origine** — « le Markdown ne convient pas à l'utilisation de scripts et est difficile à
maintenir quand il représente une liste » : **disparu** sur le périmètre traité. Les 24 entrées sont
24 fichiers, comptables par `find | wc -l`, filtrables par `--where`, validables par contrat, et
l'API rend des `Result` typés à un script tiers en trois lignes d'amorçage.

### Qualité du code

**R5 — les deux marqueurs sont recopiés hors de `types.py`, dans un fichier que rien ne contrôle.**
`.claude/implementation/todo/technical-debt/.list/templates/review.md` écrit `<À REMPLIR>` et
`<OPTIONNEL>` en dur, quatre fois. C'est une conséquence du design (`derive` recopie le corps du
gabarit tel quel), mais le mode de défaillance est celui-là même que le plan voulait interdire :
si `PLACEHOLDER` change un jour, `validate --filled` comparera le corps au nouveau marqueur, ne le
trouvera pas, et **laissera passer une fiche vierge pour instruite**. Le préambule de `review.md`
énonce la règle (« le corps est exactement le marqueur ») mais aucune commande ne la vérifie. La
Vérification #9 du plan ne balaie que `skills/list-dir/scripts/` : elle est aveugle à ce cas.

**R6 — un bloc de code contenant une ligne `## ` casse l'élément qui le porte, et ce n'est écrit
nulle part.** `parse_sections` (`items.py:48`) découpe sur toute ligne commençant par `## `, sans
tenir compte des délimiteurs ` ``` `. Éprouvé :

```
essai.md: section « Une section citée » — non déclarée au contrat
essai : 1 manquement            code=1
```

L'échec est fermé, ce qui est le bon comportement, mais **il n'existe aucun échappement** : la
section est simplement inécrivable. Or `debt-review` demande explicitement d'écrire dans la section
`Vérifié par` « la commande exécutée et **sa sortie réelle** » — une sortie contenant une ligne
`## ` rendra la fiche invalide sans que l'opérateur comprenne pourquoi. Ni `references/contrat-liste.md`
(11 sections, aucune sur le sujet) ni le SKILL ne mentionnent la contrainte.

**R7 — la migration a transformé « revue le 2026-08-17 » en « jamais revue » pour 14 entrées.**
`technical-debt.md` portait `> Dernière vérification : 2026-08-17 (chantier revue-dette)`, qui vaut
pour l'ensemble du registre. Le journal du 2026-08-22 décide de remplacer cette ligne unique par les
champs per-entrée `reviewed` et `category`, ce qui est un progrès — mais seules les 3 entrées qui
portaient un marqueur individuel (`(aggravée) 2026-08-17`, `(invérifiable) 2026-08-17`) ont reçu la
date. Les 14 autres portent `reviewed = "<OPTIONNEL>"`. Mesuré :

```
$ list-dir.py list …/technical-debt --sort reviewed
chemin-skill-code-en-dur 2026-08-17
correctif-r21-non-audite 2026-08-17
correctifs-etape-9-non-audites 2026-08-17
clause-arbre-propre-sans-le-plan <OPTIONNEL>
… (14 lignes)
```

Le journal justifie précisément l'intérêt du champ par « `list --sort reviewed` montre ce qui n'a
jamais été confronté au dépôt ». Ce que la commande montre aujourd'hui est faux pour 14 entrées sur
17, et c'est la première revue post-clôture qui s'appuiera dessus. Le fait était dans la source, il
n'est plus nulle part : ce n'est pas une omission de forme, c'est une donnée perdue.

**R8 — le champ `source` est déclaré « verbatim » au contrat et ne l'est pas tout à fait.** La
description dit « le chantier qui l'a identifiée et où il l'a écrit, **verbatim** ». La ligne source
`*Identifié par \`contrat-pipeline\`, R15 et R19 du rapport d'audit.*` devient
`source = "Identifié par \`contrat-pipeline\`, R15 et R19 du rapport d'audit."` — les délimiteurs
d'italique sont retirés. Le texte est entier, seule la mise en forme tombe ; mais le mot « verbatim »
du contrat promet plus que ce qui est livré. Le suivi consigne un écart voisin (retour à la ligne
absorbé) sans mentionner celui-ci.

**R9 — `init_list` interpole `name` et `description` dans du TOML sans échappement.**
`store.py:615` : `f'name = "{name or path.name}"'`. Un nom contenant un guillemet ou un antislash
produit un `contract.toml` que `tomllib` refusera, et l'échec surviendra au premier `open_list`, pas
à l'écriture. C'est le seul endroit du paquet où du TOML est émis **sans** passer par le sérialiseur
borné de `items.py`, qui échappe correctement (`dump_value`, `items.py:88`). La règle 3 du plan —
« `validate` relit ce qui vient d'être écrit » — n'est pas appliquée ici : `init_list` rend `ok` sans
relire.

**R10 — `where` compare les valeurs sous forme textuelle, y compris l'absence.** `store.py:90` :
`str(it.fields.get(k)) == str(v)`. Un champ absent vaut donc la chaîne `"None"`, et
`--where category=None` filtre sur les éléments qui n'ont pas de `category`. Le comportement n'est
documenté nulle part et n'est probablement pas voulu ; il est bénin tant que personne ne s'en sert,
mais c'est un piège pour qui filtre sur un champ facultatif.

Style et lisibilité, hors constat : le paquet est idiomatique et cohérent avec le reste du dépôt —
docstrings qui expliquent le *pourquoi* et pas le *quoi*, messages d'erreur en français nommant le
fichier et la cause, échec fermé partout. Les commandes sont bien réduites à `register()` + un appel
à `ListStore` : la règle de non-divergence du plan tient, en dépit de R11 qui l'énonce mal.

### Dette induite

**R11 — quatre des treize contrôles de la section *Vérification* du plan sont rouges sur du code
conforme.** Ils échoueront à l'étape 20, et le risque n'est pas qu'ils échouent : c'est qu'on
« corrige » le code pour les satisfaire.

| Contrôle | Sortie réelle | Cause |
|---|---|---|
| #6 stdlib | `__future__`, `collections` | allowlist du plan incomplète — les deux sont stdlib |
| #8 pas de logique métier | 9 lignes `utils.open(` | le motif `open(` attrape la méthode du protocole `Utils` |
| #9 marqueur unique | `À REMPLIR: 3` | `contract.py:187` et `:197` mentionnent le marqueur en prose |
| #10 `help` → 9 | `10` | `migrate`, dixième générique ratifiée le 2026-08-22, jamais reportée ici |

À quoi s'ajoute la ligne de #12 `merge` après retrait d'une fiche → `code ≠ 0`, contredite par la
mesure (voir R1) et déjà connue du suivi depuis l'étape 10 sans que le plan ait été mis à jour.
Coût futur : un bloc de vérification qui ment devient un bloc qu'on n'exécute plus.

**R12 — pendant que la branche vit, la procédure de clôture du pipeline pointe encore les registres
gelés.** `todo/README.md` déclare `technical-debt.md` et `technical-debt-solde.md` « figés et
périmés », mais `skills/implementation-tracker/references/cloture.md:40` et `:52` continuent
d'ordonner d'y écrire, et `references/contrat.md:45-47` décrit encore les trois `.md`. C'est l'objet
de l'étape 18, encore `[ ]` — donc non reproché. Ce qui l'est : dans l'état actuel de la branche,
toute clôture d'un autre chantier écrirait dans un fichier que le dépôt déclare mort. À fermer avant
toute fusion, pas seulement avant la clôture du chantier.

**R13 — `scripts/migrate-dette.py` dépasse la norme de 100 colonnes du dépôt sur 20 lignes**
(jusqu'à 125 caractères, lignes 41-65 et 184). Le dépôt suit cette norme au point d'en avoir fait
une entrée de dette (`trois-lignes-au-dela-de-100-colonnes`). Le fichier est jetable et sa
suppression est un point de clôture ; le coût est donc borné, mais il est aujourd'hui commité et
aucun contrôle ne le voit — le seul `ruff.toml` du chantier vit dans `skills/list-dir/` et ne le
couvre pas.

**R14 — l'outillage de qualité annoncé par le suivi n'est pas rejouable.** Le suivi affirme « ruff et
basedpyright (mode `recommended`) passent au vert, depuis la racine du dépôt comme depuis
`skills/list-dir/` ». Ni `ruff` ni `basedpyright` ne sont dans le PATH, ni disponibles par
`python3 -m`. Deux fichiers de configuration sont livrés et versionnés, mais **aucun moyen d'exécuter
ce qu'ils configurent n'est déclaré nulle part** — ni dans `SKILL.md`, ni dans `contrat-liste.md`.
C'est exactement le précédent que le brief cite en contre-exemple (`hooks/intent-brief-gate.sh` et
son `jq` absent) : une garantie écrite qu'aucune exécution n'établit. Les commandes du paquet, elles,
déclarent leurs dépendances par `REQUIRES` ; l'outillage du chantier, non.

### Bloquants

Aucun. Rien n'interdit de poursuivre l'étape 17. R1, R7, R11 et R12 doivent être tranchés avant la
clôture ; R3 reste à servir en propre à l'étape 20.

## 2026-08-23 — clôture — `6a29af7`

**Verdict** : RÉSERVES

Périmètre jugé : les 22 étapes du suivi, toutes cochées `[x]`, et le diff `master...format-registres`
(68 fichiers, +6382/-636). Brief lu, suivi lu, plan lu (`.claude/plans/spicy-percolating-pelican.md`,
section *Vérification*, 13 contrôles). Le suivi élargit le périmètre en quatre points datés
(`migrate` le 2026-08-22 ; conservation des anciens `.md` le 2026-08-22 ; `pyrightconfig.json` et
`.gitignore` ratifiés le 2026-08-23 ; écart sur `done/revues/` ratifié le 2026-08-20) : ils font foi
sur le brief. Cet audit reprend la numérotation à **R15** ; les constats R1 à R14 sont ceux de
l'audit intermédiaire du 2026-08-23, dont l'état est repris ci-dessous.

### Vérifications exécutées

Toutes lancées par l'auditeur depuis `/home/debian/.claude`, sorties réelles. Les injections ont été
faites **hors du dépôt** (scratchpad), le contrat de l'auditeur interdisant d'écrire ailleurs que
dans ce rapport.

Les 13 contrôles de la section *Vérification* du plan :

| # | Commande | Sortie réelle | Verdict |
|---|---|---|---|
| 1 | `bash scripts/check-pipeline.sh` | `Pipeline conforme.`, 6 contrôles verts | code 0 |
| 2 | `validate` sur les 3 listes | `17`, `7`, `0` élément(s) conformes ; contrats présents | code 0 |
| 3 | marqueur résiduel + `--filled` × 3 | aucune sortie ; `17`, `7`, `0` remplis et conformes | code 0 |
| 4 | conservation `find … \| wc -l` | **24** | ok |
| 5 | `grep -ril 'dette\|debt' skills/list-dir/` | aucune sortie | code 1 |
| 6 | stdlib seule (2 greps) | aucune sortie sur les deux | ok |
| 7 | API publique | `17 éléments` puis `/inexistant: répertoire introuvable` | ok |
| 8 | pas de logique métier dans `commands/` | aucune sortie | ok |
| 9 | définition unique des marqueurs | `À REMPLIR: 1`, `OPTIONNEL: 1` | ok |
| 10 | `help \| grep -c '^  [a-z]'` | **10** | ok |
| 11 | dépendance absente par injection | code **1**, nomme l'outil (ci-dessous) | ok |
| 12 | flux de revue de bout en bout | 17 → rouge → rempli → 17 blocs, 0 marqueur, 0 `Arbitrage` | ok |
| 13 | `git log --follow` après `move` | 3 commits, remonte au commit de création | ok |

Les quatre contrôles rouges signalés en R11 à l'audit intermédiaire (#6, #8, #9, #10) sont **verts**,
et l'ont été sans que le code soit tordu pour eux : le plan a été corrigé. **R11 est levée.**

Sortie recopiée telle que le brief l'exige (contrôle 11, injection d'une commande jetable déclarant
`REQUIRES = ["outil-absent-xyz"]` dans une liste créée hors dépôt) :

```
« probe » exige outil-absent-xyz — introuvable dans le PATH. Déclaré par REQUIRES dans
/tmp/…/audit.FUAr/essai/.list/commands/probe.py.
code=1
```

Contrôle 13, sur le dépôt réel, sans aucune écriture git de ma part — les deux commits de test
existent déjà sur la branche (`f088665` aller, `0853f31` retour) :

```
$ git show --stat -M f088665
 .../{technical-debt => technical-debt-solde}/chemin-skill-code-en-dur.md | 0
 1 file changed, 0 insertions(+), 0 deletions(-)

$ git log --follow --oneline f088665 -- …/technical-debt-solde/chemin-skill-code-en-dur.md
f088665 test(move): aller — chemin-skill-code-en-dur
1395421 format-registres: session 1 — étape 13 les trois listes permanentes   ← création

$ git diff --stat 7040218 0853f31 -- .claude/implementation/todo   → vide (aller-retour neutre)
```

**R3 de l'audit intermédiaire est levée** : le critère de traçabilité du brief est désormais servi
sur le dépôt réel, renommage pur (0 ligne changée) et historique traversé jusqu'au commit de
création.

Vérifications supplémentaires, hors plan :

- Conservation de la migration confrontée aux `.md` figés, encore présents : `technical-debt.md`
  porte **17** titres `^## `, `technical-debt-solde.md` **7** ; les 24, préfixe de date retiré, se
  retrouvent **un à un** dans le champ `title` des listes — 0 manquant.
- Conservation de bout en bout du flux de revue mesurée sur les **titres** et pas seulement sur un
  comptage : les 17 `title` du registre présents dans l'aggloméré, 0 manquant.
- Contrôle contre le registre après retrait d'une fiche (R1) : `merge` sort **0**, et le `test`
  contre `list technical-debt` détecte l'écart. **R1 est levée** — le SKILL de `debt-review` porte le
  contrôle à l'Étape 1 et le rejoue à l'Étape 3, avec le mode de défaillance écrit.
- `git ls-files skills/debt-review` → 4 fichiers, tous `.md` ; `skills/debt-review/scripts/` n'existe
  plus ; `grep -rn 'trier-revue' skills/` → aucune sortie.
- Contrôle 6 de `check-pipeline.sh` éprouvé **par injection hors dépôt**, sur une arborescence
  `skills/x/SKILL.md` jetable : les deux appels relatifs non gardés (`bash scripts/injecte.sh` et
  `python3 scripts/list-dir.py`) sont détectés ; l'appel absolu, l'appel relatif gardé par
  `[ -f … ]`, `python3 -c` et `python3 "$L"` passent. **L'extension de l'étape 21 tient.**
- `uvx basedpyright` → `0 errors, 0 warnings, 0 notes`, depuis la racine du dépôt **et** depuis
  `skills/list-dir/`. `uvx ruff check skills/list-dir` → `All checks passed!`. **R14 est levée** : le
  lanceur (`uvx`) est déclaré dans la section *Dépendances* de `contrat.md`, avec le mode de
  défaillance. J'ai pu rejouer ce que le suivi affirme.
- `git status --short` → `M settings.json` seul, étranger au chantier. Rien sous `done/`.

Non exécutée : aucune. Le seul contrôle que je ne pouvais pas produire moi-même (#13, qui exige des
commits) était déjà matérialisé sur la branche et vérifiable en lecture.

### Conformité à l'intention

Critère par critère, tel que le brief les énonce.

- **« une revue complète des 17 entrées actives tourne sur ce flux, et le fichier aggloméré est
  archivé sous `done/revues/<date>-revue.md` »** — première moitié **atteinte et vérifiée** par moi :
  `derive` → remplissage mécanique → `merge` sur les 17 entrées réelles, 17 blocs, 0 marqueur, 0
  section optionnelle non remplie, et les 17 titres retrouvés un à un. Seconde moitié **non servie**,
  écart ratifié le 2026-08-20 et écrit au suivi comme au plan. **R2 subsiste** sous une forme
  atténuée : la procédure de `debt-review` construit bien le chemin exigé
  (`R=".claude/implementation/done/revues/$(date +%F)"`, rapport en `"$R-revue.md"`), donc la lettre
  du critère sera servie par construction à la première revue post-clôture — mais rien dans ce
  chantier ne l'exécute, et aucun contrôle ne l'établit.
- **« la commande de validation passe sur les quatre répertoires-listes … et échoue sur un élément
  dont un champ du contrat manque »** — **atteint et vérifié**. Les trois listes permanentes passent
  (17/7/0) ; la quatrième, la liste de revue dérivée, passe elle aussi (17 conformes) et sort 1 avec
  85 manquements avant remplissage, en nommant chaque champ et chaque section.
- **« un élément déplacé reste suivi : `git log --follow` … »** — **atteint et vérifié sur le dépôt
  réel** (ci-dessus). R3 levée.
- **« conservation vérifiée par commande : autant d'éléments agglomérés que d'éléments dans le
  répertoire, l'écart faisant échouer »** — **atteint** au sens du brief : `merge` recompte les
  `^## ` du document rendu face aux fichiers présents et échoue sur l'écart. Le trou connu (une fiche
  supprimée réduit les deux comptes) est désormais **couvert hors de `merge`**, contre le registre,
  et documenté dans le SKILL avec sa mesure. Voir toutefois **R15** ci-dessous sur la forme de ce
  contrôle.
- **« le skill générique ne connaît aucun de ses consommateurs »** — **atteint et vérifié** :
  `grep -ril 'dette\|debt' skills/list-dir/` sans sortie. Confirmé côté conception : le gabarit
  `review.{toml,md}` vit dans `.list/templates/` de la liste source, pas dans le skill.
- **« un script dont un outil déclaré manque sort non nul en le nommant, éprouvé par injection et la
  sortie recopiée dans le rapport d'audit »** — **atteint et vérifié**, sortie recopiée ci-dessus.
- **« `trier-revue.sh` est supprimé, ses garanties reprises par les commandes génériques »** —
  **atteint et vérifié**. Découpage → `derive` ; comptage → `merge` + le contrôle contre le registre ;
  refus d'un bloc mal formé → `validate` ; fiche non instruite → `validate --filled`.
- **« les commandes n'importent que la stdlib »** — **atteint et vérifié**, les deux greps du plan
  muets.
- **« `scripts/check-pipeline.sh` passe au vert »** — **atteint et vérifié**, 6 contrôles verts.

**Hors-périmètre** — respecté sur les trois points nommés : rien sur Neovim, `road-map.md` toujours
inexistante (`todo/README.md` l'annonce comme perspective sans la créer), briefs, suivis et rapports
d'audit restent des documents.

**Signaux de dérive** — aucun matérialisé. Le sixième (« si le diff dépasse la réécriture de
`debt-review` et des registres ») s'était déclenché à l'audit intermédiaire (R4) : il est **ratifié
le 2026-08-23** par élargissement daté du périmètre, avec motif et option rejetée au journal.
**R4 est levée.** Les trois autres dépassements du diff sont couverts : `scripts/migrate-dette.py` et
les deux `.md` figés sont conservés pour cet audit et supprimés à la clôture ; l'extension du
contrôle 6 de `check-pipeline.sh` est l'étape 21, prévue au plan.

**Symptôme d'origine** — **disparu** sur le périmètre traité, et je l'ai éprouvé : les 24 entrées
sont 24 fichiers comptés par `find | wc -l`, filtrés par `--where`, triés par `--sort`, validés
contre un contrat, agglomérés par commande, et l'API rend des `Result` typés à un script tiers en
trois lignes d'amorçage.

### Qualité du code

Les constats de l'audit intermédiaire ont été retestés au commit audité. Ceux qui suivent sont
**toujours vivants** et n'ont reçu ni correction ni entrée au registre de dette.

**R5 — les deux marqueurs sont toujours recopiés en dur dans le gabarit.**
`.claude/implementation/todo/technical-debt/.list/templates/review.md` : 4 occurrences de
`<À REMPLIR>`, 2 de `<OPTIONNEL>`. Le contrôle 9 du plan ne balaie que
`skills/list-dir/scripts/` et reste aveugle à ce fichier. Si `PLACEHOLDER` changeait, `--filled`
laisserait passer une fiche vierge pour instruite. Le mode de défaillance est écrit au journal du
suivi (« le corps d'une section de gabarit est exactement le marqueur ») mais aucune commande ne le
vérifie.

**R6 — un bloc de code contenant une ligne `## ` casse toujours l'élément qui le porte, et ce n'est
écrit nulle part.** `items.py:49` (`line.startswith("## ")`) ne tient pas compte des délimiteurs
` ``` `. Éprouvé au commit audité, sur une fiche de revue dont la section `Vérifié par` contient une
sortie de commande réaliste :

```
…/revue/clause-arbre-propre-sans-le-plan.md: section « un titre dans la sortie » — non déclarée au contrat
…/revue : 1 manquement
```

Ce constat s'est **aggravé** depuis l'audit intermédiaire : la refonte de `debt-review` demande
explicitement, dans `review.md` du gabarit comme dans `gabarit-rapport.md`, d'écrire dans
`Vérifié par` « la commande exécutée et **sa sortie réelle** ». Une sortie contenant une ligne `## `
— celle de `grep` sur un Markdown, par exemple, ce que fait la moitié des contrôles de ce dépôt —
rendra la fiche invalide sans qu'aucun message n'explique pourquoi. Ni `contrat-liste.md` ni le
`SKILL.md` de `list-dir` ni celui de `debt-review` ne mentionnent la contrainte, et il n'existe aucun
échappement.

**R9 — `init_list` écrit toujours du TOML non échappé, et rend 0 sur un fichier invalide.**
`store.py:616`. Éprouvé au commit audité :

```
$ list-dir.py init r9 --name 'ma "liste"'
r9/.list/contract.toml
init code=0
$ head -1 r9/.list/contract.toml
name = "ma "liste""
$ list-dir.py validate r9
r9/.list/contract.toml: TOML invalide — Expected newline or end of document after a statement (at line 1, column 13)
validate code=1
```

La commande d'amorçage du skill produit une liste inutilisable **en signalant un succès**. C'est le
seul endroit du paquet où du TOML est émis sans passer par le sérialiseur borné d'`items.py`, et la
règle du plan « `validate` relit ce qui vient d'être écrit » n'y est pas appliquée. C'est, de tous
les constats vivants, celui dont le mode de défaillance est le plus proche de ce que le chantier
existe pour supprimer : un échec silencieux sur de la structure de données.

**R8 — le champ `source` reste déclaré « verbatim » sans l'être tout à fait.** Le contrat dit
« le chantier qui l'a identifiée et où il l'a écrit, verbatim » ; la ligne source
`*Identifié par …*` perd ses délimiteurs d'italique. Le texte est entier, la promesse du mot
« verbatim » ne l'est pas.

**R10 — `where` compare toujours les valeurs sous forme textuelle** (`store.py:90`,
`str(it.fields.get(k)) == str(v)`). Mesuré au commit audité : `--where category=None` sort **0** sans
résultat plutôt que de refuser une valeur hors énumération, alors que `--where category=aggravee`
rend bien son élément. Piège borné, non documenté.

**R15 — le contrôle de complétude d'une revue signale par `echo`, pas par un code de sortie.**
`skills/debt-review/SKILL.md:122` et `:190` :

```bash
test "$(python3 "$L" list "$R" | wc -l)" -eq "$(python3 "$L" list "$T/technical-debt" | wc -l)" \
  || echo "ÉCHEC : autant de fiches que d'entrées attendu"
```

C'est le contrôle qui referme le trou de R1, et il est le seul de la revue à ne pas vivre dans une
commande — donc le seul dont le résultat dépende de ce qu'un lecteur en fait. Le brief exige que
« l'écart faisant échouer » ; ici l'écart *s'affiche*. Dans une session où la sortie défile, un
`ÉCHEC :` en prose au milieu d'un bloc vert est exactement ce qu'on rate. Le reste du dépôt écrit
plutôt `|| { echo …; false; }` (contrôles 3, 6, 9 du plan) : le style existe, il n'est pas suivi ici.

Style et lisibilité, hors constat : le paquet reste idiomatique et homogène avec le dépôt —
docstrings qui disent le *pourquoi*, messages d'erreur en français nommant le fichier et la cause,
échec fermé partout ailleurs. `basedpyright` en mode `all` passe sur 19 fichiers, ce qui n'est pas
un acquis banal. La refonte de `debt-review` (SKILL, `categories.md`, `gabarit-rapport.md`,
`exemple-revue.md`) est cohérente et porte ses modes de défaillance mesurés.

### Dette induite

**R13 — `scripts/migrate-dette.py` dépasse toujours la norme de 100 colonnes sur 19 lignes**
(mesuré au commit audité). Le fichier est jetable et sa suppression est un point de clôture : le coût
s'éteint avec lui, à condition que la suppression ait effectivement lieu.

**R16 — la clôture doit supprimer trois fichiers et aplatir deux commits de test, et rien
d'automatique ne le rappellera.** Restent au commit audité : `todo/technical-debt.md`,
`todo/technical-debt-solde.md`, `scripts/migrate-dette.py`, plus les commits `f088665` et `0853f31`
(`test(move): aller` / `retour`). Le suivi et `todo/README.md` les annoncent tous les cinq comme
points de clôture, ce qui est la bonne façon de le tenir ; mais si la fusion partait en l'état, le
dépôt porterait deux registres dont l'un est déclaré mort par sa propre documentation — la situation
même que le brief interdit. À noter aussi : l'aplatissement de la branche effacera les deux commits
qui **démontrent** le critère `git log --follow`. La démonstration est consignée ici et dans le
suivi ; le mécanisme, lui, survit puisqu'il est dans `move`.

**R17 — la claim d'outillage du suivi n'est pas reproductible telle qu'elle est écrite.** Le suivi
affirme « `uvx ruff check .` → *All checks passed!* » depuis la racine. Mesuré au commit audité :

```
$ uvx ruff check .        (ruff 0.16.4, depuis /home/debian/.claude)
PLW1510  statusline-command.py:47   subprocess.run sans check explicite
BLE001   statusline-command.py:63   Do not catch blind exception
BLE001   statusline-command.py:110  Do not catch blind exception
Found 3 errors.
```

Les trois erreurs sont dans un fichier **antérieur au chantier et jamais touché par lui** — ce n'est
donc pas un défaut du code produit. Ce qui est en cause est la phrase : elle décrit un vert que la
commande citée ne rend pas, et la section *Dépendances* nouvellement écrite invite précisément à
rejouer cette commande. Restreinte au périmètre du chantier
(`uvx ruff check skills/list-dir`), elle est exacte : *All checks passed!*. À préciser, sans quoi le
prochain qui la rejoue conclura à une régression.

**R18 — sept constats de l'audit intermédiaire sont laissés ouverts sans trace dans le registre de
dette.** R2, R5, R6, R8, R9, R10 et R13 ne sont ni corrigés ni versés : `grep -rl 'format-registres'
todo/technical-debt/` ne rend aucun fichier, et aucune des 17 entrées ne les porte. Le suivi écrit
« Réserves d'audit : toutes traitées », ce qui n'est vrai que des quatre qui l'ont été (R1, R7, R11,
R12) plus R4 ratifiée. `cloture.md` §2 fait pourtant de l'alimentation du registre à partir des
réserves d'audit une étape de la clôture, et c'est l'orchestrateur qui écrit : la clôture n'ayant pas
eu lieu, ce n'est pas encore un manquement — c'en devient un si elle a lieu sans. Coût futur direct :
le premier chantier qui reprendra `list-dir` ne saura pas que `init` peut écrire un contrat invalide
en rendant 0.

### Bloquants

Aucun. Le chantier peut être clos, à trois conditions que l'utilisateur doit trancher lui-même :

1. verser au registre de dette les constats vivants (R5, R6, R8, R9, R10, et R2 si l'archive de revue
   reste non produite) — ou décider explicitement de ne pas le faire (**R18**) ;
2. exécuter la suppression annoncée des deux `.md` figés et de `scripts/migrate-dette.py`, et
   l'aplatissement des deux commits de test (**R16**, qui éteint **R13**) ;
3. corriger ou préciser la phrase d'outillage du suivi (**R17**).

**R9** mérite d'être regardée en premier : c'est un échec silencieux dans la commande d'amorçage d'un
skill destiné à être déployé ailleurs, et le brief fait de l'échec silencieux le défaut à ne pas
reproduire.

## 2026-08-23 — clôture (2e passe) — `6fed940`

**Verdict** : DÉFAVORABLE

Périmètre jugé : les 24 étapes du suivi, toutes `[x]`, et **en particulier le diff
`6a29af7..6fed940`** (6 fichiers, +441/-12) que les étapes 23 et 24 ont produit et que personne
n'avait jugé. Brief lu, suivi lu, plan lu (section *Vérification*, 13 contrôles). Cet audit reprend
la numérotation à **R19** ; R1 à R18 sont ceux des deux audits précédents, et leur état est repris
plus bas. Les élargissements de périmètre datés du suivi (`migrate`, `.md` figés conservés,
`pyrightconfig.json` + `.gitignore`, écart `done/revues/`) font foi sur le brief.

### Vérifications exécutées

Toutes lancées par l'auditeur depuis `/home/debian/.claude`, sorties réelles. Toute injection a été
faite **hors du dépôt** (scratchpad), le contrat de l'auditeur interdisant d'écrire ailleurs que dans
ce rapport. Aucune commande `git` d'écriture.

Les 13 contrôles du plan, au commit audité :

| # | Contrôle | Sortie réelle | Verdict |
|---|---|---|---|
| 1 | `bash scripts/check-pipeline.sh` | `Pipeline conforme.`, 6 contrôles verts | code 0 |
| 2 | contrats + `validate` × 3 | `18`, `7`, `0` élément(s) conformes | code 0 |
| 3 | marqueur résiduel + `--filled` × 3 | aucune sortie ; `18`, `7`, `0` remplis et conformes | code 0 |
| 4 | conservation `find … \| wc -l` | **25** (le plan annote « → 24 », voir R23) | voir R23 |
| 5 | `grep -ril 'dette\|debt' skills/list-dir/` | aucune sortie | code 1 |
| 6 | stdlib seule (2 greps) | aucune sortie sur les deux | ok |
| 7 | API publique | `18 éléments` puis `/inexistant: répertoire introuvable` | ok |
| 8 | pas de logique métier dans `commands/` | aucune sortie | ok |
| 9 | définition unique des marqueurs | `À REMPLIR: 1`, `OPTIONNEL: 1` | ok |
| 10 | `help \| grep -c '^  [a-z]'` | **10** | ok |
| 11 | dépendance absente, par injection hors dépôt | code **1** (sortie ci-dessous) | ok |
| 12 | flux de revue de bout en bout | 18 fiches → `--filled` vert → `merge` code 0 | ok, **mais voir R19** |
| 13 | `git log --follow` après `move` | `f088665` puis `1395421` (création) | ok, en lecture seule |

Sortie du contrôle 11, recopiée comme le brief l'exige :

```
« probe » exige outil-absent-xyz — introuvable dans le PATH. Déclaré par REQUIRES dans
liste/.list/commands/probe.py.
code=1
```

Non-régression, après les deux correctifs — je l'ai rejouée moi-même :

- aller-retour octet pour octet sur les **25** éléments réels des trois listes : `25 éléments relus,
  0 écart(s)` ;
- `uvx ruff check skills/list-dir` → `All checks passed!` ; `uvx basedpyright` → `0 errors,
  0 warnings, 0 notes` ;
- `git status --short` → `M settings.json` seul, étranger au chantier ; rien sous `done/`.

**Non exécutée** : aucune.

### Ce que les correctifs 23 et 24 ont réellement produit

**R19 — le correctif de R6 déplace la panne de `validate` vers `merge`, et la documentation livrée
affirme le contraire.** C'est le constat bloquant.

`parse_sections` ignore désormais les `## ` entre fences (`items.py:44-83`), donc `validate` accepte
une fiche portant une sortie de commande. Mais `merge_text` recompte les `^## ` **sur le document
rendu** (`store.py:539-550`) et ce recomptage, lui, n'a pas appris les fences : chaque `## ` collé
dans un bloc de code compte pour un élément de plus. Mesuré sur le cas d'usage de référence —
`derive` des 18 entrées réelles vers le scratchpad, remplissage mécanique, puis une seule section
`Vérifié par` recevant une sortie de `grep` réaliste :

```
$ python3 "$L" validate ./rev --filled
rev : 18 élément(s) remplis et conformes au contrat        code=0
$ python3 "$L" merge ./rev --out r2.md
rev: 20 élément(s) dans le document pour 18 fichier(s) dans le répertoire — un élément
a été perdu ou dédoublé en route
code=1
```

Trois choses en même temps :

1. **le flux de référence casse à sa dernière étape** dès qu'une preuve exécutée est collée telle
   quelle — or c'est ce que `debt-review` demande à chaque fiche ;
2. **le message ment** : rien n'a été perdu ni dédoublé, et il n'y a aucun moyen, depuis ce message,
   de remonter à un bloc de code dans une section ;
3. **le commit audité écrit noir sur blanc que c'est sûr.** `gabarit-rapport.md:62-64`, ajouté par ce
   diff : « Un `## ` qui apparaîtrait dans cette sortie n'ouvre **pas** de section : le découpage
   ignore ce qui est entre fences. **Coller la sortie telle quelle est donc sûr, et c'est ce qui est
   demandé.** » C'est vrai de `validate`, faux de `merge`.

Le commentaire de `store.py:525-528` est devenu faux au même commit : « Le corps d'une section ne
peut pas ouvrir un « ## » : parse_sections aurait découpé là. Le seul texte libre qui puisse casser
le compte est le TITRE ». C'est précisément l'invariant que l'étape 24 a supprimé, et le commentaire
qui autorisait le recomptage naïf n'a pas été relu.

Avant l'étape 24, ce cas échouait **tôt et clairement** (`section « … » — non déclarée au contrat`).
Après, il passe deux contrôles et tombe au dernier, avec un diagnostic faux, sur le seul chemin qui
produit le livrable de la revue. C'est une régression, pas un reste de R6.

**R20 — le correctif de R9 ne ferme que la moitié du trou : le « sérialiseur borné » émet encore du
TOML invalide, en silence.** `dump_value` (`items.py:105-125`) échappe `\` et `"`, et rien d'autre.
Une chaîne contenant un saut de ligne ou un caractère de contrôle produit une chaîne TOML *basic*
illégale, sans lever `SerialiseError`. Deux chemins d'accès, tous deux mesurés au commit audité.

`init`, la commande d'amorçage — le cas de R9, sur un autre caractère :

```
$ python3 "$L" init l3 --name "$(printf 'deux\nlignes')"
l3/.list/contract.toml
code=0
$ python3 "$L" validate l3
l3/.list/contract.toml: TOML invalide — Illegal character '\n' (at line 1, column 13)
validate=1
```

Et surtout `migrate`, qui est `PROTECTED` et réécrit les registres réels au nom du contrat. Un
élément parfaitement valide, dont un champ utilise une chaîne TOML multi-lignes, est **détruit par un
simple réordonnancement**, avec un code 0 et un compte rendu de succès :

```
$ python3 "$L" validate liste                    → liste : 2 élément(s) conformes    code=0
$ python3 "$L" migrate liste
liste/gamma.md: front matter — champs réordonnés selon le contrat
liste : 1 changement appliqué                                                        code=0
$ python3 "$L" validate liste
liste/gamma.md: front matter TOML invalide — Illegal character '\n' (at line 2, column 18)
                                                                                     code=1
```

Le journal du suivi conclut de R9 que « le sérialiseur borné devient le seul chemin d'écriture TOML
du paquet, sans exception ». C'est exact, et c'est le problème : le chemin unique est lui-même
incomplet, et la règle 3 du plan — « `validate` relit ce qui vient d'être écrit » — n'est appliquée
ni par `init` ni par `migrate`. Aucune des 25 entrées réelles n'utilise de chaîne multi-lignes
aujourd'hui : le défaut est armé, pas déclenché. Réserve, pas bloquant — mais c'est exactement le
mode de défaillance que le chantier existe pour supprimer, et le second audit consécutif où il est
signalé.

**R21 — la clôture de fence ne suit pas CommonMark là où la docstring l'affirme, et la section
fantôme réapparaît.** `FENCE` (`items.py:44`) accepte comme clôture toute ligne de ≥ N caractères du
même type, **y compris suivie d'une chaîne d'information**. CommonMark interdit l'info-string sur une
clôture : ` ```python ` à l'intérieur d'un bloc est du contenu. Mesuré :

```
corps : ## Constat / ``` / ```python / ## pas un titre / ```
sections lues : ['Constat', 'pas un titre']
```

Coller un extrait de Markdown documenté — ce que fait la moitié des fiches de ce dépôt — rouvre donc
le trou de R6, et la docstring (« Suivi de clôture au sens CommonMark ») dit que non. Le cas à quatre
backticks, lui, est correct : je l'ai vérifié.

**R22 — une fence non fermée avale silencieusement les sections suivantes.** Un bloc ouvert et jamais
refermé fait disparaître tout `## ` postérieur : `sections lues : ['Constat']` là où le fichier en
porte deux. Le comportement est conforme à CommonMark et l'aller-retour reste exact (`round-trip:
True`), mais si la section avalée est requise, `validate` dira « section manquante » sur une section
qui est écrite dans le fichier, sous les yeux du lecteur. Aucun message ne mentionne la fence. Coût
borné, diagnostic trompeur.

**R23 — le contrôle 4 du plan annote « → 24 » et le dépôt en compte 25.** L'entrée
`listdir-sans-suite-de-tests`, versée le 2026-08-23 sur demande de l'utilisateur, porte le registre
actif à 18 et le total à 25. Le plan, le suivi (« 24/24 », « les 24 entrées ») et
`todo/technical-debt.md` figé (17 titres) énoncent tous l'ancien compte. Rien n'est cassé — le
contrôle n'affiche qu'un nombre — mais c'est un contrôle dont l'attendu écrit est désormais faux, ce
que R11 avait déjà coûté une fois.

**R24 — la phrase insérée dans `gabarit-rapport.md` n'a pas été re-justifiée.** Ligne 64 : 115
caractères, quand les lignes voisines du même paragraphe font 89 à 98. Le paragraphe a été édité par
insertion, pas réécrit. Détail de style, dans un dépôt qui tient sa marge partout ailleurs.

### Conformité à l'intention

Critère par critère, tel que le brief les énonce.

- **« une revue complète des 17 entrées actives tourne sur ce flux, et le fichier aggloméré est
  archivé sous `done/revues/<date>-revue.md` »** — première moitié **atteinte** avec un contenu
  neutre (18 entrées aujourd'hui, `merge` code 0, 18 blocs), **mise en échec** dès qu'une fiche porte
  une preuve exécutée collée telle quelle (R19). Seconde moitié **non servie**, écart ratifié le
  2026-08-20 : **R2 subsiste** inchangée.
- **« la commande de validation passe sur les quatre répertoires-listes … et échoue sur un élément
  dont un champ du contrat manque »** — **atteint et vérifié** : `18`/`7`/`0` sur les permanentes, et
  la liste de revue dérivée valide elle aussi ; un champ requis retiré sort 1 en le nommant.
- **« un élément déplacé reste suivi »** — **atteint**, vérifié en lecture seule sur `f088665`, qui
  remonte à `1395421`.
- **« conservation vérifiée par commande : autant d'éléments agglomérés que d'éléments dans le
  répertoire, l'écart faisant échouer »** — **non atteint au commit audité**. Le contrôle échoue
  toujours sur un écart, mais il échoue **aussi sur des documents conformes** (R19) : un contrôle de
  conservation qui rend faux positif sur le contenu que la procédure demande d'écrire ne prouve plus
  la conservation, il l'empêche. C'est le critère que je tiens pour manqué.
- **« le skill générique ne connaît aucun de ses consommateurs »** — **atteint et vérifié**, aucune
  sortie.
- **« un script dont un outil déclaré manque sort non nul en le nommant, éprouvé par injection »** —
  **atteint et vérifié**, sortie recopiée ci-dessus.
- **« `trier-revue.sh` est supprimé, ses garanties reprises »** — **atteint**, `skills/debt-review`
  ne contient que des `.md`.
- **« les commandes n'importent que la stdlib »** — **atteint et vérifié**, les deux greps muets.
  `re`, ajouté par l'étape 24, est stdlib et déjà dans l'allowlist du plan.
- **« `scripts/check-pipeline.sh` passe au vert »** — **atteint et vérifié**, 6 contrôles verts.

**Hors-périmètre** — respecté : rien sur Neovim, `road-map.md` toujours inexistante, briefs, suivis
et rapports d'audit restent des documents. Le diff de cette session ne touche que `listdir`,
`debt-review`, un registre et les fichiers de chantier.

**Signaux de dérive** — aucun nouveau matérialisé. Le sixième reste couvert par l'élargissement
ratifié le 2026-08-23. À noter que le troisième (commit mêlant déplacement et réécriture) n'est pas
en cause ici : `6fed940` ne déplace rien.

**Symptôme d'origine** — **disparu** sur le périmètre traité, R19 ne le remet pas en cause : les
données restent des fichiers comptables, filtrables et validables. C'est l'agglomération, dernière
étape, qui refuse un contenu légitime.

### État des constats antérieurs

Levés à cette passe :

- **R9 — partiellement levée.** Le cas guillemet/antislash est corrigé et je l'ai revérifié
  (`name = "ma \"liste\""`, `validate` code 0). Le mode de défaillance générique survit : voir R20.
- **R6 — levée pour `validate`, rouverte ailleurs.** Voir R19 (merge) et R21 (info-string).

Toujours vivants, revérifiés au commit audité, sans correction ni entrée au registre :

- **R2** — l'archive `done/revues/` n'est produite par aucun contrôle de ce chantier.
- **R5** — `templates/review.md` recopie les marqueurs en dur (4 × `<À REMPLIR>`), hors de portée du
  contrôle 9.
- **R8** — `source` déclaré « verbatim » perd les délimiteurs d'italique.
- **R10** — `where` compare textuellement ; `--where category=None` reste un piège non documenté.
- **R13** — `scripts/migrate-dette.py` dépasse la marge du dépôt ; s'éteint avec sa suppression.
- **R15** — le contrôle de complétude de `debt-review` signale toujours par `echo`, sans code de
  sortie : `SKILL.md:123` et `:191`, inchangés.
- **R16** — restent à supprimer `todo/technical-debt.md`, `todo/technical-debt-solde.md`,
  `scripts/migrate-dette.py`, et à aplatir `f088665`/`0853f31`. **Aggravé** : le registre figé porte
  17 entrées quand la liste en porte 18 — les deux registres divergent désormais en contenu, pas
  seulement en forme.
- **R17** — le suivi (ligne 476) affirme toujours `uvx ruff check .` → vert depuis la racine ; la
  commande rend 3 erreurs dans `statusline-command.py`, fichier étranger au chantier. La ligne 525,
  ajoutée cette session, dit correctement `uvx ruff check skills/list-dir` : les deux phrases
  coexistent dans le même fichier.
- **R18** — un seul constat a été versé au registre (`listdir-sans-suite-de-tests`, sur demande de
  l'utilisateur et hors point 2 de la clôture) ; `grep -rl 'format-registres'` sur la liste active ne
  rend que celui-là. R2, R5, R8, R10, R15 et désormais R20 à R22 ne sont ni corrigés ni tracés.

### Bloquants

1. **R19** — le flux de référence (`derive` → instruire → `merge`) échoue sur un contenu que la
   documentation livrée au même commit déclare sûr, avec un message de diagnostic faux. Tant que le
   recomptage de `merge_text` ignore les fences comme `parse_sections` le fait désormais — ou que la
   phrase de `gabarit-rapport.md` et le commentaire de `store.py:525-528` disent la vérité —, le
   critère de conservation du brief n'est pas servi.

R20 n'est pas retenu comme bloquant : le défaut n'est armé sur aucune donnée réelle. Il mérite
néanmoins d'être tranché avant la clôture, au même titre que le sort de R5, R8, R10, R15, R17, R18
et R21 — soit corrigés, soit versés au registre, jamais laissés ouverts en silence.

## 2026-08-23 — clôture (3e passe) — `b9ca3e6`

**Verdict** : RÉSERVES

Périmètre jugé : les 27 étapes du suivi, toutes `[x]`, et **en particulier le diff
`6fed940..b9ca3e6`** (7 fichiers, +407/-43) produit par les étapes 25 à 27 en réponse au bloquant
R19 et aux réserves R20 et R21 — diff qu'aucun audit n'avait jugé. Brief lu, suivi lu, plan lu
(section *Vérification*, 13 contrôles). Numérotation reprise à **R25** ; R1 à R24 sont ceux des
trois passes précédentes, leur état est repris plus bas. Les élargissements de périmètre datés du
suivi (`migrate`, `.md` figés conservés, `pyrightconfig.json` + `.gitignore`, écart `done/revues/`)
font foi sur le brief.

### Vérifications exécutées

Toutes lancées par l'auditeur depuis `/home/debian/.claude`, sorties réelles. Toute injection a été
faite **hors du dépôt** (scratchpad). Aucune commande `git` d'écriture.

Les 13 contrôles du plan, au commit audité :

| # | Contrôle | Sortie réelle | Verdict |
|---|---|---|---|
| 1 | `bash scripts/check-pipeline.sh` | `Pipeline conforme.`, 6 contrôles verts | code 0 |
| 2 | contrats + `validate` × 3 | `18`, `7`, `0` élément(s) conformes | code 0 |
| 3 | marqueur résiduel + `--filled` × 3 | aucune sortie ; `18`, `7`, `0` remplis et conformes | code 0 |
| 4 | conservation `find … \| wc -l` | **25**, et le plan annote désormais « → 25 » | ok (R23 levée) |
| 5 | `grep -ril 'dette\|debt' skills/list-dir/` | aucune sortie | ok |
| 6 | stdlib seule (2 greps) | aucune sortie sur les deux | ok |
| 7 | API publique | `18 éléments` puis `/inexistant: répertoire introuvable` | ok |
| 8 | pas de logique métier dans `commands/` | aucune sortie | ok |
| 9 | définition unique des marqueurs | `À REMPLIR: 1`, `OPTIONNEL: 1` | ok |
| 10 | `help \| grep -c '^  [a-z]'` | **10** | ok |
| 11 | dépendance absente, par injection hors dépôt | code **1** (sortie ci-dessous) | ok |
| 12 | flux de revue de bout en bout | `derive` 18 → `--filled` code 1 → rempli → `--filled` code 0 → `merge` code 0, préambule `18 élément(s) aggloméré(s), 18 fichier(s)`, `0` marqueur | ok |
| 13 | `git log --follow` après `move` | `0853f31`, `f088665`, puis `1395421` (création) | ok, **en lecture seule** — les deux commits de test préexistent sur la branche, l'auditeur n'en crée aucun |

Sortie du contrôle 11, recopiée comme le brief l'exige :

```
« probe » exige outil-absent-xyz — introuvable dans le PATH. Déclaré par REQUIRES dans
…/liste/.list/commands/probe.py.
code=1
```

Contre-épreuve : la même commande avec `REQUIRES = ["git"]` ne s'arrête plus sur la dépendance —
elle atteint `argparse` et sort **2** sur un autre motif. L'échec vient donc bien du contrôle de
`REQUIRES`, pas d'ailleurs.

Les trois correctifs, éprouvés un par un sur le commit audité :

```
R19 — fiche portant une sortie de commande réelle collée dans « Vérifié par »
      (bloc ``` contenant « ## un titre dans la sortie » et « ## encore un ») :
      merge → code 0, préambule « 18 élément(s) aggloméré(s), 18 fichier(s) »
      relecture : une seule section, bloc intact (True)

R21 — corps « ## A / ``` / texte / ```python / ## pas une section / ``` / ## B » :
      parse_sections → ['A', 'B']   (le « ## » du bloc reste du contenu)

R20 — aller-retour tomllib par dump_value :
      'ligne1\nligne2'          → "ligne1\nligne2"           relu identique : True
      'guillemet " et \ dedans' → "guillemet \" et \\ dedans" relu identique : True
      'tab\tici', 'retour\rchariot'                          relu identique : True
      'avec \x07 cloche'        → SerialiseError : « champ « k » : caractère de
                                  contrôle U+0007 — aucune écriture TOML sur une
                                  ligne ne le porte »
```

Non-régression, rejouée par l'auditeur :

- aller-retour octet pour octet sur les **25** éléments réels des trois listes : `25 éléments,
  0 écarts` ;
- `uvx ruff check skills/list-dir` → `All checks passed!` ; `uvx basedpyright` depuis la racine →
  `0 errors, 0 warnings, 0 notes` ;
- conservation encore capable de refuser un vrai écart : un `title` portant une ligne `## ` →
  `19 élément(s) dans le document pour 18 fichier(s) … un élément a été perdu ou dédoublé` ;
- `git status --short` → `M settings.json` seul, étranger au chantier ; rien sous `done/`.

**Non exécutée** : aucune, hormis les commits du contrôle 13, interdits à l'auditeur et déjà
présents sur la branche (`f088665`, `0853f31`), dont j'ai vérifié l'effet en lecture.

### Ce que le correctif a produit

**R19 est levée, et levée à la bonne profondeur.** La règle des blocs de code devient une fonction
unique, `outside_fences` (`items.py:48-76`), dont `parse_sections` et `ListStore.merge_text` sont
les deux seuls appelants — j'ai vérifié qu'aucune troisième boucle de fences ne subsiste dans le
paquet. C'est le correctif structurel, pas le rustinage : la divergence qui avait produit R19 ne
peut plus se reformer par édition d'un seul côté. Les deux textes qui mentaient au commit précédent
sont corrigés au même endroit : le commentaire de `store.py:532-536` dit maintenant l'inverse de ce
qu'il affirmait, et `gabarit-rapport.md` remplace « le découpage ignore ce qui est entre fences »
par « le découpage **comme le recomptage** ignorent ce qui est entre fences ».

**R20 est levée.** `dump_value` échappe `\n \r \t \b \f` et **refuse** tout autre caractère de
contrôle (`< 0x20` ou `0x7F`) par `SerialiseError`. L'ordre des substitutions est correct — `\` puis
`"` puis les échappements — donc pas de double traitement, et le balayage final porte sur la chaîne
**après** échappement, ce qui ne laisse passer que les caractères réellement sans écriture légale.
Effet de bord constaté et sain : un champ multi-lignes est désormais écrit puis relu à l'identique
(vérifié sur un `title` portant un saut de ligne).

**R21 est levée.** Une clôture ne porte plus d'info string (`not info.strip()`), et une info string
de bloc à backticks ne peut plus contenir de backtick — les deux règles CommonMark que la docstring
revendiquait. Le cas à quatre backticks reste correct.

**R24 est levée** : la ligne 64 de `gabarit-rapport.md` est repassée sous la marge ; les deux seules
lignes longues du fichier sont des lignes de tableau, non repliables, antérieures au commit.

**R23 est levée** : le contrôle 4 du plan annote « → 25 » et motive l'écart. Le dépôt en compte 25.

**R25 — le faux positif de conservation subsiste sur une variante étroite : une fence non refermée
dans la dernière section d'un élément.** C'est le versant `merge` de R22, et il n'a pas été traité.
Mesuré au commit audité, sur une fiche par ailleurs complète :

```
$ validate --filled   → OK, aucun manquement (code 0)
$ merge               → 1 élément(s) dans le document pour 18 fichier(s) dans le
                        répertoire — un élément a été perdu ou dédoublé en route
```

Rien n'a été perdu : un bloc ouvert et jamais refermé absorbe tous les `## ` postérieurs du document
rendu, y compris les titres des 17 autres éléments. Deux différences avec R19, qui font que je ne le
retiens pas comme bloquant : le déclencheur n'est pas ce que la procédure demande d'écrire (il faut
un nombre **impair** de lignes de fence dans une section, ce qui est du Markdown malformé), et
l'échec est **fermé** — code non nul, aucun fichier écrit. La réserve porte sur le diagnostic : le
message désigne une perte d'élément là où la cause est un bloc de code non refermé, et aucun message
du paquet ne nomme jamais une fence. Le remède naturel — `validate` refusant un corps dont une fence
reste ouverte — n'existe pas.

Quand la fence impaire tombe dans une section **non** terminale, le défaut est en revanche rattrapé
tôt et proprement : les sections suivantes sont avalées, `validate` sort 1 en les déclarant
manquantes, `merge` refuse. Le diagnostic reste trompeur (R22, inchangée), mais l'élément ne franchit
aucun contrôle.

### Conformité à l'intention

Critère par critère, tel que le brief les énonce.

- **« une revue complète des 17 entrées actives tourne sur ce flux, et le fichier aggloméré est
  archivé sous `done/revues/<date>-revue.md` »** — première moitié **atteinte et vérifiée** : le flux
  tourne sur les 18 entrées d'aujourd'hui, **y compris avec une preuve exécutée collée telle
  quelle**, ce qui était le point de rupture de la passe précédente. Seconde moitié **non servie**,
  écart ratifié le 2026-08-20 : **R2 subsiste** inchangée.
- **« la commande de validation passe sur les quatre répertoires-listes … et échoue sur un élément
  dont un champ du contrat manque »** — **atteint et vérifié** : `18`/`7`/`0` sur les permanentes, la
  liste de revue dérivée valide, et un champ requis manquant sort 1 en le nommant.
- **« un élément déplacé reste suivi »** — **atteint**, vérifié en lecture seule : `git log --follow`
  sur `technical-debt/chemin-skill-code-en-dur.md` remonte à `1395421`, son commit de création.
- **« conservation vérifiée par commande : autant d'éléments agglomérés que d'éléments dans le
  répertoire, l'écart faisant échouer »** — **atteint**, avec la réserve R25. Le contrôle échoue sur
  un vrai écart (titre injecté, mesuré) et n'échoue plus sur le contenu que la procédure demande
  d'écrire. Il conserve un faux positif sur un Markdown malformé, à message trompeur.
- **« le skill générique ne connaît aucun de ses consommateurs »** — **atteint et vérifié**, aucune
  sortie.
- **« un script dont un outil déclaré manque sort non nul en le nommant, éprouvé par injection et la
  sortie recopiée »** — **atteint et vérifié**, sortie recopiée ci-dessus.
- **« `trier-revue.sh` est supprimé, ses garanties reprises »** — **atteint** : `git ls-files
  skills/debt-review` ne rend que quatre `.md`, et aucun fichier suivi ne porte `trier-revue`.
- **« les commandes n'importent que la stdlib »** — **atteint et vérifié**, les deux greps muets.
- **« `scripts/check-pipeline.sh` passe au vert »** — **atteint et vérifié**, 6 contrôles verts.

**Hors-périmètre** — respecté. Le diff de cette session ne touche que `listdir`, `debt-review`, le
plan et les fichiers de chantier : rien sur Neovim, `road-map.md` toujours inexistante, briefs,
suivis et rapports d'audit restent des documents.

**Signaux de dérive** — aucun nouveau matérialisé. Le sixième reste couvert par l'élargissement
ratifié le 2026-08-23 ; le troisième n'est pas en cause, `b9ca3e6` ne déplace rien.

**Symptôme d'origine** — **disparu** sur le périmètre traité, et cette fois sans réserve sur le
dernier maillon : la donnée est en fichiers comptables, filtrables, validables, et l'agglomération
accepte le contenu que la procédure prescrit.

### Qualité du code produit

`outside_fences` est un générateur qui rend `(ligne, hors_bloc)` — la ligne d'ouverture **et** la
ligne de clôture sont marquées « dans le bloc », ce qui est le choix juste pour les deux appelants
et cohérent entre eux. Le nommage suit le paquet (français pour les locales, anglais pour l'API), la
docstring dit *pourquoi* la fonction existe et non ce qu'elle fait — l'idiome du reste du paquet.
`ruff` et `basedpyright` (mode `all`) passent au vert. Aucun défaut de style relevé sur ce diff.

Un point de conception à connaître, sans reproche : la règle des fences est maintenant appliquée
deux fois sur le même contenu — une fois à la lecture de l'élément, une fois sur le document
aggloméré. C'est voulu (« compter deux fois la même variable ne prouverait rien »), et c'est ce qui
rend le contrôle de conservation capable d'attraper un titre injecté. Le coût est que tout contenu
qui trompe la règle la trompe deux fois, en deux endroits aux messages sans rapport — c'est
exactement R25.

### Dette technique induite

Aucune nouvelle. Le correctif **retire** de la duplication (une règle, un endroit) au lieu d'en
ajouter, et la documentation a été corrigée en même temps que le code, aux trois endroits qui
l'affirmaient — c'est ce que la 2e passe reprochait de ne pas avoir été fait.

### État des constats antérieurs

Levés à cette passe, vérifiés : **R19** (bloquant), **R20**, **R21**, **R23**, **R24**.

Toujours vivants, revérifiés au commit audité, sans correction ni entrée au registre :

- **R2** — l'archive `done/revues/` n'est produite par aucun contrôle de ce chantier (écart ratifié).
- **R5** — `templates/review.md` recopie les marqueurs en dur, hors de portée du contrôle 9.
- **R8** — `source` déclaré « verbatim » perd les délimiteurs d'italique.
- **R10** — `where` compare textuellement ; `--where category=None` reste un piège non documenté.
- **R13** — `scripts/migrate-dette.py` dépasse la marge du dépôt ; s'éteint avec sa suppression.
- **R15** — le contrôle de complétude de `debt-review` signale toujours par `echo` sans code de
  sortie : `SKILL.md:123` et `:191`, inchangés.
- **R16** — restent à supprimer `todo/technical-debt.md`, `todo/technical-debt-solde.md`,
  `scripts/migrate-dette.py`, et à aplatir `f088665`/`0853f31`. Le registre figé porte toujours 17
  entrées quand la liste en porte 18 : les deux divergent en contenu.
- **R17** — mesuré à nouveau : le suivi ligne 501 affirme `uvx ruff check .` → vert depuis la racine ;
  la commande rend **3 erreurs** dans `statusline-command.py`, fichier étranger au chantier. Les
  lignes 550 et 578, plus récentes, disent correctement `uvx ruff check skills/list-dir`. Trois
  phrases coexistent dans le même fichier, dont une fausse.
- **R18** — un seul constat est versé au registre (`listdir-sans-suite-de-tests`) : `grep -rl
  'format-registres'` sur la liste active ne rend que celui-là. R2, R5, R8, R10, R15, R22 et
  désormais R25 ne sont ni corrigés ni tracés.
- **R22** — inchangée, et complétée par R25 ci-dessus.

### Bloquants

Aucun. Le bloquant de la 2e passe est levé et je l'ai éprouvé sur le cas exact qui l'avait révélé.

La clôture reste conditionnée à ce qui n'est pas du ressort de l'audit : **R16** (suppression des
`.md` figés et de `migrate-dette.py`, aplatissement des deux commits de test) et **R18** — le sort
de R2, R5, R8, R10, R15, R17, R22 et R25 doit être tranché, soit corrigé, soit versé au registre au
point 2 de la clôture. Aucun ne doit rester ouvert en silence : c'est la troisième passe consécutive
où la même liste est reconduite.

Si un seul constat devait être traité plutôt que versé, ce serait **R25** : c'est un contrôle de
conservation qui accuse d'une perte inexistante, dans le seul flux que le chantier existe pour
servir.
