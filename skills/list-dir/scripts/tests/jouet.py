"""La liste-jouet : contrat, élément de référence, et les fonctions qui les montent.

ELLE DÉCLARE `def = false` : c'est une liste née à la main, sans semence à rattraper.
Sans cette ligne, chaque commande lancée sur elle porterait l'avertissement
d'adoption, et les tests de sortie devraient tous l'ignorer — ce qui reviendrait à
tester une liste que personne n'écrirait.

POURQUOI CE MODULE N'EST PAS `conftest.py` : deux suites coexistent dans ce dépôt,
et `scripts/tests/conftest.py` porte déjà ce nom. Un `from conftest import …` résout
alors vers l'un ou l'autre selon le chemin d'appel — le vérificateur de types de la
racine résolvait vers le mauvais et rapportait des symboles inconnus. Un nom unique
supprime l'ambiguïté ; `conftest.py` ne garde que les fixtures, qui ne s'importent
jamais.
"""

from __future__ import annotations

import os
from pathlib import Path

from listdir.contract import CONTRACT, PATRONS
from listdir.store import init_list

CONTRAT = """name = "jouet"
description = "liste-jouet des tests"

[origin]
def = false

[fields.id]
type = "slug"
description = ""

[fields.title]
type = "text"
required = true
description = "le titre de l'élément"

[fields.date]
type = "date"
description = ""

[fields.category]
type = "enum"
values = ["rouge", "vert"]
description = ""

[fields.tags]
type = "list"
description = ""

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


PATRON_TOML = """name = "revue"
description = "fiches de revue"

[fields.id]
type = "slug"
description = ""

[fields.title]
type = "text"
required = true
from = "title"
description = ""

[fields.verdict]
type = "text"
required = true
description = ""

[sections."Avis"]
required = true
description = ""

[sections."Remarque"]
required = false
description = ""
"""

PATRON_MD = """+++
un front matter que derive ignore
+++

## Avis

<À REMPLIR>

## Remarque

<OPTIONNEL>
"""


def monter_patron(
    liste: Path,
    nom: str = "revue",
    contrat: str = PATRON_TOML,
    corps: str = PATRON_MD,
) -> Path:
    """La paire `<nom>.toml` / `<nom>.md` sous `.list/patrons/` de la liste SOURCE."""
    _ = ecrire(liste, f".list/patrons/{nom}.toml", contrat)
    _ = ecrire(liste, f".list/patrons/{nom}.md", corps)
    return liste


SEMENCE = """name = "jouet"
description = "liste-jouet des tests"

# Ce commentaire porte le pourquoi d'un champ : il doit survivre à une recopie.
[origin]
def = "jouet"
version = 1

[fields.id]
type = "slug"
description = ""

[fields.title]
type = "text"
required = true
description = "le titre"
text = "titre par défaut"

[sections."Constat"]
required = true
description = "ce qui a été observé"
"""


def semer(tmp_path: Path, contrat: str = SEMENCE, patron: str = "") -> tuple[Path, Path]:
    """Une définition au rang 1, et la liste qu'elle vient de semer.

    LE RÉPERTOIRE COURANT DEVIENT `tmp_path` : les tests de bibliothèque de `reseed` résolvent
    la définition depuis là. Un test par la ligne de commande passe `cwd=tmp_path` à son tour.
    """
    definition = tmp_path / ".claude" / "list-dir" / "jouet"
    _ = ecrire(definition, CONTRACT, contrat)
    if patron:
        _ = ecrire(definition, f"{PATRONS}/revue.md", patron)
    cible = tmp_path / "liste"
    _ = init_list(cible, definition=definition).unwrap()
    os.chdir(tmp_path)
    return definition, cible
