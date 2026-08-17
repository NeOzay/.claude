#!/usr/bin/env bash
# Regroupe les blocs d'un rapport de revue de dette par catégorie, puis par date.
#
# PORTÉE : ce script ne juge rien. Il ne relit pas le registre, ne vérifie aucun
# constat, n'invente aucune catégorie. Il prend les étiquettes que le modèle a posées
# et les range. Le jugement est en amont, l'arbitrage en aval.
#
# POURQUOI UN SCRIPT ET PAS LE MODÈLE : regrouper une quinzaine de blocs par catégorie
# puis par date est une manipulation mécanique que le modèle fait mal — il en déplace un,
# en oublie un autre, et rien ne le signale. Ici la conservation est vérifiée : autant de
# blocs en sortie qu'en entrée, sinon erreur.
#
# ÉCHEC FERMÉ : sortie 1 dès qu'un bloc est mal formé, porte une catégorie inconnue, ou
# que le compte ne se conserve pas. Sortie 2 sur une erreur d'appel. Un tri partiel
# passerait pour un tri complet — c'est exactement le mode de défaillance qu'on refuse.
#
# ZÉRO BLOC EST UNE ERREUR, jamais un succès : un rapport vide trié sans broncher se lit
# comme « rien à arbitrer ». Même principe que les contrôles de scripts/check-pipeline.sh.
#
# IDEMPOTENT : trier un rapport déjà trié doit rendre le même document. La procédure
# l'exige — le skill écrit la sortie par-dessus le rapport, et propose de reprendre un
# rapport du jour déjà présent. Les intitulés de pile s'écrivent en « # », que le
# découpage par « ## » laissait tomber dans le corps du bloc précédent : ils étaient
# alors réémis, et se dupliquaient à chaque passe (7 → 13 → 19) sans qu'aucun contrôle
# ne bronche, celui de conservation ne comptant que les blocs. Ils sont désormais
# retirés en entrée, et leur nombre est vérifié en sortie.
#
# Identifiants de catégorie en ASCII : ce sont les seules chaînes comparées ici. Les
# libellés accentués n'apparaissent qu'en sortie, où rien ne les compare. Format du bloc :
# skills/debt-review/references/gabarit-rapport.md
set -uo pipefail

# Ordre des piles : ce qui SORT du registre d'abord, ce qui y RESTE ensuite.
CATS=(a-solder non-pertinent doublon pas-une-dette aggravee pertinent inverifiable)
LIBELLES=("À solder" "Non pertinent" "Doublon" "Pas une dette"
          "Aggravée" "Pertinent" "Invérifiable en revue")

src="${1:-}"
if [ -z "$src" ]; then
  printf 'usage: trier-revue.sh <rapport.md>\n' >&2
  exit 2
fi
if [ ! -f "$src" ]; then
  printf 'trier-revue: fichier introuvable : %s\n' "$src" >&2
  exit 2
fi

tmp=$(mktemp -d) || exit 2
trap 'rm -rf "$tmp"' EXIT

# Motif des intitulés de pile, reconstruit depuis LIBELLES pour qu'il ne puisse pas
# désigner autre chose qu'une pile réellement produite par ce script. Un « # » de corps
# qui ne correspond à aucun libellé est conservé : on ne supprime que ce qu'on a écrit.
pile_re=$(printf '%s|' "${LIBELLES[@]}")
pile_re="^# (${pile_re%|})\$"

# Découpage : un fichier par bloc, et le préambule à part. Les intitulés de pile d'un tri
# précédent sont retirés ici : sans ça, ils voyagent dans le corps du bloc qui les précède
# et ressortent en double.
#
# LE PRÉAMBULE EST CONSERVÉ. Il ne l'était pas, et c'était une impasse : la procédure y
# fait consigner la date de la revue et le compte des entrées, or le tri s'écrit par-dessus
# le rapport. Ce qui n'y survivait pas n'avait aucun endroit où exister.
awk -v dir="$tmp" -v pile="$pile_re" '
  $0 ~ pile { next }
  /^## / { n++; f = sprintf("%s/bloc-%04d", dir, n) }
  n > 0 { print > f; next }
  { print > (dir "/preambule") }
' "$src"

trim() { local s="$1"; s="${s#"${s%%[![:space:]]*}"}"; printf '%s' "${s%"${s##*[![:space:]]}"}"; }

rang() {
  local cible="$1" i
  for i in "${!CATS[@]}"; do
    [ "${CATS[$i]}" = "$cible" ] && { printf '%s' "$i"; return 0; }
  done
  return 1
}

entree=0
fails=0
: > "$tmp/index"

for f in "$tmp"/bloc-*; do
  [ -e "$f" ] || break
  entree=$((entree + 1))
  entete=$(head -1 "$f")
  corps="${entete#\#\# }"

  # Trois champs exactement. Un « | » de plus dans l'intitulé casserait l'appariement
  # avec le registre : on refuse plutôt que de deviner où couper.
  if [ "$(printf '%s' "$corps" | tr -cd '|' | wc -c)" -ne 2 ]; then
    printf 'trier-revue: en-tête mal formé (3 champs attendus) : %s\n' "$entete" >&2
    fails=$((fails + 1))
    continue
  fi

  IFS='|' read -r c d t <<< "$corps"
  c=$(trim "$c"); d=$(trim "$d"); t=$(trim "$t")

  if ! o=$(rang "$c"); then
    printf 'trier-revue: catégorie inconnue « %s » : %s\n' "$c" "$entete" >&2
    fails=$((fails + 1))
    continue
  fi
  # Mois et quantième bornés, pas seulement leur forme : « 2026-13-45 » passait, et une date
  # impossible dans un en-tête est le signe d'un intitulé recopié de travers — pas d'une coquille
  # sans conséquence. Le 30 février reste accepté : borner suffit à attraper la faute de recopie,
  # un calendrier complet en shell coûterait plus qu'il ne rapporte.
  if ! printf '%s' "$d" | grep -qE '^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'; then
    printf 'trier-revue: date invalide « %s » : %s\n' "$d" "$entete" >&2
    fails=$((fails + 1))
    continue
  fi
  if [ -z "$t" ]; then
    printf 'trier-revue: intitulé vide : %s\n' "$entete" >&2
    fails=$((fails + 1))
    continue
  fi

  printf '%s\t%s\t%s\n' "$o" "$d" "$f" >> "$tmp/index"
done

if [ "$entree" -eq 0 ]; then
  printf 'trier-revue: aucun bloc dans %s — rapport vide, rien à trier\n' "$src" >&2
  exit 1
fi
if [ "$fails" -gt 0 ]; then
  printf 'trier-revue: %d bloc(s) rejeté(s) sur %d.\n' "$fails" "$entree" >&2
  exit 1
fi

# Lignes vides de fin retirées, puis une seule réémise après le bloc. L'espacement de la
# sortie ne dépend ainsi plus de celui de l'entrée — un retrait d'intitulé de pile laisse
# la sienne derrière lui, et elle s'accumulerait à chaque passe.
corps() {
  awk '{ l[NR] = $0 }
       END { n = NR
             while (n > 0 && l[n] ~ /^[[:space:]]*$/) n--
             for (i = 1; i <= n; i++) print l[i] }' "$1"
}

if [ -s "$tmp/preambule" ]; then
  p=$(corps "$tmp/preambule")
  [ -n "$p" ] && printf '%s\n\n' "$p"
fi

sortie=0
piles=0
precedent=-1
while IFS=$'\t' read -r o d f; do
  if [ "$o" -ne "$precedent" ]; then
    printf '# %s\n\n' "${LIBELLES[$o]}"
    piles=$((piles + 1))
    precedent="$o"
  fi
  corps "$f"
  printf '\n'
  sortie=$((sortie + 1))
done < <(sort -t$'\t' -k1,1n -k2,2 -k3,3 "$tmp/index")

# Le contrôle qui justifie le script. Sans lui, un bloc perdu en route ressemble à un
# bloc qui n'a jamais existé.
if [ "$sortie" -ne "$entree" ]; then
  printf 'trier-revue: %d blocs en entrée, %d en sortie — tri incomplet.\n' "$entree" "$sortie" >&2
  exit 1
fi

# Un intitulé de pile par catégorie effectivement présente, pas un de plus. Compter les
# blocs ne suffit pas : la duplication des intitulés les laissait tous intacts.
attendu=$(cut -f1 "$tmp/index" | sort -u | wc -l)
if [ "$piles" -ne "$attendu" ]; then
  printf 'trier-revue: %d intitulés de pile pour %d catégories — sortie corrompue.\n' \
    "$piles" "$attendu" >&2
  exit 1
fi
