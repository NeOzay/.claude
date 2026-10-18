+++
id = "shadow-skill-de-compaction-de-la-prose"
title = "Un Shadow-skill qui condense la prose d'une skill ou d'une doc, par coupe ou par réécriture complète"
date = 2026-10-17
source = "analyse du skill `docs-prose-compaction` (eeriea/agent-skills) et de la réécriture de doc de claude-translator, discussion du 2026-10-17"
+++

## À faire

Un Shadow-skill global de relecture qui condense l'information sans en perdre. Il sert d'abord à
auditer le contenu des skills de ce dépôt, pour les trier et les réorganiser.

Le Shadow-skill fournit deux choses :

- **Les règles de routine**, appliquées à chaque écriture ou relecture. Elles reprennent de
  `docs-prose-compaction` ses deux points les plus utiles :
  - **les cinq classes** — fait, dérivable, narration, tampon, fioriture —, que le test de
    récupération départage, sous le veto des règles de conservation ;
  - **les paramètres qui déplacent le seuil** — genre, audience, provenance.

  La classe **dérivable** est la plus risquée : couper une information pour la laisser implicite
  oblige le lecteur à la reconstruire, et un modèle qui reconstruit peut reconstruire autrement.
  Orientation retenue : elle se scinde en deux.

  | Sous-classe | Ce qu'elle recouvre | Verdict |
  |---|---|---|
  | **Redite** | l'information est écrite en toutes lettres dans le même bloc : la phrase voisine, le code, la signature | couper |
  | **Déduction** | l'information se tire du bloc, mais par un raisonnement | garder |

  Une redite coupée ne laisse rien à reconstruire ; une déduction coupée laisse le modèle conclure
  seul, contre le principe de réduire son non-déterminisme.

  Elles ajoutent une règle que le source n'a pas, **la reformulation** : une phrase trop longue, ou
  qui mêle plusieurs consignes, se découpe — une consigne par phrase ou par élément de liste — et la
  mise en forme Markdown (listes, tableaux, gras sur le terme clé, code) porte la structure que la
  phrase portait mal. Le source s'en tient à l'inverse : couper des phrases entières, ne pas
  retoucher les mots ; seul son genre runbook pose « une étape, une action ».
- **La procédure de réécriture complète**, qui reprend ce que pratique claude-translator sur
  `docs/` → `docs2/` : un squelette d'abord, dont chaque section nomme ses sources
  (`> Sources :`) ; une notion, un endroit, ailleurs une phrase et un lien ; les motifs regroupés
  dans un fichier de décisions (Choix à jour, Motif, Ce que ça coûte, Rejeté, Révisions) ; le
  provisoire rangé dans une seule section par fichier ; l'ordre du général au spécifique ; des
  vérifications mécaniques à chaque Étape (V-squelette, V-mots, V-liens, V-revue). Le gain se lit
  en unicité, pas en volume : `decisions/` dépasse `DECISIONS.md`, `ANALYSE.md` passe de 403 à
  187 lignes.

Chaque réécriture a son espace de travail, un répertoire à part qui réunit trois choses :

- la copie des documents, que la réécriture lit sans la modifier ; les originaux ne sont pas
  touchés ;
- la réécriture, partie d'un squelette posé à côté de la copie ;
- les fichiers d'état, par exemple les résultats des scripts de vérification.

Un sous-agent évalue la réécriture. Il met chaque évaluation en correspondance avec le texte
source. Un sous-agent ne suit pas les renvois : les règles d'évaluation sont recopiées dans sa
définition, l'exception que prévoit « Un sous-agent recopie ses règles ».

La correspondance va dans les deux sens, à deux grains :

- **source → réécriture, au paragraphe** : chaque unité du source, ancrée sur une plage de lignes
  de la copie figée, reçoit un verdict — `porte`, avec sa destination dans la réécriture, ou la
  classe de sa coupe ;
- **réécriture → source, à la section** : les lignes `> Sources :` du squelette, conservées avant
  que la réécriture ne les retire.

Elle tient dans un Gabarit de l'espace de travail, dont les deux sections sont des sections à
motif — `{n: int}. {source} → {verdict: enum} {destination}` pour la première. Chacune est
préremplie par la `command` de sa Semence : le découpage de la copie pose une puce par unité, `n`
et `source` remplis ; le sous-agent remplit `verdict` et `destination` par Edit. `gabarit check`
juge la forme de chaque puce ; un script de couverture lit les puces par `section_values` et
vérifie que chaque unité a un verdict et que chaque destination existe.

Points à trancher au Brief :

- le périmètre : prose des skills, commentaires de code, mémoire ;
- la frontière avec `skill-convention` : `prose.md` garde les règles d'écriture, le Shadow-skill
  porte la méthode de relecture et y renvoie ;
- le motif d'une règle est un fait, toujours gardé, contre la coupe de la « motivation tail » ;
  une consigne découpée par la reformulation garde son motif attaché ;
- la frontière entre redite et déduction : ce que « le même bloc » recouvre, et des exemples tirés
  du dépôt de part et d'autre ;
- les seuils de la reformulation : à partir de quand une phrase est trop longue, quelle mise en
  forme pour quelle structure ;
- le mot pour « stamp », Estampille étant réservée ;
- la part confiée aux commandes : la création de l'espace de travail et de sa copie, la pose du
  squelette, le découpage en unités, le contrôle de couverture, le contrôle des liens et des
  ancres ;
- l'emplacement de l'espace de travail, sa disposition interne, et son sort une fois la
  réécriture validée : conservé, archivé, supprimé ; suivi par git ou non ;
- les contraintes du préremplissage de la correspondance :
  - le verdict d'une unité pas encore évaluée : une sortie de `command` que le Contrat refuse fait
    échouer la pose, d'où une capture `verdict` facultative ou une valeur `à-évaluer` ;
  - `check --filled` ne réclame rien dans une section préremplie : le contrôle de couverture
    exige le verdict, et la destination quand il vaut `porte`, ce qu'un motif n'exprime pas ;
  - la `command` ne reçoit que `GABARIT_FICHIER`, `GABARIT_NAME`, `GABARIT_SEMENCE` et
    `GABARIT_ROOT`, sans les champs du front matter : le document à découper se déduit du nom ou de
    l'emplacement du Gabarit posé ;
  - un Gabarit par document ou un par espace de travail ;
- le sort de la réécriture validée : remplacement des originaux, et qui le fait.

Le source n'a pas de licence : ses idées se reformulent, son texte ne se recopie pas. Ses exemples
se remplacent par des exemples tirés du dépôt. L'audit de la structure des skills (description,
partage entre `SKILL.md` et références, recouvrements) reste hors de cette entrée.

## Références

- https://github.com/eeriea/agent-skills, `skills/swe/docs-prose-compaction/` (commit d9d2cc8) :
  `SKILL.md`, `craft/keep-rules.md`, `craft/patterns.md`, `craft/genres.md`
- `shadow-skills/skill-convention/references/prose.md` : les conventions de prose qu'il recoupe
  (« Une règle, un seul endroit », « Une phrase déclare, elle ne raconte pas », « Chaque règle porte
  son motif, dans la prose »)
- `~/projects/claude-translator`, Chantier `reecrire-docs-dans-docs2` : Brief et Suivi sous
  `.claude/implementation/`, Plan `.claude/plans/mossy-moseying-swing.md` (« Règles communes à
  chaque Étape de réécriture », « Vérifications », script `liens`), commit `0a0bbc3` (les
  squelettes), `docs2/decisions/README.md` (forme d'une décision)
- Road-map `modes-de-defaillance-dans-la-prose` : un terrain d'essai, `debt-review` et `contrat.md`
- `skills/debt-review/` : un rapport de revue posé depuis une Semence
- `agents/implementation-auditor.md` : un sous-agent évaluateur qui remplit un rapport posé, et
  la recopie de ses règles
- `shadow-skills/skill-convention/references/prose.md`, « Un sous-agent recopie ses règles »
- `scripts/check_pipeline.py` : le contrôle des ancres existant
- `skills/gabarit/references/format.md`, « Les sections structurées » et « Préremplir un champ ou
  une section » ; `skills/gabarit/references/semences.md`, « L'environnement du préremplissage »
