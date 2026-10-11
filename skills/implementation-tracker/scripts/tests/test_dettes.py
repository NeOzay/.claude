"""`audit range` et `audit dette`, sur le rapport `02` posé dans le Chantier jouet (C4).

Le précédent est l'audit factice `01-38d27af`, dont la Dette actuelle porte R1, R2, R5 et R8 ; le
Suivi jouet écarte R8 en `## Dettes écartées`.
"""

import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

from chantier_jouet import SLUG
from gabarit.types import PLACEHOLDER
from rapport_audit.dettes import Tableau, ajouter, ranger
from rapport_audit.modele import Audit, controler, lire
from rapport_audit.pose import poser

FIXTURES = Path(__file__).resolve().parent / "fixtures" / f"{SLUG}.audit"
CLI = Path(__file__).resolve().parents[1] / "audit-cli.py"
DATE = dt.date(2026, 10, 11)


def _second(depot: Path) -> Path:
    dossier = depot / ".claude" / "implementation" / f"{SLUG}.audit"
    dossier.mkdir(parents=True)
    shutil.copy(FIXTURES / "01-38d27af.toml", dossier)
    return poser(depot, SLUG, "clôture", DATE).unwrap()


def _audit(rapport: Path) -> Audit:
    return lire(rapport, rempli=False).unwrap()


def test_range_vers_actuelle_sans_recopie(chantier: Path) -> None:
    rapport = _second(chantier)
    r = ranger(rapport, "R1", "actuelle", None)
    assert r, r.message
    assert r.unwrap() == "R1 rangée en actuelle"
    audit = _audit(rapport)
    assert audit.dette.actuelle == [audit.dette.precedente[0]]


def test_range_vers_corrigee_avec_sa_preuve(chantier: Path) -> None:
    rapport = _second(chantier)
    assert ranger(rapport, "R2", "corrigee", "pytest -k reprise → 4 passed")
    (d,) = _audit(rapport).dette.corrigee
    assert (d.id, d.corrigee, d.preuve) == ("R2", rapport.stem, "pytest -k reprise → 4 passed")
    assert d.constat == _audit(rapport).dette.precedente[1].constat


def test_range_vers_corrigee_exige_la_preuve(chantier: Path) -> None:
    rapport = _second(chantier)
    avant = rapport.read_text(encoding="utf-8")
    r = ranger(rapport, "R2", "corrigee", None)
    assert not r
    assert "`--preuve` est requis vers corrigee" in r.message
    assert rapport.read_text(encoding="utf-8") == avant


def test_range_vers_ecartee_lit_le_suivi(chantier: Path) -> None:
    rapport = _second(chantier)
    r = ranger(rapport, "R8", "ecartee", None)
    assert r, r.message
    (d,) = _audit(rapport).dette.ecartee
    assert d.ecartee == dt.date(2026, 10, 4)
    assert d.justificatif == (
        "Le terme entre au Lexique global à l'Étape 9, sur accord de l'utilisateur."
    )


def test_range_vers_ecartee_sans_ligne_au_suivi_est_refuse(chantier: Path) -> None:
    rapport = _second(chantier)
    r = ranger(rapport, "R5", "ecartee", None)
    assert not r
    assert "R5 n'est pas en `## Dettes écartées`" in r.message
    assert _audit(rapport).dette.ecartee == []


def test_range_d_une_dette_qui_n_est_pas_precedente(chantier: Path) -> None:
    r = ranger(_second(chantier), "R3", "actuelle", None)
    assert not r
    assert "R3 n'est pas une dette précédente" in r.message


def test_ranger_deux_fois_deplace_la_dette(chantier: Path) -> None:
    rapport = _second(chantier)
    assert ranger(rapport, "R5", "actuelle", None)
    assert ranger(rapport, "R5", "corrigee", "lu : statusline-command.py:84-88")
    dettes = _audit(rapport).dette
    assert dettes.actuelle == []
    assert [d.id for d in dettes.corrigee] == ["R5"]


def test_dette_attribue_le_numero_suivant(chantier: Path) -> None:
    rapport = _second(chantier)
    r = ajouter(rapport, "qualité", "majeur")
    assert r, r.message
    assert r.unwrap() == "R9"
    assert ajouter(rapport, "style", "note").unwrap() == "R10"
    d, _ = _audit(rapport).dette.actuelle
    assert (d.id, d.nature, d.severite, d.trouvee) == ("R9", "qualité", "majeur", rapport.stem)
    assert (d.emplacement, d.constat, d.solution) == (PLACEHOLDER,) * 3


def test_dette_au_premier_audit_garde_le_verdict_en_dernier(chantier: Path) -> None:
    rapport = poser(chantier, SLUG, "intermédiaire", DATE).unwrap()
    assert ajouter(rapport, "alignement", "bloquant").unwrap() == "R1"
    texte = rapport.read_text(encoding="utf-8")
    assert texte.index("[[dette.actuelle]]") < texte.index("[verdict]")


def test_le_rapport_range_suit_son_precedent(chantier: Path) -> None:
    rapport = _second(chantier)
    rangements: list[tuple[str, Tableau, str | None]] = [
        ("R1", "actuelle", None),
        ("R2", "corrigee", "pytest → 4 passed"),
        ("R5", "corrigee", "pytest → 1 passed"),
        ("R8", "ecartee", None),
    ]
    for id_, vers, preuve in rangements:
        assert ranger(rapport, id_, vers, preuve)
    assert ajouter(rapport, "alignement", "majeur")
    r = controler(rapport, rempli=False)
    assert r, r.message


def test_les_commandes_affichent_leur_resultat(chantier: Path) -> None:
    rapport = _second(chantier)

    def audit(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *args], capture_output=True, text=True, check=False
        )

    p = audit("range", str(rapport), "R2", "corrigee", "--preuve", "pytest → 4 passed")
    assert (p.returncode, p.stdout) == (0, "R2 rangée en corrigee\n"), p.stderr
    p = audit("dette", str(rapport), "--nature", "qualité", "--severite", "avertissement")
    assert (p.returncode, p.stdout) == (0, "R9\n"), p.stderr
    p = audit("dette", str(rapport), "--nature", "qualité", "--severite", "inconnue")
    assert p.returncode == 2
