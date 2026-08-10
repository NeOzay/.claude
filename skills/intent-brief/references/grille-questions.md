# Grille de questions — cadrage d'intention

Réservoir d'axes, pas checklist. N'utiliser que ce que la reconnaissance (Étape 1) n'a pas
couvert. Une question par tour. Toujours ancrer dans ce qui a été observé dans le dépôt.

Les axes sont ordonnés par rendement décroissant sur l'alignement.

---

## 1. Intention réelle

Le problème vécu, pas la solution demandée. Une demande arrive presque toujours déjà traduite
en solution ; la traduction peut être le désalignement à elle seule.

- « Qu'est-ce qui t'a amené à vouloir ça maintenant ? »
- « C'est quoi le symptôme que tu constates ? »
- « Si le problème disparaissait par magie sans ce changement, ça te conviendrait ? »

**Signal fort** : la réponse décrit un symptôme que la solution demandée ne traite pas. Le dire.

---

## 2. Hors-périmètre

Le rempart contre le scope creep. Le demander **explicitement** : personne ne le formule
spontanément.

- « Qu'est-ce qu'on ne touche pas dans ce chantier, même si c'est tentant ? »
- « J'ai vu que <X> est dans un sale état à côté — dedans ou dehors ? »
- « Si je trouve un bug adjacent, je le corrige ou je le signale ? »

---

## 3. Signaux de dérive

L'axe le plus efficace, et le plus rarement posé. Donne un **test de fausseté**, pas seulement
une cible : utilisable en cours d'implémentation pour détecter l'erreur tôt.

- « À quoi tu verrais, en lisant le diff, que je me suis trompé de direction ? »
- « Quel genre de solution serait techniquement correcte mais quand même la mauvaise ? »
- « Si je te proposais d'ajouter une couche d'abstraction ici, ce serait bon signe ou mauvais ? »

---

## 4. Critères de réussite

Observables. « Que ça marche mieux » n'est pas un critère.

- « Comment tu sauras que c'est fini ? »
- « Quelle commande tu lances pour vérifier ? »
- « Il y a un comportement précis qui doit changer, visible d'où ? »

---

## 5. Historique et tentatives

Invisible dans le code, souvent décisif. Les commits donnent des pistes ; la raison de l'échec
n'y est presque jamais.

- « L'historique montre <X> réécrit deux fois — qu'est-ce qui a cassé ? »
- « Il y a une approche que tu as déjà essayée et abandonnée ? »
- « Il y a une raison non évidente pour laquelle c'est fait comme ça aujourd'hui ? »

---

## 6. Intouchable

- « Il y a des fichiers, des API ou des comportements que je ne dois pas bouger ? »
- « Ce module a des consommateurs hors dépôt ? »
- « Ce test qui échoue déjà, il est censé échouer ? »

---

## 7. Existant à réutiliser

Un modèle qui ne connaît pas l'existant le recrée. Coût invisible et récurrent.

- « Il y a déjà un utilitaire pour ça quelque part ? »
- « Tu préfères que j'étende <module existant> ou que je crée à côté ? »

---

## 8. Rejets a priori

- « Il y a une approche que tu refuses d'emblée ? »
- « Une dépendance à ne pas ajouter ? »
- « Tu as une préférence de forme sur laquelle je risque de me tromper ? »

---

## 9. Granularité et ambition

Calibre l'effort. Utile quand la demande peut se lire à deux échelles très différentes.

- « Correctif minimal ou refonte de la zone ? »
- « Tu veux quelque chose d'utilisable ce soir, ou qui tienne six mois ? »

---

## Détecter les ambiguïtés

Une ambiguïté ne s'annonce pas : elle passe pour une réponse claire. Ces marqueurs la trahissent.
Chaque occurrence s'inscrit au registre (voir SKILL.md) au moment où elle apparaît.

| Marqueur | Exemple | Question de levée |
|---|---|---|
| Verbe non défini | « nettoyer », « simplifier », « améliorer » | « nettoyer, ça veut dire quoi concrètement ici ? » |
| Comparatif sans référence | « plus rapide », « plus robuste » | « plus rapide que quoi, mesuré comment ? » |
| Pronom sans antécédent | « il faut que ça marche avec » | « ça = quel élément ? » |
| Énumération ouverte | « etc. », « entre autres », « et compagnie » | « qu'est-ce qu'il y a derrière le "etc." ? » |
| Quantificateur flou | « la plupart », « souvent », « en général » | « ça vaut pour quels cas exactement ? » |
| Adjectif d'appréciation | « propre », « correct », « acceptable » | « à quoi tu le reconnaîtrais dans le diff ? » |
| Modal ambigu | « ça devrait pouvoir » | « exigence ou souhait ? » |

**Cas particulier : l'ambiguïté de périmètre.** « Refais le module d'auth » ne dit pas si les
appelants sont dedans. C'est la plus coûteuse et la plus fréquente — la lever en priorité.

**Ne pas confondre** ambiguïté et imprécision assumée. « Je ne sais pas encore » est une réponse
valide : elle part en `## Incertitudes à lever en plan`, état *reportée*. Insister est inutile.

---

## Anti-patterns

À ne jamais poser :

- Ce que la lecture du dépôt donne — « c'est quel langage ? », « il y a des tests ? »
- Des questions fermées sur la compréhension — « c'est bien ça ? » récolte un « oui » poli
- Des salves — six questions d'un coup produisent six réponses bâclées
- Des questions de plan — « on commence par quel fichier ? » relève du mode plan, pas du cadrage
