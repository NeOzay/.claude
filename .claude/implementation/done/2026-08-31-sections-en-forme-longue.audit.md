---
slug: sections-en-forme-longue
---

## 2026-08-31 — clôture — `752449e`

**Verdict** : RÉSERVES

### Vérifications exécutées

- `uvx pytest skills/list-dir/scripts/tests -q` → **307 passed** en 8,47 s, 0 échec
- `uvx ruff check scripts` (depuis `skills/list-dir`) → **All checks passed!**
- `list-dir validate .claude/implementation/todo/technical-debt` → 30 élément(s) conformes
- `list-dir validate .claude/implementation/todo/technical-debt-solde` → 16 élément(s) conformes
- `list-dir validate .claude/implementation/todo/technical-debt-ecarte` → 2 élément(s) conformes
- `list-dir derive … --template review` puis `list-dir validate <liste jetable>` → 30 fiches
  dérivées, 30 élément(s) conformes
- `list-dir contract .claude/implementation/todo/technical-debt` → forme longue, une
  `description` par section
- `list-dir contract --def technical-debt` → forme longue (le renvoi du message d'erreur est
  effectivement exécutable)
- `list-dir contract … --template review` → gabarit migré en forme longue
- `list-dir defs` → liste les 3 définitions (la seconde piste du message d'erreur tient)
- `list-dir contract <liste à l'ancien format>` (contrat fabriqué pour l'occasion) → code 1,
  message de migration citant `« list-dir contract --def vieux-registre »` et `« list-dir defs »`
- `list-dir validate <même liste>` → même message, code 1 (l'ancien format échoue partout, pas
  seulement sur `contract`)
- `list-dir init` + `list-dir new` sur une liste jetable → élément posé avec `## Constat` et
  `<À REMPLIR>`
- `grep -rn 'optional = \[' skills/ .claude/implementation/todo/` → seule occurrence :
  `skills/list-dir/scripts/tests/test_contract.py:176,185` (les cas de test qui exercent le refus)
- `diff` semence ↔ copie en vigueur sur les 4 paires de contrats → identiques
- sondage direct du parseur (`parse_contract`) sur trois cas limites non couverts par les tests —
  voir R2 et R3

Aucune commande du suivi ni du brief n'est restée non exécutée.

### Conformité à l'intention

- Critère « `list-dir contract <liste>` rend une description pour chaque section déclarée » :
  **atteint, vérifié**. Chaque section des quatre contrats migrés porte `description = ""`, servie
  telle quelle par la commande. Le contenu reste vide, ce qui est explicitement hors-périmètre.
- Critère « un contrat à l'ancien format échoue avec un message qui nomme la migration » :
  **atteint, vérifié** sur un contrat fabriqué. Le message nomme le fichier, le défaut, la nature
  manuelle de la réécriture, et les deux commandes de renvoi.
- Critère « une section sans `description` échoue ; `description = ""` passe » : **atteint,
  vérifié** (contrôle d'absence `"description" not in body` distinct du contrôle de type,
  `contract.py`; tests dédiés).
- Critère « le message renvoie à la semence ; la réécriture est manuelle » : **atteint, vérifié**.
  Aucune commande de réécriture n'a été ajoutée ; `--def <name>` et `defs` existent et répondent.
- Critère « `list-dir validate` passe sur les trois registres et sur la liste de revue » :
  **atteint, vérifié**, la liste de revue par une dérivation jetable comme le plan le prévoyait.
- Critère « la suite `scripts/tests/` passe » : **atteint, vérifié** — 307 tests verts.
- Hors-périmètre : **respecté**. Aucune clé de section au-delà de `required`/`description` ; aucune
  option `--sections` ; aucun outil de migration ; `templates/review.md` absent du diff ; toutes les
  descriptions des contrats du dépôt sont vides (les seules descriptions rédigées sont l'exemple
  pédagogique de `contrat-liste.md`, qui est de la doc, pas un contrat du dépôt).
- Signaux de dérive : **aucun matérialisé**. Les deux formats ne coexistent pas — l'ancien lève une
  erreur en lecture, donc dans toutes les commandes. Aucun module hors `contract.py`/`types.py`
  n'apprend la forme du TOML : `store.py` ne fait qu'itérer sur `Contract.sections` (clés) et lire
  `required_sections`, et son seul autre point de contact est le squelette d'`init`, qui écrit du
  TOML mais ne le lit pas.
- Symptôme d'origine : **disparu**. `list-dir contract` a désormais un emplacement documenté pour le
  corps de l'élément, là où l'outil le lit. La documentation *effective* reste à écrire, ce qui est
  le chantier suivant annoncé.

### Qualité du code

- **R1** — `skills/list-dir/references/contrat-liste.md:271-272` — le tableau des marqueurs décrit
  toujours l'ancien format : « section de `required` » / « section de `optional` », c'est-à-dire les
  deux listes que ce chantier vient de rendre illégales. Le plan (étape 5) demandait explicitement
  leur passage à « section `required = true` », par symétrie avec les deux lignes de champ
  au-dessus. L'étape est cochée et sa vérification (le `grep`) passe, mais elle ne couvrait pas ce
  point. La page de référence est précisément celle vers laquelle le message d'erreur envoie : elle
  contredit le format qu'elle vient d'introduire vingt lignes plus haut.
- **R2** — `contract.py`, boucle des sections — une clé mal orthographiée dans une section
  (`require = true` au lieu de `required`) est ignorée en silence : la section devient facultative
  sans qu'aucun message ne le signale. Vérifié par sondage : `[sections."A"] require = true` rend
  `Section(name='A', required=False)`. Le format étant volontairement « ouvert à d'autres clés plus
  tard », refuser les clés inconnues n'était pas demandé, et le même laxisme existe déjà sur
  `[fields.*]` — c'est donc une cohérence de style autant qu'un chemin d'échec silencieux. À
  connaître avant d'ajouter la première clé optionnelle réelle.
- **R3** — `contract.py`, `required=bool(body.get("required", False))` — `required = "false"` rend
  `required=True` (vérifié par sondage). Défaut hérité tel quel de la construction des `Field`
  (`contract.py`, même expression) : l'aligner ici aurait été le corriger là-bas, hors périmètre.
  Signalé pour mémoire, pas comme une régression du chantier.
- **R4** — `types.py:143-145`, `section_marker` — le repli `<OPTIONNEL>` sur un titre inconnu est
  conservé comme le plan l'exigeait, mais ses deux seuls appelants (`store.py:230` et `:331`)
  n'itèrent plus que sur `contract.sections` : la branche `section is None` n'est plus atteignable
  par le code de production, et aucun test ne l'exerce directement. Filet légitime, mais non
  couvert : une régression future y passerait sans bruit.
- **R5** — `skills/list-dir/references/contrat-liste.md:246` — ligne de 121 caractères dans un
  fichier qui enroule systématiquement à 100. Détail de style, mais introduit par ce chantier.

Rien d'autre à signaler : la boucle des sections est calquée sur celle des champs (mêmes helpers
`_table`/`_texte`, mêmes messages nommant le fichier et le sujet), les commentaires en capitales
suivent l'idiome du fichier, et les deux points délicats — la remontée de `name` sous
`contract_name` pour éviter l'écrasement par la variable de boucle, et l'absence de faux positif sur
une section titrée « required » — sont commentés à l'endroit où ils se lisent, et testés.

### Dette induite

- **R6** — aucune duplication ni abstraction gratuite introduite. `Section` reprend la forme de
  `Field` sans l'étendre, `required_sections` est dérivée plutôt que stockée, et
  `optional_sections` a été supprimée plutôt que reconduite par symétrie (décision journalisée du
  2026-08-31, vérifiée : aucun appelant résiduel dans le dépôt).
- **R7** — le couplage semence ↔ copie en vigueur reste manuel et non contrôlé : les quatre paires
  de contrats sont aujourd'hui identiques (vérifié par `diff`), mais rien dans l'outil ne le
  garantira à la migration suivante. Ce chantier n'a pas créé ce couplage — il en a payé le coût
  une fois de plus (8 fichiers réécrits à la main au lieu de 4). Coût futur : le même travail
  doublé à chaque évolution du format de contrat.
- **R8** — les archives (`.claude/implementation/done/2026-08-23-format-registres.plan.md`,
  `…/2026-08-30-semences-de-listes.audit.md`) décrivent encore l'ancien format. Ce sont des
  documents datés et clos : les laisser tels quels est correct. Signalé seulement pour que le
  prochain `grep` sur `required = [` ne conclue pas à un oubli.

### Bloquants

Aucun. R1 est la seule réserve que je recommande de lever avant de clore : c'est une contradiction
interne de la page de référence vers laquelle le message d'erreur du chantier envoie l'utilisateur,
et le plan la demandait nommément.
