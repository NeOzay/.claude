---
slug: semences-de-listes
titre: Amorcer les répertoires-listes dans un projet neuf
statut: validé
execution: direct
créé: 2026-08-30
---

## Intention

**Symptôme** : « un problème survient quand c'est utilisé dans un projet qui ne possède pas encore
les listes » (dit). Les trois registres de dette n'existent que dans ce dépôt-ci ; ailleurs,
l'Étape 0 de `debt-review` rend trois `ÉCHEC` et aucune étape ne dit quoi faire ensuite
(dépôt: skills/debt-review/SKILL.md, Étape 0).

**But** : « un répertoire dédié aux définitions de listes que lui et les autres skills pourront
utiliser comme référence, une structure précise qu'attend la skill list-dir pour trouver et
initialiser une nouvelle liste » (dit).

## Critères de réussite

- amorcer une liste par le nom de sa définition produit une liste dont `list-dir validate` sort 0
- les trois registres s'amorcent dans un projet vide, puis `list-dir validate` passe sur les trois
- `list-dir derive` fonctionne après amorçage : `templates/review.{toml,md}` ont suivi
- une définition posée dans `<projet>/.claude/list-dir/<nom>/` s'amorce sans qu'aucun skill la porte
- `list-dir init` sans définition nommée produit le squelette actuel, inchangé
- deux définitions **de même rang** portant le même nom font sortir la commande non nul, en les
  nommant toutes les deux
- `grep -ril 'dette\|debt' skills/list-dir/` ne rend toujours aucune sortie
  (dépôt: skills/implementation-tracker/references/contrat.md, section Dépendances)

## Hors-périmètre

- pas de changement aux contrats eux-mêmes : les semences sont la copie de l'existant
- **aucune commande existante** de `list-dir` autre que `init` n'est modifiée. Une commande *neuve*
  qui imprimerait le contrat en vigueur reste ouverte — voir les incertitudes
- **les plugins** (`~/.claude/plugins/cache/…/skills/`) ne forment pas un rang : aucun plugin
  installé ne porte de skill, et un rang qu'on ne peut pas tester s'écrit à l'aveugle
  (dépôt: plugins/installed_plugins.json — `rust-analyzer-lsp` seul, sans skill)

## Signaux de dérive

- si `list-dir` se met à connaître le mot « dette », c'est raté — le test grep de `contrat.md` le
  dit avant nous
- si `list-dir` tient un **registre** des définitions au lieu de les découvrir par l'arborescence,
  c'est raté : « un registre se désynchronise, une arborescence non »
  (dépôt: skills/list-dir/scripts/listdir/loader.py, en-tête)
- si l'amorçage devient un mécanisme de gabarit générique — héritage, surcharge, fusion de
  contrats — c'est un autre chantier : il copie une définition, il n'en compose pas
- si une documentation décrit un contrat que l'outil n'applique pas, c'est raté : la doc renvoie à
  la liste en vigueur, jamais à la semence qui l'a créée
- si l'amorçage crée des entrées, c'est raté : une liste neuve est vide, et `store.py:650` le dit
  déjà — « Une liste vide est légitime »

## Contraintes connues de l'utilisateur

- **La convention se nomme `list-dir/`**, pas `dir-list/` — lapsus corrigé (dit). Elle se documente
  dans `list-dir`, qui décrit une *forme* sans nommer aucun consommateur.
- **Une définition ne vit pas forcément dans un skill** (arbitrage). Quatre rangs, du plus
  spécifique au plus général — la spécificité prime, comme une commande de `.list/commands/` prime
  sur une générique :

  | # | Racine | Découverte |
  |---|---|---|
  | 1 | `<projet>/.claude/list-dir/<nom>/` | remontée depuis `cwd` jusqu'au premier `.claude/` |
  | 2 | `<projet>/.claude/skills/*/list-dir/<nom>/` | idem |
  | 3 | `~/.claude/list-dir/<nom>/` | `Path(which("list-dir")).resolve().parents[3]` |
  | 4 | `~/.claude/skills/*/list-dir/<nom>/` | `…parents[2]` — **les trois semences de dette y vont** |

- **Aucune constante, aucune variable d'environnement, aucune dépendance externe** pour trouver ces
  racines : `which` localise le paquet, la remontée trouve le projet. Vérifié — le lien
  `bin/list-dir` rend bien `parents[2] == ~/.claude/skills` (dépôt: bin/list-dir).
- **Déduplication sur chemin résolu** : ce dépôt *est* `~/.claude` **et** contient `~/.claude/.claude/`.
  Les rangs 1 et 3 y sont vivants et distincts ; une même racine atteinte par deux calculs ne doit
  pas se dénoncer comme ambiguë.
- **Mécanisme** : étendre `list-dir init`, plutôt qu'une commande `seed` neuve ou un `cp` documenté
  (arbitrage).
- **À réécrire** : `store.py:652-657` affirme que le squelette « ne peut pas venir d'un gabarit :
  un gabarit vit dans `.list/templates/` d'une liste existante, et `init` s'adresse précisément au
  cas où aucune liste n'existe encore ». Les rangs lèvent cette impossibilité — la note doit dire
  le nouveau partage (dépôt: skills/list-dir/scripts/listdir/store.py).
- **La semence fait autorité le temps de l'`init`, et pas une seconde de plus.** Toute commande
  travaillant sur une liste lit `<liste>/.list/contract.toml`, jamais une définition
  (dépôt: skills/list-dir/scripts/listdir/contract.py, `contract_path`). Une liste amorcée est donc
  **détachée** : la semence peut évoluer sans elle, et `migrate` ne la rattrapera pas — il remet les
  éléments au contrat *de la liste*. Aucun chemin de re-semis, et c'est voulu : un projet qui
  redéfinit sa liste au rang 1 a délibérément pris la main.
- **La duplication contrat / prose est dans le périmètre** (arbitrage) : `dette.md` recopie en
  tableaux les champs et sections du contrat ; les remplacer par un renvoi vers **une commande qui
  lit le contrat en vigueur**, jamais vers le fichier de semence du skill — un projet ayant
  redéfini sa liste lirait sinon une doc décrivant autre chose que ce que l'outil applique.
  La prose qui dit un *pourquoi* absent du contrat reste — l'`id` clé de dédoublonnage,
  « désigner sans numéro de ligne », « une entrée sans Pour solder est un regret ».

## Incertitudes à lever en plan

- **par quelle commande `dette.md` renvoie au contrat en vigueur** : `show` rend un élément,
  `validate` confronte, mais rien n'imprime le contrat lui-même. Un `list-dir contract <liste>`
  serait ce moyen — à trancher, et il sort du « aucune commande autre que `init` » du hors-périmètre
- le nom de l'option et l'existence d'une commande de découverte : `--from`, `--def`, un
  `list-dir defs` qui dirait ce qui est définissable et d'où. Non tranché
- `debt-review/references/gabarit-rapport.md` recopie lui aussi les sept catégories de
  `templates/review.toml` : même traitement que `dette.md`, ou laissé tel quel ? Non abordé
- la remontée s'arrête au premier `.claude/` trouvé, qui n'est pas nécessairement le bon — cas
  accepté à l'arbitrage, mais le comportement en dépôt imbriqué reste à border
