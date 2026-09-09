---
slug: tableaux-toml-aplatis-a-l-ecriture
titre: Conserver le format des tableaux TOML à la réécriture
statut: validé
execution: direct
créé: 2026-09-09
---

## Intention

**Symptôme** : « Je veux que le format des tableaux TOML soit conservé, pouvoir écrire une entrée
par ligne et que la structure ne bouge pas. » Aujourd'hui `dump_value` sérialise tout tableau sur
une seule ligne (`items.py:191`), et dès qu'un seul champ change le front matter entier est
resérialisé (`types.py:316` → `raw_front = None`, `items.py:208`) : un ajout de champ au contrat
aplatit d'un coup tous les tableaux écrits à la main.

**But** : qu'un tableau mis en forme à la main ressorte tel qu'il a été écrit après une réécriture
qui ne portait pas sur lui. Étendu par l'utilisateur : « je veux aussi que les strings multiples
soient prises en charge » — donc l'écriture doit savoir produire une chaîne multiligne `"""…"""`,
là où `dump_value` refuse aujourd'hui tout caractère de contrôle.

## Critères de réussite

- `pytest` passe sur `skills/list-dir/scripts/tests/`
- un tableau écrit à la main sur plusieurs lignes ressort **identique** après un `migrate` qui
  ajoute un champ au contrat
- une entrée de tableau contenant un saut de ligne s'écrit en `"""…"""` au lieu de lever
  `SerialiseError`
- un commentaire posé au-dessus d'un champ suit ce champ quand le contrat le réordonne
- `sante_skills.py` signale l'absence de tomlkit, comme il signale déjà une version de Python trop
  ancienne

## Hors-périmètre

- **l'enroulement automatique** d'un tableau à la première écriture (`new`, `derive`,
  préremplissage) : pas dans ce chantier (tranché). Un champ `list` prérempli continue de naître
  sur une ligne ; le mettre en forme une fois suffit ensuite
- **les contrats et gabarits** : ils restent sur `tomllib`, tomlkit ne sert qu'au front matter des
  éléments (tranché). Ils sont recopiés à l'octet, il n'y a rien à y préserver
- pas de règle de longueur d'entrée à documenter : la préservation rend la question sans objet

## Signaux de dérive

- si le diff touche la lecture ou l'écriture des **contrats**, des **gabarits** ou de
  `provenance.py`, on est sorti du périmètre — s'arrêter (dit)
- si un **test existant est modifié** plutôt qu'ajouté, s'arrêter et en reparler : ces tests
  encodent des garanties — aller-retour octet, réordonnancement selon le contrat, non-réécriture
  d'un élément conforme — qu'on veut étendre, pas relâcher (dit)

Écarté explicitement : confiner tomlkit à `items.py`/`types.py` n'est **pas** un signal de dérive
(dit) — il peut remonter ailleurs si le plan le justifie.

## Contraintes connues de l'utilisateur

- **Voulu** : une entrée de tableau par ligne doit rester possible, et la structure ne doit pas
  bouger (dit)
- **Frontière existante à réutiliser** : `raw_front` présent → front reconduit à l'octet près ;
  `None` → resérialisé. C'est « le seul commutateur » (dépôt: scripts/tests/test_items.py:173) et
  `migrate` s'appuie déjà dessus pour ne pas réécrire un élément inchangé (dépôt:
  listdir/store.py:293-296)
- **Limite dure de la sérialisation** : `dump_value` refuse tout caractère de contrôle, donc une
  entrée écrite en chaîne multiligne `"""…"""` meurt à la première réécriture (dépôt:
  listdir/items.py:176-181)
- **Rien à corriger dans la doc existante** : aucune règle de longueur d'entrée n'y figure
  aujourd'hui (dépôt: grep « court|longueur|libellé » vide sur skills/list-dir/**.md)
- **Chaînes multilignes voulues en écriture** (dit) — lève la limite posée par le docstring de
  `dump_value` (« TOUT CE QUI EST ÉCRIT DOIT SE RELIRE ») (dépôt: listdir/items.py:163-181)
- **Règle proposée pour les commentaires** : un commentaire commente la donnée qui le suit, et la
  suit donc à la réécriture (dit)
- **Hors d'atteinte du problème** : contrats et gabarits ne sont jamais resérialisés, ils sont
  recopiés en texte brut — leurs commentaires ne risquent rien (dépôt: listdir/store.py:532,
  store.py:792-796, listdir/provenance.py:762-781). L'exemple donné par l'utilisateur
  (`skills/implementation-tracker/list-dir/technical-debt/templates/review.toml`, bloc `[origin]`)
  est de ceux-là. Seul le front matter d'un élément est concerné, et il est plat : pas de table

## Piste retenue en cadrage

**tomlkit est retenu** (dit), pour le front matter des éléments seulement — les contrats restent
sur `tomllib` (tranché). « C'est mon skill personnel ; en plus, cela ouvrira la porte à
d'autres dépendances. » La dépendance tierce est donc assumée et fait précédent — `listdir/` n'a
aujourd'hui que la stdlib (dépôt: imports de listdir/*.py). `scripts/sante_skills.py` vérifiera sa
présence (dit), et ce contrôle fait partie du chantier (tranché) ; il contrôle déjà `MIN_PYTHON` de
la même manière (dépôt: scripts/sante_skills.py:76-80).

Ce que tomlkit rend natif et qu'il n'y a donc plus à écrire : round-trip fidèle, commentaires
attachés à l'item suivant, tableaux multilignes, chaînes multilignes, insertion de clé à position.

Conserver le texte brut **de chaque champ** — sa ligne ou son bloc, commentaire qui le précède
compris — au lieu du front matter entier. Réordonner déplace des blocs intacts ; modifier un champ
resérialise ce seul bloc ; ajouter un champ insère un bloc neuf à la place que le contrat lui donne.

Formulation née de la question de l'utilisateur sur l'ordre des champs : préserver les *positions*
est incompatible avec le réordonnancement selon le contrat, qui est une garantie réelle et testée
(`_reordering` émet un changement appliqué — dépôt: listdir/store.py:410-418,
tests/test_store_ecriture.py:176). Préserver le *texte* ne l'est pas.

## Incertitudes à lever en plan

- la phrase « le contrat est l'autorité, pas la mise en page » (dépôt: listdir/store.py:269-271)
  devient fausse si les commentaires sont préservés — à réécrire, ou à borner
- `raw_front: str | None` devient une découpe champ → texte brut : c'est le commutateur unique du
  paquet qui change de nature (dépôt: listdir/types.py:303-316, tests/test_items.py:173 « LA
  FRONTIÈRE »). Ampleur réelle à évaluer en plan
- un commentaire sans champ derrière lui (fin de front matter, ou entre le délimiteur et le premier
  champ) n'a pas de propriétaire sous la règle « le commentaire commente ce qui suit » — à trancher
- les valeurs de tomlkit sont des types proxy (`items.String`, `items.Array`), pas des `str`/`list`
  nus ; le paquet est typé serré (`Result`, `FieldType`, `cast`) — frontière à tenir explicitement
