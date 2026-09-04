"""Aplatir un contrat, le réécrire, et fusionner trois versions du même.

CE FICHIER NE TOUCHE À AUCUN DISQUE : la fusion est une fonction de trois tables
vers une quatrième, et c'est ce qui la rend testable cas par cas. Ce que `reseed`
en fait — sauvegarder, écrire, rafraîchir la semence — vit dans test_reseed.py.

LA RÈGLE TESTÉE ICI EST « QUI A BOUGÉ », jamais « qui a raison » : c'est elle qui
distingue un apport de définition d'une décision locale, et sans elle toute
évolution de semence se lirait comme un conflit.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from listdir.contract import parse_contract
from listdir.provenance import emit, flatten, fusionner, fusionner_gabarits

CONTRAT = """name = "jouet"
description = "liste-jouet des tests"

[origin]
def = "jouet"
version = 2

[fields.id]
type = "slug"

[fields.category]
type = "enum"
values = ["rouge", "vert"]
description = "la couleur"

[sections."Pour solder"]
required = true
description = "ce qu'il faut faire"

[sections."Constat"]
required = true
description = "ce qui a été observé"
"""


def plat(texte: str) -> dict[str, object]:
    return flatten(tomllib.loads(texte))


def test_aplatir_rend_des_cles_pointees() -> None:
    p = plat(CONTRAT)

    assert p["name"] == "jouet"
    assert p["origin.version"] == 2
    assert p["fields.category.values"] == ["rouge", "vert"]
    assert p['sections."Pour solder".required'] is True


def test_aplatir_ne_remplit_aucun_defaut() -> None:
    """Une clé absente doit le rester : c'est ce qui distingue un apport d'une valeur
    écrite à la main à la même valeur que le défaut."""
    assert "fields.id.required" not in plat(CONTRAT)


def test_un_titre_de_section_portant_un_guillemet_est_echappe() -> None:
    """Enrober ne suffit pas : `[sections."Un " ici"]` est un contrat que `tomllib`
    refuse, et il était écrit sous un code de succès."""
    contrat = CONTRAT + '\n[sections."Un \\" ici"]\nrequired = false\ndescription = ""\n'

    texte = emit(plat(contrat)).unwrap()

    assert plat(texte) == plat(contrat)
    assert parse_contract(texte, Path("x"))


def test_un_titre_de_section_reste_cite() -> None:
    """`[sections.Constat]` est un TOML équivalent mais un octet différent : un contrat
    réémis cessait pour cela seul d'égaler sa semence."""
    # Un titre en un seul mot est le cas qui révèle la règle : `Constat` passe pour un
    # jeton ordinaire, et s'écrivait donc nu.
    assert '[sections."Constat"]' in emit(plat(CONTRAT)).unwrap()
    assert '[sections."Pour solder"]' in emit(plat(CONTRAT)).unwrap()
    assert "[fields.id]" in emit(plat(CONTRAT)).unwrap()


def test_aller_retour_de_l_emetteur() -> None:
    """Ce qui est émis doit se relire à l'identique, sinon `reseed` produirait un
    contrat qu'aucune commande ne saurait appliquer."""
    texte = emit(plat(CONTRAT)).unwrap()

    assert plat(texte) == plat(CONTRAT)
    assert parse_contract(texte, Path("x")).unwrap() == parse_contract(CONTRAT, Path("x")).unwrap()


def test_la_semence_gagne_quand_le_local_n_a_pas_bouge() -> None:
    base = plat(CONTRAT)
    local = plat(CONTRAT)
    semence = plat(CONTRAT.replace("version = 2", "version = 3"))

    f = fusionner(base, local, semence)

    assert f.conflits == []
    assert f.plat["origin.version"] == 3
    assert any("origin.version" in c for c in f.changements)


def test_le_local_reste_quand_la_semence_n_a_pas_bouge() -> None:
    base = plat(CONTRAT)
    local = plat(CONTRAT.replace('description = "la couleur"', 'description = "la teinte"'))
    semence = plat(CONTRAT)

    f = fusionner(base, local, semence)

    assert f.conflits == []
    assert f.plat["fields.category.description"] == "la teinte"
    assert f.changements == []


def test_les_deux_ont_bouge_est_un_conflit_nomme() -> None:
    base = plat(CONTRAT)
    local = plat(CONTRAT.replace('description = "la couleur"', 'description = "la teinte"'))
    semence = plat(CONTRAT.replace('description = "la couleur"', 'description = "le ton"'))

    f = fusionner(base, local, semence)

    assert f.conflits == ["fields.category.description — modifiée des deux côtés"]


def test_une_cle_retiree_de_la_semence_est_gardee_sans_etre_rapportee() -> None:
    """Même règle que `migrate` : rien n'est supprimé de son propre chef. Et rien n'est
    rapporté non plus — la garder décrit un état qui persistera au prochain appel, que
    `validate` dit une fois pour toutes au lieu que `reseed` le rejoue sans fin."""
    base = plat(CONTRAT)
    local = plat(CONTRAT)
    semence = plat(CONTRAT.replace('description = "la couleur"\n', ""))

    f = fusionner(base, local, semence)

    assert f.conflits == []
    assert f.plat["fields.category.description"] == "la couleur"
    assert f.changements == []


def test_une_cle_neuve_de_la_semence_est_posee() -> None:
    base = plat(CONTRAT)
    local = plat(CONTRAT)
    semence = plat(CONTRAT + '\n[fields.reviewed]\ntype = "date"\n')

    f = fusionner(base, local, semence)

    assert f.plat["fields.reviewed.type"] == "date"
    assert any("posée de la semence" in c for c in f.changements)


def test_sans_base_seul_le_manquant_est_injecte() -> None:
    """Mode adoption : une liste antérieure n'a pas de point de référence."""
    local = plat(CONTRAT.replace('description = "la couleur"', 'description = "la teinte"'))
    semence = plat(CONTRAT + '\n[fields.reviewed]\ntype = "date"\n')

    f = fusionner({}, local, semence)

    assert f.plat["fields.reviewed.type"] == "date"
    assert f.conflits == ["fields.category.description — modifiée des deux côtés"]


def test_sans_base_une_liste_identique_ne_produit_rien() -> None:
    local = plat(CONTRAT)

    f = fusionner({}, local, plat(CONTRAT))

    assert (f.conflits, f.changements) == ([], [])
    assert f.plat == local


def test_l_ordre_emis_est_celui_de_la_semence_puis_du_local() -> None:
    """Un contrat rattrapé doit se relire comme sa définition."""
    local = plat(CONTRAT + '\n[fields.propre]\ntype = "text"\n')
    semence = plat(CONTRAT + '\n[fields.reviewed]\ntype = "date"\n')

    f = fusionner(plat(CONTRAT), local, semence)

    cles = [c for c in f.plat if c.startswith("fields.")]
    assert cles.index("fields.reviewed.type") < cles.index("fields.propre.type")


def test_les_gabarits_se_fusionnent_par_fichier_entier() -> None:
    """Une prose libre n'a pas de clés : deux versions d'un paragraphe ne se
    recollent pas ligne à ligne sans inventer un texte que personne n'a écrit."""
    base = {"revue.md": "## Revue\n"}
    local = {"revue.md": "## Revue\n", "propre.md": "## Local\n"}
    semence = {"revue.md": "## Revue remaniée\n"}

    fusionnes, changements, conflits = fusionner_gabarits(base, local, semence)

    assert conflits == []
    assert fusionnes == {"revue.md": "## Revue remaniée\n", "propre.md": "## Local\n"}
    assert any("gabarit revue.md" in c for c in changements)


def test_un_gabarit_modifie_des_deux_cotes_est_un_conflit() -> None:
    base = {"revue.md": "## Revue\n"}
    local = {"revue.md": "## Revue locale\n"}
    semence = {"revue.md": "## Revue remaniée\n"}

    _, _, conflits = fusionner_gabarits(base, local, semence)

    assert conflits == ["gabarit revue.md — modifiée des deux côtés"]


def test_une_cle_supprimee_localement_reste_supprimee() -> None:
    """La suppression est une modification comme une autre : seul le local a bougé,
    donc le local gagne — et ce que gagne une absence est de rester absente."""
    base = plat(CONTRAT)
    local = plat(CONTRAT.replace('description = "la couleur"\n', ""))
    semence = plat(CONTRAT)

    f = fusionner(base, local, semence)

    assert f.conflits == []
    assert "fields.category.description" not in f.plat
    # Et rien n'est rapporté : ce que le local a décidé seul décrit un état durable,
    # pas un changement du re-semis. Le signaler ferait annoncer un changement à
    # chaque appel sur une liste qui n'en subit aucun.
    assert f.changements == []


def test_une_cle_supprimee_localement_et_modifiee_dans_la_semence_est_un_conflit() -> None:
    base = plat(CONTRAT)
    local = plat(CONTRAT.replace('description = "la couleur"\n', ""))
    semence = plat(CONTRAT.replace('description = "la couleur"', 'description = "le ton"'))

    assert fusionner(base, local, semence).conflits == [
        "fields.category.description — modifiée des deux côtés"
    ]


def test_un_gabarit_supprime_localement_reste_supprime() -> None:
    base = {"revue.md": "## Revue\n"}
    local: dict[str, str] = {}
    semence = {"revue.md": "## Revue\n"}

    fusionnes, _, conflits = fusionner_gabarits(base, local, semence)

    assert (fusionnes, conflits) == ({}, [])


def test_l_emetteur_refuse_ce_qui_ne_s_ecrit_pas_au_lieu_de_l_ecrire() -> None:
    """Ce qu'`emit` produit est ÉCRIT : un refus du sérialiseur doit devenir un échec
    nommé, pas un traceback (valeur hors contrat) ni un fichier cassé sous un code 0
    (caractère de contrôle dans un titre)."""
    hors_contrat = fusionner({}, {}, {**plat(CONTRAT), "fields.seuil.type": 1.5})
    titre = CONTRAT + '\n[sections."Un \\u0007 ici"]\ndescription = ""\n'
    controle = fusionner({}, {}, plat(titre))

    for fusion in (hors_contrat, controle):
        r = emit(fusion.plat)
        assert not r
        assert "inécrivable" in r.message


def test_une_cle_terminale_exotique_traverse_l_aller_retour() -> None:
    """R16 : la clé d'un `[fields.*]` vient d'un contrat écrit à la main, où
    `parse_contract` tolère l'inconnu. Écrite brute, `ma cle = "x"` n'était plus du
    TOML — et `note.libre` était pire : le contrat réémis portait une table
    `[fields.id.note]` que personne n'avait écrite, et `validate` la trouvait bonne."""
    contrat = CONTRAT + '\n[fields.exotique]\ntype = "text"\n"ma cle" = "x"\n"note.libre" = "y"\n'

    texte = emit(plat(contrat)).unwrap()

    assert plat(texte) == plat(contrat)
    assert "fields.id.note" not in texte
    assert parse_contract(texte, Path("x"))


def test_une_cle_terminale_a_caractere_de_controle_est_refusee() -> None:
    contrat = CONTRAT + '\n[fields.exotique]\ntype = "text"\n"cl\\u0007e" = "x"\n'

    r = emit(plat(contrat))

    assert not r
    assert "inécrivable" in r.message


def test_une_cle_exotique_traverse_l_aller_retour_a_tous_les_etages() -> None:
    """R14, R16, R17 : la même faute à trois étages. Un nom entre par un contrat écrit
    à la main — `parse_contract` ne refuse l'inconnu que dans `[origin]` — et ressort
    par l'écriture. Ce test les tient tous les trois d'un coup."""
    contrat = (
        '"ma cle" = "premier niveau"\n'
        '"note.libre" = "point au premier niveau"\n'
        + CONTRAT
        + '\n[fields."champ exotique"]\ntype = "text"\n"sous cle" = "x"\n"sous.point" = "y"\n'
        + '\n[sections."Un \\" ici"]\ndescription = ""\n'
    )

    texte = emit(plat(contrat)).unwrap()

    assert plat(texte) == plat(contrat)
    assert parse_contract(texte, Path("x"))
    assert tomllib.loads(texte).keys() == tomllib.loads(contrat).keys()


def test_une_table_inconnue_est_nommee_table_et_la_sortie_est_dite() -> None:
    """R18 : le sérialiseur disait « champ … : type dict hors contrat » — le mot est
    faux, et rien n'indiquait comment débloquer un re-semis devenu impossible."""
    r = emit(plat(CONTRAT + "\n[extra]\nquoi = 1\n"))

    assert not r
    assert "table « extra »" in r.message
    assert "retirer" in r.message


def test_le_message_montre_le_caractere_de_controle_qu_il_denonce() -> None:
    """R19 : « clé « macle » » pour `ma\\x07cle` faisait chercher une clé inexistante."""
    r = emit({"ma\x07cle": "x"})

    assert not r
    assert "ma\\u0007cle" in r.message
