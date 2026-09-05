"""store.py — projeter une liste sur une liste neuve, agglomérer une liste en document.

CE QUE CE FICHIER CADRE :

  · `derive` N'EST PAS UNE COPIE. Chaque élément source engendre une fiche de même
    `id`, mais son corps vient du moule — jamais de la source. Une fiche qui
    porterait la prose de l'élément qu'elle instruit en serait un doublon éditable,
    et la source unique serait perdue. Le seul emprunt est déclaratif : un champ
    portant `from`.
  · TOUT EST CONSTRUIT EN MÉMOIRE D'ABORD. Un gabarit incohérent découvert après un
    mkdir laisserait une destination à moitié bâtie, que la tentative suivante
    refuserait comme « existe déjà » — l'utilisateur coincé entre une erreur qu'il a
    corrigée et un répertoire qu'il n'a pas créé.
  · `merge` VÉRIFIE LA CONSERVATION sur le texte rendu, hors blocs de code. Compter
    sur la liste qui a servi à l'écrire ne prouverait rien ; compter sans la règle
    des fences faisait échouer toute preuve exécutée collée, avec un diagnostic faux.
"""

from __future__ import annotations

from pathlib import Path

from jouet import GABARIT_TOML, ecrire, element, monter_gabarit
from listdir import open_list
from listdir.contract import load_contract
from listdir.provenance import warnings
from listdir.store import ListStore
from listdir.types import OPTIONAL, PLACEHOLDER


def ouvrir(chemin: Path) -> ListStore:
    return open_list(chemin).unwrap()


# --------------------------------------------------------------------- template
def test_gabarit_complet_est_lu(liste: Path) -> None:
    contrat, sections = ouvrir(monter_gabarit(liste)).template("revue").unwrap()
    assert 'name = "revue"' in contrat
    assert list(sections) == ["Avis", "Remarque"]


def test_le_front_matter_du_moule_est_ignore(liste: Path) -> None:
    """Seules ses SECTIONS comptent : le front matter d'une fiche vient du contrat
    cible, pour ne pas tenir la même liste de champs dans le .toml et dans le .md."""
    _, sections = ouvrir(monter_gabarit(liste)).template("revue").unwrap()
    assert "un front matter que derive ignore" not in "".join(sections)


def test_gabarit_a_moitie_present_nomme_le_fichier_manquant(liste: Path) -> None:
    _ = ecrire(liste, ".list/templates/revue.toml", GABARIT_TOML)
    r = ouvrir(liste).template("revue")

    assert not r
    assert "revue.md" in r.message
    assert "incomplet" in r.message


def test_gabarit_inconnu(liste: Path) -> None:
    r = ouvrir(monter_gabarit(liste)).template("absent")
    assert not r
    assert "absent" in r.message


# ----------------------------------------------------------------------- derive
def test_derive_engendre_une_fiche_par_element(liste: Path, tmp_path: Path) -> None:
    _ = element(liste, "second")
    cible = tmp_path / "revues"

    derivee = ouvrir(monter_gabarit(liste)).derive(cible, "revue").unwrap()
    assert [p.name for p in derivee.paths()] == ["premier.md", "second.md"]


def test_le_corps_vient_du_moule_jamais_de_la_source(liste: Path, tmp_path: Path) -> None:
    """LE POINT CENTRAL : sans cela la fiche serait un doublon éditable de la source."""
    derivee = ouvrir(monter_gabarit(liste)).derive(tmp_path / "revues", "revue").unwrap()
    fiche = derivee.get("premier").unwrap()

    assert list(fiche.sections) == ["Avis", "Remarque"]
    assert "Ce qui a été constaté" not in "".join(fiche.sections.values())
    assert fiche.sections["Avis"] == PLACEHOLDER


def test_un_champ_portant_from_recoit_la_valeur_source(liste: Path, tmp_path: Path) -> None:
    derivee = ouvrir(monter_gabarit(liste)).derive(tmp_path / "revues", "revue").unwrap()
    assert derivee.get("premier").unwrap().fields["title"] == "Le premier élément"


def test_un_champ_sans_from_recoit_son_marqueur(liste: Path, tmp_path: Path) -> None:
    derivee = ouvrir(monter_gabarit(liste)).derive(tmp_path / "revues", "revue").unwrap()
    assert derivee.get("premier").unwrap().fields["verdict"] == PLACEHOLDER


def test_un_champ_sans_from_mais_preremplissable_recoit_sa_valeur(
    liste: Path, tmp_path: Path
) -> None:
    """MÊME RÈGLE QU'À LA CRÉATION : un champ du contrat cible sans `from`, mais
    portant `text`/`command`, reçoit cette valeur — pas son marqueur."""
    contrat = GABARIT_TOML.replace(
        '[fields.verdict]\ntype = "text"\nrequired = true\n',
        '[fields.verdict]\ntype = "text"\nrequired = true\ntext = "Non instruit."\n',
    )
    derivee = (
        ouvrir(monter_gabarit(liste, contrat=contrat)).derive(tmp_path / "revues", "revue").unwrap()
    )

    assert derivee.get("premier").unwrap().fields["verdict"] == "Non instruit."


def test_un_champ_sans_from_portant_command_recoit_la_sortie(liste: Path, tmp_path: Path) -> None:
    """LE CWD DES COMMANDES N'EST PAS LA DESTINATION : `derive` calcule tout en
    mémoire avant d'écrire, et sa destination n'existe donc pas encore. Une
    commande lancée depuis ce répertoire échouerait sur chaque champ prérempli."""
    contrat = GABARIT_TOML.replace(
        '[fields.verdict]\ntype = "text"\nrequired = true\n',
        '[fields.verdict]\ntype = "text"\nrequired = true\ncommand = "echo instruit"\n',
    )
    derivee = (
        ouvrir(monter_gabarit(liste, contrat=contrat)).derive(tmp_path / "revues", "revue").unwrap()
    )

    assert derivee.get("premier").unwrap().fields["verdict"] == "instruit"


def test_une_command_qui_echoue_en_derive_n_ecrit_rien(liste: Path, tmp_path: Path) -> None:
    contrat = GABARIT_TOML.replace(
        '[fields.verdict]\ntype = "text"\nrequired = true\n',
        '[fields.verdict]\ntype = "text"\nrequired = true\ncommand = "false"\n',
    )
    cible = tmp_path / "revues"

    r = ouvrir(monter_gabarit(liste, contrat=contrat)).derive(cible, "revue")

    assert not r
    assert "false" in r.message
    assert not cible.exists()


def test_id_est_reporte_d_office(liste: Path, tmp_path: Path) -> None:
    """Le seul lien entre une fiche et l'élément qu'elle instruit."""
    derivee = ouvrir(monter_gabarit(liste)).derive(tmp_path / "revues", "revue").unwrap()
    assert derivee.get("premier").unwrap().fields["id"] == "premier"


def test_une_liste_derivee_est_conforme_et_pas_remplie(liste: Path, tmp_path: Path) -> None:
    derivee = ouvrir(monter_gabarit(liste)).derive(tmp_path / "revues", "revue").unwrap()

    assert derivee.validate().unwrap() == []
    assert derivee.validate(filled=True).unwrap() != []


def test_une_derivee_d_un_gabarit_estampille_ne_dit_rien(liste: Path, tmp_path: Path) -> None:
    """C'est le symptôme qui a ouvert ce chantier : une liste de revue naissait sans
    provenance, et `validate` réclamait à chaque fois une adoption qui n'a pas de sens
    sur une liste jetable. L'estampille voyage avec le gabarit, comme toute estampille
    voyage avec sa semence — `derive` n'en écrit pas une ligne."""
    estampille = '\n[origin]\ndef = "jouet/revue"\nversion = 1\nfrozen = true\n'
    source = monter_gabarit(liste, contrat=GABARIT_TOML + estampille)
    derivee = ouvrir(source).derive(tmp_path / "revues", "revue").unwrap()

    contrat = load_contract(derivee.path).unwrap()
    origin = contrat.origin
    assert origin is not None
    assert (origin.definition, origin.template) == ("jouet", "revue")
    assert warnings(derivee.path, contrat) == []


def test_une_derivee_sans_estampille_reclame_toujours_une_adoption(
    liste: Path, tmp_path: Path
) -> None:
    """Le pendant : rien n'est posé d'office. Un gabarit muet sème une liste muette,
    et c'est l'avertissement d'adoption qui le dit."""
    derivee = ouvrir(monter_gabarit(liste)).derive(tmp_path / "revues", "revue").unwrap()

    dits = warnings(derivee.path, load_contract(derivee.path).unwrap())
    assert any("aucune provenance déclarée" in d for d in dits)


def test_from_qui_ne_nomme_aucun_champ_source(liste: Path, tmp_path: Path) -> None:
    faux = GABARIT_TOML.replace('from = "title"', 'from = "inexistant"')
    _ = monter_gabarit(liste, contrat=faux)
    cible = tmp_path / "revues"

    r = ouvrir(liste).derive(cible, "revue")

    assert not r
    assert "inexistant" in r.message


def test_un_echec_ne_laisse_aucune_destination(liste: Path, tmp_path: Path) -> None:
    """L'ATOMICITÉ : sinon la tentative suivante refuserait un répertoire que
    l'utilisateur n'a pas créé, après qu'il a corrigé son erreur."""
    faux = GABARIT_TOML.replace('from = "title"', 'from = "inexistant"')
    _ = monter_gabarit(liste, contrat=faux)
    cible = tmp_path / "revues"

    assert not ouvrir(liste).derive(cible, "revue")
    assert not cible.exists()


def test_un_gabarit_au_contrat_incoherent_ne_cree_rien(liste: Path, tmp_path: Path) -> None:
    _ = monter_gabarit(liste, contrat='name = "revue"\n\n[fields.c]\ntype = "enum"\n')
    cible = tmp_path / "revues"

    r = ouvrir(liste).derive(cible, "revue")

    assert not r
    assert "n'admet rien" in r.message
    assert not cible.exists()


def test_destination_existante_refusee(liste: Path, tmp_path: Path) -> None:
    """derive ne fusionne ni ne met à jour : écraser ferait disparaître un travail fait."""
    cible = tmp_path / "revues"
    cible.mkdir()
    r = ouvrir(monter_gabarit(liste)).derive(cible, "revue")

    assert not r
    assert "ne fusionne ni ne met à jour" in r.message


def test_liste_source_vide_refusee(liste_vide: Path, tmp_path: Path) -> None:
    r = ouvrir(monter_gabarit(liste_vide)).derive(tmp_path / "revues", "revue")
    assert not r
    assert "il n'y a rien à projeter" in r.message


# -------------------------------------------------------------------- merge_text
def test_liste_vide_refusee(liste_vide: Path) -> None:
    """Agglomérer zéro sans broncher se lirait « rien à traiter »."""
    r = ouvrir(liste_vide).merge_text()
    assert not r
    assert "agglomérer zéro n'est pas un résultat" in r.message


def test_un_marqueur_restant_fait_echouer(liste_vide: Path) -> None:
    """merge exige --filled : un rapport contenant un marqueur se lirait comme
    instruit alors qu'il ne l'est pas."""
    _ = element(liste_vide, "a", f'id = "a"\ntitle = "{PLACEHOLDER}"\n')
    r = ouvrir(liste_vide).merge_text()

    assert not r
    assert "à compléter avant d'agglomérer" in r.message


def test_le_rendu_est_titre_puis_elements(liste: Path) -> None:
    document = ouvrir(liste).merge_text().unwrap()

    assert document.startswith("# jouet\n")
    assert "\n## Le premier élément\n" in document
    assert "\n### Constat\n" in document


def test_les_sections_sont_decalees_d_un_niveau(liste: Path) -> None:
    """SANS CE DÉCALAGE, `grep -c '^## '` compterait les sections en plus des
    éléments, vidant de sens le contrôle de conservation."""
    document = ouvrir(liste).merge_text().unwrap()
    assert "\n## Constat\n" not in document


def test_le_titre_du_bloc_vient_du_champ_title(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'id = "a"\ntitle = "Un titre porté"\n')
    assert "## Un titre porté" in ouvrir(liste_vide).merge_text().unwrap()


def test_sans_title_le_bloc_porte_l_id(liste_vide: Path) -> None:
    sans_titre = (
        'name = "n"\n\n[fields.id]\ntype = "slug"\n\n'
        '[sections."Constat"]\nrequired = true\ndescription = ""\n'
    )
    _ = ecrire(liste_vide, ".list/contract.toml", sans_titre)
    _ = element(liste_vide, "a", 'id = "a"\n')
    assert "## a" in ouvrir(liste_vide).merge_text().unwrap()


def test_une_section_restee_au_marqueur_facultatif_est_omise(liste: Path) -> None:
    """Elle a joué son rôle — guider — et n'a rien à dire ici. L'y laisser
    constellerait le rapport de vides."""
    document = ouvrir(liste).merge_text().unwrap()

    assert "### Assumé" not in document
    assert OPTIONAL not in document


def test_conservation_verifiee_sur_le_texte_rendu(liste_vide: Path) -> None:
    for n in ("a", "b", "c"):
        _ = element(liste_vide, n, f'id = "{n}"\ntitle = "T{n}"\n')
    document = ouvrir(liste_vide).merge_text().unwrap()

    assert document.count("\n## ") == 3
    assert "3 élément(s) aggloméré(s), 3 fichier(s)" in document


def test_un_titre_de_niveau_deux_dans_un_bloc_de_code_ne_compte_pas(liste_vide: Path) -> None:
    """LE DÉFAUT CORRIGÉ AVANT CE CHANTIER : le flux de revue échouait sur toute
    preuve exécutée collée, en annonçant une perte qui n'existait pas."""
    for n in ("a", "b"):
        _ = element(liste_vide, n, f'id = "{n}"\ntitle = "T{n}"\n')
    _ = element(
        liste_vide,
        "c",
        'id = "c"\ntitle = "Tc"\n',
        "## Constat\n\n```\n$ une commande\n## une sortie collée\n```\n",
    )

    document = ouvrir(liste_vide).merge_text().unwrap()
    assert "3 élément(s) aggloméré(s), 3 fichier(s)" in document
    assert "## une sortie collée" in document


# -------------------------------------------------------------------------- merge
def test_merge_ecrit_le_fichier(liste: Path, tmp_path: Path) -> None:
    cible = tmp_path / "sortie/rapport.md"
    ecrit = ouvrir(liste).merge(cible).unwrap()

    assert ecrit == cible
    assert cible.read_text(encoding="utf-8") == ouvrir(liste).merge_text().unwrap()


def test_merge_cree_les_repertoires_manquants(liste: Path, tmp_path: Path) -> None:
    cible = tmp_path / "a/b/c/rapport.md"
    _ = ouvrir(liste).merge(cible).unwrap()
    assert cible.is_file()


def test_merge_n_ecrit_rien_quand_l_agglomeration_echoue(liste_vide: Path, tmp_path: Path) -> None:
    cible = tmp_path / "rapport.md"
    assert not ouvrir(liste_vide).merge(cible)
    assert not cible.exists()
