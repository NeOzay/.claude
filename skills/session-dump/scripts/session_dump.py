"""Lit une session Claude Code et en tire des statistiques, sans rien interpréter.

PORTÉE : la lecture des JSONL de `projects/<id>/`, le calcul de tokens, coût, durée, tours,
titre, date de création et branches, puis le rendu d'un dump (frontmatter TOML, corps, nom de
fichier). Rien ici ne classe ni n'analyse le contenu d'une discussion : le corps ne garde que ce
que l'utilisateur a saisi, ce que l'assistant a écrit, et une ligne par appel d'outil. Résultats
d'outils, thinking, messages méta et attachments n'y entrent jamais.

TOKENS : de la dernière ligne `cost-state` quand la session en porte une — son `modelUsage` est
seul cohérent avec `totalCostUSD`, il compte aussi les appels annexes (titres, classifieur) et
les sous-agents. À défaut, recalculés depuis les transcriptions (principale et sous-agents), et
le coût comme la durée restent absents : aucun nombre inventé.

DÉDOUBLONNAGE : un message `assistant` est éclaté en plusieurs lignes de même `message.id`, qui
répètent son `usage`. Sommer ligne à ligne compterait plusieurs fois le même message.

THINKING : `thinkingTokens` n'a pas de ligne propre. Il est déjà compté dans `outputTokens`, donc
dans `sortie` ; l'ajouter le compterait deux fois.

TOLÉRANCE : une ligne illisible est comptée et signalée par l'appelant, jamais fatale.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, cast

type Ligne = Mapping[str, object]

# Messages utilisateur que le harnais écrit seul : ils ne sont pas des tours saisis. Définis ICI
# ET NULLE PART AILLEURS ; le rendu du corps s'appuie sur la même liste.
PREFIXES_AUTOMATIQUES = (
    "<local-command-stdout>",
    "<local-command-stderr>",
    "<task-notification>",
    "<bash-stdout>",
    "<bash-stderr>",
    "[Request interrupted by user",
)

# Bloc de rappel que le harnais ajoute au texte d'un message utilisateur.
SYSTEM_REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL)


@dataclass(frozen=True)
class Tokens:
    """Tokens par type ; `sortie` contient le thinking."""

    entree: int = 0
    sortie: int = 0
    cache_lu: int = 0
    cache_cree: int = 0

    @property
    def total(self) -> int:
        return self.entree + self.sortie + self.cache_lu + self.cache_cree

    def __add__(self, autre: Tokens) -> Tokens:
        return Tokens(
            self.entree + autre.entree,
            self.sortie + autre.sortie,
            self.cache_lu + autre.cache_lu,
            self.cache_cree + autre.cache_cree,
        )


@dataclass(frozen=True)
class Duree:
    """Durées en secondes, d'après `cost-state` (qui les donne en millisecondes)."""

    totale_s: int
    api_s: int


@dataclass(frozen=True)
class Session:
    """Les statistiques d'une session principale."""

    uuid: str
    titre: str
    cree: datetime | None
    branches: tuple[str, ...]
    tours: int
    mesure: Literal["cost-state", "transcriptions"]
    tokens: Tokens
    cout_usd: float | None
    duree: Duree | None
    illisibles: int


def analyser_ligne(brute: str) -> Ligne | None:
    """L'objet JSON de `brute`, ou None si elle est illisible ou n'est pas un objet."""
    try:
        valeur = cast("object", json.loads(brute))
    except json.JSONDecodeError:
        return None
    objet = dictionnaire(valeur)
    return objet if isinstance(valeur, dict) else None


def lire_jsonl(chemin: Path) -> tuple[list[Ligne], int]:
    """Les lignes JSON objet de `chemin`, et le nombre de lignes illisibles écartées."""
    lignes: list[Ligne] = []
    illisibles = 0
    with chemin.open(encoding="utf-8", errors="replace") as flux:
        for brute in flux:
            if not brute.strip():
                continue
            valeur = analyser_ligne(brute)
            if valeur is None:
                illisibles += 1
            else:
                lignes.append(valeur)
    return lignes, illisibles


def entier(valeur: object) -> int:
    """`valeur` si c'est un entier, sinon 0 : une valeur lue du JSON n'est pas prise sur parole."""
    return valeur if isinstance(valeur, int) and not isinstance(valeur, bool) else 0


def dictionnaire(valeur: object) -> Ligne:
    """`valeur` si c'est un objet JSON, sinon un objet vide."""
    if isinstance(valeur, dict):
        # Les clés d'un objet JSON sont toujours des chaînes : le typeur ne le sait pas.
        return cast("Ligne", valeur)
    return {}


def liste(valeur: object) -> list[object]:
    """`valeur` si c'est un tableau JSON, sinon un tableau vide."""
    if isinstance(valeur, list):
        return cast("list[object]", valeur)  # éléments de types quelconques : tous des `object`
    return []


def chaine(valeur: object) -> str | None:
    """`valeur` si c'est une chaîne, sinon None."""
    return valeur if isinstance(valeur, str) else None


def tokens_transcriptions(lignes: Iterable[Ligne]) -> Tokens:
    """Les tokens des messages `assistant`, un seul décompte par `message.id`."""
    par_message: dict[str, Tokens] = {}
    for ligne in lignes:
        if ligne.get("type") != "assistant":
            continue
        message = dictionnaire(ligne.get("message"))
        identifiant = message.get("id")
        if not isinstance(identifiant, str):
            continue
        usage = dictionnaire(message.get("usage"))
        # La dernière ligne d'un message porte son usage complet.
        par_message[identifiant] = Tokens(
            entree=entier(usage.get("input_tokens")),
            sortie=entier(usage.get("output_tokens")),
            cache_lu=entier(usage.get("cache_read_input_tokens")),
            cache_cree=entier(usage.get("cache_creation_input_tokens")),
        )
    return sum(par_message.values(), Tokens())


def dernier_cost_state(lignes: Iterable[Ligne]) -> Ligne | None:
    """La dernière ligne `cost-state` : elle est cumulative, la dernière fait foi."""
    retenue: Ligne | None = None
    for ligne in lignes:
        if ligne.get("type") == "cost-state":
            retenue = ligne
    return retenue


def tokens_cost_state(cost_state: Ligne) -> Tokens:
    """Les tokens de `modelUsage`, additionnés sur tous les modèles."""
    total = Tokens()
    for brut in dictionnaire(cost_state.get("modelUsage")).values():
        usage = dictionnaire(brut)
        total += Tokens(
            entree=entier(usage.get("inputTokens")),
            sortie=entier(usage.get("outputTokens")),
            cache_lu=entier(usage.get("cacheReadInputTokens")),
            cache_cree=entier(usage.get("cacheCreationInputTokens")),
        )
    return total


def duree_cost_state(cost_state: Ligne) -> Duree:
    """Les durées de `cost-state`, converties de millisecondes en secondes."""
    return Duree(
        totale_s=round(entier(cost_state.get("totalDuration")) / 1000),
        api_s=round(entier(cost_state.get("totalAPIDuration")) / 1000),
    )


def cout_cost_state(cost_state: Ligne) -> float | None:
    """`totalCostUSD`, ou None s'il manque."""
    cout = cost_state.get("totalCostUSD")
    return float(cout) if isinstance(cout, int | float) and not isinstance(cout, bool) else None


def titre(lignes: Iterable[Ligne], uuid: str) -> str:
    """Le dernier `custom-title`, sinon le dernier `ai-title`, sinon l'UUID.

    Seul `custom-title` est un titre donné par l'utilisateur ; `agent-name` n'en est pas un.
    """
    donne = ""
    genere = ""
    for ligne in lignes:
        type_ = ligne.get("type")
        if type_ == "custom-title":
            donne = (chaine(ligne.get("customTitle")) or "").strip()
        elif type_ == "ai-title":
            genere = (chaine(ligne.get("aiTitle")) or "").strip()
    return donne or genere or uuid


def horodatage(valeur: object) -> datetime | None:
    """La date d'un horodatage ISO 8601, en UTC, ou None s'il est absent ou illisible."""
    if not isinstance(valeur, str):
        return None
    try:
        date = datetime.fromisoformat(valeur.replace("Z", "+00:00"))
    except ValueError:
        return None
    return date.astimezone(UTC) if date.tzinfo else date.replace(tzinfo=UTC)


def creation(lignes: Iterable[Ligne]) -> datetime | None:
    """Le premier horodatage de la session."""
    for ligne in lignes:
        date = horodatage(ligne.get("timestamp"))
        if date is not None:
            return date
    return None


def branches(lignes: Iterable[Ligne]) -> tuple[str, ...]:
    """Les valeurs de `gitBranch`, dans l'ordre de première apparition."""
    vues: dict[str, None] = {}
    for ligne in lignes:
        branche = ligne.get("gitBranch")
        if isinstance(branche, str) and branche:
            vues.setdefault(branche)
    return tuple(vues)


def texte_utilisateur(message: Ligne) -> str | None:
    """Le texte d'un message utilisateur sans ses blocs `<system-reminder>`.

    None quand le message ne porte que des résultats d'outils, ou rien. Les images ne sont pas
    du texte : un message d'images seules rend la chaîne vide.
    """
    contenu = message.get("content")
    if isinstance(contenu, str):
        brut = contenu
    elif isinstance(contenu, list):
        blocs = [dictionnaire(bloc) for bloc in liste(cast("object", contenu))]
        if blocs and all(bloc.get("type") == "tool_result" for bloc in blocs):
            return None
        textes = (chaine(bloc.get("text")) for bloc in blocs if bloc.get("type") == "text")
        brut = "\n".join(texte for texte in textes if texte is not None)
    else:
        return None
    return SYSTEM_REMINDER.sub("", brut).strip()


def est_tour(ligne: Ligne) -> bool:
    """Vrai si la ligne est un message saisi par l'utilisateur : prompt ou commande `/`.

    Exclus : les messages méta, le résumé que Claude Code écrit après une compaction du contexte
    (`isCompactSummary`), les résultats d'outils, ceux d'un sous-agent et les messages que le
    harnais écrit seul (`PREFIXES_AUTOMATIQUES`).
    """
    if ligne.get("type") != "user" or ligne.get("isSidechain"):
        return False
    if ligne.get("isMeta") or ligne.get("isCompactSummary"):
        return False
    texte = texte_utilisateur(dictionnaire(ligne.get("message")))
    if texte is None:
        return False
    return not texte.startswith(PREFIXES_AUTOMATIQUES)


def compter_tours(lignes: Iterable[Ligne]) -> int:
    """Le nombre de tours saisis par l'utilisateur."""
    return sum(1 for ligne in lignes if est_tour(ligne))


def analyser(chemin: Path) -> Session:
    """Les statistiques de la session dont le JSONL principal est `chemin`."""
    lignes, illisibles = lire_jsonl(chemin)
    return analyser_lignes(chemin, lignes, illisibles)


def analyser_lignes(chemin: Path, lignes: Sequence[Ligne], illisibles: int) -> Session:
    """Les statistiques d'une session dont `lignes` est le JSONL principal, lu de `chemin`.

    Les transcriptions des sous-agents (`<uuid>/subagents/*.jsonl`) ne se lisent que si la
    session n'a pas de `cost-state`.
    """
    uuid = chemin.stem
    cost_state = dernier_cost_state(lignes)
    if cost_state is not None:
        mesure: Literal["cost-state", "transcriptions"] = "cost-state"
        tokens = tokens_cost_state(cost_state)
        cout = cout_cost_state(cost_state)
        duree = duree_cost_state(cost_state)
    else:
        mesure = "transcriptions"
        tokens = tokens_transcriptions(lignes)
        for sous in sorted((chemin.parent / uuid / "subagents").glob("*.jsonl")):
            lignes_sous, illisibles_sous = lire_jsonl(sous)
            tokens += tokens_transcriptions(lignes_sous)
            illisibles += illisibles_sous
        cout = None
        duree = None
    return Session(
        uuid=uuid,
        titre=titre(lignes, uuid),
        cree=creation(lignes),
        branches=branches(lignes),
        tours=compter_tours(lignes),
        mesure=mesure,
        tokens=tokens,
        cout_usd=cout,
        duree=duree,
        illisibles=illisibles,
    )


def sessions_du_projet(repertoire: Path) -> list[Path]:
    """Les JSONL des sessions principales de `repertoire` (`projects/<id>/`), triés par nom."""
    return sorted(repertoire.glob("*.jsonl"))


# --- Rendu -------------------------------------------------------------------------------------

COMMANDE = re.compile(r"<command-name>\s*/?(.*?)\s*</command-name>", re.DOTALL)
ARGUMENTS = re.compile(r"<command-args>(.*?)</command-args>", re.DOTALL)
NON_MOT = re.compile(r"[\W_]+")
# Une moitié de paire de substitution UTF-16 (`\ud83d` seule) passe `json.loads` mais ne s'encode
# pas en UTF-8 : le JSONL, écrit depuis JavaScript, peut en porter.
SUBSTITUT_SEUL = re.compile(r"[\ud800-\udfff]")
LONGUEUR_NOM = 80


def chaine_toml(valeur: str) -> str:
    """Une chaîne TOML de base : l'échappement JSON est valide en TOML, DEL en plus."""
    return json.dumps(valeur, ensure_ascii=False).replace("\x7f", "\\u007f")


def rendre_frontmatter(session: Session) -> str:
    """Le frontmatter TOML de `session`, délimité par `+++`, champs plats dans un ordre fixe.

    `session`, `titre`, `cree` et `branches` identifient la session ; ils ne sont pas des
    métriques. `cout_usd` et `[duree]` n'existent que si la mesure vient de `cost-state`. Les
    nombres s'écrivent par groupes de trois chiffres séparés par `_` (`45_372_384`), que TOML
    admet et que `tomllib` relit.
    """
    lignes = [
        "+++",
        f"session = {chaine_toml(session.uuid)}",
        f"titre = {chaine_toml(session.titre)}",
    ]
    if session.cree is not None:
        lignes.append(f"cree = {session.cree.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    branches_toml = ", ".join(chaine_toml(branche) for branche in session.branches)
    lignes += [
        f"branches = [{branches_toml}]",
        f"tours = {session.tours:_}",
        f"mesure = {chaine_toml(session.mesure)}",
    ]
    if session.cout_usd is not None:
        lignes.append(f"cout_usd = {session.cout_usd:_.4f}")
    tokens = session.tokens
    lignes += [
        "",
        "[tokens]",
        f"total = {tokens.total:_}",
        f"entree = {tokens.entree:_}",
        f"sortie = {tokens.sortie:_}",
        f"cache_lu = {tokens.cache_lu:_}",
        f"cache_cree = {tokens.cache_cree:_}",
    ]
    if session.duree is not None:
        lignes += [
            "",
            "[duree]",
            f"totale_s = {session.duree.totale_s:_}",
            f"api_s = {session.duree.api_s:_}",
        ]
    lignes.append("+++")
    return "\n".join(lignes) + "\n"


def texte_tour(message: Ligne) -> str:
    """Le texte d'un tour utilisateur ; une commande `/` devient `/<nom> <arguments>`."""
    texte = texte_utilisateur(message) or ""
    commande = COMMANDE.search(texte)
    if commande is None:
        return texte
    arguments = ARGUMENTS.search(texte)
    return f"/{commande.group(1)} {arguments.group(1).strip() if arguments else ''}".strip()


def cible_outil(nom: str, entree: Ligne) -> str:
    """Ce qui désigne l'appel d'un outil en quelques mots, sans le contenu de ses arguments."""
    match nom:
        case "Read" | "Edit" | "Write":
            cible = chaine(entree.get("file_path"))
        case "NotebookEdit":
            cible = chaine(entree.get("notebook_path"))
        case "Bash":
            cible = chaine(entree.get("description"))
        case "Skill":
            cible = chaine(entree.get("skill"))
        case "Agent":
            morceaux = (chaine(entree.get("subagent_type")), chaine(entree.get("description")))
            cible = " — ".join(morceau for morceau in morceaux if morceau)
        case "AskUserQuestion":
            questions = (dictionnaire(q) for q in liste(entree.get("questions")))
            cible = ", ".join(h for h in (chaine(q.get("header")) for q in questions) if h)
        case _:
            cible = None
    return " ".join((cible or "").split())


def ligne_outil(bloc: Ligne) -> str:
    """La ligne d'un appel d'outil : `` > - `<Outil>` <cible> ``."""
    nom = chaine(bloc.get("name")) or "?"
    cible = cible_outil(nom, dictionnaire(bloc.get("input")))
    return f"> - `{nom}` {cible}".rstrip()


def paragraphes_assistant(ligne: Ligne) -> list[tuple[str, bool]]:
    """Les textes et les appels d'outils d'une ligne `assistant`, hors thinking.

    Chaque paragraphe est suivi de `True` quand c'est une ligne d'appel d'outil.
    """
    contenu = dictionnaire(ligne.get("message")).get("content")
    if isinstance(contenu, str):
        return [(contenu.strip(), False)] if contenu.strip() else []
    paragraphes: list[tuple[str, bool]] = []
    for brut in liste(contenu):
        bloc = dictionnaire(brut)
        if bloc.get("type") == "text":
            texte = (chaine(bloc.get("text")) or "").strip()
            if texte:
                paragraphes.append((texte, False))
        elif bloc.get("type") == "tool_use":
            paragraphes.append((ligne_outil(bloc), True))
    return paragraphes


def rendre_corps(lignes: Iterable[Ligne]) -> str:
    """La discussion, dans l'ordre, sous des titres `## Utilisateur` et `## Assistant`.

    Un titre n'est écrit que quand l'interlocuteur change. Les appels d'outils consécutifs
    forment une seule citation à puces, sans ligne vide entre eux.
    """
    blocs: list[str] = []
    interlocuteur = ""
    precedent_outil = False
    for ligne in lignes:
        if ligne.get("isSidechain") or ligne.get("isMeta"):
            continue
        type_ = ligne.get("type")
        if type_ == "user":
            if not est_tour(ligne):
                continue
            paragraphes = [(texte_tour(dictionnaire(ligne.get("message"))), False)]
            nom = "Utilisateur"
        elif type_ == "assistant":
            paragraphes = paragraphes_assistant(ligne)
            nom = "Assistant"
        else:
            continue
        paragraphes = [(texte, outil) for texte, outil in paragraphes if texte]
        if not paragraphes:
            continue
        if nom != interlocuteur:
            blocs.append(f"## {nom}")
            interlocuteur = nom
            precedent_outil = False
        for paragraphe, outil in paragraphes:
            if outil and precedent_outil:
                blocs[-1] += "\n" + paragraphe
            else:
                blocs.append(paragraphe)
            precedent_outil = outil
    return "\n\n".join(blocs) + "\n" if blocs else ""


def rendre(session: Session, lignes: Iterable[Ligne]) -> str:
    """Le dump complet : frontmatter, ligne vide, corps."""
    return rendre_frontmatter(session) + "\n" + rendre_corps(lignes)


def nom_kebab(titre_session: str) -> str:
    """Le titre en kebab-case : minuscules, accents conservés, tout séparateur devient `-`."""
    return NON_MOT.sub("-", titre_session.lower()).strip("-")[:LONGUEUR_NOM].strip("-")


def nom_de_base(session: Session) -> str:
    """`<date de création en UTC>-<titre en kebab-case>`, sans extension ni suffixe."""
    date = session.cree.strftime("%Y-%m-%d") if session.cree is not None else "sans-date"
    return f"{date}-{nom_kebab(session.titre) or session.uuid}"


def noms_de_fichiers(sessions: Iterable[Session]) -> dict[str, str]:
    """Le nom de fichier de chaque session, par UUID.

    Deux sessions au même nom de base reçoivent toutes deux le suffixe des 8 premiers caractères
    de leur UUID : le nom d'une session ne dépend pas de l'ordre dans lequel on les rend.
    """
    sessions = list(sessions)
    bases = {session.uuid: nom_de_base(session) for session in sessions}
    compte = Counter(base.casefold() for base in bases.values())
    return {
        uuid: f"{base}-{uuid[:8]}.md" if compte[base.casefold()] > 1 else f"{base}.md"
        for uuid, base in bases.items()
    }


# --- Écriture ----------------------------------------------------------------------------------


@dataclass(frozen=True)
class Bilan:
    """Ce qu'un dump a écrit."""

    destination: Path
    ecrits: int
    ecartes: int
    illisibles: int


@dataclass(frozen=True)
class Echec:
    """Un échec nommé : le message va sur stderr, `code` est la sortie du processus."""

    code: int
    message: str


def id_projet(projet: Path) -> str:
    """Le nom du répertoire de `projet` sous `projects/` : tout caractère non alphanumérique
    du chemin absolu devient `-`."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(projet))


def repertoire_config(environ: Mapping[str, str]) -> Path:
    """Le répertoire de configuration de Claude Code : `$CLAUDE_CONFIG_DIR`, sinon `~/.claude`."""
    donne = environ.get("CLAUDE_CONFIG_DIR")
    return Path(donne) if donne else Path(environ.get("HOME") or Path.home()) / ".claude"


def remplacer(destination: Path, contenus: Mapping[str, str]) -> None:
    """Écrit `contenus` (nom → texte) dans `destination`, dont le contenu précédent est vidé.

    TOUT LE CONTENU EST REMPLACÉ : un dump périmé ne survit pas à un nouveau. Le répertoire lui-même
    reste le même, car un outil peut l'avoir ouvert ou s'y tenir. Les fichiers sont d'abord écrits
    dans un répertoire voisin : un échec d'écriture laisse `destination` intact.

    Un caractère qui ne s'encode pas en UTF-8 (une moitié de paire de substitution) est remplacé
    par U+FFFD : une seule ligne de ce genre n'empêche pas de dumper tout le projet.

    Raises:
        OSError: l'écriture a échoué ; rien n'a changé à `destination`.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    neuf = destination.parent / f".{destination.name}.neuf-{os.getpid()}"
    shutil.rmtree(neuf, ignore_errors=True)
    neuf.mkdir()
    try:
        for nom, texte in contenus.items():
            (neuf / nom).write_text(SUBSTITUT_SEUL.sub("\ufffd", texte), encoding="utf-8")
        destination.mkdir(exist_ok=True)
        for ancien in destination.iterdir():
            if ancien.is_dir() and not ancien.is_symlink():
                shutil.rmtree(ancien)
            else:
                ancien.unlink()
        for ecrit in neuf.iterdir():
            ecrit.rename(destination / ecrit.name)
    finally:
        # Quelle que soit l'issue, le répertoire en construction ne reste pas sur le disque.
        shutil.rmtree(neuf, ignore_errors=True)


def dumper(projet: Path, environ: Mapping[str, str]) -> Bilan | Echec:
    """Écrit un dump par session principale de `projet` dans `<projet>/.claude/session-dump/<id>/`.

    Une session sans aucun tour n'est pas une discussion : elle n'est pas dumpée, et le bilan la
    compte. Le dump de la session en cours y figure, partiel.
    """
    if not projet.is_dir():
        return Echec(2, f"session-dump : {projet} n'est pas un répertoire.")
    projet = projet.resolve()
    identifiant = id_projet(projet)
    source = repertoire_config(environ) / "projects" / identifiant
    if not source.is_dir():
        return Echec(1, f"session-dump : aucune session pour {projet} — attendu : {source}.")

    sessions: list[Session] = []
    corps: dict[str, Sequence[Ligne]] = {}
    ecartes = 0
    illisibles = 0
    for chemin in sessions_du_projet(source):
        lignes, ill = lire_jsonl(chemin)
        session = analyser_lignes(chemin, lignes, ill)
        illisibles += session.illisibles
        if session.tours == 0:
            ecartes += 1
            continue
        sessions.append(session)
        corps[session.uuid] = lignes

    noms = noms_de_fichiers(sessions)
    contenus = {noms[s.uuid]: rendre(s, corps[s.uuid]) for s in sessions}
    destination = projet / ".claude" / "session-dump" / identifiant
    try:
        remplacer(destination, contenus)
    except OSError as erreur:
        return Echec(1, f"session-dump : écriture impossible dans {destination} : {erreur}")
    return Bilan(destination, len(contenus), ecartes, illisibles)
