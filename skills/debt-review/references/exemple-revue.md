# Exemple de rapport de revue — jeu de test du script de tri

**Huit blocs pour sept catégories** : la pile `pertinent` en porte deux, de dates différentes, sans
quoi le tri par date **à l'intérieur** d'une pile ne serait couvert par aucun test. Catégories et
dates sont volontairement mêlées, et les deux blocs `pertinent` apparaissent ici **du plus récent au
plus ancien** — le tri doit les inverser. Ne pas ranger ce fichier.

Ce fichier est le jeu de test permanent de `../scripts/trier-revue.sh`. Le modifier sans relancer le
script est le meilleur moyen de casser le tri en silence.

> **Les entrées ci-dessous sont fictives**, ainsi que le dépôt qu'elles décrivent — un service de
> commandes en Python qui n'existe pas. C'est délibéré : un exemple bâti sur une vraie entrée du
> registre livre un verdict pré-mâché sur une dette que le relecteur va rencontrer, et le pousse à
> recopier ce verdict au lieu d'exécuter sa commande. Aucun intitulé d'ici ne doit figurer dans
> `technical-debt.md`.

## pertinent | 2025-06-19 | Le client HTTP ne fixe aucun timeout

**Vérifié par** — `grep -rn 'requests.get\|requests.post' orders/ | grep -vc timeout` → 7 appels sur
7 sans timeout.

**Verdict** — inchangé depuis le constat d'origine.

**Action** — laisser au registre.

## aggravee | 2025-02-11 | Trois vues dupliquent la règle de remise

**Vérifié par** — `grep -rln 'discount_rate' orders/views/` → 5 fichiers, là où l'entrée en
décrivait 3.

**Verdict** — toujours vrai, et deux vues de plus qu'à l'origine.

**Action** — laisser au registre, réécrire le **Constat**, marquer `(aggravée) <date>` sous le
titre.

## pertinent | 2025-01-08 | Les migrations ne sont pas rejouables

**Vérifié par** — `grep -c 'def downgrade' orders/migrations/*.py | grep -c ':0$'` → 12 migrations
sans `downgrade`.

**Verdict** — inchangé. Second bloc `pertinent` du jeu de test, et le plus ancien des deux : c'est
lui qui couvre le tri par date au sein d'une pile. Le retirer rend la régression d'ordonnancement
invisible.

**Action** — laisser au registre.

## non-pertinent | 2025-04-23 | Le module `legacy/xmlrpc.py` n'a aucun test

**Vérifié par** — `ls orders/legacy/xmlrpc.py` → `No such file or directory`, code de sortie 2.

**Verdict** — l'élément cité n'existe plus : le module a été supprimé, pas testé. Rien n'a été
réparé, d'où `non-pertinent` et non `a-solder`.

**Action** — écarter, motif `non pertinent`.

## inverifiable | 2025-02-11 | La migration 0042 n'a jamais été rejouée sur une copie de production

**Vérifié par** — sans objet : le constat porte un fait historique, pas un état du code. Aucune
lecture du dépôt ne peut établir qu'une opération n'a pas eu lieu ailleurs.

**Verdict** — restera vrai indéfiniment ; seul un usage réel peut le solder.

**Action** — laisser au registre, marquer `(invérifiable en revue) <date>` sous le titre.

## a-solder | 2025-03-04 | Le cache de sessions n'expire jamais

**Vérifié par** — `grep -n 'ttl' orders/cache.py` → `ttl=1800` passé au constructeur depuis le
commit `4f1c9ab`.

**Verdict** — la dette a été payée : les entrées de cache expirent, le problème décrit ne se
reproduit plus.

**Action** — déplacer en fin de `technical-debt-solde.md` avec la commande ci-dessus.

## doublon | 2025-07-02 | Le timeout du client HTTP n'est pas configurable

**Vérifié par** — sans objet : la preuve est l'intitulé de l'entrée conservée.

**Verdict** — dit la même chose que « Le client HTTP ne fixe aucun timeout », datée du 2025-06-19,
qui est **la plus ancienne des deux** et donc celle qui est conservée.

**Action** — écarter, motif `doublon`, en nommant l'entrée conservée.

## pas-une-dette | 2025-01-08 | Les noms de variables du module de facturation sont abrégés

**Vérifié par** — `grep -rnc '\bqty\b\|\bamt\b' orders/billing.py` → 23 occurrences, le constat
tient toujours.

**Verdict** — exact, mais c'est une préférence de style qu'aucun critère ne porte — exclue du
registre par construction.

**Action** — écarter, motif `pas une dette`.
