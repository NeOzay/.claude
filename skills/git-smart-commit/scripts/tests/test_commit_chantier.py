"""commit_chantier.py — la lettre des tags d'étape, et la clôture d'un chantier.

Le script est lancé en SOUS-PROCESSUS, comme l'agent le lance : c'est la ligne de
commande qui est le contrat, codes de sortie compris. Chaque test monte son dépôt sur
`tmp_path`, avec une identité git LOCALE — un test qui dépendrait de la configuration de
la machine passerait ici et nulle part ailleurs.

Pas de `conftest.py` : les suites du dépôt ne partagent jamais un nom de module (voir
`scripts/tests/README.md`). Les fixtures vivent dans ce fichier.
"""

from __future__ import annotations

import datetime
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "commit_chantier.py"
SLUG = "chantier-jouet"
BASE = "principale"
PLAN = ".claude/plans/plan-genere.md"
SUIVI = f".claude/implementation/{SLUG}.md"
BRIEF = f".claude/implementation/{SLUG}.brief.md"
AUDIT = f".claude/implementation/{SLUG}.audit.md"
DATE = datetime.date.today().isoformat()
DONE = ".claude/implementation/done"

SUIVI_TEXTE = f"""---
slug: {SLUG}
titre: Un chantier jouet
branche: {SLUG}
base: {BASE}               # branche principale
statut: en-cours
session: 2
lettre: A
plan: {PLAN}
brief: {BRIEF}
créé: 2026-01-01
maj: 2026-01-02
---

## Étapes

- [x] 1. Écrire le code
"""


def git(depot: Path, *argv: str) -> str:
    """git dans le dépôt jouet, en échec bruyant. Ce n'est pas le git du script."""
    proc = subprocess.run(["git", *argv], cwd=depot, capture_output=True, text=True, check=True)
    return proc.stdout


def ecrire(depot: Path, rel: str, contenu: str) -> None:
    chemin = depot / rel
    chemin.parent.mkdir(parents=True, exist_ok=True)
    _ = chemin.write_text(contenu, encoding="utf-8")


def lancer(depot: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *argv], cwd=depot, capture_output=True, text=True, check=False
    )


def message(depot: Path, texte: str = "feat(jouet): livrer le chantier\n\nPourquoi.\n") -> str:
    chemin = depot.parent / f"{depot.name}-message.txt"
    _ = chemin.write_text(texte, encoding="utf-8")
    return str(chemin)


def instantane(depot: Path) -> tuple[str, ...]:
    """Tout ce qu'un refus ou un dry-run ne doit pas changer."""
    return (
        git(depot, "rev-parse", "HEAD"),
        git(depot, "branch", "--list"),
        git(depot, "tag", "--list"),
        git(depot, "status", "--porcelain", "--untracked-files=all"),
        (depot / SUIVI).read_text(encoding="utf-8"),
    )


@pytest.fixture
def depot(tmp_path: Path) -> Path:
    """Un chantier prêt à clore : état initial tagué AE0, une étape tagée AE1."""
    d = tmp_path / "depot"
    d.mkdir()
    _ = git(d, "init", "-q", "-b", BASE)
    _ = git(d, "config", "user.name", "Jouet")
    _ = git(d, "config", "user.email", "jouet@example.invalid")
    _ = git(d, "config", "commit.gpgsign", "false")
    _ = git(d, "config", "tag.gpgsign", "false")
    ecrire(d, "README.md", "base\n")
    _ = git(d, "add", "-A")
    _ = git(d, "commit", "-q", "-m", "initial")

    _ = git(d, "checkout", "-q", "-b", SLUG)
    ecrire(d, SUIVI, SUIVI_TEXTE)
    ecrire(d, BRIEF, "brief\n")
    ecrire(d, PLAN, "plan\n")
    _ = git(d, "add", "-A")
    _ = git(d, "commit", "-q", "-m", f"{SLUG}: E0 — état initial")
    _ = git(d, "tag", "AE0")
    ecrire(d, "code.txt", "le code\n")
    _ = git(d, "add", "code.txt")
    _ = git(d, "commit", "-q", "-m", f"{SLUG}: E1 — écrire le code")
    _ = git(d, "tag", "AE1")
    return d


# ------------------------------------------------------------------------- lettre
def test_lettre_a_sans_aucun_tag(tmp_path: Path) -> None:
    _ = git(tmp_path, "init", "-q")
    proc = lancer(tmp_path, "lettre")
    assert (proc.returncode, proc.stdout) == (0, "A\n")


def test_lettre_b_quand_a_est_prise(depot: Path) -> None:
    _ = git(depot, "tag", "version-1")  # un tag qui n'est pas d'étape n'occupe rien
    proc = lancer(depot, "lettre")
    assert (proc.returncode, proc.stdout) == (0, "B\n")


def test_lettre_refusee_quand_les_26_sont_prises(depot: Path) -> None:
    for lettre in "BCDEFGHIJKLMNOPQRSTUVWXYZ":
        _ = git(depot, "tag", f"{lettre}E0")
    proc = lancer(depot, "lettre")
    assert proc.returncode == 1
    assert proc.stdout == ""
    assert "26 lettres" in proc.stderr


# ------------------------------------------------------------------------ dry-run
def test_dry_run_ne_modifie_rien(depot: Path) -> None:
    avant = instantane(depot)
    proc = lancer(depot, "cloture", SLUG, "--message", message(depot), "--dry-run")
    assert proc.returncode == 0, proc.stderr
    assert instantane(depot) == avant
    assert f"{SUIVI} → {DONE}/{DATE}-{SLUG}.md" in proc.stdout
    assert "Tags supprimés : AE0 AE1" in proc.stdout


# ----------------------------------------------------------------- clôture nominale
def test_cloture_aplatit_archive_et_nettoie(depot: Path) -> None:
    commits_base = git(depot, "rev-list", "--count", BASE)
    proc = lancer(depot, "cloture", SLUG, "--message", message(depot))
    assert proc.returncode == 0, proc.stderr

    assert git(depot, "branch", "--show-current").strip() == BASE
    assert int(git(depot, "rev-list", "--count", BASE)) == int(commits_base) + 1
    assert git(depot, "log", "-1", "--format=%s").strip() == "feat(jouet): livrer le chantier"
    assert git(depot, "status", "--porcelain", "--untracked-files=all") == ""
    assert (depot / "code.txt").is_file()

    suivi = depot / DONE / f"{DATE}-{SLUG}.md"
    for rel in (f"{DATE}-{SLUG}.brief.md", f"{DATE}-{SLUG}.plan.md"):
        assert (depot / DONE / rel).is_file()
    for rel in (SUIVI, BRIEF, PLAN):
        assert not (depot / rel).exists()
    texte = suivi.read_text(encoding="utf-8")
    assert "statut: terminé\n" in texte
    assert f"maj: {DATE}\n" in texte
    assert f"plan: {DONE}/{DATE}-{SLUG}.plan.md\n" in texte
    assert f"brief: {DONE}/{DATE}-{SLUG}.brief.md\n" in texte
    assert "base: principale               # branche principale\n" in texte

    assert SLUG not in git(depot, "branch", "--list")
    assert git(depot, "tag", "--list") == ""


def test_cloture_accepte_un_audit_non_suivi(depot: Path) -> None:
    ecrire(depot, AUDIT, "audit\n")
    proc = lancer(depot, "cloture", SLUG, "--message", message(depot))
    assert proc.returncode == 0, proc.stderr
    archive = f"{DONE}/{DATE}-{SLUG}.audit.md"
    assert git(depot, "ls-files", archive).strip() == archive
    assert f"audit: {archive}" not in (depot / DONE / f"{DATE}-{SLUG}.md").read_text(
        encoding="utf-8"
    )  # le champ n'existait pas : rien n'est inventé


def test_cloture_ne_supprime_que_les_tags_de_sa_lettre(depot: Path) -> None:
    _ = git(depot, "tag", "BE0", BASE)
    proc = lancer(depot, "cloture", SLUG, "--message", message(depot))
    assert proc.returncode == 0, proc.stderr
    assert git(depot, "tag", "--list").split() == ["BE0"]


# -------------------------------------------------------------------------- refus
def refuse(depot: Path, *argv: str) -> str:
    """Lance la clôture, vérifie qu'elle refuse sans rien toucher, rend stderr."""
    avant = instantane(depot)
    proc = lancer(depot, "cloture", SLUG, *argv)
    assert proc.returncode == 1, proc.stdout
    assert proc.stderr.startswith("REFUS : ")
    assert instantane(depot) == avant
    return proc.stderr


def test_refus_sur_conflit_avec_la_base(depot: Path) -> None:
    _ = git(depot, "checkout", "-q", BASE)
    ecrire(depot, "code.txt", "une autre version\n")
    _ = git(depot, "add", "code.txt")
    _ = git(depot, "commit", "-q", "-m", "divergence")
    _ = git(depot, "checkout", "-q", SLUG)
    assert "code.txt" in refuse(depot, "--message", message(depot))


def test_refus_si_une_cible_existe_deja(depot: Path) -> None:
    ecrire(depot, f"{DONE}/{DATE}-{SLUG}.plan.md", "archive d'un autre jour\n")
    _ = git(depot, "add", "-A")
    _ = git(depot, "commit", "-q", "-m", "collision")
    assert "existe déjà" in refuse(depot, "--message", message(depot))


def test_refus_si_le_titre_depasse_50_caracteres(depot: Path) -> None:
    assert "caractères" in refuse(depot, "--message", message(depot, "x" * 51 + "\n"))


def test_refus_si_la_ligne_2_n_est_pas_vide(depot: Path) -> None:
    assert "ligne 2" in refuse(depot, "--message", message(depot, "titre\ncorps collé\n"))


def test_refus_hors_de_la_branche_du_chantier(depot: Path) -> None:
    _ = git(depot, "checkout", "-q", "-b", "une-autre")  # le suivi reste lisible
    assert "branche courante" in refuse(depot, "--message", message(depot))


def test_refus_sur_modification_etrangere(depot: Path) -> None:
    ecrire(depot, "brouillon.txt", "hors chantier\n")
    assert "brouillon.txt" in refuse(depot, "--message", message(depot))


def test_refus_sans_lettre_au_frontmatter(depot: Path) -> None:
    ecrire(depot, SUIVI, SUIVI_TEXTE.replace("lettre: A\n", ""))
    assert "lettre" in refuse(depot, "--message", message(depot))


def test_refus_sans_maj_au_frontmatter(depot: Path) -> None:
    ecrire(depot, SUIVI, SUIVI_TEXTE.replace("maj: 2026-01-02\n", ""))
    assert "maj" in refuse(depot, "--message", message(depot))


def test_refus_si_le_plan_est_introuvable(depot: Path) -> None:
    ecrire(depot, SUIVI, SUIVI_TEXTE.replace(f"plan: {PLAN}", "plan: .claude/plans/absent.md"))
    assert "plan introuvable" in refuse(depot, "--message", message(depot))


def test_refus_si_la_base_est_introuvable(depot: Path) -> None:
    ecrire(depot, SUIVI, SUIVI_TEXTE.replace(f"base: {BASE}", "base: inexistante"))
    assert "base introuvable" in refuse(depot, "--message", message(depot))


def test_refus_hors_de_la_racine_du_depot(depot: Path) -> None:
    avant = instantane(depot)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "cloture", SLUG, "--message", message(depot)],
        cwd=depot / ".claude",
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
    assert "racine du dépôt" in proc.stderr
    assert instantane(depot) == avant


# --------------------------------------------------------- champs du frontmatter
def test_un_champ_colle_a_ses_deux_points_est_reecrit(depot: Path) -> None:
    colle = SUIVI_TEXTE.replace("maj: 2026-01-02", "maj:2026-01-02").replace(
        f"plan: {PLAN}", f"plan:{PLAN}"
    )
    ecrire(depot, SUIVI, colle)
    proc = lancer(depot, "cloture", SLUG, "--message", message(depot))
    assert proc.returncode == 0, proc.stderr
    texte = (depot / DONE / f"{DATE}-{SLUG}.md").read_text(encoding="utf-8")
    assert f"maj: {DATE}\n" in texte
    assert f"plan: {DONE}/{DATE}-{SLUG}.plan.md\n" in texte


def test_le_registre_non_suivi_entre_dans_l_aplatissement(depot: Path) -> None:
    entree = ".claude/implementation/todo/technical-debt/une-dette.md"
    ecrire(depot, entree, "une dette\n")
    proc = lancer(depot, "cloture", SLUG, "--message", message(depot))
    assert proc.returncode == 0, proc.stderr
    assert git(depot, "ls-files", entree).strip() == entree
    assert git(depot, "show", "--name-only", "--format=", "HEAD").count(entree) == 1


# ---------------------------------------------------------------- échec et relance
def crochet_qui_refuse_sur(depot: Path, branche: str) -> Path:
    """Un pre-commit qui échoue sur `branche` : le moyen le plus sûr de faire échouer git."""
    crochet = depot / ".git/hooks/pre-commit"
    _ = crochet.write_text(
        f'#!/bin/sh\n[ "$(git branch --show-current)" = "{branche}" ] && exit 1\nexit 0\n',
        encoding="utf-8",
    )
    crochet.chmod(0o755)
    return crochet


def test_un_echec_sur_la_base_dit_ce_qui_reste_a_faire(depot: Path) -> None:
    _ = crochet_qui_refuse_sur(depot, BASE)
    proc = lancer(depot, "cloture", SLUG, "--message", message(depot))
    assert proc.returncode == 1
    assert proc.stderr.startswith("ÉCHEC")
    fait, reste = proc.stderr.split("Reste à faire", 1)
    assert f"git merge --squash {SLUG}" in fait
    assert "git commit -F" in reste
    assert f"git branch -D {SLUG}" in reste
    assert "git tag -d AE0 AE1" in reste
    assert "terminer à la main" in reste
    # rien au-delà du geste en échec n'a été fait
    assert SLUG in git(depot, "branch", "--list")
    assert git(depot, "tag", "--list").split() == ["AE0", "AE1"]


def test_un_echec_sur_la_branche_se_relance_tel_quel(depot: Path) -> None:
    crochet = crochet_qui_refuse_sur(depot, SLUG)
    premier = lancer(depot, "cloture", SLUG, "--message", message(depot))
    assert premier.returncode == 1
    assert "relancée telle quelle" in premier.stderr
    crochet.unlink()
    second = lancer(depot, "cloture", SLUG, "--message", message(depot))
    assert second.returncode == 0, second.stderr
    assert git(depot, "branch", "--show-current").strip() == BASE


def test_relance_quand_la_finalisation_est_deja_commitee(depot: Path) -> None:
    ecrire(
        depot,
        SUIVI,
        SUIVI_TEXTE.replace("statut: en-cours", "statut: terminé").replace(
            "maj: 2026-01-02", f"maj: {DATE}"
        ),
    )
    _ = git(depot, "add", SUIVI)
    _ = git(depot, "commit", "-q", "-m", f"{SLUG}: finalisation du suivi")
    proc = lancer(depot, "cloture", SLUG, "--message", message(depot))
    assert proc.returncode == 0, proc.stderr
    assert git(depot, "branch", "--show-current").strip() == BASE


def test_refus_nomme_un_frontmatter_non_ferme(depot: Path) -> None:
    ecrire(depot, SUIVI, SUIVI_TEXTE.replace("maj: 2026-01-02\n---\n", "maj: 2026-01-02\n"))
    assert "non fermé" in refuse(depot, "--message", message(depot))


def test_la_reecriture_conserve_le_commentaire_de_fin_de_ligne(depot: Path) -> None:
    commente = SUIVI_TEXTE.replace("maj: 2026-01-02", "maj: 2026-01-02   # à chaque écriture")
    ecrire(depot, SUIVI, commente)
    proc = lancer(depot, "cloture", SLUG, "--message", message(depot))
    assert proc.returncode == 0, proc.stderr
    texte = (depot / DONE / f"{DATE}-{SLUG}.md").read_text(encoding="utf-8")
    assert f"maj: {DATE}   # à chaque écriture\n" in texte


def test_un_chemin_commente_est_reecrit_sans_perdre_son_commentaire(depot: Path) -> None:
    commente = SUIVI_TEXTE.replace(f"plan: {PLAN}", f"plan: {PLAN}   # plan du harness")
    ecrire(depot, SUIVI, commente)
    proc = lancer(depot, "cloture", SLUG, "--message", message(depot))
    assert proc.returncode == 0, proc.stderr
    texte = (depot / DONE / f"{DATE}-{SLUG}.md").read_text(encoding="utf-8")
    assert f"plan: {DONE}/{DATE}-{SLUG}.plan.md   # plan du harness\n" in texte

