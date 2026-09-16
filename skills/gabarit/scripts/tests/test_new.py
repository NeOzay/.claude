"""`gabarit new` — poser un fichier depuis une semence, et l'estampiller.

CE QUE CE FICHIER PROUVE : le fichier créé porte tout le contrat — marqueurs,
préremplissage, sections — et l'estampille `gabarit = "<nom>"` en tête ; la semence se
trouve par son nom dans les racines ou se prend à un chemin, jamais les deux ; rien
n'est écrasé ni écrit à moitié ; l'environnement `GABARIT_*` est celui annoncé. Le
dernier bloc lance le point d'entrée : codes de sortie et canaux.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from gabarit.commandes import ESTAMPILLE, lire_semence, new, trouver_semence
from gabarit.definitions import DEFS, roots
from gabarit.items import read_item
from gabarit.types import OPTIONAL, PLACEHOLDER

CLI = Path(__file__).resolve().parent.parent / "gabarit-cli.py"

CONTRAT = """name = "essai"
description = "une semence d'essai"

[fields.titre]
type = "text"
required = true
description = "l'intitulé"

[fields.session]
type = "int"
required = true
description = ""
text = "1"

[fields.notes]
type = "text"
description = ""

[sections."Objectif"]
required = true
description = "ce qu'on vise"

[sections."Journal"]
description = ""
text = "Rien à ce jour."
"""


def semer(racine: Path, nom: str = "essai", contrat: str = CONTRAT) -> Path:
    d = racine / nom
    d.mkdir(parents=True)
    _ = (d / "contract.toml").write_text(contrat, encoding="utf-8")
    return d


# ------------------------------------------------------------------------- pose
def test_new_pose_tout_le_contrat_et_l_estampille(tmp_path: Path) -> None:
    semence = lire_semence(semer(tmp_path / "semences")).unwrap()
    cible = tmp_path / "sortie" / "fiche.md"

    assert new(cible, semence).unwrap() == cible

    item = read_item(cible).unwrap()
    assert list(item.fields) == [ESTAMPILLE, "titre", "session", "notes"]
    assert item.fields[ESTAMPILLE] == "essai"
    assert item.fields["titre"] == PLACEHOLDER
    assert item.fields["session"] == 1
    assert item.fields["notes"] == OPTIONAL
    assert item.sections == {"Objectif": PLACEHOLDER, "Journal": "Rien à ce jour."}


def test_new_n_ecrase_rien(tmp_path: Path) -> None:
    semence = lire_semence(semer(tmp_path / "semences")).unwrap()
    cible = tmp_path / "fiche.md"
    _ = cible.write_text("déjà là\n", encoding="utf-8")

    r = new(cible, semence)

    assert not r
    assert "existe déjà" in r.message
    assert cible.read_text(encoding="utf-8") == "déjà là\n"


def test_une_commande_qui_echoue_n_ecrit_rien(tmp_path: Path) -> None:
    casse = CONTRAT.replace('text = "Rien à ce jour."', 'command = "exit 4"')
    semence = lire_semence(semer(tmp_path / "semences", contrat=casse)).unwrap()
    cible = tmp_path / "fiche.md"

    r = new(cible, semence)

    assert not r
    assert "exit 4" in r.message
    assert not cible.exists()


def test_environnement_gabarit(tmp_path: Path) -> None:
    contrat = CONTRAT.replace(
        'text = "Rien à ce jour."',
        'command = "echo $GABARIT_SEMENCE:$GABARIT_NAME:$GABARIT_FICHIER:${GABARIT_ROOT:-absent}"',
    )
    semence = lire_semence(semer(tmp_path / "semences", contrat=contrat)).unwrap()
    cible = tmp_path / "fiche.md"

    _ = new(cible, semence).unwrap()

    rendu = read_item(cible).unwrap().sections["Journal"]
    assert rendu == f"essai:Journal:{cible}:absent"


# --------------------------------------------------------------------- semence
def test_une_semence_qui_declare_l_estampille_est_refusee(tmp_path: Path) -> None:
    contrat = CONTRAT + '\n[fields.gabarit]\ntype = "text"\ndescription = ""\n'
    r = lire_semence(semer(tmp_path, contrat=contrat))
    assert not r
    assert "réservé" in r.message


def test_trouver_par_nom_dans_les_racines(tmp_path: Path) -> None:
    projet = tmp_path / "projet"
    d = semer(projet / ".claude" / DEFS)
    where = roots(DEFS, cwd=projet, package=tmp_path / "ailleurs")

    semence = trouver_semence("essai", None, where).unwrap()

    assert semence.nom == "essai"
    assert semence.chemin == d


def test_nom_inconnu_nomme_les_semences_connues(tmp_path: Path) -> None:
    projet = tmp_path / "projet"
    _ = semer(projet / ".claude" / DEFS)
    where = roots(DEFS, cwd=projet, package=tmp_path / "ailleurs")

    r = trouver_semence("absente", None, where)

    assert not r
    assert "semence « absente » introuvable" in r.message
    assert "essai" in r.message


def test_nom_et_chemin_sont_exclusifs(tmp_path: Path) -> None:
    d = semer(tmp_path)
    assert trouver_semence("essai", d).status == 2
    assert trouver_semence(None, None).status == 2


# ------------------------------------------------------------------- point d'entrée
def lancer(*argv: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *argv], cwd=cwd, capture_output=True, text=True, check=False
    )


def test_cli_new_par_nom_puis_refus_sur_existant(tmp_path: Path) -> None:
    _ = semer(tmp_path / ".claude" / DEFS)

    r = lancer("new", "essai", "fiche.md", cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "fiche.md"
    assert (tmp_path / "fiche.md").is_file()

    r = lancer("new", "essai", "fiche.md", cwd=tmp_path)
    assert r.returncode == 1
    assert "existe déjà" in r.stderr
    assert r.stdout == ""


def test_cli_new_from(tmp_path: Path) -> None:
    d = semer(tmp_path / "ailleurs")
    r = lancer("new", "--from", str(d), "fiche.md", cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert read_item(tmp_path / "fiche.md").unwrap().fields[ESTAMPILLE] == "essai"


def test_cli_erreurs_d_appel_en_code_2(tmp_path: Path) -> None:
    assert lancer(cwd=tmp_path).returncode == 2
    assert lancer("inconnue", cwd=tmp_path).returncode == 2
    assert lancer("new", "fiche.md", cwd=tmp_path).returncode == 2
    assert lancer("new", "a", "b", "c", cwd=tmp_path).returncode == 2


def test_cli_nom_et_from_dans_n_importe_quel_ordre_disent_la_vraie_faute(tmp_path: Path) -> None:
    d = semer(tmp_path / "ailleurs")
    for argv in (
        ("new", "essai", "--from", str(d), "fiche.md"),
        ("new", "--from", str(d), "essai", "fiche.md"),
        ("new", "essai", "fiche.md", "--from", str(d)),
    ):
        r = lancer(*argv, cwd=tmp_path)
        assert r.returncode == 2, argv
        assert "pas les deux" in r.stderr, argv
        assert not (tmp_path / "fiche.md").exists()
