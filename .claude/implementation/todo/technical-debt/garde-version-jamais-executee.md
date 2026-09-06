+++
id = "garde-version-jamais-executee"
title = "La garde de version de `list-dir.py` n'est vérifiée que par son rang, jamais exécutée"
date = 2026-08-24
source = "chantier `tests-listdir`, constat de l'étape 9"
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

`list-dir.py` s'ouvre sur une garde qui refuse un Python antérieur à 3.12, parce que le paquet
utilise la syntaxe de généricité de PEP 695 et qu'un import lèverait sinon un `SyntaxError`
illisible.

`test_entree_cli.py`, « la garde de version précède tout import de listdir », vérifie par analyse
syntaxique que le bloc `sys.version_info` précède le premier `from listdir …` dans l'arbre du
fichier. C'est son *rang* qui est testé, et c'est bien l'enjeu principal — mais **le corps de la
garde n'est jamais exécuté** : ni le message qu'elle écrit sur stderr, ni le code 2 qu'elle rend.

La cause est matérielle : aucun interpréteur antérieur à 3.12 n'est disponible sur la machine.

## Pourquoi c'est gênant

Le message de cette garde est la seule chose qu'un utilisateur sur un Python ancien verra jamais du
paquet. Une faute de frappe dans le `sys.stderr.write`, un `sys.executable` mal interpolé, un
`raise SystemExit(2)` devenu `SystemExit(1)` : rien ne le signalerait, et le défaut ne se
manifesterait que chez quelqu'un qui n'a précisément pas les moyens de le diagnostiquer.

Le skill est explicitement destiné à être déployé ailleurs (`skills/list-dir/ruff.toml`, « ce skill
est destiné à être déployé ailleurs »), donc « ailleurs » est le cas nominal, pas le cas rare.

## Pour solder

Exécuter le fichier avec un `sys.version_info` truqué. La garde lit `sys.version_info` au
chargement du module : un sous-processus lancé avec `-c` qui monkeypatche `sys.version_info` avant
`runpy.run_path("list-dir.py")` suffirait à faire prendre la branche, sans interpréteur ancien.

Solde établi par un test qui capture le message et assert le code 2.

## Assumé

<OPTIONNEL>
