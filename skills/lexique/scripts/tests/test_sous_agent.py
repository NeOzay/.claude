"""Lexiques d'un sous-agent : ce que son fichier décide qu'il reçoit."""

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from lexique import annonce_sous_agent, entete_agent, fichier_agent

Ecrire = Callable[[str, str], Path]

LOCAL = "| Zorglubage | Un terme local. | [x](x) |\n"
GLOBAL = "| Gabarit | Un fichier posé. | [g](g) |\n"


def _agent(dossier: Path, nom: str, champs: str = "", sous: str = "") -> Path:
    """Pose `<dossier>/agents/<sous>/<nom>.md` avec le frontmatter `name` et `champs`."""
    fichier = dossier / "agents" / sous / f"{nom}.md"
    fichier.parent.mkdir(parents=True, exist_ok=True)
    fichier.write_text(f"---\nname: {nom}\n{champs}---\nCorps.\n", encoding="utf-8")
    return fichier


def _decor(ecrire: Ecrire, tmp_path: Path) -> tuple[Path, Path]:
    """Un projet (avec lexique local) et une racine globale (lexique et instructions)."""
    projet = tmp_path / "p"
    ecrire("p/.claude/LEXIQUE.md", LOCAL)
    racine = tmp_path / "racine"
    ecrire("racine/LEXIQUE.md", GLOBAL)
    instructions = racine / "skills" / "lexique" / "instructions.md"
    instructions.parent.mkdir(parents=True)
    instructions.write_text("# Règles du lexique\n", encoding="utf-8")
    return projet, racine


def test_entete_lit_les_scalaires_et_ote_les_guillemets(tmp_path: Path) -> None:
    f = _agent(tmp_path, "a", 'omitClaudeMd: "true"\ntools: Read, Grep\n')
    assert entete_agent(f) == {"name": "a", "omitClaudeMd": "true", "tools": "Read, Grep"}


def test_entete_vide_sans_frontmatter_ou_sans_fichier(tmp_path: Path) -> None:
    f = tmp_path / "x.md"
    f.write_text("name: a\n", encoding="utf-8")
    assert entete_agent(f) == {}
    assert entete_agent(tmp_path / "absent.md") == {}


def test_agent_introuvable(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, racine = _decor(ecrire, tmp_path)
    assert fichier_agent("inconnu", projet, racine) is None
    assert annonce_sous_agent("Explore", projet, racine) == ""
    assert annonce_sous_agent("plugin:agent", projet, racine) == ""


def test_sans_omit_verse_le_local(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, racine = _decor(ecrire, tmp_path)
    _agent(racine, "a")
    texte = annonce_sous_agent("a", projet, racine)
    assert texte.startswith(f"Lexique local de {projet}")
    assert "Zorglubage" in texte
    assert "Gabarit" not in texte


def test_sans_omit_ni_lexique_local_rien(tmp_path: Path) -> None:
    racine = tmp_path / "racine"
    _agent(racine, "a")
    assert annonce_sous_agent("a", tmp_path / "p", racine) == ""


def test_omit_seul_isole(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, racine = _decor(ecrire, tmp_path)
    _agent(racine, "a", "omitClaudeMd: true\n")
    assert annonce_sous_agent("a", projet, racine) == ""


def test_entete_lit_le_yaml_comme_claude_code(tmp_path: Path) -> None:
    f = _agent(tmp_path, "a", "omitClaudeMd: True\ninjectLexique: true  # voulu\nautre: 'x # y'\n")
    champs = entete_agent(f)
    assert champs["omitClaudeMd"] == "true"
    assert champs["injectLexique"] == "true"
    assert champs["autre"] == "x # y"
    assert entete_agent(_agent(tmp_path, "b", 'omitClaudeMd: "True"\n'))["omitClaudeMd"] == "True"


def test_omit_majuscule_ou_commente_isole(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, racine = _decor(ecrire, tmp_path)
    _agent(racine, "a", "omitClaudeMd: True\n")
    _agent(racine, "b", "omitClaudeMd: true  # isolé\n")
    assert annonce_sous_agent("a", projet, racine) == ""
    assert annonce_sous_agent("b", projet, racine) == ""


def test_omit_chaine_majuscule_n_isole_pas(ecrire: Ecrire, tmp_path: Path) -> None:
    """Claude Code ne lit que `"true"` exact entre guillemets : `"True"` n'isole pas."""
    projet, racine = _decor(ecrire, tmp_path)
    _agent(racine, "a", 'omitClaudeMd: "True"\n')
    assert "Zorglubage" in annonce_sous_agent("a", projet, racine)


def test_omit_entre_guillemets_vaut_vrai(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, racine = _decor(ecrire, tmp_path)
    _agent(racine, "a", 'omitClaudeMd: "true"\n')
    assert annonce_sous_agent("a", projet, racine) == ""


def test_omit_et_injection_versent_les_trois_dans_l_ordre(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, racine = _decor(ecrire, tmp_path)
    _agent(racine, "a", "omitClaudeMd: true\ninjectLexique: true\n")
    texte = annonce_sous_agent("a", projet, racine)
    ordre = [texte.index(m) for m in ("Règles du lexique", "Gabarit", "Zorglubage")]
    assert ordre == sorted(ordre)
    assert f"Instructions du lexique ({racine / 'skills' / 'lexique' / 'instructions.md'})" in texte
    assert f"Lexique global ({racine / 'LEXIQUE.md'})" in texte
    assert f"Lexique local de {projet}" in texte


def test_injection_refusee_isole(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, racine = _decor(ecrire, tmp_path)
    _agent(racine, "a", "omitClaudeMd: true\ninjectLexique: false\n")
    assert annonce_sous_agent("a", projet, racine) == ""


def test_injection_sans_omit_ne_verse_que_le_local(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, racine = _decor(ecrire, tmp_path)
    _agent(racine, "a", "injectLexique: true\n")
    texte = annonce_sous_agent("a", projet, racine)
    assert "Zorglubage" in texte
    assert "Règles du lexique" not in texte


def test_injection_sans_lexique_local_verse_global_et_instructions(
    ecrire: Ecrire, tmp_path: Path
) -> None:
    _, racine = _decor(ecrire, tmp_path)
    _agent(racine, "a", "omitClaudeMd: true\ninjectLexique: true\n")
    texte = annonce_sous_agent("a", tmp_path / "sans-lexique", racine)
    assert "Règles du lexique" in texte
    assert "Gabarit" in texte
    assert "Lexique local" not in texte


def test_fichier_illisible_se_dit_dans_son_bloc(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, racine = _decor(ecrire, tmp_path)
    (racine / "skills" / "lexique" / "instructions.md").unlink()
    _agent(racine, "a", "omitClaudeMd: true\ninjectLexique: true\n")
    texte = annonce_sous_agent("a", projet, racine)
    assert "(illisible ou absent)" in texte
    assert "Gabarit" in texte
    assert "Zorglubage" in texte


def test_agent_de_projet_masque_agent_utilisateur(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, racine = _decor(ecrire, tmp_path)
    _agent(racine, "a", "omitClaudeMd: true\n")
    doublon = _agent(projet / ".claude", "a")
    assert fichier_agent("a", projet, racine) == doublon
    assert "Zorglubage" in annonce_sous_agent("a", projet, racine)


def test_agent_dans_un_sous_repertoire(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, racine = _decor(ecrire, tmp_path)
    f = _agent(racine, "a", sous="equipe/sous")
    assert fichier_agent("a", projet, racine) == f


CLI = Path(__file__).resolve().parents[1] / "lexique-cli.py"


def _hook(projet: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(projet)}
    return subprocess.run(
        [sys.executable, str(CLI), "sous-agent", *args],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_cli_verse_le_local_en_texte_brut(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, _ = _decor(ecrire, tmp_path)
    _agent(projet / ".claude", "a")
    r = _hook(projet, "a")
    assert r.returncode == 0
    assert "Zorglubage" in r.stdout


def test_cli_silencieuse_pour_un_agent_isole(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, _ = _decor(ecrire, tmp_path)
    _agent(projet / ".claude", "a", "omitClaudeMd: true\n")
    r = _hook(projet, "a")
    assert (r.returncode, r.stdout) == (0, "")


def test_cli_silencieuse_pour_un_agent_inconnu(ecrire: Ecrire, tmp_path: Path) -> None:
    projet, _ = _decor(ecrire, tmp_path)
    r = _hook(projet, "Explore")
    assert (r.returncode, r.stdout) == (0, "")


def test_cli_en_deux_sans_type_d_agent(tmp_path: Path) -> None:
    r = _hook(tmp_path)
    assert (r.returncode, r.stdout) == (2, "")
