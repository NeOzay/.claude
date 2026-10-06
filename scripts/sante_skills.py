#!/usr/bin/env python3
"""Santé du système de skills, vérifiée une fois par session.

POURQUOI CE SCRIPT EXISTE. Les skills s'appellent entre eux par une commande nue
(`list-dir validate …`), résolue via les liens de `bin/` et le `PATH`. Cette forme a un
mode de défaillance connu et silencieux : commande absente → code 127 et sortie VIDE,
que l'appelant lit comme un résultat, pas comme une erreur. C'est le défaut qui a bloqué
la clôture du 2026-08-14.

La parade retenue n'est PAS une garde recopiée dans chaque bloc de chaque skill — ce
serait le rituel que ce dépôt cherche justement à supprimer. C'est une vérification
unique, au démarrage de session, qui crie fort et une seule fois.

SILENCIEUX QUAND TOUT VA BIEN : un hook qui parle à chaque session finit par ne plus
être lu, et ce qu'il dirait le jour où ça compte se perdrait dans le bruit.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import cast

MIN_PYTHON = (3, 12)

# Le venv du dépôt, celui dans lequel `list-dir.py` se ré-exécute. Les scripts de
# skill n'ont plus la stdlib pour seul horizon : ce qui manque ici ne se voit
# autrement qu'en ImportError au milieu d'une opération.
VENV = ".venv"
REQUIREMENTS = "requirements.txt"


def racine() -> Path:
    """La racine du dépôt de skills, déduite de la position de ce fichier.

    Aucune constante, aucune variable d'environnement : le script sait où il est, et
    c'est précisément ce que le reste du système ne peut pas faire depuis un `.md`.
    """
    return Path(__file__).resolve().parent.parent


def _requises(root: Path) -> list[tuple[str, str | None]]:
    """Les distributions déclarées par `requirements.txt` : (nom, version épinglée).

    PAS DE requirements.txt = RIEN À CONTRÔLER, et c'est voulu : un dépôt qui ne
    déclare aucune dépendance n'a pas à se voir reprocher l'absence d'un venv. C'est
    la déclaration qui crée l'exigence, jamais l'inverse.

    SEUL `==` DONNE UNE VERSION, et seulement SANS MARQUEUR D'ENVIRONNEMENT. Une
    contrainte souple (`>=`, `~=`) déclare un intervalle, dont ce script ne saurait
    dire s'il est respecté sans embarquer un résolveur ; elle ne contrôle donc que la
    présence. Épingler, c'est demander à être averti — et ne rien vérifier d'une
    épingle la rendrait décorative.

    UN MARQUEUR (`… ; python_version >= "3.12"`) retombe sur la présence seule : dire
    si la ligne s'applique demande d'évaluer le marqueur, ce qui est le travail d'un
    résolveur. Signaler une version « divergente » sur une ligne peut-être inactive
    serait pire que se taire — c'est l'avertissement qu'on apprend à ignorer.
    """
    fichier = root / REQUIREMENTS
    if not fichier.is_file():
        return []
    requises: list[tuple[str, str | None]] = []
    for ligne in fichier.read_text(encoding="utf-8").splitlines():
        brut = ligne.split("#")[0].strip()
        if not brut or brut.startswith("-"):
            continue
        nom, epingle, version = brut.partition("==")
        requises.append(
            (
                re.split(r"[<>=!~;\[ ]", nom)[0].strip(),
                version.strip() if epingle and ";" not in version else None,
            )
        )
    return requises


def _dependances(root: Path) -> list[str]:
    """Le venv du dépôt porte-t-il ce que `requirements.txt` déclare ?

    SANS SOUS-PROCESSUS. Ce script tourne à chaque démarrage de session ; lancer un
    interpréteur par dépendance pour l'interroger coûterait plus que tout le reste
    du contrôle réuni. Les `*.dist-info` posés par pip et uv disent la même chose,
    en une lecture de répertoire.
    """
    requises = _requises(root)
    if not requises:
        return []

    venv = root / VENV
    reparer = (
        f"uv venv {venv} && uv pip install --python {venv}/bin/python -r {root / REQUIREMENTS}"
    )

    site = next(iter(sorted(venv.glob("lib/python*/site-packages"))), None)
    if site is None:
        return [f"{venv} absent ou incomplet — le (re)créer : {reparer}"]

    def normal(nom: str) -> str:
        return nom.lower().replace("_", "-")

    # `tomlkit-0.15.1.dist-info` → « tomlkit » : « 0.15.1 ». Le nom d'une
    # distribution peut porter des tirets, la version jamais : c'est le DERNIER
    # tiret qui sépare les deux.
    installees = {
        normal(d.name.removesuffix(".dist-info").rpartition("-")[0]): d.name.removesuffix(
            ".dist-info"
        ).rpartition("-")[2]
        for d in site.glob("*.dist-info")
    }

    absentes = [nom for nom, _ in requises if normal(nom) not in installees]
    if absentes:
        mal = (
            f"{venv} : {', '.join(absentes)} déclaré(s) dans {REQUIREMENTS} mais absent(s) — "
            f"réinstaller : {reparer}"
        )
        return [mal]

    divergentes = [
        f"{nom} {installees[normal(nom)]} au lieu de {version}"
        for nom, version in requises
        if version is not None and installees[normal(nom)] != version
    ]
    if divergentes:
        mal = (
            f"{venv} : {', '.join(divergentes)} — {REQUIREMENTS} épingle une autre "
            f"version ; réaligner : {reparer}"
        )
        return [mal]
    return []


def _objet_json(chemin: Path) -> dict[str, object] | str:
    """L'objet JSON que porte `chemin`, ou le motif qui l'en empêche."""
    try:
        # `json.loads` rend Any : le lire comme `object` oblige à vérifier sa forme.
        valeur = cast("object", json.loads(chemin.read_text(encoding="utf-8")))
    except (OSError, ValueError) as e:
        return f"illisible ({e})"
    if not isinstance(valeur, dict):
        return "n'est pas un objet JSON"
    # Les clés d'un objet JSON sont TOUJOURS des chaînes : le type ne le sait pas.
    return cast("dict[str, object]", valeur)


def _liste(valeur: object) -> list[object]:
    """Une valeur JSON lue comme liste : une valeur seule en est une d'un élément."""
    return cast("list[object]", valeur) if isinstance(valeur, list) else [valeur]


def mods_en_defaut(root: Path) -> list[str]:
    """Chaque mod posé à la racine d'un skill peut-il se charger ?

    UN MOD QUI NE SE CHARGE PAS NE DIT RIEN : le moteur le saute, et la session tourne
    sans le contexte qu'il devait verser. Ce contrôle voit ce qui se lit sans lancer
    le moteur — manifeste, modules nommés, dépendances. Un module présent qui échoue
    au chargement lui échappe : seul le journal de `claude --debug` le montre.

    UN MOD EST UN DOSSIER DE SKILL qui porte `.claude-plugin/` ou `hooks/hooks.json`,
    sous `skills/` et sous le `.claude/skills/` du dépôt. L'un sans l'autre est déjà
    un mod incomplet.
    """
    maux: list[str] = []
    dossiers = sorted(
        d
        for parent in (root / "skills", root / ".claude" / "skills")
        if parent.is_dir()
        for d in parent.iterdir()
        if (d / ".claude-plugin").is_dir() or (d / "hooks" / "hooks.json").is_file()
    )
    noms: set[object] = set()
    dependances: dict[Path, list[object]] = {}

    for mod in dossiers:
        ici = mod.relative_to(root)
        plugin = _objet_json(mod / ".claude-plugin" / "plugin.json")
        if isinstance(plugin, str):
            maux.append(f"mod {ici} : .claude-plugin/plugin.json {plugin}.")
        else:
            nom = plugin.get("name")
            if isinstance(nom, str) and nom:
                noms.add(nom)
            else:
                maux.append(f"mod {ici} : .claude-plugin/plugin.json ne porte pas de « name ».")
            dependances[mod] = _liste(plugin.get("dependencies", []))

        # Les modules se résolvent depuis `hooks/`, où `hooks.json` les nomme.
        crochets = _objet_json(mod / "hooks" / "hooks.json")
        if isinstance(crochets, str):
            maux.append(f"mod {ici} : hooks/hooks.json {crochets}.")
            continue
        for module in _liste(crochets.get("modules", [])):
            if not isinstance(module, str) or not (mod / "hooks" / module).is_file():
                maux.append(f"mod {ici} : le module {module!r} de hooks/hooks.json est absent.")

    for mod, deps in dependances.items():
        maux.extend(
            f"mod {mod.relative_to(root)} : la dépendance {dep!r} ne nomme aucun mod présent."
            for dep in deps
            if dep not in noms
        )
    return maux


def plugin_dirs_restant(root: Path) -> list[str]:
    """`CLAUDE_CODE_PLUGIN_DIRS` resté dans `settings.json` ?

    Les mods de ce dépôt se chargent depuis la racine de leur skill. Un dossier encore
    nommé là se chargerait deux fois, ou désignerait un dossier qui n'existe plus.
    """
    reglages = root / "settings.json"
    if reglages.is_file() and "CLAUDE_CODE_PLUGIN_DIRS" in reglages.read_text(encoding="utf-8"):
        return [
            (
                "settings.json nomme encore CLAUDE_CODE_PLUGIN_DIRS — un mod se charge depuis"
                " la racine de son skill ; retirer la variable."
            )
        ]
    return []


def anomalies() -> list[str]:
    maux: list[str] = []
    root = racine()
    bin_dir = root / "bin"

    if not bin_dir.is_dir():
        return [f"{bin_dir} n'existe pas — aucune commande de skill n'est résoluble."]

    liens = sorted(p for p in bin_dir.iterdir() if not p.name.startswith("."))
    if not liens:
        maux.append(f"{bin_dir} est vide — aucune commande de skill n'est exposée.")

    for lien in liens:
        if not lien.is_symlink():
            maux.append(f"bin/{lien.name} n'est pas un lien symbolique.")
            continue
        # Un lien ABSOLU fonctionne ici et nulle part ailleurs : c'est la valeur
        # machine-spécifique que `bin/` existe pour supprimer.
        cible = os.readlink(lien)
        if Path(cible).is_absolute():
            maux.append(
                f"bin/{lien.name} pointe en absolu ({cible}) — attendu : un chemin relatif."
            )
        if not lien.exists():
            maux.append(f"bin/{lien.name} pointe dans le vide ({cible}).")
            continue
        if not os.access(lien, os.X_OK):
            maux.append(f"bin/{lien.name} n'est pas exécutable.")

    # Le PATH ne doit pas seulement CONTENIR bin/ : il doit gagner. Un homonyme
    # installé ailleurs et trouvé en premier est plus trompeur qu'une absence.
    for lien in liens:
        trouve = shutil.which(lien.name)
        if trouve is None:
            maux.append(
                f"« {lien.name} » est introuvable dans le PATH — ajouter au profil :"
                f' export PATH="{bin_dir}:$PATH"'
            )
        elif Path(trouve).resolve() != lien.resolve():
            maux.append(f"« {lien.name} » résout vers {trouve}, pas vers bin/{lien.name}.")

    maux.extend(_dependances(root))
    maux.extend(mods_en_defaut(root))
    maux.extend(plugin_dirs_restant(root))

    if sys.version_info < MIN_PYTHON:
        v = ".".join(str(n) for n in sys.version_info[:3])
        attendu = ".".join(str(n) for n in MIN_PYTHON)
        maux.append(f"Python {attendu} est exigé par les scripts de skill, trouvé {v}.")

    return maux


def main() -> int:
    """Deux destinations, parce que deux lecteurs et deux troncatures.

    L'hôte n'affiche à l'utilisateur que la PREMIÈRE ligne du `stderr` d'un hook en
    échec — constaté le 2026-08-29 : « Failed with non-blocking status code: Santé du
    système de skills — 2 anomalie(s) : », et rien de plus. Un en-tête qui compte sans
    nommer est alors exactement l'information inutile. D'où une ligne unique, complète
    et auto-suffisante.

    Le `stdout` d'un hook `SessionStart` est repris dans le contexte du modèle. C'est
    l'autre lecteur, et le plus concerné : c'est lui qui lance les commandes, donc lui
    qui se heurterait au 127 muet. Il reçoit le détail, une anomalie par ligne.
    """
    maux = anomalies()
    if not maux:
        return 0
    sys.stdout.write(f"Santé du système de skills — {len(maux)} anomalie(s) :\n")
    for m in maux:
        sys.stdout.write(f"  ✗ {m}\n")
    sys.stdout.flush()
    sys.stderr.write(f"{len(maux)} anomalie(s) — " + " ; ".join(maux) + "\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
