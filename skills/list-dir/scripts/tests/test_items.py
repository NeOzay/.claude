"""items.py — lecture d'un élément, et l'écriture qui reprojette au lieu de réécrire.

CE QUE CE FICHIER CADRE, et qu'aucun linter ne dira :

  Écrire, c'est REPROJETER. Le texte brut du front matter lu est le document sur
  lequel on repose les champs, et seuls ceux dont la valeur a changé sont réécrits.
  Guillemets, ordre des clés, tableaux mis en forme et commentaires survivent donc à
  une réécriture qui ne portait pas sur eux.

  Un type hors contrat reste une erreur qui le NOMME. tomlkit écrirait un dict en
  table sans broncher : la garde ne vient pas de l'écrivain, elle est à nous.

Il y avait ici une frontière — `raw_front is None` déclenchait une resérialisation
intégrale — et c'est elle qui aplatissait tous les tableaux au premier `migrate`.
Les trois défauts historiques du paquet vivaient dans ce module : le découpage sur un
`## ` de bloc de code, un sérialiseur qui n'échappait pas les sauts de ligne, et ce
reformatage massif. Les trois sont corrigés ; ce qui suit est ce qui empêche leur
retour.
"""

from __future__ import annotations

import datetime
import tomllib
from pathlib import Path

import pytest
from listdir.items import (
    SerialiseError,
    dump_front,
    dump_value,
    fence_ouverte,
    outside_fences,
    parse_sections,
    read_item,
    render_item,
    split_front,
    write_item,
)
from listdir.types import Item

# ------------------------------------------------------------------ split_front
FICHIER = Path("/jouet/x.md")


def test_front_matter_absent_est_nomme() -> None:
    r = split_front("pas de délimiteur\n", FICHIER)
    assert not r
    assert "front matter absent" in r.message


def test_front_matter_non_ferme_est_nomme() -> None:
    r = split_front('+++\nid = "x"\n\n## Constat\n', FICHIER)
    assert not r
    assert "non fermé" in r.message


def test_front_matter_vide_est_legitime() -> None:
    """Deux délimiteurs collés : un front matter vide n'est pas un front matter absent."""
    front, corps = split_front("+++\n+++\n\n## Constat\n\nx\n", FICHIER).unwrap()
    assert front == ""
    assert corps.startswith("\n## Constat")


# -------------------------------------------------- outside_fences / parse_sections
def test_titre_dans_un_bloc_de_code_n_ouvre_pas_de_section() -> None:
    """Le défaut historique : une preuve exécutée collée créait des sections fantômes."""
    corps = "## Constat\n\n```\n## pas un titre\n```\n\n## Assumé\n\nx\n"
    assert list(parse_sections(corps)) == ["Constat", "Assumé"]
    assert "## pas un titre" in parse_sections(corps)["Constat"]


def test_bloc_a_tildes() -> None:
    corps = "## Constat\n\n~~~\n## pas un titre\n~~~\n\n## Assumé\n\nx\n"
    assert list(parse_sections(corps)) == ["Constat", "Assumé"]


def test_une_cloture_plus_courte_ne_ferme_pas() -> None:
    """CommonMark : une clôture doit répéter le caractère AU MOINS autant de fois."""
    corps = "## Constat\n\n````\n```\n## avalé\n````\n\n## Assumé\n\nx\n"
    assert list(parse_sections(corps)) == ["Constat", "Assumé"]
    assert "## avalé" in parse_sections(corps)["Constat"]


def test_une_cloture_portant_une_info_string_n_en_est_pas_une() -> None:
    """« ```python » DANS un bloc ouvert par « ``` » est du contenu, pas une fermeture."""
    corps = "## Constat\n\n```\n```python\n## avalé\n```\n\n## Assumé\n\nx\n"
    assert list(parse_sections(corps)) == ["Constat", "Assumé"]


def test_un_bloc_ne_s_ouvre_pas_sur_une_info_string_a_backtick() -> None:
    """L'info string d'un bloc à backticks ne peut pas contenir de backtick."""
    lignes = dict(outside_fences("``` `x`\n## un vrai titre\n"))
    assert lignes["## un vrai titre"] is True


def test_ce_qui_precede_le_premier_titre_est_ignore() -> None:
    assert parse_sections("préambule libre\n\n## Constat\n\nx\n") == {"Constat": "x"}


def test_sections_vides_et_ordre_conserve() -> None:
    sections = parse_sections("## A\n\n## B\n\ntexte\n")
    assert list(sections) == ["A", "B"]
    assert sections["A"] == ""


# ------------------------------------------------------------------ fence_ouverte
def test_fence_refermee_ne_signale_rien() -> None:
    assert fence_ouverte("```\ncode\n```\n") is None


def test_texte_finissant_sur_la_cloture_ne_signale_rien() -> None:
    """Le cas limite : la ligne de clôture est elle-même rendue « non libre »."""
    assert fence_ouverte("avant\n```\ncode\n```") is None


def test_fence_jamais_refermee_est_nommee() -> None:
    assert fence_ouverte("## Constat\n\n```\ncode sans fin\n") == "```"


def test_une_fence_ouverte_avale_les_sections_suivantes() -> None:
    """COMPORTEMENT JUSTE, et qui doit le rester : c'est CommonMark, et l'aller-retour
    reste exact. Ce qui était faux, ce sont les diagnostics — cf. test_store_lecture."""
    corps = "## Constat\n\n```\n## Assumé\n\navalé\n"
    assert list(parse_sections(corps)) == ["Constat"]


# ------------------------------------------------- règle 1 : l'aller-retour octet
BRUT = '''+++
# un commentaire que tomllib ignore
title = "des \\"guillemets\\" et une apostrophe"
id = "z"
tags = [ "b",  "a" ]
+++

## Constat

Le corps.

## Assumé

<OPTIONNEL>
'''


def test_aller_retour_octet_pour_octet(tmp_path: Path) -> None:
    """Guillemets, ORDRE DES CLÉS et commentaires compris — c'est la règle 1."""
    path = tmp_path / "z.md"
    _ = path.write_text(BRUT, encoding="utf-8")
    item = read_item(path).unwrap()
    assert item.render() == BRUT


def test_raw_front_conserve_le_texte_brut(tmp_path: Path) -> None:
    path = tmp_path / "z.md"
    _ = path.write_text(BRUT, encoding="utf-8")
    item = read_item(path).unwrap()
    assert item.raw_front is not None
    assert "# un commentaire" in item.raw_front
    assert item.fields["id"] == "z"


def test_toml_invalide_est_nomme(tmp_path: Path) -> None:
    path = tmp_path / "z.md"
    _ = path.write_text("+++\nid = \n+++\n\n## Constat\n\nx\n", encoding="utf-8")
    r = read_item(path)
    assert not r
    assert "TOML invalide" in r.message


def test_fichier_illisible_est_nomme(tmp_path: Path) -> None:
    r = read_item(tmp_path / "absent.md")
    assert not r
    assert "illisible" in r.message


# ------------------------------------------ ce que l'écriture reprojette, ou non
def test_un_champ_modifie_ne_touche_que_lui(tmp_path: Path) -> None:
    """CE QUI A CHANGÉ EST RÉÉCRIT, LE RESTE EST RECONDUIT. C'était l'inverse : le
    moindre champ modifié resérialisait tout, et un `migrate` qui ajoutait un champ
    au contrat aplatissait au passage les tableaux de tous les éléments."""
    path = tmp_path / "z.md"
    _ = path.write_text(BRUT, encoding="utf-8")
    item = read_item(path).unwrap()
    modifie = item.with_fields(id="autre")

    assert modifie.raw_front is not None
    assert 'id = "autre"' in modifie.render()
    assert "# un commentaire" in modifie.render()
    assert 'tags = [ "b",  "a" ]' in modifie.render()


def test_with_sections_ne_reserialise_pas(tmp_path: Path) -> None:
    """Toucher le corps ne touche pas le front matter : la règle 1 y prime encore."""
    path = tmp_path / "z.md"
    _ = path.write_text(BRUT, encoding="utf-8")
    item = read_item(path).unwrap()
    modifie = item.with_sections(Constat="autre chose")

    assert modifie.raw_front is not None
    assert "# un commentaire" in modifie.render()


def test_realigned_remplace_et_retire(tmp_path: Path) -> None:
    """realigned REMPLACE — il sait retirer et réordonner, là où with_fields fusionne.
    Il le fait désormais SUR le document d'origine, sans reformater ce qui reste."""
    path = tmp_path / "z.md"
    _ = path.write_text(BRUT, encoding="utf-8")
    item = read_item(path).unwrap()
    aligne = item.realigned({"id": "z"}, {"Constat": "x"})

    assert dict(aligne.fields) == {"id": "z"}
    assert "title" not in aligne.render()
    assert 'id = "z"' in aligne.render()


@pytest.mark.parametrize(
    ("valeur", "attendu"),
    [
        ("texte", '"texte"'),
        (True, "true"),
        (False, "false"),
        (7, "7"),
        (datetime.date(2026, 8, 24), "2026-08-24"),
        (["a", "b"], '["a", "b"]'),
        ([], "[]"),
    ],
)
def test_dump_value_couvre_les_types_du_contrat(valeur: object, attendu: str) -> None:
    assert dump_value(valeur, "champ") == attendu


def test_bool_est_serialise_avant_int() -> None:
    """bool EST un int en Python : l'ordre des tests du sérialiseur est ce qui décide."""
    assert dump_value(True, "x") == "true"
    assert dump_value(True, "x") != "1"


@pytest.mark.parametrize(
    ("brut", "attendu"),
    [
        ("a\nb", '"a\\nb"'),
        ("a\rb", '"a\\rb"'),
        ("a\tb", '"a\\tb"'),
        ("a\bb", '"a\\bb"'),
        ("a\fb", '"a\\fb"'),
        ('un "mot"', '"un \\"mot\\""'),
        ("c:\\chemin", '"c:\\\\chemin"'),
    ],
)
def test_echappements_relisibles(brut: str, attendu: str) -> None:
    """TOUT CE QUI EST ÉCRIT DOIT SE RELIRE : un saut de ligne non échappé fermait la
    chaîne au milieu, et migrate écrivait un fichier que tomllib refuse en rendant 0."""
    assert dump_value(brut, "x") == attendu


def test_caractere_de_controle_refuse_et_nomme() -> None:
    with pytest.raises(SerialiseError) as exc:
        _ = dump_value("a\x00b", "champ")
    assert "champ" in str(exc.value)
    assert "U+0000" in str(exc.value)


def test_type_hors_contrat_refuse_et_nomme() -> None:
    with pytest.raises(SerialiseError) as exc:
        _ = dump_value({"a": 1}, "champ")
    assert "champ" in str(exc.value)
    assert "dict" in str(exc.value)


def test_dump_front_conserve_l_ordre() -> None:
    assert dump_front({"b": "1", "a": "2"}) == 'b = "1"\na = "2"'


# ------------------------------------------------------------ write_item / relecture
def test_ecrire_puis_relire(tmp_path: Path) -> None:
    item = Item(
        tmp_path / "sous/dossier/n.md",
        {"id": "n", "title": "Titre", "tags": ["x"]},
        {"Constat": "corps"},
    )
    chemin = write_item(item).unwrap()
    relu = read_item(chemin).unwrap()

    assert relu.fields["id"] == "n"
    assert relu.fields["tags"] == ["x"]
    assert relu.sections["Constat"] == "corps"


def test_ecriture_refusee_sur_type_hors_contrat(tmp_path: Path) -> None:
    """L'échec du sérialiseur devient un Result, jamais une exception qui remonte nue."""
    item = Item(tmp_path / "n.md", {"id": "n", "bizarre": {"a": 1}}, {"Constat": "x"})
    r = write_item(item)
    assert not r
    assert "hors contrat" in r.message


def test_render_item_est_la_forme_canonique() -> None:
    item = Item(Path("/x/n.md"), {"id": "n"}, {"A": "un", "B": "deux"})
    assert render_item(item) == '+++\nid = "n"\n+++\n\n## A\n\nun\n\n## B\n\ndeux\n'


# ------------------------------------ ce que le document d'origine impose au rendu
FRONT_MIS_EN_FORME = """\
id = "z"
# la légende de « tags », sur deux lignes
# et qui appartient au champ qu'elle précède
tags = [
  "premier",
  "deuxième",
]
title = 'guillemets simples'
# celui-ci ne précède aucun champ
"""


def test_un_champ_modifie_laisse_les_autres_a_l_octet() -> None:
    """LE CŒUR DU DISPOSITIF : reprojeter, ce n'est pas réécrire. Un champ qui n'a pas
    bougé n'est pas resérialisé, donc garde la mise en forme qu'on lui a donnée."""
    fields = {"id": "autre", "tags": ["premier", "deuxième"], "title": "guillemets simples"}
    sortie = dump_front(fields, FRONT_MIS_EN_FORME)

    assert 'id = "autre"' in sortie
    assert '  "premier",\n  "deuxième",\n' in sortie
    assert "# la légende de « tags »" in sortie
    assert "'guillemets simples'" in sortie


def test_sans_raw_front_le_document_est_neuf() -> None:
    """Un élément créé de toutes pièces n'a aucune mise en forme à préserver."""
    assert dump_front({"b": "1", "a": "2"}) == 'b = "1"\na = "2"'


def test_le_commentaire_suit_son_champ_au_reordonnancement() -> None:
    """UN COMMENTAIRE APPARTIENT AU CHAMP QU'IL PRÉCÈDE — c'est la seule règle
    décidable sur un front matter plat, et celle qu'avait en tête qui l'a écrit."""
    ordre = {"title": "guillemets simples", "tags": ["premier", "deuxième"], "id": "z"}
    sortie = dump_front(ordre, FRONT_MIS_EN_FORME)

    assert sortie.index("title") < sortie.index("tags =") < sortie.index("id =")
    assert sortie.index("# la légende de « tags »") < sortie.index("tags =")
    assert '  "premier",\n  "deuxième",\n' in sortie


def test_le_commentaire_sans_champ_derriere_reste_en_queue() -> None:
    """Il ne précède aucun champ : le rattacher au dernier le ferait voyager au
    premier réordonnancement, sans que personne l'ait voulu."""
    ordre = {"title": "guillemets simples", "tags": ["premier", "deuxième"], "id": "z"}
    sortie = dump_front(ordre, FRONT_MIS_EN_FORME)

    assert sortie.rstrip().endswith("# celui-ci ne précède aucun champ")


def test_le_commentaire_de_queue_ne_se_fait_pas_adopter_par_un_champ_ajoute() -> None:
    """CE QUE FAIT UN `migrate` ORDINAIRE : il ajoute un champ, qui se pose en fin de
    document — donc derrière le commentaire orphelin. Sans précaution, celui-ci devient
    sa légende et le suit au premier réordonnancement, alors qu'il n'appartient à
    personne."""
    avec_ajout = dump_front(
        {"id": "z", "tags": ["premier", "deuxième"], "title": "guillemets simples", "neuf": "X"},
        FRONT_MIS_EN_FORME,
    )
    assert avec_ajout.index('neuf = "X"') < avec_ajout.index("# celui-ci ne précède aucun champ")

    puis_reordonne = dump_front(
        {"neuf": "X", "id": "z", "tags": ["premier", "deuxième"], "title": "guillemets simples"},
        FRONT_MIS_EN_FORME,
    )
    assert puis_reordonne.rstrip().endswith("# celui-ci ne précède aucun champ")


# Sans commentaire final, DÉLIBÉRÉMENT : le front matter que rend `split_front` n'a
# pas de saut de ligne final, donc son dernier item n'a pas de séparateur derrière lui.
# Toutes les fixtures ci-dessus finissent par un commentaire de queue, qui en tient
# lieu — et masquait donc le défaut que les deux tests suivants cadrent.
FRONT_FINISSANT_PAR_UN_CHAMP = 'title = "Un essai"\nid = "exemple"'


def test_reordonner_ne_colle_pas_deux_champs() -> None:
    """RÉGRESSION VÉCUE : `migrate` écrivait `id = "exemple"title = "Un essai"` en
    annonçant « 1 changement appliqué » et en rendant 0. Le fichier suivant était
    refusé par tomllib — une donnée valide détruite par un succès annoncé."""
    sortie = dump_front({"id": "exemple", "title": "Un essai"}, FRONT_FINISSANT_PAR_UN_CHAMP)

    assert sortie == 'id = "exemple"\ntitle = "Un essai"'
    assert tomllib.loads(sortie) == {"id": "exemple", "title": "Un essai"}


def test_un_champ_ajoute_ne_se_colle_pas_au_dernier() -> None:
    """Même cause, autre geste : la clé neuve se pose derrière le dernier champ, qui
    n'a pas de séparateur à lui offrir."""
    sortie = dump_front(
        {"title": "Un essai", "id": "exemple", "neuf": "X"}, FRONT_FINISSANT_PAR_UN_CHAMP
    )

    assert tomllib.loads(sortie) == {"title": "Un essai", "id": "exemple", "neuf": "X"}


def test_un_champ_retire_disparait_du_document() -> None:
    """`migrate --drop` retire un champ non déclaré : la reprojection doit le suivre."""
    sortie = dump_front({"id": "z"}, FRONT_MIS_EN_FORME)

    assert "tags" not in sortie and "title" not in sortie


def test_un_champ_ajoute_se_pose_a_la_place_du_contrat() -> None:
    fields = {"id": "z", "neuf": "posé", "tags": ["premier", "deuxième"]}
    sortie = dump_front(fields, FRONT_MIS_EN_FORME)

    assert sortie.index('neuf = "posé"') < sortie.index("tags =")


def test_saut_de_ligne_ecrit_en_chaine_multiligne() -> None:
    """Ce que `dump_value` refuse encore, et qu'il continue de refuser pour les
    contrats : ici la lecture l'accepte déjà, l'écriture le sait maintenant aussi."""
    sortie = dump_front({"texte": "deux\nlignes"})

    assert '"""' in sortie
    assert tomllib.loads(sortie)["texte"] == "deux\nlignes"


def test_saut_de_ligne_dans_une_entree_de_tableau() -> None:
    sortie = dump_front({"liste": ["a\nb", "court"]})

    assert '"""' in sortie
    assert tomllib.loads(sortie)["liste"] == ["a\nb", "court"]


def test_type_hors_contrat_refuse_meme_par_tomlkit() -> None:
    """tomlkit écrirait un dict en table `[x]` sans broncher. Le contrat n'admet
    pas de table : la garde reste à notre charge."""
    with pytest.raises(SerialiseError) as exc:
        _ = dump_front({"champ": {"imbriqué": 1}})
    assert "champ" in str(exc.value)
    assert "dict" in str(exc.value)
