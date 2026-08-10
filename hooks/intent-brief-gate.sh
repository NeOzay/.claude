#!/usr/bin/env bash
# PreToolUse / EnterPlanMode — rappelle le skill intent-brief avant le premier passage
# en mode plan d'une session. Bloque une seule fois : le second appel passe.
#
# PORTÉE : ce hook n'intercepte que le mode plan déclenché par un appel d'outil
# EnterPlanMode. Une bascule manuelle du mode de permission (Shift+Tab) ne passe pas
# par un outil et n'est donc PAS couverte. Choix assumé : couvrir ce cas imposerait un
# hook UserPromptSubmit qui injecterait du contexte à chaque session, y compris hors
# planification.
#
# Échoue toujours OUVERT : un hook purement pédagogique ne doit jamais verrouiller le
# mode plan.
set -uo pipefail

payload=$(cat)

session=""
if command -v jq >/dev/null 2>&1; then
  session=$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null)
fi
# Pas de session identifiable → ne pas bloquer, plutôt que de mutualiser un marqueur
# entre toutes les sessions (le gate ne se déclencherait alors plus jamais).
[ -n "$session" ] || exit 0

# Un brief déjà écrit ou repris récemment → le cadrage a eu lieu, laisser filer.
# Couvre aussi l'auto-interception : intent-brief appelle lui-même EnterPlanMode.
if find .claude/implementation -maxdepth 1 -name '*.brief.md' -mmin -120 2>/dev/null | read -r _; then
  exit 0
fi

marker_dir="${TMPDIR:-/tmp}/claude-intent-brief-gate"
marker="$marker_dir/$session"

# Déjà passé pour cette session → laisser filer.
[ -e "$marker" ] && exit 0

# Purge opportuniste des marqueurs des sessions anciennes.
find "$marker_dir" -maxdepth 1 -type f -mtime +7 -delete 2>/dev/null

# Marqueur impossible à poser → ne pas bloquer : sans lui, le déblocage promis dans le
# message ci-dessous n'aurait pas lieu et le mode plan resterait verrouillé.
mkdir -p "$marker_dir" && : >"$marker" || exit 0

cat >&2 <<'EOF'
Passage en mode plan intercepté (une seule fois par session).

Avant de planifier : demander à l'utilisateur s'il veut cadrer l'intention avec le skill
intent-brief (brief persistant : intention, critères de réussite, hors-périmètre, signaux
de dérive). S'il existe déjà un .claude/implementation/<slug>.brief.md correspondant au
chantier, le lire et enchaîner directement sur le plan.

Poser la question, attendre la réponse, puis relancer EnterPlanMode — le prochain appel
ne sera pas intercepté.
EOF
exit 2
