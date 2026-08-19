# Répertoires-listes — format de données manipulable par script

## État au 2026-08-19 — plan non validé, à reprendre

Le plan a été relu par `plan-reviewer` avant présentation. **Verdict : NON CONFORME.** Il a été
présenté à l'utilisateur, qui a reporté sa décision. Aucun fichier de suivi n'existe : le chantier
n'est pas ouvert, la branche `format-registres` n'est pas créée.

**Déjà fait** — brief figé (`.claude/implementation/format-registres.brief.md`, `statut: validé`) ;
purge des plans obsolètes commitée (`2501a05`) ; ce plan écrit et corrigé de ses défauts de
rédaction.

**Corrigé sans arbitrage après la relecture** — syntaxe TOML invalide dans l'exemple de contrat
(`type = "text"; required = true`) ; compte de conservation qui incluait `todo/README.md` et rendait
25 au lieu de 24 ; vérification de l'étape 2 qui exigeait `help`, livrée plus loin ; garde `[ -d … ]`
qui transformait une liste absente en succès ; chemins manquants sur `dette.md`, `cloture.md`,
`contrat.md` ; vérification de migration reposant sur un jugement humain ; neuf commandes empilées
en deux étapes, redécoupées en huit ; `git commit` + `git reset --hard` retirés du bloc de
vérification ; contexte faux sur le nombre de bugs documentés par `trier-revue.sh` (un, pas deux).

**À trancher avant toute exécution** — trois critères du brief ne sont servis par aucune étape, et
n'ont volontairement pas été comblés d'office :

1. le cas d'usage de référence (revue complète des 17 entrées, `derive` → remplir → `merge`,
   archivée sous `done/revues/`) est renvoyé à la première revue réelle, alors que le brief en fait
   le critère central ;
2. la déclaration des dépendances des commandes et son épreuve par injection ne sont nulle part ;
3. `technical-debt-ecarte/` et la liste de revue ne sont créées par aucune étape — deux des quatre
   listes annoncées manquent à la clôture.

Un quatrième point a été retiré du plan : l'étape qui débranchait `jq` de
`hooks/intent-brief-gate.sh` déclenchait le signal de dérive « si le diff dépasse la réécriture de
`debt-review` et des registres ». C'est un élargissement à ratifier, pas une décision d'exécution.

> **Ce fichier n'est pas versionné et son nom est attribué par le harness.** Le contrat du pipeline
> documente le cas : un plan laissé sous son nom généré a déjà été écrasé par celui d'un autre
> chantier. À la reprise, le committer ou le renommer avant d'ouvrir un second plan.

---

## Contexte

Les registres vivants du pipeline (`.claude/implementation/todo/technical-debt.md` et ses deux
compagnons) sont des listes stockées dans un document unique. Toutes les opérations coûteuses le
sont pour cette raison : solder une entrée, c'est découper 30 lignes de prose d'un fichier et les
recoller dans un autre, sans qu'aucune commande ne signale une perte ; dédoublonner, c'est comparer
des intitulés caractère par caractère ; compter, c'est recompter à la main.

Le coût est mesurable dans le dépôt : `skills/debt-review/scripts/trier-revue.sh` fait 177 lignes
dont l'essentiel découpe des blocs `## ` et les recolle, et son en-tête documente un bug déjà
rencontré — des intitulés de pile qui se dupliquaient à chaque passe (7 → 13 → 19) sans qu'aucun
contrôle ne bronche. C'est un bug de manipulation de texte à la main, imposé par le format.

Le chantier remplace ce modèle par le **répertoire-liste** : un répertoire = une liste, un fichier
= un élément, un contrat embarqué qui déclare la structure, et une interface de commandes commune
portée par un skill déployable dans n'importe quel dépôt. Principe directeur, arrêté au brief :
*les scripts font la structure, le modèle fait le jugement et la correction*.

Brief : `.claude/implementation/format-registres.brief.md`.

---

## Décisions structurantes

Elles lèvent les quatre incertitudes reportées par le brief.

**Un élément = un fichier Markdown à front matter TOML**, délimité par `+++`.

```markdown
+++
id = "filtres-listing-hook-rtk"
title = "Les filtres de listing sont cassés par le hook rtk"
date = 2026-08-14
source = "audit-integre"
refs = ["R4"]
+++

## Constat
…prose inchangée…
```

TOML plutôt qu'un format `clé: valeur` maison **parce que `tomllib` est dans la stdlib** : aucune
ligne de parsing écrite à la main, dates et listes natives, erreurs localisées précisément. C'est
la même raison qui fait tout le chantier — le parsing artisanal est ce qu'on supprime. Contrepartie
assumée : les valeurs texte demandent des guillemets, `validate` le signale immédiatement.

**Le contrat vit dans `.list/contract.toml`**, dans la liste elle-même. Le sous-répertoire `.list/`
tient tout ce qui n'est pas un élément hors de l'espace de noms : **tout `*.md` à la racine d'une
liste est un élément, sans exception**, ce qui rend le contrôle de conservation trivial.

```toml
name = "technical-debt"
description = "Dette technique constatée et non résolue"

[fields.id]
type = "slug"          # toujours obligatoire, toujours égal au nom de fichier

[fields.title]
type = "text"
required = true

[fields.date]
type = "date"
required = true
description = "date du constat, jamais modifiée"

[fields.category]
type = "enum"
required = false
values = ["a-solder", "non-pertinent", "doublon", "pas-une-dette",
          "aggravee", "pertinent", "inverifiable"]

[sections]
required = ["Constat", "Pourquoi c'est gênant", "Pour solder"]
optional = ["Assumé"]
```

**L'état est porté par le répertoire, jamais par un champ** — décision du brief. Les trois registres
de dette deviennent trois listes sœurs avec trois contrats distincts (celui des soldés exige une
section `Soldé le`, celui des écartés une section `Écartée le`).

**`move` est un renommage pur** : `git mv` et rien d'autre, pour que la détection de renommage de
Git tienne. La preuve exécutée qui accompagne un solde s'écrit **dans un second commit**.

**`validate` repasse après toute écriture** — c'est ce qui paie la dispense d'écriture directe
accordée au modèle. Elle est lancée en fin de chaque étape, par `debt-review` avant de rendre la
main, et par `scripts/check-pipeline.sh`.

**`list --where` filtre sur les champs déclarés au contrat, et rien d'autre.** Pas de recherche
plein texte : `grep` la fait déjà mieux.

---

## Les neuf commandes génériques

Point d'entrée unique : `python3 "$HOME/.claude/skills/list-dir/scripts/list-dir.py" <cmd> …`

| Commande | Rôle |
|---|---|
| `help [liste]` | commandes génériques **et** commandes propres à la liste, avec leur description |
| `init <dir>` | crée une liste : `.list/contract.toml` squelette |
| `new <liste> <id>` | crée un élément prérempli des champs et sections du contrat, vides |
| `list <liste> [--where champ=valeur] [--sort champs]` | une ligne par élément |
| `show <liste> <id>` | affiche un élément |
| `validate <liste>` | chaque élément contre le contrat : champs, types, enums, sections, `id` = nom de fichier |
| `move <liste> <id> <liste-cible>` | `git mv` seul, puis rappelle ce que le contrat cible exige |
| `derive <src> <dst> --template <nom>` | crée une liste dérivée, un élément par élément source |
| `merge <liste> [--out <fichier>]` | agglomère en un fichier, ordre déclaré, conservation vérifiée |

**Échec fermé** : sortie ≠ 0 et message nommant la cause — contrat introuvable, champ inconnu passé
à `--where`, élément non conforme, `merge` qui perd un élément en route. Même règle que
`scripts/check-pipeline.sh`.

**Une liste sans élément est valide pour `init` et `validate`** — une liste fraîchement créée est
légitimement vide. Elle est en revanche une erreur pour `merge` et `derive`, qui agglomèrent ou
projettent : agglomérer zéro élément sans broncher se lit comme « rien à traiter », exactement le
mode de défaillance que `trier-revue.sh` refuse déjà.

**Commandes spécifiques** : `.list/commands/<nom>.py`, chacune déclarant un `DESCRIPTION = "…"` au
niveau module et une fonction `main(args)`. `help` lit la description **sans exécuter le fichier**,
via `ast.parse` — stdlib.

---

## Étapes

- [ ] 1. Squelette du skill et contrat de format — `skills/list-dir/SKILL.md`,
  `skills/list-dir/references/contrat-liste.md` — vérif: `bash scripts/check-pipeline.sh`
- [ ] 2. Noyau Python : front matter TOML, chargement du contrat, résolution de liste —
  `skills/list-dir/scripts/list-dir.py` — vérif: `python3 …/list-dir.py` sans argument → code 2 et
  usage sur stderr ; `… show` sur une liste sans contrat → code ≠ 0 nommant `.list/contract.toml`
- [ ] 3. `init`, `new`, `show` — même fichier — vérif: `init` puis `new` sur une liste jetable du
  scratchpad, `show` rend le fichier créé, champs et sections du contrat présents et vides
- [ ] 4. `validate` : champs obligatoires, types, enums, sections, `id` = nom de fichier — même
  fichier — vérif: vert sur la liste jetable, puis un champ obligatoire retiré → code ≠ 0 nommant
  le champ et le fichier ; une valeur hors enum → code ≠ 0
- [ ] 5. `list --where --sort` — même fichier — vérif: `--where` sur un champ déclaré filtre,
  `--where` sur un champ inconnu → code ≠ 0 nommant le champ
- [ ] 6. `move` — même fichier — vérif: après `move` d'un élément entre deux listes jetables,
  `git status --short` montre `R  <ancien> -> <nouveau>` ; l'élément n'est pas modifié
- [ ] 7. `derive` et `merge` — même fichier — vérif: `derive` d'une liste de 3 rend 3 éléments,
  `merge` en rend 3 ; un élément retiré entre les deux → code ≠ 0
- [ ] 8. `help`, lecture des `DESCRIPTION` par `ast.parse` — même fichier — vérif: `help` liste les
  9 commandes ; `help <liste>` y ajoute une commande spécifique posée dans `.list/commands/`
- [ ] 9. Migration des 24 entrées par un script de migration jetable (`scripts/migrate-dette.py`,
  supprimé à l'étape suivante) vers `todo/technical-debt/` et `todo/technical-debt-solde/` —
  vérif: 24 éléments, `validate` vert sur les deux listes, et chaque **Constat** migré retrouvé à
  l'identique dans le `.md` d'origine (`grep -Fq`), sortie « 24/24 »
- [ ] 10. Retrait des anciens `.md` et du script de migration ; réécriture de
  `skills/implementation-tracker/references/dette.md` et de
  `.claude/implementation/todo/README.md` — vérif: `bash scripts/check-pipeline.sh`
- [ ] 11. Refonte de `debt-review` sur `derive` → remplir → `merge`, suppression de
  `skills/debt-review/scripts/trier-revue.sh` — vérif: `git ls-files skills/debt-review` ne
  contient plus `trier-revue.sh`
- [ ] 12. `skills/implementation-tracker/references/cloture.md` et
  `skills/implementation-tracker/references/contrat.md` : arborescence, écriture au registre,
  section *Dépendances* — vérif: `bash scripts/check-pipeline.sh`
- [ ] 13. Garde-fou : contrôle 6 étendu aux appels `python3` — vérif:
  `bash scripts/check-pipeline.sh` vert, puis injection d'un appel `python3` relatif non gardé dans
  un `.md` de `skills/` → contrôle 6 rouge, injection retirée
- [ ] 14. Passe de vérification d'ensemble — vérif: section *Vérification* ci-dessous, intégralement

---

## Ce qui n'est pas fait

Repris du brief : la vue Neovim de la liste (sujet à part), `road-map.md` (inexistante), et les
autres fichiers du pipeline — briefs, suivis, rapports d'audit — qui restent des documents.

**Trois critères du brief ne sont servis par aucune étape** — ils appellent ton arbitrage, ils ne
sont pas comblés d'office :

1. le cas d'usage de référence (une revue complète des 17 entrées, `derive` → remplir → `merge`,
   archivée sous `done/revues/`) est renvoyé à la première revue réelle ;
2. la déclaration des dépendances des commandes et son épreuve par injection ne sont nulle part ;
3. `technical-debt-ecarte/` et la liste de revue ne sont créées par aucune étape — seules deux des
   quatre listes annoncées au brief existent à la clôture.

`hooks/intent-brief-gate.sh` n'est plus touché : le brief ne le cite que comme précédent, et le
signal de dérive « si le diff dépasse la réécriture de `debt-review` et des registres » se
déclenchait.

## Vérification

```bash
L="$HOME/.claude/skills/list-dir/scripts/list-dir.py"
T=.claude/implementation/todo

# 1. Le garde-fou du pipeline
bash scripts/check-pipeline.sh                                   # → Pipeline conforme.

# 2. Les listes valident, sans garde qui transforme une absence en succès
for l in technical-debt technical-debt-solde; do
  python3 "$L" validate "$T/$l" || echo "ÉCHEC : $l"
done

# 3. Conservation : 24 éléments migrés, aucun perdu
find "$T" -mindepth 2 -maxdepth 2 -name '*.md' -not -path '*/.list/*' | wc -l   # → 24

# 4. Le skill générique ne connaît aucun consommateur
grep -ril 'dette\|debt' skills/list-dir/ ; echo "attendu : aucune sortie"

# 5. Stdlib seule
grep -rhn '^[[:space:]]*\(import\|from\) ' skills/list-dir/scripts/ | sort -u

# 6. Traçabilité d'un déplacement, éprouvée sur un élément déjà commité par l'étape 10,
#    sans créer ni détruire aucun commit
id=$(python3 "$L" list "$T/technical-debt" --sort date | head -1 | cut -d' ' -f1)
python3 "$L" move "$T/technical-debt" "$id" "$T/technical-debt-solde"
git status --short          # → R  …/technical-debt/$id.md -> …/technical-debt-solde/$id.md
python3 "$L" move "$T/technical-debt-solde" "$id" "$T/technical-debt"
git status --short          # → vide : l'aller-retour ne laisse rien
```
