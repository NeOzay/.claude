+++
id = "garde-fou-cinq-angles-morts"
title = "Le garde-fou de pipeline a cinq angles morts connus"
date = 2026-08-14
source = "Identifié par `contrat-pipeline`, R4, R5, R6, R11 et R22 du rapport d'audit."
reviewed = 2026-08-17
category = "pertinent"
+++

## Constat

`scripts/check-pipeline.sh` passe au vert sur cinq situations qu'il devrait signaler,
toutes vérifiées par injection à l'audit :

- **contrôle 1 limité à `skills/`** (ses `grep -r … --include='*.md' skills`) : un renvoi
  `contrat.md#…` écrit dans `CLAUDE.md`, `hooks/` ou `.claude/` échapperait au contrôle d'ancre
  morte. Le motif d'exclusion devrait viser `agents/`, pas « tout sauf `skills/` ».
- **`slugify()` plus étroite que la règle** (`sed "s/['’]//g; s/ /-/g"`) : elle ne retire que les
  apostrophes. Un futur titre de section contenant une virgule ou des parenthèses produirait une
  ancre fausse — invisible au script, les deux côtés de la comparaison passant par la même fonction.
- **contrôle 2 comptant des fichiers, pas des occurrences** (`grep -rl "$motif" … | wc -l`) : deux
  copies d'une même règle dans un seul fichier passent, alors que la règle écrite dit « exactement
  une occurrence ».
- **auto-citation du contrat** : l'exemple de renvoi que `contrat.md` contient sous « Une règle
  déplacée ici laisse … une ligne d'appel portant sa conséquence » satisfait à lui seul le contrôle
  « section jamais citée ».
- **garde textuel du contrôle 6** (`grep -q "\[ -f \"\?$call"`) : `bash scripts/foo.sh   # [ -f
  scripts/foo.sh ]` passe au vert, le test cherchant la chaîne n'importe où dans la ligne sans
  exiger qu'elle commande l'appel ; et `$call` est injecté tel quel dans un motif `grep`, où les
  `.` du chemin sont des métacaractères.

## Soldé le

**Soldé le 2026-08-24 par le chantier `check-pipeline-python`** — les cinq points repris dans la
réécriture Python du garde-fou :

- portée du contrôle 1 étendue à tout le dépôt, `agents/` excepté comme la dette le demandait ;
- `slugify()` retire toute la ponctuation et conserve les accents, au lieu des seules apostrophes ;
- le contrôle 2 compte des **occurrences**, non des fichiers ;
- l'auto-citation du contrat ne vaut plus citation pour « section jamais citée » ;
- le garde du contrôle 6 doit **précéder** l'appel qu'il commande, et le chemin passe par
  `re.escape` avant d'entrer dans un motif.

Établi par : `uvx pytest scripts/tests -q` → **65 passed**, dont un test par point
(`test_portee_hors_skills`, `test_slugify_ponctuation`,
`test_deux_occurrences_dans_un_seul_fichier`, `test_auto_citation_ne_compte_pas`,
`test_garde_en_commentaire_apres_lappel`, `test_point_nest_pas_un_metacaractere`) ; et
`python3 scripts/check_pipeline.py` → 7 contrôles verts, rc 0.

**Restriction assumée sur le premier point** : `.claude/implementation/` reste hors portée, avec
`.git/` et `plugins/`. Archives figées et registre de dette portent des renvois volontairement
morts — dont les deux `contrat.md#autorité)` que la note du 2026-08-17 signalait ici même. Ce sont
des documents datés qu'on ne réécrit pas ; les scanner ferait crier le garde-fou sans qu'aucune
correction soit possible. L'extension est donc **invisible sur l'arbre actuel** (30 renvois avant
comme après) et ne se prouve que par `test_portee_hors_skills`, qui injecte un renvoi mort dans
`CLAUDE.md` et dans `hooks/`.

## Pourquoi c'est gênant

le garde-fou est ce qui doit empêcher la dérive de revenir. Un contrôle
qui ne couvre qu'une écriture du défaut donne surtout de la confiance : `R12` l'a démontré, trois
formes fautives sur quatre passaient au vert un tour après l'écriture du contrôle.

## Pour solder

reprendre les cinq points ; les quatre premiers sont des corrections d'une à trois
lignes, le cinquième demande d'exiger que le garde précède l'appel.

## Assumé

aucune de ces situations n'existe **dans `skills/`**, toutes vérifiées.

**Corrigé le 2026-08-17 par `revue-dette`** — l'**Assumé** disait « aucune de ces situations
n'existe dans le dépôt aujourd'hui », ce qui était faux avant même ce chantier : le premier angle
mort est réalisé hors de `skills/`, où le contrôle ne regarde pas.
Établi par : `grep -rl 'contrat.md#autorité)' --include='*.md' .claude` → 2 fichiers de `done/`,
alors que la section réelle est « Autorité et divergence », d'ancre `#autorité-et-divergence`
(`grep -c '^## Autorité et divergence' contrat.md` → 1). Renvoi mort, hors de la portée du contrôle
1. `#ancre` est dans le même cas. Ces deux-là sont en prose d'exemple, ce qui atténue sans annuler.
