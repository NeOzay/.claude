"""La liste-jouet : contrat, élément de référence, et les fonctions qui les montent.

POURQUOI CE MODULE N'EST PAS `conftest.py` : deux suites coexistent dans ce dépôt,
et `scripts/tests/conftest.py` porte déjà ce nom. Un `from conftest import …` résout
alors vers l'un ou l'autre selon le chemin d'appel — le vérificateur de types de la
racine résolvait vers le mauvais et rapportait des symboles inconnus. Un nom unique
supprime l'ambiguïté ; `conftest.py` ne garde que les fixtures, qui ne s'importent
jamais.
"""

from __future__ import annotations

from pathlib import Path

CONTRAT = """name = "jouet"
description = "liste-jouet des tests"

[fields.id]
type = "slug"

[fields.title]
type = "text"
required = true
description = "le titre de l'élément"

[fields.date]
type = "date"

[fields.category]
type = "enum"
values = ["rouge", "vert"]

[fields.tags]
type = "list"

[sections."Constat"]
required = true
description = ""

[sections."Assumé"]
required = false
description = ""
"""

ELEMENT = """+++
id = "premier"
title = "Le premier élément"
date = 2026-08-24
category = "rouge"
tags = ["a", "b"]
+++

## Constat

Ce qui a été constaté.

## Assumé

<OPTIONNEL>
"""


def ecrire(root: Path, rel: str, contenu: str) -> Path:
    """Écrit `contenu` dans `root/rel`, en créant les répertoires manquants."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(contenu, encoding="utf-8")
    return path


def monter_liste(racine: Path, contrat: str = CONTRAT) -> Path:
    """Un répertoire-liste au contrat donné, sans aucun élément."""
    _ = ecrire(racine, ".list/contract.toml", contrat)
    return racine


def element(
    liste: Path,
    item_id: str,
    front: str = "",
    corps: str = "## Constat\n\nx\n",
) -> Path:
    """Un élément écrit tel quel. `front` remplace le front matter par défaut."""
    defaut = f'id = "{item_id}"\ntitle = "T"\n'
    return ecrire(liste, f"{item_id}.md", f"+++\n{front or defaut}+++\n\n{corps}")


GABARIT_TOML = """name = "revue"
description = "fiches de revue"

[fields.id]
type = "slug"

[fields.title]
type = "text"
required = true
from = "title"

[fields.verdict]
type = "text"
required = true

[sections."Avis"]
required = true
description = ""

[sections."Remarque"]
required = false
description = ""
"""

GABARIT_MD = """+++
un front matter que derive ignore
+++

## Avis

<À REMPLIR>

## Remarque

<OPTIONNEL>
"""


def monter_gabarit(
    liste: Path,
    nom: str = "revue",
    contrat: str = GABARIT_TOML,
    corps: str = GABARIT_MD,
) -> Path:
    """La paire `<nom>.toml` / `<nom>.md` sous `.list/templates/` de la liste SOURCE."""
    _ = ecrire(liste, f".list/templates/{nom}.toml", contrat)
    _ = ecrire(liste, f".list/templates/{nom}.md", corps)
    return liste
