# Grille de questions — cadrage d'intention

Réservoir d'axes, pas checklist. N'utiliser que ce que la reconnaissance (Phase 1) n'a pas
couvert. Deux questions au plus par tour, regroupées par thème, toujours ancrées dans ce qui a été
observé dans le dépôt.

---

## Axes prioritaires

### 1. Intention réelle

Le problème vécu, pas la solution demandée. Une demande arrive presque toujours déjà traduite
en solution ; la traduction peut être le désalignement à elle seule.

- « Qu'est-ce qui t'a amené à vouloir ça maintenant ? »
- « C'est quoi le symptôme que tu constates ? »
- « Si le problème disparaissait par magie sans ce changement, ça te conviendrait ? »

**Signal fort** : la réponse décrit un symptôme que la solution demandée ne traite pas. Le dire.

### 2. Hors-périmètre

Le rempart contre le scope creep. Le demander **explicitement** : personne ne le formule
spontanément.

- « Qu'est-ce qu'on ne touche pas dans ce chantier, même si c'est tentant ? »
- « J'ai vu que <X> est dans un sale état à côté — dedans ou dehors ? »
- « Si je trouve un bug adjacent, je le corrige ou je le signale ? »

---

## Axes secondaires

Une question chacun, si le chantier s'y prête :

- **Historique** — « l'historique montre <X> réécrit deux fois : qu'est-ce qui a cassé ? »
  (invisible dans le code, souvent décisif)
- **Intouchable** — « ce module a des consommateurs hors dépôt ? »
- **Réutiliser** — « tu préfères que j'étende <module existant> ou que je crée à côté ? »
  (un modèle qui ne connaît pas l'existant le recrée)
- **Rejets a priori** — « une approche ou une dépendance que tu refuses d'emblée ? »
- **Ambition** — « correctif minimal ou refonte de la zone ? »

---

## Critères et signaux

Ils ne se demandent pas aux échanges : l'agent les propose à la fin du cadrage (Phase 5), tirés de
ce que les échanges et le dépôt ont établi, et l'utilisateur les décide. Demandés d'emblée, ils
récoltent une réponse générique ; proposés, ils se corrigent.

- **Signaux de dérive** — l'axe le plus efficace : un **test de fausseté**, pas seulement une
  cible, utilisable en cours d'implémentation pour détecter l'erreur tôt. Chaque signal proposé
  répond à « à quoi verrait-on, en lisant le diff, que le chantier part dans la mauvaise
  direction ? » ou à « quelle solution serait techniquement correcte, mais la mauvaise ? ».
- **Critères de réussite** — une commande qui dit que c'est fini, plutôt qu'une phrase : une
  commande se rejoue.

---

## Détecter les ambiguïtés

Une ambiguïté ne s'annonce pas : elle passe pour une réponse claire. Ces marqueurs la trahissent.
Chaque occurrence s'inscrit au registre (voir SKILL.md) au moment où elle apparaît.

| Marqueur | Exemple | Question de levée |
|---|---|---|
| Verbe non défini | « nettoyer », « simplifier », « améliorer » | « nettoyer, ça veut dire quoi concrètement ici ? » |
| Comparatif sans référence | « plus rapide », « plus robuste » | « plus rapide que quoi, mesuré comment ? » |
| Pronom sans antécédent | « il faut que ça marche avec » | « ça = quel élément ? » |
| Énumération ouverte | « etc. », « entre autres » | « qu'est-ce qu'il y a derrière le "etc." ? » |
| Quantificateur flou | « la plupart », « souvent », « en général » | « ça vaut pour quels cas exactement ? » |
| Adjectif d'appréciation | « propre », « correct », « acceptable » | « à quoi tu le reconnaîtrais dans le diff ? » |
| Modal ambigu | « ça devrait pouvoir » | « exigence ou souhait ? » |

**Cas particulier : l'ambiguïté de périmètre.** « Refais le module d'auth » ne dit pas si les
appelants sont dedans. C'est la plus coûteuse et la plus fréquente — la lever en priorité.

**Ne pas confondre** ambiguïté et imprécision assumée. « Je ne sais pas encore » est une réponse
valide : elle part en `## Incertitudes à lever en plan`, état *reportée*. Insister est inutile.
