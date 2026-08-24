"""Bout-en-bout : un dépôt-jouet sain, puis un défaut injecté par contrôle.

CE QUE CE FICHIER PROUVE et que les unitaires ne prouvent pas : que les sept contrôles
sont branchés dans `main`, que chacun CRIE sur son défaut, et que le script sort en
code 1 dès qu'un seul est rouge. Un garde-fou dont un contrôle serait débranché
passerait tous les unitaires.

C'est la version rejouable des injections manuelles que les rapports d'audit de
`contrat-pipeline` recopiaient en prose.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import check_pipeline
import pytest
from check_pipeline import LISTER, main
from conftest import CONTRAT_REL, ecrire

CONTRAT = """# Contrat

## Une regle

Le corps porte la formulation distinctive.

## Une autre

Le second corps, avec sa propre formule.
"""

TABLE = {"une-regle": ("formulation distinctive",), "une-autre": ("propre formule",)}

LISTER_FIDELE = '''
from pathlib import Path

ANNEXES = (".brief.md", ".audit.md", ".plan.md")


def suivis(dir: Path) -> list[str]:
    if not dir.is_dir():
        return []
    return sorted(
        p.name for p in dir.iterdir()
        if p.is_file() and p.name.endswith(".md") and not p.name.endswith(ANNEXES)
    )
'''


@pytest.fixture
def depot_sain(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(check_pipeline, "EMPREINTES", TABLE)
    monkeypatch.setattr(check_pipeline, "repo_root", lambda: tmp_path)

    _ = ecrire(tmp_path, CONTRAT_REL, CONTRAT)
    _ = ecrire(tmp_path, LISTER, LISTER_FIDELE)
    _ = ecrire(
        tmp_path,
        "skills/implementation-tracker/SKILL.md",
        "[Une](references/contrat.md#une-regle) et [Autre](references/contrat.md#une-autre)\n\n"
        "```bash\n"
        'python3 "$HOME/.claude/skills/implementation-tracker/scripts/impl_list.py" .\n'
        "```\n",
    )
    _ = ecrire(tmp_path, "agents/auditeur.md", "Tu lis le suivi et le brief.\n")
    _ = ecrire(tmp_path, ".claude/plans/p.md", "plan\n")
    _ = ecrire(
        tmp_path,
        ".claude/implementation/done/chantier.md",
        "---\nplan: .claude/plans/p.md\n---\n\ncorps\n",
    )
    return tmp_path


def test_depot_sain(depot_sain: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert (depot_sain / CONTRAT_REL).is_file()
    code = main()
    sortie = capsys.readouterr().out
    assert code == 0, sortie
    assert "Pipeline conforme." in sortie
    assert sortie.count("✗") == 0
    # Les sept contrôles ont bien tourné : un titre numéroté chacun.
    for n in range(1, 8):
        assert f"\n{n}. " in sortie


INJECTIONS: list[tuple[int, str, str]] = [
    (1, "skills/x/SKILL.md", "[X](../implementation-tracker/references/contrat.md#morte)\n"),
    (2, "skills/x/SKILL.md", "la formulation distinctive recopiée\n"),
    (3, LISTER, "from pathlib import Path\n\n\ndef suivis(dir):\n    return sorted(p.name for p in dir.iterdir())\n"),
    (4, "agents/auditeur.md", "Voir references/contrat.md.\n"),
    (5, ".claude/implementation/done/chantier.md", "---\nplan: .claude/plans/disparu.md\n---\n"),
    (6, "skills/x/SKILL.md", "```bash\nbash scripts/x.sh\n```\n"),
    (7, "skills/x/SKILL.md", '```bash\npython3 "$HOME/.claude/skills/x/disparu.py"\n```\n'),
]


@pytest.mark.parametrize(("numero", "rel", "contenu"), INJECTIONS)
def test_injection(
    depot_sain: Path,
    capsys: pytest.CaptureFixture[str],
    numero: int,
    rel: str,
    contenu: str,
) -> None:
    """Un défaut, un contrôle rouge, code 1."""
    if numero == 3:
        _ = ecrire(depot_sain, ".claude/implementation/done/chantier.brief.md", "x\n")
    _ = ecrire(depot_sain, rel, contenu)

    code = main()
    sortie = capsys.readouterr().out
    assert code == 1, sortie

    bloc = sortie.split(f"\n{numero}. ")[1].split("\n\n")[0]
    assert "✗" in bloc, f"contrôle {numero} muet :\n{sortie}"


def test_repo_root_hors_depot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """La seule dépendance à git : elle se vérifie sur un vrai répertoire non versionné."""
    monkeypatch.chdir(tmp_path)
    assert check_pipeline.repo_root() is None


def test_repo_root_dans_un_depot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _ = subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    monkeypatch.chdir(tmp_path)
    racine = check_pipeline.repo_root()
    assert racine is not None
    assert racine.resolve() == tmp_path.resolve()
