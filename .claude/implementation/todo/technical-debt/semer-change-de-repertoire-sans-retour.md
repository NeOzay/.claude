+++
id = "semer-change-de-repertoire-sans-retour"
title = "`semer` change le répertoire courant des tests sans le rétablir"
date = 2026-10-15
severite = "note"
chantier = "solder-sept-dettes"
reference = "R4"
pin = false
reviewed = "<OPTIONNEL date>"
category = "<OPTIONNEL>"
+++

## Constat

`semer`, dans `skills/list-dir/scripts/tests/jouet.py`, fait un `os.chdir(tmp_path)` et ne revient
jamais au répertoire d'origine. Les tests de bibliothèque de `test_reseed.py` en ont besoin : la
définition se résout depuis le répertoire courant. Les tests `reseed` de `test_entree_cli.py`, qui
appellent `semer` puis `lancer(..., cwd=tmp_path)`, en héritent sans en avoir besoin.

## Pourquoi c'est gênant

Le répertoire courant du processus de test dépend de l'ordre des tests : un test lancé après un
`semer` part du `tmp_path` d'un autre, déjà supprimé ou non. La suite est verte aujourd'hui ; un
test qui résout un chemin relatif peut changer de résultat selon qu'il tourne avant ou après.

## Pour solder

Faire prendre à `semer` le `monkeypatch` de pytest et changer de répertoire par
`monkeypatch.chdir`, rétabli à la fin du test, ou laisser le `chdir` aux seuls tests de
bibliothèque qui en ont besoin.

## Assumé

<OPTIONNEL>
