#!/usr/bin/env python3
"""Point d'entrée en ligne de commande des répertoires-listes.

AUCUNE LOGIQUE MÉTIER ICI. Ce fichier parse des arguments, appelle la bibliothèque
et traduit un Result en code de sortie. Toute la logique vit dans listdir/ — c'est
ce qui garantit qu'un script qui importe le paquet a exactement les mêmes moyens
que cette commande, et que les deux ne peuvent pas diverger.

ÉCHEC FERMÉ : sortie 2 sur une erreur d'appel, sortie non nulle et message sur
stderr sur toute autre erreur. Jamais de succès silencieux.

LA GARDE DE VERSION EST ICI, AVANT TOUT IMPORT DE listdir : le paquet utilise la
syntaxe de généricité de PEP 695, et sur un Python plus ancien l'import lèverait
un SyntaxError illisible au lieu de dire ce qui manque.
"""

import sys

# Le `noqa: UP036` ci-dessous : ruff juge ce bloc mort parce que target-version vaut
# py312. C'est l'inverse : il n'existe que pour le Python plus ancien qui
# exécuterait ce fichier.
if sys.version_info < (3, 12):  # noqa: UP036
    v = ".".join(str(n) for n in sys.version_info[:3])  # pyright: ignore[reportUnreachable]
    sys.stderr.write(f"list-dir exige Python >= 3.12, trouvé {v} ({sys.executable}).\n")
    raise SystemExit(2)

import argparse
from collections.abc import Callable
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parent))

from listdir.loader import check_requires, discover
from listdir.utils import Toolbox

USAGE = "list-dir.py <commande> [<liste>] [options]"


def sniff_list_dir(argv: list[str]) -> Path | None:
    """La liste visée, si elle est déjà lisible dans la ligne de commande.

    Les commandes propres à une liste vivent DANS cette liste : il faut donc savoir
    laquelle avant de pouvoir construire le parseur. On regarde les arguments
    positionnels, sans rien décider — si aucun n'est un répertoire de liste, seules
    les génériques sont visibles, ce qui est exactement le bon comportement.
    """
    for arg in argv:
        if arg.startswith("-"):
            continue
        path = Path(arg)
        if (path / ".list").is_dir():
            return path
    return None


def main(argv: list[str]) -> int:
    if not argv:
        sys.stderr.write(f"usage: {USAGE}\n\nAucune commande. « help » les liste.\n")
        return 2

    name, rest = argv[0], argv[1:]
    list_dir = sniff_list_dir(rest)
    commands, refus = discover(list_dir)

    # Une surcharge interdite n'est jamais ignorée en silence : c'est une erreur.
    for message in refus:
        sys.stderr.write(f"{message}\n")
    if refus:
        return 1

    spec = commands.get(name)
    if spec is None:
        connues = ", ".join(sorted(commands)) or "aucune"
        sys.stderr.write(f"usage: {USAGE}\n\ncommande « {name} » inconnue ; connues : {connues}\n")
        return 2
    if spec.broken:
        sys.stderr.write(f"{spec.path}: {spec.broken}\n")
        return 1

    dep = check_requires(spec)
    if not dep:
        sys.stderr.write(f"{dep.message}\n")
        return dep.status

    module = spec.load()
    if not module:
        sys.stderr.write(f"{module.message}\n")
        return module.status
    module = module.unwrap()

    parser = argparse.ArgumentParser(prog=f"list-dir.py {name}", description=spec.description)
    register = cast(
        "Callable[[argparse.ArgumentParser], None] | None", getattr(module, "register", None)
    )
    if register is not None:
        register(parser)
    args = parser.parse_args(rest)

    result = module.command(args, Toolbox(list_dir))
    # Le vérificateur tient ce test pour mort, parce que le protocole annonce un
    # Result. Le protocole ne contraint pourtant personne : le module est du Python
    # écrit à la main, dans une liste, hors de ce dépôt. La garde reste.
    if result is None:  # pyright: ignore[reportUnnecessaryComparison]
        sys.stderr.write(f"{spec.path}: command() n'a rien rendu — un Result est attendu\n")
        return 1
    if not result:
        sys.stderr.write(f"{result.message}\n")
        return result.status or 1
    if result.value is not None:
        print(result.value if isinstance(result.value, str) else repr(result.value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
