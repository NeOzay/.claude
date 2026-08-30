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

from jouet import CONTRAT, ELEMENT, ecrire, monter_liste

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
    assert "Commandes génériques (12)" in r.out
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


# ------------------------------------------------ init : --def et --from
def poser_definition(base: Path, nom: str) -> Path:
    """Une définition sous un rang de projet : `<base>/.claude/list-dir/<nom>/`.

    Le rang 1 gagne toujours, ce qui rend ces tests indépendants des définitions
    réellement installées sur la machine : la configuration ne contribue qu'aux
    rangs 3 et 4, que celui-ci masque.
    """
    _ = ecrire(base, f".claude/list-dir/{nom}/contract.toml", CONTRAT)
    return base / ".claude/list-dir" / nom


def test_init_def_inconnu(tmp_path: Path) -> None:
    """Introuvable est un échec fermé, pas un repli sur le squelette : amorcer au
    squelette une liste dont on a nommé la définition donnerait un contrat faux
    sous un code de succès."""
    r = lancer(
        "init", str(tmp_path / "neuve"), "--def", "aucune-definition-de-ce-nom", cwd=tmp_path
    )

    assert r.code == 1
    assert "introuvable" in r.err
    assert not (tmp_path / "neuve").exists()


def test_init_def_et_from_exclusifs(tmp_path: Path) -> None:
    """Les combiner poserait la question de qui gagne, et toute réponse serait
    arbitraire. argparse refuse : code 2, comme toute erreur d'appel."""
    r = lancer(
        "init", str(tmp_path / "neuve"), "--def", "jouet", "--from", str(tmp_path), cwd=tmp_path
    )

    assert r.code == 2
    assert r.out == ""


def test_init_def_amorce_depuis_le_rang_projet(tmp_path: Path) -> None:
    _ = poser_definition(tmp_path, "jouet")
    r = lancer("init", str(tmp_path / "neuve"), "--def", "jouet", cwd=tmp_path)

    assert r.code == 0
    assert r.out.strip().endswith("neuve/.list/contract.toml")
    assert lancer("validate", str(tmp_path / "neuve")).code == 0


def test_init_from_amorce_depuis_un_chemin(tmp_path: Path) -> None:
    """La porte de sortie : essayer une définition qu'aucun rang ne porte encore."""
    src = tmp_path / "hors-rang"
    _ = ecrire(src, "contract.toml", CONTRAT)
    r = lancer("init", str(tmp_path / "neuve"), "--from", str(src), cwd=tmp_path)

    assert r.code == 0
    assert lancer("validate", str(tmp_path / "neuve")).code == 0


def test_init_sans_definition_reste_le_squelette(tmp_path: Path) -> None:
    r = lancer("init", str(tmp_path / "neuve"), cwd=tmp_path)

    assert r.code == 0
    contrat = (tmp_path / "neuve/.list/contract.toml").read_text(encoding="utf-8")
    assert 'required = ["Constat"]' in contrat
    assert "category" not in contrat


# ------------------------------------------------------------------ defs
def test_defs_liste_et_origine(tmp_path: Path) -> None:
    _ = poser_definition(tmp_path, "alpha")
    _ = poser_definition(tmp_path, "beta")
    r = lancer("defs", cwd=tmp_path)

    assert r.code == 0
    assert "alpha" in r.out
    assert "beta" in r.out
    assert "rang 1" in r.out
    assert "projet" in r.out


def test_defs_imprime_la_racine_de_projet_retenue(tmp_path: Path) -> None:
    """La remontée s'arrête au premier `.claude` trouvé, qui n'est pas toujours
    celui qu'on avait en tête. L'imprimer rend le choix visible."""
    _ = poser_definition(tmp_path, "alpha")
    profond = tmp_path / "src" / "a"
    profond.mkdir(parents=True)
    r = lancer("defs", cwd=profond)

    assert r.code == 0
    assert str(tmp_path / ".claude") in r.out


def test_defs_dit_qu_une_definition_en_masque_une_autre(tmp_path: Path) -> None:
    """Taire la perdante ferait chercher longtemps pourquoi une liste n'est pas
    amorcée avec le contrat attendu."""
    _ = poser_definition(tmp_path, "jouet")
    _ = ecrire(tmp_path, ".claude/skills/s1/list-dir/jouet/contract.toml", CONTRAT)
    r = lancer("defs", cwd=tmp_path)

    assert r.code == 0
    assert "masque projet:s1" in r.out


def test_defs_hors_de_tout_claude_le_dit(tmp_path: Path) -> None:
    """Une sortie muette se lirait comme un plantage."""
    nu = tmp_path / "nu"
    nu.mkdir()
    r = lancer("defs", cwd=nu)

    assert r.code == 0
    assert "aucun — rangs 1 et 2 absents" in r.out


def test_defs_apparait_dans_help() -> None:
    r = lancer("help")

    assert r.code == 0
    assert "defs" in r.out


# -------------------------------------------------------------- contract
def test_contract_imprime_le_contrat(tmp_path: Path) -> None:
    liste = liste_sur_disque(tmp_path)
    r = lancer("contract", str(liste))

    assert r.code == 0
    assert r.out.rstrip("\n") == CONTRAT.rstrip("\n")


def test_contract_rend_le_texte_tel_quel_commentaires_compris(tmp_path: Path) -> None:
    """Les commentaires portent le pourquoi d'un champ : un aller-retour de parseur
    perdrait exactement ce que le lecteur venait chercher."""
    avec_commentaire = "# pourquoi ce contrat existe\n" + CONTRAT
    liste = monter_liste(tmp_path / "commentee", avec_commentaire)
    r = lancer("contract", str(liste))

    assert r.code == 0
    assert "# pourquoi ce contrat existe" in r.out


def test_contract_refuse_un_contrat_casse(tmp_path: Path) -> None:
    """Imprimer sans juger rendrait la règle sous un code de succès alors qu'aucune
    commande ne peut l'appliquer."""
    liste = monter_liste(tmp_path / "cassee", 'name = "n"\n\n[fields.c]\ntype = "inconnu"\n')
    r = lancer("contract", str(liste))

    assert r.code == 1
    assert r.out == ""


def test_contract_sur_un_repertoire_qui_n_est_pas_une_liste(tmp_path: Path) -> None:
    r = lancer("contract", str(tmp_path))

    assert r.code == 1
    assert r.out == ""


# ---------------------------------- R2/R3 : ce que defs annonce, init le fait
def test_defs_ne_designe_pas_de_gagnante_a_rang_egal(tmp_path: Path) -> None:
    """R2 — `defs` annonçait « rang 2, projet:a (masque projet:b) » pendant qu'`init
    --def` sortait 1 en refusant de trancher. La commande de découverte promettait
    ce que la commande d'amorçage refusait, et c'est la promesse qu'on croit."""
    _ = ecrire(tmp_path, ".claude/skills/a/list-dir/dupe/contract.toml", CONTRAT)
    _ = ecrire(tmp_path, ".claude/skills/b/list-dir/dupe/contract.toml", CONTRAT)

    vu = lancer("defs", cwd=tmp_path)
    assert vu.code == 0
    assert "AMBIGUË" in vu.out
    assert "masque" not in vu.out

    amorce = lancer("init", str(tmp_path / "neuve"), "--def", "dupe", cwd=tmp_path)
    assert amorce.code == 1
    assert "ambiguë" in amorce.err


def test_defs_annonce_encore_le_masquage_entre_rangs_differents(tmp_path: Path) -> None:
    """Le correctif de R2 ne doit pas emporter le masquage légitime, qui lui est un
    succès : c'est ainsi qu'un projet reprend la main."""
    _ = poser_definition(tmp_path, "jouet")
    _ = ecrire(tmp_path, ".claude/skills/s1/list-dir/jouet/contract.toml", CONTRAT)

    r = lancer("defs", cwd=tmp_path)
    assert r.code == 0
    assert "masque projet:s1" in r.out
    assert "AMBIGUË" not in r.out


def test_name_avec_def_est_refuse(tmp_path: Path) -> None:
    """R3 — `--name` était ignoré en silence : la commande rendait 0 sur un contrat
    qui ne portait pas ce qui avait été demandé."""
    _ = poser_definition(tmp_path, "jouet")
    r = lancer("init", str(tmp_path / "neuve"), "--def", "jouet", "--name", "MonNom", cwd=tmp_path)

    assert r.code == 2
    assert "ne s'appliquent qu'au squelette" in r.err
    assert not (tmp_path / "neuve").exists()


def test_description_avec_from_est_refusee(tmp_path: Path) -> None:
    """`--description` est ignoré exactement comme `--name` : le laisser passer
    reproduirait le constat à l'identique."""
    src = tmp_path / "hors-rang"
    _ = ecrire(src, "contract.toml", CONTRAT)
    r = lancer(
        "init", str(tmp_path / "neuve"), "--from", str(src), "--description", "x", cwd=tmp_path
    )

    assert r.code == 2
    assert not (tmp_path / "neuve").exists()


def test_name_reste_accepte_sur_le_squelette(tmp_path: Path) -> None:
    """Le refus ne vaut que combiné à une définition : sans elle, ces deux options
    sont la seule façon de nommer une liste."""
    r = lancer("init", str(tmp_path / "neuve"), "--name", "MonNom", cwd=tmp_path)

    assert r.code == 0
    assert 'name = "MonNom"' in (tmp_path / "neuve/.list/contract.toml").read_text(encoding="utf-8")
