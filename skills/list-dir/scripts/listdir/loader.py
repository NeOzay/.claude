"""Découverte des commandes, résolution des surcharges, contrôle des dépendances.

DÉCOUVERTE PAR LE SYSTÈME DE FICHIERS, jamais par un registre à tenir à jour : un
registre se désynchronise, une arborescence non.

  génériques           listdir/commands/<nom>.py
  propres à une liste  <liste>/.list/commands/<nom>.py

DESCRIPTION ET REQUIRES SONT LUS PAR ast.parse, SANS IMPORTER LE MODULE. help
n'exécute donc rien pour afficher une liste, et une commande au Python cassé ne
fait pas tomber les autres. Seule la commande appelée est importée.

REQUIRES EST VÉRIFIÉ AVANT L'APPEL : une dépendance déclarée absente sort non nulle
en la nommant. C'est la réponse au précédent du dépôt — un hook qui gardait sur un
outil absent et sortait 0 sans un mot, si bien que le garde n'a jamais gardé.
"""

from __future__ import annotations

import ast
import importlib.util
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from .types import Command, Result, fail, ok

# Celles-là ne se surchargent pas. Elles portent le contrat, la découvrabilité,
# et la remise en conformité. Une liste qui redéfinit ce que « valide » veut dire
# vide le contrat de son sens ; une liste qui redéfinit help peut cacher ses
# commandes ; une liste qui redéfinit migrate réécrit ses fichiers comme elle
# l'entend sous couvert d'une commande générique.
PROTECTED = ("validate", "help", "migrate")

GENERIC_DIR = Path(__file__).resolve().parent / "commands"
LIST_COMMANDS = ".list/commands"


@dataclass(frozen=True)
class CommandSpec:
    name: str
    path: Path
    origin: str  # "générique" | "liste"
    description: str = ""
    requires: tuple[str, ...] = ()
    overrides: bool = False  # masque une générique de même nom
    broken: str = ""  # Python illisible : le dire sans tomber

    def load(self) -> Result[Command[object]]:
        """Le module importé, vu à travers le protocole Command.

        Le cast n'est pas cosmétique : sans lui, `module.command(...)` est un appel
        sur un ModuleType, donc de type Any, et le protocole ne vaudrait que pour la
        documentation. Ce qui l'autorise est le contrôle de `command` juste en dessous.
        """
        spec = importlib.util.spec_from_file_location(f"_listdir_cmd_{self.name}", self.path)
        if spec is None or spec.loader is None:
            return fail(f"{self.path}: module illisible")
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:
            return fail(f"{self.path}: import impossible — {exc}")
        if not callable(getattr(module, "command", None)):
            return fail(f"{self.path}: aucune fonction command(args, utils)")
        # Le double cast passe par `object` : un ModuleType et un Protocol ne se
        # recouvrent pas structurellement pour le vérificateur, qui refuse le
        # raccourci. Ce qui rend la conversion sûre est le contrôle ci-dessus.
        return ok(cast("Command[object]", cast("object", module)))


def _read_meta(path: Path) -> tuple[str, tuple[str, ...], str]:
    """DESCRIPTION et REQUIRES par analyse syntaxique. Rien n'est exécuté."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError) as exc:
        return ("", (), f"illisible — {exc}")

    description, requires = "", ()
    for node in tree.body:
        # Les deux formes d'affectation. `REQUIRES: list[str] = []` est une AnnAssign
        # et non une Assign : ne lire que la seconde ferait passer pour absente une
        # déclaration annotée, c'est-à-dire celle qu'un auteur soigneux écrit.
        if isinstance(node, ast.Assign):
            targets, value_node = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value_node = [node.target], node.value
        else:
            continue
        for target in targets:
            if not isinstance(target, ast.Name):
                continue
            try:
                value = cast("object", ast.literal_eval(value_node))
            except ValueError:
                continue
            if target.id == "DESCRIPTION" and isinstance(value, str):
                description = value
            elif target.id == "REQUIRES" and isinstance(value, (list, tuple)):
                seq = cast("list[object] | tuple[object, ...]", value)
                requires = tuple(str(v) for v in seq)
    return (description, requires, "")


def _scan(directory: Path, origin: str) -> dict[str, CommandSpec]:
    found: dict[str, CommandSpec] = {}
    if not directory.is_dir():
        return found
    for path in sorted(directory.glob("*.py")):
        if path.name.startswith("_"):
            continue
        description, requires, broken = _read_meta(path)
        found[path.stem] = CommandSpec(
            path.stem, path, origin, description, requires, broken=broken
        )
    return found


def discover(list_dir: Path | None = None) -> tuple[dict[str, CommandSpec], list[str]]:
    """Les commandes visibles, la liste gagnant sur le générique.

    Rend aussi les refus : une surcharge d'une commande protégée n'est pas
    silencieusement ignorée, elle est rapportée.
    """
    commands = _scan(GENERIC_DIR, "générique")
    refus: list[str] = []

    if list_dir is not None:
        for name, spec in _scan(list_dir / LIST_COMMANDS, "liste").items():
            if name in PROTECTED:
                refus.append(
                    f"{spec.path}: « {name} » ne se surcharge pas — "
                    "elle porte le contrat de toutes les listes"
                )
                continue
            commands[name] = CommandSpec(
                spec.name,
                spec.path,
                "liste",
                spec.description,
                spec.requires,
                overrides=name in commands,
                broken=spec.broken,
            )
    return commands, refus


def check_requires(spec: CommandSpec) -> Result[None]:
    """Échec fermé sur outil déclaré absent, en le nommant."""
    manquants = [tool for tool in spec.requires if shutil.which(tool) is None]
    if manquants:
        return fail(
            f"« {spec.name} » exige {', '.join(manquants)} — introuvable dans le PATH. "
            f"Déclaré par REQUIRES dans {spec.path}."
        )
    return ok(None)
