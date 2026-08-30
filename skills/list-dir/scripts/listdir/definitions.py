"""Définitions de listes : où les trouver, et laquelle gagne.

UNE DÉFINITION EST LE CONTENU D'UN FUTUR `.list/` — un `contract.toml`, et un
`templates/` facultatif. Elle vit hors de tout répertoire-liste, ce qui est
exactement ce qui la rend utilisable au moment où aucune liste n'existe encore.

DÉCOUVERTE PAR LE SYSTÈME DE FICHIERS, jamais par un registre à tenir à jour :
même principe que loader.py pour les commandes, et pour la même raison — un
registre se désynchronise, une arborescence non.

LES QUATRE RANGS, du plus spécifique au plus général :

  1  <projet>/.claude/list-dir/<nom>/
  2  <projet>/.claude/skills/*/list-dir/<nom>/
  3  <config>/list-dir/<nom>/
  4  <config>/skills/*/list-dir/<nom>/

La spécificité prime, comme une commande de `.list/commands/` prime sur une
générique : le rang 1 MASQUE le rang 4, et c'est un succès, pas un conflit. Une
ambiguïté ne se déclare qu'à RANG ÉGAL — deux skills qui définissent le même nom.

CE MODULE NE NOMME AUCUN CONSOMMATEUR. Il décrit une forme ; ce qu'on range dedans
ne le regarde pas. C'est ce qui garde `list-dir` déployable ailleurs.

AUCUNE CONSTANTE DE CHEMIN, aucune variable d'environnement, aucune dépendance
externe : les deux ancrages sortent de la MÊME remontée, l'une depuis le répertoire
courant, l'autre depuis ce fichier. `Path(__file__)` est déjà le motif de
loader.GENERIC_DIR.

POURQUOI PAS `shutil.which("list-dir")` : il rend None quand le paquet est appelé
par son chemin plutôt que par le lien de `bin/`, et les rangs 3 et 4 disparaîtraient
alors EN SILENCE — un échec ouvert, ce que ce paquet existe pour supprimer. Un
index fixe sur `parents[…]` suppose en outre une installation en
`~/.claude/skills/list-dir/`, que rien ne garantit.

LES DEUX REMONTÉES NE CHERCHENT PAS LA MÊME CHOSE, et les confondre casse le cas
imbriqué. Un projet est un répertoire qui CONTIENT un `.claude` ; la configuration
est un répertoire QUI EST un `.claude`. Sur ce dépôt-ci — la configuration est
`~/.claude` et porte son propre `~/.claude/.claude` — une règle unique ferait
répondre la même chose aux deux questions, et l'un des deux rangs viserait le
mauvais répertoire.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .contract import CONTRACT
from .types import Result, fail, ok

CLAUDE = ".claude"
SKILLS = "skills"
DEFS = "list-dir"
"""Le répertoire qu'une racine porte. Le nom est celui du skill : une définition de
liste se range sous le nom de ce qui sait la lire."""


@dataclass(frozen=True)
class Root:
    """Une racine de définitions, et d'où elle vient.

    `origin` n'est pas cosmétique : sans elle, `defs` dirait qu'un nom est
    définissable sans dire par qui, et deux définitions homonymes seraient
    indiscernables dans le message qui les refuse.
    """

    path: Path
    rank: int
    origin: str

    def names(self) -> list[str]:
        """Les définitions présentes ici — un répertoire portant un `contract.toml`.

        Un répertoire sans contrat n'est pas une définition à moitié faite : ce n'en
        est pas une. L'ignorer ici vaut mieux que le proposer à `--def` pour échouer
        ensuite sur un fichier manquant.
        """
        if not self.path.is_dir():
            return []
        return sorted(d.name for d in self.path.iterdir() if (d / CONTRACT).is_file())


def project_root(start: Path) -> Path | None:
    """Le `.claude` du premier projet trouvé en remontant depuis `start`, ou None.

    Un projet est un répertoire qui CONTIENT un `.claude`. La remontée s'arrête au
    premier, qui n'est pas nécessairement celui qu'on aurait choisi : `defs`
    l'imprime pour que le choix soit visible plutôt que deviné.

    Hors de tout projet, None — un état parfaitement légitime, pas une erreur : il
    n'y a alors simplement rien à proposer aux rangs 1 et 2.
    """
    here = start.resolve()
    for candidate in (here, *here.parents):
        if (candidate / CLAUDE).is_dir():
            return candidate / CLAUDE
    return None


def config_root(start: Path) -> Path | None:
    """Le premier répertoire NOMMÉ `.claude` en remontant depuis `start`, ou None.

    La configuration est un `.claude`, elle n'en contient pas un — c'est toute la
    différence avec `project_root`, et elle compte : sur ce dépôt-ci, `~/.claude`
    porte son propre `~/.claude/.claude`, si bien que la règle du projet répondrait
    `~/.claude/.claude` là où l'ancrage du paquet veut `~/.claude`.

    None quand le paquet est déployé hors de toute configuration `.claude` : les
    rangs 3 et 4 sont alors absents, et `defs` le dit au lieu de le taire.
    """
    here = start.resolve()
    for candidate in (here, *here.parents):
        if candidate.name == CLAUDE and candidate.is_dir():
            return candidate
    return None


def _pair(base: Path, rank: int, label: str) -> list[Root]:
    """Les deux rangs d'un même `.claude` : le sien, puis ceux de ses skills."""
    roots = [Root(base / DEFS, rank, label)]
    skills = base / SKILLS
    if skills.is_dir():
        roots += [
            Root(d / DEFS, rank + 1, f"{label}:{d.name}")
            for d in sorted(skills.iterdir())
            if (d / DEFS).is_dir()
        ]
    return roots


def roots(cwd: Path | None = None, package: Path | None = None) -> list[Root]:
    """Les quatre rangs, dédupliqués, du plus spécifique au plus général.

    LES DEUX ANCRAGES SONT DES PARAMÈTRES, et pas des constantes lues au vol : c'est
    ce qui rend la découverte testable sur un tmp_path. Un module qui lit `Path.cwd()`
    en dur ne se teste qu'en changeant le répertoire courant du processus, ce qu'une
    suite parallèle ne pardonne pas.

    DÉDUPLICATION SUR CHEMIN RÉSOLU, et c'est un cas réel, pas une précaution : le
    dépôt de configuration EST `~/.claude` et CONTIENT `~/.claude/.claude`. Une même
    racine atteinte par les deux remontées se dénoncerait sinon comme ambiguë avec
    elle-même.
    """
    found: list[Root] = []
    projet = project_root(cwd if cwd is not None else Path.cwd())
    if projet is not None:
        found += _pair(projet, 1, "projet")
    config = config_root(package if package is not None else Path(__file__).parent)
    if config is not None:
        found += _pair(config, 3, "config")

    # Le premier vu gagne : `found` est déjà dans l'ordre de spécificité, donc
    # l'exemplaire conservé est toujours celui du rang le plus fort.
    vus: set[Path] = set()
    uniques: list[Root] = []
    for root in found:
        resolved = root.path.resolve()
        if resolved in vus:
            continue
        vus.add(resolved)
        uniques.append(root)
    return uniques


def definitions(where: list[Root]) -> dict[str, list[Root]]:
    """Tout ce qui est définissable, par nom, racines dans l'ordre de spécificité.

    La valeur est une LISTE et non une racine unique : c'est elle qui porte de quoi
    dire « le rang 1 masque le rang 4 » à `defs`, et de quoi nommer les deux fautives
    quand elles sont à égalité.
    """
    par_nom: dict[str, list[Root]] = {}
    for root in where:
        for name in root.names():
            par_nom.setdefault(name, []).append(root)
    return par_nom


def resolve(name: str, where: list[Root]) -> Result[Path]:
    """Le répertoire de définition retenu pour `name`.

    TROIS ISSUES, et pas une de plus :
      - un seul rang le porte, ou plusieurs à des rangs différents → le plus
        spécifique gagne. Masquer est le comportement voulu : c'est ainsi qu'un
        projet reprend la main sur une définition de la configuration ;
      - deux racines DE MÊME RANG le portent → échec les nommant toutes les deux.
        Choisir en silence ferait dépendre le contrat d'une liste de l'ordre de
        parcours d'un répertoire ;
      - personne → échec listant les noms connus, comme le fait `list-dir.py` pour
        une commande inconnue. Un « introuvable » sec obligerait à aller lire
        l'arborescence pour trouver l'orthographe exacte.
    """
    candidates = definitions(where).get(name, [])
    if not candidates:
        connues = ", ".join(sorted(definitions(where))) or "aucune"
        return fail(f"définition « {name} » introuvable ; connues : {connues}")

    best = candidates[0].rank
    exaequo = [r for r in candidates if r.rank == best]
    if len(exaequo) > 1:
        chemins = ", ".join(str(r.path / name) for r in exaequo)
        return fail(
            f"définition « {name} » ambiguë — {len(exaequo)} racines de même rang : {chemins}"
        )
    return ok(candidates[0].path / name)
