---
paths:
  - "**/.claude/**/*.py"
  - "scripts/**/*.py"
  - "skills/*/scripts/**/*.py"
---

# Convention de code Python

Chaque règle cite entre parenthèses un endroit du dépôt où elle est pratiquée. Lancer les
linters et les tests : `OUTILLAGE.md`, à la racine du dépôt, qui en est l'autorité.

## Version et typage

- Python ≥ 3.12, avec la syntaxe de généricité PEP 695 (`class Result[T]`, `type Alias = …`). La garde de version vit dans le point d'entrée, **avant** tout import du paquet : un `SyntaxError` à l'import ne laisse aucune place à un message lisible. (`skills/gabarit/scripts/gabarit-cli.py`)
- Typage strict : basedpyright en `typeCheckingMode: "all"`. Tout ce qui est public est annoté. (`skills/gabarit/pyrightconfig.json`)
- Une exception au typeur est ciblée et justifiée : `cast("T", …)` accompagné d'un commentaire qui dit l'invariant que le type ne sait pas exprimer ; sinon `# pyright: ignore[<règle>]` avec la règle nommée. Jamais de `# type: ignore` nu. (`skills/gabarit/scripts/gabarit/types.py`, `Result.unwrap`)
- Même règle pour ruff : `# noqa: <code>` avec le code, et un commentaire au-dessus qui dit pourquoi. (`skills/gabarit/scripts/gabarit-cli.py`)

## Configuration

- `pyrightconfig.json` et `ruff.toml` vivent **dans la skill**, pas seulement à la racine : la skill est déployable ailleurs, et sa configuration voyage avec elle. Deux skills dont le code passe de l'une à l'autre gardent des configurations identiques. (`skills/gabarit/ruff.toml`)
- ruff : `line-length = 100`, `target-version = "py312"`, règles `E F I UP B SIM RUF`. (`skills/gabarit/ruff.toml`)

## Documentation

- Chaque module ouvre sur une docstring : une ligne de résumé, puis des paragraphes-clés dont l'intitulé est en capitales (`PORTÉE :`, `ÉCHEC FERMÉ :`, ou une affirmation qui résume le paragraphe). Ils disent ce que le module fait, ce qu'il refuse de faire, et pourquoi. (`skills/gabarit/scripts/gabarit/types.py`, `skills/list-dir/scripts/listdir/contract.py`)
- **Docstrings de fonction et de classe au format Google, compactes** : une ligne de résumé ; puis `Args:`, `Returns:`, `Raises:` seulement quand ils apprennent quelque chose que la signature typée ne dit pas déjà. — *Prescrite, pas encore pratiquée : le code existant n'en porte aucune.*
- Un commentaire dit **pourquoi**, jamais ce que fait la ligne. Un commentaire qui porte une règle en met le cœur en capitales (« Définis ici et NULLE PART AILLEURS »). (`skills/gabarit/scripts/gabarit/types.py`, `PLACEHOLDER`)

## Structure

- Le point d'entrée CLI ne contient aucune logique métier : il parse, appelle la bibliothèque, traduit le résultat en code de sortie. Son nom porte un tiret pour ne pas être importable. (`skills/gabarit/scripts/gabarit-cli.py`)
- Entre couches, un `Result[T]` plutôt qu'une exception : le statut et le message voyagent jusqu'à la CLI, qui seule écrit sur stderr et sort. (`skills/gabarit/scripts/gabarit/types.py`)
- Collecte et jugement séparés : une fonction de contrôle reçoit ses entrées et rend des constats ; elle ne lit pas `sys.argv`, n'imprime rien et n'appelle pas `exit`. C'est ce qui la rend testable seule. (`scripts/check_pipeline.py`)
- Une valeur lue de l'extérieur (TOML, JSON, argv) n'est pas prise sur parole : elle passe par une fonction qui la vérifie et rend un échec nommé. (`skills/list-dir/scripts/listdir/contract.py`)
- Une constante partagée est définie à un seul endroit, avec son motif en commentaire. (`skills/gabarit/scripts/gabarit/types.py`)
- Messages d'erreur, docstrings et commentaires en français. (`skills/gabarit/scripts/gabarit/check.py`)

## Tests

- pytest, sous `scripts/tests/` de la skill, un fichier par sujet, un `conftest.py` pour les fixtures partagées. (`skills/gabarit/scripts/tests/`, `skills/list-dir/scripts/tests/`)
