#!/usr/bin/env bash
# SessionStart — met les commandes de `.claude/bin/` à la disposition de l'agent.
#
# MODÈLE À COPIER dans `<projet>/.claude/hooks/commandes-locales.sh`, et à brancher dans
# `<projet>/.claude/settings.json`, LES SETTINGS DU PROJET : branché dans ceux de
# l'utilisateur, il vaudrait pour tous ses projets. Procédure et limites :
# `references/commandes-locales.md` de la skill skill-convention.
#
# PORTÉE : l'agent et ses sous-agents, dans ce projet seulement. Le `PATH` est étendu par
# `$CLAUDE_ENV_FILE`, que Claude Code source avant chaque commande Bash de la session ;
# le shell de l'utilisateur n'est pas touché.
#
# AJOUTER, NE JAMAIS ÉCRASER : `>>` sur `$CLAUDE_ENV_FILE`. Claude Code donne aujourd'hui
# un fichier à chaque hook, mais rien ne promet qu'il le fera toujours.
#
# ÉCHOUE OUVERT : un projet sans `.claude/bin/`, une session hors du projet, une variable
# absente — sortie 0 et rien d'écrit. Un rappel n'interrompt jamais un démarrage.
set -uo pipefail

racine="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
bin="$racine/.claude/bin"

# Hors du projet → rien à faire. `$PWD` est le répertoire de travail de la session.
case "$PWD/" in
  "$racine"/*) ;;
  *) exit 0 ;;
esac

[ -n "${CLAUDE_ENV_FILE:-}" ] || exit 0
[ -d "$bin" ] || exit 0

# `%q` : un chemin qui porte une espace, un guillemet ou un `$` reste un seul mot.
printf 'export PATH=%q:"$PATH"\n' "$bin" >> "$CLAUDE_ENV_FILE" || exit 0

# L'agent ne découvre pas seul le contenu d'un `PATH` : la sortie du hook les lui annonce.
commandes=()
for f in "$bin"/*; do
  [ -f "$f" ] && [ -x "$f" ] && commandes+=("$(basename "$f")")
done
[ "${#commandes[@]}" -gt 0 ] || exit 0

echo "Commandes locales à ce projet ($bin), appelables par leur nom :"
printf '  · %s\n' "${commandes[@]}"
exit 0
