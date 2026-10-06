"""Santé du système de skills — ce que le hook de démarrage garantit.

Chaque cas monte un `bin/` jouet : le script ne lit que la racine qu'on lui donne,
donc un test se réduit à fabriquer le défaut visé. Aucun test ne lit le vrai dépôt —
un contrôle qui ne passerait au vert qu'ici serait invérifiable.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import sante_skills


@pytest.fixture
def racine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Une racine jouet avec un `bin/` vide et un skill à cibler."""
    (tmp_path / "bin").mkdir()
    cible = tmp_path / "skills" / "x" / "scripts" / "y.py"
    cible.parent.mkdir(parents=True)
    _ = cible.write_text("#!/usr/bin/env python3\n")
    cible.chmod(0o755)
    monkeypatch.setattr(sante_skills, "racine", lambda: tmp_path)
    return tmp_path


def lier(racine: Path, nom: str, cible: str) -> None:
    (racine / "bin" / nom).symlink_to(cible)


def test_systeme_sain(racine: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    lier(racine, "y", "../skills/x/scripts/y.py")
    monkeypatch.setenv("PATH", str(racine / "bin") + os.pathsep + os.environ["PATH"])
    assert sante_skills.anomalies() == []


def test_bin_absent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sante_skills, "racine", lambda: tmp_path)
    assert any("n'existe pas" in m for m in sante_skills.anomalies())


@pytest.mark.usefixtures("racine")
def test_bin_vide() -> None:
    """Le `bin/` que monte la fixture est vide : elle sert ici d'effet de bord seul."""
    assert any("est vide" in m for m in sante_skills.anomalies())


def test_lien_casse(racine: Path) -> None:
    lier(racine, "y", "../skills/x/scripts/disparu.py")
    assert any("pointe dans le vide" in m for m in sante_skills.anomalies())


def test_lien_absolu(racine: Path) -> None:
    """Un lien absolu marche ici et nulle part ailleurs : c'est ce que bin/ supprime."""
    lier(racine, "y", str(racine / "skills" / "x" / "scripts" / "y.py"))
    assert any("pointe en absolu" in m for m in sante_skills.anomalies())


def test_absent_du_path(racine: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    lier(racine, "y", "../skills/x/scripts/y.py")
    monkeypatch.setenv("PATH", "/nulle/part")
    maux = sante_skills.anomalies()
    assert any("introuvable dans le PATH" in m for m in maux)
    assert any('export PATH="' in m for m in maux), "le message doit dire quoi faire"


def test_homonyme_gagne_dans_le_path(racine: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Plus trompeur qu'une absence : la commande existe, mais ce n'est pas la nôtre."""
    autre = racine / "ailleurs"
    autre.mkdir()
    impost = autre / "y"
    _ = impost.write_text("#!/bin/sh\n")
    impost.chmod(0o755)
    lier(racine, "y", "../skills/x/scripts/y.py")
    monkeypatch.setenv("PATH", str(autre) + os.pathsep + str(racine / "bin"))
    assert any("résout vers" in m for m in sante_skills.anomalies())


def test_fichier_ordinaire_dans_bin(racine: Path) -> None:
    _ = (racine / "bin" / "y").write_text("#!/bin/sh\n")
    assert any("n'est pas un lien symbolique" in m for m in sante_skills.anomalies())


# --- Deux lecteurs, deux troncatures ----------------------------------------
#
# Constaté le 2026-08-29 : de tout le `stderr` d'un hook en échec, l'hôte n'affiche à
# l'utilisateur que la PREMIÈRE ligne. Un en-tête qui compte sans nommer y perd
# exactement ce qui sert.


def test_stderr_tient_sur_une_ligne_et_nomme_tout(
    racine: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    lier(racine, "casse", "../skills/x/scripts/disparu.py")
    code = sante_skills.main()
    capture = capsys.readouterr()

    assert code == 1
    lignes = capture.err.rstrip("\n").split("\n")
    assert len(lignes) == 1, "l'hôte ne montre que la première ligne : tout doit y tenir"
    assert "pointe dans le vide" in lignes[0], "la ligne unique doit nommer l'anomalie"


def test_stdout_porte_le_detail(racine: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Le `stdout` d'un hook SessionStart revient au modèle — l'autre lecteur."""
    lier(racine, "casse", "../skills/x/scripts/disparu.py")
    _ = sante_skills.main()
    capture = capsys.readouterr()

    assert "pointe dans le vide" in capture.out
    assert capture.out.count("✗") >= 1


def test_silencieux_sur_les_deux_flux_quand_tout_va_bien(
    racine: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    lier(racine, "y", "../skills/x/scripts/y.py")
    monkeypatch.setenv("PATH", str(racine / "bin") + os.pathsep + os.environ["PATH"])
    code = sante_skills.main()
    capture = capsys.readouterr()

    assert code == 0
    assert capture.out == "" and capture.err == ""


# ------------------------------------------------------- le venv et ses dépendances
def poser_venv(racine: Path, *distributions: str) -> Path:
    """Un venv jouet : le `site-packages` et les `*.dist-info` que pip et uv y posent.

    Chaque distribution s'écrit « nom » ou « nom==version » ; sans version, 1.0.
    """
    site = racine / ".venv" / "lib" / "python3.12" / "site-packages"
    site.mkdir(parents=True)
    for spec in distributions:
        nom, _, version = spec.partition("==")
        (site / f"{nom}-{version or '1.0'}.dist-info").mkdir()
    return site


def test_sans_requirements_aucune_exigence(racine: Path) -> None:
    """LA DÉCLARATION CRÉE L'EXIGENCE : un dépôt qui ne déclare rien n'a pas à se voir
    reprocher l'absence d'un venv — sinon tout dépôt sans dépendance crierait."""
    assert sante_skills._dependances(racine) == []


def test_venv_absent_est_nomme_avec_la_reparation(racine: Path) -> None:
    _ = (racine / "requirements.txt").write_text("tomlkit\n", encoding="utf-8")
    (mal,) = sante_skills._dependances(racine)

    assert "absent ou incomplet" in mal
    assert "uv venv" in mal


def test_dependance_declaree_mais_absente_est_nommee(racine: Path) -> None:
    _ = (racine / "requirements.txt").write_text("tomlkit\npytest\n", encoding="utf-8")
    _ = poser_venv(racine, "pytest")
    (mal,) = sante_skills._dependances(racine)

    assert "tomlkit déclaré" in mal  # nommée seule : pytest est là, il ne doit pas figurer


def test_venv_complet_ne_dit_rien(racine: Path) -> None:
    _ = (racine / "requirements.txt").write_text("tomlkit\npytest\n", encoding="utf-8")
    _ = poser_venv(racine, "tomlkit", "pytest")

    assert sante_skills._dependances(racine) == []


def test_commentaires_et_contraintes_de_version_sont_ignores(racine: Path) -> None:
    """`tomlkit>=0.13` déclare la distribution « tomlkit » : la contrainte n'est pas
    du nom, et un `# commentaire` n'est pas une dépendance."""
    _ = (racine / "requirements.txt").write_text(
        "# les écrivains TOML\ntomlkit>=0.13  # préservant\n\n", encoding="utf-8"
    )
    _ = poser_venv(racine, "tomlkit")

    assert sante_skills._dependances(racine) == []


def test_le_nom_de_distribution_est_normalise(racine: Path) -> None:
    """pip écrit `ruamel_yaml-…dist-info` pour « ruamel-yaml » : comparer brut ferait
    crier le contrôle sur une dépendance pourtant installée."""
    _ = (racine / "requirements.txt").write_text("ruamel-yaml\n", encoding="utf-8")
    _ = poser_venv(racine, "ruamel_yaml")

    assert sante_skills._dependances(racine) == []


def test_version_epinglee_divergente_est_nommee(racine: Path) -> None:
    """UNE ÉPINGLE QU'ON NE VÉRIFIE PAS EST DÉCORATIVE. tomlkit est épinglé parce que
    `list-dir` s'en sert comme garant de mise en forme : un changement de son rendu se
    verrait dans le front matter de tous les éléments, pas dans une exception."""
    _ = (racine / "requirements.txt").write_text("tomlkit==0.15.1\n", encoding="utf-8")
    _ = poser_venv(racine, "tomlkit==0.11.0")
    (mal,) = sante_skills._dependances(racine)

    assert "tomlkit 0.11.0 au lieu de 0.15.1" in mal
    assert "uv pip install" in mal


def test_version_epinglee_respectee_ne_dit_rien(racine: Path) -> None:
    _ = (racine / "requirements.txt").write_text("tomlkit==0.15.1\n", encoding="utf-8")
    _ = poser_venv(racine, "tomlkit==0.15.1")

    assert sante_skills._dependances(racine) == []


def test_contrainte_souple_ne_controle_que_la_presence(racine: Path) -> None:
    """`>=` déclare un intervalle, pas une version : le vérifier demanderait un
    résolveur. On ne contrôle donc que la présence, et on le dit."""
    _ = (racine / "requirements.txt").write_text("tomlkit>=0.13\n", encoding="utf-8")
    _ = poser_venv(racine, "tomlkit==0.15.1")

    assert sante_skills._dependances(racine) == []


def test_un_nom_a_tirets_garde_sa_version(racine: Path) -> None:
    """`ruamel_yaml-0.18.6.dist-info` : c'est le DERNIER tiret qui sépare le nom de la
    version, sinon « ruamel » serait pris pour la distribution et « yaml » pour sa
    version."""
    _ = (racine / "requirements.txt").write_text("ruamel-yaml==0.18.6\n", encoding="utf-8")
    _ = poser_venv(racine, "ruamel_yaml==0.18.6")

    assert sante_skills._dependances(racine) == []


def test_une_epingle_a_marqueur_ne_controle_que_la_presence(racine: Path) -> None:
    """Dire si `; python_version >= "3.12"` s'applique demande un résolveur. Signaler
    une divergence sur une ligne peut-être inactive serait l'avertissement qu'on
    apprend à ignorer — on retombe donc sur la présence seule, et on le dit."""
    _ = (racine / "requirements.txt").write_text(
        'tomlkit==0.15.1 ; python_version >= "3.12"\n', encoding="utf-8"
    )
    _ = poser_venv(racine, "tomlkit==0.11.0")

    assert sante_skills._dependances(racine) == []


def test_une_epingle_a_marqueur_exige_quand_meme_la_presence(racine: Path) -> None:
    _ = (racine / "requirements.txt").write_text(
        'tomlkit==0.15.1 ; python_version >= "3.12"\n', encoding="utf-8"
    )
    _ = poser_venv(racine)
    (mal,) = sante_skills._dependances(racine)

    assert "tomlkit" in mal


# ------------------------------------------------- les mods à la racine des skills
def poser_mod(
    racine: Path,
    dossier: str,
    plugin: str | None = '{"name": "m"}',
    modules: str | None = '{"modules": ["./register.ts"]}',
    *,
    module: bool = True,
) -> Path:
    """Un mod jouet : son manifeste, son `hooks.json` et `hooks/register.ts`.

    `None` omet le fichier, `module=False` omet le module.
    """
    mod = racine / dossier
    (mod / ".claude-plugin").mkdir(parents=True)
    (mod / "hooks").mkdir()
    if plugin is not None:
        _ = (mod / ".claude-plugin" / "plugin.json").write_text(plugin, encoding="utf-8")
    if modules is not None:
        _ = (mod / "hooks" / "hooks.json").write_text(modules, encoding="utf-8")
    if module:
        _ = (mod / "hooks" / "register.ts").write_text("", encoding="utf-8")
    return mod


def test_mods_sains_ne_disent_rien(racine: Path) -> None:
    """Un fournisseur sous `skills/`, son client sous `.claude/skills/` : la dépendance
    se résout d'un dossier à l'autre, comme `outillage` vers `mod-commun`."""
    _ = poser_mod(racine, "skills/commun", '{"name": "commun"}')
    _ = poser_mod(racine, ".claude/skills/client", '{"name": "client", "dependencies": ["commun"]}')

    assert sante_skills.mods_en_defaut(racine) == []


def test_un_skill_sans_mod_n_est_pas_controle(racine: Path) -> None:
    """La fixture pose `skills/x/` sans `.claude-plugin/` ni `hooks/` : rien à dire."""
    assert sante_skills.mods_en_defaut(racine) == []


def test_manifeste_absent_est_nomme(racine: Path) -> None:
    _ = poser_mod(racine, "skills/m", plugin=None)
    (mal,) = sante_skills.mods_en_defaut(racine)

    assert "skills/m" in mal and "plugin.json illisible" in mal


def test_manifeste_qui_n_est_pas_du_json_est_nomme(racine: Path) -> None:
    _ = poser_mod(racine, "skills/m", plugin='{"name": "m",}')
    (mal,) = sante_skills.mods_en_defaut(racine)

    assert "plugin.json illisible" in mal


def test_manifeste_sans_nom_est_nomme(racine: Path) -> None:
    """Le moteur range un mod sous son `name` : sans lui, rien ne le désigne."""
    _ = poser_mod(racine, "skills/m", plugin='{"version": "0.1.0"}')
    (mal,) = sante_skills.mods_en_defaut(racine)

    assert "ne porte pas de « name »" in mal


def test_hooks_json_absent_est_nomme(racine: Path) -> None:
    _ = poser_mod(racine, "skills/m", modules=None)
    (mal,) = sante_skills.mods_en_defaut(racine)

    assert "hooks.json illisible" in mal


def test_module_absent_est_nomme(racine: Path) -> None:
    _ = poser_mod(racine, "skills/m", module=False)
    (mal,) = sante_skills.mods_en_defaut(racine)

    assert "'./register.ts'" in mal and "absent" in mal


def test_dependance_absente_est_nommee(racine: Path) -> None:
    """Un client dont le fournisseur manque appelle un nom de `$` que rien ne pose."""
    _ = poser_mod(racine, "skills/m", '{"name": "m", "dependencies": ["mod-commun"]}')
    (mal,) = sante_skills.mods_en_defaut(racine)

    assert "'mod-commun'" in mal and "aucun mod présent" in mal


def test_plugin_dirs_dans_settings_est_nomme(racine: Path) -> None:
    _ = (racine / "settings.json").write_text(
        '{"env": {"CLAUDE_CODE_PLUGIN_DIRS": "skills/lexique/mod"}}', encoding="utf-8"
    )
    (mal,) = sante_skills.plugin_dirs_restant(racine)

    assert "CLAUDE_CODE_PLUGIN_DIRS" in mal


def test_settings_sans_plugin_dirs_ne_dit_rien(racine: Path) -> None:
    _ = (racine / "settings.json").write_text('{"env": {}}', encoding="utf-8")

    assert sante_skills.plugin_dirs_restant(racine) == []


def test_les_mods_remontent_dans_anomalies(racine: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Le contrôle est branché : le hook de démarrage le voit, pas seulement les tests."""
    lier(racine, "y", "../skills/x/scripts/y.py")
    monkeypatch.setenv("PATH", str(racine / "bin") + os.pathsep + os.environ["PATH"])
    _ = poser_mod(racine, "skills/m", plugin=None)
    _ = (racine / "settings.json").write_text(
        '{"env": {"CLAUDE_CODE_PLUGIN_DIRS": "x"}}', encoding="utf-8"
    )

    maux = sante_skills.anomalies()
    assert any("plugin.json illisible" in m for m in maux)
    assert any("CLAUDE_CODE_PLUGIN_DIRS" in m for m in maux)
