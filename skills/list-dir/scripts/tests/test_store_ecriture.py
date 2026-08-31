"""store.py, versant écriture — créer un élément, migrer une liste, créer une liste.

CE QUE CE FICHIER CADRE :

  · `create` pose TOUT le contrat, facultatifs compris — ce qu'on ne voit pas n'est
    jamais rempli, et c'est un modèle qui remplira ce fichier.
  · `migrate` fait de la STRUCTURE, et rien d'autre : elle pose ce qui manque au
    marqueur et remet dans l'ordre. Elle ne renomme rien, ne reporte rien, ne
    supprime rien de son propre chef — décider que `severite` est devenu `gravite`,
    c'est juger, et un script qui juge est la ligne que ce dispositif ne franchit pas.
  · MIGRER EST REJOUABLE, et un élément déjà conforme n'est PAS réécrit : le
    réécrire pour rien lui coûterait son `raw_front`, donc l'aller-retour octet.
  · `init_list` fait passer ses deux valeurs libres par le sérialiseur. Un `--name`
    contenant un guillemet produisait un contrat que `tomllib` refuse — en rendant 0.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import cast

from jouet import CONTRAT, GABARIT_MD, GABARIT_TOML, ecrire, element, monter_liste
from listdir import open_list
from listdir.store import ListStore, init_list
from listdir.types import OPTIONAL, PLACEHOLDER, Change


def ouvrir(chemin: Path) -> ListStore:
    return open_list(chemin).unwrap()


def actes(changes: list[Change]) -> list[str]:
    return [f"{c.path.name}: {c.subject} — {c.action}" for c in changes]


# ---------------------------------------------------------------------- create
def test_create_pose_tout_le_contrat(liste_vide: Path) -> None:
    """Requis ET facultatifs : ce qu'on ne voit pas n'est jamais rempli."""
    item = ouvrir(liste_vide).create("neuf").unwrap()

    assert list(item.fields) == ["id", "title", "date", "category", "tags"]
    assert list(item.sections) == ["Constat", "Assumé"]


def test_create_pose_le_marqueur_de_chaque_statut(liste_vide: Path) -> None:
    item = ouvrir(liste_vide).create("neuf").unwrap()

    assert item.fields["title"] == PLACEHOLDER  # requis
    assert item.fields["category"] == OPTIONAL  # facultatif
    assert item.sections["Constat"] == PLACEHOLDER
    assert item.sections["Assumé"] == OPTIONAL


def test_create_pose_id_au_nom_du_fichier(liste_vide: Path) -> None:
    """`id` n'a jamais de marqueur : c'est le seul lien entre l'élément et son support."""
    item = ouvrir(liste_vide).create("neuf").unwrap()
    assert item.fields["id"] == "neuf"
    assert item.path.name == "neuf.md"


def test_create_accepte_des_valeurs_d_emblee(liste_vide: Path) -> None:
    item = ouvrir(liste_vide).create("neuf", title="Un titre").unwrap()
    assert item.fields["title"] == "Un titre"


def test_create_refuse_d_ecraser(liste: Path) -> None:
    r = ouvrir(liste).create("premier")
    assert not r
    assert "existe déjà" in r.message


def test_un_element_cree_est_conforme_mais_pas_rempli(liste_vide: Path) -> None:
    """LA JONCTION DES DEUX VERDICTS : une fiche neuve passe validate, et échoue
    sous --filled. C'est ce qui rend le préremplissage utilisable."""
    store = ouvrir(liste_vide)
    _ = store.write(store.create("neuf").unwrap()).unwrap()

    assert ouvrir(liste_vide).validate().unwrap() == []
    assert ouvrir(liste_vide).validate(filled=True).unwrap() != []


# --------------------------------------------------------------------- migrate
def test_liste_deja_conforme_ne_change_rien(liste: Path) -> None:
    avant = (liste / "premier.md").read_text(encoding="utf-8")
    changes = ouvrir(liste).migrate().unwrap()

    assert changes == []
    assert (liste / "premier.md").read_text(encoding="utf-8") == avant


def test_champ_manquant_est_ajoute_au_marqueur(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'id = "a"\n')
    changes = ouvrir(liste_vide).migrate().unwrap()

    assert f"a.md: champ « title » — ajouté, {PLACEHOLDER}" in actes(changes)
    assert ouvrir(liste_vide).get("a").unwrap().fields["title"] == PLACEHOLDER


def test_section_manquante_est_ajoutee_au_marqueur(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", corps="## Constat\n\nx\n")
    changes = ouvrir(liste_vide).migrate().unwrap()

    assert f"a.md: section « Assumé » — ajoutée, {OPTIONAL}" in actes(changes)


def test_id_est_pose_au_nom_du_fichier_jamais_au_marqueur(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'title = "T"\n')
    changes = ouvrir(liste_vide).migrate().unwrap()

    assert "a.md: champ « id » — posé à « a »" in actes(changes)
    assert ouvrir(liste_vide).get("a").unwrap().fields["id"] == "a"


def test_champs_reordonnes_selon_le_contrat(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'title = "T"\nid = "a"\n')
    changes = ouvrir(liste_vide).migrate().unwrap()

    assert "a.md: front matter — champs réordonnés selon le contrat" in actes(changes)
    assert list(ouvrir(liste_vide).get("a").unwrap().fields)[:2] == ["id", "title"]


def test_sections_reordonnees_selon_le_contrat(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", corps="## Assumé\n\ny\n\n## Constat\n\nx\n")
    changes = ouvrir(liste_vide).migrate().unwrap()

    assert "a.md: corps — sections réordonnées selon le contrat" in actes(changes)
    assert list(ouvrir(liste_vide).get("a").unwrap().sections) == ["Constat", "Assumé"]


def test_valeur_deja_ecrite_n_est_jamais_touchee(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'id = "a"\ntitle = "Un titre tenu"\n')
    _ = ouvrir(liste_vide).migrate().unwrap()

    assert ouvrir(liste_vide).get("a").unwrap().fields["title"] == "Un titre tenu"


def test_migration_rejouable(liste_vide: Path) -> None:
    """REJOUABLE : c'est ce qui permet de relancer après une écriture interrompue."""
    _ = element(liste_vide, "a", 'id = "a"\n')
    _ = ouvrir(liste_vide).migrate().unwrap()

    apres = (liste_vide / "a.md").read_text(encoding="utf-8")
    seconde = ouvrir(liste_vide).migrate().unwrap()

    assert seconde == []
    assert (liste_vide / "a.md").read_text(encoding="utf-8") == apres


def test_champ_non_declare_est_conserve_et_signale_sans_ecriture(liste_vide: Path) -> None:
    """LE POINT LE PLUS FIN : une REMARQUE ne fait rien écrire. Réécrire un élément
    que la migration n'a pas eu à changer lui coûterait son raw_front pour rien."""
    # L'élément est DÉJÀ CONFORME par ailleurs : sans cela les ajouts légitimes
    # noieraient la remarque, et le test ne prouverait plus rien sur elle.
    _ = element(
        liste_vide,
        "a",
        'id = "a"\ntitle = "T"\ndate = 2026-08-24\ncategory = "rouge"\n'
        'tags = ["x"]\nbizarre = "gardé"\n',
        "## Constat\n\nx\n\n## Assumé\n\ny\n",
    )
    avant = (liste_vide / "a.md").read_text(encoding="utf-8")

    changes = ouvrir(liste_vide).migrate().unwrap()

    assert [c.applied for c in changes] == [False]
    assert "conservé — non déclaré au contrat (voir --drop)" in changes[0].action
    assert (liste_vide / "a.md").read_text(encoding="utf-8") == avant


def test_drop_retire_ce_que_le_contrat_ne_declare_plus(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'id = "a"\ntitle = "T"\nbizarre = "x"\n')
    changes = ouvrir(liste_vide).migrate(drop=True).unwrap()

    assert "a.md: champ « bizarre » — retiré — non déclaré au contrat" in actes(changes)
    assert "bizarre" not in ouvrir(liste_vide).get("a").unwrap().fields


def test_section_non_declaree_conservee_puis_retiree_par_drop(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", corps="## Constat\n\nx\n\n## Inventée\n\ny\n")

    gardee = ouvrir(liste_vide).migrate().unwrap()
    assert any("conservée — non déclarée au contrat" in c.action for c in gardee)
    assert "Inventée" in ouvrir(liste_vide).get("a").unwrap().sections

    retiree = ouvrir(liste_vide).migrate(drop=True).unwrap()
    assert any("retirée — non déclarée au contrat" in c.action for c in retiree)
    assert "Inventée" not in ouvrir(liste_vide).get("a").unwrap().sections


def test_dry_run_n_ecrit_rien(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'id = "a"\n')
    avant = (liste_vide / "a.md").read_text(encoding="utf-8")

    changes = ouvrir(liste_vide).migrate(dry_run=True).unwrap()

    assert changes != []
    assert (liste_vide / "a.md").read_text(encoding="utf-8") == avant


def test_dry_run_annonce_ce_que_la_migration_ferait(liste_vide: Path) -> None:
    _ = element(liste_vide, "a", 'id = "a"\n')
    sec = ouvrir(liste_vide).migrate(dry_run=True).unwrap()
    reel = ouvrir(liste_vide).migrate().unwrap()
    assert actes(sec) == actes(reel)


def test_migration_echoue_sur_un_element_illisible(liste_vide: Path) -> None:
    """Tout est calculé avant la moindre écriture : une migration qui échouerait à
    mi-parcours laisserait la liste dans un état qu'aucun contrat ne décrit."""
    _ = element(liste_vide, "bon", 'id = "bon"\n')
    _ = ecrire(liste_vide, "casse.md", "pas de front matter\n")
    avant = (liste_vide / "bon.md").read_text(encoding="utf-8")

    r = ouvrir(liste_vide).migrate()
    assert not r
    assert (liste_vide / "bon.md").read_text(encoding="utf-8") == avant


# ------------------------------------------------------------------- init_list
def test_init_cree_un_contrat_lisible(tmp_path: Path) -> None:
    cible = init_list(tmp_path / "neuve").unwrap()
    donnees = tomllib.loads(cible.read_text(encoding="utf-8"))

    assert cible == tmp_path / "neuve/.list/contract.toml"
    assert donnees["name"] == "neuve"


def test_init_ouvre_une_liste_valide(tmp_path: Path) -> None:
    _ = init_list(tmp_path / "neuve").unwrap()
    assert open_list(tmp_path / "neuve").unwrap().contract.name == "neuve"


def test_init_porte_nom_et_description(tmp_path: Path) -> None:
    _ = init_list(tmp_path / "neuve", "Ma liste", "à quoi elle sert").unwrap()
    contrat = open_list(tmp_path / "neuve").unwrap().contract

    assert contrat.name == "Ma liste"
    assert contrat.description == "à quoi elle sert"


def test_un_guillemet_dans_le_nom_ne_casse_plus_le_contrat(tmp_path: Path) -> None:
    """LA RÉGRESSION À NE PLUS JAMAIS REVOIR : interpolé, ce nom produisait un contrat
    que tomllib refuse — et init rendait 0. Un échec ouvert, exactement ce que ce
    paquet existe pour supprimer. Le guillemet est un caractère de nom ordinaire."""
    cible = init_list(tmp_path / "neuve", 'ma "liste"').unwrap()

    donnees = tomllib.loads(cible.read_text(encoding="utf-8"))
    assert donnees["name"] == 'ma "liste"'
    assert open_list(tmp_path / "neuve").unwrap().contract.name == 'ma "liste"'


def test_un_saut_de_ligne_dans_la_description_reste_relisible(tmp_path: Path) -> None:
    cible = init_list(tmp_path / "neuve", "n", "deux\nlignes").unwrap()
    assert tomllib.loads(cible.read_text(encoding="utf-8"))["description"] == "deux\nlignes"


def test_un_caractere_de_controle_est_refuse_et_nomme(tmp_path: Path) -> None:
    r = init_list(tmp_path / "neuve", "ma\x00liste")
    assert not r
    assert "U+0000" in r.message
    assert not (tmp_path / "neuve/.list/contract.toml").exists()


def test_init_refuse_une_liste_deja_montee(tmp_path: Path) -> None:
    cible = monter_liste(tmp_path / "deja", CONTRAT)
    r = init_list(cible)

    assert not r
    assert "contrat déjà présent" in r.message
    assert "jouet" in open_list(cible).unwrap().contract.name


def test_le_squelette_accepte_un_element_neuf(tmp_path: Path) -> None:
    """Le squelette n'est pas décoratif : `new` doit pouvoir s'y appuyer aussitôt."""
    _ = init_list(tmp_path / "neuve").unwrap()
    store = ouvrir(tmp_path / "neuve")
    _ = store.write(store.create("premier").unwrap()).unwrap()

    assert ouvrir(tmp_path / "neuve").validate().unwrap() == []


# ------------------------------------------------- init_list avec une définition
def semence(base: Path, contrat: str = CONTRAT) -> Path:
    """Une définition : le contenu d'un futur `.list/`, hors de tout répertoire-liste."""
    _ = ecrire(base, "contract.toml", contrat)
    return base


def test_une_definition_donne_son_contrat_a_la_liste(tmp_path: Path) -> None:
    src = semence(tmp_path / "defs/jouet")
    cible = init_list(tmp_path / "neuve", definition=src).unwrap()

    assert cible.read_text(encoding="utf-8") == (src / "contract.toml").read_text(encoding="utf-8")
    assert open_list(tmp_path / "neuve").unwrap().contract.name == "jouet"


def test_les_gabarits_de_la_definition_suivent(tmp_path: Path) -> None:
    """Sans eux, `derive` échouerait sur une liste pourtant amorcée — et l'échec
    ne se verrait qu'au moment de projeter, loin de l'amorçage qui l'a causé."""
    src = semence(tmp_path / "defs/jouet")
    _ = ecrire(src, "templates/revue.toml", GABARIT_TOML)
    _ = ecrire(src, "templates/revue.md", GABARIT_MD)

    _ = init_list(tmp_path / "neuve", definition=src).unwrap()
    templates = tmp_path / "neuve/.list/templates"
    assert sorted(f.name for f in templates.iterdir()) == ["revue.md", "revue.toml"]


def test_une_definition_sans_gabarit_s_amorce(tmp_path: Path) -> None:
    """`templates/` est facultatif : la plupart des listes ne dérivent jamais."""
    src = semence(tmp_path / "defs/jouet")
    _ = init_list(tmp_path / "neuve", definition=src).unwrap()

    assert not (tmp_path / "neuve/.list/templates").exists()
    assert open_list(tmp_path / "neuve").unwrap().validate().unwrap() == []


def test_une_definition_sans_contrat_est_refusee(tmp_path: Path) -> None:
    vide = tmp_path / "defs/vide"
    vide.mkdir(parents=True)
    r = init_list(tmp_path / "neuve", definition=vide)

    assert not r
    assert "définition sans contrat" in r.message
    assert not (tmp_path / "neuve").exists()


def test_un_contrat_de_definition_invalide_ne_cree_rien(tmp_path: Path) -> None:
    """TOUT EST JUGÉ EN MÉMOIRE D'ABORD. Créée puis refusée, la liste serait ensuite
    rejetée comme « contrat déjà présent » : l'appelant resterait coincé entre une
    erreur corrigée et un répertoire qu'il n'a pas créé."""
    src = semence(tmp_path / "defs/casse", 'name = "n"\n\n[fields.c]\ntype = "inconnu"\n')
    r = init_list(tmp_path / "neuve", definition=src)

    assert not r
    assert not (tmp_path / "neuve").exists()


def test_une_definition_ne_recoit_pas_nom_ni_description(tmp_path: Path) -> None:
    """Les écraser ferait mentir le `diff` qui prouve qu'une semence est la copie
    de son original."""
    src = semence(tmp_path / "defs/jouet")
    _ = init_list(tmp_path / "neuve", "Autre nom", "autre", definition=src).unwrap()

    assert open_list(tmp_path / "neuve").unwrap().contract.name == "jouet"


def test_le_squelette_reste_inchange_sans_definition(tmp_path: Path) -> None:
    """Critère de réussite du chantier : l'ajout de `definition` ne touche pas le
    comportement par défaut d'`init`."""
    cible = init_list(tmp_path / "neuve").unwrap()
    donnees = tomllib.loads(cible.read_text(encoding="utf-8"))

    assert donnees["name"] == "neuve"
    assert sorted(cast("dict[str, object]", donnees["fields"])) == ["id", "title"]
    assert donnees["sections"] == {"Constat": {"required": True, "description": ""}}


def test_une_liste_deja_montee_est_refusee_avant_de_lire_la_definition(tmp_path: Path) -> None:
    """La garde passe en tête : une définition fautive ne doit pas masquer le vrai
    motif du refus, qui est que la liste existe déjà."""
    cible = monter_liste(tmp_path / "deja", CONTRAT)
    r = init_list(cible, definition=tmp_path / "inexistante")

    assert not r
    assert "contrat déjà présent" in r.message
