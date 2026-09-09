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
