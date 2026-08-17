---
name: debt-review
description: >
  Relit le registre de dette technique entrée par entrée et le confronte au dépôt : chaque entrée
  reçoit une catégorie instruite par une commande exécutée, l'utilisateur arbitre, puis les
  registres de todo/ sont mis à jour et le rapport archivé. Skill exclusivement manuelle : elle
  s'invoque uniquement via /debt-review. Ne corrige aucun code.
disable-model-invocation: true
argument-hint: "[@chemin/vers/technical-debt.md]"
---

# Debt Review

Le pipeline sait **alimenter** le registre de dette — l'orchestrateur y verse à la clôture ce qu'un
chantier laisse derrière lui — mais rien ne savait le **relire**. Une entrée soldée par un autre
chantier y reste, un constat devenu sans objet y reste, et un registre qu'on soupçonne périmé ne se
lit plus.

Ce skill est cette relecture, et rien d'autre : **il instruit, il ne répare pas.**

---

## Les trois règles

**1. Le skill ne corrige aucun code.** Même une dette qui se solderait en trente secondes. Un
correctif ouvre un chantier avec `/implementation-tracker` — c'est ce qui empêche une revue de se
transformer en session de bricolage dont personne n'a validé le périmètre.

**2. Un verdict par entrée, aucune omise.** Le compte des blocs du rapport égale le nombre d'entrées
du registre. Une entrée qu'on ne sait pas classer est `pertinent` : le doute laisse la dette où elle
est.

**3. L'utilisateur arbitre, le skill écrit ensuite.** Le rapport trié est présenté, l'utilisateur
tranche entrée par entrée, l'écriture suit. Jamais l'inverse.

> *Mode de défaillance* — un skill qui solde de sa propre autorité produit exactement le geste que
> le registre existe pour empêcher : faire disparaître un problème avec l'air de l'avoir traité.

## Ce qu'il faut lire

- `references/categories.md` — les sept catégories, ce qui entre dans chacune, la preuve exigée et
  la destination. **À lire avant d'instruire**, pas après.
- `references/gabarit-rapport.md` — la forme du bloc, seule chose que le modèle et le script
  doivent respecter à l'identique.
- `../implementation-tracker/references/dette.md` — la tenue des registres : gabarit d'entrée,
  règle de solde, ligne de dernière vérification.

---

## Étape 0 — Prérequis

```bash
date +%F
git rev-parse --is-inside-work-tree 2>/dev/null || echo "NON_GIT"
ls .claude/implementation/todo/
mkdir -p .claude/implementation/done/revues
ls .claude/implementation/done/revues/
git status --short | grep -v '^.. \.claude/implementation/'
```

Utiliser la date renvoyée par `date`, jamais l'inventer :
[Dates et listing](../implementation-tracker/references/contrat.md#dates-et-listing).

Le `mkdir -p` n'est pas une précaution : `done/revues/` n'existe pas dans un dépôt qui n'a jamais
été revu, et l'Étape 1 y écrit directement. Sans lui, la première revue d'un dépôt échoue à
l'écriture — après avoir instruit toutes les entrées.

- **Registre absent** → le dire et s'arrêter. Ce skill relit un registre existant ; il n'en crée
  pas, et n'a rien à instruire sur un fichier vide.
- **Modifications hors de `.claude/implementation/`** → le signaler et demander. C'est ce que
  filtre le `grep -v` ci-dessus : une sortie vide suffit à continuer. Le contrôle ne porte que sur
  ce qui **fausserait** le `git status --short` de l'Étape 5 — un fichier déjà modifié sous
  `.claude/implementation/` y serait de toute façon accepté, donc l'exiger propre rejetterait des
  arbres parfaitement sains.
- **Un rapport existe déjà à la date du jour** parmi les fichiers listés → le lire et proposer de le
  reprendre. Ne jamais l'écraser sans accord ; le tri est idempotent, le relancer ne coûte rien.

**Personne à qui demander** — appel non interactif, ou sous-agent : **s'arrêter et le dire**, sans
instruire. Ce skill est manuel par construction (`disable-model-invocation`), et chacun de ses
points d'arrêt attend une réponse humaine. Continuer sur une supposition produirait un rapport que
personne n'a arbitré, c'est-à-dire précisément ce que la troisième règle interdit.

Un argument `@chemin` désigne un autre registre que celui par défaut.

## Étape 1 — Instruire, entrée par entrée

Lire le registre en entier, puis traiter les entrées **une à une, dans l'ordre du fichier**.

Pour chacune :

1. Lire son **Constat** et son **Pour solder** — ce sont eux qui disent quoi aller chercher.
2. **Exécuter la commande** qui établit si le constat tient encore. La choisir pour qu'elle se
   rejoue seule, sans contexte : c'est elle qui sera recopiée dans le registre.
3. Classer, selon `references/categories.md`.
4. Écrire le bloc dans le rapport, au format du gabarit.

Le rapport s'écrit directement à sa place définitive, `done/revues/<AAAA-MM-DD>-revue.md` : il n'y a
pas de fichier de travail à déplacer ensuite, donc pas d'archivage à oublier.

**Ne pas grouper les vérifications.** Une passe de `grep` qui répond à six entrées d'un coup produit
six classements adossés à la même lecture — c'est le raccourci qui fait rater les cas particuliers,
et il ne laisse aucune commande rejouable par entrée.

**Les repères d'une entrée ancienne sont périmés par défaut.** Chercher le **texte** que l'entrée
décrit, jamais la ligne qu'elle nomme : un `fichier.md:42` qui a glissé de trois lignes se lit comme
une cible disparue, et fait classer `non-pertinent` une dette parfaitement vivante. Le registre ne
doit plus en contenir (`../implementation-tracker/references/dette.md`, « Gabarit d'entrée ») ; ceux
qui restent sont à corriger, pas à croire.

**Sans commande exécutée, l'entrée est `pertinent`.** Pas « probablement soldée », pas « sans doute
obsolète » : la plausibilité ne fait sortir personne du registre.

**`## ` est réservé aux en-têtes de bloc**, dans tout le rapport — c'est le séparateur du script,
pas un niveau de titre. Un `## Comptes`, un `## ` de pile vide, et le tri s'arrête sur « en-tête mal
formé » sans dire pourquoi le titre gêne. Le préambule accueille tout le reste : lui survit au tri,
et rien n'y est découpé.

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

## Étape 2 — Trier

```bash
bash "$HOME/.claude/skills/debt-review/scripts/trier-revue.sh" \
     .claude/implementation/done/revues/<AAAA-MM-DD>-revue.md
```

Le modèle étiquette, le script regroupe : le tri par catégorie puis par date est mécanique, et le
script vérifie qu'aucun bloc ne s'est perdu en route.

**Sortie ≠ 0 → corriger le rapport, pas contourner le script.** Un bloc rejeté est un bloc dont
l'en-tête ne rattache plus rien au registre.

Puis remplacer le rapport par sa version triée — **jamais par une redirection vers lui-même** :

```bash
R=.claude/implementation/done/revues/<AAAA-MM-DD>-revue.md
bash "$HOME/.claude/skills/debt-review/scripts/trier-revue.sh" "$R" > "$R.trie" \
  && mv "$R.trie" "$R"
```

> *Mode de défaillance* — `trier-revue.sh "$R" > "$R"` **détruit le rapport** : le shell tronque le
> fichier avant que le script ne le lise, et le tri s'exécute sur du vide. Mesuré : 8 blocs et 4172
> octets ramenés à 0. Le rapport vit dans `done/revues/`, que git ne suit pas encore à ce stade —
> il n'y a rien à restaurer, et c'est le travail de l'Étape 1 en entier qui disparaît. Le `&&` du
> bon idiome sert la même prudence : sortie ≠ 0, le rapport d'origine reste en place.

**Confronter le compte** : autant de blocs que d'entrées au registre. Un écart ici est une entrée
oubliée à l'Étape 1, pas une erreur de tri.

Ce compte s'écrit **dans le préambule du rapport**, avec la date de la revue et le chemin du
registre. Le tri le conserve — c'est le seul endroit du fichier qu'il ne redécoupe pas — donc le
rapport archivé porte lui-même la preuve qu'aucune entrée n'a été oubliée, sans dépendre de la
conversation où il a été produit.

## Étape 3 — Restituer et arbitrer

Présenter **les piles**, pas les blocs un par un : leur intitulé, leur effectif, et pour celles qui
font sortir une entrée du registre, le verdict en une ligne chacune.

Puis faire arbitrer, pile par pile. Une décision peut être :

- **suivie** — la destination prévue s'applique ;
- **renversée** — l'utilisateur reclasse l'entrée ; réécrire le bloc, ne pas le laisser mentir ;
- **différée** — l'entrée reste au registre telle quelle, sans marqueur ;
- **élargie en règle** — l'arbitrage ne porte plus sur l'entrée seule, mais sur la façon dont le
  registre se tient. Voir ci-dessous.

Consigner l'arbitrage dans le rapport, sous le bloc concerné. C'est ce qui distingue un rapport
archivé d'un rapport qui n'a servi à rien.

### Quand l'arbitrage produit une règle

Une entrée révèle souvent moins un problème isolé qu'un **manque dans la tenue du registre** : des
repères qui se périment, un genre de défaut qu'aucune catégorie ne nomme. L'utilisateur tranche
alors une règle, et cette règle s'écrit — sinon la revue suivante rejouera le même arbitrage sans
mandat, et les entrées corrigées ici auront l'air de l'avoir été sans autorité.

Où elle s'écrit, selon ce qu'elle régit :

- **la tenue des registres** (gabarit d'entrée, solde, mise à l'écart, correction, marqueur) →
  `../implementation-tracker/references/dette.md`, qui en est l'autorité ;
- **le classement** (ce qu'une catégorie couvre, ce qu'elle ne couvre pas) →
  `references/categories.md`, avec un renvoi vers `dette.md` plutôt qu'une recopie ;
- **le geste de la revue** → ce fichier.

**La règle s'écrit avant les corrections qu'elle autorise**, jamais après : c'est elle qui les rend
rejouables. Et elle est **la seule raison** pour laquelle une passe de revue écrit hors de
`.claude/implementation/` — l'Étape 5 en tient compte.

> *Mode de défaillance* — sans ce chemin, la seule issue est de corriger les entrées sans écrire la
> règle. Les corrections passent alors pour des retouches d'humeur, et le prochain relecteur, qui
> lit un dispositif muet sur le sujet, les défait de bonne foi.

## Étape 4 — Écrire les registres

Dans cet ordre, et seulement sur les entrées arbitrées :

1. **`a-solder`** → retirer du registre, appender en fin de `technical-debt-solde.md` avec
   `**Soldé le <date> par <ce qui l'a soldé>**` et la commande exécutée.
2. **`non-pertinent`, `doublon`, `pas-une-dette`** → retirer du registre, appender en fin de
   `technical-debt-ecarte.md` avec `**Écartée le <date> — <motif>**` et la commande, ou l'entrée
   conservée pour un doublon.
3. **`aggravee`** → réécrire le **Constat**, daté du jour ; ajouter `(aggravée) <date>` sous le
   titre. L'intitulé ne change pas.
4. **`inverifiable`** → ajouter `(invérifiable en revue) <date>` sous le titre. Rien d'autre.
5. **`pertinent`** → ne rien écrire.
6. **Corrections de contenu arbitrées** — une entrée vraie mais mal écrite se corrige sur place,
   quelle que soit sa catégorie : `../implementation-tracker/references/dette.md`, « Corriger une
   entrée ».
   Date et intitulé ne bougent pas, et la correction porte sa commande.
7. **Actualiser la ligne de dernière vérification** en tête du registre, avec la date du jour —
   y compris si la revue n'a rien fait sortir. C'est l'information qu'elle porte : le registre a
   été relu.

Forme exacte des champs `Soldé le` et `Écartée le`, preuve exigée, et création du fichier des
écartés s'il n'existe pas encore : `../implementation-tracker/references/dette.md`, sections
« Solder » et « Écarter ».

**Contrôle de conservation** — aucune entrée ne disparaît en chemin :

```bash
total=0
for f in technical-debt technical-debt-solde technical-debt-ecarte; do
  p=".claude/implementation/todo/$f.md"
  n=$([ -f "$p" ] && grep -c '^## ' "$p" || echo 0)
  printf '%-22s %s\n' "$f" "$n"
  total=$((total + n))
done
printf '%-22s %s\n' TOTAL "$total"
```

La somme après la revue égale la somme avant. Une entrée manquante n'est signalée par rien d'autre.

**Un registre absent compte 0**, il ne fait pas échouer le contrôle : `technical-debt-ecarte.md`
n'existe qu'à partir de la première mise à l'écart, donc toute revue qui n'écarte rien tomberait
sinon sur `No such file or directory` et un `rc=2` — un contrôle en erreur là où le résultat est
bon.

**Rester à la racine du dépôt**, ici comme partout dans ce skill : pas de `cd` vers `todo/`. Les
chemins que `git status --short` rend sont relatifs au répertoire courant, et l'Étape 5 a besoin de
les lire préfixés.

## Étape 5 — Rendre la main

```bash
git status --short
```

**Il ne doit lister que des chemins sous `.claude/implementation/`** — plus, si et seulement si un
arbitrage a produit une règle, le ou les fichiers de règle que l'Étape 3 nomme. Tout autre chemin
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
