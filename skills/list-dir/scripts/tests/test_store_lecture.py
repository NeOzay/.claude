"""store.py, versant lecture — lire, filtrer, valider.

CE QUE CE FICHIER CADRE, et qui est la raison d'être du contrat :

  · TOUT *.md À LA RACINE EST UN ÉLÉMENT, sans exception. Un README posé là en est
    un, et le contrôle de conservation de `merge` compterait faux sans cette règle.
  · DEUX VERDICTS DE VALIDATION. Sans `filled`, la structure seule — les marqueurs
    sont légitimes sur une fiche fraîchement créée. Avec `filled`, plus aucun
    marqueur là où le contrat exige quelque chose, MAIS jamais de réclamation sur
    ce qu'il dit facultatif.
  · UN FILTRE N'EST PAS UNE RECHERCHE. `where` porte sur les champs déclarés ; un
    champ inconnu est une erreur, pas un résultat vide.
"""

from __future__ import annotations

from pathlib import Path

from jouet import CONTRAT, ecrire, element, monter_liste
from listdir import open_list
from listdir.store import ListStore
from listdir.types import OPTIONAL, PLACEHOLDER


def ouvrir(chemin: Path) -> ListStore:
    return open_list(chemin).unwrap()


def sujets(store: ListStore, filled: bool = False) -> list[str]:
    return [f"{v.subject} — {v.reason}" for v in store.validate(filled=filled).unwrap()]


# ------------------------------------------------------------------- open_list
def test_repertoire_introuvable(tmp_path: Path) -> None:
    r = open_list(tmp_path / "absent")
    assert not r
    assert "répertoire introuvable" in r.message


def test_repertoire_sans_contrat_n_est_pas_une_liste(tmp_path: Path) -> None:
    r = open_list(tmp_path)
    assert not r
    assert "contrat introuvable" in r.message


# ----------------------------------------------------------------------- paths
def test_seuls_les_md_de_la_racine_sont_des_elements(liste: Path) -> None:
    _ = ecrire(liste, ".list/templates/revue.md", "## X\n")
    _ = ecrire(liste, "sous/dossier/autre.md", "## X\n")
    _ = ecrire(liste, "notes.txt", "pas un élément")

    assert [p.name for p in ouvrir(liste).paths()] == ["premier.md"]


def test_un_readme_a_la_racine_est_un_element(liste: Path) -> None:
    """RÈGLE SANS EXCEPTION, et c'est délibéré : le compter à part rendrait le
    contrôle de conservation de merge silencieusement faux."""
    _ = ecrire(liste, "README.md", "## Constat\n\nx\n")
    assert [p.name for p in ouvrir(liste).paths()] == ["README.md", "premier.md"]


def test_les_elements_sont_tries_par_nom(liste_vide: Path) -> None:
    for n in ("c", "a", "b"):
        _ = element(liste_vide, n)
    assert [it.id for it in ouvrir(liste_vide).items().unwrap()] == ["a", "b", "c"]


def test_un_element_illisible_fait_echouer_la_lecture(liste: Path) -> None:
    """Échec fermé : items() ne rend pas « les éléments qui ont bien voulu se lire »."""
    _ = ecrire(liste, "casse.md", "pas de front matter\n")
    r = ouvrir(liste).items()
    assert not r
    assert "front matter absent" in r.message


# ------------------------------------------------------------------------- get
def test_get_rend_l_element(liste: Path) -> None:
    assert ouvrir(liste).get("premier").unwrap().fields["title"] == "Le premier élément"


def test_get_sur_id_inconnu(liste: Path) -> None:
    r = ouvrir(liste).get("absent")
    assert not r
    assert "« absent » introuvable" in r.message


# ----------------------------------------------------------------------- where
def test_where_filtre_sur_un_champ_declare(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'id = "a"\ntitle = "T"\ncategory = "rouge"\n')
    _ = element(liste_vide, "b", 'id = "b"\ntitle = "T"\ncategory = "vert"\n')

    trouves = ouvrir(liste_vide).where(category="rouge").unwrap()
    assert [it.id for it in trouves] == ["a"]


def test_where_cumule_les_criteres(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'id = "a"\ntitle = "T"\ncategory = "rouge"\n')
    _ = element(liste_vide, "b", 'id = "b"\ntitle = "U"\ncategory = "rouge"\n')

    trouves = ouvrir(liste_vide).where(category="rouge", title="U").unwrap()
    assert [it.id for it in trouves] == ["b"]


def test_where_compare_textuellement(liste_vide: Path) -> None:
    """VOULU : un critère marche sans que l'appelant connaisse le type déclaré."""
    _ = element(liste_vide, "a", 'id = "a"\ntitle = "T"\ndate = 2026-08-24\n')
    assert [it.id for it in ouvrir(liste_vide).where(date="2026-08-24").unwrap()] == ["a"]


def test_un_champ_absent_ne_vaut_pas_la_chaine_none(liste_vide: Path) -> None:
    """Il l'a valu : `--where category=None` sélectionnait les éléments SANS category,
    par accident, sans que rien ne le distingue d'une valeur littérale « None »."""
    _ = element(liste_vide, "sans", 'id = "sans"\ntitle = "T"\n')
    _ = element(liste_vide, "avec", 'id = "avec"\ntitle = "T"\ncategory = "None"\n')

    trouves = ouvrir(liste_vide).where(category="None").unwrap()
    assert [it.id for it in trouves] == ["avec"]


def test_le_critere_vide_selectionne_les_champs_absents(liste_vide: Path) -> None:
    """La forme EXPLICITE de « ce champ n'est pas écrit »."""
    _ = element(liste_vide, "sans", 'id = "sans"\ntitle = "T"\n')
    _ = element(liste_vide, "avec", 'id = "avec"\ntitle = "T"\ncategory = "rouge"\n')

    trouves = ouvrir(liste_vide).where(category="").unwrap()
    assert [it.id for it in trouves] == ["sans"]


def test_where_refuse_un_champ_non_declare(liste: Path) -> None:
    """Un champ inconnu est une ERREUR, pas un filtre vide : un résultat vide se
    lirait « aucun élément ne correspond »."""
    r = ouvrir(liste).where(inconnu="x")
    assert not r
    assert "non déclaré au contrat" in r.message
    assert "category" in r.message  # les champs connus sont énumérés


def test_where_sans_critere_rend_tout(liste: Path) -> None:
    assert len(ouvrir(liste).where().unwrap()) == 1


# -------------------------------------------------------------------- validate
def test_liste_vide_est_conforme(liste_vide: Path) -> None:
    """Une liste fraîchement créée est légitimement vide."""
    assert ouvrir(liste_vide).validate().unwrap() == []
    assert ouvrir(liste_vide).validate(filled=True).unwrap() == []


def test_element_conforme_et_rempli(liste: Path) -> None:
    assert sujets(ouvrir(liste)) == []
    assert sujets(ouvrir(liste), filled=True) == []


def test_marqueurs_legitimes_sans_filled(liste_vide: Path) -> None:
    """LE PREMIER VERDICT : une fiche fraîchement créée n'est pas encore instruite."""
    _ = element(
        liste_vide,
        "neuf",
        f'id = "neuf"\ntitle = "{PLACEHOLDER}"\n',
        f"## Constat\n\n{PLACEHOLDER}\n\n## Assumé\n\n{OPTIONAL}\n",
    )
    assert sujets(ouvrir(liste_vide)) == []


def test_filled_reclame_les_requis_restes_au_marqueur(liste_vide: Path) -> None:
    """LE SECOND VERDICT."""
    _ = element(
        liste_vide,
        "neuf",
        f'id = "neuf"\ntitle = "{PLACEHOLDER}"\n',
        f"## Constat\n\n{PLACEHOLDER}\n\n## Assumé\n\n{OPTIONAL}\n",
    )
    trouves = sujets(ouvrir(liste_vide), filled=True)
    assert "champ « title » — à remplir" in trouves
    assert "section « Constat » — à remplir" in trouves


def test_filled_ne_reclame_jamais_un_facultatif(liste_vide: Path) -> None:
    """LE POINT QUI SÉPARE LES DEUX VERDICTS D'UN TROISIÈME QUI N'EXISTE PAS :
    --filled n'exige QUE ce que le contrat exige."""
    _ = element(
        liste_vide,
        "neuf",
        f'id = "neuf"\ntitle = "rempli"\ncategory = "{OPTIONAL}"\n',
        f"## Constat\n\nrempli\n\n## Assumé\n\n{OPTIONAL}\n",
    )
    assert sujets(ouvrir(liste_vide), filled=True) == []


def test_champ_non_declare_est_signale(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'id = "a"\ntitle = "T"\nbizarre = "x"\n')
    assert "champ « bizarre » — non déclaré au contrat" in sujets(ouvrir(liste_vide))


def test_champ_requis_manquant(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'id = "a"\n')
    assert "champ « title » — manquant" in sujets(ouvrir(liste_vide))


def test_champ_facultatif_manquant_ne_gene_pas(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'id = "a"\ntitle = "T"\n')
    assert sujets(ouvrir(liste_vide), filled=True) == []


def test_valeur_hors_contrat_est_signalee(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'id = "a"\ntitle = "T"\ncategory = "bleu"\n')
    assert any("hors des valeurs déclarées" in s for s in sujets(ouvrir(liste_vide)))


def test_id_doit_suivre_le_nom_du_fichier(liste_vide: Path) -> None:
    """Ce contrôle est ce qui empêche un renommage à la main de désolidariser
    l'identifiant de son support."""
    _ = element(liste_vide, "a", 'id = "autre"\ntitle = "T"\n')
    assert "champ « id » — vaut « autre », attendu « a »" in sujets(ouvrir(liste_vide))


def test_section_non_declaree_est_signalee(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", corps="## Constat\n\nx\n\n## Inventée\n\ny\n")
    assert "section « Inventée » — non déclarée au contrat" in sujets(ouvrir(liste_vide))


def test_section_requise_manquante(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", corps="## Assumé\n\nx\n")
    assert "section « Constat » — manquante" in sujets(ouvrir(liste_vide))


def test_section_requise_vide(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", corps="## Constat\n\n\n")
    assert "section « Constat » — vide" in sujets(ouvrir(liste_vide))


def test_fence_ouverte_est_nommee_a_sa_source(liste_vide: Path) -> None:
    """LE DIAGNOSTIC CORRIGÉ : avant, la section avalée était rapportée « manquante »
    alors qu'elle est écrite dans le fichier, et merge annonçait plus loin une perte
    qui n'existait pas."""
    _ = element(liste_vide, "a", corps="## Constat\n\n```\nsans fin\n\n## Assumé\n\ny\n")
    trouves = sujets(ouvrir(liste_vide))

    assert any("jamais refermé" in s for s in trouves)
    assert not any("section « Assumé » — manquante" in s for s in trouves)


def test_check_item_juge_un_element_etranger(liste_vide: Path) -> None:
    """Publique parce que `move` en a besoin : ce que le contrat d'ARRIVÉE exige d'un
    élément écrit pour le contrat de départ."""
    autre = monter_liste(liste_vide.parent / "autre", CONTRAT)
    _ = element(autre, "venu", 'id = "venu"\n')

    etranger = ouvrir(autre).get("venu").unwrap()
    manquements = ouvrir(liste_vide).check_item(etranger)
    assert [f"{v.subject} — {v.reason}" for v in manquements] == ["champ « title » — manquant"]
