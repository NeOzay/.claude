"""Tests de la commande `contexte` : écriture par la statusline, lecture par l'agent."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import contexte
import pytest

SESSION = "1f6e9a80-8cf2-4d2c-92cf-dca8fce47cc7"


def env(tmp_path: Path, **extra: str) -> dict[str, str]:
    return {"XDG_RUNTIME_DIR": str(tmp_path), **extra}


def test_ecrire_puis_lire(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert contexte.main(["ecrire", SESSION, "123456"], env(tmp_path)) == 0
    assert contexte.main([], env(tmp_path, CLAUDE_CODE_SESSION_ID=SESSION)) == 0
    assert capsys.readouterr().out == "123456\n"


def test_reecrire_remplace(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    contexte.main(["ecrire", SESSION, "10"], env(tmp_path))
    contexte.main(["ecrire", SESSION, "20"], env(tmp_path))
    contexte.main([], env(tmp_path, CLAUDE_CODE_SESSION_ID=SESSION))
    assert capsys.readouterr().out == "20\n"
    # Le fichier temporaire de l'écriture atomique ne doit pas rester derrière.
    assert [p.name for p in (tmp_path / "claude-contexte").iterdir()] == [SESSION]


def test_sessions_separees(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    contexte.main(["ecrire", SESSION, "10"], env(tmp_path))
    contexte.main(["ecrire", "autre", "99"], env(tmp_path))
    contexte.main([], env(tmp_path, CLAUDE_CODE_SESSION_ID=SESSION))
    assert capsys.readouterr().out == "10\n"


def test_session_absente_de_l_environnement(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert contexte.main([], env(tmp_path)) == 1
    assert "CLAUDE_CODE_SESSION_ID" in capsys.readouterr().err


def test_mesure_absente(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert contexte.main([], env(tmp_path, CLAUDE_CODE_SESSION_ID=SESSION)) == 1
    sortie = capsys.readouterr()
    assert sortie.out == ""
    assert "aucune mesure" in sortie.err


def test_mesure_illisible(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rep = tmp_path / "claude-contexte"
    rep.mkdir()
    (rep / SESSION).write_text("pas un nombre\n")
    assert contexte.main([], env(tmp_path, CLAUDE_CODE_SESSION_ID=SESSION)) == 1
    assert capsys.readouterr().out == ""


def test_mesure_non_utf8(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rep = tmp_path / "claude-contexte"
    rep.mkdir()
    (rep / SESSION).write_bytes(b"\xff\xfe")
    assert contexte.main([], env(tmp_path, CLAUDE_CODE_SESSION_ID=SESSION)) == 1
    assert "aucune mesure" in capsys.readouterr().err


def test_ecriture_impossible(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Un fichier à la place du répertoire des mesures : mkdir échoue.
    (tmp_path / "claude-contexte").write_text("")
    assert contexte.main(["ecrire", SESSION, "1"], env(tmp_path)) == 1
    assert "écriture impossible" in capsys.readouterr().err


def test_echec_d_ecriture_ne_laisse_rien(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def refuser(_src: object, _dst: object) -> None:
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(os, "replace", refuser)
    with pytest.raises(OSError):
        contexte.ecrire(tmp_path, SESSION, 1)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("session", ["../evasion", "a/b", "", ".cache", "-x"])
def test_session_invalide_refusee(tmp_path: Path, session: str) -> None:
    assert contexte.main(["ecrire", session, "1"], env(tmp_path)) == 2
    assert not (tmp_path / "claude-contexte").exists()


@pytest.mark.parametrize("tokens", ["-3", "abc", "1.5", "", "١٢"])
def test_tokens_invalides_refuses(tmp_path: Path, tokens: str) -> None:
    assert contexte.main(["ecrire", SESSION, tokens], env(tmp_path)) == 2
    assert not (tmp_path / "claude-contexte").exists()


@pytest.mark.parametrize("argv", [["lire"], ["ecrire", SESSION], ["ecrire", SESSION, "1", "2"]])
def test_appel_invalide(
    tmp_path: Path, argv: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    assert contexte.main(argv, env(tmp_path)) == 2
    assert "usage" in capsys.readouterr().err


def test_repertoire_xdg(tmp_path: Path) -> None:
    assert contexte.repertoire(env(tmp_path)) == tmp_path / "claude-contexte"


def test_repertoire_sans_xdg(tmp_path: Path) -> None:
    attendu = tmp_path / ".cache" / "claude-contexte"
    assert contexte.repertoire({"HOME": str(tmp_path)}) == attendu
    assert contexte.repertoire({"XDG_RUNTIME_DIR": "", "HOME": str(tmp_path)}) == attendu


def test_commande_executable(tmp_path: Path) -> None:
    """Le script tourne seul, tel que le lien de `bin/` l'exécute."""
    script = Path(contexte.__file__)
    assert os.access(script, os.X_OK)
    environ = {**os.environ, **env(tmp_path, CLAUDE_CODE_SESSION_ID=SESSION)}
    subprocess.run([script, "ecrire", SESSION, "42"], env=environ, check=True)
    lu = subprocess.run([script], env=environ, check=True, capture_output=True, text=True)
    assert lu.stdout == "42\n"
