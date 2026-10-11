"""`audit new` : la pose d'un rapport sur un Chantier jouet (C1).

Les audits factices de `fixtures/contexte-tracker.audit/` servent de précédents remplis : le
Chantier jouet porte le même slug.
"""

import datetime as dt
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from chantier_jouet import SLUG
from gabarit.types import PLACEHOLDER
from rapport_audit.modele import Verification, controler, lire
from rapport_audit.pose import poser

FIXTURES = Path(__file__).resolve().parent / "fixtures" / f"{SLUG}.audit"
CLI = Path(__file__).resolve().parents[1] / "audit-cli.py"
DATE = dt.date(2026, 10, 11)


def _head(depot: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=depot, capture_output=True, text=True
    ).stdout.strip()


def _dossier(depot: Path) -> Path:
    return depot / ".claude" / "implementation" / f"{SLUG}.audit"


def _precedents(depot: Path, *noms: str) -> None:
    _dossier(depot).mkdir(parents=True)
    for nom in noms:
        shutil.copy(FIXTURES / nom, _dossier(depot) / nom)


def test_le_premier_audit_se_pose_sans_precedent(chantier: Path) -> None:
    r = poser(chantier, SLUG, "intermédiaire", DATE)
    assert r, r.message
    assert r.unwrap() == _dossier(chantier) / f"01-{_head(chantier)}.toml"
    audit = controler(r.unwrap(), rempli=False).unwrap()
    assert (audit.rang, audit.type, audit.date, audit.precedent) == (1, "intermédiaire", DATE, None)
    assert (audit.base, audit.plan) == ("master", ".claude/plans/jouet.md")
    assert audit.suivi == f".claude/implementation/{SLUG}.md"
    assert audit.dette.precedente == []
    assert audit.verdict.valeur == PLACEHOLDER


def test_la_revue_reprend_le_brief_sans_numero_ni_source(chantier: Path) -> None:
    c = lire(poser(chantier, SLUG, "clôture", DATE).unwrap(), rempli=False).unwrap().conformite
    assert [(x.id, x.critere) for x in c.critere] == [
        ("C1", "La reprise signale une Passation périmée."),
        ("C2", "`contexte --session courante` rend la taille du contexte (`pytest`)."),
    ]
    assert [x.exclusion for x in c.hors_perimetre] == ["La ligne de statut."]
    assert [(x.id, x.signal) for x in c.signal] == [("S1", "Un script lit le rapport en entier.")]
    assert c.symptome is not None
    assert c.symptome.symptome == "« la Passation est jugée périmée » après chaque audit."
    assert {x.etat for x in c.critere} == {PLACEHOLDER}


def test_un_rapport_pose_attend_d_etre_rempli(chantier: Path) -> None:
    r = controler(poser(chantier, SLUG, "clôture", DATE).unwrap(), rempli=True)
    assert not r
    assert "verdict.valeur : à remplir" in r.message
    assert "conformite.critere[C1].etat : à remplir" in r.message


def test_le_deuxieme_reprend_la_dette_actuelle_du_premier(chantier: Path) -> None:
    _precedents(chantier, "01-38d27af.toml")
    r = poser(chantier, SLUG, "clôture", DATE)
    assert r, r.message
    assert r.unwrap().name == f"02-{_head(chantier)}.toml"
    # Le contrôle relit le précédent : la suite tient, Dette précédente comprise.
    audit = controler(r.unwrap(), rempli=False).unwrap()
    premier = lire(_dossier(chantier) / "01-38d27af.toml", rempli=True).unwrap()
    assert audit.precedent == "01-38d27af"
    assert audit.dette.precedente == premier.dette.actuelle
    assert audit.dette.actuelle == []


def test_les_cumuls_passent_d_un_audit_au_suivant(chantier: Path) -> None:
    _precedents(chantier, "01-38d27af.toml", "02-b323e5a.toml")
    r = poser(chantier, SLUG, "clôture", DATE)
    assert r, r.message
    audit = controler(r.unwrap(), rempli=False).unwrap()
    second = lire(_dossier(chantier) / "02-b323e5a.toml", rempli=True).unwrap()
    assert (audit.rang, audit.precedent) == (3, "02-b323e5a")
    assert audit.dette.precedente == second.dette.actuelle
    assert audit.dette.corrigee == second.dette.corrigee
    assert audit.dette.ecartee == second.dette.ecartee


def test_les_textes_multilignes_restent_en_bloc(chantier: Path) -> None:
    _precedents(chantier, "01-38d27af.toml")
    texte = poser(chantier, SLUG, "clôture", DATE).unwrap().read_text(encoding="utf-8")
    assert 'constat = """« Rendre la main' in texte
    assert tomllib.loads(texte)["dette"]["precedente"][0]["id"] == "R1"


def test_un_precedent_non_rempli_est_refuse(chantier: Path) -> None:
    premier = poser(chantier, SLUG, "intermédiaire", DATE).unwrap()
    r = poser(chantier, SLUG, "clôture", DATE)
    assert not r
    assert "le précédent n'est pas un rapport rempli" in r.message
    assert sorted(p.name for p in _dossier(chantier).iterdir()) == [premier.name]


def test_hors_de_la_branche_du_chantier_rien_n_est_pose(chantier: Path) -> None:
    subprocess.run(["git", "checkout", "-q", "-b", "autre"], cwd=chantier, check=True)
    r = poser(chantier, SLUG, "clôture", DATE)
    assert not r
    assert f"s'audite sur {SLUG}" in r.message
    assert not _dossier(chantier).exists()


def test_sans_brief_la_revue_est_vide(chantier: Path) -> None:
    suivi = chantier / ".claude" / "implementation" / f"{SLUG}.md"
    suivi.write_text(
        "\n".join(
            ligne
            for ligne in suivi.read_text(encoding="utf-8").splitlines()
            if not ligne.startswith("brief = ")
        ),
        encoding="utf-8",
    )
    audit = lire(poser(chantier, SLUG, "clôture", DATE).unwrap(), rempli=False).unwrap()
    assert audit.brief is None
    assert audit.conformite.est_vide()


def test_un_critere_sans_numero_est_nomme(chantier: Path) -> None:
    brief = chantier / ".claude" / "implementation" / f"{SLUG}.brief.md"
    brief.write_text(
        brief.read_text(encoding="utf-8").replace("- **C1** — La", "- La"), encoding="utf-8"
    )
    r = poser(chantier, SLUG, "clôture", DATE)
    assert not r
    assert "Critères de réussite : puce sans numéro" in r.message


def test_new_affiche_le_chemin_du_rapport(chantier: Path) -> None:
    p = subprocess.run(
        [sys.executable, str(CLI), "new", SLUG, "--intermediaire"],
        cwd=chantier,
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    assert p.stdout == f"{_dossier(chantier) / f'01-{_head(chantier)}.toml'}\n"


# --- Les vérifications des Étapes (C2) -------------------------------------------------------


def _etape(depot: Path, verif: str) -> None:
    """Remplace la vérification de l'Étape 1, cochée, du Suivi jouet."""
    suivi = depot / ".claude" / "implementation" / f"{SLUG}.md"
    texte = suivi.read_text(encoding="utf-8")
    assert "vérif: `test -f a.txt`" in texte
    suivi.write_text(texte.replace("vérif: `test -f a.txt`", f"vérif: {verif}"), encoding="utf-8")


def _verifications(depot: Path) -> list[Verification]:
    return lire(poser(depot, SLUG, "clôture", DATE).unwrap(), rempli=False).unwrap().verification


def test_verification_des_seules_etapes_cochees(chantier: Path) -> None:
    (v,) = _verifications(chantier)
    assert (v.origine, v.commande, v.statut, v.dette) == (
        "Étape 1",
        "test -f a.txt",
        "passée",
        None,
    )
    assert v.sortie == "aucune sortie"


def test_verification_lancee_depuis_la_racine(chantier: Path) -> None:
    _etape(chantier, "`pwd`")
    (v,) = _verifications(chantier)
    assert v.sortie == str(chantier)


def test_verification_echouee_attend_sa_dette(chantier: Path) -> None:
    _etape(chantier, "`echo raté >&2; exit 3`")
    rapport = poser(chantier, SLUG, "clôture", DATE).unwrap()
    (v,) = lire(rapport, rempli=False).unwrap().verification
    assert (v.statut, v.sortie, v.dette) == ("échouée", "code de sortie 3\nraté", PLACEHOLDER)
    r = lire(rapport, rempli=True)
    assert not r
    assert "verification[Étape 1].dette : à remplir" in r.message


def test_verification_introuvable_non_executee(chantier: Path) -> None:
    _etape(chantier, "`commande-qui-n-existe-pas`")
    (v,) = _verifications(chantier)
    assert (v.statut, v.dette) == ("non-exécutée", None)
    assert "commande-qui-n-existe-pas" in v.sortie


def test_verification_en_prose_non_executee(chantier: Path) -> None:
    _etape(chantier, "la liste des agents donne `Edit` à l'auditeur")
    (v,) = _verifications(chantier)
    assert v.statut == "non-exécutée"
    assert v.commande == "la liste des agents donne `Edit` à l'auditeur"


def test_verification_sortie_bornee_et_nettoyee(chantier: Path) -> None:
    _etape(chantier, r"`for i in $(seq 1 50); do printf '\033[32m%s\033[0m\n' $i; done`")
    (v,) = _verifications(chantier)
    assert v.sortie.splitlines() == [str(i) for i in range(31, 51)]


def test_verification_d_une_etape_enroulee(chantier: Path) -> None:
    _etape(chantier, "\n      `test -f a.txt`")
    (v,) = _verifications(chantier)
    assert (v.origine, v.commande, v.statut) == ("Étape 1", "test -f a.txt", "passée")
