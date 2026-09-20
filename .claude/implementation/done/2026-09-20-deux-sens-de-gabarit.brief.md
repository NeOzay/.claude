+++
gabarit = "brief"
slug = "deux-sens-de-gabarit"
titre = "Donner un mot neuf au moule de `derive`, et remettre la prose dans le sens de la dépendance"
statut = "validé"
execution = "direct"
"créé" = 2026-09-20
+++

## Intention

**Symptôme** : « le mot "gabarit" a deux sens dans le couple » — et les instructions des deux
skills sont à réécrire, parce que `list-dir` dépend de `gabarit` et non l'inverse, alors que la
prose fait le chemin contraire.

**But** : baptiser **patron** le moule de `derive` (`.list/templates/<nom>.{toml,md}`), pour que
« gabarit » ne désigne plus que le fichier préstructuré posé depuis une semence ; puis écrire le
socle commun dans `gabarit` — format d'un fichier, contrat, types admis, marqueurs,
préremplissage, verdicts — et ne laisser à `list-dir` que ce qui est propre à une liste, en renvoi
vers `gabarit`.

## Critères de réussite

- `grep -rn 'gabarit' skills/list-dir/ --include=*.md --include=*.py` → chaque occurrence restante
  désigne le paquet `gabarit` ou le fichier posé, jamais un patron
- `grep -rni 'template' skills/list-dir/ --include=*.md --include=*.py` → aucune occurrence
- `ls .claude/implementation/todo/technical-debt/.list/patrons/` → `review.md`, `review.toml`
- `list-dir validate .claude/implementation/todo/technical-debt` → conforme, et
  `list-dir contract .claude/implementation/todo/technical-debt --template review` renommé
  fonctionne sous son nouveau drapeau
- `grep -n 'Prérequis' skills/list-dir/SKILL.md` → une section qui nomme `gabarit` et renvoie à
  `skills/gabarit/SKILL.md`
- `gabarit contract` et les références de `gabarit` listent les six types admis (`slug`, `text`,
  `date`, `enum`, `list`, `int`) sans renvoyer à `list-dir`
- `grep -rn 'list-dir/references' skills/gabarit/` → aucun renvoi de gabarit vers list-dir
- `/home/debian/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests skills/gabarit/scripts/tests -q`
  → 508 passed
- `/home/debian/.claude/.venv/bin/python scripts/check_pipeline.py` → conforme
- `uvx ruff check skills/list-dir skills/gabarit` et `uvx --with pytest basedpyright` → sans
  régression par rapport à la base

## Hors-périmètre

- **Le fichier posé depuis une semence garde son nom** : ni le skill `gabarit`, ni le paquet, ni
  la commande, ni le lien de `bin/`, ni le champ d'estampille `gabarit = "…"` en tête des fiches
  posées ne changent
- Les quatre skills tierces (`skill-convention`, `intent-brief`, `implementation-tracker`,
  `debt-review`) ne sont pas modifiées : elles emploient « gabarit » pour le fichier posé, qui ne
  change pas. Un grep de contrôle en fin de chantier confirme qu'aucune n'en désignait un moule
- Aucun changement de comportement : c'est un renommage et un déplacement de prose. Aucune
  commande ne gagne ni ne perd d'option, aucun verdict ne change
- La dette `gabarit-porte-des-residus-de-liste` (déplacer `Item.id` vers `listdir`, purger les
  docstrings qui citent leur consommateur) — c'est du découpage de paquet, pas du vocabulaire
- La road-map `rapport-audit-en-liste` (porter le rapport d'audit par une liste)
- Les cinq références de `list-dir` ne sont pas réorganisées : elles perdent le socle et gagnent
  des renvois, elles ne changent pas de découpage

## Signaux de dérive

- Le diff touche un fichier hors de `skills/list-dir/`, `skills/gabarit/` et des trois
  répertoires `templates/` à migrer
- Une phrase de prose change de **sens** au lieu de changer de **mot** : le renommage est devenu
  une réécriture d'autorité, et le chantier de vocabulaire finance une revue qui n'a pas été cadrée
- Le déplacement du socle vers `gabarit` commence avant que le renommage en `patron` soit
  terminé et vérifié — les renvois neufs arriveraient dans une prose encore ambiguë
- Une notion propre à une liste (`id` égal au nom du fichier, `.list/`, `from`, `[origin]`,
  `reseed`) est écrite dans `gabarit`
- Le nombre de tests passants baisse, ou un test est ajusté pour accepter un message d'erreur
  au lieu que le message soit corrigé

## Contraintes connues de l'utilisateur

- **Décision** : le mot neuf est **patron**, et il nomme le moule de `derive` — la paire
  `.list/templates/<nom>.{toml,md}` qui projette une liste sur une liste neuve. Le fichier posé
  depuis une semence, lui, reste un gabarit (dit)
- **Décision** : le renommage porte sur le code **et** la documentation, et descend **jusqu'aux
  données sur disque** : `.list/patrons/` et `--patron` (dit)
- **Décision** : les skills tierces sont vérifiées, pas touchées (dit)
- **Existant** : trois entrées de dette décrivent déjà ce chantier — `gabarit-nomme-deux-choses-dans-list-dir`
  (« trancher avec l'utilisateur : renommer l'un des deux sens »),
  `list-dir-depend-de-gabarit-sans-le-dire` (qui réclame la section « Prérequis »), et
  `gabarit-porte-des-residus-de-liste`, laissée hors-périmètre
  (dépôt: .claude/implementation/todo/technical-debt/)
- **Existant** : la collision est chiffrée — 30 emplois de « gabarit » pour un moule de `derive`
  dans la prose de list-dir, une soixantaine d'identifiants, et les deux sens se croisent dans un même fichier en
  quatre endroits (`definitions.py:36-38`, `types.py:48/84/137`, `store.py:147/431`,
  `contract.py:37/312`) (dépôt: skills/list-dir/)
- **Existant** : trois répertoires `templates/` sur disque portent la même paire `review`, dont
  une copie de semence que `reseed` compare fichier par fichier
  (dépôt: .claude/implementation/todo/technical-debt/.list/semence/templates/)
- **Existant** : le titre de section `provenance.md:33` est une ancre citée par `operations.md:142`
  — le renommer casse le renvoi s'il n'est pas suivi (dépôt: skills/list-dir/references/)
- **Existant** : 508 tests passent avant le chantier, et les messages d'erreur destinés à
  l'utilisateur y sont assertés — c'est le filet qui prouve qu'aucune occurrence n'a été manquée
  (dépôt: skills/{list-dir,gabarit}/scripts/tests)

## Incertitudes à lever en plan

- Comment migrer les trois `templates/` sur disque sans que `reseed` lise la disparition des
  fichiers comme un conflit : la copie de semence (`.list/semence/templates/`) et la copie vive
  (`.list/templates/`) sont comparées en chemins relatifs par `provenance.py`, et rien n'existe
  aujourd'hui pour renommer un répertoire des deux côtés à la fois.
- Où atterrit exactement le socle dans `gabarit` : une référence neuve (`references/format.md`),
  ou l'agrandissement de `references/semences.md` qui le renvoie aujourd'hui.
