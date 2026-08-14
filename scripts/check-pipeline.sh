#!/usr/bin/env bash
# Garde-fou du pipeline de skills : vérifie que le contrat partagé n'a pas dérivé.
#
# PORTÉE : six contrôles, tous mécaniques. Ce script ne juge ni le contenu ni la
# pertinence des règles — il constate que chacune reste définie à un seul endroit et
# que les renvois qui y mènent résolvent encore.
#
# ÉCHEC FERMÉ : sortie 1 dès qu'un contrôle échoue. C'est un outil de vérification,
# contrairement à hooks/intent-brief-gate.sh qui est pédagogique et échoue ouvert.
#
# UN CONTRÔLE QUI N'EXAMINE RIEN ÉCHOUE. Un motif qui ne matche plus rien, une liste
# vide, un répertoire absent : tous signalés comme erreurs, jamais comme succès. Un
# garde-fou silencieusement vide est pire que pas de garde-fou.
#
# LES AGENTS SONT HORS PÉRIMÈTRE des contrôles 1 et 2. agents/step-implementer.md et
# agents/implementation-auditor.md dupliquent volontairement les règles qui les
# concernent : ils se chargent dans leur propre fenêtre, et un agent en isolation qui
# ne suivrait pas un renvoi perdrait le garde-fou. Le contrôle 4 vérifie justement
# qu'ils n'ont pas été rendus dépendants du noyau.
#
# Identifiants en ASCII : bash n'accepte pas les caractères accentués dans les noms
# de variables.
set -uo pipefail

cd "$(git rev-parse --show-toplevel)" || exit 1

CONTRAT="skills/implementation-tracker/references/contrat.md"
# Copie **du dépôt audité**, pas la skill installée : le script vient de `cd` vers la
# racine git, et il doit juger ce que le diff contient — sur un clone ailleurs, viser
# $HOME validerait un fichier étranger au chantier.
LISTER="skills/implementation-tracker/scripts/impl-list.sh"
fails=0

ko() { printf '  ✗ %s\n' "$1"; fails=$((fails + 1)); }
ok() { printf '  ✓ %s\n' "$1"; }

slugify() { printf '%s\n' "$1" | tr 'A-Z' 'a-z' | sed "s/['’]//g; s/ /-/g"; }

[ -f "$CONTRAT" ] || { printf 'FATAL : contrat introuvable (%s)\n' "$CONTRAT"; exit 1; }

# ---------------------------------------------------------------- 1. ancres mortes
printf '\n1. Renvois vers le contrat\n'

anchors=$(grep '^## ' "$CONTRAT" | sed 's/^## //' | while IFS= read -r t; do slugify "$t"; done)
[ -n "$anchors" ] || ko "aucune section dans le contrat — le fichier a été vidé ou restructuré"

total=$(grep -roh '](\([^)]*\)contrat\.md#[a-zà-ÿ0-9-]*' --include='*.md' skills | wc -l)
if [ "$total" -eq 0 ]; then
  ko "aucun renvoi trouvé — le contrat n'est cité nulle part, ou le motif ne matche plus"
fi

bad=0
while IFS= read -r file; do
  dir=$(dirname "$file")
  while IFS= read -r link; do
    path=${link%contrat.md#*}
    anchor=${link##*#}
    if [ ! -f "$dir/${path}contrat.md" ]; then
      printf '  ✗ %s → chemin mort : %scontrat.md\n' "$file" "$path"
      bad=$((bad + 1))
    elif ! printf '%s\n' "$anchors" | grep -qx "$anchor"; then
      printf '  ✗ %s → ancre morte : #%s\n' "$file" "$anchor"
      bad=$((bad + 1))
    fi
  done < <(grep -o '](\([^)]*\)contrat\.md#[a-zà-ÿ0-9-]*' "$file" | sed 's/^](//')
done < <(grep -rl 'contrat\.md#' --include='*.md' skills)

if [ "$bad" -gt 0 ]; then
  fails=$((fails + bad))
elif [ "$total" -gt 0 ]; then
  ok "$total renvois, tous résolvent"
fi

while IFS= read -r a; do
  [ -n "$a" ] || continue
  grep -rq "contrat.md#$a" --include='*.md' skills || ko "section jamais citée : #$a"
done <<< "$anchors"

# ------------------------------------------------- 2. empreintes de définition unique
printf '\n2. Règles définies à un seul endroit\n'

# Chaque motif est une formulation distinctive du **corps** d'une règle — jamais d'une
# ligne d'appel. Table construite empiriquement le 2026-08-14 : chacun n'avait alors
# qu'une occurrence dans skills/. Exactement une reste la règle, dans les deux sens —
# 0 signifie que la définition a disparu du contrat, ≥2 qu'elle a été recopiée.
fingerprints=(
  'refonte-complete-du-systeme-dauth'   # arborescence : contre-exemple de slug
  'réattribue ces noms'                 # arborescence : nommage du plan archivé
  'Une valeur absente vaut'             # frontmatter : défaut d'execution
  'le suivi fait foi'                   # autorité et divergence
  'un seul tour'                        # format d'étape : granularité
  'rev-parse --show-toplevel'           # contrat des sous-agents : racine du dépôt
  'ramasse ce qui traîne'               # branche et commits : staging
  'jamais devinée'                      # dates et listing
)

for motif in "${fingerprints[@]}"; do
  n=$(grep -rl "$motif" --include='*.md' skills | wc -l)
  case "$n" in
    1) ok "« $motif »" ;;
    0) ko "« $motif » : introuvable — la règle a disparu du contrat" ;;
    *) ko "« $motif » : $n fichiers — la règle a été recopiée hors du contrat" ;;
  esac
done

# ------------------------------------------------------------- 3. filtre de listing
printf '\n3. Filtre de listing des suivis\n'

if [ ! -f "$LISTER" ]; then
  ko "script de listing absent : $LISTER"
else
  listing=$(bash "$LISTER" .claude/implementation/done)
  if [ -z "$listing" ]; then
    ko "aucun fichier examiné dans done/ — contrôle sans objet"
  else
    noise=$(printf '%s\n' "$listing" | grep -cE '\.(brief|audit|plan)\.md$')
    if [ "$noise" -eq 0 ]; then
      ok "$(printf '%s\n' "$listing" | wc -l) fichiers listés, aucun brief/audit/plan"
    else
      ko "$noise fichiers parasites remontés par le listing"
    fi
  fi
fi

# ---------------------------------------------------- 4. indépendance des sous-agents
printf '\n4. Indépendance des sous-agents\n'

if [ ! -d agents ]; then
  ko "répertoire agents/ absent — contrôle sans objet"
else
  count=$(ls agents/*.md 2>/dev/null | wc -l)
  if [ "$count" -eq 0 ]; then
    ko "aucun agent examiné — contrôle sans objet"
  else
    coupled=$(grep -l 'contrat\.md' agents/*.md 2>/dev/null || true)
    if [ -n "$coupled" ]; then
      while IFS= read -r f; do
        ko "$f renvoie au contrat : un agent isolé doit rester auto-suffisant"
      done <<< "$coupled"
    else
      ok "$count agents, aucun renvoi au contrat"
    fi
  fi
fi

# ------------------------------------------- 5. chemins du frontmatter après archivage
printf '\n5. Chemins du frontmatter des chantiers archivés\n'

archives=$(bash "$LISTER" .claude/implementation/done 2>/dev/null)
if [ -z "$archives" ]; then
  ko "aucun suivi archivé examiné — contrôle sans objet"
else
  dead=0
  while IFS= read -r name; do
    suivi=".claude/implementation/done/$name"
    for champ in plan brief audit; do
      cible=$(sed -n "s/^${champ}: *//p" "$suivi" | head -1)
      [ -n "$cible" ] || continue
      if [ ! -f "$cible" ]; then
        printf '  ✗ %s → %s: pointe dans le vide (%s)\n' "$name" "$champ" "$cible"
        dead=$((dead + 1))
      fi
    done
  done <<< "$archives"
  if [ "$dead" -gt 0 ]; then
    fails=$((fails + dead))
  else
    ok "tous les champs plan/brief/audit résolvent"
  fi
fi

# --------------------------------------- 6. portabilité des appels de script des skills
printf '\n6. Portabilité des appels de script\n'

# Un skill s'invoque depuis n'importe quel dépôt. Un chemin de script relatif au dépôt
# courant y renvoie code 127 et une sortie **vide** — que l'appelant lit comme un
# résultat, pas comme une erreur. Les scripts d'un skill s'appellent donc par chemin
# absolu ancré dans la skill. Ce contrôle existe parce que l'audit du 2026-08-14 a
# bloqué la clôture sur exactement ce défaut.
mds=$(grep -rl '' --include='*.md' skills 2>/dev/null | wc -l)
if [ "$mds" -eq 0 ]; then
  ko "aucun fichier examiné dans skills/ — contrôle sans objet"
else
  # Est acceptable : un chemin absolu (`/…` ou `$HOME/…`), ou un appel relatif **gardé
  # par un test d'existence portant sur ce même script** (cf. cloture.md, appel du
  # garde-fou : il vise un script local au dépôt et se saute proprement ailleurs).
  # Tout le reste est fautif — y compris `./scripts/…`, un chemin relatif vers la skill,
  # et un garde qui teste un autre fichier que celui qu'on lance.
  relatives=""
  while IFS= read -r hit; do
    file=${hit%%:*}
    line=${hit#*:}; line=${line#*:}
    for call in $(printf '%s\n' "$line" | grep -o 'bash "\?[^" ;)]*\.sh' | sed 's/^bash "\?//'); do
      # Toutes les écritures d'un chemin absolu, sinon le contrôle crie à tort — et un
      # contrôle qui crie à tort se fait désactiver, ce qui tue le garde-fou entier.
      case "$call" in
        /*|'~'/*|'$HOME'/*|'${HOME}'/*) continue ;;
      esac
      printf '%s\n' "$line" | grep -q "\[ -f \"\?$call" && continue
      relatives="$relatives$file → $call"$'\n'
    done
  done < <(grep -rn 'bash [^ ]*\.sh' --include='*.md' skills 2>/dev/null)

  if [ -n "$relatives" ]; then
    while IFS= read -r l; do
      [ -n "$l" ] || continue
      ko "appel relatif non gardé : $l — inopérant et silencieux hors de ~/.claude"
    done <<< "$relatives"
  else
    ok "$mds fichiers examinés, aucun appel de script relatif non gardé"
  fi
fi

# ------------------------------------------------------------------------- verdict
printf '\n'
if [ "$fails" -eq 0 ]; then
  printf 'Pipeline conforme.\n'
  exit 0
fi
printf '%d anomalie(s).\n' "$fails"
exit 1
