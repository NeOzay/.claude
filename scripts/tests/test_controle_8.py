"""Contrôle 8 — renvois documentaires entre skills.

Le pendant des contrôles 6 et 7 : ceux-ci gardent l'APPEL d'un autre skill, celui-ci
garde le RENVOI vers lui. Un lien relatif survit au déplacement de la racine mais pas
au renommage d'un skill — et un renvoi mort se lit comme une section absente.
"""

from __future__ import annotations

from pathlib import Path

from check_pipeline import check_renvois_skill
from conftest import ecrire


def rouges(root: Path) -> list[str]:
    return [f.message for f in check_renvois_skill(root) if not f.ok]


def test_renvoi_qui_resout(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, "skills/cible/references/contrat.md", "# Contrat\n\n## Champs\n\nx\n")
    _ = ecrire(
        tmp_path,
        "skills/source/SKILL.md",
        "Voir [Contrat](../cible/references/contrat.md#champs).\n",
    )
    assert rouges(tmp_path) == []


def test_renvoi_mort(tmp_path: Path) -> None:
    """Le cas du renommage : le skill visé n'existe plus sous ce nom."""
    _ = ecrire(
        tmp_path,
        "skills/source/SKILL.md",
        "Voir [Contrat](../disparu/references/contrat.md).\n",
    )
    assert any("renvoi mort" in m for m in rouges(tmp_path))


def test_ancre_seule_ne_casse_pas_le_chemin(tmp_path: Path) -> None:
    """L'ancre `#…` n'appartient pas au chemin : la couper avant de résoudre."""
    _ = ecrire(
        tmp_path,
        "skills/cible/references/contrat.md",
        "# Contrat\n\n## Dates et listing\n\nx\n",
    )
    _ = ecrire(
        tmp_path,
        "skills/source/references/note.md",
        "Voir [Dates](../../cible/references/contrat.md#dates-et-listing).\n",
    )
    assert rouges(tmp_path) == []


def test_ancre_morte(tmp_path: Path) -> None:
    """Le fichier existe, la section non : le renvoi fonctionne, il ne conduit pas.

    Sans ce cas, un lien vers une section renommée dépose le lecteur en tête d'une
    référence de 400 lignes — le mode de défaillance même que ce contrôle invoque.
    """
    _ = ecrire(tmp_path, "skills/cible/references/contrat.md", "# Contrat\n\n## Champs\n\nx\n")
    _ = ecrire(
        tmp_path,
        "skills/source/SKILL.md",
        "Voir [Contrat](../cible/references/contrat.md#section-renommee).\n",
    )
    assert any("ancre morte" in m for m in rouges(tmp_path))


def test_renvoi_sans_ancre_reste_licite(tmp_path: Path) -> None:
    """Renvoyer vers un fichier entier est légitime : il n'y a rien à vérifier."""
    _ = ecrire(tmp_path, "skills/cible/references/contrat.md", "# Contrat\n")
    _ = ecrire(
        tmp_path,
        "skills/source/SKILL.md",
        "Voir [Contrat](../cible/references/contrat.md).\n",
    )
    assert rouges(tmp_path) == []


def test_gabarit_ignore(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, "skills/source/SKILL.md", "Voir [X](../<skill>/SKILL.md).\n")
    assert any("aucun renvoi entre skills" in m for m in rouges(tmp_path))


def test_aucun_renvoi(tmp_path: Path) -> None:
    """Un contrôle qui n'examine rien échoue."""
    _ = ecrire(tmp_path, "skills/source/SKILL.md", "Aucun renvoi ici.\n")
    assert any("contrôle sans objet" in m for m in rouges(tmp_path))


def test_skills_vide(tmp_path: Path) -> None:
    assert any("contrôle sans objet" in m for m in rouges(tmp_path))


# --- Deux défauts introduits par le contrôle d'ancre, trouvés à l'audit ------


def test_ancre_vers_un_titre_de_niveau_trois(tmp_path: Path) -> None:
    """R9 — une ancre vise n'importe quel niveau de titre, pas seulement `## `.

    `sections()` ne retient que les `## ` parce que le contrôle 1 juge la couverture
    des sections de premier rang. Réutiliser sa vue ici déclarait morte une ancre
    parfaitement valide.
    """
    _ = ecrire(
        tmp_path,
        "skills/cible/references/contrat.md",
        "# Contrat\n\n## Champs\n\n### Cas particulier\n\nx\n",
    )
    _ = ecrire(
        tmp_path,
        "skills/source/SKILL.md",
        "Voir [Cas](../cible/references/contrat.md#cas-particulier).\n",
    )
    assert rouges(tmp_path) == []


def test_lien_avec_titre_markdown(tmp_path: Path) -> None:
    """R10 — le titre optionnel d'un lien ne doit pas faire échapper le renvoi.

    Un motif qui exigeait `)` juste après l'ancre laissait passer ces liens sans
    aucun contrôle : la cible pouvait être absente sans qu'un rouge apparaisse.
    """
    _ = ecrire(
        tmp_path,
        "skills/source/SKILL.md",
        'Voir [X](../disparu/references/contrat.md "Le contrat").\n',
    )
    assert any("renvoi mort" in m for m in rouges(tmp_path))


def test_lien_avec_titre_markdown_qui_resout(tmp_path: Path) -> None:
    _ = ecrire(tmp_path, "skills/cible/references/contrat.md", "# Contrat\n\n## Champs\n\nx\n")
    _ = ecrire(
        tmp_path,
        "skills/source/SKILL.md",
        'Voir [X](../cible/references/contrat.md#champs "Le contrat").\n',
    )
    assert rouges(tmp_path) == []


def test_titre_dans_une_fence_nest_pas_une_ancre(tmp_path: Path) -> None:
    """Un `###` à l'intérieur d'un bloc de code est du contenu, pas un titre."""
    _ = ecrire(
        tmp_path,
        "skills/cible/references/contrat.md",
        "# Contrat\n\n```markdown\n### Faux titre\n```\n",
    )
    _ = ecrire(
        tmp_path,
        "skills/source/SKILL.md",
        "Voir [X](../cible/references/contrat.md#faux-titre).\n",
    )
    assert any("ancre morte" in m for m in rouges(tmp_path))
