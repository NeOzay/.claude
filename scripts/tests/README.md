# Les tests Python du dépôt

Deux suites `pytest`, **342 tests**, aucune dépendance déclarée ailleurs que dans cette page :
`uvx` fournit l'interpréteur et `pytest`, le dépôt ne porte ni `pyproject.toml`, ni
`pytest.ini`, ni `requirements.txt`.

| Suite | Ce qu'elle couvre | Tests |
| --- | --- | --- |
| `scripts/tests/` | le garde-fou `check_pipeline.py` (contrôles 1 à 8, bout en bout) et `sante_skills.py` | 101 |
| `skills/list-dir/scripts/tests/` | le paquet `listdir` : `items`, `contract`, `store`, `loader`, la CLI en sous-processus | 241 |

## Lancer

Depuis la racine du dépôt :

```bash
uvx pytest -q                              # les deux suites
uvx pytest scripts/tests -q                # le garde-fou seul
uvx pytest skills/list-dir/scripts/tests -q  # listdir seul
```

Faute de fichier de configuration, il n'y a **pas de `rootdir` déclaré ni de `testpaths`** :
`uvx pytest` nu se fie au répertoire courant. Lancé d'ailleurs que de la racine, il collecte
autre chose — au mieux une suite, au pire `plugins/`, qui n'est pas à nous et n'est pas
collectable.

Les linters, eux aussi depuis la racine :

```bash
uvx ruff check scripts skills/list-dir
uvx --with pytest basedpyright             # `--with pytest` : sinon les imports de test manquent
```

## Deux règles que la structure impose

**Aucun test ne lit le vrai dépôt.** Chaque test monte sur `tmp_path` l'arborescence minimale
qui déclenche — ou non — le comportement visé : un dépôt-jouet pour le garde-fou, une
liste-jouet pour `listdir`. Un contrôle qui ne serait vert qu'en lisant le vrai dépôt serait
invérifiable, et deviendrait faux au premier fichier ajouté.

**Deux suites ne partagent jamais un nom de module.** Aucun `__init__.py` n'existe dans les
répertoires de tests, et pytest importe en mode « prepend » : le nom du module vient du
*basename* du fichier, donc deux fichiers homonymes dans deux suites se disputent le même nom
et le premier collecté gagne. D'où :

- `conftest.py` ne porte **que des fixtures** et ne s'importe jamais par son nom — les deux
  suites en ont un, un `from conftest import …` résoudrait vers l'un ou l'autre selon l'ordre
  de collecte, en accusant le mauvais fichier dans son message d'erreur ;
- ce qu'un test importe explicitement vit dans un module au **basename unique au dépôt** :
  `scripts/tests/depot_jouet.py` d'un côté, `skills/list-dir/scripts/tests/jouet.py` de
  l'autre.

Ajouter une troisième suite, c'est lui donner à son tour un nom d'appui qui n'existe nulle part
ailleurs — et vérifier que `uvx pytest` rend le même compte quel que soit l'ordre des
arguments :

```bash
uvx pytest scripts/tests skills/list-dir/scripts/tests -q
uvx pytest skills/list-dir/scripts/tests scripts/tests -q
```
