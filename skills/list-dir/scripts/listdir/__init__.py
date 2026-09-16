"""list-dir — répertoires-listes : un répertoire = une liste, un fichier = un élément.

La surface publique est ce que __all__ énumère, et rien d'autre. Le reste du paquet
peut bouger d'une version à l'autre.

    import shutil, sys
    from pathlib import Path

    cmd = shutil.which("list-dir")
    if cmd is None:
        raise SystemExit("list-dir introuvable dans le PATH")
    sys.path.insert(0, str(Path(cmd).resolve().parent))
    from listdir import open_list

    lst = open_list("chemin/vers/ma-liste").unwrap()
    for item in lst.items().unwrap():
        print(item.id, item.fields["title"])
"""

import shutil
import sys
from pathlib import Path

# LE PAQUET `gabarit` SE TROUVE PAR SON LIEN DE `bin/`, qui désigne le `scripts/` qui
# le porte. Aucun chemin entre skills n'est écrit en dur. Ceci vit ici, avant tout
# import relatif, parce que `from listdir.items import …` exécute ce fichier d'abord :
# c'est le seul point par lequel passe tout consommateur du paquet.
#
# LE `bin/` DU DÉPÔT D'ABORD, EN REMONTANT, le PATH seulement en repli — sur le modèle
# de la recherche du `.venv` dans `list-dir.py`. Résoudre par le PATH seul faisait
# dépendre list-dir d'un PATH qu'il n'exigeait pas : lancé par son chemin avec un PATH
# réduit, il sortait sur un ImportError au lieu de nommer l'outil qui manquait
# réellement (test_git_absent_du_path_sort_non_nul_en_le_nommant).
#
# ÉCHEC FERMÉ ET NOMMÉ : sans gabarit, un ImportError sur un module interne dirait ce
# qui manque trois imports plus loin, sans dire pourquoi. `append` et non `insert` :
# ce répertoire ne doit masquer aucun module déjà résoluble.
if (
    _gabarit := next(
        (
            str(a / "bin" / "gabarit")
            for a in Path(__file__).resolve().parents
            if (a / "bin" / "gabarit").exists()
        ),
        None,
    )
    or shutil.which("gabarit")
) is None:
    raise ImportError(
        "listdir exige le paquet gabarit : aucun bin/gabarit en remontant depuis "
        f"{Path(__file__).resolve().parent}, ni de commande « gabarit » dans le PATH"
    )
if (_scripts := str(Path(_gabarit).resolve().parent)) not in sys.path:
    sys.path.append(_scripts)

from .contract import load_contract
from .items import read_item, write_item
from .store import ListStore, init_list, open_list
from .types import (
    FIELD_TYPES,
    OPTIONAL,
    PLACEHOLDER,
    Change,
    Command,
    Contract,
    Field,
    FieldType,
    FieldValue,
    Item,
    ListError,
    Origin,
    Result,
    Utils,
    Violation,
    fail,
    ok,
)

__all__ = [
    "FIELD_TYPES",
    "OPTIONAL",
    "PLACEHOLDER",
    "Change",
    "Command",
    "Contract",
    "Field",
    "FieldType",
    "FieldValue",
    "Item",
    "ListError",
    "ListStore",
    "Origin",
    "Result",
    "Utils",
    "Violation",
    "fail",
    "init_list",
    "load_contract",
    "ok",
    "open_list",
    "read_item",
    "write_item",
]
