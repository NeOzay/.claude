"""Santé du système de skills — ce que le hook de démarrage garantit.

Chaque cas monte un `bin/` jouet : le script ne lit que la racine qu'on lui donne,
donc un test se réduit à fabriquer le défaut visé. Aucun test ne lit le vrai dépôt —
un contrôle qui ne passerait au vert qu'ici serait invérifiable.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import sante_skills


@pytest.fixture
def racine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Une racine jouet avec un `bin/` vide et un skill à cibler."""
    (tmp_path / "bin").mkdir()
    cible = tmp_path / "skills" / "x" / "scripts" / "y.py"
    cible.parent.mkdir(parents=True)
    _ = cible.write_text("#!/usr/bin/env python3\n")
    cible.chmod(0o755)
    monkeypatch.setattr(sante_skills, "racine", lambda: tmp_path)
    return tmp_path


def lier(racine: Path, nom: str, cible: str) -> None:
    (racine / "bin" / nom).symlink_to(cible)


def test_systeme_sain(racine: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    lier(racine, "y", "../skills/x/scripts/y.py")
    monkeypatch.setenv("PATH", str(racine / "bin") + os.pathsep + os.environ["PATH"])
    assert sante_skills.anomalies() == []


def test_bin_absent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sante_skills, "racine", lambda: tmp_path)
    assert any("n'existe pas" in m for m in sante_skills.anomalies())


@pytest.mark.usefixtures("racine")
def test_bin_vide() -> None:
    """Le `bin/` que monte la fixture est vide : elle sert ici d'effet de bord seul."""
    assert any("est vide" in m for m in sante_skills.anomalies())


def test_lien_casse(racine: Path) -> None:
    lier(racine, "y", "../skills/x/scripts/disparu.py")
    assert any("pointe dans le vide" in m for m in sante_skills.anomalies())


def test_lien_absolu(racine: Path) -> None:
    """Un lien absolu marche ici et nulle part ailleurs : c'est ce que bin/ supprime."""
    lier(racine, "y", str(racine / "skills" / "x" / "scripts" / "y.py"))
    assert any("pointe en absolu" in m for m in sante_skills.anomalies())


def test_absent_du_path(racine: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    lier(racine, "y", "../skills/x/scripts/y.py")
    monkeypatch.setenv("PATH", "/nulle/part")
    maux = sante_skills.anomalies()
    assert any("introuvable dans le PATH" in m for m in maux)
    assert any('export PATH="' in m for m in maux), "le message doit dire quoi faire"


def test_homonyme_gagne_dans_le_path(racine: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Plus trompeur qu'une absence : la commande existe, mais ce n'est pas la nôtre."""
    autre = racine / "ailleurs"
    autre.mkdir()
    impost = autre / "y"
    _ = impost.write_text("#!/bin/sh\n")
    impost.chmod(0o755)
    lier(racine, "y", "../skills/x/scripts/y.py")
    monkeypatch.setenv("PATH", str(autre) + os.pathsep + str(racine / "bin"))
    assert any("résout vers" in m for m in sante_skills.anomalies())


def test_fichier_ordinaire_dans_bin(racine: Path) -> None:
    _ = (racine / "bin" / "y").write_text("#!/bin/sh\n")
    assert any("n'est pas un lien symbolique" in m for m in sante_skills.anomalies())


# --- Deux lecteurs, deux troncatures ----------------------------------------
#
# Constaté le 2026-08-29 : de tout le `stderr` d'un hook en échec, l'hôte n'affiche à
# l'utilisateur que la PREMIÈRE ligne. Un en-tête qui compte sans nommer y perd
# exactement ce qui sert.


def test_stderr_tient_sur_une_ligne_et_nomme_tout(
    racine: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    lier(racine, "casse", "../skills/x/scripts/disparu.py")
    code = sante_skills.main()
    capture = capsys.readouterr()

    assert code == 1
    lignes = capture.err.rstrip("\n").split("\n")
    assert len(lignes) == 1, "l'hôte ne montre que la première ligne : tout doit y tenir"
    assert "pointe dans le vide" in lignes[0], "la ligne unique doit nommer l'anomalie"


def test_stdout_porte_le_detail(racine: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Le `stdout` d'un hook SessionStart revient au modèle — l'autre lecteur."""
    lier(racine, "casse", "../skills/x/scripts/disparu.py")
    _ = sante_skills.main()
    capture = capsys.readouterr()

    assert "pointe dans le vide" in capture.out
    assert capture.out.count("✗") >= 1


def test_silencieux_sur_les_deux_flux_quand_tout_va_bien(
    racine: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    lier(racine, "y", "../skills/x/scripts/y.py")
    monkeypatch.setenv("PATH", str(racine / "bin") + os.pathsep + os.environ["PATH"])
    code = sante_skills.main()
    capture = capsys.readouterr()

    assert code == 0
    assert capture.out == "" and capture.err == ""
