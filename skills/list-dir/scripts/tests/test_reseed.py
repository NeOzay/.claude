"""`reseed` sur le disque : ce qu'il écrit, ce qu'il sauvegarde, ce qu'il refuse.

LA FUSION EST TESTÉE AILLEURS (test_fusion.py), en mémoire et cas par cas. Ici on
vérifie ce qu'une commande qui écrit doit garantir : ne jamais laisser une liste à
moitié rattrapée, ne jamais perdre l'état d'avant, et ne rien écrire du tout quand
elle refuse.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from jouet import ecrire
from listdir.contract import BACKUP, CONTRACT, LIST_DIR, SEED, TEMPLATES, load_contract
from listdir.provenance import emit, flatten, reseed, warnings
from listdir.store import init_list

SEMENCE = """name = "jouet"
description = "liste-jouet des tests"

# Ce commentaire porte le pourquoi d'un champ : il doit survivre à une recopie.
[origin]
def = "jouet"
version = 1

[fields.id]
type = "slug"
description = ""

[fields.title]
type = "text"
required = true
description = "le titre"
text = "titre par défaut"

[sections."Constat"]
required = true
description = "ce qui a été observé"
"""


def semer(tmp_path: Path, contrat: str = SEMENCE, gabarit: str = "") -> tuple[Path, Path]:
    """Une définition au rang 1, et la liste qu'elle vient de semer."""
    definition = tmp_path / ".claude" / "list-dir" / "jouet"
    _ = ecrire(definition, CONTRACT, contrat)
    if gabarit:
        _ = ecrire(definition, f"{TEMPLATES}/revue.md", gabarit)
    cible = tmp_path / "liste"
    _ = init_list(cible, definition=definition).unwrap()
    os.chdir(tmp_path)
    return definition, cible


def contrat_de(liste: Path) -> str:
    return (liste / LIST_DIR / CONTRACT).read_text(encoding="utf-8")


def test_liste_deja_a_jour_ne_change_rien(tmp_path: Path) -> None:
    definition, cible = semer(tmp_path)

    fait = reseed(cible, definition).unwrap()

    assert fait.changements == []
    assert contrat_de(cible) == SEMENCE


def test_semence_qui_evolue_est_recopiee_verbatim(tmp_path: Path) -> None:
    """Rien n'avait bougé localement : la nouvelle semence s'applique telle quelle,
    commentaires compris — les réémettre les perdrait pour rien."""
    definition, cible = semer(tmp_path)
    neuve = (
        SEMENCE.replace("version = 1", "version = 2")
        + '\n[fields.reviewed]\ntype = "date"\ndescription = ""\n'
    )
    _ = ecrire(definition, CONTRACT, neuve)

    fait = reseed(cible, definition).unwrap()

    assert fait.verbatim
    assert contrat_de(cible) == neuve
    assert "Ce commentaire porte le pourquoi" in contrat_de(cible)


def test_apport_de_semence_sur_une_liste_editee_est_reemis(tmp_path: Path) -> None:
    """Le local a bougé : le contrat est reconstruit, et l'édition locale survit."""
    definition, cible = semer(tmp_path)
    _ = ecrire(
        cible,
        f"{LIST_DIR}/{CONTRACT}",
        SEMENCE.replace('description = "le titre"', 'description = "l\'intitulé"'),
    )
    _ = ecrire(
        definition,
        CONTRACT,
        SEMENCE.replace("version = 1", "version = 2")
        + '\n[fields.vu]\ntype = "date"\ndescription = ""\n',
    )

    fait = reseed(cible, definition).unwrap()

    assert not fait.verbatim
    assert "l'intitulé" in contrat_de(cible)
    assert "fields.vu" in contrat_de(cible)


def test_conflit_refuse_et_n_ecrit_rien(tmp_path: Path) -> None:
    definition, cible = semer(tmp_path)
    avant = SEMENCE.replace('description = "le titre"', 'description = "l\'intitulé"')
    _ = ecrire(cible, f"{LIST_DIR}/{CONTRACT}", avant)
    _ = ecrire(
        definition, CONTRACT, SEMENCE.replace('description = "le titre"', 'description = "le nom"')
    )

    r = reseed(cible, definition)

    assert not r
    assert "fields.title.description" in r.message
    assert contrat_de(cible) == avant
    assert not (cible / LIST_DIR / BACKUP).exists()


def test_force_ne_tranche_pas_un_conflit(tmp_path: Path) -> None:
    """`--force` dégèle, et rien d'autre : le seul arbitrage possible appartient à
    celui qui a écrit l'une des deux versions."""
    definition, cible = semer(tmp_path)
    _ = ecrire(
        cible,
        f"{LIST_DIR}/{CONTRACT}",
        SEMENCE.replace('description = "le titre"', 'description = "l\'intitulé"'),
    )
    _ = ecrire(
        definition, CONTRACT, SEMENCE.replace('description = "le titre"', 'description = "le nom"')
    )

    assert not reseed(cible, definition, force=True)


def test_liste_gelee_est_refusee_puis_degelee(tmp_path: Path) -> None:
    definition, cible = semer(tmp_path)
    _ = ecrire(
        cible,
        f"{LIST_DIR}/{CONTRACT}",
        SEMENCE.replace("version = 1", "version = 1\nfrozen = true"),
    )
    _ = ecrire(definition, CONTRACT, SEMENCE.replace("version = 1", "version = 2"))

    refus = reseed(cible, definition)
    assert not refus
    assert "gelée" in refus.message

    assert reseed(cible, definition, force=True)


def test_la_sauvegarde_garde_l_etat_d_avant(tmp_path: Path) -> None:
    definition, cible = semer(tmp_path, gabarit="## Revue\n")
    avant = contrat_de(cible)
    _ = ecrire(definition, CONTRACT, SEMENCE.replace("version = 1", "version = 2"))

    _ = reseed(cible, definition).unwrap()

    backup = cible / LIST_DIR / BACKUP
    assert (backup / CONTRACT).read_text(encoding="utf-8") == avant
    assert (backup / TEMPLATES / "revue.md").read_text(encoding="utf-8") == "## Revue\n"


def test_la_semence_gardee_est_rafraichie(tmp_path: Path) -> None:
    """Sans ce rafraîchissement, le re-semis suivant comparerait à un état que plus
    rien ne reflète, et rejouerait indéfiniment les mêmes apports."""
    definition, cible = semer(tmp_path)
    neuve = SEMENCE.replace("version = 1", "version = 2")
    _ = ecrire(definition, CONTRACT, neuve)

    _ = reseed(cible, definition).unwrap()

    assert (cible / LIST_DIR / SEED / CONTRACT).read_text(encoding="utf-8") == neuve
    assert reseed(cible, definition).unwrap().changements == []


def test_dry_run_rapporte_sans_rien_ecrire(tmp_path: Path) -> None:
    definition, cible = semer(tmp_path)
    avant = contrat_de(cible)
    _ = ecrire(definition, CONTRACT, SEMENCE.replace("version = 1", "version = 2"))

    fait = reseed(cible, definition, dry_run=True).unwrap()

    assert fait.changements and not fait.ecrit
    assert contrat_de(cible) == avant
    assert not (cible / LIST_DIR / BACKUP).exists()


def test_gabarit_de_la_semence_est_repris(tmp_path: Path) -> None:
    definition, cible = semer(tmp_path, gabarit="## Revue\n")
    _ = ecrire(definition, f"{TEMPLATES}/revue.md", "## Revue remaniée\n")

    fait = reseed(cible, definition).unwrap()

    assert any("gabarit revue.md" in c for c in fait.changements)
    assert (cible / LIST_DIR / TEMPLATES / "revue.md").read_text(
        encoding="utf-8"
    ) == "## Revue remaniée\n"


def test_nom_discordant_refuse_en_code_2(tmp_path: Path) -> None:
    definition, cible = semer(tmp_path)

    r = reseed(cible, definition, expected_name="autre")

    assert r.status == 2
    assert "jouet" in r.message


# ------------------------------------------------ adoption d'une liste antérieure
def anterieure(tmp_path: Path, contrat: str) -> tuple[Path, Path]:
    """Une liste écrite avant ce dispositif : ni `[origin]`, ni `.list/semence/`."""
    definition = tmp_path / ".claude" / "list-dir" / "jouet"
    _ = ecrire(definition, CONTRACT, SEMENCE)
    cible = tmp_path / "liste"
    _ = ecrire(cible, f"{LIST_DIR}/{CONTRACT}", contrat)
    os.chdir(tmp_path)
    return definition, cible


SANS_ORIGIN = SEMENCE.replace('\n[origin]\ndef = "jouet"\nversion = 1\n', "")


def test_adoption_d_une_liste_identique_est_verbatim(tmp_path: Path) -> None:
    """Le cas de toutes les listes antérieures : elles ne diffèrent de leur semence
    que par l'absence de l'estampille."""
    definition, cible = anterieure(tmp_path, SANS_ORIGIN)

    fait = reseed(cible, definition).unwrap()

    assert fait.verbatim
    assert contrat_de(cible) == SEMENCE
    assert "Ce commentaire porte le pourquoi" in contrat_de(cible)


def test_adoption_estampille_a_la_version_de_la_semence(tmp_path: Path) -> None:
    definition, cible = anterieure(tmp_path, SANS_ORIGIN)

    _ = reseed(cible, definition).unwrap()

    origin = load_contract(cible).unwrap().origin
    assert origin is not None
    assert (origin.name, origin.version) == ("jouet", 1)


def test_adoption_cree_la_semence_gardee(tmp_path: Path) -> None:
    """La liste devient comparable hors ligne, sans résoudre aucune définition."""
    definition, cible = anterieure(tmp_path, SANS_ORIGIN)

    _ = reseed(cible, definition).unwrap()

    assert (cible / LIST_DIR / SEED / CONTRACT).read_text(encoding="utf-8") == SEMENCE


def test_adoption_d_une_liste_divergente_injecte_sans_ecraser(tmp_path: Path) -> None:
    definition, cible = anterieure(
        tmp_path, SANS_ORIGIN + '\n[fields.propre]\ntype = "text"\ndescription = ""\n'
    )

    fait = reseed(cible, definition).unwrap()

    assert not fait.verbatim
    assert "fields.propre" in contrat_de(cible)
    assert 'def = "jouet"' in contrat_de(cible)


def test_adoption_refuse_sur_une_cle_divergente(tmp_path: Path) -> None:
    """Sans point de référence, l'attribution est impossible : la refuser vaut mieux
    que la deviner."""
    definition, cible = anterieure(
        tmp_path, SANS_ORIGIN.replace('description = "le titre"', 'description = "l\'intitulé"')
    )

    r = reseed(cible, definition)

    assert not r
    assert "fields.title.description" in r.message


def test_suppression_locale_survit_a_un_re_semis(tmp_path: Path) -> None:
    """Le bogue que l'audit a trouvé : le sentinelle d'absence descendait jusque dans
    l'émetteur, qui sortait par un traceback — après la sauvegarde et une partie de
    l'écriture, donc en laissant la liste à moitié appliquée."""
    definition, cible = semer(tmp_path)
    _ = ecrire(cible, f"{LIST_DIR}/{CONTRACT}", SEMENCE.replace('text = "titre par défaut"\n', ""))
    _ = ecrire(definition, CONTRACT, SEMENCE.replace("version = 1", "version = 2"))

    fait = reseed(cible, definition).unwrap()

    assert fait.ecrit
    assert "titre par défaut" not in contrat_de(cible)
    assert "version = 2" in contrat_de(cible)


def test_gabarit_supprime_localement_survit_a_un_re_semis(tmp_path: Path) -> None:
    definition, cible = semer(tmp_path, gabarit="## Revue\n")
    (cible / LIST_DIR / TEMPLATES / "revue.md").unlink()
    _ = ecrire(definition, CONTRACT, SEMENCE.replace("version = 1", "version = 2"))

    _ = reseed(cible, definition).unwrap()

    assert not (cible / LIST_DIR / TEMPLATES / "revue.md").exists()
    assert "version = 2" in contrat_de(cible)


def test_re_semis_sans_effet_ne_touche_pas_a_la_sauvegarde(tmp_path: Path) -> None:
    """R9 : un second `reseed` — le geste de qui doute que le premier ait pris —
    remplaçait la sauvegarde par une copie de l'état courant, en répondant « déjà à
    jour ». La seule marche arrière disparaissait sans un mot."""
    definition, cible = semer(tmp_path)
    avant = contrat_de(cible)
    _ = ecrire(definition, CONTRACT, SEMENCE.replace("version = 1", "version = 2"))
    _ = reseed(cible, definition).unwrap()

    fait = reseed(cible, definition).unwrap()

    assert not fait.ecrit
    assert (cible / LIST_DIR / BACKUP / CONTRACT).read_text(encoding="utf-8") == avant


def test_une_liste_a_suppression_locale_finit_par_dire_qu_elle_est_a_jour(
    tmp_path: Path,
) -> None:
    """R10 : la suppression était rapportée comme un changement à chaque appel, donc
    une telle liste n'annonçait jamais « déjà à jour » et `--dry-run` promettait sans
    fin un changement qui n'en était pas un."""
    definition, cible = semer(tmp_path)
    _ = ecrire(cible, f"{LIST_DIR}/{CONTRACT}", SEMENCE.replace('text = "titre par défaut"\n', ""))
    _ = reseed(cible, definition).unwrap()

    fait = reseed(cible, definition).unwrap()

    assert (fait.changements, fait.ecrit) == ([], False)


def test_une_difference_de_pure_forme_ne_se_dit_pas_modifiee(tmp_path: Path) -> None:
    """R7 : un contrat réémis perd ses commentaires et peut recomposer une écriture
    équivalente. Comparé à l'octet, il se déclarait modifié localement pour toujours —
    un avertissement permanent qu'on apprend à ignorer, et qui emporte les vrais.

    Une divergence de CONTENU, elle, continue de se dire : le test suivant l'exige."""
    definition, cible = semer(tmp_path)
    _ = ecrire(cible, f"{LIST_DIR}/{CONTRACT}", emit(flatten(tomllib.loads(SEMENCE))).unwrap())

    dits = warnings(cible, load_contract(cible).unwrap())

    assert contrat_de(cible) != SEMENCE  # l'octet diffère : commentaire perdu
    assert [d for d in dits if "modifié localement" in d] == []
    _ = definition


def test_une_divergence_de_contenu_se_dit_toujours(tmp_path: Path) -> None:
    definition, cible = semer(tmp_path)
    _ = ecrire(cible, f"{LIST_DIR}/{CONTRACT}", SEMENCE.replace('text = "titre par défaut"\n', ""))

    dits = warnings(cible, load_contract(cible).unwrap())

    assert any("modifié localement" in d for d in dits)
    _ = definition


def test_un_commentaire_local_ne_fait_pas_reecrire_le_contrat(tmp_path: Path) -> None:
    """R13 : une divergence de pure forme faisait réécrire le contrat — donc perdre le
    commentaire — sous le message « déjà à jour »."""
    definition, cible = semer(tmp_path)
    annote = SEMENCE.replace("[fields.id]", "# noté sur place\n[fields.id]")
    _ = ecrire(cible, f"{LIST_DIR}/{CONTRACT}", annote)

    fait = reseed(cible, definition).unwrap()

    assert not fait.ecrit
    assert contrat_de(cible) == annote


def test_un_champ_ajoute_localement_ne_se_rejoue_pas_a_chaque_appel(tmp_path: Path) -> None:
    """R12 : « retirée de la semence » décrivait un état durable — le local garde une
    clé que la semence ne porte pas — rapporté comme un changement à chaque re-semis."""
    definition, cible = semer(tmp_path)
    _ = ecrire(
        cible,
        f"{LIST_DIR}/{CONTRACT}",
        SEMENCE + '\n[fields.propre]\ntype = "text"\ndescription = ""\n',
    )
    _ = ecrire(definition, CONTRACT, SEMENCE.replace("version = 1", "version = 2"))
    _ = reseed(cible, definition).unwrap()

    fait = reseed(cible, definition).unwrap()

    assert (fait.changements, fait.ecrit) == ([], False)
    assert "fields.propre" in contrat_de(cible)
