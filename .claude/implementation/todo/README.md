# todo/

Registres **vivants** du dépôt : ce qui reste à faire, et que rien d'autre ne retient.

Symétrique de `done/`, mais de nature opposée. `done/` porte des **archives figées** — un suivi,
un brief, un rapport d'audit, tous datés au jour de la clôture, qu'on ne rouvre que pour comprendre
un chantier passé. Ce qui vit ici est **relu et modifié** : une entrée s'y ajoute, s'y corrige, en
sort quand elle est soldée. Rien n'y est archivé.

## Deux familles, six répertoires-listes

Un répertoire = une liste, **un fichier = une entrée**, et `.list/contract.toml` déclare ce qu'une
entrée doit porter. Tout `*.md` à la racine d'une liste est une entrée, sans exception ; tout le
reste vit sous `.list/`.

Chaque famille tient en trois listes : celle qui est active, et deux sorties. Une entrée ne change
jamais d'état par un champ, mais **par un `move` d'une liste vers l'autre**, ce qui préserve son
historique jusqu'à son commit de création.

### La dette — ce qu'on a constaté

Procédure complète, contrat et règle de solde :
`skills/implementation-tracker/references/dette.md`.

- **`technical-debt/`** — la dette constatée et non résolue. Alimenté à la clôture d'un chantier,
  par l'orchestrateur, une seule fois.
- **`technical-debt-solde/`** — ce qui a été soldé, avec la commande exécutée qui l'établit.
- **`technical-debt-ecarte/`** — ce qui est sorti du registre **sans avoir été payé** : devenu
  sans objet, doublon d'une autre entrée, ou n'ayant jamais été une dette. Chaque entrée porte son
  motif et la preuve qui l'établit.

### La road-map — ce qu'on veut faire

Rôle, frontière avec la dette et mécanique de sortie :
`skills/implementation-tracker/references/road-map.md`.

- **`road-map/`** — les tâches qu'on veut accomplir : correction d'une dette devenue gênante, idée
  rencontrée pendant un chantier. Un pense-bête. Alimenté **à la demande de l'utilisateur, et par
  personne d'autre** — c'est ce qui la distingue du registre de dette. Une entrée sert de point de
  départ à un chantier : elle référence contexte, code, entrées de dette, chantiers archivés.
- **`road-map-fait/`** — ce qu'un chantier a porté, avec son slug et son archive dans `done/`.
  L'entrée y est déplacée à la clôture, quand le suivi du chantier porte son `id` en `road-map:`.
- **`road-map-ecarte/`** — ce qu'on a cessé de vouloir : sans objet, doublon, faite ailleurs, plus
  voulue. Le motif suffit ; **aucune preuve exécutée n'y est exigée**, contrairement à la dette —
  une tâche à laquelle on renonce n'établit rien dans le dépôt.

Une liste existante et **vide** est valide : `technical-debt-ecarte/` l'a été longtemps, les deux
sorties de road-map le sont aujourd'hui.

```bash
list-dir list .claude/implementation/todo/technical-debt --sort date
list-dir validate .claude/implementation/todo/road-map --filled
```

## Lecture

Rien ici n'est lu automatiquement par le pipeline. Ces listes se consultent sur demande,
typiquement en cherchant un sujet de chantier — à une exception près, elle aussi manuelle :
`/debt-review` relit `technical-debt/` entrée par entrée pour vérifier qu'elle tient encore, et
écrit dans les trois listes de dette après arbitrage. La road-map n'a pas d'équivalent : rien ne la
relit.

Le pipeline y **écrit** en revanche, à un seul moment et dans deux listes : la clôture d'un chantier
alimente `technical-debt/` de ce qu'il laisse derrière lui, et déplace vers `road-map-fait/`
l'entrée dont il était parti. Écrire n'est pas lire, mais l'omettre laisserait croire que ces
répertoires sont hors d'atteinte du pipeline.
