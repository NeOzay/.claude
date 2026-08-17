# todo/

Registres **vivants** du dépôt : ce qui reste à faire, et que rien d'autre ne retient.

Symétrique de `done/`, mais de nature opposée. `done/` porte des **archives figées** — un suivi,
un brief, un rapport d'audit, tous datés au jour de la clôture, qu'on ne rouvre que pour comprendre
un chantier passé. Les fichiers d'ici sont **relus et modifiés** : une entrée s'y ajoute, s'y
corrige, en sort quand elle est soldée. Ils ne sont jamais archivés.

- **`technical-debt.md`** — la dette constatée et non résolue. Alimenté à la clôture d'un chantier,
  par l'orchestrateur, une seule fois. Procédure complète, gabarit d'entrée et règle de solde :
  `skills/implementation-tracker/references/dette.md`.
- **`technical-debt-solde.md`** — ce qui a été soldé, avec la commande exécutée qui l'établit.
- **`technical-debt-ecarte.md`** — ce qui est sorti du registre **sans avoir été payé** : devenu
  sans objet, doublon d'une autre entrée, ou n'ayant jamais été une dette. Chaque entrée porte son
  motif et la preuve qui l'établit. Créé à la première revue qui en écarte une.

Le répertoire a vocation à en accueillir d'autres — `road-map.md` pour les idées d'amélioration,
que `technical-debt.md` exclut par construction.

Rien ici n'est lu automatiquement par le pipeline. Ces fichiers se consultent sur demande,
typiquement en cherchant un sujet de chantier — à une exception près, elle aussi manuelle :
`/debt-review` relit `technical-debt.md` entrée par entrée pour vérifier qu'il tient encore, et
écrit dans les trois registres après arbitrage.
