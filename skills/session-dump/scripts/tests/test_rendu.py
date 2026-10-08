"""Tests du rendu d'un dump : frontmatter TOML, corps, nom de fichier."""

from __future__ import annotations

import tomllib
from datetime import UTC, datetime

import session_dump as sd

type Ligne = dict[str, object]


def session(**extra: object) -> sd.Session:
    champs: dict[str, object] = {
        "uuid": "0123456789abcdef",
        "titre": "Un titre",
        "cree": datetime(2026, 10, 8, 9, 12, 44, 123000, tzinfo=UTC),
        "branches": ("master", "dump-sessions"),
        "tours": 12,
        "mesure": "cost-state",
        "tokens": sd.Tokens(entree=1, sortie=2, cache_lu=3, cache_cree=4),
        "cout_usd": 38.2371,
        "duree": sd.Duree(totale_s=93160, api_s=2999),
        "illisibles": 0,
    } | extra
    return sd.Session(**champs)  # pyright: ignore[reportArgumentType]


def frontmatter(texte: str) -> dict[str, object]:
    _, fm, _ = texte.split("+++\n", 2)
    return tomllib.loads(fm)


def assistant(*blocs: Ligne) -> Ligne:
    return {"type": "assistant", "message": {"id": "m", "content": list(blocs)}}


def texte(valeur: str) -> Ligne:
    return {"type": "text", "text": valeur}


def outil(nom: str, **entree: object) -> Ligne:
    return {"type": "tool_use", "id": "t", "name": nom, "input": entree}


def utilisateur(contenu: object, **extra: object) -> Ligne:
    return {"type": "user", "message": {"role": "user", "content": contenu}} | extra


def test_le_frontmatter_se_lit_par_tomllib() -> None:
    donnees = frontmatter(sd.rendre_frontmatter(session()))
    assert donnees["session"] == "0123456789abcdef"
    assert donnees["titre"] == "Un titre"
    assert donnees["cree"] == datetime(2026, 10, 8, 9, 12, 44, tzinfo=UTC)
    assert donnees["branches"] == ["master", "dump-sessions"]
    assert donnees["tours"] == 12
    assert donnees["mesure"] == "cost-state"
    assert donnees["cout_usd"] == 38.2371
    assert donnees["tokens"] == {
        "total": 10,
        "entree": 1,
        "sortie": 2,
        "cache_lu": 3,
        "cache_cree": 4,
    }
    assert donnees["duree"] == {"totale_s": 93160, "api_s": 2999}


def test_les_nombres_du_frontmatter_separent_leurs_milliers_par_des_tirets_bas() -> None:
    grand = session(
        tours=1234,
        cout_usd=1234.5,
        tokens=sd.Tokens(entree=128766, sortie=239447, cache_lu=43941711, cache_cree=1062460),
        duree=sd.Duree(totale_s=93160, api_s=2999),
    )
    rendu = sd.rendre_frontmatter(grand)
    for ligne in (
        "tours = 1_234",
        "cout_usd = 1_234.5000",
        "total = 45_372_384",
        "cache_lu = 43_941_711",
        "totale_s = 93_160",
        "api_s = 2_999",
        "entree = 128_766",
    ):
        assert f"\n{ligne}\n" in rendu
    donnees = frontmatter(rendu)
    assert donnees["tokens"] == {
        "total": 45372384,
        "entree": 128766,
        "sortie": 239447,
        "cache_lu": 43941711,
        "cache_cree": 1062460,
    }
    assert donnees["tours"] == 1234
    assert donnees["cout_usd"] == 1234.5


def test_le_frontmatter_omet_cout_et_duree_sans_cost_state() -> None:
    rendu = sd.rendre_frontmatter(
        session(mesure="transcriptions", cout_usd=None, duree=None, cree=None, branches=())
    )
    donnees = frontmatter(rendu)
    assert "cout_usd" not in donnees
    assert "duree" not in donnees
    assert "cree" not in donnees
    assert donnees["branches"] == []
    assert donnees["mesure"] == "transcriptions"


def test_le_frontmatter_echappe_un_titre_difficile() -> None:
    titre = 'Guillemets " et \\ antislash\nligne 2\t« accents » \x7f'
    donnees = frontmatter(sd.rendre_frontmatter(session(titre=titre)))
    assert donnees["titre"] == titre


def test_le_corps_garde_la_discussion_et_une_ligne_par_outil() -> None:
    lignes = [
        utilisateur("Bonjour <system-reminder>bruit</system-reminder>"),
        assistant(
            {"type": "thinking", "thinking": "secret"},
            texte("Je lis."),
            outil("Read", file_path="/a/b.py", offset=3),
            outil("Bash", command="rm -rf /", description="Lister\nles fichiers"),
        ),
        utilisateur([{"type": "tool_result", "content": "RÉSULTAT"}]),
        assistant(outil("Skill", skill="lexique"), outil("Agent", subagent_type="Explore")),
        assistant(texte("Voilà.")),
        utilisateur("Merci", isMeta=False),
        {"type": "attachment", "attachment": {"content": "PIÈCE JOINTE"}},
    ]
    corps = sd.rendre_corps(lignes)
    assert corps == (
        "## Utilisateur\n\nBonjour\n\n"
        "## Assistant\n\nJe lis.\n\n"
        "- `Read` /a/b.py\n- `Bash` Lister les fichiers\n- `Skill` lexique\n- `Agent` Explore\n\n"
        "Voilà.\n\n"
        "## Utilisateur\n\nMerci\n"
    )
    for absent in ("secret", "RÉSULTAT", "PIÈCE JOINTE", "rm -rf", "offset", "bruit"):
        assert absent not in corps


def test_le_corps_exclut_meta_automatiques_et_sous_agents() -> None:
    lignes = [
        utilisateur("<local-command-caveat>x</local-command-caveat>", isMeta=True),
        utilisateur("corps du skill", isMeta=True),
        utilisateur("Résumé de compaction", isCompactSummary=True, isVisibleInTranscriptOnly=True),
        utilisateur("<local-command-stdout>ok</local-command-stdout>"),
        utilisateur("<task-notification>fini</task-notification>"),
        utilisateur("[Request interrupted by user]"),
        utilisateur("d'un sous-agent", isSidechain=True),
        utilisateur("Seul message"),
    ]
    assert sd.rendre_corps(lignes) == "## Utilisateur\n\nSeul message\n"


def test_une_commande_se_rend_par_son_nom_et_ses_arguments() -> None:
    commande = (
        "<command-message>implementation-tracker</command-message>\n"
        "<command-name>/implementation-tracker</command-name>\n"
        "<command-args>@suivi.md</command-args>"
    )
    sans_arguments = "<command-name>/clear</command-name>\n<command-args></command-args>"
    corps = sd.rendre_corps([utilisateur(commande), utilisateur(sans_arguments)])
    assert corps == "## Utilisateur\n\n/implementation-tracker @suivi.md\n\n/clear\n"


def test_un_texte_d_assistant_qui_ressemble_a_un_outil_reste_un_texte() -> None:
    lignes = [assistant(texte("- `Read` n'est pas un appel")), assistant(texte("suite"))]
    assert sd.rendre_corps(lignes) == "## Assistant\n\n- `Read` n'est pas un appel\n\nsuite\n"


def test_cible_outil() -> None:
    cible = sd.cible_outil
    assert cible("Edit", {"file_path": "/x"}) == "/x"
    assert cible("Write", {"file_path": "/y"}) == "/y"
    assert cible("NotebookEdit", {"notebook_path": "/n.ipynb"}) == "/n.ipynb"
    assert cible("Agent", {"subagent_type": "Plan", "description": "Plan du dump"}) == (
        "Plan — Plan du dump"
    )
    questions = {"questions": [{"header": "Modèle"}, {"header": "Portée"}, {"question": "?"}]}
    assert cible("AskUserQuestion", questions) == "Modèle, Portée"
    assert cible("WebFetch", {"url": "https://exemple.fr"}) == ""
    assert sd.ligne_outil({"name": "WebFetch", "input": {}}) == "- `WebFetch`"


def test_rendre_assemble_frontmatter_et_corps() -> None:
    rendu = sd.rendre(session(), [utilisateur("Salut")])
    assert rendu.startswith("+++\nsession = ")
    assert rendu.endswith("+++\n\n## Utilisateur\n\nSalut\n")


def test_nom_de_fichier() -> None:
    assert sd.nom_de_base(session(titre="Commit et continue")) == "2026-10-08-commit-et-continue"
    assert sd.nom_de_base(session(titre="Écrire / lire: côté « UTC »")) == (
        "2026-10-08-écrire-lire-côté-utc"
    )
    assert sd.nom_de_base(session(titre="???")) == "2026-10-08-0123456789abcdef"
    assert sd.nom_de_base(session(cree=None)).startswith("sans-date-")
    assert len(sd.nom_kebab("mot " * 50)) <= sd.LONGUEUR_NOM


def test_les_collisions_recoivent_toutes_le_suffixe_uuid() -> None:
    a = session(uuid="aaaaaaaa-1", titre="Commit")
    b = session(uuid="bbbbbbbb-2", titre="COMMIT")
    c = session(uuid="cccccccc-3", titre="Autre")
    noms = sd.noms_de_fichiers([a, b, c])
    assert noms == {
        "aaaaaaaa-1": "2026-10-08-commit-aaaaaaaa.md",
        "bbbbbbbb-2": "2026-10-08-commit-bbbbbbbb.md",
        "cccccccc-3": "2026-10-08-autre.md",
    }
    assert sd.noms_de_fichiers([c, b, a]) == noms
