"""`liste`, `cherche`, `charge`, `chemin` : sortie tabulée et codes de sortie.

Le niveau global est celui du dépôt : les skills posés ici portent des noms inventés, qu'il ne
peut pas déjà définir.
"""

import subprocess
import sys
from pathlib import Path

from conftest import Poser

CLI = Path(__file__).resolve().parents[1] / "shadow-skill-cli.py"
LOCAL = "p/.claude/shadow-skills"


def _cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args], capture_output=True, text=True, check=False
    )


def test_liste_rend_un_skill_local(poser: Poser, tmp_path: Path) -> None:
    poser(LOCAL, "zorglub", description="Un skill inventé.", quand="Pour zorgluber.")
    r = _cli("liste", "--projet", str(tmp_path / "p"))
    assert r.returncode == 0, r.stderr
    assert "local\tzorglub\tUn skill inventé.\tPour zorgluber." in r.stdout.splitlines()


def test_liste_dit_un_skill_mal_forme_sans_echouer(poser: Poser, tmp_path: Path) -> None:
    poser(LOCAL, "zorglub", front='name = "zorglub"\n')
    r = _cli("liste", "--projet", str(tmp_path / "p"))
    assert r.returncode == 0
    assert "zorglub" in r.stderr


def test_cherche_trouve_et_sort_en_un_sinon(poser: Poser, tmp_path: Path) -> None:
    poser(LOCAL, "zorglub", tags=["zorglang"])
    p = str(tmp_path / "p")
    r = _cli("cherche", "ZORGLANG", "--projet", p)
    assert r.returncode == 0, r.stderr
    assert r.stdout.startswith("local\tzorglub\t")
    assert _cli("cherche", "zorglang", "introuvable-xyz", "--projet", p).returncode == 1


def test_charge_affiche_le_fichier(poser: Poser, tmp_path: Path) -> None:
    chemin = poser(LOCAL, "zorglub")
    r = _cli("charge", "zorglub", "--projet", str(tmp_path / "p"))
    assert r.returncode == 0, r.stderr
    assert r.stdout.startswith(f"Répertoire : {chemin.parent}\n")
    assert "## Instructions" in r.stdout


def test_chemin_et_charge_sortent_en_un_sur_un_nom_inconnu(tmp_path: Path) -> None:
    for commande in ("chemin", "charge"):
        r = _cli(commande, "zorglub-inconnu", "--projet", str(tmp_path))
        assert r.returncode == 1
        assert "aucun Shadow-skill de ce nom" in r.stderr


def test_chemin_rend_le_fichier_principal(poser: Poser, tmp_path: Path) -> None:
    chemin = poser(LOCAL, "zorglub")
    r = _cli("chemin", "zorglub", "--projet", str(tmp_path / "p"))
    assert r.returncode == 0, r.stderr
    assert r.stdout == f"{chemin}\n"


def test_erreur_d_appel() -> None:
    assert _cli().returncode == 2
    assert _cli("cherche").returncode == 2


def _suivi(tmp_path: Path, front: str, slug: str = "zorg-chantier") -> Path:
    chemin = tmp_path / "p" / ".claude" / "implementation" / f"{slug}.md"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(f"+++\n{front}+++\n\n## Étapes\n\nx\n", encoding="utf-8")
    return chemin


def test_depuis_suivi_rend_les_skills_du_suivi(poser: Poser, tmp_path: Path) -> None:
    poser(LOCAL, "zorglub", description="Un skill.", quand="Pour zorgluber.")
    _suivi(tmp_path, 'skills = ["zorglub"]\n')
    r = _cli("depuis-suivi", "zorg-chantier", "--projet", str(tmp_path / "p"))
    assert r.returncode == 0, r.stderr
    assert r.stdout == "zorglub\tUn skill.\tPour zorgluber.\n"


def test_depuis_suivi_sert_les_connus_et_sort_en_un_sur_un_inconnu(
    poser: Poser, tmp_path: Path
) -> None:
    poser(LOCAL, "zorglub")
    _suivi(tmp_path, 'skills = ["zorglub-inconnu", "zorglub"]\n')
    r = _cli("depuis-suivi", "zorg-chantier", "--projet", str(tmp_path / "p"))
    assert r.returncode == 1
    assert r.stdout.startswith("zorglub\t")
    assert "zorglub-inconnu" in r.stderr


def test_depuis_suivi_sort_en_un_sans_champ_skills(tmp_path: Path) -> None:
    _suivi(tmp_path, 'slug = "x"\n')
    r = _cli("depuis-suivi", "zorg-chantier", "--projet", str(tmp_path / "p"))
    assert r.returncode == 1
    assert "aucun champ « skills »" in r.stderr


def test_depuis_suivi_d_une_liste_vide_ne_rend_rien(tmp_path: Path) -> None:
    _suivi(tmp_path, "skills = []\n")
    r = _cli("depuis-suivi", "zorg-chantier", "--projet", str(tmp_path / "p"))
    assert (r.returncode, r.stdout) == (0, "")


def test_depuis_suivi_sort_en_un_sans_suivi_actif(tmp_path: Path) -> None:
    r = _cli("depuis-suivi", "zorg-absent", "--projet", str(tmp_path / "p"))
    assert r.returncode == 1
    assert "aucun Suivi actif" in r.stderr


def test_depuis_suivi_refuse_un_chemin_pour_slug(tmp_path: Path) -> None:
    for slug in ("../x", "a/b", ".cache"):
        r = _cli("depuis-suivi", slug, "--projet", str(tmp_path / "p"))
        assert r.returncode == 1
        assert "n'est pas un slug" in r.stderr


def test_tags_rend_le_registre_local(tmp_path: Path) -> None:
    racine = tmp_path / LOCAL
    racine.mkdir(parents=True)
    (racine / "tags.toml").write_text('zorgtag = "Un tag inventé."\n', encoding="utf-8")
    r = _cli("tags", "--projet", str(tmp_path / "p"))
    assert r.returncode == 0, r.stderr
    assert "local\tzorgtag\tUn tag inventé." in r.stdout.splitlines()


def test_verifie_sort_en_un_sur_un_tag_hors_registre(poser: Poser, tmp_path: Path) -> None:
    poser(LOCAL, "zorglub", tags=["zorgtag-inconnu"])
    r = _cli("verifie", "--projet", str(tmp_path / "p"))
    assert r.returncode == 1
    assert "zorgtag-inconnu" in r.stderr
