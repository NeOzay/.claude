#!/usr/bin/env bash
# SessionStart — rappelle l'outillage du dépôt.
#
# BRANCHÉ DANS `.claude/settings.json`, LES SETTINGS DE PROJET, et pas dans
# `~/.claude/settings.json`, qui est celui de l'utilisateur : ceux-là valent pour tous
# ses projets, où les règles d'ici sont hors sujet et parfois fausses (« uvx
# basedpyright » dans un projet Node). Le settings de projet ne charge le hook que
# lorsque ce dépôt est ouvert, et il est versionné avec lui.
#
# La garde sur le répertoire ci-dessous n'est donc plus ce qui limite la portée — c'est
# une ceinture, qui rend le script correct où qu'on le branche.
#
# QUATRE LIGNES, PAS LE FICHIER. `OUTILLAGE.md` fait ~2 000 tokens ; le recopier à chaque
# session coûterait plus que ce qu'il évite. Le rappel nomme les lanceurs, l'interdit qui
# a réellement coûté, et le chemin — le reste se lit à la demande.
#
# CE HOOK NE COUVRE PAS LES SOUS-AGENTS : ils ne reçoivent pas SessionStart. C'est
# pourquoi la même règle est recopiée en dur dans `agents/*.md`, et c'est là qu'elle
# manquait le 2026-09-09, quand trois audits de clôture ont lancé `pyright`.
#
# ÉCHOUE OUVERT : un rappel n'a jamais de raison d'interrompre le démarrage d'une session.
set -uo pipefail

racine="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Hors du dépôt → rien à dire. `$PWD` est le répertoire de travail de la session.
case "$PWD/" in
  "$racine"/*) ;;
  *) exit 0 ;;
esac

[ -f "$racine/OUTILLAGE.md" ] || exit 0

cat <<EOF
Outillage de ce dépôt ($racine/OUTILLAGE.md) :
  · linters : \`uvx ruff check <chemins>\` et \`uvx --with pytest basedpyright\` — jamais
    \`pyright\`, qui rejette le typeCheckingMode "all" du dépôt et vérifie en mode par
    défaut en rendant un décompte d'apparence normale.
  · tests : \`$racine/.venv/bin/python -m pytest <chemins>\` — le python3 du PATH n'a ni
    pytest ni tomlkit.
  · comparer à la base : \`git archive <base>\` vers un répertoire temporaire, jamais
    \`git stash\`, qui n'annule pas un fichier déjà commité sur la branche.
EOF
