---
name: debt-review
description: >
  Relit le registre de dette technique entrée par entrée et le confronte au dépôt : une liste de
  revue est dérivée du registre, le modèle instruit chaque fiche par une commande exécutée,
  l'utilisateur arbitre, puis les entrées sont déplacées et le rapport aggloméré archivé. Skill
  exclusivement manuelle : elle s'invoque uniquement via /debt-review. Ne corrige aucun code.
disable-model-invocation: true
argument-hint: "[@chemin/vers/technical-debt]"
---

# Debt Review

Le pipeline sait **alimenter** le registre de dette — l'orchestrateur y verse à la clôture ce qu'un
chantier laisse derrière lui — mais rien ne savait le **relire**. Une entrée soldée par un autre
chantier y reste, un constat devenu sans objet y reste, et un registre qu'on soupçonne périmé ne se
lit plus.

Ce skill est cette relecture, et rien d'autre : **il instruit, il ne répare pas.**

Le registre est un **répertoire-liste** (`../implementation-tracker/references/dette.md`), et la
revue en est une seconde : `derive` engendre une fiche par entrée, le modèle les remplit, `merge`
les agglomère en rapport. Ce partage est le principe du dispositif — **les scripts font la
structure, le modèle fait le jugement**. Ni le découpage, ni le tri, ni le comptage ne sont écrits
ici.

---

## Les trois règles

**1. Le skill ne corrige aucun code.** Même une dette qui se solderait en trente secondes. Un
correctif ouvre un chantier avec `/implementation-tracker` — c'est ce qui empêche une revue de se
transformer en session de bricolage dont personne n'a validé le périmètre.

**2. Un verdict par fiche, aucune omise.** `derive` crée exactement une fiche par entrée et
`validate --filled` refuse la moindre fiche vierge : la complétude n'est plus quelque chose qu'on
vérifie à la main, c'est quelque chose qu'une commande refuse.

Une entrée qu'on ne sait pas classer est `pertinent` : le doute laisse la dette où elle est.

**3. L'utilisateur arbitre, le skill écrit ensuite.** Le rapport aggloméré est présenté,
l'utilisateur tranche entrée par entrée, l'écriture suit. Jamais l'inverse.

> *Mode de défaillance* — un skill qui solde de sa propre autorité produit exactement le geste que
> le registre existe pour empêcher : faire disparaître un problème avec l'air de l'avoir traité.

## Ce qu'il faut lire

- `references/categories.md` — les catégories de verdict, ce qui entre dans chacune, la preuve
  exigée et la destination. **À lire avant d'instruire**, pas après.
- `references/gabarit-rapport.md` — la fiche et l'aggloméré : ce que chaque section attend, et ce
  que `merge` en fait.
- `references/exemple-revue.md` — une fiche instruite par catégorie, sur un dépôt fictif.
- `../implementation-tracker/references/dette.md` — la tenue des registres : contrat d'une entrée,
  règle de solde, champs de revue.

**Aucun fichier n'est créé, déplacé ni renommé à la main.** Toute manipulation de liste passe par
une commande de `list-dir` ; le modèle n'écrit que **dans** des fiches déjà créées. Un `mv` ou un
`cp` sur un élément de liste est le signe qu'on a repris le travail du script.

---

## Étape 0 — Prérequis

```bash
date +%F
git rev-parse --is-inside-work-tree 2>/dev/null || echo "NON_GIT"

T=.claude/implementation/todo

for l in technical-debt technical-debt-solde technical-debt-ecarte; do
  if [ ! -d "$T/$l" ]; then
    echo "ABSENT : $l"
    continue
  fi
  list-dir validate "$T/$l" >/dev/null; rc=$?
  if [ "$rc" -eq 127 ]; then
    echo "OUTIL ABSENT : list-dir"
    break
  elif [ "$rc" -ne 0 ]; then
    echo "NON CONFORME : $l"
  elif [ "$(list-dir list "$T/$l" | wc -l)" -eq 0 ]; then
    echo "VIDE : $l"
  else
    echo "OK : $l"
  fi
done
ls .claude/implementation/done/revues/ 2>/dev/null
git status --short | grep -v '^.. \.claude/implementation/'
```

**Chaque registre imprime son état, et chaque état a sa puce plus bas.** `list-dir validate` sort 1
aussi bien sur un répertoire absent que sur des éléments non conformes ou sur un `list-dir`
introuvable, et rend 0 sur une liste vide comme sur une liste pleine : aucun de ces états ne se
déduit de son seul code de retour. Un `ÉCHEC` unique — ou pire, un silence — laisserait le lecteur
choisir sa règle sans rien pour trancher.

Ne pas annoncer ici **combien** il y en a : le compte s'est déjà périmé une fois, l'étiquette
`OUTIL ABSENT` ayant été ajoutée sans que la phrase suive. Le bloc et les puces se répondent, et
c'est cette correspondance qui se relit — pas un nombre écrit à côté d'eux.

> *Mode de défaillance* — une version de ce bloc taisait `validate` par `>/dev/null` et n'imprimait
> **rien** quand les trois registres étaient conformes et vides. Un état auquel une règle s'applique
> se lisait comme « tout va bien ». D'où le `OK :` explicite : ici, aucune sortie du tout signifie
> que la boucle n'a pas tourné, pas que tout est en ordre.

Utiliser la date renvoyée par `date`, jamais l'inventer :
[Dates et listing](../implementation-tracker/references/contrat.md#dates-et-listing).

Un état, une suite, et pas deux :

- **`ABSENT` sur les trois** → les registres n'existent pas encore dans ce projet. Les amorcer,
  puis reprendre l'étape : [Registre de dette](../implementation-tracker/references/dette.md) en
  porte la procédure. Ne pas la recopier ici, et ne créer aucun répertoire à la main — l'amorçage
  est une commande.
- **`ABSENT` sur un ou deux** → le dire et s'arrêter. Ce n'est pas un projet neuf mais un registre
  incomplet, et amorcer par-dessus masquerait la question de savoir ce qui a disparu.
- **`NON CONFORME`, quel que soit le registre** → le dire et s'arrêter. Une revue qui part d'un
  registre non conforme instruit des entrées dont la structure ment déjà — mais **la remise en
  conformité n'est pas le travail d'une revue**, et `migrate` réécrit des fichiers que
  l'utilisateur n'a pas demandé à voir changer sous prétexte qu'il demandait une relecture.
- **`VIDE` sur `technical-debt`** → le dire et s'arrêter : il n'y a rien à instruire, et l'Étape 1
  échouerait de toute façon — `derive` refuse une liste sans élément. Ce n'est pas une anomalie :
  un registre soldé jusqu'à la dernière entrée est un bon registre.
- **`VIDE` sur `technical-debt-solde` ou `-ecarte`** → **continuer, c'est l'état normal.** Ces deux
  registres sont des **destinations**, pas des sources : ils ne se remplissent qu'à l'Étape 5, quand
  un `move` y dépose une entrée sortie du registre actif. Un projet qui n'a jamais rien soldé les a
  légitimement vides, et l'Étape 5 le redit en toutes lettres — « `technical-debt-ecarte` reste vide
  tant qu'aucune revue n'a écarté d'entrée ».
- **`OK` sur `technical-debt`** → continuer. C'est le seul registre dont l'état décide qu'il y a une
  revue à faire ; les deux autres n'ont qu'à exister et être conformes, puisque l'Étape 5 y écrit.
- **`OUTIL ABSENT`** → s'arrêter, et dire que `list-dir` est introuvable dans le `PATH` — pas qu'un
  registre est en faute. Ce n'est pas une garde de présence recopiée ici : `sante_skills.py` la fait
  déjà une fois par session ([Dépendances](../implementation-tracker/references/contrat.md#dépendances)).
  C'est le refus d'**attribuer au registre** un code 127 qui n'est pas le sien.

- **Modifications hors de `.claude/implementation/`** → le signaler et demander. C'est ce que
  filtre le `grep -v` ci-dessus : une sortie vide suffit à continuer. Le contrôle ne porte que sur
  ce qui **fausserait** le `git status --short` de l'Étape 5 — un fichier déjà modifié sous
  `.claude/implementation/` y serait de toute façon accepté, donc l'exiger propre rejetterait des
  arbres parfaitement sains.
- **Une revue existe déjà à la date du jour** parmi les répertoires listés → la lire et proposer de
  la reprendre. `derive` **refuse** d'écraser une destination existante, et c'est voulu : deux
  revues sont deux répertoires, jamais une fusion.

> *Mode de défaillance* — ces règles ont été fautives trois fois de suite, toujours de la même
> façon : chaque correctif relisait la ligne qu'il visait, jamais son voisinage. Deux pièges s'y
> cachent. D'abord, **les trois registres ne sont pas symétriques** — `technical-debt` est la
> source dont l'Étape 1 dérive, `-solde` et `-ecarte` sont les destinations où l'Étape 5 écrit ;
> une règle qui les traite uniformément se trompe forcément sur deux d'entre eux, et l'une d'elles
> arrêtait la revue d'un projet amorcé dès sa première dette. Ensuite, **le bloc et les puces
> vieillissent séparément** : un état que le bloc cesse d'imprimer laisse une puce sans déclencheur,
> et l'inverse laisse une sortie sans consigne. Une règle ajoutée ici se relit donc contre les trois
> autres puces **et** contre les Étapes 1 et 5.

> *Mode de défaillance* — `! list-dir validate` était vrai pour **n'importe quel** code non nul, y
> compris le 127 d'une commande introuvable : un registre parfaitement sain s'affichait alors
> `NON CONFORME`, et la seule trace du vrai motif partait sur `stderr`. Un diagnostic faux coûte
> plus cher qu'une absence de diagnostic — il envoie corriger ce qui n'est pas cassé.

**Personne à qui demander** — appel non interactif, ou sous-agent : **s'arrêter et le dire**, sans
instruire. Ce skill est manuel par construction (`disable-model-invocation`), et chacun de ses
points d'arrêt attend une réponse humaine. Continuer sur une supposition produirait un rapport que
personne n'a arbitré, c'est-à-dire précisément ce que la troisième règle interdit.

Un argument `@chemin` désigne un autre registre que celui par défaut.

## Étape 1 — Dériver la liste de revue

```bash
R=".claude/implementation/done/revues/$(date +%F)"
list-dir derive "$T/technical-debt" "$R" --template review
list-dir validate "$R"
```

`derive` crée exactement une fiche par entrée du registre — **à cet instant, et à cet instant
seul.** Ce qu'il reporte et depuis quels gabarits :
[Listes dérivées](../list-dir/references/contrat-liste.md#listes-dérivées).

Ce que `merge` vérifiera plus tard est autre chose : il recompte les blocs rendus face aux
**fichiers présents dans la liste de revue**. Une fiche disparue entre les deux réduit les deux
comptes à la fois et ne fait donc rien échouer. Le registre est la seule référence qui ne bouge pas,
et c'est contre lui que la complétude se contrôle :

```bash
test "$(list-dir list "$R" | wc -l)" -eq "$(list-dir list "$T/technical-debt" | wc -l)" \
  || echo "ÉCHEC : autant de fiches que d'entrées attendu"
```

À rejouer **avant `merge`**, à l'Étape 3. C'est le seul contrôle de la revue qui ne soit pas dans
une commande, précisément parce que la liste générique ne connaît pas le registre dont elle dérive.

La fiche **ne porte rien de la prose de l'entrée**, et c'est délibéré : une fiche qui recopierait le
*Constat* en serait un doublon éditable, et le registre cesserait d'être la source unique.

## Étape 2 — Instruire, fiche par fiche

Traiter les fiches **une à une**, dans l'ordre du registre :

```bash
list-dir list "$T/technical-debt" --sort date     # l'ordre de travail
list-dir show "$T/technical-debt" <id>            # l'entrée à instruire
```

Pour chacune :

1. Lire son **Constat** et son **Pour solder** — ce sont eux qui disent quoi aller chercher.
2. **Exécuter la commande** qui établit si le constat tient encore. Ce qu'elle doit être est dit
   au contrat de la liste de revue, section `Vérifié par`.
3. Classer, selon `references/categories.md`.
4. Écrire la fiche `$R/<id>.md` : les champs `category` et `reviewed`, puis les sections **Vérifié
   par**, **Verdict** et **Action**. La section `Arbitrage` reste au marqueur jusqu'à l'Étape 4.

**Ne pas grouper les vérifications.** Une passe de `grep` qui répond à six entrées d'un coup produit
six classements adossés à la même lecture — c'est le raccourci qui fait rater les cas particuliers,
et il ne laisse aucune commande rejouable par entrée.

**Les repères d'une entrée ancienne sont périmés par défaut.** Chercher le **texte** que l'entrée
décrit, jamais la ligne qu'elle nomme : un `fichier.md:42` qui a glissé de trois lignes se lit comme
une cible disparue, et fait classer `non-pertinent` une dette parfaitement vivante. Le registre ne
doit plus en contenir (`../implementation-tracker/references/dette.md`, « Ce qu'une entrée porte ») ;
ceux qui restent sont à corriger, pas à croire.

**Sans commande exécutée, l'entrée est `pertinent`.** Pas « probablement soldée », pas « sans doute
obsolète » : la plausibilité ne fait sortir personne du registre.

**Compter en caractères, pas en octets.** Sur un corpus accentué, `awk 'length > 100'` compte les
octets : il rend une centaine de faux dépassements et fait conclure `aggravee` sur un artefact
d'encodage. Utiliser `wc -L`, ou `python3` quand il faut le détail :

```bash
python3 -c "
import sys
for i, l in enumerate(open(sys.argv[1], encoding='utf-8'), 1):
    if len(l.rstrip('\n')) > 100: print(i, len(l.rstrip('\n')))" <fichier>
```

Le piège vaut au-delà des longueurs de ligne : toute commande qui compte des caractères sur du texte
français doit être choisie pour ça.

Quand toutes les fiches sont écrites :

```bash
list-dir validate "$R" --filled
```

**Sortie ≠ 0 → une fiche n'est pas instruite**, et le message nomme le fichier et ce qui y manque.
Ce contrôle dit que chaque fiche **présente** est remplie ; il ne dit rien de celles qui auraient
disparu — c'est le rôle du comptage contre le registre, ci-dessous.

## Étape 3 — Agglomérer et restituer

```bash
test "$(list-dir list "$R" | wc -l)" -eq "$(list-dir list "$T/technical-debt" | wc -l)" \
  || echo "ÉCHEC : autant de fiches que d'entrées attendu"
list-dir merge "$R" --out "$R-revue.md"
```

**Le comptage passe avant `merge`, et il n'est pas redondant avec lui.** `merge` recompte les blocs
rendus face aux fichiers présents dans la liste de revue : il attrape un `title` qui ouvrirait un
faux bloc, mais **pas** une fiche supprimée, qui réduit les deux comptes ensemble. Seul le registre
est une référence extérieure.

> *Mode de défaillance* — mesuré : 16 fiches dérivées de 17 entrées s'agglomèrent en 16 blocs, code
> 0, préambule « 16 — 16 ». Le rapport se lit comme complet, et l'entrée manquante n'est signalée
> par rien. C'est la seule façon qu'une revue a de perdre une entrée en silence.

Le rapport s'écrit à côté de sa liste, `done/revues/<AAAA-MM-DD>-revue.md`, directement à sa place
définitive : pas de fichier de travail à déplacer, donc pas d'archivage à oublier. `merge` refuse
par ailleurs d'agglomérer tant qu'un marqueur subsiste.

Présenter **les piles**, pas les fiches une par une : leur intitulé, leur effectif, et pour celles
qui font sortir une entrée du registre, le verdict en une ligne chacune.

```bash
if ! CATEGORIES=$(list-dir contract "$R" --values category); then
  echo "ÉCHEC : contrat illisible — les piles ne peuvent pas être comptées"; false
else
  printf '%s\n' "$CATEGORIES" | while read -r c; do
    printf '%-16s %s\n' "$c" "$(list-dir list "$R" --where category=$c | wc -l)"
  done
fi
```

L'affectation testée puis le `while read` ne sont pas un détour : c'est la forme qu'impose le
contrat de `--values`
([Ce que `contract` vise](../list-dir/references/contrat-liste.md#ce-que-contract-vise-et-ce-que-ça-engage)).
Ici, un tableau vide se lirait « aucune fiche » au lieu de « liste illisible ».

> *Mode de défaillance* — le `if … ; false` plutôt qu'un `|| exit 1` : ces blocs se collent dans un
> shell interactif, où un `exit` fermerait la session de l'opérateur. Le `false` rend l'échec au
> code de sortie sans rien tuer.

**L'ordre des piles est celui du contrat** — ce qui **sort** du registre d'abord, ce qui y **reste**
ensuite. Il n'est pas recopié ici : `--values` rend les valeurs déclarées dans l'ordre du fichier,
et c'est le commentaire du contrat qui dit pourquoi cet ordre-là. Une catégorie ajoutée entre donc
dans la boucle sans que rien ne soit à retoucher ici. Il ne s'obtient pas par `--sort category`,
qui ordonne les valeurs alphabétiquement ; `--sort date` ordonne l'intérieur d'une pile.

## Étape 4 — Arbitrer

Faire trancher, pile par pile. Une décision peut être :

- **suivie** — la destination prévue s'applique ;
- **renversée** — l'utilisateur reclasse l'entrée ; corriger `category` **et** le **Verdict** de la
  fiche, ne pas la laisser mentir ;
- **différée** — l'entrée reste au registre telle quelle, sans marqueur ;
- **élargie en règle** — l'arbitrage ne porte plus sur l'entrée seule, mais sur la façon dont le
  registre se tient. Voir ci-dessous.

Consigner l'arbitrage dans la section `Arbitrage` de la fiche concernée, puis **réagglomérer** :

```bash
list-dir merge "$R" --out "$R-revue.md"
```

C'est ce qui distingue un rapport archivé d'un rapport qui n'a servi à rien. Une section `Arbitrage`
laissée au marqueur est simplement omise du rapport — le fichier ne se constelle pas de sections
vides.

### Quand l'arbitrage produit une règle

Une entrée révèle souvent moins un problème isolé qu'un **manque dans la tenue du registre** : des
repères qui se périment, un genre de défaut qu'aucune catégorie ne nomme. L'utilisateur tranche
alors une règle, et cette règle s'écrit — sinon la revue suivante rejouera le même arbitrage sans
mandat, et les entrées corrigées ici auront l'air de l'avoir été sans autorité.

Où elle s'écrit, selon ce qu'elle régit :

- **la tenue des registres** (contrat d'une entrée, solde, mise à l'écart, correction, champs de
  revue) → `../implementation-tracker/references/dette.md`, qui en est l'autorité ;
- **le classement** (ce qu'une catégorie couvre, ce qu'elle ne couvre pas) →
  `references/categories.md`, avec un renvoi vers `dette.md` plutôt qu'une recopie ;
- **la structure d'une liste** (un champ à ajouter au contrat, une section à déclarer) → le
  `.list/contract.toml` concerné, puis `migrate` pour remettre les éléments en conformité ;
- **le geste de la revue** → ce fichier.

**La règle s'écrit avant les corrections qu'elle autorise**, jamais après : c'est elle qui les rend
rejouables. Et elle est **la seule raison** pour laquelle une passe de revue écrit hors de
`.claude/implementation/` — l'Étape 6 en tient compte.

> *Mode de défaillance* — sans ce chemin, la seule issue est de corriger les entrées sans écrire la
> règle. Les corrections passent alors pour des retouches d'humeur, et le prochain relecteur, qui
> lit un dispositif muet sur le sujet, les défait de bonne foi.

## Étape 5 — Écrire les registres

Seulement sur les entrées arbitrées, et **jamais à la main** : une entrée qui sort du registre
change de liste par `move`.

1. **`a-solder`** :

   ```bash
   list-dir move "$T/technical-debt" <id> "$T/technical-debt-solde"
   ```

   **Proposer le commit du seul déplacement** — jamais le lancer d'autorité. Puis, une fois
   accordé et fait, écrire la section `## Soldé le` de l'entrée déplacée : la date, ce qui l'a
   soldée, et la commande exécutée avec sa sortie. Elle part **dans un second commit**.

2. **`non-pertinent`, `doublon`, `pas-une-dette`** → même geste vers `$T/technical-debt-ecarte`,
   puis la section `## Écartée le` avec son motif et sa preuve.

3. **`aggravee`** → l'entrée ne bouge pas : réécrire son **Constat**, daté du jour.

4. **`inverifiable`, `pertinent`, `aggravee`** et toute entrée restée au registre → écrire ses deux
   champs de revue, `category` et `reviewed` (la date du jour).

5. **Corrections de contenu arbitrées** — une entrée vraie mais mal écrite se corrige sur place,
   quelle que soit sa catégorie. Date et `id` ne bougent pas, et la correction porte sa commande.

Forme exacte des sections `Soldé le` et `Écartée le`, preuve exigée, et raison pour laquelle le
déplacement et la réécriture ne partagent jamais un commit :
[Solder](../implementation-tracker/references/dette.md#solder) et
[Écarter](../implementation-tracker/references/dette.md#écarter).

**Contrôle de conservation** — aucune entrée ne disparaît en chemin :

```bash
for l in technical-debt technical-debt-solde technical-debt-ecarte; do
  printf '%-26s %s\n' "$l" "$(list-dir list "$T/$l" | wc -l)"
done
list-dir validate "$T/technical-debt" --filled
```

La somme après la revue égale la somme avant. Une liste vide compte 0 et ne fait pas échouer le
contrôle — `technical-debt-ecarte` reste vide tant qu'aucune revue n'a écarté d'entrée.

**Rester à la racine du dépôt**, ici comme partout dans ce skill : pas de `cd` vers `todo/`. Les
chemins que `git status --short` rend sont relatifs au répertoire courant, et l'Étape 6 a besoin de
les lire préfixés.

## Étape 6 — Rendre la main

```bash
git status --short
```

**Il ne doit lister que des chemins sous `.claude/implementation/`** — plus, si et seulement si un
arbitrage a produit une règle, le ou les fichiers de règle que l'Étape 4 nomme. Tout autre chemin
est un fichier de code, et l'avoir modifié est la violation de la première règle : le dire, et
proposer de l'annuler.

> *Mode de défaillance* — ce contrôle a d'abord interdit **tout** chemin hors de
> `.claude/implementation/`, ce qui faisait de son propre cas nominal une faute : à la première
> passe réelle, deux arbitrages sur trois ont produit une règle, donc une écriture dans `skills/`.
> Un contrôle qui traite le cas courant comme une violation ne se lit plus — on apprend à passer
> outre, et le jour où il signale une vraie modification de code, il a déjà perdu son autorité.

> *Mode de défaillance* — lancée depuis `todo/`, cette commande rend ` M README.md` : le préfixe
> disparaît, et le contrôle ne peut plus établir ce qu'il est là pour établir. C'est le seul
> contrôle qui garantit qu'aucun code n'a été touché — il se lit depuis la racine, ou pas du tout.

Puis, en deux ou trois lignes : ce qui est sorti du registre et vers où, ce qui a été marqué, ce
qui reste. Le rapport porte le détail, ne pas le recopier.

Un correctif à mener n'est **pas** proposé ici comme une suite naturelle. Il s'ouvre avec
`/implementation-tracker`, qui le cadrera comme n'importe quel autre chantier — c'est le seul moyen
qu'une dette soldée le soit avec un périmètre écrit et une vérification.
