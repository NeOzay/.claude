"""prefill.py — le calcul faillible de la valeur initiale d'un champ ou d'une section.

CE QUE CE FICHIER PROUVE : `text` pose sa valeur littérale sans rien exécuter,
`command` pose la sortie strippée de `bash -c`, et l'absence des deux rend le
marqueur — exactement comme avant ce chantier. Un échec de commande (code retour non
nul, binaire absent, sortie refusée par `check_value`) rend un `Result` en échec
nommant le sujet et la commande, RIEN N'EST AVALÉ. Le dernier bloc prouve
l'environnement `LISTDIR_*` : présence et valeur de chacune, et l'absence de
`LISTDIR_ROOT` hors dépôt.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from listdir.prefill import context, initial_field, initial_section, preview
from listdir.types import OPTIONAL, PLACEHOLDER, Field, Section


def champ(
    type: str = "text",
    *,
    required: bool = False,
    text: str | None = None,
    command: str | None = None,
    values: list[str] | None = None,
) -> Field:
    return Field(
        name="date" if type == "date" else "titre",
        type=type,  # pyright: ignore[reportArgumentType]
        required=required,
        text=text,
        command=command,
        values=values or [],
    )


def section(
    *, required: bool = False, text: str | None = None, command: str | None = None
) -> Section:
    return Section(name="Origine", required=required, text=text, command=command)


# ------------------------------------------------------------------------ text
def test_champ_text_pose_la_valeur_litterale(liste_vide: Path) -> None:
    ctx = context(liste_vide, _contrat_vide())
    r = initial_field(champ(text="un titre"), "premier", ctx)
    assert r.unwrap() == "un titre"


def test_section_text_pose_la_valeur_litterale(liste_vide: Path) -> None:
    ctx = context(liste_vide, _contrat_vide())
    r = initial_section(section(text="Créé automatiquement."), "premier", ctx)
    assert r.unwrap() == "Créé automatiquement."


# --------------------------------------------------------------------- command
def test_champ_command_pose_la_sortie_strippee(liste_vide: Path) -> None:
    ctx = context(liste_vide, _contrat_vide())
    r = initial_field(champ(type="date", command="echo '  2026-01-01  '"), "premier", ctx)
    assert r.unwrap() == "2026-01-01"


def test_section_command_pose_la_sortie_strippee(liste_vide: Path) -> None:
    ctx = context(liste_vide, _contrat_vide())
    r = initial_section(section(command="printf '  x  '"), "premier", ctx)
    assert r.unwrap() == "x"


def test_champ_command_qui_echoue_nomme_la_commande(liste_vide: Path) -> None:
    ctx = context(liste_vide, _contrat_vide())
    r = initial_field(champ(command="false"), "premier", ctx)
    assert not r
    assert "titre" in r.message
    assert "false" in r.message


def test_section_command_qui_echoue_nomme_la_commande(liste_vide: Path) -> None:
    ctx = context(liste_vide, _contrat_vide())
    r = initial_section(section(command="exit 3"), "premier", ctx)
    assert not r
    assert "Origine" in r.message
    assert "exit 3" in r.message


def test_champ_command_binaire_absent(liste_vide: Path) -> None:
    ctx = context(liste_vide, _contrat_vide())
    r = initial_field(champ(command="/inexistant/binaire"), "premier", ctx)
    assert not r


def test_champ_command_dont_la_sortie_est_refusee_par_check_value(liste_vide: Path) -> None:
    ctx = context(liste_vide, _contrat_vide())
    r = initial_field(champ(type="date", command="echo pas-une-date"), "premier", ctx)
    assert not r
    assert "date" in r.message
    assert "echo pas-une-date" in r.message


def test_champ_text_refuse_par_check_value(liste_vide: Path) -> None:
    ctx = context(liste_vide, _contrat_vide())
    r = initial_field(champ(type="date", text="pas-une-date"), "premier", ctx)
    assert not r
    assert "« text »" in r.message


# ---------------------------------------------------------------------- marqueur
def test_champ_sans_text_ni_command_pose_son_marqueur(liste_vide: Path) -> None:
    ctx = context(liste_vide, _contrat_vide())
    assert initial_field(champ(required=True), "premier", ctx).unwrap() == PLACEHOLDER
    assert initial_field(champ(required=False), "premier", ctx).unwrap() == OPTIONAL


def test_section_sans_text_ni_command_pose_son_marqueur(liste_vide: Path) -> None:
    ctx = context(liste_vide, _contrat_vide())
    assert initial_section(section(required=True), "premier", ctx).unwrap() == PLACEHOLDER
    assert initial_section(section(required=False), "premier", ctx).unwrap() == OPTIONAL


# -------------------------------------------------------------------- environnement
def test_environnement_expose_les_listdir(liste_vide: Path) -> None:
    ctx = context(liste_vide, _contrat_vide())
    cmd = "echo $LISTDIR_ID:$LISTDIR_NAME:$LISTDIR_LIST:$LISTDIR_CONTRACT"
    r = initial_field(champ(type="text", command=cmd), "premier", ctx)
    id_, name, list_dir, contract_name = r.unwrap().split(":")
    assert id_ == "premier"
    assert name == "titre"
    assert list_dir == str(liste_vide)
    assert contract_name == "jouet"


def test_listdir_root_absente_hors_depot(liste_vide: Path) -> None:
    ctx = context(liste_vide, _contrat_vide())
    assert ctx.root is None
    r = initial_field(champ(type="text", command="echo ${LISTDIR_ROOT:-absent}"), "premier", ctx)
    assert r.unwrap() == "absent"


def _git(depot: Path, *argv: str) -> None:
    _ = subprocess.run(["git", *argv], cwd=depot, capture_output=True, text=True, check=True)


@pytest.fixture
def depot(tmp_path: Path) -> Path:
    """Un dépôt jetable dont la liste-jouet vit à la racine."""
    _git(tmp_path, "init", "-q", "-b", "principale")
    _git(tmp_path, "config", "user.name", "Jouet")
    _git(tmp_path, "config", "user.email", "jouet@example.invalid")
    _git(tmp_path, "config", "commit.gpgsign", "false")
    from jouet import CONTRAT, monter_liste

    monter_liste(tmp_path, CONTRAT)
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "amorçage")
    return tmp_path


def test_listdir_root_presente_dans_un_depot(depot: Path) -> None:
    ctx = context(depot, _contrat_vide())
    assert ctx.root == depot.resolve()
    r = initial_field(champ(type="text", command="echo $LISTDIR_ROOT"), "premier", ctx)
    assert r.unwrap() == str(depot.resolve())


def _contrat_vide():
    from listdir.types import Contract

    return Contract(name="jouet")


# ------------------------------------------------------------------------ preview
def test_preview_nomme_la_commande_sans_la_jouer(tmp_path: Path) -> None:
    """Ce que `migrate --dry-run` affiche : la commande, pas son résultat."""
    temoin = tmp_path / "TEMOIN"
    rendu = preview(champ(type="text", command=f"touch {temoin} && echo v"))

    assert not temoin.exists()
    assert rendu == f"sortie de « touch {temoin} && echo v »"


def test_preview_refuse_une_declaration_sans_command() -> None:
    """LA BRANCHE EST EXERCÉE, PAS SEULEMENT ÉCRITE. `text` et le marqueur passent
    par `initial_field` même en dry-run : les faire passer ici sauterait leur
    contrôle de type, et la garde le dit plutôt que de rendre un libellé faux."""
    with pytest.raises(ValueError, match="portant `command`"):
        _ = preview(champ(type="text", text="littéral"))
