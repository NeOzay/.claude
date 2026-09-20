"""Définitions de listes : où les trouver, et laquelle gagne.

UNE DÉFINITION EST LE CONTENU D'UN FUTUR `.list/` — un `contract.toml`, et un
`patrons/` facultatif. Elle vit hors de tout répertoire-liste, ce qui est
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

LE MÉCANISME VIT DANS `gabarit.definitions`, qui le partage avec les semences de
gabarit sous un autre répertoire. Ce module n'y ajoute que le nom `list-dir` et le refus
d'un nom de patron de liste (`technical-debt/review`), propre à une liste.

LES DEUX REMONTÉES NE CHERCHENT PAS LA MÊME CHOSE, et les confondre casse le cas
imbriqué. Un projet est un répertoire qui CONTIENT un `.claude` ; la configuration
est un répertoire QUI EST un `.claude`. Sur ce dépôt-ci — la configuration est
`~/.claude` et porte son propre `~/.claude/.claude` — une règle unique ferait
répondre la même chose aux deux questions, et l'un des deux rangs viserait le
mauvais répertoire.
"""

from __future__ import annotations

from pathlib import Path

from gabarit.definitions import CLAUDE as CLAUDE
from gabarit.definitions import SKILLS as SKILLS
from gabarit.definitions import Root as Root
from gabarit.definitions import config_root as config_root
from gabarit.definitions import definitions as definitions
from gabarit.definitions import project_root as project_root
from gabarit.definitions import resolve as _resolve
from gabarit.definitions import roots as _roots

from .types import SEPARATEUR, Result, fail, nom_mal_forme

DEFS = "list-dir"
"""Le répertoire qu'une racine porte. Le nom est celui du skill : une définition de
liste se range sous le nom de ce qui sait la lire."""


def roots(cwd: Path | None = None, package: Path | None = None) -> list[Root]:
    """Les quatre rangs des définitions de liste : voir `gabarit.definitions.roots`.

    L'ANCRAGE DU PAQUET RESTE CE PAQUET-CI par défaut, et non celui de `gabarit` : les
    deux vivent aujourd'hui sous la même configuration, mais rien ne l'impose.
    """
    return _roots(DEFS, cwd, package if package is not None else Path(__file__).parent)


def resolve(name: str, where: list[Root]) -> Result[Path]:
    """Le répertoire de définition retenu pour `name`.

    QUATRE ISSUES, et pas une de plus :
      - un nom de PATRON — `technical-debt/review` — → échec disant ce qu'il est. Un
        patron n'est pas une définition : il ne s'amorce ni ne se rattrape, il
        transforme une liste qui existe déjà. Le chercher dans les rangs rendrait
        « introuvable » sur un nom parfaitement valide, et enverrait chercher là où
        il n'a jamais été ;
      - un seul rang le porte, ou plusieurs à des rangs différents → le plus
        spécifique gagne. Masquer est le comportement voulu : c'est ainsi qu'un
        projet reprend la main sur une définition de la configuration ;
      - deux racines DE MÊME RANG le portent → échec les nommant toutes les deux.
        Choisir en silence ferait dépendre le contrat d'une liste de l'ordre de
        parcours d'un répertoire ;
      - personne → échec listant les noms connus, comme le fait `list-dir.py` pour
        une commande inconnue. Un « introuvable » sec obligerait à aller lire
        l'arborescence pour trouver l'orthographe exacte.

    LE REFUS DU PATRON VIENT EN PREMIER, et c'est ce qui donne son message à
    `init --def a/b` comme à `reseed --def a/b` : un seul point de contrôle pour tous
    ceux qui résolvent un nom, plutôt qu'un contrôle par appelant qui finirait par
    manquer au dernier arrivé.
    """
    if SEPARATEUR in name:
        motif = nom_mal_forme(name)
        if motif is not None:
            # LA FORME SE JUGE AVANT LE SENS, sans quoi le refus conseille une commande
            # qui ne marchera pas : « --def technical-debt/ » nommerait un patron vide,
            # et « --def a/b/c » un patron « b/c » qui ne peut pas exister.
            return fail(f"« {name} » n'est pas un nom de semence : {motif}")
        definition, _, patron = name.partition(SEPARATEUR)
        return fail(
            f"« {name} » nomme le patron « {patron} » de la définition « {definition} », "
            "pas une définition — un patron ne s'amorce ni ne se rattrape ; il projette une "
            f"liste existante (« list-dir derive <src> <dst> --patron {patron} »), et "
            f"« list-dir contract --def {definition} --patron {patron} » l'imprime"
        )

    return _resolve(name, where, "définition")
