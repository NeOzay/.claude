"""Les semences livrées avec gabarit déclarent la forme de leurs sections structurées.

CE QUE CE FICHIER PROUVE (C1, C3 de `semences-a-sections-structurees`) : chaque semence livrée,
résolue par son nom dans le paquet, pose un fichier que `check` juge conforme ; une puce mal formée
d'une section structurée fait échouer `check`, qui nomme la section et la puce ; un fichier rempli
à la forme que lit `rapport_audit` passe `--filled`.

LES SEMENCES SONT CELLES DE LA CONFIGURATION, pas celles du dépôt courant : la racine de projet
est un répertoire vide. `brief` et `suivi` viennent du paquet de gabarit, `shadow-skill` de la
skill du même nom, rangée à côté.
"""

from __future__ import annotations

from pathlib import Path

from gabarit.commandes import Semence, check, new, trouver_semence
from gabarit.definitions import DEFS, roots


def semence(nom: str, tmp_path: Path) -> Semence:
    projet = tmp_path / "projet"
    projet.mkdir(exist_ok=True)
    return trouver_semence(nom, None, roots(DEFS, cwd=projet)).unwrap()


def ecrire(tmp_path: Path, texte: str) -> Path:
    fiche = tmp_path / "fiche.md"
    _ = fiche.write_text(texte, encoding="utf-8")
    return fiche


def remplace(texte: str, titre: str, corps: str) -> str:
    """`texte` dont la section `titre` porte `corps`, jusqu'à la section suivante."""
    debut = texte.index(f"## {titre}\n")
    suite = texte.find("\n## ", debut + 1)
    fin = len(texte) if suite == -1 else suite
    return f"{texte[:debut]}## {titre}\n\n{corps}\n{texte[fin:]}"


# ---------------------------------------------------------------------- brief
FRONT_BRIEF = """+++
gabarit = "brief"
slug = "jouet"
titre = "Un chantier jouet"
statut = "validé"
"créé" = 2026-11-08
+++
"""

# Les sections du BRIEF des fixtures d'implementation-tracker (`scripts/tests/conftest.py`),
# la forme que `rapport_audit` lit, sous un front matter complet et complétées des deux
# sections requises qu'elles omettent.
BRIEF = f"""{FRONT_BRIEF}
## Intention

**Symptôme** : « la Passation est jugée périmée » après
chaque audit.

**But** : la reprendre.

## Critères de réussite

- **C1** — La reprise signale une Passation périmée.
- **C2** — `contexte --session courante` rend la taille
  du contexte (`pytest`).

## Hors-périmètre

- La ligne de statut (dit ; dépôt:
  `statusline-command.py`).

## Signaux de dérive

- **S1** — Un script lit le rapport en entier (dit).

## Contraintes connues de l'utilisateur

- **Décision** : le compteur reste au front matter (dit).

## Incertitudes à lever en plan

— aucune
"""


def test_brief_pose_conforme(tmp_path: Path) -> None:
    s = semence("brief", tmp_path)
    fiche = tmp_path / "pose.md"
    _ = new(fiche, s).unwrap()
    texte = fiche.read_text(encoding="utf-8")
    assert "<À REMPLIR motif: - **C{n: int}** — {critere}>" in texte
    assert "**Symptôme** : <À REMPLIR>" in texte
    assert check(fiche, semence=s)


def test_brief_rempli_passe_filled(tmp_path: Path) -> None:
    s = semence("brief", tmp_path)
    r = check(ecrire(tmp_path, BRIEF), filled=True, semence=s)
    assert r, r.message


def test_brief_puce_mal_formee(tmp_path: Path) -> None:
    s = semence("brief", tmp_path)
    for titre, corps, attendu in (
        (
            "Critères de réussite",
            "- **C1** — Un critère.\n- Un critère sans numéro.",
            "section « Critères de réussite », puce 2",
        ),
        (
            "Signaux de dérive",
            "- **S1** — Un signal (dit).\n- **S3** — Hors séquence (dit).",
            "section « Signaux de dérive », puce 2, capture « n »",
        ),
        (
            "Contraintes connues de l'utilisateur",
            "- Une contrainte sans nature (dit).",
            "section « Contraintes connues de l'utilisateur », puce 1",
        ),
        (
            "Intention",
            "**Symptôme** : vécu.",
            "section « Intention », label « But »",
        ),
    ):
        r = check(ecrire(tmp_path, remplace(BRIEF, titre, corps)), semence=s)
        assert not r, titre
        assert attendu in r.message, r.message


# ---------------------------------------------------------------------- suivi
SUIVI = """+++
gabarit = "suivi"
slug = "jouet"
titre = "Un chantier jouet"
branche = "jouet"
base = "master"
statut = "en-cours"
session = 2
lettre = "A"
"modèle" = "opus"
plan = ".claude/plans/jouet.md"
skills = []
"créé" = 2026-11-08
maj = 2026-11-08
+++

## Objectif et périmètre

**Symptôme** : « la Passation est jugée périmée » après chaque audit.

**But** : la reprendre.

**Critères de réussite** :

- **C1** — La reprise signale une Passation périmée.

**Hors-périmètre** :

- La ligne de statut (dit).

**Signaux de dérive** :

- **S1** — Un script lit le rapport en entier (dit).

## Étapes

- [x] 1. Un fichier — `a.txt` — vérif: `test -f a.txt`
- [!] 2. Un autre, dont l'intitulé court
  sur deux lignes — `b.txt` — vérif: `test -f b.txt`
- [ ] 3. Vérification d'ensemble — aucun fichier — vérif: C1

## État courant

**Prochaine action** : Étape 2.

**Vérification** : `pytest`

**Dernier audit** : aucun

**Notes** : l'Étape 2 attend une réponse.

## Passation

**Écrite** : <À REMPLIR>

**En cours** : <À REMPLIR>

**À savoir** : <À REMPLIR>

## Dettes écartées

- R8 — Le terme entre au Lexique global à l'Étape 9, sur accord de
  l'utilisateur. — 2026-10-04

## Journal de décisions

- **2026-11-08** — Le compteur reste au front matter. *Pourquoi* : il se lit sans la prose.
  *Rejeté* : un compteur en section.
"""


def test_suivi_pose_conforme(tmp_path: Path) -> None:
    s = semence("suivi", tmp_path)
    fiche = tmp_path / "pose.md"
    _ = new(fiche, s).unwrap()
    texte = fiche.read_text(encoding="utf-8")
    assert "<À REMPLIR motif: - [{etat: enum}] {n: int}. {intitule}" in texte
    assert "**Prochaine action** : <À REMPLIR>" in texte
    assert check(fiche, semence=s)


def test_suivi_rempli_passe_filled(tmp_path: Path) -> None:
    s = semence("suivi", tmp_path)
    r = check(ecrire(tmp_path, SUIVI), filled=True, semence=s)
    assert r, r.message


def test_suivi_puce_mal_formee(tmp_path: Path) -> None:
    s = semence("suivi", tmp_path)
    for titre, corps, attendu in (
        (
            "Étapes",
            "- [x] 1. Un fichier — `a.txt` — vérif: `test -f a.txt`\n- [x] 2. Sans vérification",
            "section « Étapes », puce 2",
        ),
        (
            "Étapes",
            "- [?] 1. Un fichier — `a.txt` — vérif: `test -f a.txt`",
            "section « Étapes », puce 1, capture « etat »",
        ),
        (
            "Dettes écartées",
            "- R8 — Écartée sans date.",
            "section « Dettes écartées », puce 1",
        ),
        (
            "Journal de décisions",
            "- Une décision sans date.",
            "section « Journal de décisions », puce 1",
        ),
    ):
        r = check(ecrire(tmp_path, remplace(SUIVI, titre, corps)), semence=s)
        assert not r, corps
        assert attendu in r.message, r.message


def test_suivi_critere_mal_numerote_dans_l_objectif(tmp_path: Path) -> None:
    s = semence("suivi", tmp_path)
    texte = SUIVI.replace("- **C1** — La reprise", "- **C2** — La reprise")
    r = check(ecrire(tmp_path, texte), semence=s)
    assert not r
    assert "label « Critères de réussite », puce 1, capture « n »" in r.message, r.message


# --------------------------------------------------------------- shadow-skill
SHADOW = """+++
gabarit = "shadow-skill"
name = "jouet"
description = "Un skill jouet."
when-to-load = "Jamais."
tags = ["conventions"]
+++

## Instructions

Rien.

## Références

- [`references/prose.md`](references/prose.md) : on écrit ou relit un `SKILL.md` ou une
  référence.
"""


def test_shadow_skill_pose_conforme(tmp_path: Path) -> None:
    s = semence("shadow-skill", tmp_path)
    fiche = tmp_path / "pose.md"
    _ = new(fiche, s).unwrap()
    assert "<OPTIONNEL motif: - [`{chemin}`]({lien}) : {quand}>" in fiche.read_text("utf-8")
    assert check(fiche, semence=s)


def test_shadow_skill_rempli_passe_filled(tmp_path: Path) -> None:
    s = semence("shadow-skill", tmp_path)
    r = check(ecrire(tmp_path, SHADOW), filled=True, semence=s)
    assert r, r.message


def test_shadow_skill_reference_sans_lien(tmp_path: Path) -> None:
    s = semence("shadow-skill", tmp_path)
    for corps in (
        "- `references/prose.md` : on écrit une référence.",
        "- [`references/prose.md`](references/prose.md)",
    ):
        r = check(ecrire(tmp_path, remplace(SHADOW, "Références", corps)), semence=s)
        assert not r, corps
        assert "section « Références », puce 1" in r.message, r.message
