---
slug: revue-dette
titre: Skill manuelle de revue du registre de dette
statut: validé
execution: direct
créé: 2026-08-16
---

## Intention

**Symptôme** : « Actuellement, il n'y a aucun système pour vérifier si une dette est encore
pertinente. » (dit)
**But** : un nouveau skill à déclenchement manuel qui vérifie la pertinence des entrées du
registre. (dit)

## Critères de réussite

Établis par une passe réelle sur le registre du dépôt (14 entrées au 2026-08-16).

- chaque entrée du registre reçoit **exactement une** des sept catégories, aucune omise : le compte
  des entrées classées dans le rapport égale `grep -c '^## ' technical-debt.md`
- le script de tri, lancé sur le rapport, rend les entrées **regroupées par catégorie puis par
  date**, sans en perdre : même compte avant et après
- après arbitrage, `grep -n 'Dernière vérification' technical-debt.md` porte la date du jour
  obtenue par `date +%F`, et aucune entrée arbitrée ne subsiste sans son traitement
- `git status --short` après une passe ne montre que des chemins sous `.claude/implementation/` :
  aucun fichier de code touché

## Hors-périmètre

- **Le skill ne corrige aucun code.** Tout correctif, même trivial, passe par
  `implementation-tracker` — « pour éviter les mauvaises surprises » (dit)
- pas d'invocation automatique : déclenchement manuel uniquement (dit)
- le skill n'invente pas de dette : il statue sur les entrées existantes du registre (dit)

## Signaux de dérive

- si le skill se met à écrire dans le code plutôt qu'à instruire un verdict, c'est raté (dit)
- si le modèle se met à trier lui-même au lieu d'étiqueter, le script n'a plus de raison d'être et
  le tri redevient peu fiable (dit)
- si une entrée sort du registre sans atterrir ni dans `technical-debt-solde.md` ni dans le fichier
  de trace, la trace est perdue — ce que le dispositif existe pour éviter (dit)

## Contraintes connues de l'utilisateur

- **Déclenchement** : manuel, pas d'invocation par le modèle (dit) — cohérent avec
  `implementation-tracker` et `intent-brief`, tous deux `disable-model-invocation: true`
  (dépôt: skills/implementation-tracker/SKILL.md:8)
- **Le pipeline n'ouvre jamais le registre de lui-même** : il l'alimente à la clôture,
  l'utilisateur le consulte (dépôt: skills/implementation-tracker/references/dette.md:155)
- **La procédure de solde existe déjà** : retrait du registre, déplacement en fin de
  `technical-debt-solde.md`, et preuve par commande exécutée avec sa sortie réelle — sans quoi
  l'entrée reste (dépôt: skills/implementation-tracker/references/dette.md:130-146)
- **La ligne de tête prévoit déjà ce geste** : « Dernière vérification » s'actualise « à chaque
  fois qu'on relit le registre entrée par entrée pour vérifier qu'il tient encore » — sans qu'aucun
  skill ne le fasse (dépôt: skills/implementation-tracker/references/dette.md:70-72)
- **Une entrée aggravée** reste en place, son **Constat** mis à jour et redaté
  (dépôt: skills/implementation-tracker/references/dette.md:148-149)
- **Une entrée se référence par son intitulé**, pas par un numéro
  (dépôt: skills/implementation-tracker/references/dette.md:76-78)
- **Le skill met à jour tous les registres** une fois l'arbitrage rendu (dit)
- **`non pertinent` et `doublon` sont tracés dans un fichier à part** : ne pas perdre la trace,
  ne pas polluer `technical-debt-solde.md` (dit)
- **`aggravée` se marque dans le titre de l'entrée** — mention `(aggravée)` (dit)
- **Le rapport de revue est archivé**, pas jeté (dit) — `done/` porte les archives figées
  (dépôt: skills/implementation-tracker/references/contrat.md:36-40)

- **Un verdict par entrée, puis arbitrage de l'utilisateur** : le skill ne solde pas de sa propre
  autorité (dit)
- **Le tri porte sur la sortie du modèle, pas sur le registre** : le modèle écrit son avis sur les
  dettes dans un fichier, qu'un **script** trie ensuite (dit)
- **Rôle du script** : « regrouper par catégorie puis par date les dettes du fichier — c'est une
  tâche compliquée pour un modèle » (dit). Le modèle étiquette, le script regroupe. Un script
  appelé depuis un skill se référence par **chemin absolu ancré dans la skill**
  (dépôt: skills/implementation-tracker/references/contrat.md:183-186)
- **Catégories retenues** — trois proposées par l'utilisateur (dit) : `non pertinent` (les éléments
  cités n'existent plus), `à solder` (la dette a été payée dans un autre chantier), `pertinent`
  (la dette est identifiable dans le code) ; quatre ajoutées sur arbitrage (dit) : `invérifiable en
  revue`, `aggravée`, `pas une dette`, `doublon`.

## Incertitudes à lever en plan

- sortie d'une entrée `pas une dette` : `road-map.md` est annoncé par `dette.md:48` mais n'existe
  pas dans `todo/` — le créer dans ce chantier, ou verser au fichier de trace ?
- nom d'archive du rapport : `done/` est nommé `<AAAA-MM-DD>-<slug>.*` et une revue n'a pas de slug
  de chantier
- nom et emplacement du fichier de trace `non pertinent` / `doublon`, et son entrée dans
  l'arborescence du contrat
- marquer `(aggravée)` dans le titre change l'intitulé, qui est **la clé de référence d'une entrée**
  (`dette.md:76-78`) et sert au dédoublonnage à la clôture (`dette.md:119`) : à concilier
