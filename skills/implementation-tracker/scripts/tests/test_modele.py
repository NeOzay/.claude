"""Le modèle du rapport d'audit et `audit check`.

Les deux audits factices de `fixtures/contexte-tracker.audit/` passent ; chaque faute est dérivée
de l'un d'eux par un remplacement de texte, posée à côté d'une copie du `01` pour que le second
trouve son précédent.
"""

import subprocess
import sys
from pathlib import Path

import pytest
from gabarit.types import PLACEHOLDER
from rapport_audit.modele import controler, lire, verdicts_admis

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "contexte-tracker.audit"
PREMIER = FIXTURES / "01-38d27af.toml"
SECOND = FIXTURES / "02-b323e5a.toml"
CLI = Path(__file__).resolve().parents[1] / "audit-cli.py"


def _derive(dossier: Path, source: Path, *remplacements: tuple[str, str]) -> Path:
    """Une copie de `source` dans `dossier`, chaque remplacement appliqué ; le `01` à côté."""
    texte = source.read_text(encoding="utf-8")
    for avant, apres in remplacements:
        assert avant in texte, f"remplacement sans prise : {avant!r}"
        texte = texte.replace(avant, apres)
    (dossier / PREMIER.name).write_text(PREMIER.read_text(encoding="utf-8"), encoding="utf-8")
    cible = dossier / source.name
    cible.write_text(texte, encoding="utf-8")
    return cible


@pytest.mark.parametrize("fichier", [PREMIER, SECOND])
def test_les_audits_factices_passent_remplis(fichier: Path) -> None:
    r = controler(fichier, rempli=True)
    assert r, r.message


def test_les_verdicts_admis_suivent_la_dette_actuelle() -> None:
    assert verdicts_admis(controler(PREMIER, True).unwrap().dette.actuelle) == {"DÉFAVORABLE"}
    assert verdicts_admis(controler(SECOND, True).unwrap().dette.actuelle) == {"RÉSERVES"}


# --- Les fautes de l'annexe (C3) -------------------------------------------------------------

R8_ECARTEE = """[[dette.ecartee]]
id = "R8"
nature = "style"
emplacement = "LEXIQUE.md"
constat = "« Passation » porte une majuscule sans être un terme défini."
trouvee = "01-38d27af"
solution = "Proposer « Passation » au Lexique global."
severite = "avertissement"
ecartee = 2026-10-04
justificatif = "Le terme entre au Lexique global à l'Étape 9, sur accord de l'utilisateur."
"""

# La fin de la solution de R12, qui précède sa sévérité : la seule prise sur elle seule.
ECARTER_R12 = "puis l'écrire en `## Dettes écartées`.\"\n"

FAUTES: dict[str, tuple[tuple[tuple[str, str], ...], str]] = {
    "dette précédente non rangée": (
        ((R8_ECARTEE, ""),),
        "dettes précédentes non réévaluées : R8",
    ),
    "renvoi vers une dette absente": (
        (('dette = "R12"', 'dette = "R13"'),),
        "R13 renvoyée mais ni actuelle ni écartée",
    ),
    "R<n> déjà servi": (
        (('dette = "R12"', 'dette = "R3"'), ('id = "R12"', 'id = "R3"')),
        "R3 neuve, mais un numéro déjà servi dans le Chantier",
    ),
    "verdict non admis": (
        (('valeur = "RÉSERVES"', 'valeur = "FAVORABLE"'),),
        "verdict FAVORABLE : la Dette actuelle n'admet que RÉSERVES",
    ),
    "cote d'office non respectée": (
        ((ECARTER_R12 + 'severite = "majeur"', ECARTER_R12 + 'severite = "avertissement"'),),
        "R12 cotée `avertissement`, attendu `majeur` d'office",
    ),
}


@pytest.mark.parametrize("faute", sorted(FAUTES))
def test_chaque_faute_de_l_annexe_est_refusee(tmp_path: Path, faute: str) -> None:
    remplacements, attendu = FAUTES[faute]
    r = controler(_derive(tmp_path, SECOND, *remplacements), rempli=True)
    assert not r
    assert attendu in r.message


def test_une_dette_precedente_reste_a_ranger_sans_filled(tmp_path: Path) -> None:
    remplacements, _ = FAUTES["dette précédente non rangée"]
    assert lire(_derive(tmp_path, SECOND, *remplacements), rempli=False)


def test_une_faute_se_situe_dans_le_rapport(tmp_path: Path) -> None:
    r = lire(_derive(tmp_path, SECOND, ('etat = "disparu"', 'etat = "envolé"')), rempli=False)
    assert not r
    assert r.message.startswith("02-b323e5a.toml : conformite.symptome.etat : ")


def test_une_valeur_n_est_pas_convertie(tmp_path: Path) -> None:
    r = lire(_derive(tmp_path, PREMIER, ("rang = 1", 'rang = "1"')), rempli=False)
    assert not r
    assert "rang" in r.message


def test_le_fichier_porte_le_nom_de_son_audit(tmp_path: Path) -> None:
    cible = tmp_path / "03-38d27af.toml"
    cible.write_text(PREMIER.read_text(encoding="utf-8"), encoding="utf-8")
    r = controler(cible, rempli=True)
    assert not r
    assert "se nomme 01-38d27af.toml" in r.message


def test_un_precedent_absent_est_nomme(tmp_path: Path) -> None:
    cible = tmp_path / SECOND.name
    cible.write_text(SECOND.read_text(encoding="utf-8"), encoding="utf-8")
    r = controler(cible, rempli=True)
    assert not r
    assert "précédent 01-38d27af" in r.message


# --- Le Marqueur -----------------------------------------------------------------------------

POSE = (
    ('etat = "persiste"', f'etat = "{PLACEHOLDER}"'),
    ('severite = "avertissement"', f'severite = "{PLACEHOLDER}"'),
    ('valeur = "DÉFAVORABLE"', f'valeur = "{PLACEHOLDER}"'),
)


def test_un_rapport_au_marqueur_passe_sans_filled(tmp_path: Path) -> None:
    r = controler(_derive(tmp_path, PREMIER, *POSE), rempli=False)
    assert r, r.message
    # R2 reste `bloquant` : le verdict est connu, quelle que soit la sévérité au Marqueur.
    assert verdicts_admis(r.unwrap().dette.actuelle) == {"DÉFAVORABLE"}


def test_une_severite_au_marqueur_suspend_les_verdicts_admis(tmp_path: Path) -> None:
    r = controler(
        _derive(
            tmp_path,
            SECOND,
            (ECARTER_R12 + 'severite = "majeur"', ECARTER_R12 + f'severite = "{PLACEHOLDER}"'),
        ),
        False,
    )
    assert r, r.message
    assert verdicts_admis(r.unwrap().dette.actuelle) is None


def test_filled_nomme_chaque_marqueur(tmp_path: Path) -> None:
    r = controler(_derive(tmp_path, PREMIER, *POSE), rempli=True)
    assert not r
    lignes = set(r.message.splitlines())
    assert {
        "01-38d27af.toml : conformite.symptome.etat : à remplir",
        "01-38d27af.toml : dette.actuelle[R5].severite : à remplir",
        "01-38d27af.toml : dette.actuelle[R8].severite : à remplir",
        "01-38d27af.toml : verdict.valeur : à remplir",
    } <= lignes


def test_l_en_tete_n_est_jamais_au_marqueur(tmp_path: Path) -> None:
    r = lire(_derive(tmp_path, PREMIER, ('base = "master"', f'base = "{PLACEHOLDER}"')), False)
    assert not r
    assert "base" in r.message


def test_seul_le_marqueur_requis_se_pose(tmp_path: Path) -> None:
    r = lire(
        _derive(tmp_path, PREMIER, ('valeur = "DÉFAVORABLE"', 'valeur = "<OPTIONNEL>"')), False
    )
    assert not r
    assert "verdict.valeur" in r.message


def test_une_verification_echouee_au_marqueur_attend_sa_dette(tmp_path: Path) -> None:
    pose = _derive(
        tmp_path,
        PREMIER,
        (
            'sortie = "1 failed : test_passation_perimee_apres_audit"\ndette = "R2"',
            f'sortie = "1 failed"\ndette = "{PLACEHOLDER}"',
        ),
    )
    assert lire(pose, rempli=False)
    r = lire(pose, rempli=True)
    assert not r
    assert "verification[C3].dette : à remplir" in r.message


# --- La commande -----------------------------------------------------------------------------


def _audit(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args], capture_output=True, text=True, check=False
    )


def test_check_affiche_les_verdicts_admis() -> None:
    p = _audit("check", "--filled", str(SECOND))
    assert p.returncode == 0, p.stderr
    assert p.stdout == "verdicts admis : RÉSERVES\n"


def test_check_sort_en_1_une_faute_par_ligne(tmp_path: Path) -> None:
    remplacements, attendu = FAUTES["verdict non admis"]
    p = _audit("check", str(_derive(tmp_path, SECOND, *remplacements)))
    assert p.returncode == 1
    assert p.stdout == ""
    assert attendu in p.stderr
