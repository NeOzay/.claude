# Plan — `debt-review`, revue de pertinence du registre de dette

Brief : `.claude/implementation/revue-dette.brief.md` (slug `revue-dette`, `execution: direct`).

## Contexte

Le pipeline sait **alimenter** le registre de dette — l'orchestrateur y verse à la clôture ce que
le chantier laisse derrière lui (`references/dette.md`, « Alimenter ») — mais rien ne sait le
**relire**. `dette.md:155` l'acte : « Le pipeline n'ouvre jamais le registre de lui-même […] Il
l'alimente, l'utilisateur le consulte. »

La conséquence est visible dans le dépôt : `todo/technical-debt.md` porte 14 entrées, dont 13
datées du `2026-08-14`, et sa ligne de tête annonce `Dernière vérification : 2026-08-16` — une
date posée par le dernier chantier qui y a **écrit**, sans qu'aucune entrée n'ait été confrontée au
code. `dette.md:70-72` décrit pourtant déjà le geste manquant : cette ligne « s'actualise […] à
chaque fois qu'on relit le registre entrée par entrée pour vérifier qu'il tient encore ». Personne
ne le fait, et un registre qu'on soupçonne périmé ne se lit plus.

Ce chantier crée le skill manuel qui fait cette relecture : il instruit un verdict par entrée, le
fait arbitrer, puis met les registres à jour. **Il ne corrige aucun code** — tout correctif passe
par `implementation-tracker`.

## Décisions arrêtées

| Point | Décision |
|---|---|
| Nom du skill | `debt-review` — aligné sur `implementation-tracker`, `intent-brief`, `git-smart-commit` |
| Entrées écartées | un seul `todo/technical-debt-ecarte.md`, chaque entrée portant son motif |
| Rapport archivé | `done/revues/<AAAA-MM-DD>-revue.md` — sous-répertoire invisible pour `impl-list.sh` (`-maxdepth 1`), donc contrôles 3 et 5 du garde-fou inchangés |
| Répartition | le modèle **étiquette**, le script **regroupe** — le tri par catégorie puis par date est mécanique |

## Les sept catégories

Ordre de tri : ce qui **sort** du registre d'abord, ce qui y **reste** ensuite.

| # | Catégorie | Constat | Destination |
|---|---|---|---|
| 1 | `à solder` | la dette a été payée dans un autre chantier | `technical-debt-solde.md`, avec la commande et sa sortie |
| 2 | `non pertinent` | les éléments cités n'existent plus | `technical-debt-ecarte.md` |
| 3 | `doublon` | une autre entrée dit la même chose | `technical-debt-ecarte.md`, l'entrée conservée nommée |
| 4 | `pas une dette` | idée d'amélioration ou préférence de style — exclues par `dette.md:47-50` | `technical-debt-ecarte.md` |
| 5 | `aggravée` | toujours vraie, mais pire qu'à l'origine | reste, **Constat** réécrit et redaté, ` (aggravée)` suffixé à l'intitulé |
| 6 | `pertinent` | la dette est identifiable dans le code | reste inchangée |
| 7 | `invérifiable en revue` | l'entrée porte un fait historique, pas un état du code | reste, marquée pour ne pas être réinstruite chaque fois |

Les catégories 1 à 4 exigent une **preuve d'exécution** — commande lancée et sortie réelle. C'est
la règle déjà posée pour le solde (`dette.md:144`), étendue à toute sortie du registre : sans
preuve, l'entrée reste et bascule en `pertinent`.

## Étapes

- [ ] 1. Gabarit du rapport et échantillon — `skills/debt-review/references/gabarit-rapport.md`, `skills/debt-review/references/exemple-revue.md` — vérif: `grep -c '^## ' skills/debt-review/references/exemple-revue.md` → 7, et `grep -c '^## .* | 20' skills/debt-review/references/exemple-revue.md` → 7 (chaque bloc porte bien ses trois champs)
- [ ] 2. Script de tri — `skills/debt-review/scripts/trier-revue.sh` — vérif: `bash skills/debt-review/scripts/trier-revue.sh skills/debt-review/references/exemple-revue.md | grep -c '^# '` → 7 piles dans l'ordre du tableau, et `| grep -c '^## '` → 7 (conservation)
- [ ] 3. Référence des catégories — `skills/debt-review/references/categories.md` — vérif: `grep -c '^## ' skills/debt-review/references/categories.md` → 7
- [ ] 4. Corps du skill — `skills/debt-review/SKILL.md` — vérif: `bash scripts/check-pipeline.sh` (contrôle 6 : l'appel du script de tri doit être en `$HOME/…`)
- [ ] 5. Arborescence du contrat — `skills/implementation-tracker/references/contrat.md` — vérif: `bash scripts/check-pipeline.sh` (contrôles 1 et 2 : aucune ancre morte, aucune empreinte dupliquée)
- [ ] 6. Amendements du registre — `skills/implementation-tracker/references/dette.md`, `.claude/implementation/todo/README.md` — vérif: `bash scripts/check-pipeline.sh`
- [ ] 7. Passe réelle sur les 14 entrées — `.claude/implementation/todo/*.md` — vérif: somme des `grep -c '^## '` sur `technical-debt.md`, `technical-debt-solde.md` et `technical-debt-ecarte.md` → **20** (14 + 6 soldés existants), et `grep -n 'Dernière vérification' technical-debt.md` porte la sortie de `date +%F`

### Étapes 1 et 2 — le format, puis le script

Le script est **la raison d'être du découpage** : le modèle étiquette entrée par entrée, le
regroupement par catégorie puis par date est une manipulation mécanique qu'il fait mal. Le gabarit
vient donc avant lui — c'est le format qu'il consomme — accompagné d'un `exemple-revue.md` à sept
blocs, catégories et dates mêlées, qui sert de jeu de test permanent au script.

Entrée : le rapport brut, un bloc par entrée du registre, en-tête à trois champs séparés par `|` :

```markdown
## <catégorie> | <AAAA-MM-DD de l'entrée> | <intitulé de l'entrée>
```

Sortie : les mêmes blocs, regroupés sous un titre `# <catégorie>` par pile, dans l'ordre du tableau
ci-dessus, dates croissantes à l'intérieur de chaque pile.

Trois règles reprises de `impl-list.sh` (`skills/implementation-tracker/scripts/impl-list.sh`),
qui sert de modèle de rédaction — en-tête commentée disant la portée et le *pourquoi un script* :

- **échec fermé** sur catégorie inconnue ou en-tête mal formé, comme `check-pipeline.sh` ;
- **un contrôle qui n'examine rien échoue** : zéro bloc en entrée → erreur, pas succès ;
- **conservation** : le nombre de blocs en sortie doit égaler celui en entrée, sinon erreur.

### Étape 4 — le corps du skill

Frontmatter calqué sur `implementation-tracker/SKILL.md:1-10` : `disable-model-invocation: true`,
`argument-hint` pour un chemin de registre optionnel.

Déroulé : prérequis (`date +%F`, arbre propre) → lecture du registre entrée par entrée →
instruction d'un verdict avec sa preuve → écriture du rapport brut → tri par le script → **restitution
et arbitrage** → mise à jour des trois registres → archivage du rapport en `done/revues/`.

L'appel du script se fait par chemin absolu ancré dans la skill —
`bash "$HOME/.claude/skills/debt-review/scripts/trier-revue.sh"` — sans quoi le contrôle 6 de
`check-pipeline.sh` échoue, et le script serait silencieusement inopérant hors de `~/.claude`
(`contrat.md:183-196`).

**Arbitrage obligatoire avant écriture.** Le skill ne solde ni n'écarte de sa propre autorité : le
rapport trié est présenté, l'utilisateur tranche, l'écriture suit. C'est la même règle que
« l'orchestrateur écrit, jamais l'auditeur » (`dette.md:26-28`), appliquée à l'utilisateur.

### Étape 5 — le contrat

**Aucune section nouvelle** dans `contrat.md` : le contrôle 1 du garde-fou exige que chaque section
soit citée au moins une fois depuis `skills/`, et le contrôle 2 refuse toute formulation recopiée.
Seul le bloc d'arborescence de la section existante *Arborescence et nommage* s'étend :

```
  done/
    revues/
      <AAAA-MM-DD>-revue.md      # rapports de revue du registre, archivés
  todo/
    technical-debt-ecarte.md     # sorti du registre sans avoir été payé
```

### Étape 6 — les amendements

Dans `dette.md` :

- section **Écarter**, symétrique de la section *Solder* existante (`dette.md:130-149`) : destination,
  champ `**Écartée le <date> — <motif>**`, et la même exigence de preuve exécutée ;
- section *Lecture* (`dette.md:153-157`) : le « Le pipeline n'ouvre jamais le registre de lui-même »
  reste vrai des skills du chantier, mais `debt-review` est désormais l'exception explicite ;
- point 3 d'*Alimenter* (`dette.md:119`), qui dédoublonne sur l'intitulé : **comparer en ignorant le
  suffixe ` (aggravée)`**. Sans cette ligne, une entrée marquée aggravée cesse d'être reconnue par
  la clôture suivante, qui reverserait le même constat en doublon — l'intitulé est la clé de
  référence d'une entrée (`dette.md:76-78`).

Dans `todo/README.md` : `technical-debt-ecarte.md` prend sa place dans la liste des registres
(lignes 10-13, à la suite de `technical-debt-solde.md`) ; la phrase « Rien ici n'est lu
automatiquement par le pipeline » (ligne 18) gagne son exception.

### Étape 7 — la passe réelle

C'est le critère de réussite du brief : le dispositif n'est établi que par un passage sur les 14
entrées réelles. Elle modifiera les trois registres — écriture attendue, pas un effet de bord, et
l'arbitrage reste à l'utilisateur entrée par entrée.

Deux entrées sont déjà identifiées comme `invérifiable en revue` au cadrage (`technical-debt.md:69`
et `:280`, toutes deux « n'a jamais été audité ») : si la passe les classe autrement, c'est le
critère de la catégorie qui est mal écrit.

## Vérification d'ensemble

```bash
bash scripts/check-pipeline.sh                                   # 6 contrôles, sortie 0
bash "$HOME/.claude/skills/implementation-tracker/scripts/impl-list.sh" \
     .claude/implementation/done                                  # done/revues/ invisible
grep -n 'Dernière vérification' .claude/implementation/todo/technical-debt.md
```

Somme conservée : `grep -c '^## '` sur `technical-debt.md` + `-solde.md` + `-ecarte.md` après la
passe = 14 + 6 (soldés existants) — aucune entrée perdue en chemin.

## Hors-périmètre (du brief)

- aucun code corrigé, même trivial : tout correctif passe par `implementation-tracker` ;
- pas d'invocation automatique du skill ;
- pas de dette inventée : le skill statue sur l'existant ;
- `road-map.md`, annoncé par `dette.md:48` et `todo/README.md:15`, n'est **pas** créé ici.
