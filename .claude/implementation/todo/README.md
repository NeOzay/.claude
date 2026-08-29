# todo/

Registres **vivants** du dépôt : ce qui reste à faire, et que rien d'autre ne retient.

Symétrique de `done/`, mais de nature opposée. `done/` porte des **archives figées** — un suivi,
un brief, un rapport d'audit, tous datés au jour de la clôture, qu'on ne rouvre que pour comprendre
un chantier passé. Ce qui vit ici est **relu et modifié** : une entrée s'y ajoute, s'y corrige, en
sort quand elle est soldée. Rien n'y est archivé.

## Trois répertoires-listes

Un répertoire = une liste, **un fichier = une entrée**, et `.list/contract.toml` déclare ce qu'une
entrée doit porter. Tout `*.md` à la racine d'une liste est une entrée, sans exception ; tout le
reste vit sous `.list/`.

- **`technical-debt/`** — la dette constatée et non résolue. Alimenté à la clôture d'un chantier,
  par l'orchestrateur, une seule fois. Procédure complète, contrat et règle de solde :
  `skills/implementation-tracker/references/dette.md`.
- **`technical-debt-solde/`** — ce qui a été soldé, avec la commande exécutée qui l'établit.
- **`technical-debt-ecarte/`** — ce qui est sorti du registre **sans avoir été payé** : devenu
  sans objet, doublon d'une autre entrée, ou n'ayant jamais été une dette. Chaque entrée porte son
  motif et la preuve qui l'établit. Existante et **vide** : une liste vide est valide.

Une entrée ne change jamais d'état par un champ, mais **par un `move` d'une liste vers l'autre**,
ce qui préserve son historique jusqu'à son commit de création.

```bash
list-dir list .claude/implementation/todo/technical-debt --sort date
list-dir validate .claude/implementation/todo/technical-debt --filled
```

Le répertoire a vocation à en accueillir d'autres — `road-map/` pour les idées d'amélioration, que
`technical-debt/` exclut par construction.

## Lecture

Rien ici n'est lu automatiquement par le pipeline. Ces listes se consultent sur demande,
typiquement en cherchant un sujet de chantier — à une exception près, elle aussi manuelle :
`/debt-review` relit `technical-debt/` entrée par entrée pour vérifier qu'elle tient encore, et
écrit dans les trois listes après arbitrage.
