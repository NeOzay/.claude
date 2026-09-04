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
