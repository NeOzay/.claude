---
slug: tableaux-toml-aplatis-a-l-ecriture
titre: Conserver le format des tableaux TOML à la réécriture
branche: tableaux-toml-aplatis-a-l-ecriture
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-09-09-tableaux-toml-aplatis-a-l-ecriture.plan.md
brief: .claude/implementation/done/2026-09-09-tableaux-toml-aplatis-a-l-ecriture.brief.md
audit: .claude/implementation/done/2026-09-09-tableaux-toml-aplatis-a-l-ecriture.audit.md
road-map: tableaux-toml-aplatis-a-l-ecriture
créé: 2026-09-09
maj: 2026-09-09
---

## Objectif et périmètre

Repris du brief, non reformulé.

**Symptôme** : « Je veux que le format des tableaux TOML soit conservé, pouvoir écrire une entrée
par ligne et que la structure ne bouge pas. » `dump_value` sérialise tout tableau sur une seule
ligne (`items.py:191`), et dès qu'un seul champ change le front matter entier est resérialisé
(`types.py:316` → `raw_front = None`, `items.py:208`) : un ajout de champ au contrat aplatit d'un
coup tous les tableaux écrits à la main.

**But** : qu'un tableau mis en forme à la main ressorte tel qu'il a été écrit après une réécriture
qui ne portait pas sur lui. Étendu par l'utilisateur : les chaînes multilignes `"""…"""` doivent
être prises en charge à l'écriture.

**Critères de réussite** :
- `pytest` passe sur `skills/list-dir/scripts/tests/`
- un tableau écrit à la main sur plusieurs lignes ressort **identique** après un `migrate` qui
  ajoute un champ au contrat
- une entrée de tableau contenant un saut de ligne s'écrit en `"""…"""` au lieu de lever
  `SerialiseError`
- un commentaire posé au-dessus d'un champ suit ce champ quand le contrat le réordonne
- `sante_skills.py` signale l'absence de tomlkit, comme il signale déjà une version de Python trop
  ancienne

**Hors-périmètre** :
- l'enroulement automatique d'un tableau à la première écriture (`new`, `derive`, préremplissage)
- les contrats et gabarits : ils restent sur `tomllib`, tomlkit ne sert qu'au front matter des
  éléments
- pas de règle de longueur d'entrée à documenter : la préservation rend la question sans objet

**Signaux de dérive** :
- si le diff touche la lecture ou l'écriture des **contrats**, des **gabarits** ou de
  `provenance.py`, on est sorti du périmètre — s'arrêter
- si un **test existant est modifié** plutôt qu'ajouté, s'arrêter et en reparler

Écarté explicitement au cadrage : confiner tomlkit à `items.py`/`types.py` n'est **pas** un signal
de dérive.

**Élargissement du 2026-09-09** — l'amorçage entre dans le périmètre : venv dédié à `~/.claude`,
`requirements.txt` versionné, ré-exécution de `list-dir.py` dans ce venv, contrôle par
`sante_skills.py`, et `venvPath` dans `pyrightconfig.json`. Le brief ne l'envisageait pas ; sans
lui, rien n'est exécutable puisque le `python3` de Linuxbrew est `EXTERNALLY-MANAGED`. Accepté par
l'utilisateur au moment du choix du mode d'installation.

## Étapes

- [x] 1. Amorcer le venv et le rendre obligatoire — `requirements.txt`, `list-dir.py`, `pyrightconfig.json` — vérif: `list-dir help >/dev/null && ~/.claude/.venv/bin/python -c "import tomlkit, pytest"`
- [x] 2. Contrôler la dépendance dans `sante_skills.py` — `scripts/sante_skills.py` — vérif: `python3 ~/.claude/scripts/sante_skills.py; echo $?`
- [x] 3. Prouver tomlkit avant d'écrire quoi que ce soit — script jetable au scratchpad — vérif: le script porte ses assertions et rend un code de sortie
- [x] 4. `toml_value` et `dump_front` reprojetant, sans réordonnancement — `listdir/items.py` — vérif: `pytest tests/test_items.py` + pyright
- [x] 5. Réordonner les blocs, commentaire compris — `listdir/items.py` — vérif: `pytest tests/test_store_ecriture.py tests/test_items.py`
- [x] 6. Retirer la frontière et réécrire ce qui la documente — `listdir/types.py`, `listdir/items.py`, `listdir/store.py`, `references/operations.md` — vérif: `pytest tests/`
- [x] 7. Tests de bout en bout de la préservation — `tests/` — vérif: `pytest tests/`

## État courant

**Prochaine action** : aucune — chantier terminé, R16 à R18 soldées après le troisième audit.

**Base de référence** : **545 tests avant le chantier** (mesurés sur l'arbre `master` extrait par
`git archive`, même venv), **572 après** — soit +27, pour 2 retirés, ces deux
derniers étant les réécritures autorisées.
pyright : 4 erreurs, toutes préexistantes dans `test_prefill.py`. ruff : **3 erreurs, autant que sur
`master`** et les mêmes — les deux `E402` induites par le ré-amorçage ont été supprimées en le
ramenant à un `if` unique, forme que ruff admet avant les imports comme la garde de version. `sante_skills` silencieux.

**Reproduction de l'entrée de road-map, rejouée** : sur une liste neuve portant un tableau écrit
sur trois lignes avec un commentaire au-dessus, l'ajout de deux champs au contrat suivi d'un
`migrate` produit un diff de **deux lignes ajoutées, rien d'autre**. Le tableau et son commentaire
sont intacts.

**Vérification** : `~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/`

**Dernier audit** : `9e9e855` — RÉSERVES — 2026-09-09, aucun bloquant (R11 à R15 levées)

**Notes — à porter au registre de dette à la clôture** : `test_prefill.py:127` produit 4 erreurs
pyright préexistantes (`.split` sur une valeur de type `FieldValue` non rétrécie), et
`test_contract.py:108` / `test_fusion.py:266,292` dépassent 100 colonnes. Hors périmètre de ce
chantier, constatés en le menant.

## Journal de décisions

- **2026-09-09** — troisième audit `RÉSERVES` sur `9e9e855`, aucun bloquant : R11 à R15 levées,
  reproduction du bloquant refaite de bout en bout. R16 : mon relevé de tests était faux pour la
  **seconde fois** — la base est 545, pas 551 (mon chiffre incluait déjà les tests de l'étape 2).
  Corrigé en remesurant sur l'arbre `master`. *Leçon* : un chiffre cité dans le suivi se remesure
  après chaque correction, il ne se reconduit pas.
- **2026-09-09** — R17 et R18 soldées sans quatrième audit, sur arbitrage de l'utilisateur. R17 :
  le correctif de R15 avait ajouté un paragraphe sans retirer celui qu'il remplaçait — `_reordonne`
  énonçait une règle de queue que `_detacher_queue` porte déjà. R18 : une épingle assortie d'un
  marqueur d'environnement retombe sur la présence seule, faute de résolveur ; c'est maintenant dit
  au docstring et cadré par deux tests.
- **2026-09-09** — R11 soldée : le saut de ligne final est garanti avant de parser
  (`items.py`, `dump_front`). *Pourquoi là* : `split_front` rend le front matter par un
  `"\n".join(…)`, donc le dernier item n'a pas de `trail` ; le corriger au parsing vaut pour tous
  les items sans que `_reordonne` ait à connaître cette subtilité. *Test* : vérifié qu'il échoue
  sans le correctif et passe avec.
- **2026-09-09** — R12 à R15 soldées. R12 : le ré-amorçage tient dans un `if` unique, admis avant
  les imports là où une affectation ne l'est pas. R13 : les quatre endroits qui justifiaient encore
  la non-réécriture par « perdrait son raw_front » disent maintenant la vraie raison — une date de
  modification neuve et du bruit dans `git status`. R14 : `sante_skills` compare désormais la
  version épinglée par `==`, et pas seulement le nom ; une contrainte souple ne contrôle que la
  présence. R15 : `courant` retiré de `_reordonne`, mort depuis le correctif de R4.
- **2026-09-09** — second audit de clôture `DÉFAVORABLE` sur `07ad9a6`. **R11, bloquant** :
  régression vs `master` — `migrate` corrompt le front matter d'un élément réordonné dont le dernier
  item est un champ, silencieusement et en rendant 0. Les 457 tests ne le voyaient pas : toutes les
  fixtures de réordonnancement finissent par un commentaire de queue, seul cas où le `trail` manquant
  ne sert jamais de séparateur. La reproduction de road-map inscrite ici en portait un, elle aussi.
- **2026-09-09** — R12 : mon relevé « ruff, 5 erreurs toutes préexistantes » était **faux**. `master`
  en a 3 ; les deux `E402` sont induites par le chantier. La comparaison d'alors passait par un
  `git stash` incapable d'annuler `list-dir.py`, déjà commité en `10edfcb`. Restent à traiter R13
  (`store.py:300,319` disent encore que réécrire un élément « perdrait son raw_front »), R14
  (l'épingle `tomlkit==0.15.1` n'est pas contrôlée : `sante_skills` ne compare que des noms) et R15
  (`neuf.body.extend(courant)` dans `_reordonne`, mort depuis le correctif de R4).
- **2026-09-09** — audit de clôture `RÉSERVES` (R1-R8, aucun bloquant). R1-R4 et R8 traités avant de
  clore, sur arbitrage de l'utilisateur ; R5 et R6 écartés. R4 était un défaut réel : un commentaire
  de queue se faisait adopter par un champ ajouté, contre la décision journalisée le même jour — la
  queue est désormais détachée avant tout ajout, et un test couvre la combinaison. R6 est
  inatteignable : `FieldType` (`types.py:120`) n'admet ni booléen ni entier.
- **2026-09-09** — `dump_value` est **déprécié**, sa suppression est planifiée hors de ce chantier.
  *Pourquoi* : décision de l'utilisateur — ses deux derniers appelants (`store.init_list`,
  `provenance`) touchent des zones que le brief pose en signal de dérive, donc pas ici. *Écrit* :
  dette `deux-ecrivains-toml-coexistent`, road-map `supprimer-dump-value`, et la dépréciation
  marquée dans le docstring de la fonction.
- **2026-09-09** — `dump_value` est **gardé intact** ; tomlkit ne sert qu'à `dump_front`, donc au
  seul front matter des éléments. *Pourquoi* : `dump_value` écrit aussi les contrats
  (`store.py:802-803`) et les semences (`provenance.py:431`), que le brief pose en signal de dérive
  et qui n'ont rien à préserver puisqu'ils sont recopiés à l'octet. *Prix assumé* : deux écrivains
  TOML cohabitent, et l'en-tête d'`items.py` dit lequel sert à quoi.
- **2026-09-09** — la lecture reste sur `tomllib`, tomlkit ne sert qu'à l'écriture. *Pourquoi* :
  aucun type proxy de tomlkit ne circule alors dans le paquet — l'incertitude « frontière de
  typage » du brief se referme sans avoir à être tenue.
- **2026-09-09** — un champ retiré emporte le commentaire qui le précédait. *Pourquoi* : découvert
  en écrivant le test — `migrate --drop` laissait derrière lui la légende d'un champ disparu, un
  commentaire devenu faux que plus rien ne rattachait à quoi que ce soit. *Conséquence* : la
  suppression se fait par omission à la reconstruction, pas par `del`.
- **2026-09-09** — signal de dérive « test existant modifié » déclenché à l'étape 6, comme prévu,
  et **sur les deux tests annoncés seulement**. Levée autorisée par l'utilisateur avant l'étape 4.
  `test_un_champ_modifie_declenche_la_reserialisation` et `test_realigned_reserialise_et_remplace`
  ont été réécrits sans perdre ce qu'ils cadraient.
- **2026-09-09** — étape 3, tomlkit prouvé sur le vrai besoin : aller-retour à l'octet ; modifier un
  champ laisse les autres intacts ; les commentaires autonomes sont des items distincts de
  `doc.body`, regroupables avec la clé qui suit et déplaçables avec elle ; multiligne natif y
  compris dans un tableau ; **tous** les caractères de contrôle sont écrits et relus à l'identique,
  `\x00` compris. Aucune incertitude du brief ne reste ouverte.
- **2026-09-09** — le commentaire sans champ derrière lui est reconduit **en queue de document**.
  *Pourquoi* : c'est ce que le regroupement produit naturellement — un commentaire final n'a pas de
  clé à suivre. *Rejeté* : le rattacher à la dernière clé, qui le ferait voyager au réordonnancement
  sans que personne l'ait voulu.
- **2026-09-09** — la garde de type reste à notre charge : tomlkit accepte un `dict` et l'écrit en
  table `[x]`. *Pourquoi* : le contrat n'admet ni table ni type hors liste ; sans `SerialiseError`,
  un type non couvert passerait silencieusement. *Rejeté* : s'en remettre au refus de tomlkit, qui
  n'existe pas.
- **2026-09-09** — le contrôle de dépendances ne se déclenche que si `requirements.txt` existe.
  *Pourquoi* : la déclaration crée l'exigence, et sans cette règle tout dépôt sans dépendance
  crierait à l'absence d'un venv. *Effet* : aucun test existant de `sante_skills` n'a eu à changer.
- **2026-09-09** — tomlkit retenu pour le front matter des éléments, les contrats restant sur
  `tomllib`. *Pourquoi* : parseur préservant, il rend natifs commentaires, ordre, tableaux et
  chaînes multilignes ; l'en-tête d'`items.py` justifiait le sérialiseur maison par « la stdlib n'a
  aucun écrivain TOML », prémisse que tomlkit supprime. *Rejeté* : une découpe champ → texte
  maison, qui revient à réimplémenter un tiers de parseur.
- **2026-09-09** — venv dédié à `~/.claude` avec pytest embarqué, plutôt qu'une installation dans
  le Python de Linuxbrew. *Pourquoi* : `EXTERNALLY-MANAGED` y refuse `pip install`, et
  l'utilisateur assume l'ouverture à d'autres dépendances. *Rejeté* : `pip
  --break-system-packages` (contamine un interpréteur géré par brew) et PEP 723 + `uv run --script`
  (fait passer chaque appel par uv).
- **2026-09-09** — le modèle retenu reparse `raw_front` à l'écriture et n'y reprojette que les
  champs modifiés, plutôt que de stocker une découpe champ → texte. *Pourquoi* : un seul chemin de
  rendu, aucun état supplémentaire dans `Item`. *Écart assumé* : le brief décrivait la découpe ;
  l'utilisateur a validé ce modèle en approuvant le plan.
- **2026-09-09** — le venv est amorcé par `uv venv` + `uv pip install --python`, pas par `pip` :
  `uv venv` ne pose aucun `pip` dans l'environnement. C'est cette commande que le message de
  réparation de `sante_skills` devra citer. Python 3.12.13, conforme à `MIN_PYTHON` et au
  `pythonVersion` de pyright.
- **2026-09-09** — plan relu par `plan-reviewer` : verdict NON CONFORME, dix constats. Les défauts
  de rédaction (recensement des tests, localisation du signal, vérifications manquantes) ont été
  corrigés dans le plan ; les arbitrages de fond sont reportés en « À trancher » et validés avec le
  plan.
