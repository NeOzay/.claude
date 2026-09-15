#!/usr/bin/env python3
"""Les opérations git et fichiers d'un chantier, sans aucun jugement.

DEUX SOUS-COMMANDES :

- `lettre` : la première lettre de A à Z qu'aucun tag d'étape `<L>E<n>` n'occupe. Elle nomme
  les tags d'un chantier (`AE0`, `AE1`…) et se note dans le frontmatter de son suivi.
- `cloture <slug> --message <fichier> [--dry-run]` : finalise le suivi, aplatit la
  branche `<slug>` en un commit unique sur `base:`, archive les fichiers du chantier en
  `done/`, puis supprime la branche et ses tags.

AUCUN JUGEMENT ICI. Compacter le journal, rédiger le message, décider de clore : tout
cela est fait avant, par l'agent et l'utilisateur. Le script vérifie des conditions
mécaniques et exécute. C'est ce qui permet de le tester sur un dépôt jouet, et ce qui
rend son `--dry-run` fidèle : il affiche exactement ce que l'exécution fera.

POURQUOI UN SCRIPT ET PAS DES COMMANDES EN LIGNE : le hook `rtk` réécrit les appels Bash
du modèle et modifie leur sortie, ce qui a déjà cassé un filtre écrit en ligne sans
qu'aucune commande n'échoue. Un script échappe à cette réécriture.

TOUS LES REFUS PRÉCÈDENT LA PREMIÈRE ÉCRITURE. Un refus sort avec 1 et ne touche à
rien. Un échec git APRÈS la première écriture arrête tout et affiche l'état, sans rien
défaire : une clôture à moitié défaite par un script est plus difficile à reprendre
qu'une clôture arrêtée net.

Stdlib seule : le script doit tourner avec n'importe quel Python 3.12 du PATH.
"""

from __future__ import annotations

import argparse
import datetime
import re
import string
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import cast

IMPLEMENTATION = Path(".claude/implementation")
TODO = IMPLEMENTATION / "todo"
DONE = IMPLEMENTATION / "done"
TAG_ETAPE = re.compile(r"^(?P<lettre>[A-Z])E\d+$")
TITRE_MAX = 50


class Refus(Exception):
    """Une condition préalable n'est pas remplie. Rien n'a été touché."""


class Echec(Exception):
    """Une commande git a échoué après la première écriture."""


def git(*argv: str) -> subprocess.CompletedProcess[str]:
    """git dans le répertoire courant, sans lever d'exception : l'appelant juge."""
    return subprocess.run(["git", *argv], capture_output=True, text=True, check=False)


def git_ecriture(*argv: str) -> str:
    """git qui écrit. Un code non nul lève `Echec`, qui arrête tout sans rien défaire."""
    proc = git(*argv)
    if proc.returncode != 0:
        raise Echec(f"git {' '.join(argv)} :\n{proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout


# ------------------------------------------------------------------------- lettre
def tags_etape() -> dict[str, list[str]]:
    """Les tags d'étape du dépôt, regroupés par lettre."""
    proc = git("tag", "--list")
    if proc.returncode != 0:
        raise Refus(f"git tag --list : {proc.stderr.strip()}")
    par_lettre: dict[str, list[str]] = {}
    for tag in proc.stdout.split():
        m = TAG_ETAPE.match(tag)
        if m is not None:
            par_lettre.setdefault(m.group("lettre"), []).append(tag)
    return par_lettre


def lettre_libre() -> str:
    occupees = tags_etape()
    for lettre in string.ascii_uppercase:
        if lettre not in occupees:
            return lettre
    raise Refus(
        "les 26 lettres sont occupées par des tags d'étape : clore ou abandonner un chantier"
        " libère la sienne"
    )


# ------------------------------------------------------------------------ clôture
def frontmatter(texte: str) -> dict[str, str]:
    """Les champs `clé: valeur` du frontmatter, commentaire `  # …` retiré.

    Lecture ligne à ligne, sans dépendance : le frontmatter d'un suivi est plat, et le
    garde-fou du dépôt le lit déjà de cette façon.
    """
    lignes = texte.splitlines()
    if not lignes or lignes[0].strip() != "---":
        raise Refus("pas de frontmatter : la première ligne du suivi doit être « --- »")
    champs: dict[str, str] = {}
    for ligne in lignes[1:]:
        if ligne.strip() == "---":
            return champs
        m = re.match(r"^(?P<cle>[\w-]+): *(?P<valeur>.*?)(?:\s+#.*)?$", ligne)
        if m is not None and m.group("valeur"):
            champs[m.group("cle")] = m.group("valeur")
    # Nommer CE défaut : lu comme vide, le frontmatter ferait accuser le premier champ
    # requis d'être absent, alors qu'il est là et que c'est la clôture qui manque.
    raise Refus("frontmatter non fermé : aucune ligne « --- » ne le termine")


def remplacer_champ(texte: str, cle: str, valeur: str) -> str:
    """Réécrit la ligne `cle:` du frontmatter. Le reste du fichier n'est pas touché.

    LE MOTIF EST CELUI DU LECTEUR : `cle:` suivi ou non d'une espace. Un champ que
    `frontmatter` sait lire est un champ qu'on sait réécrire — sinon `maj:2026-01-01`
    serait lu, jamais réécrit, et le suivi archivé garderait sa valeur sans un mot. Seule
    la valeur change : un commentaire `  # …` en fin de ligne est conservé.
    Un champ introuvable lève `Echec` : un fichier laissé inchangé en silence est le
    défaut que ce script existe pour ne pas avoir.
    """
    fin = texte.find("\n---", 3)
    if fin < 0:
        raise Echec(f"frontmatter non fermé : « {cle}: » ne peut pas être réécrit")
    tete, reste = texte[:fin], texte[fin:]
    tete, n = re.subn(
        rf"(?m)^{re.escape(cle)}:.*?(?P<commentaire>\s+#.*)?$",
        lambda m: f"{cle}: {valeur}{m.group('commentaire') or ''}",
        tete,
        count=1,
    )
    if n == 0:
        raise Echec(f"champ « {cle}: » introuvable dans le frontmatter")
    return tete + reste


@dataclass(frozen=True)
class Cloture:
    slug: str
    base: str
    lettre: str
    suivi: Path
    message: Path
    date: str
    deplacements: list[tuple[Path, Path]]  # (source, cible), suivi en tête
    champs: dict[str, str]  # champ du frontmatter → cible dans done/
    tags: list[str]
    plage: str

    @property
    def suivi_archive(self) -> Path:
        return self.deplacements[0][1]


def statut_porcelain() -> list[str]:
    """Les chemins modifiés, indexés ou non suivis, un par entrée."""
    proc = git("status", "--porcelain=v1", "-z", "--untracked-files=all")
    if proc.returncode != 0:
        raise Refus(f"git status : {proc.stderr.strip()}")
    chemins: list[str] = []
    entrees = iter(proc.stdout.split("\0"))
    for entree in entrees:
        if not entree:
            continue
        chemins.append(entree[3:])
        if entree[0] in "RC":
            chemins.append(next(entrees, ""))  # la source d'un renommage suit
    return chemins


def verifier_message(message: Path) -> None:
    if not message.is_file():
        raise Refus(f"fichier de message introuvable : {message}")
    lignes = message.read_text(encoding="utf-8").strip("\n").splitlines()
    if not lignes or not lignes[0].strip():
        raise Refus(f"fichier de message vide, ou titre vide : {message}")
    if len(lignes[0]) > TITRE_MAX:
        raise Refus(f"titre de {len(lignes[0])} caractères, {TITRE_MAX} au plus : « {lignes[0]} »")
    if len(lignes) > 1 and lignes[1].strip():
        raise Refus("la ligne 2 du message doit être vide : elle sépare le titre du corps")


def preparer(slug: str, message: Path) -> Cloture:
    """Toutes les vérifications, et le relevé de ce que l'exécution fera. N'écrit rien."""
    racine = git("rev-parse", "--show-toplevel")
    if racine.returncode != 0:
        raise Refus("hors d'un dépôt git")
    if Path(racine.stdout.strip()).resolve() != Path.cwd().resolve():
        raise Refus(f"à lancer depuis la racine du dépôt : {racine.stdout.strip()}")

    courante = git("branch", "--show-current").stdout.strip()
    if courante != slug:
        raise Refus(f"branche courante « {courante} », attendue « {slug} »")

    suivi = IMPLEMENTATION / f"{slug}.md"
    if not suivi.is_file():
        raise Refus(f"suivi introuvable : {suivi}")
    champs = frontmatter(suivi.read_text(encoding="utf-8"))
    for requis in ("base", "lettre", "plan", "statut", "maj"):
        if requis not in champs:
            raise Refus(f"{suivi} : champ « {requis}: » absent du frontmatter")
    base, lettre = champs["base"], champs["lettre"]
    if not re.fullmatch(r"[A-Z]", lettre):
        raise Refus(f"{suivi} : « lettre: {lettre} » n'est pas une lettre de A à Z")
    if git("rev-parse", "--verify", "--quiet", f"refs/heads/{base}").returncode != 0:
        raise Refus(f"branche de base introuvable : {base}")
    plan = Path(champs["plan"])
    if not plan.is_file():
        raise Refus(f"plan introuvable : {plan}")

    brief = IMPLEMENTATION / f"{slug}.brief.md"
    audit = IMPLEMENTATION / f"{slug}.audit.md"
    annexes = {p.as_posix() for p in (suivi, brief, audit, plan)}
    etrangers = [
        c
        for c in statut_porcelain()
        if c not in annexes and not c.startswith(TODO.as_posix() + "/")
    ]
    if etrangers:
        raise Refus(
            "modifications étrangères au chantier, à traiter avant de clore :\n  "
            + "\n  ".join(etrangers)
        )

    verifier_message(message)

    date = datetime.date.today().isoformat()
    deplacements = [(suivi, DONE / f"{date}-{slug}.md")]
    champs_cibles: dict[str, str] = {}
    for champ, source in (("brief", brief), ("audit", audit), ("plan", plan)):
        if source.is_file():
            cible = DONE / f"{date}-{slug}.{champ}.md"
            deplacements.append((source, cible))
            if champ in champs:  # un champ absent n'est pas inventé
                champs_cibles[champ] = cible.as_posix()
    for _, cible in deplacements:
        if cible.exists():
            raise Refus(f"{cible} existe déjà : rien n'est écrasé")

    conflit = git("merge-tree", "--write-tree", "--name-only", "--no-messages", base, slug)
    if conflit.returncode == 1:
        fichiers = conflit.stdout.splitlines()[1:]
        raise Refus(
            f"« {base} » a divergé : l'aplatissement produirait un conflit sur\n  "
            + "\n  ".join(fichiers)
        )
    if conflit.returncode != 0:
        raise Refus(f"git merge-tree : {conflit.stderr.strip()}")

    return Cloture(
        slug=slug,
        base=base,
        lettre=lettre,
        suivi=suivi,
        message=message.resolve(),
        date=date,
        deplacements=deplacements,
        champs=champs_cibles,
        tags=sorted(tags_etape().get(lettre, []), key=lambda t: int(t[2:])),
        plage=git("log", "--oneline", f"{base}..{slug}").stdout.rstrip(),
    )


def decrire(c: Cloture) -> str:
    lignes = [
        f"Branche aplatie : {c.slug} → un commit sur {c.base}",
        "Commits réunis :",
        *(f"  {ligne}" for ligne in (c.plage.splitlines() or ["(aucun)"])),
        f"Commit préalable sur {c.slug} : « {c.slug}: finalisation du suivi » (statut: terminé)",
        "Déplacements :",
        *(f"  {s} → {t}" for s, t in c.deplacements),
        "Champs réécrits dans le suivi archivé :",
        *(f"  {k}: {v}" for k, v in c.champs.items()),
        f"Branche supprimée : {c.slug}",
        f"Tags supprimés : {' '.join(c.tags) or '(aucun)'}",
        "Message :",
        *(f"  {ligne}" for ligne in c.message.read_text(encoding="utf-8").rstrip().splitlines()),
    ]
    return "\n".join(lignes)


def finaliser(c: Cloture) -> None:
    """Point 3 — sur la branche : `statut: terminé`, `maj:` du jour, commit des annexes.

    Toutes les annexes présentes sont indexées : non suivies, elles resteraient hors de
    l'aplatissement ; suivies et modifiées, elles feraient refuser le changement de branche.
    """
    texte = c.suivi.read_text(encoding="utf-8")
    texte = remplacer_champ(texte, "statut", "terminé")
    texte = remplacer_champ(texte, "maj", c.date)
    _ = c.suivi.write_text(texte, encoding="utf-8")
    a_indexer = [s.as_posix() for s, _ in c.deplacements]
    if TODO.is_dir():
        a_indexer.append(TODO.as_posix())
    _ = git_ecriture("add", "--", *a_indexer)
    # UNE RELANCE TROUVE LA FINALISATION DÉJÀ COMMITÉE : rien d'indexé, donc pas de commit.
    # Sans cette garde, `git commit` échoue sur « nothing to commit » et la clôture ne
    # peut plus jamais être relancée.
    if git("diff", "--cached", "--quiet").returncode != 0:
        _ = git_ecriture("commit", "-q", "-m", f"{c.slug}: finalisation du suivi")


def archiver(c: Cloture) -> None:
    """Déplace les fichiers du chantier vers `done/` et réécrit les champs du suivi archivé."""
    DONE.mkdir(parents=True, exist_ok=True)
    for source, cible in c.deplacements:
        _ = git_ecriture("mv", source.as_posix(), cible.as_posix())
    texte = c.suivi_archive.read_text(encoding="utf-8")
    for champ, cible in c.champs.items():
        texte = remplacer_champ(texte, champ, cible)
    _ = c.suivi_archive.write_text(texte, encoding="utf-8")
    _ = git_ecriture("add", "--", c.suivi_archive.as_posix())


def gestes(c: Cloture) -> list[tuple[str, Callable[[], object]]]:
    """La clôture, geste par geste, chacun avec le libellé qu'un humain rejouerait."""
    liste: list[tuple[str, Callable[[], object]]] = [
        (
            f"finaliser le suivi sur {c.slug} (statut, maj, commit des annexes)",
            lambda: finaliser(c),
        ),
        (f"git checkout {c.base}", lambda: git_ecriture("checkout", "-q", c.base)),
        (f"git merge --squash {c.slug}", lambda: git_ecriture("merge", "--squash", c.slug)),
        (
            "git mv des fichiers du chantier vers done/, réécriture de plan/brief/audit",
            lambda: archiver(c),
        ),
        (f"git commit -F {c.message}", lambda: git_ecriture("commit", "-q", "-F", str(c.message))),
        (f"git branch -D {c.slug}", lambda: git_ecriture("branch", "-D", c.slug)),
    ]
    if c.tags:
        liste.append(
            (f"git tag -d {' '.join(c.tags)}", lambda: git_ecriture("tag", "-d", *c.tags))
        )
    return liste


def executer(c: Cloture) -> None:
    """Enchaîne les gestes. Un échec dit ce qui est fait, ce qui reste, et si relancer.

    Les deux premiers gestes laissent sur `<slug>` : la commande se relance telle quelle.
    Au-delà, on est sur la base avec un aplatissement entamé, et la suite se fait à la
    main — d'où la liste exacte de ce qui reste, plutôt qu'un simple message git.
    """
    liste = gestes(c)
    for rang, (_, geste) in enumerate(liste):
        try:
            _ = geste()
        except Echec as echec:
            fait = [libelle for libelle, _ in liste[:rang]] or ["(rien)"]
            reste = [libelle for libelle, _ in liste[rang:]]
            suite = (
                f"Toujours sur {c.slug} : la commande peut être relancée telle quelle."
                if rang <= 1
                else f"Sur {c.base}, aplatissement entamé : terminer à la main, dans l'ordre."
            )
            raise Echec(
                f"{echec}\n\nFait :\n  "
                + "\n  ".join(fait)
                + "\nReste à faire (le premier a pu être entamé) :\n  "
                + "\n  ".join(reste)
                + f"\n{suite}"
            ) from None


# ---------------------------------------------------------------------------- CLI
def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="commit-chantier")
    sous = parser.add_subparsers(dest="commande", required=True)
    _ = sous.add_parser("lettre", help="première lettre libre pour les tags d'étape")
    p_cloture = sous.add_parser("cloture", help="aplatir et archiver un chantier")
    _ = p_cloture.add_argument("slug")
    _ = p_cloture.add_argument("--message", required=True, type=Path)
    _ = p_cloture.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    commande = cast("str", args.commande)

    try:
        if commande == "lettre":
            print(lettre_libre())
            return 0
        cloture = preparer(cast("str", args.slug), cast("Path", args.message))
        print(decrire(cloture))
        if cast("bool", args.dry_run):
            print("\n--dry-run : rien n'a été modifié.")
            return 0
        executer(cloture)
    except Refus as refus:
        sys.stderr.write(f"REFUS : {refus}\n")
        return 1
    except Echec as echec:
        sys.stderr.write(f"ÉCHEC, clôture arrêtée en l'état : {echec}\n")
        sys.stderr.write(git("status", "--short", "--branch").stdout)
        return 1

    print()
    print(git("log", "--oneline", "-3").stdout.rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
