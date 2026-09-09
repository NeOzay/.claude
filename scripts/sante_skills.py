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

import os
import re
import shutil
import sys
from pathlib import Path

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
            maux.append(f"bin/{lien.name} pointe en absolu ({cible}) — attendu : un chemin relatif.")
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
