+++
id = "typecheckingmode-all-rejete-par-pyright"
title = "pyright rejette le typeCheckingMode « all » de list-dir et vérifie en mode par défaut"
date = 2026-09-09
source = "chantier tableaux-toml-aplatis-a-l-ecriture, audit de clôture R10 — et démontré sur ce chantier même"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

`skills/list-dir/pyrightconfig.json` déclare `"typeCheckingMode": "all"`. C'est un mode propre à
**basedpyright** ; `pyright` ne le connaît pas. Lancé sur ce répertoire, il ouvre sa sortie par :

```
Config "typeCheckingMode" entry must contain "off", "basic", "standard", or "strict".
```

puis vérifie en **mode par défaut**, sans autre avertissement et en rendant un décompte d'apparence
normale. Le fichier de configuration n'est pas invalide : il est écrit pour un outil, et lu par un
autre qui l'ignore silencieusement.

L'écart est mesurable sur le même arbre : `pyright` rend **4 erreurs**, `basedpyright` en rend
**13**. Un contrôle qui passe sous le premier ne dit donc rien de ce que le dépôt croit exiger.

Établi par : `(cd skills/list-dir && npx --yes pyright)` → première ligne de sortie ci-dessus, puis
« 4 errors » ; `(cd skills/list-dir && uvx --with pytest basedpyright)` → aucun message de rejet,
« 13 errors ».

## Pourquoi c'est gênant

Le coût n'est pas théorique : il s'est réalisé pendant le chantier qui a produit cette entrée.

Les trois audits de clôture de `tableaux-toml-aplatis-a-l-ecriture` ont lancé `pyright` et conclu
« 4 erreurs, toutes préexistantes ». Une comparaison ultérieure sous `basedpyright`, contre l'arbre
`master` extrait par `git archive`, a montré **trois erreurs induites par le chantier** —
`Type of "extend" is partially unknown` et deux `reportUnusedParameter` — qu'aucun des trois
passages n'avait pu voir. Elles ont été corrigées, mais elles ont failli être livrées avec la
mention « aucune régression de typage », qui aurait été fausse et vérifiée.

Le mode de défaillance est celui d'un garde-fou qui répond toujours oui : tant que la ligne de
rejet passe pour du bruit, chaque chantier croit contrôler son typage et ne contrôle qu'un
sous-ensemble. Plus le dépôt s'appuie sur ce contrôle, plus la fausse assurance coûte cher.

## Pour solder

Trancher quel outil fait foi, puis rendre la configuration cohérente avec ce choix.

- **basedpyright fait foi** → laisser `"typeCheckingMode": "all"` et écrire quelque part que le
  contrôle de typage de ce dépôt s'exécute par `uvx --with pytest basedpyright`, jamais par
  `pyright`. L'entrée `basedpyright-treize-erreurs-non-tenues` devient alors le travail restant.
- **pyright fait foi** → remplacer `"all"` par `"strict"`, valeur qu'il accepte, et remesurer la
  base : le décompte de référence changera.

Vérification, dans les deux cas : la commande retenue ne doit plus produire de ligne
`Config "typeCheckingMode" entry must contain …`, et le décompte d'erreurs doit être identique
entre l'arbre courant et `master` extrait par `git archive`.

## Assumé

Préexistant au chantier qui l'a constaté, et hors de son périmètre — celui-ci portait sur la
sérialisation TOML, pas sur l'outillage de typage. Le report est délibéré ; ce qui ne l'était pas,
c'est de découvrir en le clôturant que le contrôle de typage utilisé par ses propres audits était
plus faible que ce que le dépôt déclare.

## Soldé le

**2026-09-09, hors chantier, sur décision de l'utilisateur** — `basedpyright` fait foi, `pyright`
n'est plus un outil de ce dépôt. La configuration ne change pas : `typeCheckingMode: "all"` est
correct pour l'outil retenu, et c'est l'usage de `pyright` qui était fautif.

Ce qui rend la décision opposable, plutôt qu'écrite quelque part :

1. la règle vit dans `OUTILLAGE.md`, à la racine — l'ancienne section « Dépendances » du contrat du
   tracker était un mauvais endroit pour un outillage valable dans tout le dépôt, ce que montrait
   déjà le fait que deux skills extérieurs y renvoyaient ;
2. les **trois agents** la portent en dur (`agents/*.md`), parce que le garde-fou leur interdit tout
   renvoi au contrat. C'est eux qui choisissaient l'outil, et c'est là que la règle manquait : les
   trois audits de `tableaux-toml-aplatis-a-l-ecriture` ont lancé `pyright` sans que rien ne les en
   dissuade.

Établi par :

- `grep -c basedpyright agents/*.md` → `implementation-auditor.md:5`, `plan-reviewer.md:2`,
  `step-implementer.md:3` — les trois agents nomment l'outil et son lanceur ;
- `python3 scripts/check_pipeline.py` → « Pipeline conforme », les 8 contrôles au vert, dont
  « 4 chemins de skill cités, tous existent » et « 40 renvois entre skills, tous résolvent » après
  recâblage des deux renvois vers `OUTILLAGE.md` ;
- `(cd skills/list-dir && uvx --with pytest basedpyright)` → `13 errors, 0 warnings, 0 notes`,
  identique à l'arbre `master` avant le chantier : aucune régression de typage ne subsiste.

**Complété le 2026-09-09**, après deux dispositifs ajoutés depuis. La règle écrite ne suffisait
pas : l'ancienne section « Dépendances » disait déjà de lancer `basedpyright`, et trois audits ont
lancé `pyright` quand même. Ce qui manquait n'était pas le texte, mais qu'il atteigne ses lecteurs
et qu'il résiste à l'oubli.

- **La session principale le reçoit au démarrage.** `hooks/outillage-rappel.sh`, branché dans
  `.claude/settings.json` — les settings de **projet**, versionnés avec le dépôt et chargés pour lui
  seul, là où `~/.claude/settings.json` vaut pour tous les projets de l'utilisateur. Il émet quatre
  lignes, pas le fichier : les lanceurs, l'interdit de `pyright`, la règle `git archive`.
- **Le garde-fou refuse la dérive.** Contrôle 9 de `scripts/check_pipeline.py` : toute mention de
  « pyright » dans les `.md` versionnés, les hooks et les agents doit l'écarter. Il raisonne par
  voisinage et ignore `basedpyright` et `pyrightconfig.json`, ce dernier étant un nom de fichier.

Établi par :

- transcript de la session `106abb91-b2b2-415a-8f34-fef9e476182e`, ligne 6 :
  `{"type": "hook_success", "hookName": "SessionStart:startup", …, "content": "Outillage de ce dépôt
  (/home/debian/.claude/OUTILLAGE.md) : …"}` — le hook s'est déclenché seul, sans approbation
  demandée, dans une session ouverte après le branchement ;
- `python3 scripts/check_pipeline.py` → « 9. pyright n'est cité que pour être écarté ✓ 13
  mention(s), toutes des interdictions », et l'ajout d'une ligne « Lancer `npx pyright` » à
  `OUTILLAGE.md` la fait refuser en la nommant.

**Ce qui n'est pas couvert, et qui ne peut pas l'être ainsi** : les sous-agents ne reçoivent pas
`SessionStart`. Or ce sont eux qui avaient dérivé. Leur couverture repose entièrement sur la règle
recopiée en dur dans `agents/*.md` — que le contrôle 9 empêche désormais de disparaître.

La dette restante sur ces 13 erreurs est distincte et reste ouverte :
`basedpyright-treize-erreurs-non-tenues`.
