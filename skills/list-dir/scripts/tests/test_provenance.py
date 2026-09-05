"""La table `[origin]` d'un contrat : ce qu'elle admet, et ce qu'elle refuse en le nommant.

CHAQUE REFUS A SON TEST, et pour la raison qui vaut dans tout ce paquet : une table
de provenance mal écrite qui passerait laisserait une liste que son auteur croit
gelée, ou rattachée, se comporter autrement — sans qu'aucune commande n'échoue.

Le contrat-jouet de `jouet.py` ne porte pas d'`[origin]` : c'est l'état d'une liste
antérieure à ce dispositif, et il doit rester valide.
"""

from __future__ import annotations

import os
from pathlib import Path

from jouet import ecrire
from listdir.contract import CONTRACT, LIST_DIR, SEED, TEMPLATES, load_contract, parse_contract
from listdir.provenance import warnings
from listdir.store import init_list
from listdir.types import Contract, Result

BASE = """name = "jouet"
description = "liste-jouet des tests"

[fields.id]
type = "slug"

[sections."Constat"]
required = true
description = ""
"""

SEMEE = BASE + '\n[origin]\ndef = "semee"\nversion = 2\n'
"""Le même contrat, tel qu'une définition installée le porte."""

CHEMIN = Path("/tmp/contrat-jouet/contract.toml")


def _chdir(base: Path) -> None:
    """Les rangs 1 et 2 se cherchent en remontant depuis le RÉPERTOIRE COURANT : sans
    ce déplacement, la définition posée sous `tmp_path/.claude/` resterait invisible."""
    os.chdir(base)


def contrat(origin: str = "") -> Result[Contract]:
    """Le contrat minimal, avec la table `[origin]` passée telle quelle."""
    return parse_contract(BASE + origin, CHEMIN)


def test_absence_d_origin_reste_legitime() -> None:
    """Une liste antérieure au dispositif n'a pas de provenance — c'est un état, pas une faute."""
    assert contrat().unwrap().origin is None


def test_def_false_dit_qu_il_n_y_a_pas_de_semence() -> None:
    origin = contrat("\n[origin]\ndef = false\n").unwrap().origin
    assert origin is not None
    assert origin.name is None
    assert origin.frozen is False


def test_def_nomme_avec_version_et_gel() -> None:
    origin = (
        contrat('\n[origin]\ndef = "technical-debt"\nversion = 3\nfrozen = true\n').unwrap().origin
    )
    assert origin is not None
    assert (origin.name, origin.version, origin.frozen) == ("technical-debt", 3, True)


def test_frozen_vaut_faux_par_defaut() -> None:
    origin = contrat('\n[origin]\ndef = "d"\nversion = 1\n').unwrap().origin
    assert origin is not None
    assert origin.frozen is False


def test_cle_inconnue_refusee_en_la_nommant() -> None:
    """Un « frozen » mal orthographié ferait réécrire une liste que son auteur croit gelée."""
    r = contrat('\n[origin]\ndef = "d"\nversion = 1\nfrozzen = true\n')
    assert not r
    assert "frozzen" in r.message


def test_def_manquante_refusee() -> None:
    r = contrat("\n[origin]\nversion = 1\n")
    assert not r
    assert "def" in r.message


def test_def_ni_chaine_ni_false_refusee() -> None:
    r = contrat("\n[origin]\ndef = 12\nversion = 1\n")
    assert not r
    assert "int" in r.message


def test_def_vide_refusee() -> None:
    r = contrat('\n[origin]\ndef = ""\nversion = 1\n')
    assert not r


def test_def_avec_espace_refusee() -> None:
    """Le nom traverse une substitution de shell : une espace le couperait en deux."""
    r = contrat('\n[origin]\ndef = "deux mots"\nversion = 1\n')
    assert not r
    assert "espace" in r.message


def test_nom_de_gabarit_admis() -> None:
    """« mère/dérivée » nomme le gabarit d'une définition — la semence d'une dérivée."""
    r = contrat('\n[origin]\ndef = "technical-debt/review"\nversion = 1\nfrozen = true\n')
    origin = r.unwrap().origin
    assert origin is not None
    assert origin.name == "technical-debt/review"
    assert origin.definition == "technical-debt"
    assert origin.template == "review"


def test_nom_simple_ne_vise_aucun_gabarit() -> None:
    origin = contrat('\n[origin]\ndef = "technical-debt"\nversion = 1\n').unwrap().origin
    assert origin is not None
    assert origin.definition == "technical-debt"
    assert origin.template is None


def test_sans_semence_les_deux_parts_sont_absentes() -> None:
    origin = contrat("\n[origin]\ndef = false\n").unwrap().origin
    assert origin is not None
    assert origin.definition is None
    assert origin.template is None


def test_trois_segments_refuses() -> None:
    """Les gabarits vivent à plat dans `templates/` : un troisième segment ne vise rien."""
    for nom in ("a/b/c", "a//b"):
        r = contrat(f'\n[origin]\ndef = "{nom}"\nversion = 1\n')
        assert not r, nom
        assert "au plus un" in r.message


def test_segment_vide_refuse() -> None:
    for nom in ("a/", "/a"):
        r = contrat(f'\n[origin]\ndef = "{nom}"\nversion = 1\n')
        assert not r, nom
        assert "n'est pas un nom" in r.message


def test_remontee_de_chemin_refusee() -> None:
    """C'est un nom, pas un chemin : `..` sortirait de `templates/`."""
    for nom in ("../x", "a/..", "./a", "a/."):
        r = contrat(f'\n[origin]\ndef = "{nom}"\nversion = 1\n')
        assert not r, nom


def test_version_manquante_sous_un_nom_refusee() -> None:
    r = contrat('\n[origin]\ndef = "d"\n')
    assert not r
    assert "version" in r.message


def test_version_booleenne_refusee() -> None:
    """`isinstance(True, int)` est vrai : sans refus, `version = true` passerait pour 1."""
    r = contrat('\n[origin]\ndef = "d"\nversion = true\n')
    assert not r
    assert "bool" in r.message


def test_version_nulle_refusee() -> None:
    r = contrat('\n[origin]\ndef = "d"\nversion = 0\n')
    assert not r
    assert ">= 1" in r.message


def test_frozen_non_booleen_refuse() -> None:
    r = contrat('\n[origin]\ndef = "d"\nversion = 1\nfrozen = "oui"\n')
    assert not r
    assert "booléen" in r.message


def test_version_sous_def_false_refusee() -> None:
    """Sans semence, il n'y a ni version à comparer ni semis à refuser."""
    r = contrat("\n[origin]\ndef = false\nversion = 1\n")
    assert not r
    assert "version" in r.message


def test_frozen_sous_def_false_refuse() -> None:
    r = contrat("\n[origin]\ndef = false\nfrozen = true\n")
    assert not r
    assert "frozen" in r.message


def test_origin_qui_n_est_pas_une_table_refusee() -> None:
    """La ligne va AVANT les tables : en TOML, une clé nue posée après appartient à la
    dernière table ouverte, et ne serait donc plus la provenance du contrat."""
    r = parse_contract('origin = "technical-debt"\n' + BASE, CHEMIN)
    assert not r
    assert "origin" in r.message


# ------------------------------------------------ ce qu'`init` écrit
def test_squelette_declare_qu_il_n_a_pas_de_semence(tmp_path: Path) -> None:
    """Une liste née à la main n'aura jamais de définition à rattraper : elle le dit
    d'emblée, sinon l'avertissement d'adoption la poursuivrait pour toujours."""
    cible = tmp_path / "neuve"
    _ = init_list(cible).unwrap()

    origin = load_contract(cible).unwrap().origin
    assert origin is not None
    assert origin.name is None


def test_init_depuis_une_definition_copie_et_garde_la_semence(tmp_path: Path) -> None:
    """La copie est octet pour octet la semence, et `.list/semence/` en garde une
    seconde, intacte : c'est le point de référence de `reseed`."""
    definition = tmp_path / "def"
    _ = ecrire(definition, CONTRACT, SEMEE)
    _ = ecrire(definition, f"{TEMPLATES}/revue.md", "## Revue\n")
    cible = tmp_path / "neuve"

    _ = init_list(cible, definition=definition).unwrap()

    base = cible / LIST_DIR
    assert (base / CONTRACT).read_text(encoding="utf-8") == SEMEE
    assert (base / SEED / CONTRACT).read_text(encoding="utf-8") == SEMEE
    assert (base / SEED / TEMPLATES / "revue.md").read_text(encoding="utf-8") == "## Revue\n"


def test_from_estampille_comme_def(tmp_path: Path) -> None:
    """`init` n'écrit jamais `[origin]`, il la REÇOIT : le chemin emprunté pour
    atteindre la semence ne change donc rien à ce qui est estampillé."""
    definition = tmp_path / "ailleurs"
    _ = ecrire(definition, CONTRACT, SEMEE)
    cible = tmp_path / "neuve"

    _ = init_list(cible, definition=definition).unwrap()

    origin = load_contract(cible).unwrap().origin
    assert origin is not None
    assert (origin.name, origin.version) == ("semee", 2)


def test_def_discordant_refuse_en_code_2(tmp_path: Path) -> None:
    """L'estampille copiée nommerait une définition que `reseed` irait chercher à tort."""
    definition = tmp_path / "def"
    _ = ecrire(definition, CONTRACT, SEMEE)
    cible = tmp_path / "neuve"

    r = init_list(cible, definition=definition, expected_name="autre-nom")

    assert r.status == 2
    assert "semee" in r.message
    assert not cible.exists()


def test_definition_sans_origin_seme_sans_provenance(tmp_path: Path) -> None:
    """Une absence n'est pas une contradiction : le contrôle ne mord que sur deux
    noms qui se contredisent."""
    definition = tmp_path / "def"
    _ = ecrire(definition, CONTRACT, BASE)
    cible = tmp_path / "neuve"

    _ = init_list(cible, definition=definition, expected_name="jouet").unwrap()

    assert load_contract(cible).unwrap().origin is None


# ------------------------------------------------ les avertissements
def semer(tmp_path: Path, version: int = 2, nom: str = "semee") -> tuple[Path, Path]:
    """Une définition installée au rang 1, et une liste qu'elle a semée.

    Le rang 1 gagne toujours : ces tests ne dépendent donc pas des définitions
    réellement installées sur la machine.
    """
    definition = tmp_path / ".claude" / "list-dir" / nom
    _ = ecrire(definition, CONTRACT, BASE + f'\n[origin]\ndef = "{nom}"\nversion = {version}\n')
    cible = tmp_path / "liste"
    _ = init_list(cible, definition=definition).unwrap()
    return definition, cible


def dits(liste: Path) -> list[str]:
    return warnings(liste, load_contract(liste).unwrap())


def test_sans_origin_le_geste_d_adoption_est_rappele(tmp_path: Path) -> None:
    cible = tmp_path / "liste"
    _ = ecrire(cible, f"{LIST_DIR}/{CONTRACT}", BASE)

    assert "reseed" in "\n".join(dits(cible))


def test_def_false_ne_dit_rien(tmp_path: Path) -> None:
    """Une liste née à la main n'a rien à rattraper : l'avertir serait du bruit."""
    cible = tmp_path / "liste"
    _ = ecrire(cible, f"{LIST_DIR}/{CONTRACT}", BASE + "\n[origin]\ndef = false\n")

    assert dits(cible) == []


def test_semence_a_la_meme_version_ne_dit_rien(tmp_path: Path) -> None:
    _, cible = semer(tmp_path)
    _chdir(tmp_path)

    assert dits(cible) == []


def test_semence_plus_recente_dit_la_peremption_et_le_geste(tmp_path: Path) -> None:
    definition, cible = semer(tmp_path, version=2)
    _ = ecrire(definition, CONTRACT, BASE + '\n[origin]\ndef = "semee"\nversion = 5\n')
    _chdir(tmp_path)

    (dit,) = dits(cible)
    assert "v2" in dit and "v5" in dit and "reseed" in dit


def test_frozen_tait_la_peremption(tmp_path: Path) -> None:
    """La reprise en main est déclarée : on ne la rappelle plus."""
    definition, cible = semer(tmp_path, version=2)
    _ = ecrire(definition, CONTRACT, BASE + '\n[origin]\ndef = "semee"\nversion = 9\n')
    _ = ecrire(
        cible,
        f"{LIST_DIR}/{CONTRACT}",
        BASE + '\n[origin]\ndef = "semee"\nversion = 2\nfrozen = true\n',
    )
    _chdir(tmp_path)

    assert dits(cible) == []


def test_estampille_de_gabarit_ne_se_dit_pas_introuvable(tmp_path: Path) -> None:
    """Une dérivée dégelée à la main ne doit pas s'entendre envoyer au mauvais endroit.

    Le gel du gabarit fait taire ce cas en temps normal ; il reste que le message,
    quand on l'atteint, doit dire la vérité plutôt que « définition introuvable ».
    """
    definition, cible = semer(tmp_path)
    _ = ecrire(
        cible,
        f"{LIST_DIR}/{CONTRACT}",
        BASE + '\n[origin]\ndef = "semee/review"\nversion = 1\n',
    )
    _chdir(tmp_path)
    assert definition.is_dir()

    (dit,) = [d for d in dits(cible) if "péremption d'un gabarit" in d]
    assert "introuvable dans les quatre rangs" not in dit
    assert "list-dir contract --def semee --template review" in dit


def test_semence_introuvable_dit_que_la_peremption_est_invérifiable(tmp_path: Path) -> None:
    """Sur une machine où le skill n'est pas installé, le silence ne prouverait rien."""
    definition, cible = semer(tmp_path)
    for f in sorted(definition.glob("*")):
        f.unlink()
    definition.rmdir()
    _chdir(tmp_path)

    assert "invérifiable" in "\n".join(dits(cible))


def test_semence_sans_provenance_est_signalee(tmp_path: Path) -> None:
    definition, cible = semer(tmp_path)
    _ = ecrire(definition, CONTRACT, BASE)
    _chdir(tmp_path)

    assert "invérifiable" in "\n".join(dits(cible))


def test_contrat_modifie_localement_est_dit_sans_resoudre_la_definition(tmp_path: Path) -> None:
    """La comparaison se fait avec `.list/semence/` : elle vaut là où rien n'est installé."""
    definition, cible = semer(tmp_path)
    _ = ecrire(
        cible,
        f"{LIST_DIR}/{CONTRACT}",
        BASE + '\n[fields.local]\ntype = "text"\n\n[origin]\ndef = "semee"\nversion = 2\n',
    )
    for f in sorted(definition.glob("*")):
        f.unlink()
    definition.rmdir()
    _chdir(tmp_path)

    assert any("modifié localement" in d for d in dits(cible))


def test_gabarit_modifie_localement_est_dit(tmp_path: Path) -> None:
    definition = tmp_path / ".claude" / "list-dir" / "semee"
    _ = ecrire(definition, CONTRACT, BASE + '\n[origin]\ndef = "semee"\nversion = 1\n')
    _ = ecrire(definition, f"{TEMPLATES}/revue.md", "## Revue\n")
    cible = tmp_path / "liste"
    _ = init_list(cible, definition=definition).unwrap()
    _ = ecrire(cible, f"{LIST_DIR}/{TEMPLATES}/revue.md", "## Revue remaniée\n")
    _chdir(tmp_path)

    assert any("revue.md" in d and "modifié localement" in d for d in dits(cible))


def test_sans_semence_gardee_on_se_tait_sur_les_modifications(tmp_path: Path) -> None:
    """Une liste adoptée n'a pas de point de référence : on ne sait pas ce qui a été semé."""
    _, cible = semer(tmp_path)
    for f in sorted((cible / LIST_DIR / SEED).rglob("*")):
        if f.is_file():
            f.unlink()
    _ = ecrire(cible, f"{LIST_DIR}/{CONTRACT}", BASE + '\n[origin]\ndef = "semee"\nversion = 2\n')
    _chdir(tmp_path)

    assert dits(cible) == []
