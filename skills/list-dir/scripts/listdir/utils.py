"""La façade passée aux commandes. Elles ne reçoivent rien d'autre.

utils.run() donne accès aux commandes génériques : c'est ce qui rend une surcharge
DÉCORATIVE plutôt que réimplémentée. Un `close.py` de liste, c'est `move` plus une
exigence supplémentaire — pas une seconde implémentation de git mv.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Never, cast, final

from .gitcmd import git
from .store import ListStore, open_list
from .types import Result, fail, ok


@final
class Toolbox:
    """Implémentation du protocole Utils."""

    list_dir: Path | None

    def __init__(self, list_dir: Path | None = None) -> None:
        self.list_dir = list_dir

    def open(self, list_dir: Path | str) -> Result[ListStore]:
        return open_list(list_dir)

    def git(self, *argv: str) -> Result[str]:
        """git, dans le répertoire de la liste visée quand il y en a une."""
        return git(*argv, cwd=self.list_dir)

    def run(self, name: str, argv: list[str]) -> Result[object]:
        """Appelle une autre commande, générique ou de la liste."""
        from .loader import check_requires, discover

        commands, _ = discover(self.list_dir)
        spec = commands.get(name)
        if spec is None:
            return fail(f"commande « {name} » inconnue")
        dep = check_requires(spec)
        if not dep:
            return Result(dep.status, None, dep.message)
        module = spec.load()
        if not module:
            return Result(module.status, None, module.message)
        import argparse

        entry = module.unwrap()
        parser = argparse.ArgumentParser(prog=name)
        register = cast(
            "Callable[[argparse.ArgumentParser], None] | None",
            getattr(entry, "register", None),
        )
        if register is not None:
            register(parser)
        return entry.command(parser.parse_args(argv), self)

    def ok[T](self, value: T = None) -> Result[T]:
        return ok(value)

    def fail(self, message: str, code: int = 1) -> Result[Never]:
        return fail(message, code)
