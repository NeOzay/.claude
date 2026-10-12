"""Tests de la commande : résolution du projet, écriture, écrasement, échecs."""

from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path

import pytest
import session_dump as sd

type Ligne = Mapping[str, object]
type Ecrire = Callable[[Path, Iterable[Ligne]], Path]

CLI = Path(__file__).resolve().parent.parent / "session-dump-cli.py"


def session_jsonl(titre: str = "Un titre", **extra: object) -> list[Ligne]:
    """Une session de deux tours : assez longue pour n'être écartée par aucun motif."""
    tour: Ligne = {"type": "user", "message": {"role": "user", "content": "salut"}} | extra
    return [tour, tour, {"type": "ai-title", "aiTitle": titre}]


@pytest.fixture
def monde(tmp_path: Path, ecrire_jsonl: Ecrire) -> tuple[Path, Path, dict[str, str]]:
    """Un projet, le répertoire `projects/<id>/` qui lui répond, et l'environnement."""
    projet = tmp_path / "mon projet.v2"
    projet.mkdir()
    config = tmp_path / "config"
    source = config / "projects" / sd.id_projet(projet.resolve())
    ecrire_jsonl(source / "aaaaaaaa.jsonl", session_jsonl("Première"))
    ecrire_jsonl(source / "bbbbbbbb.jsonl", session_jsonl("Seconde"))
    ecrire_jsonl(source / "cccccccc.jsonl", [{"type": "mode"}])
    return projet, source, {"CLAUDE_CONFIG_DIR": str(config)}


def test_id_projet_remplace_tout_caractere_non_alphanumerique() -> None:
    assert sd.id_projet(Path("/home/debian/.claude")) == "-home-debian--claude"
    assert sd.id_projet(Path("/home/debian/mon projet.v2")) == "-home-debian-mon-projet-v2"


def test_repertoire_config(tmp_path: Path) -> None:
    assert sd.repertoire_config({"CLAUDE_CONFIG_DIR": str(tmp_path)}) == tmp_path
    assert sd.repertoire_config({"HOME": str(tmp_path)}) == tmp_path / ".claude"


def test_dumper_ecrit_un_dump_par_session_avec_tour(
    monde: tuple[Path, Path, dict[str, str]],
) -> None:
    projet, _, environ = monde
    bilan = sd.dumper(projet, environ)
    assert isinstance(bilan, sd.Bilan)
    assert (bilan.ecrits, dict(bilan.ecartes), bilan.illisibles) == (2, {"sans-tour": 1}, 0)
    attendu = projet / ".claude" / "session-dump" / sd.id_projet(projet.resolve())
    assert bilan.destination == attendu
    fichiers = sorted(p.name for p in attendu.iterdir())
    assert fichiers == ["sans-date-première.md", "sans-date-seconde.md"]
    _, fm, corps = (attendu / fichiers[0]).read_text(encoding="utf-8").split("+++\n", 2)
    assert tomllib.loads(fm)["titre"] == "Première"
    assert "salut" in corps


def test_dumper_ecrase_les_dumps_perimes(monde: tuple[Path, Path, dict[str, str]]) -> None:
    projet, _, environ = monde
    bilan = sd.dumper(projet, environ)
    assert isinstance(bilan, sd.Bilan)
    perime = bilan.destination / "ancien-dump.md"
    perime.write_text("périmé", encoding="utf-8")
    assert isinstance(sd.dumper(projet, environ), sd.Bilan)
    assert not perime.exists()
    assert len(list(bilan.destination.iterdir())) == 2
    voisins = [p.name for p in bilan.destination.parent.iterdir()]
    assert voisins == [bilan.destination.name]


def test_remplacer_vide_le_repertoire_sans_le_remplacer(tmp_path: Path) -> None:
    destination = tmp_path / "dumps" / "id"
    (destination / "sous").mkdir(parents=True)
    (destination / "sous" / "reste.md").write_text("périmé", encoding="utf-8")
    (destination / "ancien.md").write_text("périmé", encoding="utf-8")
    inode = destination.stat().st_ino
    sd.remplacer(destination, {"a.md": "neuf"})
    assert [p.name for p in destination.iterdir()] == ["a.md"]
    assert destination.stat().st_ino == inode
    assert [p.name for p in destination.parent.iterdir()] == ["id"]


def test_dumper_chemin_inexistant(tmp_path: Path) -> None:
    echec = sd.dumper(tmp_path / "absent", {})
    assert isinstance(echec, sd.Echec)
    assert echec.code == 2


def test_dumper_id_inconnu_nomme_le_chemin_attendu(tmp_path: Path) -> None:
    projet = tmp_path / "p"
    projet.mkdir()
    echec = sd.dumper(projet, {"CLAUDE_CONFIG_DIR": str(tmp_path / "config")})
    assert isinstance(echec, sd.Echec)
    assert echec.code == 1
    assert str(tmp_path / "config" / "projects" / sd.id_projet(projet.resolve())) in echec.message
    assert not (projet / ".claude").exists()


def test_un_echec_d_ecriture_laisse_l_ancien_dump_intact(
    monde: tuple[Path, Path, dict[str, str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    projet, _, environ = monde
    bilan = sd.dumper(projet, environ)
    assert isinstance(bilan, sd.Bilan)
    avant = {p.name: p.read_text(encoding="utf-8") for p in bilan.destination.iterdir()}

    ecrits: list[str] = []
    ecrire = Path.write_text

    def echoue_au_second(self: Path, data: str, *args: object, **kwargs: object) -> int:
        ecrits.append(self.name)
        if len(ecrits) == 2:
            raise OSError("disque plein")
        return ecrire(self, data, *args, **kwargs)  # pyright: ignore[reportArgumentType]

    monkeypatch.setattr(Path, "write_text", echoue_au_second)
    echec = sd.dumper(projet, environ)
    assert isinstance(echec, sd.Echec)
    assert echec.code == 1
    assert "disque plein" in echec.message
    monkeypatch.undo()
    apres = {p.name: p.read_text(encoding="utf-8") for p in bilan.destination.iterdir()}
    assert apres == avant
    assert [p.name for p in bilan.destination.parent.iterdir()] == [bilan.destination.name]


def test_un_demi_caractere_n_empeche_pas_le_dump_et_ne_laisse_rien(
    monde: tuple[Path, Path, dict[str, str]], ecrire_jsonl: Ecrire
) -> None:
    projet, source, environ = monde
    # `json.dumps` écrit la moitié de paire en échappement ASCII `\ud83d`, que `json.loads` relit.
    ecrire_jsonl(source / "dddddddd.jsonl", session_jsonl("Titre \ud83d seul"))
    ligne = {"type": "user", "message": {"role": "user", "content": "texte \ud83d seul"}}
    ecrire_jsonl(source / "eeeeeeee.jsonl", [ligne, ligne])
    bilan = sd.dumper(projet, environ)
    assert isinstance(bilan, sd.Bilan)
    assert bilan.ecrits == 4
    contenus = [p.read_text(encoding="utf-8") for p in bilan.destination.iterdir()]
    assert any("texte \ufffd seul" in contenu for contenu in contenus)
    assert [p.name for p in bilan.destination.parent.iterdir()] == [bilan.destination.name]


def test_toute_erreur_d_ecriture_retire_le_repertoire_en_construction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "dumps" / "id"

    # `write_text` est appelé avec `encoding=` : le remplaçant doit accepter les mêmes arguments.
    def echoue(*_: object, **__: object) -> int:  # pyright: ignore[reportUnusedParameter]
        raise ValueError("inattendue")

    monkeypatch.setattr(Path, "write_text", echoue)
    with pytest.raises(ValueError, match="inattendue"):
        sd.remplacer(destination, {"a.md": "x"})
    assert list(destination.parent.iterdir()) == []


def lancer(cwd: Path, environ: Mapping[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=cwd,
        env={**os.environ, **environ},
        capture_output=True,
        text=True,
        check=False,
    )


def test_la_commande_sans_argument_prend_le_repertoire_courant(
    monde: tuple[Path, Path, dict[str, str]],
) -> None:
    projet, _, environ = monde
    resultat = lancer(projet, environ)
    assert resultat.returncode == 0, resultat.stderr
    assert "2 dumps écrits" in resultat.stdout
    assert "1 session(s) écartée(s) — sans tour" in resultat.stdout


def test_la_commande_avec_le_chemin_d_un_autre_projet(
    monde: tuple[Path, Path, dict[str, str]], tmp_path: Path
) -> None:
    projet, _, environ = monde
    ailleurs = tmp_path / "ailleurs"
    ailleurs.mkdir()
    resultat = lancer(ailleurs, environ, str(projet))
    assert resultat.returncode == 0, resultat.stderr
    assert (projet / ".claude" / "session-dump").is_dir()
    assert not (ailleurs / ".claude").exists()


def test_la_commande_sort_2_sur_un_chemin_inexistant(tmp_path: Path) -> None:
    resultat = lancer(tmp_path, {}, str(tmp_path / "absent"))
    assert resultat.returncode == 2
    assert "n'est pas un répertoire" in resultat.stderr


def test_la_commande_sort_1_sans_session(tmp_path: Path) -> None:
    resultat = lancer(tmp_path, {"CLAUDE_CONFIG_DIR": str(tmp_path / "vide")})
    assert resultat.returncode == 1
    assert "aucune session" in resultat.stderr


def test_dumper_compte_les_ecartees_par_motif(
    monde: tuple[Path, Path, dict[str, str]], ecrire_jsonl: Ecrire
) -> None:
    projet, source, environ = monde
    ecrire_jsonl(source / "dddddddd.jsonl", session_jsonl("Par -p", entrypoint="sdk-cli"))
    ecrire_jsonl(source / "eeeeeeee.jsonl", session_jsonl("Par -p bis", entrypoint="sdk-cli"))
    ecrire_jsonl(source / "ffffffff.jsonl", session_jsonl("Courte")[1:])
    bilan = sd.dumper(projet, environ)
    assert isinstance(bilan, sd.Bilan)
    assert bilan.ecrits == 2
    assert dict(bilan.ecartes) == {"sans-tour": 1, "claude-p": 2, "trop-courte": 1}
    assert sorted(p.name for p in bilan.destination.iterdir()) == [
        "sans-date-première.md",
        "sans-date-seconde.md",
    ]


def test_la_commande_rapporte_chaque_motif_d_ecart(
    monde: tuple[Path, Path, dict[str, str]], ecrire_jsonl: Ecrire
) -> None:
    projet, source, environ = monde
    ecrire_jsonl(source / "dddddddd.jsonl", session_jsonl("Par -p", entrypoint="sdk-cli"))
    ecrire_jsonl(source / "ffffffff.jsonl", session_jsonl("Courte")[1:])
    resultat = lancer(projet, environ)
    assert resultat.returncode == 0, resultat.stderr
    assert resultat.stdout.splitlines()[1:] == [
        "session-dump : 1 session(s) écartée(s) — sans tour",
        "session-dump : 1 session(s) écartée(s) — lancée(s) par claude -p",
        "session-dump : 1 session(s) écartée(s) — moins de 2 tours et de 10 000 tokens",
    ]


def test_la_commande_ne_dit_rien_des_motifs_sans_ecartee(
    tmp_path: Path, ecrire_jsonl: Ecrire
) -> None:
    projet = tmp_path / "p"
    projet.mkdir()
    config = tmp_path / "config"
    ecrire_jsonl(
        config / "projects" / sd.id_projet(projet.resolve()) / "aaaaaaaa.jsonl", session_jsonl()
    )
    resultat = lancer(projet, {"CLAUDE_CONFIG_DIR": str(config)})
    assert resultat.returncode == 0, resultat.stderr
    assert len(resultat.stdout.splitlines()) == 1
