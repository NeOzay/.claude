---
slug: decoupe-contrat-liste
---

## 2026-09-05 — clôture — `476292a`

**Verdict** : RÉSERVES

### Vérifications exécutées

- `python3 scripts/check_pipeline.py` → **exit 0**, « Pipeline conforme », 8 contrôles verts
  (contrôle 8 : « 35 renvois entre skills, tous résolvent »)
- `cd skills/list-dir/scripts && uvx pytest tests -q` → **440 passed** en 9.45s
- Contrôle de complétude de l'inventaire (bloc du plan) → `total: 193  affectees: 193` → **COMPLET**,
  aucune règle orpheline
- `grep -rn 'contrat-liste' skills/ scripts/` → **aucun résultat**
- `grep -rn 'contrat-liste' .claude/implementation/todo/` → **3 lignes / 2 fichiers** (voir R2)
- `grep -rn 'contrat-liste' .` hors `.git/`, hors `done/`, hors slug → seuls le plan et la mention
  historique ratifiée ; **aucun renvoi vivant**
- `list-dir validate .claude/implementation/todo/technical-debt` → « 46 élément(s) conformes au
  contrat », exit 0
- `list-dir help` → 13 commandes listées, skill opérationnel
- `wc -l skills/list-dir/references/*.md` → 128 / 132 / 241 / 167 / 166 (aucun au-delà de ~250)
- `uvx ruff format --check` fichier par fichier sous `skills/list-dir/` → `references/extension.md`
  + 4 suites de tests (contrôle du repointage de la fiche `ruff-format-jamais-applique`, voir plus bas)
- Conservation des 13 `> *Mode de défaillance*` de la source : chacun retrouvé en substance dans
  les nouveaux fichiers, par recherche de sa phrase clé (détail en « Signaux de dérive »)
- Échantillon de 8 règles de l'inventaire (R012, R040, R070, R090, R115, R135, R150, R170)
  confrontée à sa ligne d'origine dans `git show master:…/contrat-liste.md` puis à son fichier
  d'arrivée → aucune dérive de sens constatée

### Conformité à l'intention

- **Critère « `python3 scripts/check_pipeline.py` passe »** : **atteint, vérifié** (exit 0, contrôle 8
  compris). Les 11 renvois entre nouveaux fichiers sont tous écrits `../references/<f>.md#<ancre>`
  conformément au journal, donc réellement soumis au contrôle 8 — vérifié par extraction de tous les
  `](…)` des cinq fichiers : aucun renvoi voisin sans préfixe.
- **Critère « `SKILL.md` référence les nouveaux documents »** : **atteint, vérifié**. La section
  « Pour aller plus loin » porte une table des cinq fichiers, et les quatre renvois en ligne
  (l. 87, 95, 99, 145) sont repointés chacun sur le fichier compétent.
- **Critère « `contrat-liste.md` supprimé, aucun renvoi résiduel hors `done/` »** : **atteint,
  vérifié**. Le fichier est supprimé (828 lignes en moins au diff). Les seules occurrences restantes
  hors archives sont le plan du chantier lui-même (artefact daté) et la mention historique gardée
  dans `renvois-sans-prefixe-hors-du-controle-des-ancres.md` — ratifiée au journal, et qui n'est
  effectivement pas un renvoi (aucun lien Markdown, tournure « l'ancien `contrat-liste.md` »).
- **Critère « inventaire des règles figé, chaque règle cochée avant suppression »** : **atteint,
  vérifié**. 193 règles, 193 destinations, réparties 48 `format` / 47 `provenance` / 40 `operations`
  / 31 `definitions` / 27 `extension`. Le motif de contrôle cible bien `→ <fichier>.md` et non la
  flèche seule — le durcissement décidé au journal (R060, R122, R173, R183 portent un `→` dans leur
  propre texte) est effectivement en place dans le fichier d'inventaire.
  Écart au brief assumé : l'inventaire vit en fichier annexe et non « dans le plan ». Ratifié dans
  le plan le 2026-09-05, l'esprit du critère (traçable, rejouable) est tenu.
- **Hors-périmètre** : **respecté**. `git diff master...HEAD -- skills/list-dir/scripts/` ne touche
  qu'un seul fichier, `commands/contract.py`, et qu'une seule ligne, à l'intérieur de la docstring —
  exception explicitement ratifiée au suivi et au plan. Aucun test modifié, 440 tests passent
  inchangés. `contrat-liste.md` n'a reçu aucune modification avant sa suppression (vérifié : il
  n'apparaît au diff qu'en suppression intégrale).
- **Signaux de dérive** : **aucun matérialisé**.
  - Aucune règle changée de sens : échantillon de 8 règles confronté ligne à ligne à la source, plus
    relecture intégrale des passages sensibles (`migrate`, `move`, surcharge, `reseed`, `--values`).
  - Les 13 `> *Mode de défaillance*` de la source (l. 35, 107, 131, 193, 228, 305, 418, 437, 443,
    607, 628, 638, 746) sont **tous** intégrés au corps du texte, aucun perdu — y compris les deux
    qui ne se retrouvent plus par leur formulation d'origine : le `README.md` à la racine est en
    `format.md:29-31`, l'état porté par le répertoire en `format.md:149-152`. C'est exactement la
    transformation annoncée au plan (intégration à l'exemple plutôt que bloc cité isolé).
  - `scripts/listdir/` et les tests : voir ci-dessus.
- **Symptôme d'origine** : **disparu pour l'essentiel**. Le plus gros fichier passe de 828 à 241
  lignes ; les trois sujets nommés comme dispersés dans le brief sont regroupés — `derive` tient
  désormais dans la seule section « Listes dérivées » d'`operations.md`, le contrat dans
  `format.md`, `validate` réparti entre `operations.md` (ce qu'il confronte) et `provenance.md` (ce
  dont il avertit), séparation qui est un choix documenté et non une dispersion résiduelle. Réserve
  R3 sur la taille brute.

### Qualité du code (documentation produite)

- **R1** — `.claude/implementation/decoupe-contrat-liste.inventaire.md` est **toujours suivi par git
  à `476292a`**, alors que l'étape 10 est cochée `[x]` et libellée « `git rm contrat-liste.md` **+
  l'inventaire** », et que le plan (étape 9) prescrivait son `git rm` avec un motif précis : son
  suffixe `.inventaire.md` n'est pas dans `ANNEXES` (`scripts/check_pipeline.py:330`). Le motif est
  **vérifié comme réel** : `python3 skills/implementation-tracker/scripts/impl_list.py` rend
  aujourd'hui deux entrées pour ce chantier —
  `decoupe-contrat-liste.inventaire.md` et `decoupe-contrat-liste.md`. Le listing des suivis est
  donc pollué dès maintenant, pas seulement à l'archivage. Le suivi documente le report (« gardé
  jusque-là — l'auditeur en a besoin — et supprimé à l'archivage ») : le choix est cohérent et
  légitime, mais une étape cochée dont une moitié de l'action annoncée n'est pas au HEAD est un
  écart de forme, et le `git rm` reste à faire impérativement à la clôture. Le contrôle 3 de
  `check_pipeline` ne le rattrapera pas : il n'examine que les archives `done/`.
- **R2** — La vérification écrite à l'étape 9 du suivi (« `grep -rn 'contrat-liste\.md'
  .claude/implementation/todo/` ne rend que la mention historique de
  `renvois-sans-prefixe-hors-du-controle-des-ancres.md` ») **ne passe pas littéralement** : le grep
  exécuté rend 3 lignes dans 2 fichiers — les deux lignes attendues (l. 17-18), plus
  `description-obligatoire-sur-les-sections-seulement.md:5` (`source = "chantier
  \`decoupe-contrat-liste\`…"`). Sans conséquence de fond — c'est le slug du chantier, pas un renvoi
  au fichier supprimé, et le critère du brief vise les cibles à lire — mais la commande de
  vérification telle qu'elle est inscrite au suivi induit en erreur qui la rejouera. Le plan
  (étape 8) porte la même formulation, encore plus stricte (`grep -rln` « sans résultat »).
- **R3** — **La taille brute n'est pas réduite** : 828 lignes en un fichier deviennent 834 lignes en
  cinq (`wc -l` : 241 + 167 + 166 + 132 + 128). Le plan annonçait pourtant de « condenser » les
  passages redondants, et le brief nommait la taille comme gêne secondaire. Le gain réel est
  entièrement dans la dispersion et le plus gros fichier (828 → 241) — ce qui est bien la gêne
  principale du brief, donc le critère n'est pas manqué. Mais le lecteur du suivi doit savoir que le
  volume total de documentation `list-dir` est inchangé : les renvois croisés et les cinq en-têtes
  ont consommé ce que la condensation a gagné.
- **R4** — **`migrate --dry-run` est décrit à deux endroits** : `format.md:199-205` (sous
  « Préremplir un champ ou une section », angle des commandes préremplies) et `operations.md:53`
  (« `--dry-run` montre le plan sans rien écrire »). Les deux ne se contredisent pas et
  `format.md:200` renvoie explicitement à `operations.md#quand-le-contrat-change`, ce qui limite
  fortement le risque. C'est néanmoins précisément la forme de dispersion que le chantier corrige —
  une règle de `migrate` énoncée hors du fichier qui fait autorité sur `migrate`. Le découpage
  d'origine du plan plaçait cette règle en `format.md` (source l. 491, section « Préremplir »), donc
  l'écart est hérité, pas introduit ; il mérite d'être connu.
- **R5** — `skills/list-dir/references/format.md:200` fait **165 caractères** : c'est une puce de
  prose, non une ligne de table, et elle n'a pas été réenveloppée après insertion du lien
  `[migrate](…)` en tête. Les autres lignes longues des cinq fichiers sont des lignes de table ou
  des URLs, forme admise ailleurs dans le dépôt (`implementation-tracker/references/contrat.md`
  monte à 193). C'est le seul débordement de style franc du diff.

### Dette induite

- **R6** — La convention `> *Mode de défaillance*` **disparaît entièrement** des références de
  `list-dir` (13 → 0 occurrences), alors qu'elle reste vivante et lisible ailleurs dans le dépôt —
  `debt-review/SKILL.md`, `implementation-tracker/references/dette.md`. C'est une décision explicite
  du plan et du brief (« intégrer les modes de défaillance aux exemples »), et le fond est
  intégralement conservé : ce n'est donc pas une perte. Le coût futur est ailleurs : deux
  conventions de rédaction coexistent désormais dans `skills/`, sans que rien ne dise laquelle
  s'applique à quoi. Un prochain chantier de `list-dir` hésitera. À trancher un jour, ou à assumer
  par écrit.
- Aucune duplication de code introduite, aucun couplage nouveau, aucun contournement laissé en
  place. Les 9 fiches de dette repointées l'ont été vers des cibles vérifiées : le repointage de
  `ruff-format-jamais-applique.md` vers `references/extension.md` a été **contrôlé à l'exécution**
  (`uvx ruff format --check` fichier par fichier confirme que c'est bien `extension.md`, et lui
  seul parmi les `.md`, qui serait reformaté) ; celui de `regles-hors-contrat-sans-empreinte.md`
  vise `operations.md « Déplacer un élément »`, ancre qui existe (`operations.md:67`) ; la mise à
  jour de `renvois-sans-prefixe-hors-du-controle-des-ancres.md` (« il en reste **deux**, dans
  `dette.md` ») est exacte — grep confirme `dette.md:280` et `:305` comme seuls renvois
  intra-fichier de la famille visée. Ce niveau de vérification des fiches est notable.
- La fiche `description-obligatoire-sur-les-sections-seulement.md` ouverte à l'étape 8 cite
  `listdir/contract.py:422`, `:475` et `_texte()` l. 163 : **les trois lignes ont été vérifiées et
  correspondent**. L'élargissement de périmètre est daté et ratifié au suivi, il n'entame pas le
  hors-périmètre (rien du code n'a été corrigé).

### Bloquants

Aucun.
