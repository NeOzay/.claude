# Définitions de listes

`init` seul rend un squelette : un `id`, un `title`, une section. C'est assez pour commencer une
liste à la main, et pas assez pour recréer une liste dont le contrat est connu
([Le contrat](../references/format.md#le-contrat)). Une **définition** comble ce trou.

Une définition est un répertoire dont le contenu **est** ce qui va dans le futur `.list/` — le
contrat et ses gabarits, rien d'autre. Une liste semée y ajoute ensuite ce qui ne vient pas d'une
définition : ses commandes, sa semence gardée, sa sauvegarde.

```
list-dir/
└── recettes/            le nom de la définition
    ├── contract.toml          obligatoire — sans lui, ce n'est pas une définition
    └── templates/             facultatif, copié tel quel s'il existe
        ├── review.toml
        └── review.md
```

```bash
list-dir defs                                # ce qui est définissable, et d'où
list-dir init <cible> --def recettes         # résolu par son nom, dans les racines
list-dir init <cible> --from <chemin>        # ou pris à un chemin, tel quel
```

**Pourquoi une définition peut ce qu'un gabarit ne pouvait pas** : un gabarit vit dans le
`.list/templates/` d'une liste *existante*, et `init` s'adresse justement au cas où aucune liste
n'existe. Une définition vit hors de tout répertoire-liste — c'est exactement ce qui la rend
disponible quand il n'y a encore rien.

---

## Les quatre racines

Un nom est cherché dans quatre racines, du plus spécifique au plus général :

| # | Racine | Ancrage |
|---|---|---|
| 1 | `<projet>/.claude/list-dir/<nom>/` | le premier répertoire **contenant** un `.claude`, en remontant depuis le répertoire courant |
| 2 | `<projet>/.claude/skills/*/list-dir/<nom>/` | idem |
| 3 | `<config>/list-dir/<nom>/` | le premier répertoire **nommé** `.claude`, en remontant depuis le paquet |
| 4 | `<config>/skills/*/list-dir/<nom>/` | idem |

**Les deux ancrages ne cherchent pas la même chose**, et les confondre casse le cas où une
configuration porte son propre projet : un projet *contient* un `.claude`, une configuration *est*
un `.claude`. Une règle unique ferait viser le même répertoire aux deux, et l'un des deux couples
de racines serait faux.

Aucune constante de chemin, aucune variable d'environnement : les deux ancrages sont des remontées.
`defs` imprime celui qu'il a retenu — la remontée s'arrête au **premier** `.claude` trouvé, qui
n'est pas toujours celui qu'on avait en tête, et le voir vaut mieux que le deviner.

**N'avoir aucune racine est un état légitime**, pas une erreur : hors de tout `.claude`, `defs` ne
liste rien et `--def` échoue en le disant.

## Qui gagne

**La spécificité prime, et masquer est le comportement voulu** : une définition de rang 1 l'emporte
sur son homonyme de rang 4, exactement comme une commande de `.list/commands/` l'emporte sur une
générique. C'est ainsi qu'un projet reprend la main sur une définition de sa configuration. `defs`
montre la masquée plutôt que de la taire.

**L'ambiguïté ne se déclare qu'à rang égal** : deux skills qui définissent le même nom font sortir
la commande non nulle, en les nommant tous les deux. Choisir en silence ferait dépendre le contrat
d'une liste de l'ordre de parcours d'un répertoire : deux machines rendraient deux contrats, et
rien ne dirait pourquoi.

Un répertoire sans `contract.toml` n'est pas une définition à moitié faite : ce n'en est pas une, et
`defs` ne le propose pas. L'annoncer pour échouer ensuite sur un fichier manquant serait pire que
de l'ignorer.

## La définition n'est autorité que le temps de l'`init`

C'est la règle dont tout le reste découle. Une liste amorcée porte **sa propre copie** du contrat,
et `contract_path` la lit toujours depuis `<liste>/.list/contract.toml` — jamais depuis une
définition. `list-dir contract <liste>` imprime cette copie, c'est-à-dire la règle réellement
appliquée.

**Rien ne resynchronise une liste avec sa définition de lui-même.** La définition peut évoluer,
`migrate` ne la rattrapera pas : il remet les éléments au contrat *de la liste*. Un projet qui
redéfinit sa liste au rang 1 a délibérément pris la main, et rien ne la lui retire.

Ce qui a changé depuis, c'est que la filiation est **dite** au lieu d'être supposée : la liste
porte le nom de sa définition et la version à laquelle elle a été semée, `validate` avertit quand
la définition a bougé depuis, et `reseed` rattrape **sur ordre**. L'autorité, elle, n'a pas bougé
d'un pouce : c'est toujours la copie qui s'applique, et rien ne l'écrase sans qu'on l'ait demandé.

C'est pourquoi une prose ne renvoie jamais au **fichier** d'une définition pour dire ce qui
s'applique : elle décrirait autre chose que ce que l'outil applique, et d'autant plus faux que le
projet a justement redéfini sa liste. Un renvoi vers `list-dir contract` ne peut pas mentir — il
rend ce que la commande rendrait.

## Ce que `contract` vise, et ce que ça engage

`contract` accepte les deux cibles d'`init`, et la différence n'est pas cosmétique :

| Forme | Ce qui est imprimé | Ce que ça vaut |
|---|---|---|
| `contract <liste>` | `<liste>/.list/contract.toml` | la règle **réellement appliquée** |
| `contract --def <nom>` | `<définition>/contract.toml` | une **semence**, appliquée à rien |
| `contract --from <chemin>` | idem, sans passer par les rangs | idem |

`--template <nom>` vise le `<nom>.toml` de `templates/` au lieu du contrat, dans les trois cas.

**Une prose doit dire laquelle des deux elle décrit.** Renvoyer à une définition alors qu'une
liste existe et a divergé décrit ce qui *aurait été* semé, pas ce qui s'applique — c'est le mode de
défaillance ci-dessus, déplacé d'un cran. Le renvoi à une définition se justifie quand la liste
**n'existe pas encore** au moment de la lecture : une liste engendrée par `derive` n'a de contrat
qu'après coup, et son gabarit source est le seul fichier déjà là.

`--values <champ>` rend les valeurs déclarées d'un champ, une par ligne et **dans l'ordre du
fichier**. Il extrait : rien n'est trié, filtré ni jugé. Un champ inconnu ou sans `values` est un
échec nommé, jamais une sortie vide sous un code 0.

**Le code de retour est à l'appelant, et il n'est pas facultatif.** `for c in $(list-dir contract …
--values category)` avale l'échec : la substitution rend une chaîne vide, la boucle itère zéro fois
et le bloc réussit. Affecter, tester, puis lire ligne à ligne :

```bash
if ! VALEURS=$(list-dir contract "$L" --values category); then
  echo "ÉCHEC : contrat illisible"; false
else
  printf '%s\n' "$VALEURS" | while read -r v; do …; done
fi
```

Le `while read` plutôt qu'un `for` sur la variable : zsh ne découpe pas une variable en mots, et la
boucle y tournerait une seule fois sur la chaîne entière.
