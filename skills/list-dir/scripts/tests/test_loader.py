"""loader.py et utils.py — découverte des commandes, surcharges, dépendances.

CE QUE CE FICHIER CADRE :

  · LA DÉCOUVERTE PASSE PAR LE SYSTÈME DE FICHIERS, jamais par un registre à tenir
    à jour — un registre se désynchronise, une arborescence non.
  · DESCRIPTION ET REQUIRES SONT LUS SANS IMPORTER LE MODULE. Afficher l'aide ne
    doit pas pouvoir exécuter le code d'un module déposé dans une liste, ni échouer
    parce que ce module est cassé. C'est le test le plus important du fichier.
  · TROIS COMMANDES NE SE SURCHARGENT PAS. Une liste qui redéfinit « valide » vide
    le contrat de son sens ; une qui redéfinit `help` peut cacher ses commandes ;
    une qui redéfinit `migrate` réécrit ses fichiers comme elle l'entend sous
    couvert d'une commande générique. Le refus est RAPPORTÉ, jamais silencieux.
  · UNE DÉPENDANCE DÉCLARÉE ABSENTE SORT NON NULLE EN LA NOMMANT — la réponse au
    précédent du dépôt, un hook qui gardait sur un outil absent et sortait 0 sans
    un mot, si bien que le garde n'a jamais gardé.
"""

from __future__ import annotations

from pathlib import Path

from jouet import ecrire
from listdir.loader import PROTECTED, CommandSpec, check_requires, discover
from listdir.utils import Toolbox

COMMANDE = '''
"""Une commande de liste."""

DESCRIPTION = "une commande propre à la liste"
REQUIRES: list[str] = []


def command(args, utils):
    return utils.ok("faite")
'''

ANNOTEE = '''
DESCRIPTION: str = "déclarée avec une annotation"
REQUIRES: list[str] = ["git"]


def command(args, utils):
    return utils.ok(None)
'''

EFFET_DE_BORD = '''
from pathlib import Path

Path(__file__).parent.joinpath("importee.temoin").write_text("le module a été exécuté")

DESCRIPTION = "celle qui laisse une trace si on l'importe"
REQUIRES: list[str] = []


def command(args, utils):
    return utils.ok(None)
'''


def poser(liste: Path, nom: str, source: str = COMMANDE) -> Path:
    return ecrire(liste, f".list/commands/{nom}.py", source)


# ------------------------------------------------------------------ découverte
def test_les_generiques_sont_trouvees_sans_liste() -> None:
    commands, refus = discover(None)

    assert refus == []
    assert set(commands) >= {
        "init",
        "new",
        "list",
        "show",
        "validate",
        "migrate",
        "move",
        "derive",
        "merge",
        "help",
    }
    assert all(s.origin == "générique" for s in commands.values())


def test_une_generique_porte_sa_description_et_ses_requires() -> None:
    commands, _ = discover(None)

    assert commands["move"].requires == ("git",)
    assert commands["merge"].description.startswith("agglomère")


def test_une_commande_de_liste_s_ajoute(liste: Path) -> None:
    _ = poser(liste, "solder")
    commands, refus = discover(liste)

    assert refus == []
    assert commands["solder"].origin == "liste"
    assert commands["solder"].description == "une commande propre à la liste"
    assert commands["solder"].overrides is False


def test_une_commande_de_liste_masque_une_generique(liste: Path) -> None:
    _ = poser(liste, "list")
    commands, _ = discover(liste)

    assert commands["list"].origin == "liste"
    assert commands["list"].overrides is True


def test_les_modules_prefixes_d_un_souligne_sont_ignores(liste: Path) -> None:
    _ = poser(liste, "_prive")
    commands, _ = discover(liste)
    assert "_prive" not in commands


def test_sans_repertoire_de_commandes_rien_ne_casse(liste: Path) -> None:
    commands, refus = discover(liste)
    assert refus == []
    assert "list" in commands


# ------------------------------------------- lecture des métadonnées sans import
def test_les_metadonnees_sont_lues_sans_importer_le_module(liste: Path) -> None:
    """LE TEST CENTRAL : afficher l'aide ne doit pas exécuter le code d'un module
    déposé dans une liste par quelqu'un d'autre."""
    _ = poser(liste, "tracante", EFFET_DE_BORD)

    commands, _ = discover(liste)

    assert commands["tracante"].description == "celle qui laisse une trace si on l'importe"
    assert not (liste / ".list/commands/importee.temoin").exists()


def test_la_forme_annotee_est_lue(liste: Path) -> None:
    """`REQUIRES: list[str] = []` est une AnnAssign, pas une Assign : ne lire que la
    seconde ferait passer pour absente la déclaration qu'un auteur soigneux écrit."""
    _ = poser(liste, "annotee", ANNOTEE)
    commands, _ = discover(liste)

    assert commands["annotee"].description == "déclarée avec une annotation"
    assert commands["annotee"].requires == ("git",)


def test_un_module_au_python_casse_est_signale_sans_faire_tomber_les_autres(
    liste: Path,
) -> None:
    _ = poser(liste, "cassee", "def command(:\n")
    _ = poser(liste, "saine")

    commands, refus = discover(liste)

    assert refus == []
    assert commands["cassee"].broken != ""
    assert commands["saine"].description == "une commande propre à la liste"
    assert "list" in commands


def test_un_module_sans_metadonnees_reste_decouvert(liste: Path) -> None:
    _ = poser(liste, "muette", "def command(args, utils):\n    return utils.ok(None)\n")
    commands, _ = discover(liste)

    assert commands["muette"].description == ""
    assert commands["muette"].requires == ()


# --------------------------------------------------------- commandes protégées
def test_les_trois_protegees_sont_bien_celles_la() -> None:
    assert PROTECTED == ("validate", "help", "migrate")


def test_surcharger_une_protegee_est_refuse_et_rapporte(liste: Path) -> None:
    """Une surcharge invisible est un piège : le refus se dit, il ne s'ignore pas."""
    for nom in PROTECTED:
        _ = poser(liste, nom)

    commands, refus = discover(liste)

    assert len(refus) == 3
    for nom in PROTECTED:
        assert any(f"« {nom} » ne se surcharge pas" in m for m in refus)
        assert commands[nom].origin == "générique"


# ------------------------------------------------------------- check_requires
def test_un_outil_present_passe() -> None:
    commands, _ = discover(None)
    assert check_requires(commands["move"])


def test_un_outil_absent_est_nomme(tmp_path: Path) -> None:
    spec = CommandSpec("fictive", tmp_path / "fictive.py", "liste", requires=("outil-absent",))
    r = check_requires(spec)

    assert not r
    assert "outil-absent" in r.message
    assert "REQUIRES" in r.message


def test_seuls_les_outils_manquants_sont_nommes(tmp_path: Path) -> None:
    spec = CommandSpec(
        "fictive", tmp_path / "fictive.py", "liste", requires=("git", "outil-absent")
    )
    assert "outil-absent" in check_requires(spec).message
    assert "git," not in check_requires(spec).message


# ---------------------------------------------------------------- CommandSpec.load
def test_load_rend_le_module(liste: Path) -> None:
    _ = poser(liste, "solder")
    commands, _ = discover(liste)

    module = commands["solder"].load().unwrap()
    assert module.DESCRIPTION == "une commande propre à la liste"


def test_load_refuse_un_module_sans_command(liste: Path) -> None:
    _ = poser(liste, "vide", 'DESCRIPTION = "sans point d\'entrée"\n')
    commands, _ = discover(liste)

    r = commands["vide"].load()
    assert not r
    assert "aucune fonction command(args, utils)" in r.message


def test_load_nomme_une_erreur_d_import(liste: Path) -> None:
    _ = poser(liste, "explosive", 'raise RuntimeError("boum")\n')
    commands, _ = discover(liste)

    r = commands["explosive"].load()
    assert not r
    assert "import impossible" in r.message
    assert "boum" in r.message


# ---------------------------------------------------------------------- Toolbox
def test_run_appelle_une_generique(liste: Path) -> None:
    """C'est ce qui rend une surcharge DÉCORATIVE plutôt que réimplémentée : un
    `close.py` de liste, c'est `move` plus une exigence, pas un second git mv."""
    r = Toolbox(liste).run("validate", [str(liste)])

    assert r
    assert "conformes au contrat" in str(r.unwrap())


def test_run_sur_une_commande_inconnue(liste: Path) -> None:
    r = Toolbox(liste).run("inexistante", [])
    assert not r
    assert "« inexistante » inconnue" in r.message


def test_run_verifie_les_dependances_avant_d_appeler(liste: Path) -> None:
    exigeante = (
        'REQUIRES = ["outil-absent"]\n\n'
        "def command(args, utils):\n"
        '    raise AssertionError("la commande ne doit jamais être appelée")\n'
    )
    _ = poser(liste, "exigeante", exigeante)
    r = Toolbox(liste).run("exigeante", [])

    assert not r
    assert "outil-absent" in r.message


def test_run_atteint_une_commande_de_liste(liste: Path) -> None:
    _ = poser(liste, "solder")
    r = Toolbox(liste).run("solder", [])

    assert r
    assert r.unwrap() == "faite"


def test_toolbox_ouvre_et_git(liste: Path) -> None:
    outils = Toolbox(liste)
    assert outils.open(liste).unwrap().contract.name == "jouet"
    assert outils.ok(3).unwrap() == 3
    assert not outils.fail("non")
