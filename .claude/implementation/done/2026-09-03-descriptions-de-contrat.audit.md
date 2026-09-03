---
slug: descriptions-de-contrat
---

## 2026-09-03 — clôture — `54090d8`

**Verdict** : RÉSERVES

### Vérifications exécutées

- `grep -rn --include='*.toml' 'description = ""' skills/implementation-tracker/list-dir .claude/implementation/todo`
  → aucune sortie, exit 1 (rien trouvé)
- `grep -rn 'description = ""' skills/implementation-tracker/list-dir .claude/implementation/todo`
  (forme littérale du brief) → 2 lignes, toutes deux en prose dans
  `technical-debt/sections-declarees-sans-description-redigee.md` (l. 18 et 26), aucune dans un
  contrat
- `diff -r .claude/implementation/todo/<l>/.list skills/implementation-tracker/list-dir/<l>` pour
  les trois registres → exit 0, muet sur les trois (gabarits `review.toml` et `review.md` compris)
- `list-dir validate` sur les trois registres → « 40 élément(s) conformes », « 17 élément(s)
  conformes », « 2 élément(s) conformes »
- `list-dir contract .../technical-debt-solde | grep -c "Dette soldée"` → 1
- `list-dir contract .../technical-debt-ecarte | grep -c "Sorti du registre"` → 1
- `list-dir derive .../technical-debt "$S/revue-test" --template review` → « 40 fiche(s) à
  instruire », puis `list-dir contract "$S/revue-test"` → les 4 sections imprimées avec leur
  description rédigée (liste jetable supprimée)
- `python3 scripts/check_pipeline.py` → « Pipeline conforme. », exit 0
- `python3 scripts/sante_skills.py` → exit 0, aucune sortie
- `list-dir defs` → les trois listes résolvent en rang 4
- `diff <(git show master:…/dette.md | grep '^#') <(grep '^#' …/dette.md)` → exit 0, aucun titre
  supprimé
- `git diff master...descriptions-de-contrat --name-only | grep -v -E '\.(md|toml)$'` → vide,
  aucun fichier de code touché
- comptage des lignes > 100 colonnes, master contre branche, sur chaque fichier modifié → aucune
  ligne longue introduite (`dette.md` en perd une : 35 → 34)

### Conformité à l'intention

- Critère « aucune `description = ""` dans les contrats, et aucune description de champ ne recopie
  celle de sa liste » : **atteint, vérifié**. Les 18 sections vides (4 + 5 + 5 + 4 du gabarit) sont
  rédigées, et les 4 champs de `technical-debt-solde` / `technical-debt-ecarte` qui portaient la
  description de leur liste portent désormais, mot pour mot, celles de `technical-debt` — les trois
  contrats sont identiques sur `title`, `date`, `source`, `reviewed`, `category`.
- Critère « semence et copie restent identiques, gabarit `review.toml` compris » : **atteint,
  vérifié** — `diff -r` muet sur les trois arbres, ce qui couvre `templates/review.toml` et
  `templates/review.md`.
- Critère « `list-dir validate` passe sur les trois registres » : **atteint, vérifié**.
- Critère « `list-dir contract "$T/technical-debt-solde"` n'affiche plus quatre fois la même
  phrase » : **atteint, vérifié** — 1 occurrence au lieu de 5, idem pour `technical-debt-ecarte`.
- Critère « les règles de `dette.md` qui décrivent le contenu d'une section ont laissé place à un
  renvoi au contrat » : **atteint** — les trois règles visées par l'étape 4 du plan (facultativité
  dans les listes de sortie, « une entrée sans Pour solder est un regret », « Désigner sans numéro
  de ligne ») ont cédé la place à un paragraphe de renvoi, sans qu'aucun titre `##` disparaisse et
  avec `check_pipeline.py` toujours à 0. Voir toutefois **R1**.
- Hors-périmètre « aucune modification de code » : **respecté** — le diff ne contient que des
  `.md` et des `.toml`, `prefill.py` et les scripts sont intacts.
- Hors-périmètre « pas de réécriture des entrées de dette existantes » : **respecté** — aucun
  fichier d'entrée n'apparaît au `--name-only`, y compris
  `sections-declarees-sans-description-redigee.md` dont les deux occurrences en prose de
  `description = ""` sont laissées telles quelles.
- Signaux de dérive : **aucun matérialisé**. Aucune `description` n'excède une phrase nominale
  d'une ligne ; `dette.md` conserve « Alimenter », « Solder », « Écarter », « L'`id` ne se renomme
  pas » et ses encadrés `> *Mode de défaillance*`, donc le fonctionnement et la manipulation ; la
  semence et la copie ne divergent nulle part.
- Symptôme d'origine (« plusieurs contrats ont leurs champs remplis avec des descriptions
  vides ») : **disparu**, et le second défaut — plus trompeur — l'est aussi.

### Qualité du code

- **R1** — `skills/implementation-tracker/references/dette.md`, paragraphe « Ce que ce fichier ne
  redit pas non plus » : le renvoi annonce que les `description` du contrat disent « pourquoi
  `Constat` reste requis jusque dans les listes de sortie ». Elles ne le disent pas : le contrat
  déclare `required = true` et décrit *quoi* écrire (« ce qui a été observé, factuel et daté, sans
  remède ni numéro de ligne »), jamais *pourquoi* la section survit à la sortie du registre. Le
  motif — « sans lui, une entrée soldée ne dirait plus de quoi elle parlait, et le registre des
  payées deviendrait une liste de dates » — a disparu du dépôt avec l'ancien paragraphe. Le lecteur
  qui suit le renvoi ne trouve pas ce qu'on lui a promis, et c'est précisément le genre de
  justification que le brief laisse à `dette.md`. Les deux autres promesses du même paragraphe
  (« ce qu'une entrée sortie n'a plus à plaider », « une entrée sans `Pour solder` est un regret »)
  sont, elles, bien portées par les descriptions.
- **R2** — `skills/implementation-tracker/list-dir/technical-debt-ecarte/contract.toml`, section
  `Écartée le` : la description s'arrête à « la preuve exécutée » et omet la dispense que l'étape 2
  du plan lui assignait explicitement — « pour un doublon, l'`id` de l'entrée conservée » à la place
  d'une commande. La règle survit dans `dette.md` (« Écarter ») et dans `templates/review.md` pour
  la fiche de revue, donc rien n'est perdu ; mais c'est justement le cas où le contrat, seul lu par
  `list-dir contract`, laisse croire qu'une commande est toujours exigée. Écart au plan, non au
  brief.
- **R3** — `skills/debt-review/SKILL.md`, Étape 2, point 2 : « La choisir pour qu'elle se rejoue
  seule, sans contexte : c'est elle qui sera recopiée dans le registre » redit désormais la
  description de `Vérifié par` au gabarit (« la commande exécutée et sa sortie réelle, rejouable
  sans contexte »). Le journal du suivi tranche que `SKILL.md` « n'avait rien à céder » parce que
  son point 4 relève de la manipulation — c'est juste pour le point 4, mais le point 2 reste une
  redite de contenu, celle-là même que le chantier existe pour supprimer. Le brief posait pourtant
  `skills/debt-review/` comme « devenant renvoyant à son tour » (tranché). Le constat Q5 de
  `plan-reviewer`, consigné non tranché au journal, porte exactement là.
- Style : conforme aux voisins. Phrases nominales, minuscule initiale, tiret cadratin, mêmes
  idiomes que les descriptions préexistantes de `technical-debt` (« date du constat, jamais
  modifiée ») et de `review.toml`. Aucune description n'utilise d'accent grave, ce que le plan
  imposait pour que les trois contrats restent identiques champ à champ. Aucune ligne longue
  introduite.

### Dette induite

- **R4** — l'incertitude que le brief demandait de lever à la clôture reste ouverte : le second
  défaut (descriptions de champ recopiées, origine d8a06ac) n'a toujours aucune entrée au registre,
  et ni le journal du suivi ni le « Reste ouvert » du plan ne tranche s'il en mérite une
  rétroactive. Le chantier se clôt donc sans avoir répondu à une question qu'il s'était posée ;
  coût : le seul défaut jamais consigné du chantier n'existera plus qu'en archive de suivi.
- **R5** — le critère du brief se lit littéralement sans `--include='*.toml'` et, sous cette forme,
  il rend deux lignes. Le suivi porte la forme amendée et fait foi, le plan justifie l'ajout (le
  hors-périmètre interdit de retoucher l'entrée de dette qui cite `description = ""` en prose) :
  le critère est donc bien servi. Constat consigné pour que la divergence brief/suivi ne se relise
  pas comme un échec silencieux — et parce que la commande littérale du brief restera fausse tant
  que l'entrée `sections-declarees-sans-description-redigee` existera, y compris une fois soldée
  et déplacée sous `technical-debt-solde/`.
- Aucune duplication ni abstraction nouvelle par ailleurs : le chantier retire de la prose plutôt
  qu'il n'en ajoute, et `dette.md` perd trois règles pour un paragraphe.

### Bloquants

Aucun.

## 2026-09-03 — clôture (contre-audit) — `f2c64bf`

**Verdict** : RÉSERVES

Contre-audit du commit `f2c64bf`, qui traite les réserves R1-R3 de l'audit `54090d8`. Le diff
depuis `54090d8` touche 4 fichiers de doctrine et de contrat (11 lignes), plus le suivi et le
rapport d'audit. Les cinq critères de réussite ont été **réexécutés en entier**, pas seulement les
vérifications des correctifs.

### Vérifications exécutées

- `grep -rn --include='*.toml' 'description = ""' skills/implementation-tracker/list-dir
  .claude/implementation/todo` → aucune sortie, exit 1
- `grep -rn 'description = ""' …` (forme littérale du brief) → 2 lignes, toutes deux en prose dans
  `technical-debt/sections-declarees-sans-description-redigee.md` (l. 18 et 26), aucune dans un
  contrat — inchangé, cf. R5
- `diff -r .claude/implementation/todo/<l>/.list skills/implementation-tracker/list-dir/<l>` sur
  les trois registres → muet, exit 0 sur les trois
- `list-dir validate` ×3 → « 40 élément(s) conformes », « 17 élément(s) conformes »,
  « 2 élément(s) conformes »
- `list-dir contract …/technical-debt-solde | grep -c "Dette soldée"` → 1
- `list-dir contract …/technical-debt-ecarte | grep -c "Sorti du registre"` → 1
- `list-dir derive …/technical-debt "$S/revue-test2" --template review` puis `list-dir contract
  "$S/revue-test2"` → les 4 sections imprimées avec leur description rédigée (liste jetable
  supprimée après lecture)
- `python3 scripts/check_pipeline.py` → 8 contrôles verts, « Pipeline conforme. », exit 0
- `python3 scripts/sante_skills.py` → exit 0, aucune sortie
- `list-dir defs` → les trois listes en rang 4
- `diff <(git show master:…/dette.md | grep '^#') <(grep '^#' …/dette.md)` → exit 0, aucun titre
  supprimé ni ajouté
- `git diff master...descriptions-de-contrat --name-only | grep -v -E '\.(md|toml)$'` → vide
- comptage des lignes > 100 colonnes, master contre branche, fichier par fichier → aucune ligne
  longue introduite dans un fichier de doctrine ou de contrat. `dette.md` repasse de 34 à 35, soit
  son compte de `master` : le correctif R1 réintroduit une ligne longue là où l'état `54090d8` en
  avait supprimé une. Pas de régression au sens de la dette `trois-lignes-au-dela-de-100-colonnes`,
  qui compte par rapport à `master`.

### Suite donnée aux réserves de `54090d8`

- **R1 — levée.** Le motif retiré est revenu à `dette.md`, section « Ce qu'une entrée porte » :
  « Ce que le contrat déclare sans pouvoir le motiver, en revanche, reste ici : **`Constat` est
  requis jusque dans les listes de sortie** — sans lui, une entrée soldée ne dirait plus de quoi
  elle parlait, et le registre des payées deviendrait une liste de dates. » Le paragraphe de renvoi
  ne promet plus que ce que les `description` portent réellement (« ce qu'une entrée sortie du
  registre n'a plus à plaider », « une entrée sans `Pour solder` est un regret ») — les deux
  promesses que le premier audit avait vérifiées comme tenues. La correction respecte la ligne de
  partage du brief sans allonger aucune `description` : aucun signal de dérive.
- **R2 — levée, avec un report de substance (voir R6).** La section `Écartée le` porte désormais
  « date, motif et preuve exécutée ; pour un doublon, l'id de l'entrée conservée ». La dispense que
  l'étape 2 du plan assignait explicitement est là, dans les deux exemplaires (`diff -r` muet).
- **R3 — levée.** `skills/debt-review/SKILL.md`, Étape 2 point 2, ne redit plus le gabarit :
  « Ce qu'elle doit être est dit au contrat de la liste de revue, section `Vérifié par`. » La moitié
  supprimée qui n'était pas portée par le contrat (« c'est elle qui sera recopiée dans le registre »)
  survit dans `references/categories.md:38` : rien n'a disparu du dépôt. Le renvoi est suivable —
  `$R` est défini en amont (l. 171) et `gabarit-rapport.md:70` en donne la forme de commande. Le
  point 4, qui dit *quand* écrire chaque section, reste intact : c'est bien de la manipulation.
  Le constat Q5 de `plan-reviewer`, consigné non tranché au journal, est de ce fait purgé.

### Conformité à l'intention

Les cinq critères sont **atteints et revérifiés** sur `f2c64bf`, dans les mêmes termes qu'à
`54090d8` — les conclusions de la section correspondante du rapport précédent tiennent, aucune
n'est infirmée. Le hors-périmètre reste respecté (aucun fichier de code au diff, aucune entrée de
dette réécrite), aucun signal de dérive n'est matérialisé : `dette.md` conserve « Alimenter »,
« Solder », « Écarter », « L'`id` ne se renomme pas » et ses encadrés `> *Mode de défaillance*` —
le correctif R1 lui en **rend** même, aucune `description` n'excède une phrase d'une ligne, et
semence et copie ne divergent nulle part. Le symptôme d'origine a disparu.

### Qualité du code

- **R6** — `technical-debt-ecarte/contract.toml`, section `Écartée le` : en gagnant la dispense
  « doublon », la description a **perdu l'énumération des motifs** qu'elle portait à `54090d8`
  (« non pertinent, doublon, pas une dette »), que l'étape 2 du plan demandait elle aussi. Le
  correctif a donc échangé une moitié du contenu prévu contre l'autre, faute de place sous 100
  colonnes. Rien n'est perdu du dépôt — `dette.md`, « Écarter » : « Motifs admis, et rien d'autre :
  **non pertinent**, **doublon**, **pas une dette** » — mais le contrat, seul lu par
  `list-dir contract`, dit maintenant « motif » sans dire lesquels sont admis, alors qu'il déclare
  par ailleurs toutes les valeurs admises de `category`. Un lecteur du seul contrat peut écrire un
  motif libre, et `validate` ne verra rien : la section est de la prose. Constat de fidélité au
  plan, non au brief — aucun critère de réussite n'est en cause.
- Style : inchangé et conforme. Les trois lignes ajoutées à `dette.md` reprennent le gras et le
  tiret cadratin des paragraphes voisins ; la phrase de renvoi de `SKILL.md` suit la forme déjà
  employée à `gabarit-rapport.md:70`. Aucun accent grave introduit dans une `description`, les trois
  contrats restent identiques champ à champ.

### Dette induite

- **R4 — toujours ouverte.** L'incertitude que le brief demandait de lever *à la clôture* n'est
  toujours pas tranchée : le second défaut (descriptions de champ recopiées, origine d8a06ac) n'a
  aucune entrée au registre, et ni le journal du suivi ni le « Reste ouvert » du plan ne dit s'il en
  mérite une rétroactive. Le suivi la porte explicitement comme restant à trancher (« R4 … reste à
  trancher »), ce qui vaut prise en compte, pas décision. C'est le dernier point de clôture ouvert.
- **R5 — inchangée, et sans effet sur le verdict.** Le critère du brief se lit littéralement sans
  `--include='*.toml'` et rend alors deux lignes de prose ; le suivi porte la forme amendée et fait
  foi, le plan justifie l'ajout par le hors-périmètre. Le critère est servi.
- Aucune duplication ni abstraction nouvelle depuis `54090d8` : le correctif R3 supprime une redite,
  le correctif R1 rapatrie une justification dans le seul fichier compétent pour la porter.

### Bloquants

Aucun.
