#!/usr/bin/env bash
# Rappelle l'outillage du dépôt à un sous-agent, à son lancement.
#
# APPELÉ PAR LE MOD OUTILLAGE, `.claude/skills/outillage/`, au hook `agent.spawn` : le mod
# lance ce script par `$.commande.lancer` et préfixe le prompt du sous-agent de sa sortie.
# Il ne porte aucune règle, il transporte : ce que le sous-agent reçoit s'écrit ici.
#
# LES SOUS-AGENTS SEULS. La session principale trouve l'outillage par `.claude/CLAUDE.md`,
# qui renvoie à `OUTILLAGE.md` ; un sous-agent ne lit ni l'un ni l'autre. Le mod vit dans
# `.claude/skills/` du dépôt : il ne se charge que dans une session ouverte sur ce dépôt,
# où les règles d'ici valent, et non dans les autres projets, où elles seraient fausses
# (« uvx basedpyright » dans un projet Node).
#
# QUELQUES LIGNES, PAS LE FICHIER. `OUTILLAGE.md` fait ~2 000 tokens ; le recopier à chaque
# sous-agent coûterait plus que ce qu'il évite. Le rappel nomme les lanceurs, l'interdit qui
# a réellement coûté, et le chemin — le reste se lit à la demande.
#
# ÉCHOUE OUVERT : un rappel n'a jamais de raison d'empêcher un sous-agent de démarrer.
set -uo pipefail

# Le script vit en `.claude/skills/outillage/scripts/` : la racine est quatre niveaux
# au-dessus.
racine="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"

# Hors du dépôt → rien à dire. Le mod le lance depuis la racine de la session : c'est une
# ceinture, qui rend le script correct où qu'on l'appelle.
case "$PWD/" in
  "$racine"/*) ;;
  *) exit 0 ;;
esac

[ -f "$racine/OUTILLAGE.md" ] || exit 0

cat <<EOF
Outillage de ce dépôt ($racine/OUTILLAGE.md) :
  · formatage : \`uvx ruff format <chemins>\` avant de commiter du Python,
    \`uvx rumdl fmt <chemins>\` avant de commiter du Markdown,
    \`npx --yes @biomejs/biome@2 format --write <chemins>\` avant de commiter le TypeScript
    d'un mod.
  · linters : \`uvx ruff check <chemins>\` et \`uvx --with pytest basedpyright\` — jamais
    \`pyright\`, qui rejette le typeCheckingMode "all" du dépôt et vérifie en mode par
    défaut en rendant un décompte d'apparence normale.
  · tests : \`$racine/.venv/bin/python -m pytest <chemins>\` — le python3 du PATH n'a ni
    pytest ni tomlkit.
  · comparer à la base : \`git archive <base>\` vers un répertoire temporaire, jamais
    \`git stash\`, qui n'annule pas un fichier déjà commité sur la branche.
EOF
