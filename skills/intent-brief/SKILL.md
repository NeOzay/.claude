---
name: intent-brief
description: >
  Cadre l'intention de l'utilisateur AVANT le mode plan et produit un brief persistant
  (.claude/implementation/<slug>.brief.md) : intention réelle, critères de réussite,
  hors-périmètre, contraintes non devinables, signaux de dérive. Se déclenche sur "cadrer",
  "brief", "avant de planifier", "aligner l'intention", ou quand une demande de
  planification/refonte arrive sans brief existant. Alimente implementation-tracker.
argument-hint: "[sujet du chantier]"
---

# Intent Brief

Le mode plan produit un bon plan **pour la demande telle qu'il l'a comprise**. Le désalignement naît
en amont — intention floue ou reformulée de travers, contraintes que seul l'utilisateur connaît,
périmètre jamais borné — et se constate en aval, quand le plan ne défend plus rien.

Ce skill cadre l'amont, et rien d'autre. Il ne planifie pas et ne relit pas le plan : le plan se
construit dans `implementation-tracker`, qui le fait relire par `plan-reviewer` avant de le
présenter. Sortie : `.claude/implementation/<slug>.brief.md`, apparié par slug au fichier de suivi
d'`implementation-tracker`.

Argument éventuel = sujet du chantier : il amorce le slug et oriente la reconnaissance.

---

## Règle directrice

**Ne jamais poser une question dont le dépôt contient la réponse.**

D'où l'ordre non négociable : **explorer → questionner → écrire**. Explorer d'abord est ce qui rend
les questions spécifiques ; sauter la Phase 1 ramène au questionnaire générique, qui fatigue
l'utilisateur et ne produit rien. Écrire après les échanges donne à l'utilisateur un fichier qu'il
relit dans son éditeur, en entier, au lieu d'une lecture à réfuter phrase à phrase dans la
conversation.

Un message ne rend que ce que l'utilisateur ne voit pas déjà dans son éditeur :
[Messages à l'utilisateur](../implementation-tracker/references/contrat.md#messages-à-lutilisateur).

## Quand ne pas cadrer

Le cadrage a un coût. Il ne se justifie pas pour :

- une demande dont le périmètre tient dans un fichier,
- un correctif de bug déjà reproduit,
- une tâche que l'utilisateur a déjà décrite avec ses critères.

Dans ces cas : le dire en une ligne et renvoyer directement à `/implementation-tracker`, qui sait
ouvrir un chantier sans brief. **Sortie anticipée** également si, au terme des échanges, aucune
ambiguïté n'est ouverte et que l'utilisateur n'a rien à ajouter : écrire un brief minimal —
intention et hors-périmètre, les autres sections à `— non abordé` — et passer à la Phase 6.

## Règle du sourçage

**Toute affirmation du brief est sourcée : dite par l'utilisateur, ou vérifiée dans le dépôt.**

Supposer n'est pas interdit — le brief écrit à la Phase 3 expose ce que l'agent a compris, pour
que l'utilisateur le corrige. La ligne de partage est **exposée / silencieuse** : une supposition
affichée appelle la réfutation, une supposition non marquée devient une vérité de référence que
plus rien ne remettra en cause.

- Les puces de `## Contraintes connues` et `## Signaux de dérive` portent leur source :
  `(dit)` ou `(dépôt: <chemin ou sha>)`. Une puce sans marqueur est une supposition — la retirer.
- Un trou se déclare `— non abordé`, ou part en `## Incertitudes à lever en plan`.
- **Combler un trou par plausibilité est interdit**, même quand la réponse paraît évidente.
- **Pas de comblement rétroactif** : une question restée sans réponse ne se résout pas d'elle-même
  trois tours plus tard. La reposer, ou la reporter en incertitude.

## Registre des ambiguïtés

Le registre **est le fichier brief**, pas la mémoire de la conversation — c'est là qu'elles
s'évaporent. Pendant les échanges, le fichier n'existe pas encore : une ambiguïté se nomme dans le
tour où elle apparaît, et toutes celles qui restent ouvertes entrent à
`## Incertitudes à lever en plan` dès l'écriture, dans leur formulation d'origine. Ensuite, chacune
y est appendue **au moment où elle apparaît**.

Chacune finit dans un de trois états :

| État | Sortie |
|---|---|
| **Levée** | réponse de l'utilisateur → déplacée dans la section concernée, retirée des incertitudes |
| **Tranchée** | arbitrage `AskUserQuestion` → décision écrite, retirée des incertitudes |
| **Reportée** | reste en `## Incertitudes à lever en plan` — mission explicite du plan |

**Disparaître silencieusement n'est pas un état.**

Marqueurs de détection : `references/grille-questions.md`, section « Détecter les ambiguïtés ».

---

## Phase 0 — Prérequis

```bash
date +%F
git rev-parse --is-inside-work-tree 2>/dev/null || echo "NON_GIT"
git branch --show-current
ls .claude/implementation/*.brief.md 2>/dev/null
```

Utiliser la date renvoyée par `date`, jamais l'inventer :
[Dates et listing](../implementation-tracker/references/contrat.md#dates-et-listing).

- `NON_GIT` → demander si l'utilisateur veut quand même un brief (non versionné). Attendre la
  réponse.
- `.claude/implementation/` absent → demander confirmation avant de créer l'arborescence.
- **Brief existant sur un sujet proche** → le lire, proposer de le reprendre ou d'en créer un
  nouveau. Ne jamais écraser sans accord.

## Phase 1 — Reconnaissance silencieuse

Objectif : savoir ce que le code répond déjà, pour ne demander que le reste. Aucune question ici,
et pas de narration fichier par fichier.

- **l'entrée de `road-map/` dont part la demande**, s'il y en a une : c'est un point de départ déjà
  écrit, et sa section `Références` **est** le début de cette reconnaissance. Retenir son `id` — il
  ira dans le `road-map` du futur suivi, et c'est lui qui fera sortir l'entrée à la clôture
  ([Road-map](../implementation-tracker/references/road-map.md#le-champ-road-map))
- `CLAUDE.md` du projet, `README`, conventions locales
- **les Shadow-skills du sujet** : `shadow-skill tags`, puis `shadow-skill cherche <mots du
  sujet>`. Charger par `shadow-skill charge <nom>` ceux dont le `when-to-load` décrit la demande :
  ils disent ce que le domaine attend, et donc ce qui reste à demander
- fichiers concernés par la demande
- `git log --oneline -20` sur la zone visée — les commits racontent les tentatives passées
- tests existants : ils encodent le comportement attendu

**Plafond** : pour une demande ciblée, une passe de recherche et cinq fichiers lus. Au-delà, c'est
du plan, pas du cadrage.

## Phase 2 — Échanges

Puiser dans `references/grille-questions.md`. **Réservoir, pas checklist** : n'en tirer que les
axes que la Phase 1 n'a pas couverts. Aucun fichier ne s'écrit à ce stade.

- **Deux questions au plus par tour, regroupées par thème.** Une salve récolte des réponses
  bâclées ; deux questions d'un même thème se répondent d'un même mouvement.
- Des questions ouvertes, ancrées dans le concret observé : « j'ai vu `TokenStore` réécrit deux
  fois — qu'est-ce qui a cassé ? » vaut mieux que « des contraintes particulières ? ».
- **Contrainte de vérification** : le premier tour cite au moins un fait concret du dépôt — un
  commit, un fichier, un test, une fonction. Sans citation, la Phase 1 n'a pas eu lieu : la
  refaire.
- Une réponse ambiguë → la nommer dans ce tour : elle entrera au registre à l'écriture.
- S'arrêter quand les réponses cessent d'apporter du neuf. Typiquement 3 à 6 questions.
- Une réponse qui ouvre une zone inconnue → creuser là, quitte à ignorer le reste de la grille.

Critères de réussite et signaux de dérive ne se demandent pas ici : l'agent les propose à la
Phase 5.

**Axes prioritaires si le temps manque** : intention réelle, hors-périmètre.

## Phase 3 — Écriture

**Choisir le slug**, tiré de l'argument ou du sujet. Forme :
[Arborescence et nommage](../implementation-tracker/references/contrat.md#arborescence-et-nommage).
Jusqu'à la validation, il se renomme — le fichier et le champ `slug` ensemble ; validé, il ne
change plus, et le fichier de suivi le reprendra tel quel.

**Poser le brief** depuis sa semence, qui le crée en brouillon :

```bash
gabarit new brief .claude/implementation/<slug>.brief.md
gabarit contract brief
```

Le contrat dit ce que chaque champ et chaque section attend : le lire, puis écrire tout ce que les
échanges ont établi, chaque puce avec sa source, et toutes les ambiguïtés restées ouvertes aux
incertitudes. Critères de réussite et signaux de dérive restent au Marqueur jusqu'à la Phase 5.

Le message donne le chemin du brief et ses incertitudes, rien d'autre : le reste, l'utilisateur le
lit dans le fichier.

## Phase 4 — Corrections et arbitrages

L'utilisateur corrige le brief : il ajuste, résout une incertitude, exige. L'agent reporte chaque
correction dans le fichier, avec sa source. Chaque message qui modifie le brief redonne son chemin
et les incertitudes restantes, rien d'autre.

Les incertitudes restantes dont les réponses sont fermées se tranchent par `AskUserQuestion`, en
un seul appel qui les groupe toutes : ce sont des arbitrages, pas de l'exploration. Ne pas y
recycler les questions ouvertes des échanges. S'il n'y a rien à trancher, passer.

## Phase 5 — Critères et signaux

L'agent propose les critères de réussite et les signaux de dérive, tirés des échanges et du dépôt ;
l'utilisateur les décide. Ce qu'un bon critère et un bon signal portent :
`references/grille-questions.md`, section « Critères et signaux ». Ceux que l'utilisateur retient
s'écrivent au brief.

## Phase 6 — Validation

**Contrôles avant de figer :**

- Chaque ambiguïté est levée, tranchée ou reportée — aucune n'a disparu.
- Chaque puce de contrainte porte son marqueur de source. Sans marqueur : retirer ou reposer.

Puis :

1. **Vérifier le brief** contre sa semence :

   ```bash
   gabarit check .claude/implementation/<slug>.brief.md --filled
   ```

   Un échec nomme ce qui reste à remplir : le brief ne se propose pas à la validation tant qu'il
   n'est pas conforme. Un axe resté vide s'écrit `— non abordé`, jamais une supposition.
2. Sur validation : `statut` passe à `validé`. Le brief est figé, slug compris.

Le brief tient en une page. S'il déborde, c'est un plan déguisé.

## Phase 7 — Passage au suivi

Le brief est figé : il lui faut maintenant un fichier de suivi, sinon tout ce travail vit dans une
conversation qui se fermera. **Le proposer explicitement** — `implementation-tracker` ne s'invoque
qu'à la main, le modèle ne peut pas l'appeler :

> Brief validé dans `.claude/implementation/<slug>.brief.md`.
>
> Ouvre le suivi avec `/implementation-tracker` pour figer les étapes et démarrer — il reprendra
> ce brief.

C'est la sortie unique de ce skill. Le plan se construit dans le tracker, qui le fait relire par
`plan-reviewer` avant de le présenter : ni l'un ni l'autre ne se fait ici.

---

## Articulation avec implementation-tracker

Le brief précède le suivi et ne le remplace pas : le brief porte l'intention et ses bornes, figées ;
le suivi porte les étapes et leur avancement, mis à jour en continu.

La coupure est nette : **ce skill s'arrête au brief validé.** Le plan, sa relecture par
`plan-reviewer` et le figeage des étapes appartiennent tous à la Phase 2 d'`implementation-tracker`.
Un brief qui déborde sur le plan reprend le travail que le tracker refera — et deux versions d'une
même chose ne peuvent que diverger.

Ce qui fait foi en cas de divergence, et où s'écrit un périmètre qui change réellement :
[Autorité et divergence](../implementation-tracker/references/contrat.md#autorité-et-divergence).

Ce que le suivi reprend du brief à sa création (Phase 2 d'`implementation-tracker`) : toute la
section `## Objectif et périmètre`, dont la semence `suivi` déclare les blocs. Les **signaux de
dérive** y deviennent un déclencheur d'arrêt pendant l'implémentation.
