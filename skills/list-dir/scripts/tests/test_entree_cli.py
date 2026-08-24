"""list-dir.py — ce que le point d'entrée seul porte.

CE FICHIER N'EST PAS UN DOUBLON DES AUTRES. Tout le reste de la suite passe par la
bibliothèque, où un échec est un `Result` inspectable. Ici on exerce ce qu'aucun
appel de fonction ne peut montrer : LE CODE DE SORTIE, le canal sur lequel le
message part, et ce que la ligne de commande imprime sur stdout — c'est-à-dire tout
ce sur quoi un script appelant s'appuie.

  2  erreur d'appel : aucune commande, commande inconnue, argument invalide
  1  refus ou échec
  0  succès, et la valeur seule sur stdout

`list-dir.py` porte un tiret : il n'est pas importable, et le sous-processus est la
seule voie. C'est aussi ce qui rend ces tests fidèles — ils lancent exactement ce
que l'utilisateur tape.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

from jouet import ELEMENT, ecrire, monter_liste

CLI = Path(__file__).resolve().parent.parent / "list-dir.py"


class Sortie:
    """Le triplet d'un appel : code, stdout, stderr."""

    def __init__(self, proc: subprocess.CompletedProcess[str]) -> None:
        self.code: int = proc.returncode
        self.out: str = proc.stdout
        self.err: str = proc.stderr


def lancer(*argv: str, env: dict[str, str] | None = None, cwd: Path | None = None) -> Sortie:
    return Sortie(
        subprocess.run(
            [sys.executable, str(CLI), *argv],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            env=env,
            cwd=cwd,
        )
    )


def liste_sur_disque(racine: Path, avec_element: bool = True) -> Path:
    chemin = monter_liste(racine / "jouet")
    if avec_element:
        _ = ecrire(chemin, "premier.md", ELEMENT)
    return chemin


# ---------------------------------------------------- erreurs d'appel : code 2
def test_aucune_commande() -> None:
    r = lancer()

    assert r.code == 2
    assert "usage:" in r.err
    assert "« help » les liste" in r.err
    assert r.out == ""


def test_commande_inconnue_enumere_les_connues() -> None:
    r = lancer("inexistante")

    assert r.code == 2
    assert "« inexistante » inconnue" in r.err
    assert "merge" in r.err and "validate" in r.err
    assert r.out == ""


def test_argument_manquant() -> None:
    """argparse rend 2 de lui-même : le code d'erreur d'appel est le même partout."""
    r = lancer("validate")
    assert r.code == 2


# ------------------------------------------------------------- succès : code 0
def test_succes_imprime_la_valeur_sur_stdout(tmp_path: Path) -> None:
    liste = liste_sur_disque(tmp_path)
    r = lancer("validate", str(liste))

    assert r.code == 0
    assert "1 élément(s) conformes au contrat" in r.out
    assert r.err == ""


def test_show_rend_le_fichier(tmp_path: Path) -> None:
    liste = liste_sur_disque(tmp_path)
    r = lancer("show", str(liste), "premier")

    assert r.code == 0
    assert r.out == (liste / "premier.md").read_text(encoding="utf-8")


def test_list_sans_element_rend_zero_et_rien(tmp_path: Path) -> None:
    """Un filtre qui ne rend rien est une réponse, pas une erreur — contrairement à
    merge, qui perdrait un élément."""
    liste = liste_sur_disque(tmp_path, avec_element=False)
    r = lancer("list", str(liste))

    assert r.code == 0
    assert r.out.strip() == ""


def test_init_puis_new_puis_validate(tmp_path: Path) -> None:
    """Le parcours minimal d'un utilisateur, de bout en bout."""
    neuve = tmp_path / "neuve"

    assert lancer("init", str(neuve)).code == 0
    assert lancer("new", str(neuve), "entree").code == 0

    fait = lancer("validate", str(neuve))
    assert fait.code == 0
    assert "1 élément(s) conformes" in fait.out

    pas_rempli = lancer("validate", str(neuve), "--filled")
    assert pas_rempli.code == 1


# --------------------------------------------------------------- échecs : code 1
def test_echec_part_sur_stderr_et_stdout_reste_vide(tmp_path: Path) -> None:
    """CE QUI COMPTE POUR UN SCRIPT APPELANT : stdout ne porte que le résultat."""
    r = lancer("validate", str(tmp_path / "absente"))

    assert r.code == 1
    assert "répertoire introuvable" in r.err
    assert r.out == ""


def test_manquement_de_validation(tmp_path: Path) -> None:
    liste = liste_sur_disque(tmp_path, avec_element=False)
    _ = ecrire(liste, "a.md", '+++\nid = "a"\n+++\n\n## Constat\n\nx\n')

    r = lancer("validate", str(liste))

    assert r.code == 1
    assert "champ « title » — manquant" in r.err
    assert r.out == ""


def test_merge_sur_liste_vide(tmp_path: Path) -> None:
    liste = liste_sur_disque(tmp_path, avec_element=False)
    r = lancer("merge", str(liste))

    assert r.code == 1
    assert "agglomérer zéro n'est pas un résultat" in r.err


# ------------------------------------------------------ surcharge interdite : 1
def test_surcharge_protegee_refusee(tmp_path: Path) -> None:
    """Elle n'est jamais ignorée en silence : c'est une erreur, et elle bloque
    l'appel — y compris celui d'une tout autre commande."""
    liste = liste_sur_disque(tmp_path)
    _ = ecrire(liste, ".list/commands/validate.py", "DESCRIPTION = 'la mienne'\n")

    r = lancer("list", str(liste))

    assert r.code == 1
    assert "ne se surcharge pas" in r.err


def test_module_casse_est_signale(tmp_path: Path) -> None:
    liste = liste_sur_disque(tmp_path)
    _ = ecrire(liste, ".list/commands/cassee.py", "def command(:\n")

    r = lancer("cassee", str(liste))

    assert r.code == 1
    assert "illisible" in r.err


# ------------------------------------------------------------------------ help
def test_help_seul_ne_montre_que_les_generiques() -> None:
    r = lancer("help")

    assert r.code == 0
    assert "Commandes génériques (10)" in r.out
    assert "Passer un répertoire-liste en argument" in r.out


def test_help_annonce_les_dependances() -> None:
    assert "[exige git]" in lancer("help").out


def test_help_avec_une_liste_montre_ses_commandes(tmp_path: Path) -> None:
    liste = liste_sur_disque(tmp_path)
    _ = ecrire(
        liste,
        ".list/commands/solder.py",
        'DESCRIPTION = "solde une entrée"\n\ndef command(args, utils):\n'
        "    return utils.ok(None)\n",
    )

    r = lancer("help", str(liste))

    assert r.code == 0
    assert "solder" in r.out
    assert "solde une entrée" in r.out


def test_help_signale_une_surcharge(tmp_path: Path) -> None:
    """Une surcharge invisible est un piège : c'est ce que la mention existe pour
    empêcher."""
    liste = liste_sur_disque(tmp_path)
    _ = ecrire(
        liste,
        ".list/commands/list.py",
        'DESCRIPTION = "la mienne"\n\ndef command(args, utils):\n    return utils.ok(None)\n',
    )

    assert "(surchargée)" in lancer("help", str(liste)).out


def test_help_sur_un_repertoire_qui_n_est_pas_une_liste(tmp_path: Path) -> None:
    r = lancer("help", str(tmp_path))

    assert r.code == 1
    assert "n'est pas un répertoire-liste" in r.err


# ------------------------------------------------------ dépendance déclarée absente
def test_git_absent_du_path_sort_non_nul_en_le_nommant(tmp_path: Path) -> None:
    """LE PRÉCÉDENT DU DÉPÔT : un hook gardait sur un outil absent et sortait 0 sans
    un mot, si bien que le garde n'a jamais gardé. Ici, l'outil est nommé."""
    liste = liste_sur_disque(tmp_path)
    vide = tmp_path / "path-vide"
    vide.mkdir()

    r = lancer("move", str(liste), "premier", str(liste), env={"PATH": str(vide)})

    assert r.code != 0
    assert "git" in r.err
    assert "REQUIRES" in r.err


# ------------------------------------------------------------- garde de version
def test_la_garde_de_version_precede_tout_import_de_listdir() -> None:
    """ELLE NE PEUT PAS ÊTRE TESTÉE EN LANÇANT UN VIEUX PYTHON — il n'y en a pas ici.
    Ce qui se vérifie, et qui est tout l'enjeu, c'est SON RANG : le paquet utilise la
    syntaxe de généricité de PEP 695, et un import placé avant la garde lèverait un
    SyntaxError illisible au lieu de dire ce qui manque."""
    arbre = ast.parse(CLI.read_text(encoding="utf-8"))

    rang_garde = next(
        i
        for i, node in enumerate(arbre.body)
        if isinstance(node, ast.If) and "version_info" in ast.dump(node.test)
    )
    rang_import = next(
        i
        for i, node in enumerate(arbre.body)
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("listdir")
    )

    assert rang_garde < rang_import
