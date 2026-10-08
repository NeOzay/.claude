"""Tests de la lecture et des statistiques d'une session, sur des JSONL synthétiques."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path

import session_dump as sd

type Ligne = dict[str, object]
type Ecrire = Callable[[Path, Iterable[Ligne]], Path]


def assistant(identifiant: str, sortie: int, **extra: object) -> Ligne:
    usage: dict[str, object] = {
        "input_tokens": 2,
        "output_tokens": sortie,
        "cache_read_input_tokens": 100,
        "cache_creation_input_tokens": 10,
    } | extra
    return {"type": "assistant", "message": {"id": identifiant, "usage": usage}}


def utilisateur(contenu: object, **extra: object) -> Ligne:
    return {"type": "user", "message": {"role": "user", "content": contenu}} | extra


def cost_state(**extra: object) -> Ligne:
    return {
        "type": "cost-state",
        "totalCostUSD": 1.5,
        "totalDuration": 93_160_400,
        "totalAPIDuration": 2_999_000,
        "modelUsage": {
            "claude-opus": {
                "inputTokens": 10,
                "outputTokens": 20,
                "thinkingTokens": 5,
                "cacheReadInputTokens": 300,
                "cacheCreationInputTokens": 40,
            },
            "claude-haiku": {
                "inputTokens": 1,
                "outputTokens": 2,
                "cacheReadInputTokens": 3,
                "cacheCreationInputTokens": 4,
            },
        },
    } | extra


def test_lire_jsonl_compte_les_lignes_illisibles(tmp_path: Path) -> None:
    chemin = tmp_path / "s.jsonl"
    chemin.write_text('{"type": "mode"}\n{pas du json\n\n[1, 2]\n{"type": "x"}\n', encoding="utf-8")
    lignes, illisibles = sd.lire_jsonl(chemin)
    assert [ligne["type"] for ligne in lignes] == ["mode", "x"]
    assert illisibles == 2


def test_un_message_eclate_en_plusieurs_lignes_compte_une_fois() -> None:
    lignes = [assistant("m1", 5), assistant("m1", 30), assistant("m2", 7)]
    tokens = sd.tokens_transcriptions(lignes)
    assert tokens.sortie == 37
    assert tokens.entree == 4
    assert tokens.cache_lu == 200
    assert tokens.cache_cree == 20
    assert tokens.total == 261


def test_tokens_transcriptions_ignore_ce_qui_n_est_pas_un_entier() -> None:
    lignes = [assistant("m1", 5, input_tokens="beaucoup", cache_read_input_tokens=True)]
    tokens = sd.tokens_transcriptions(lignes)
    assert tokens.entree == 0
    assert tokens.cache_lu == 0


def test_cost_state_additionne_les_modeles_et_garde_le_thinking_dans_la_sortie() -> None:
    tokens = sd.tokens_cost_state(cost_state())
    assert tokens == sd.Tokens(entree=11, sortie=22, cache_lu=303, cache_cree=44)
    assert tokens.total == 380


def test_le_dernier_cost_state_fait_foi() -> None:
    lignes = [cost_state(totalCostUSD=1.0), {"type": "mode"}, cost_state(totalCostUSD=2.0)]
    retenue = sd.dernier_cost_state(lignes)
    assert retenue is not None
    assert retenue["totalCostUSD"] == 2.0
    assert sd.dernier_cost_state([{"type": "mode"}]) is None


def test_duree_en_secondes() -> None:
    assert sd.duree_cost_state(cost_state()) == sd.Duree(totale_s=93160, api_s=2999)


def test_titre_prefere_celui_de_l_utilisateur_puis_le_dernier_genere() -> None:
    generes = [
        {"type": "ai-title", "aiTitle": "Premier"},
        {"type": "agent-name", "agentName": "clear-conversation-history"},
        {"type": "ai-title", "aiTitle": "Second"},
    ]
    assert sd.titre(generes, "uuid") == "Second"
    donne = [*generes, {"type": "custom-title", "customTitle": "Le mien"}]
    assert sd.titre(donne, "uuid") == "Le mien"
    assert sd.titre([{"type": "agent-name", "agentName": "x"}], "uuid") == "uuid"


def test_creation_et_branches() -> None:
    lignes = [
        {"type": "mode"},
        {"timestamp": "2026-10-08T09:12:44.123Z", "gitBranch": "master"},
        {"timestamp": "2026-10-08T10:00:00.000Z", "gitBranch": "dump-sessions"},
        {"timestamp": "2026-10-08T11:00:00.000Z", "gitBranch": "master"},
    ]
    assert sd.creation(lignes) == datetime(2026, 10, 8, 9, 12, 44, 123000, tzinfo=UTC)
    assert sd.branches(lignes) == ("master", "dump-sessions")
    assert sd.creation([{"timestamp": "pas une date"}]) is None


def test_tours_comptent_ce_que_l_utilisateur_a_saisi() -> None:
    lignes = [
        utilisateur("salut"),
        utilisateur([{"type": "text", "text": "avec bloc"}]),
        utilisateur("<command-name>/clear</command-name>"),
        utilisateur("<system-reminder>rien</system-reminder>et un texte"),
        utilisateur("caveat", isMeta=True),
        utilisateur("This session is being continued…", isCompactSummary=True),
        utilisateur([{"type": "tool_result", "content": "sortie"}]),
        utilisateur("<local-command-stdout>ok</local-command-stdout>"),
        utilisateur("<task-notification>fini</task-notification>"),
        utilisateur([{"type": "text", "text": "[Request interrupted by user]"}]),
        utilisateur("d'un sous-agent", isSidechain=True),
        {"type": "assistant", "message": {"content": "réponse"}},
    ]
    assert sd.compter_tours(lignes) == 4


def test_texte_utilisateur_retire_les_system_reminder() -> None:
    message = {"content": "avant <system-reminder>\nbruit\n</system-reminder> après"}
    assert sd.texte_utilisateur(message) == "avant  après"


def test_analyser_prefere_cost_state(tmp_path: Path, ecrire_jsonl: Ecrire) -> None:
    chemin = ecrire_jsonl(
        tmp_path / "abc.jsonl",
        [
            utilisateur("salut", timestamp="2026-10-08T09:00:00Z", gitBranch="master"),
            assistant("m1", 999),
            {"type": "ai-title", "aiTitle": "Mon titre"},
            cost_state(),
        ],
    )
    session = sd.analyser(chemin)
    assert session.uuid == "abc"
    assert session.titre == "Mon titre"
    assert session.mesure == "cost-state"
    assert session.tokens.total == 380
    assert session.cout_usd == 1.5
    assert session.duree == sd.Duree(totale_s=93160, api_s=2999)
    assert session.tours == 1
    assert session.branches == ("master",)


def test_analyser_sans_cost_state_somme_les_transcriptions(
    tmp_path: Path, ecrire_jsonl: Ecrire
) -> None:
    chemin = ecrire_jsonl(tmp_path / "abc.jsonl", [utilisateur("salut"), assistant("m1", 30)])
    ecrire_jsonl(tmp_path / "abc" / "subagents" / "agent-1.jsonl", [assistant("s1", 12)])
    ecrire_jsonl(tmp_path / "abc" / "subagents" / "agent-2.jsonl", [assistant("s2", 8)])
    session = sd.analyser(chemin)
    assert session.mesure == "transcriptions"
    assert session.tokens.sortie == 50
    assert session.cout_usd is None
    assert session.duree is None
    assert session.titre == "abc"
    assert session.cree is None


def test_analyser_signale_les_lignes_illisibles(tmp_path: Path) -> None:
    chemin = tmp_path / "abc.jsonl"
    chemin.write_text('{"type": "mode"}\nillisible\n', encoding="utf-8")
    assert sd.analyser(chemin).illisibles == 1


def test_sessions_du_projet_ne_prend_que_les_jsonl_de_la_racine(
    tmp_path: Path, ecrire_jsonl: Ecrire
) -> None:
    ecrire_jsonl(tmp_path / "b.jsonl", [])
    ecrire_jsonl(tmp_path / "a.jsonl", [])
    ecrire_jsonl(tmp_path / "a" / "subagents" / "agent-1.jsonl", [])
    assert [p.name for p in sd.sessions_du_projet(tmp_path)] == ["a.jsonl", "b.jsonl"]
