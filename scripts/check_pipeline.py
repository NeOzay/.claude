#!/usr/bin/env python3
"""Garde-fou du pipeline de skills : vérifie que le contrat partagé n'a pas dérivé.

PORTÉE : sept contrôles, tous mécaniques. Ce script ne juge ni le contenu ni la
pertinence des règles — il constate que chacune reste définie à un seul endroit et
que les renvois qui y mènent résolvent encore.

ÉCHEC FERMÉ : sortie 1 dès qu'un contrôle échoue. C'est un outil de vérification,
contrairement à hooks/intent-brief-gate.sh qui est pédagogique et échoue ouvert.

UN CONTRÔLE QUI N'EXAMINE RIEN ÉCHOUE. Un motif qui ne matche plus rien, une liste
vide, un répertoire absent : tous signalés comme erreurs, jamais comme succès. Un
garde-fou silencieusement vide est pire que pas de garde-fou. La règle est ici
structurelle : un contrôle rend un Finding(ok=False) explicite quand sa population
d'entrée est vide, et jamais une liste de constats vide — que `main` compterait
comme un succès.

LES AGENTS SONT HORS PÉRIMÈTRE des contrôles 1 et 2. agents/step-implementer.md et
agents/implementation-auditor.md dupliquent volontairement les règles qui les
concernent : ils se chargent dans leur propre fenêtre, et un agent en isolation qui
ne suivrait pas un renvoi perdrait le garde-fou. Le contrôle 4 vérifie justement
qu'ils n'ont pas été rendus dépendants du noyau.

COLLECTE ET JUGEMENT SÉPARÉS : chaque contrôle est une fonction pure qui reçoit la
racine du dépôt et rend des Finding. Aucune ne lit sys.argv, aucune n'imprime,
aucune n'appelle exit — c'est ce qui les rend testables une par une, sur une
arborescence-jouet.
"""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import cast

CONTRAT = "skills/implementation-tracker/references/contrat.md"

# Zones que les contrôles de renvois n'inspectent jamais. `agents/` est un
# hors-périmètre de conception (voir l'en-tête) ; `.claude/implementation/` porte des
# archives figées et un registre de dette qui *décrit* des renvois morts — les
# scanner ferait crier le garde-fou sur des documents datés qu'on ne réécrit pas.
ZONES_EXCLUES = (
    "agents",
    ".git",
    "plugins",
    ".claude/implementation",
    ".claude/plans",
    "node_modules",
)


@dataclass(frozen=True)
class Finding:
    """Un constat élémentaire. `ok=False` compte pour une anomalie, une seule."""

    ok: bool
    message: str


@dataclass(frozen=True)
class Control:
    number: int
    title: str
    run: Callable[[Path], list[Finding]]


CONTROLS: list[Control] = []


def control(number: int, title: str) -> Callable[
    [Callable[[Path], list[Finding]]], Callable[[Path], list[Finding]]
]:
    """Enregistre une fonction de contrôle. L'ordre d'exécution est celui des numéros."""

    def register(fn: Callable[[Path], list[Finding]]) -> Callable[[Path], list[Finding]]:
        CONTROLS.append(Control(number, title, fn))
        CONTROLS.sort(key=lambda c: c.number)
        return fn

    return register


def repo_root() -> Path | None:
    """La racine du dépôt git courant, ou None hors dépôt."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if out.returncode != 0:
        return None
    return Path(out.stdout.strip())


def fichiers_versionnables(root: Path) -> list[Path] | None:
    """Les `.md` que git suit ou suivrait, ou None hors dépôt git.

    `--cached --others --exclude-standard` : les fichiers suivis PLUS les nouveaux qui
    ne sont pas ignorés. Un `.md` déposé par un outil dans un répertoire ignoré —
    `cache/` en porte déjà un — n'a rien à faire dans le jugement du garde-fou : son
    auteur ne peut pas le corriger, et le rouge serait sans cause.
    """
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others",
         "--exclude-standard", "--", "*.md"],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode != 0:
        return None
    return [root / nom for nom in out.stdout.split("\0") if nom]


def markdown_files(root: Path, *, only: str | None = None) -> Iterator[Path]:
    """Les `.md` du dépôt, hors zones exclues et hors fichiers ignorés par git.

    `only` restreint à un sous-répertoire (« skills » pour les contrôles qui ne
    regardent que le noyau du pipeline). Hors dépôt git — le cas des tests — on retombe
    sur un parcours du disque : c'est la liste des fichiers qui change, pas le jugement.
    """
    base = root / only if only else root
    if not base.is_dir():
        return
    versionnables = fichiers_versionnables(root)
    candidats = (
        sorted(p for p in versionnables if p.is_relative_to(base))
        if versionnables is not None
        else sorted(base.rglob("*.md"))
    )
    for path in candidats:
        rel = path.relative_to(root).as_posix()
        if any(rel == z or rel.startswith(z + "/") for z in ZONES_EXCLUES):
            continue
        yield path


def slugify(title: str) -> str:
    """L'ancre que GitHub donne à un titre de section.

    Minuscules, ponctuation retirée, espaces en tirets — les lettres accentuées
    RESTENT (« Format d'étape » donne « format-détape »). L'ancienne version bash ne
    retirait que les apostrophes : une virgule ou une parenthèse dans un titre
    produisait une ancre fausse, invisible au contrôle puisque les deux côtés de la
    comparaison passaient par la même fonction.
    """
    kept = "".join(c for c in title.strip().lower() if c.isalnum() or c in " -_")
    return kept.replace(" ", "-")


def sections(texte: str) -> dict[str, str]:
    """Les sections `## ` d'un document : ancre → corps, dans l'ordre du fichier.

    Les blocs de code sont sautés : un `## ` à l'intérieur d'une fence est du contenu,
    pas un titre. C'est exactement le défaut qu'un auditeur avait trouvé dans
    `parse_sections` de listdir, découvert par lecture et non par un test.
    """
    trouvees: dict[str, str] = {}
    ancre: str | None = None
    corps: list[str] = []
    dans_fence = False
    for ligne in texte.splitlines():
        if ligne.lstrip().startswith("```"):
            dans_fence = not dans_fence
        if not dans_fence and ligne.startswith("## "):
            if ancre is not None:
                trouvees[ancre] = "\n".join(corps)
            ancre, corps = slugify(ligne.removeprefix("## ")), []
            continue
        corps.append(ligne)
    if ancre is not None:
        trouvees[ancre] = "\n".join(corps)
    return trouvees


TITRE = re.compile(r"^(#{1,6}) +(.+?)\s*$")


def ancres_markdown(texte: str) -> set[str]:
    """Toutes les ancres d'un document, quel que soit le niveau du titre.

    Distinct de `sections()`, qui ne retient que les `## ` parce que le contrôle 1
    juge la couverture des sections de premier rang du contrat. Ici la question est
    autre : un lien peut viser un `###` parfaitement légitime, et le déclarer mort
    serait un faux positif — celui que l'audit de clôture a trouvé par sonde.

    Les blocs de code sont sautés, pour la même raison que dans `sections()`.
    """
    trouvees: set[str] = set()
    dans_fence = False
    for ligne in texte.splitlines():
        if ligne.lstrip().startswith("```"):
            dans_fence = not dans_fence
            continue
        if dans_fence:
            continue
        m = TITRE.match(ligne)
        if m is not None:
            trouvees.add(slugify(cast("str", m.group(2))))
    return trouvees


LIEN_CONTRAT = re.compile(r"\]\(([^)#]*contrat\.md)#([^)]*)\)")


@control(1, "Renvois vers le contrat")
def check_renvois(root: Path) -> list[Finding]:
    contrat = root / CONTRAT
    if not contrat.is_file():
        return [Finding(False, f"contrat introuvable ({CONTRAT})")]

    ancres = set(sections(contrat.read_text(encoding="utf-8")))
    findings: list[Finding] = []
    if not ancres:
        findings.append(
            Finding(False, "aucune section dans le contrat — fichier vidé ou restructuré")
        )

    total = 0
    citees: set[str] = set()
    for md in markdown_files(root):
        for m in LIEN_CONTRAT.finditer(md.read_text(encoding="utf-8")):
            chemin, ancre = cast("str", m.group(1)), cast("str", m.group(2))
            total += 1
            rel = md.relative_to(root)
            cible = (md.parent / chemin).resolve()
            if not cible.is_file():
                findings.append(Finding(False, f"{rel} → chemin mort : {chemin}"))
            elif ancre not in ancres:
                findings.append(Finding(False, f"{rel} → ancre morte : #{ancre}"))
            elif md != contrat:
                # L'auto-citation ne compte pas : l'exemple de renvoi que contrat.md
                # porte dans sa propre prose satisfaisait à lui seul « section jamais
                # citée », qui ne prouvait donc rien.
                citees.add(ancre)

    if total == 0:
        findings.append(
            Finding(False, "aucun renvoi trouvé — le contrat n'est cité nulle part")
        )
    elif not any(not f.ok for f in findings):
        findings.append(Finding(True, f"{total} renvois, tous résolvent"))

    findings.extend(
        Finding(False, f"section jamais citée : #{a}") for a in sorted(ancres - citees)
    )
    return findings


# Chaque motif est une formulation distinctive du CORPS d'une règle — jamais d'une
# ligne d'appel — rattachée à la section qu'elle protège. Table construite
# empiriquement le 2026-08-14, rattachée aux sections le 2026-08-24 : chaque motif
# n'avait alors qu'une occurrence dans skills/, dans sa section. Exactement une reste
# la règle, dans les deux sens — 0 signifie que la définition a disparu du contrat,
# ≥ 2 qu'elle a été recopiée.
#
# LE RATTACHEMENT EST CE QUI REND LA TABLE VÉRIFIABLE : une section du contrat sans
# empreinte n'est protégée par rien, et rien ne le disait tant que la table n'était
# qu'une liste plate. Une section porte une ou plusieurs empreintes, jamais zéro.
EMPREINTES: dict[str, tuple[str, ...]] = {
    "arborescence-et-nommage": (
        "refonte-complete-du-systeme-dauth",  # contre-exemple de slug
        "réattribue ces noms",  # nommage du plan archivé
    ),
    "frontmatter": ("Une valeur absente vaut",),
    "autorité-et-divergence": ("le suivi fait foi",),
    "format-détape-et-délégabilité": ("un seul tour",),  # granularité
    "contrat-des-sous-agents": ("rev-parse --show-toplevel",),  # racine du dépôt
    "branche-et-commits": ("ramasse ce qui traîne",),  # staging
    "dates-et-listing": ("jamais devinée",),
}


@control(2, "Règles définies à un seul endroit")
def check_empreintes(root: Path) -> list[Finding]:
    contrat = root / CONTRAT
    if not contrat.is_file():
        return [Finding(False, f"contrat introuvable ({CONTRAT})")]

    corps = sections(contrat.read_text(encoding="utf-8"))
    findings: list[Finding] = []

    if not corps:
        findings.append(Finding(False, "aucune section dans le contrat"))
    findings.extend(
        Finding(False, f"section sans empreinte : #{a} — la règle n'est protégée par rien")
        for a in sorted(set(corps) - set(EMPREINTES))
    )
    findings.extend(
        Finding(False, f"empreinte orpheline : #{a} n'est plus une section du contrat")
        for a in sorted(set(EMPREINTES) - set(corps))
    )

    textes = {md: md.read_text(encoding="utf-8") for md in markdown_files(root, only="skills")}
    if not textes:
        findings.append(Finding(False, "aucun fichier examiné dans skills/"))

    for ancre, motifs in EMPREINTES.items():
        for motif in motifs:
            # Des OCCURRENCES, pas des fichiers : deux copies d'une même règle dans un
            # seul fichier passaient au vert alors que la règle dit « exactement une ».
            n = sum(texte.count(motif) for texte in textes.values())
            if n == 0:
                findings.append(Finding(False, f"« {motif} » : introuvable — la règle a disparu"))
            elif n > 1:
                findings.append(Finding(False, f"« {motif} » : {n} occurrences — règle recopiée"))
            elif motif not in corps.get(ancre, ""):
                findings.append(
                    Finding(False, f"« {motif} » : hors de la section #{ancre} qu'elle protège")
                )
            else:
                findings.append(Finding(True, f"« {motif} » (#{ancre})"))

    return findings


LISTER = "skills/implementation-tracker/scripts/impl_list.py"
IMPLEMENTATION = ".claude/implementation"
ANNEXES = (".brief.md", ".audit.md", ".plan.md")


def charger_suivis(root: Path) -> Callable[[Path], list[str]] | None:
    """La fonction `suivis()` du LISTER **du dépôt audité**, ou None s'il est absent.

    Copie du dépôt, jamais la skill installée : le garde-fou doit juger ce que le diff
    contient — sur un clone ailleurs, viser $HOME validerait un fichier étranger au
    chantier. Et on importe plutôt qu'on ne sous-processe : c'est le même code que la
    CLI, les deux ne peuvent donc pas diverger.
    """
    chemin = root / LISTER
    if not chemin.is_file():
        return None
    spec = importlib.util.spec_from_file_location("_impl_list_audite", chemin)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = getattr(module, "suivis", None)
    return cast("Callable[[Path], list[str]]", fn) if callable(fn) else None


@control(3, "Filtre de listing des suivis")
def check_listing(root: Path) -> list[Finding]:
    suivis = charger_suivis(root)
    if suivis is None:
        return [Finding(False, f"script de listing absent ou sans suivis() : {LISTER}")]

    listing = suivis(root / IMPLEMENTATION / "done")
    if not listing:
        return [Finding(False, "aucun fichier examiné dans done/ — contrôle sans objet")]

    parasites = [n for n in listing if n.endswith(ANNEXES)]
    if parasites:
        return [Finding(False, f"{len(parasites)} fichiers parasites remontés par le listing")]
    return [Finding(True, f"{len(listing)} fichiers listés, aucun brief/audit/plan")]


@control(4, "Indépendance des sous-agents")
def check_agents(root: Path) -> list[Finding]:
    """Un agent se charge dans sa propre fenêtre : un renvoi au contrat lui coûterait
    la règle qu'il ne pourrait pas suivre. La duplication y est donc voulue."""
    agents = root / "agents"
    if not agents.is_dir():
        return [Finding(False, "répertoire agents/ absent — contrôle sans objet")]

    fichiers = sorted(agents.glob("*.md"))
    if not fichiers:
        return [Finding(False, "aucun agent examiné — contrôle sans objet")]

    couples = [
        f for f in fichiers if "contrat.md" in f.read_text(encoding="utf-8")
    ]
    if couples:
        return [
            Finding(
                False,
                f"{f.relative_to(root)} renvoie au contrat : un agent isolé doit rester auto-suffisant",
            )
            for f in couples
        ]
    return [Finding(True, f"{len(fichiers)} agents, aucun renvoi au contrat")]


@control(5, "Chemins du frontmatter des chantiers archivés")
def check_archives(root: Path) -> list[Finding]:
    suivis = charger_suivis(root)
    if suivis is None:
        return [Finding(False, f"script de listing absent ou sans suivis() : {LISTER}")]

    done = root / IMPLEMENTATION / "done"
    archives = suivis(done)
    if not archives:
        return [Finding(False, "aucun suivi archivé examiné — contrôle sans objet")]

    findings: list[Finding] = []
    for nom in archives:
        texte = (done / nom).read_text(encoding="utf-8")
        for champ in ("plan", "brief", "audit"):
            m = re.search(rf"^{champ}: *(\S.*)$", texte, re.MULTILINE)
            if m is None:
                continue
            cible = cast("str", m.group(1)).strip()
            if not (root / cible).is_file():
                findings.append(
                    Finding(False, f"{nom} → {champ}: pointe dans le vide ({cible})")
                )
    if not findings:
        findings.append(
            Finding(True, f"{len(archives)} archives, tous les champs plan/brief/audit résolvent")
        )
    return findings


# Un skill s'invoque depuis n'importe quel dépôt. Un chemin de script relatif au dépôt
# courant y renvoie code 127 et une sortie VIDE — que l'appelant lit comme un résultat,
# pas comme une erreur. Les scripts d'un skill s'appellent donc par chemin absolu ancré
# dans la skill. Ce contrôle existe parce que l'audit du 2026-08-14 a bloqué la clôture
# sur exactement ce défaut.
#
# DEUX INTERPRÉTEURS, `bash …*.sh` et `python3 …*.py` : un appel `python3 scripts/x.py`
# échoue exactement de la même façon — 127 et rien sur stdout. Un contrôle qui ne couvre
# qu'une moitié de ce qu'il protège finit par donner l'assurance qu'il n'a plus.
#
# `python3 -c`, `python3 - <<'PY'` et `python3 "$L"` ne sont pas concernés : aucun ne
# porte un chemin de fichier en clair. La variable est résolue à l'exécution, et c'est
# sa définition — non cet appel — qui doit être absolue.
#
# APPEL DIRECT, sans interpréteur : les scripts de skill portent leur shebang et
# s'exposent dans `bin/`, donc la forme employée est `list-dir validate …` — ou, pour
# ce qui n'a pas de lien, un chemin nu sans `python3` devant. Un contrôle resté sur
# `bash|python3` serait devenu aveugle à tout ce qui a été converti, c'est-à-dire vert
# sans rien examiner. Ce motif ne s'applique qu'à l'intérieur d'un bloc ```bash et en
# tête de commande, faute de quoi un chemin cité en prose deviendrait un appel.
APPEL = re.compile(r"\b(?:bash|python3)\s+\"?([^\"\s;)]+\.(?:sh|py))")
APPEL_DIRECT = re.compile(r"(?:^|[;&|]\s*|\$\(\s*)\"?([^\"\s;)]+\.(?:sh|py))\"?(?=\s|$)")
ABSOLUS = ("/", "~/", "$HOME/", "${HOME}/")


def blocs_bash(texte: str) -> Iterator[list[tuple[int, str]]]:
    """Les blocs ```bash d'un markdown, en (numéro de ligne, contenu).

    Le découpage est volontairement littéral : ce qui n'est pas dans un bloc `bash`
    n'est pas une commande à exécuter, et n'a donc pas à porter de garde.
    """
    bloc: list[tuple[int, str]] | None = None
    for no, ligne in enumerate(texte.splitlines(), 1):
        depouille = ligne.strip()
        if bloc is None:
            if depouille.startswith("```") and depouille[3:].strip() in ("bash", "sh"):
                bloc = []
            continue
        if depouille.startswith("```"):
            yield bloc
            bloc = None
            continue
        bloc.append((no, ligne))
    if bloc:
        yield bloc


def garde_commande(ligne: str, appel: str, debut_appel: int) -> bool:
    """Vrai si un `[ -f <appel> ]` **commande** cet appel, sur cette ligne.

    Deux exigences, chacune née d'un faux vert : le garde doit porter sur le script
    qu'on lance (d'où re.escape — les `.` d'un chemin sont des métacaractères), et il
    doit le PRÉCÉDER. `bash x.sh  # [ -f x.sh ]` passait au vert : le test cherchait la
    chaîne n'importe où dans la ligne, y compris derrière un commentaire.
    """
    motif = re.compile(r"\[\s*-f\s+\"?" + re.escape(appel) + r"\"?\s*\]")
    for m in motif.finditer(ligne):
        if m.start() >= debut_appel:
            continue
        commentaire = ligne.find("#")
        if 0 <= commentaire < m.start():
            continue
        return True
    return False


@control(6, "Portabilité des appels de script")
def check_portabilite(root: Path) -> list[Finding]:
    fichiers = list(markdown_files(root, only="skills"))
    if not fichiers:
        return [Finding(False, "aucun fichier examiné dans skills/ — contrôle sans objet")]

    findings: list[Finding] = []
    for md in fichiers:
        texte = md.read_text(encoding="utf-8")
        for ligne in texte.splitlines():
            for m in APPEL.finditer(ligne):
                appel = cast("str", m.group(1))
                if appel.startswith(ABSOLUS):
                    continue
                if garde_commande(ligne, appel, m.start()):
                    continue
                findings.append(
                    Finding(
                        False,
                        f"appel relatif non gardé : {md.relative_to(root)} → {appel}"
                        " — inopérant et silencieux hors de ~/.claude",
                    )
                )
        for bloc in blocs_bash(texte):
            for no, ligne in bloc:
                for m in APPEL_DIRECT.finditer(ligne):
                    appel = cast("str", m.group(1))
                    if appel.startswith(ABSOLUS) or appel.startswith("$"):
                        continue
                    if garde_commande(ligne, appel, m.start()):
                        continue
                    findings.append(
                        Finding(
                            False,
                            f"appel relatif non gardé : {md.relative_to(root)}:{no} → {appel}"
                            " — inopérant et silencieux hors de ~/.claude",
                        )
                    )
    if not findings:
        findings.append(
            Finding(True, f"{len(fichiers)} fichiers examinés, aucun appel relatif non gardé")
        )
    return findings


# Le chemin de la skill est écrit EN DUR, et le contrôle 6 impose cette forme : chaque
# skill neuve ajoute donc ses points d'édition, et aucun n'échoue bruyamment s'il est
# oublié. Ce contrôle ne supprime pas la cause — il rend l'oubli visible. La cause reste
# au registre de dette sous `chemin-skill-code-en-dur`.
#
# `$HOME/.claude` DÉSIGNE LE DÉPÔT AUDITÉ, pas le home de qui lance le script : sur un
# clone ailleurs, résoudre vers le vrai $HOME validerait des fichiers étrangers au
# chantier — exactement ce que le garde-fou existe pour ne pas faire.
# Deux écritures d'un même chemin : ancrée sur le HOME (`$HOME/.claude/skills/x`) ou
# relative à la racine du dépôt (`skills/x`). La première est REFUSÉE depuis le solde de
# `chemin-skill-code-en-dur` : elle suppose le dépôt installé dans `~/.claude`, et c'est
# cette supposition, recopiée à chaque point d'usage, qui a fait passer le compte de 3 à
# 8 points d'édition sans qu'aucun n'échoue bruyamment. La seconde est vérifiée, jamais
# supposée. Le motif garde les deux : on ne peut refuser que ce qu'on sait reconnaître.
CHEMIN_SKILL = re.compile(
    r"(?:(?:\$HOME|\$\{HOME\}|~)/\.claude/(?P<home>[^\"\s)`,;]+)"
    r"|(?<![\w/.])(?P<rel>skills/[^\"\s)`,;]+))"
)


def commandes_bin(root: Path) -> dict[str, str]:
    """Les commandes exposées dans `bin/`, par chemin de cible relatif au dépôt.

    C'est le point de rendez-vous du système : un exécutable qui y a son lien s'appelle
    PAR SON NOM. Continuer à l'appeler par son chemin, c'est rouvrir la dette
    `chemin-skill-code-en-dur` — un point d'édition de plus, qu'un déplacement ou un
    renommage casse en silence.
    """
    bin_dir = root / "bin"
    if not bin_dir.is_dir():
        return {}
    table: dict[str, str] = {}
    for lien in bin_dir.iterdir():
        if not lien.is_symlink():
            continue
        cible = (bin_dir / os.readlink(lien)).resolve()
        try:
            table[cible.relative_to(root).as_posix()] = lien.name
        except ValueError:
            continue  # pointe hors du dépôt : le script de santé s'en charge
    return table


@control(7, "Chemins de skill cités : existence et forme")
def check_chemins_skill(root: Path) -> list[Finding]:
    # Les `.md` de la racine comptent : `OUTILLAGE.md` cite des chemins de skill, et
    # un chemin faux y trompe autant qu'ailleurs.
    fichiers = [*markdown_files(root, only="skills"), *root.glob("*.md")]
    if not fichiers:
        return [Finding(False, "aucun fichier examiné — contrôle sans objet")]

    commandes = commandes_bin(root)
    cites = 0
    findings: list[Finding] = []
    for md in fichiers:
        for ligne_no, ligne in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for m in CHEMIN_SKILL.finditer(ligne):
                brut = m.group("home") or m.group("rel")
                rel = cast("str", brut).rstrip("/")
                if m.group("home") is not None and not rel.startswith("skills/"):
                    continue  # `$HOME/.claude/…` hors skills/ : pas notre affaire ici
                if any(c in rel for c in "<>*…"):
                    continue  # gabarit, pas un chemin
                cites += 1
                if m.group("home") is not None:
                    findings.append(
                        Finding(
                            False,
                            f"{md.relative_to(root)}:{ligne_no} → chemin ancré sur le HOME :"
                            f" {rel} — écrire le chemin relatif à la racine du dépôt, ou"
                            " appeler la commande de bin/",
                        )
                    )
                    continue
                cible = root / rel
                if not cible.exists():
                    findings.append(
                        Finding(
                            False,
                            f"{md.relative_to(root)}:{ligne_no} → chemin de skill inexistant : {rel}",
                        )
                    )
                elif rel in commandes:
                    findings.append(
                        Finding(
                            False,
                            f"{md.relative_to(root)}:{ligne_no} → {rel} s'appelle par son nom :"
                            f" « {commandes[rel]} » — un chemin de plus est un point d'édition"
                            " de plus, que le prochain déplacement casse en silence",
                        )
                    )
    if cites == 0:
        findings.append(Finding(False, "aucun chemin de skill cité — contrôle sans objet"))
    elif not findings:
        findings.append(Finding(True, f"{cites} chemins de skill cités, tous existent"))
    return findings


# Un skill en cite un autre de deux façons : il l'APPELLE (contrôles 6 et 7, chemin
# ancré sur la racine résolue) ou il y RENVOIE le lecteur. Le renvoi est un lien
# Markdown relatif — forme retenue parce qu'elle reste cliquable et survit à un
# déplacement de la racine. Ce qu'elle ne supporte pas, c'est le RENOMMAGE d'un skill :
# le lien pointe alors dans le vide sans que rien ne le signale, et le lecteur — modèle
# ou humain — lit un renvoi mort comme une section absente. D'où ce contrôle.
RENVOI_INTER_SKILL = re.compile(r"\]\((\.\./[^)#\s]+)(#[^)\s]+)?(?:\s+\"[^\"]*\")?\)")


@control(8, "Renvois documentaires entre skills")
def check_renvois_skill(root: Path) -> list[Finding]:
    fichiers = list(markdown_files(root, only="skills"))
    if not fichiers:
        return [Finding(False, "aucun fichier examiné dans skills/ — contrôle sans objet")]

    cites = 0
    findings: list[Finding] = []
    for md in fichiers:
        for ligne_no, ligne in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for m in RENVOI_INTER_SKILL.finditer(ligne):
                rel = cast("str", m.group(1))
                if any(c in rel for c in "<>*…"):
                    continue  # gabarit, pas un chemin
                cites += 1
                cible = md.parent / rel
                if not cible.exists():
                    findings.append(
                        Finding(
                            False,
                            f"{md.relative_to(root)}:{ligne_no} → renvoi mort : {rel}",
                        )
                    )
                    continue
                # L'ANCRE FAIT PARTIE DU RENVOI. Sans ce contrôle, un lien vers une
                # section renommée reste vert et dépose le lecteur en tête d'une
                # référence de 400 lignes — c'est-à-dire le mode de défaillance même
                # que ce contrôle invoque pour exister.
                ancre = m.group(2)
                if ancre is None or not cible.is_file():
                    continue
                connues = ancres_markdown(cible.read_text(encoding="utf-8"))
                if cast("str", ancre)[1:] not in connues:
                    findings.append(
                        Finding(
                            False,
                            f"{md.relative_to(root)}:{ligne_no} → ancre morte :"
                            f" {rel}{ancre} — le renvoi fonctionne, il ne conduit pas",
                        )
                    )
    if cites == 0:
        findings.append(Finding(False, "aucun renvoi entre skills — contrôle sans objet"))
    elif not findings:
        findings.append(Finding(True, f"{cites} renvois entre skills, tous résolvent"))
    return findings


def main() -> int:
    root = repo_root()
    if root is None:
        sys.stderr.write("FATAL : hors d'un dépôt git.\n")
        return 1

    fails = 0
    for ctl in CONTROLS:
        print(f"\n{ctl.number}. {ctl.title}")
        findings = ctl.run(root)
        if not findings:
            # Un contrôle muet est un contrôle qui n'a rien examiné : la règle de
            # l'en-tête interdit de le lire comme un succès.
            print("  ✗ aucun constat rendu — contrôle sans objet")
            fails += 1
            continue
        for f in findings:
            print(f"  {'✓' if f.ok else '✗'} {f.message}")
            fails += 0 if f.ok else 1

    if not CONTROLS:
        print("\n✗ aucun contrôle exécuté — le registre est vide")
        fails += 1

    print()
    if fails == 0:
        print("Pipeline conforme.")
        return 0
    print(f"{fails} anomalie(s).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
