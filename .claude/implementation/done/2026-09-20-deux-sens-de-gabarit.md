+++
gabarit = "suivi"
slug = "deux-sens-de-gabarit"
titre = "Donner un mot neuf au moule de `derive`, et remettre la prose dans le sens de la dépendance"
branche = "deux-sens-de-gabarit"
base = "master"
statut = "terminé"
session = 1
lettre = "A"
execution = "direct"
plan = ".claude/implementation/done/2026-09-20-deux-sens-de-gabarit.plan.md"
brief = ".claude/implementation/done/2026-09-20-deux-sens-de-gabarit.brief.md"
audit = ".claude/implementation/done/2026-09-20-deux-sens-de-gabarit.audit.md"
road-map = "<OPTIONNEL>"
"créé" = 2026-09-20
maj = 2026-09-20
+++

## Objectif et périmètre

**Symptôme** : « le mot "gabarit" a deux sens dans le couple » — et les instructions des deux
skills sont à réécrire, parce que `list-dir` dépend de `gabarit` et non l'inverse, alors que la
prose fait le chemin contraire.

**But** : baptiser **patron** le moule de `derive` (`.list/templates/<nom>.{toml,md}`), pour que
« gabarit » ne désigne plus que le fichier préstructuré posé depuis une semence ; puis écrire le
socle commun dans `gabarit` — format d'un fichier, contrat, types admis, marqueurs,
préremplissage, verdicts — et ne laisser à `list-dir` que ce qui est propre à une liste, en renvoi
vers `gabarit`.

**Critères de réussite** :
- `grep -rni 'template' skills/list-dir skills/debt-review --include=*.py --include=*.md` → aucune
- `grep -rn 'gabarit' skills/list-dir --include=*.py --include=*.md` → chaque occurrence désigne le
  paquet `gabarit` ou le fichier posé, jamais un patron
- `ls .claude/implementation/todo/technical-debt/.list/patrons/` → `review.md`, `review.toml`
- `list-dir validate .claude/implementation/todo/technical-debt` → conforme ; `reseed --dry-run` →
  aucun conflit ; `derive … --patron review` puis `validate` → conforme
- `grep -n 'Prérequis' skills/list-dir/SKILL.md` → une section qui nomme `gabarit` et y renvoie
- les six types (`slug`, `text`, `date`, `enum`, `list`, `int`) sont écrits dans une référence de
  `gabarit`, et `grep -rn 'list-dir/references' skills/gabarit/` → aucun renvoi
- `pytest skills/list-dir/scripts/tests skills/gabarit/scripts/tests -q` → 508 passed
- `scripts/check_pipeline.py` → conforme
- `ruff` et `basedpyright` → aucun écart avec le relevé de base pris à l'étape 1

**Hors-périmètre** :
- Le fichier posé depuis une semence garde son nom : ni le skill `gabarit`, ni le paquet, ni la
  commande, ni le lien de `bin/`, ni le champ d'estampille `gabarit = "…"`
- Aucun changement de comportement : aucune commande ne gagne ni ne perd d'option
- La dette `gabarit-porte-des-residus-de-liste` (déplacer `Item.id`) — c'est du découpage de paquet
- La road-map `rapport-audit-en-liste`
- Les cinq références de `list-dir` ne sont pas réorganisées : elles perdent du texte et gagnent
  des renvois, leur découpage ne bouge pas
- Les archives de `.claude/implementation/done/` gardent leurs `--template`

**Signaux de dérive** :
- Le diff touche un fichier hors des chemins autorisés (voir l'élargissement du 2026-09-20)
- Une phrase de prose change de **sens** au lieu de changer de **mot** : le renommage est devenu
  une réécriture d'autorité
- Le déplacement du socle vers `gabarit` commence avant que le renommage en `patron` soit terminé
  et vérifié
- Une notion propre à une liste (`id` égal au nom du fichier, `.list/`, `from`, `[origin]`,
  `reseed`) est écrite dans `gabarit`
- Le nombre de tests passants baisse, ou un test est ajusté pour accepter un message d'erreur au
  lieu que le message soit corrigé

**Élargissement du 2026-09-20** — le brief bornait le diff à `skills/list-dir/`, `skills/gabarit/`
et « trois répertoires `templates/` ». Le plan, relu par `plan-reviewer` (verdict NON CONFORME sur
ce seul point) et approuvé ensuite par l'utilisateur, l'étend à :

- `skills/debt-review/SKILL.md` et `references/gabarit-rapport.md` — deux appels à `--template`,
  dont un exécutable : sans eux la skill casse ;
- `skills/implementation-tracker/list-dir/technical-debt/templates/` — définition de liste, à
  renommer sinon `init --def technical-debt` sème une liste sans patrons ;
- **quatre** répertoires `templates/` et non trois : `.list/backup/templates/` s'y ajoute ;
- `.claude/implementation/todo/technical-debt/` — soldage des deux dettes, à l'étape 5.

Le hors-périmètre « les skills tierces ne sont pas modifiées » devient donc : **aucune skill tierce
n'est modifiée au-delà des appels au drapeau renommé et du répertoire de définition**. Aucun mot
n'y change.

## Étapes

- [x] 1. Renommer le moule dans le code, sur le disque et à l'interface — `skills/list-dir/scripts/`, 4 répertoires `templates/`, `skills/debt-review/` — vérif: `pytest skills/list-dir/scripts/tests skills/gabarit/scripts/tests -q` → 508 passed, et `list-dir reseed .claude/implementation/todo/technical-debt --dry-run` → aucun conflit
- [x] 2. Renommer le moule dans la prose de `list-dir` — `skills/list-dir/SKILL.md`, `references/*.md` — vérif: `grep -rni 'template\|gabarit' skills/list-dir/SKILL.md skills/list-dir/references/` → aucune, et `scripts/check_pipeline.py` → conforme
- [x] 3. Poser le socle dans `gabarit/references/format.md` — `skills/gabarit/` — vérif: `grep -rn 'list-dir/references\|\.\./list-dir' skills/gabarit/` → aucun, les six types présents, `check_pipeline.py` → conforme
- [x] 4. `list-dir` perd le socle et gagne ses « Prérequis » — `skills/list-dir/references/format.md`, `SKILL.md` — vérif: `grep -n 'Prérequis' -A6 skills/list-dir/SKILL.md`, `check_pipeline.py` → conforme, pytest → 508 passed
- [x] 5. Contrôles finaux et registre de dette — `.claude/implementation/todo/technical-debt/` — vérif: `diff` ruff et basedpyright contre le relevé de base, et les deux dettes sorties du registre

## État courant

**Prochaine action** : les cinq étapes sont faites. Le chantier est prêt pour la clôture —
`/implementation-tracker close`, qui commence par l'audit d'`implementation-auditor`.
**Vérification** : `/home/debian/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests skills/gabarit/scripts/tests -q` → 508 passed, puis `scripts/check_pipeline.py` → conforme.
**Dernier audit** : ffc2297 — RÉSERVES — 2026-09-20 (quatre constats, tous traités ; voir le
journal)
**Notes** : le filet est la suite de tests — les messages d'erreur destinés à l'utilisateur y sont
assertés, ce sont eux qui prouvent qu'aucune occurrence n'a été manquée. Base des linters relevée
avant l'étape 1 : ruff 3 erreurs, basedpyright 5536 (l'essentiel venant de `skills/synced/`).
**Assumé** : quatre identifiants d'entrées de dette gardent un mot au sens moule — décision de
l'utilisateur du 2026-09-20, voir le journal.

## Journal de décisions

- **2026-09-20** — Le moule de `derive` s'appelle **patron** ; « gabarit » ne désigne plus que le
  fichier posé depuis une semence. Le renommage descend au disque (`.list/patrons/`) et à
  l'interface (`--patron`). *Pourquoi* : le moule ne sort pas de list-dir, quand « gabarit » au sens
  du fichier posé est employé par quatre skills et par l'estampille de toutes les fiches. *Rejeté* :
  renommer le fichier posé ; tolérer `--template` en alias.
- **2026-09-20** — Le socle — format du fichier, contrat, six types, préremplissage, marqueurs,
  verdicts — fait autorité dans `gabarit/references/format.md` ; `list-dir` y renvoie et ne garde
  que l'`id`, `.list/`, `from`, `[origin]`, les `LISTDIR_*`. *Pourquoi* : la dépendance de code va
  de list-dir vers gabarit, la prose allait dans l'autre sens. *Rejeté* : laisser le socle à
  list-dir et y renvoyer depuis gabarit.
- **2026-09-20** — Le renommage précède le déplacement du socle et ne s'y mêle pas. *Pourquoi* :
  les renvois neufs de list-dir vers gabarit arriveraient sinon dans une prose où le mot a encore
  deux sens. *Rejeté* : une seule passe.
- **2026-09-20** — Le refus de l'ancien format `[sections]` à deux listes reste à list-dir.
  *Pourquoi* : il vit dans `listdir/contract.py`, pas dans `gabarit` — le plan le comptait à tort
  dans le socle. *Rejeté* : le remonter pour la symétrie.
- **2026-09-20** — Périmètre élargi, sur accord de l'utilisateur, à `debt-review` (appels au
  drapeau et chemins), à la définition `implementation-tracker/list-dir/technical-debt/`, à un
  quatrième répertoire (`.list/backup/`, gitignoré, donc renommé par `mv`) et au registre de dette.
  *Pourquoi* : `plan-reviewer` a rendu NON CONFORME sur ce seul point, et sans eux la skill casse et
  la définition sème une liste sans patrons. *Rejeté* : réduire le plan au hors-périmètre du brief.
- **2026-09-20** — Les quatre identifiants d'entrées de dette portant un mot au sens moule ne sont
  pas renommés ; chacun reçoit une note de vocabulaire en tête de `## Constat`. *Pourquoi* :
  décision de l'utilisateur — un id est une identité. *Rejeté* : `list-dir move` sur les quatre.
- **2026-09-20** — Les entrées de `technical-debt-solde/` gardent leurs `templates/`. *Pourquoi* :
  un `## Constat` est daté et décrit l'état du dépôt à sa date. *Rejeté* : les aligner pour
  l'uniformité du grep.
- **2026-09-20** — Audit de clôture `ffc2297` : **RÉSERVES**, quatre constats, tous traités avant
  la clôture sur décision de l'utilisateur. Cause commune : les critères du brief bornaient leurs
  greps à `skills/list-dir` en `*.md`/`*.py`, laissant hors de portée les `.toml` de définition et
  le registre — versé au registre sous `criteres-de-brief-bornes-a-une-extension`. *Rejeté* :
  clore avec les réserves.
