---
name: intent-brief
description: >
  Cadre l'intention de l'utilisateur AVANT le mode plan et produit un brief persistant
  (.claude/implementation/<slug>.brief.md) : intention réelle, critères de réussite,
  hors-périmètre, contraintes non devinables, signaux de dérive. Confronte ensuite le plan
  produit au brief. Se déclenche sur "cadrer", "brief", "avant de planifier", "aligner
  l'intention", ou quand une demande de planification/refonte arrive sans brief existant.
  Alimente implementation-tracker.
argument-hint: "[sujet du chantier]"
---

# Intent Brief

Le mode plan produit un bon plan **pour la demande telle qu'il l'a comprise**. Le désalignement
naît en amont — intention reformulée de travers, contraintes que seul l'utilisateur connaît,
périmètre jamais borné — et se constate en aval, quand le plan ne défend plus rien.

Ce skill couvre les deux bouts : il cadre avant, et il confronte après (Étape 7).
Sortie : `.claude/implementation/<slug>.brief.md`, apparié par slug au fichier de suivi
d'`implementation-tracker`.

Argument éventuel = sujet du chantier : il amorce le slug et oriente la reconnaissance.

---

## Règle directrice

**Ne jamais poser une question dont le dépôt contient la réponse.**

D'où l'ordre non négociable : **explorer → restituer → questionner les trous**. Explorer d'abord
est ce qui rend les questions spécifiques ; sauter l'Étape 1 ramène au questionnaire générique,
qui fatigue l'utilisateur et ne produit rien.

## Quand ne pas cadrer

Le cadrage a un coût. Il ne se justifie pas pour :

- une demande dont le périmètre tient dans un fichier,
- un correctif de bug déjà reproduit,
- une tâche que l'utilisateur a déjà décrite avec ses critères.

Dans ces cas : le dire en une ligne et passer directement au plan. **Sortie anticipée** également
si, après l'Étape 2, l'utilisateur valide la restitution sans correction et qu'aucune ambiguïté
n'est ouverte : proposer un brief minimal (intention + hors-périmètre) et enchaîner.

## Règle du sourçage

**Toute affirmation du brief est sourcée : dite par l'utilisateur, ou vérifiée dans le dépôt.**

Supposer n'est pas interdit — l'Étape 2 est une supposition assumée, et c'est la meilleure du
dispositif. La ligne de partage est **exposée / silencieuse** : une supposition affichée appelle
la réfutation, une supposition non marquée devient une vérité de référence que plus rien ne
remettra en cause.

- Les puces de `## Contraintes connues` et `## Signaux de dérive` portent leur source :
  `(dit)` ou `(dépôt: <chemin ou sha>)`. Une puce sans marqueur est une supposition — la retirer.
- Un trou se déclare `— non abordé`, ou part en `## Incertitudes à lever en plan`.
- **Combler un trou par plausibilité est interdit**, même quand la réponse paraît évidente.
- **Pas de comblement rétroactif** : une question restée sans réponse ne se résout pas d'elle-même
  trois tours plus tard. La reposer, ou la reporter en incertitude.

## Registre des ambiguïtés

Le registre **est le fichier brief**, pas la mémoire de la conversation — c'est là qu'elles
s'évaporent. Toute ambiguïté est appendue à `## Incertitudes à lever en plan` **au moment où elle
apparaît**, dans la formulation d'origine.

Chacune finit dans un de trois états :

| État | Sortie |
|---|---|
| **Levée** | réponse de l'utilisateur → déplacée dans la section concernée, retirée des incertitudes |
| **Tranchée** | arbitrage `AskUserQuestion` → décision écrite, retirée des incertitudes |
| **Reportée** | reste en `## Incertitudes à lever en plan` — mission explicite du plan |

**Disparaître silencieusement n'est pas un état.**

Marqueurs de détection : `references/grille-questions.md`, section « Détecter les ambiguïtés ».

---

## Étape 0 — Prérequis

```bash
date +%F
git rev-parse --is-inside-work-tree 2>/dev/null || echo "NON_GIT"
git branch --show-current
ls .claude/implementation/*.brief.md 2>/dev/null
```

Utiliser la date renvoyée par `date`, jamais l'inventer :
[Dates et listing](../implementation-tracker/references/contrat.md#dates-et-listing).

- `NON_GIT` → demander si l'utilisateur veut quand même un brief (non versionné). Attendre la réponse.
- `.claude/implementation/` absent → demander confirmation avant de créer l'arborescence.
- **Brief existant sur un sujet proche** → le lire, proposer de le reprendre ou d'en créer un
  nouveau. Ne jamais écraser sans accord.

## Étape 1 — Reconnaissance silencieuse

Objectif : savoir ce que le code répond déjà, pour ne demander que le reste. Aucune question ici,
et pas de narration fichier par fichier.

- `CLAUDE.md` du projet, `README`, conventions locales
- fichiers concernés par la demande
- `git log --oneline -20` sur la zone visée — les commits racontent les tentatives passées
- tests existants : ils encodent le comportement attendu

**Plafond** : pour une demande ciblée, une passe de recherche et cinq fichiers lus. Au-delà, c'est
du plan, pas du cadrage.

## Étape 2 — Restitution de la compréhension

L'étape la plus rentable : un malentendu se corrige ici en une phrase, au lieu d'être découvert
dans l'implémentation.

```
Ma lecture :
- Ce que je crois que tu veux : …
- Ce que je crois que fait le code aujourd'hui : … (au moins un fait daté ou nommé du dépôt)
- Ce que je m'attends à toucher : …
- Ce dont je ne suis pas sûr : …
```

Puis : **« Qu'est-ce qui est faux là-dedans ? »** Demander ce qui est faux, pas si c'est correct :
une question fermée récolte un « oui » poli, une ouverte récolte la correction.

**Contrainte de vérification** : la restitution doit citer au moins un fait concret du dépôt — un
commit, un fichier, un test, une fonction. Sans citation, l'Étape 1 n'a pas eu lieu : la refaire.

Puis **arrêter le slug**, tiré de l'argument ou du sujet. Il nomme le fichier et ne change plus :
**le brief fait autorité**, le fichier de suivi le reprendra tel quel. Forme et conséquence :
[Arborescence et nommage](../implementation-tracker/references/contrat.md#arborescence-et-nommage).

**Créer le brief en `statut: brouillon`** (gabarit : `references/gabarit-brief.md`), rempli de ce
qui est déjà établi. Il sert de registre à partir d'ici.

## Étape 3 — Questions ouvertes, une par tour

Puiser dans `references/grille-questions.md`. **Réservoir, pas checklist** : n'en tirer que les
axes que l'Étape 1 n'a pas couverts.

- **Une seule question par tour.** Une salve récolte des réponses bâclées.
- Ancrer dans le concret observé : « j'ai vu `TokenStore` réécrit deux fois — qu'est-ce qui a
  cassé ? » vaut mieux que « des contraintes particulières ? ».
- Écrire chaque réponse dans le brief au fil de l'eau, avec son marqueur de source.
- Une réponse ambiguë → l'appender aux incertitudes **immédiatement**.
- S'arrêter quand les réponses cessent d'apporter du neuf. Typiquement 3 à 6 questions.
- Une réponse qui ouvre une zone inconnue → creuser là, quitte à ignorer le reste de la grille.

**Axes prioritaires si le temps manque** : intention réelle, hors-périmètre, signaux de dérive.

## Étape 4 — Arbitrages fermés

Sur les seules ambiguïtés relevées aux Étapes 2-3, utiliser `AskUserQuestion`. Grouper plusieurs
questions dans un même appel est ici **permis** : ce sont des arbitrages à choix fermés, pas de
l'exploration — la règle « une question par tour » ne s'applique qu'à l'Étape 3.

Ne pas y recycler les questions ouvertes déjà posées. S'il n'y a rien à trancher, sauter l'étape.

## Étape 5 — Finalisation

**Contrôles avant de figer :**

- Chaque ambiguïté est levée, tranchée ou reportée — aucune n'a disparu.
- Chaque puce de contrainte porte son marqueur de source. Sans marqueur : retirer ou reposer.

Puis :

1. **Trancher la délégabilité** et l'écrire dans `execution:`, au frontmatter du brief — champ,
   valeurs et défaut :
   [Frontmatter](../implementation-tracker/references/contrat.md#frontmatter).

   `délégué` si les étapes prévisibles se borneront à des fichiers nommés, avec une commande de
   vérification chacune. `direct` sinon — et `direct` dès qu'il reste une incertitude reportée ou
   que `## Signaux de dérive` est vide : un exécutant en sous-agent n'a personne à qui poser la
   question, il tranchera seul, et sans signaux il n'a rien qui l'arrête.
2. Restituer les trois sections décisives — intention, hors-périmètre, incertitudes — et pointer
   le fichier pour le reste. Ne pas recopier le brief entier.
3. Sur validation : `statut: validé`. Le brief est figé.

Le brief tient en une page. S'il déborde, c'est un plan déguisé.

## Étape 6 — Passage au plan

**Proposer**, jamais enchaîner d'office :

> Brief écrit dans `.claude/implementation/<slug>.brief.md`. On passe en mode plan avec ça comme cadre ?

Sur accord : `EnterPlanMode`, en rappelant les critères de réussite, le hors-périmètre, les
signaux de dérive et les incertitudes à lever.

## Étape 7 — Confrontation plan ↔ brief

**Obligatoire, juste après `ExitPlanMode`.** C'est ici que le brief cesse d'être documentaire et
devient contraignant — sans cette étape, tout ce qui précède n'améliore que des probabilités.

Relire le brief et confronter point par point :

- **Critères de réussite** → chacun est servi par au moins une étape du plan ?
- **Hors-périmètre** → aucune étape ne l'entame ?
- **Signaux de dérive** → le plan en déclenche-t-il un ?
- **Incertitudes** → chacune tranchée par le plan, ou toujours ouverte ?

Sortie en trois lignes, pas un rapport. **Tout écart se dit**, même mineur : c'est exactement
l'information qui manquait jusqu'ici. Un plan qui sort du périmètre n'est pas corrigé d'office —
le signaler et laisser l'utilisateur trancher entre élargir le brief et resserrer le plan.

## Étape 8 — Passage au suivi

Le plan est validé et confronté : il faut maintenant un fichier de suivi, sinon tout ce travail
vit dans une conversation qui se fermera. **Le proposer explicitement** — `implementation-tracker`
ne s'invoque qu'à la main, le modèle ne peut pas l'appeler :

> Plan validé et conforme au brief. Ouvre le suivi avec `/implementation-tracker` pour figer les
> étapes et démarrer — il reprendra ce brief et ce plan.

---

## Articulation avec implementation-tracker

Le brief précède le suivi et ne le remplace pas : le brief porte l'intention et ses bornes, figées ;
le suivi porte les étapes et leur avancement, mis à jour en continu. Ce qui fait foi en cas de
divergence, et où s'écrit un périmètre qui change réellement :
[Autorité et divergence](../implementation-tracker/references/contrat.md#autorité-et-divergence).

Ce que le suivi reprend du brief à sa création (Étape 2 d'`implementation-tracker`) :
`## Objectif et périmètre` — symptôme, but, critères, hors-périmètre et **signaux de dérive**, ces
derniers devenant un déclencheur d'arrêt pendant l'implémentation.
