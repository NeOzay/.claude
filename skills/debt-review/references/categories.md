# Les catégories de verdict

Une entrée du registre reçoit **exactement une** catégorie. Aucune n'est omise : une entrée qu'on
ne sait pas classer est `pertinent` — le doute laisse la dette où elle est, il ne la fait pas
disparaître.

Le classement se fait **entrée par entrée, contre le dépôt**, jamais de mémoire ni par lecture du
seul registre. Trois entrées voisines dans le fichier peuvent avoir trois destins opposés.

**Règle de preuve** — les quatre catégories qui font *sortir* une entrée du registre exigent une
commande lancée et sa sortie réelle. C'est la règle du solde
(`../../implementation-tracker/references/dette.md`, « Solder ») étendue à toute sortie : *un solde
s'établit, il ne se déclare pas*, et une entrée écartée sans preuve est un solde déguisé. Sans
preuve exécutée, le classement retombe sur `pertinent`.

Deux catégories en sont dispensées, et seulement elles : `inverifiable`, où il n'y a rien à
exécuter, et `doublon`, où la preuve est l'intitulé de l'entrée conservée.

**Champs de revue** — toute entrée qui reste au registre reçoit `category` et `reviewed`, quels que
soient son verdict et la suite donnée. Forme exacte de ces deux champs et raison pour laquelle
l'intitulé n'est jamais touché : `../../implementation-tracker/references/dette.md`, « Marqueur
d'une entrée relue ». Ce fichier-ci dit **quel** verdict s'écrit, `dette.md` dit **comment** — la
tenue du registre lui appartient.

**Correction** — une entrée peut être vraie et **mal écrite** : chiffre faux dès l'origine, `Pour
solder` inexécutable, `Assumé` périmé, repère de ligne qui ne désigne plus rien. Aucune des
catégories ci-dessous ne le dit, et aucune n'a à le dire : la catégorie juge le **fait**, pas sa
rédaction. La fiche le signale, l'utilisateur arbitre, le texte se corrige sans que le verdict
change — `../../implementation-tracker/references/dette.md`, « Corriger une entrée ».

---

## À solder — `a-solder`

**Ce qui y entre** — la dette a été payée, par un autre chantier ou par un effet de bord. Le
problème que l'entrée décrit ne se reproduit plus.

**Preuve exigée** — la commande qui l'établit, avec sa sortie. C'est celle qui sera recopiée dans
le registre des soldes : la choisir pour qu'elle se rejoue seule, sans contexte.

**Destination** — `technical-debt-solde`, par `move` ; l'entrée déplacée reçoit sa section
`## Soldé le`, avec la date, ce qui l'a soldée et la commande.

> *Mode de défaillance* — celui qui vient de faire le travail est le plus mal placé pour affirmer
> qu'il l'a fait. Une entrée soldée sur constat de lecture, sans commande, reste au registre.

## Non pertinent — `non-pertinent`

**Ce qui y entre** — les éléments que l'entrée cite n'existent plus : le fichier a disparu, la
fonction a été retirée, le mécanisme décrit a été remplacé. La dette n'a pas été payée, elle est
devenue **sans objet**.

**Preuve exigée** — la commande qui montre l'absence. Un `grep` qui ne renvoie rien est une preuve,
à condition d'être cité tel quel : c'est la seule façon de distinguer « n'existe plus » de « je ne
l'ai pas trouvé ».

**Destination** — `technical-debt-ecarte`, par `move`, motif `non pertinent`.

> *Mode de défaillance* — confondre avec `à solder` efface l'information la plus utile du registre
> des soldes : ce qui a réellement été réparé, et par quoi. Un code supprimé n'a rien réparé.

## Doublon — `doublon`

**Ce qui y entre** — une autre entrée du registre dit la même chose. Le dédoublonnage n'a lieu
qu'à l'écriture (`../../implementation-tracker/references/dette.md`, « Alimenter ») ; rien ne le
refait ensuite, et deux chantiers successifs peuvent verser le même constat sous deux
formulations.

**Preuve exigée** — aucune commande : **l'`id` de l'entrée conservée**, cité dans le verdict. Sans
lui, la fiche n'est pas arbitrable.

**Destination** — `technical-debt-ecarte`, par `move`, motif `doublon`, en nommant l'`id` de
l'entrée conservée. La conservée est toujours **la plus ancienne** : c'est elle qui porte la date
d'origine du constat.

> *Mode de défaillance* — écarter les deux, ou garder la plus récente, perd la date à laquelle le
> problème a été vu pour la première fois. Le registre est ordonné par cette date.

## Pas une dette — `pas-une-dette`

**Ce qui y entre** — le constat est peut-être exact, mais il n'avait pas sa place au registre : une
idée d'amélioration, ou une préférence de style qu'aucun critère ne porte. Le filtre à l'entrée est
volontairement large (`../../implementation-tracker/references/dette.md`, « Ce qui entre »), donc
des entrées de ce genre sont
**attendues**, pas exceptionnelles.

**Preuve exigée** — la commande qui montre que le constat tient toujours, **plus** la raison de
l'exclusion. Une entrée fausse *et* hors sujet est `non pertinent` : cette catégorie-ci suppose que
le fait est vrai.

**Destination** — `technical-debt-ecarte`, par `move`, motif `pas une dette`.

> *Mode de défaillance* — cette catégorie est la porte de sortie facile. Y verser une vraie dette
> parce qu'elle ennuie fait exactement ce que le registre existe pour empêcher : la perdre avec
> l'accord de tout le monde. Dans le doute, c'est `pertinent`.

## Aggravée — `aggravee`

**Ce qui y entre** — l'entrée est toujours vraie, et le problème s'est étendu depuis le constat
d'origine : plus de fichiers touchés, plus d'appelants, un contournement de plus posé par-dessus.

**Preuve exigée** — la commande qui **chiffre** l'écart avec le constat d'origine. « C'est pire »
n'est pas un verdict ; « trois occurrences là où l'entrée en décrivait une » en est un.

**Destination** — reste au registre. Son **Constat** est réécrit et **daté du jour de la revue**,
pas de l'origine. Les champs `category` et `reviewed` de l'entrée portent le verdict ; `title` et
`id` ne bougent pas.

> *Mode de défaillance* — redater l'entrée entière la ferait remonter dans l'ordre chronologique et
> effacerait depuis quand le problème est connu. Seul le **Constat** est daté du jour.

## Pertinent — `pertinent`

**Ce qui y entre** — la dette est identifiable dans le code, telle que l'entrée la décrit. C'est
aussi la catégorie de repli : tout ce qui n'est pas établi par une preuve atterrit ici.

**Preuve exigée** — la commande qui montre que le constat tient. Elle vaut aussi pour la revue
suivante, qui n'aura pas à la retrouver.

**Destination** — inchangée, aux deux champs de revue près : `category = "pertinent"` et
`reviewed` à la date du jour.

> *Mode de défaillance* — une pile `pertinent` vide ou quasi vide après une revue est un signal, pas
> une réussite : elle veut dire que le classement a cherché des sorties plutôt que des faits.

## Invérifiable en revue — `inverifiable`

**Ce qui y entre** — le constat porte un **fait historique**, pas un état du code : « n'a jamais été
audité », « personne n'a relu ce diff ». Aucune lecture du dépôt ne peut le confirmer ni l'infirmer,
et il restera vrai indéfiniment. Le **Pour solder** de ces entrées est typiquement passif — attendre
un usage réel plutôt que produire un changement.

**Preuve exigée** — aucune. La fiche dit **pourquoi** rien n'est exécutable ; c'est ce qui la
distingue d'un classement paresseux.

**Destination** — reste au registre, `category = "inverifiable"` et `reviewed` à la date du jour.
Les revues suivantes la lisent sans la réinstruire, sauf si son **Pour solder** est devenu
actionnable.

> *Mode de défaillance* — sans ce marquage, ces entrées repassent en `pertinent` à chaque revue et
> occupent la pile qui demande une décision. Au bout de deux passages, la pile ne se lit plus.
