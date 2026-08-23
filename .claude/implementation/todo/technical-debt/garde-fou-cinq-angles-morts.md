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
