"""`deprecated` côté liste : ni posé, ni ajouté par `migrate`, ni réclamé par `validate`.

CE QUE CE FICHIER PROUVE : `create` et `derive` ne posent pas un champ ou une section
dépréciés ; `migrate` ne les ajoute jamais, les garde là où ils sont, et `drop` ne les
retire pas — ils sont déclarés ; `validate` ne s'en plaint pas, qu'un élément les porte ou non.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from jouet import CONTRAT, PATRON_MD, PATRON_TOML, ecrire, element, monter_liste, monter_patron
from listdir import open_list
from listdir.store import ListStore
from listdir.types import Change

CONTRAT_DEPRECIE = CONTRAT.replace(
    '[fields.tags]\ntype = "list"\ndescription = ""\n',
    '[fields.tags]\ntype = "list"\ndescription = ""\ndeprecated = "utiliser « category »"\n',
).replace(
    '[sections."Assumé"]\nrequired = false\ndescription = ""\n',
    '[sections."Assumé"]\ndescription = ""\ndeprecated = "ne plus écrire"\n',
)

PATRON_DEPRECIE = PATRON_TOML.replace(
    '[fields.verdict]\ntype = "text"\nrequired = true\ndescription = ""\n',
    '[fields.verdict]\ntype = "text"\ndescription = ""\ndeprecated = "dans « Avis »"\n',
).replace(
    '[sections."Remarque"]\nrequired = false\ndescription = ""\n',
    '[sections."Remarque"]\ndescription = ""\ndeprecated = "ne plus écrire"\n',
)


CLI = Path(__file__).resolve().parent.parent / "list-dir.py"


def lancer(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *argv],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def ouvrir(chemin: Path) -> ListStore:
    return open_list(chemin).unwrap()


def actes(changes: list[Change]) -> list[str]:
    return [f"{c.path.name}: {c.subject} — {c.action}" for c in changes]


def liste_depreciee(tmp_path: Path) -> Path:
    return monter_liste(tmp_path / "jouet", CONTRAT_DEPRECIE)


def test_le_contrat_d_essai_depreci_bien_ce_qu_il_dit() -> None:
    assert "deprecated" in CONTRAT_DEPRECIE
    assert CONTRAT_DEPRECIE.count("deprecated") == 2
    assert PATRON_DEPRECIE.count("deprecated") == 2


def test_create_ne_pose_ni_champ_ni_section_deprecies(tmp_path: Path) -> None:
    item = ouvrir(liste_depreciee(tmp_path)).create("neuf").unwrap()

    assert "tags" not in item.fields
    assert list(item.sections) == ["Constat"]


def test_migrate_n_ajoute_jamais_ce_qui_est_deprecie(tmp_path: Path) -> None:
    liste = liste_depreciee(tmp_path)
    _ = element(liste, "a", 'id = "a"\ntitle = "T"\n', "## Constat\n\nx\n")

    changes = ouvrir(liste).migrate().unwrap()

    assert not any("tags" in a or "Assumé" in a for a in actes(changes))
    lu = ouvrir(liste).get("a").unwrap()
    assert "tags" not in lu.fields
    assert "Assumé" not in lu.sections


def test_migrate_garde_ce_qui_est_deprecie_et_porte(tmp_path: Path) -> None:
    liste = liste_depreciee(tmp_path)
    _ = element(
        liste,
        "a",
        'id = "a"\ntitle = "T"\ndate = 2020-01-01\ncategory = "rouge"\ntags = ["x"]\n',
        "## Constat\n\nx\n\n## Assumé\n\nreste\n",
    )
    avant = (liste / "a.md").read_text(encoding="utf-8")

    for drop in (False, True):
        changes = ouvrir(liste).migrate(drop=drop).unwrap()
        assert not any("retir" in a or "conserv" in a for a in actes(changes))

    assert (liste / "a.md").read_text(encoding="utf-8") == avant


def test_validate_se_tait_sur_l_absence_et_sur_la_presence(tmp_path: Path) -> None:
    liste = liste_depreciee(tmp_path)
    _ = element(liste, "sans", 'id = "sans"\ntitle = "T"\n', "## Constat\n\nx\n")
    _ = element(
        liste,
        "avec",
        'id = "avec"\ntitle = "T"\ntags = ["x"]\n',
        "## Constat\n\nx\n\n## Assumé\n\nreste\n",
    )

    assert ouvrir(liste).validate().unwrap() == []
    assert ouvrir(liste).validate(filled=True).unwrap() == []


def test_derive_ne_pose_ni_champ_ni_section_deprecies(liste: Path, tmp_path: Path) -> None:
    derivee = (
        ouvrir(monter_patron(liste, contrat=PATRON_DEPRECIE, corps=PATRON_MD))
        .derive(tmp_path / "revues", "revue")
        .unwrap()
    )

    fiche = derivee.get("premier").unwrap()
    assert "verdict" not in fiche.fields
    assert "Remarque" not in fiche.sections
    assert "Avis" in fiche.sections


def test_une_liste_sans_deprecated_est_inchangee(tmp_path: Path) -> None:
    liste = monter_liste(tmp_path / "jouet")
    _ = ecrire(liste, "a.md", '+++\nid = "a"\ntitle = "T"\n+++\n\n## Constat\n\nx\n')

    item = ouvrir(liste).create("neuf").unwrap()

    assert "tags" in item.fields
    assert "Assumé" in item.sections


# ----------------------------------------------------------------- avertissement
def test_validate_avertit_sur_stderr_sans_changer_le_code(tmp_path: Path) -> None:
    liste = liste_depreciee(tmp_path)
    _ = element(
        liste,
        "avec",
        'id = "avec"\ntitle = "T"\ndate = 2020-01-01\ncategory = "rouge"\ntags = ["x"]\n',
        "## Constat\n\nx\n\n## Assumé\n\nreste\n",
    )
    _ = element(
        liste,
        "sans",
        'id = "sans"\ntitle = "T"\ndate = 2020-01-01\ncategory = "rouge"\n',
        "## Constat\n\nx\n",
    )

    r = lancer("validate", str(liste))

    assert r.returncode == 0
    assert "avec.md: champ « tags » — déprécié : utiliser « category »" in r.stderr
    assert "avec.md: section « Assumé » — dépréciée : ne plus écrire" in r.stderr
    assert "sans.md" not in r.stderr  # une absence ne dit rien : une note par élément qui le porte
    assert "déprécié" not in r.stdout
