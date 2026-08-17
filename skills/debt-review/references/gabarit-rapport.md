# Gabarit du rapport de revue

Fichier : `.claude/implementation/done/revues/<AAAA-MM-DD>-revue.md`, écrit **directement à sa place
définitive** — pas de fichier de travail à déplacer ensuite, donc pas d'archivage à oublier. Le
sous-répertoire le tient hors de portée de `impl-list.sh`, qui ne descend qu'à un niveau.

Le modèle **étiquette**, le script **regroupe** : ce fichier définit la seule chose que les deux
doivent respecter à l'identique, la ligne d'en-tête d'un bloc.

---

## Le préambule

En tête du fichier, avant le premier bloc : la date de la revue, le registre relu, et le **compte**
des entrées instruites face au compte du registre.

```markdown
# Revue du registre — 2026-08-17

Registre : `.claude/implementation/todo/technical-debt.md`
**Entrées au registre : 14 — blocs instruits : 14.**
```

**Le tri conserve le préambule et ne le redécoupe pas** : c'est le seul endroit du rapport où écrire
quelque chose qui n'est pas un bloc. Un rapport archivé porte ainsi lui-même la preuve qu'aucune
entrée n'a été omise.

> *Mode de défaillance* — **`## ` est réservé aux en-têtes de bloc**, partout dans le fichier. C'est
> le séparateur du script, pas un niveau de titre : un `## Comptes` ou un `## ` de pile vide part au
> découpage et fait échouer le tri en « en-tête mal formé », message qui n'explique pas ce qui gêne.
> Les titres du préambule s'écrivent en `#`.

## La ligne d'en-tête

```markdown
## <catégorie> | <AAAA-MM-DD> | <intitulé exact de l'entrée>
```

Trois champs séparés par ` | `, dans cet ordre, sur une seule ligne.

- **catégorie** — un des sept identifiants ci-dessous, en ASCII kebab-case.
- **date** — celle de l'entrée dans le registre, **pas** celle de la revue. C'est elle qui ordonne
  chaque pile.
- **intitulé** — recopié **caractère pour caractère** depuis le registre, marqueur de catégorie
  exclu s'il y en a déjà un. C'est la clé qui rattache le bloc à son entrée
  (`../../implementation-tracker/references/dette.md`, « Gabarit d'entrée »).

| Identifiant | Pile rendue par le script |
|---|---|
| `a-solder` | À solder |
| `non-pertinent` | Non pertinent |
| `doublon` | Doublon |
| `pas-une-dette` | Pas une dette |
| `aggravee` | Aggravée |
| `pertinent` | Pertinent |
| `inverifiable` | Invérifiable en revue |

> *Mode de défaillance* — les identifiants sont en ASCII parce qu'ils sont comparés par le script.
> Un libellé accentué se serait cassé au premier fichier réencodé, sans qu'une commande n'échoue :
> le bloc serait tombé dans « catégorie inconnue » et le script se serait arrêté — visible, mais
> pour la mauvaise raison. Les libellés accentués n'apparaissent que dans la sortie, où rien ne les
> compare.

L'ordre des piles est celui du tableau : ce qui **sort** du registre d'abord, ce qui y **reste**
ensuite. Il est fixé dans le script, pas ici — le rapport brut peut mêler les catégories.

## Le corps d'un bloc

```markdown
## non-pertinent | 2025-04-23 | Le module `legacy/xmlrpc.py` n'a aucun test

**Vérifié par** — `ls orders/legacy/xmlrpc.py` → `No such file or directory`, code de sortie 2.

**Verdict** — l'élément cité n'existe plus : le module a été supprimé, pas testé. Rien n'a été
réparé, d'où `non-pertinent` et non `a-solder`.

**Action** — écarter vers `technical-debt-ecarte.md`, motif `non pertinent`.
```

> *Mode de défaillance* — **cet exemple est fictif, et doit le rester.** Bâti sur une vraie entrée
> du registre, il livrerait un verdict tout fait sur une dette que le relecteur va rencontrer :
> celui-ci recopie l'exemple au lieu d'exécuter sa commande, et écarte une dette vivante sur une
> preuve périmée. Le dépôt d'exemple — un service de commandes en Python — n'existe pas, et aucun
> intitulé de `technical-debt.md` ne doit apparaître dans ce répertoire.

**`Vérifié par` porte une commande lancée et sa sortie réelle.** C'est la règle du solde
(`../../implementation-tracker/references/dette.md`, « Solder »), étendue ici à toute sortie du
registre : sans preuve exécutée, l'entrée
ne sort pas et le bloc se classe `pertinent`.

Deux catégories en sont dispensées, et seulement elles :

- `inverifiable` — par définition, il n'y a rien à exécuter ; le bloc dit pourquoi ;
- `doublon` — la preuve est l'intitulé de l'entrée conservée, qui doit être cité dans `Verdict`.

## Ce que le rapport n'est pas

Ce n'est **pas** un journal : un rapport par revue, archivé tel quel, jamais appendu. Le journal
des soldes vit dans `technical-debt-solde.md`, celui des sorties sèches dans
`technical-debt-ecarte.md`.

Ce n'est **pas** une décision : le rapport trié est présenté, l'utilisateur tranche, l'écriture
suit. Un rapport archivé sans arbitrage écrit à côté est un rapport qui n'a servi à rien.
