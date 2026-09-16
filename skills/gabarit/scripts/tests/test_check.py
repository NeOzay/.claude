"""`gabarit check` — un fichier confronté au contrat de sa semence.

CE QUE CE FICHIER PROUVE : la semence se retrouve par l'estampille, qui n'est jamais
comptée comme champ non déclaré ; un fichier sans estampille n'est vérifié que contre
une semence imposée ; les deux verdicts — structure, puis `--filled` — sont ceux de
`list-dir validate` ; une semence imposée qui contredit l'estampille est dite sans
changer le verdict. Le dernier bloc lance le point d'entrée.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from gabarit.commandes import check, lire_semence, new, trouver_semence
from gabarit.definitions import DEFS, roots

CLI = Path(__file__).resolve().parent.parent / "gabarit-cli.py"

CONTRAT = """name = "essai"
description = ""

[fields.titre]
type = "text"
required = true
description = ""

[fields.notes]
type = "text"
description = ""

[sections."Objectif"]
required = true
description = ""
"""


def semer(racine: Path, nom: str = "essai", contrat: str = CONTRAT) -> Path:
    d = racine / nom
    d.mkdir(parents=True)
    _ = (d / "contract.toml").write_text(contrat, encoding="utf-8")
    return d


def projet_avec_fiche(tmp_path: Path) -> tuple[Path, Path]:
    """Un projet dont la semence `essai` est au rang 1, et une fiche fraîchement posée."""
    projet = tmp_path / "projet"
    d = semer(projet / ".claude" / DEFS)
    fiche = projet / "fiche.md"
    _ = new(fiche, lire_semence(d).unwrap()).unwrap()
    return projet, fiche


def remplir(fiche: Path) -> None:
    texte = fiche.read_text(encoding="utf-8")
    texte = texte.replace('titre = "<À REMPLIR>"', 'titre = "Un titre"')
    texte = texte.replace("## Objectif\n\n<À REMPLIR>", "## Objectif\n\nCe qu'on vise.")
    _ = fiche.write_text(texte, encoding="utf-8")


# ---------------------------------------------------------------- par estampille
def test_une_fiche_posee_est_conforme_sans_etre_remplie(tmp_path: Path) -> None:
    projet, fiche = projet_avec_fiche(tmp_path)
    where = roots(DEFS, cwd=projet, package=tmp_path / "ailleurs")

    r = check(fiche, where=where)

    assert r, r.message
    assert "conforme à la semence « essai »" in r.unwrap()
    assert r.message == ""


def test_filled_reclame_les_requis_et_pas_les_facultatifs(tmp_path: Path) -> None:
    projet, fiche = projet_avec_fiche(tmp_path)
    where = roots(DEFS, cwd=projet, package=tmp_path / "ailleurs")

    r = check(fiche, filled=True, where=where)
    assert not r
    assert "champ « titre » — à remplir" in r.message
    assert "section « Objectif » — à remplir" in r.message
    assert "notes" not in r.message
    assert "2 manquements" in r.message

    remplir(fiche)
    assert check(fiche, filled=True, where=where)


def test_un_champ_non_declare_est_signale_mais_pas_l_estampille(tmp_path: Path) -> None:
    projet, fiche = projet_avec_fiche(tmp_path)
    where = roots(DEFS, cwd=projet, package=tmp_path / "ailleurs")
    texte = fiche.read_text(encoding="utf-8").replace("+++\n\n", 'intrus = "x"\n+++\n\n', 1)
    _ = fiche.write_text(texte, encoding="utf-8")

    r = check(fiche, where=where)

    assert not r
    assert "champ « intrus » — non déclaré au contrat" in r.message
    assert "gabarit" not in r.message.split("\n\n")[0]


def test_une_estampille_qui_ne_se_resout_pas_est_nommee(tmp_path: Path) -> None:
    projet, fiche = projet_avec_fiche(tmp_path)
    where = roots(DEFS, cwd=tmp_path / "vide", package=tmp_path / "ailleurs")
    _ = projet

    r = check(fiche, where=where)

    assert not r
    assert "semence « essai » introuvable" in r.message
    assert r.message.startswith(f"{fiche}: estampille « essai »")


def test_une_estampille_mal_formee_est_refusee(tmp_path: Path) -> None:
    _, fiche = projet_avec_fiche(tmp_path)
    texte = fiche.read_text(encoding="utf-8").replace('gabarit = "essai"', 'gabarit = "a b"')
    _ = fiche.write_text(texte, encoding="utf-8")

    r = check(fiche, where=[])

    assert not r
    assert "champ « gabarit »" in r.message


# ---------------------------------------------------------------- semence imposée
def test_sans_estampille_ni_semence_imposee_echec_nomme(tmp_path: Path) -> None:
    fiche = tmp_path / "fiche.md"
    _ = fiche.write_text('+++\ntitre = "x"\n+++\n\n## Objectif\n\nv\n', encoding="utf-8")

    r = check(fiche, where=[])

    assert not r
    assert "aucune estampille" in r.message
    assert "--def" in r.message


def test_sans_estampille_avec_semence_imposee(tmp_path: Path) -> None:
    fiche = tmp_path / "fiche.md"
    _ = fiche.write_text('+++\ntitre = "x"\n+++\n\n## Objectif\n\nv\n', encoding="utf-8")
    semence = lire_semence(semer(tmp_path / "semences")).unwrap()

    assert check(fiche, filled=True, semence=semence)


def test_semence_imposee_contredisant_l_estampille_est_dite(tmp_path: Path) -> None:
    _, fiche = projet_avec_fiche(tmp_path)
    autre = trouver_semence(None, semer(tmp_path / "semences", nom="autre")).unwrap()

    r = check(fiche, semence=autre)

    assert r
    assert "estampillé « essai », vérifié contre la semence « autre »" in r.message


# ------------------------------------------------------------------- point d'entrée
def lancer(*argv: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *argv], cwd=cwd, capture_output=True, text=True, check=False
    )


def test_cli_check_codes_et_canaux(tmp_path: Path) -> None:
    projet, fiche = projet_avec_fiche(tmp_path)

    r = lancer("check", fiche.name, cwd=projet)
    assert r.returncode == 0, r.stderr
    assert "conforme" in r.stdout

    r = lancer("check", fiche.name, "--filled", cwd=projet)
    assert r.returncode == 1
    assert "à remplir" in r.stderr
    assert r.stdout == ""


def test_cli_check_def_et_from_exclusifs(tmp_path: Path) -> None:
    projet, fiche = projet_avec_fiche(tmp_path)
    r = lancer("check", fiche.name, "--def", "essai", "--from", "x", cwd=projet)
    assert r.returncode == 2
