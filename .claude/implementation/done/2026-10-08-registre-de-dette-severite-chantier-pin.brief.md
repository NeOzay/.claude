+++
gabarit = "brief"
slug = "registre-de-dette-severite-chantier-pin"
titre = "Faire évoluer le registre de dette : sévérité, chantier, référence, pin, découpage de `source`"
statut = "validé"
"créé" = 2026-10-07
+++

## Intention

**Symptôme** : on ne peut pas trier les entrées du registre par chantier, ni repérer rapidement les
dettes qui valent la peine d'être traitées ; rien ne permet de retrouver facilement certaines
dettes.

**But** : trier le registre par date et par chantier, classer les dettes par sévérité pour voir
celles qui valent d'être traitées, et épingler (`pin`) celles qu'on veut retrouver sans effort.

## Critères de réussite

- `list-dir contract "$T/technical-debt" --values severite` rend `inconnue`, `note`,
  `avertissement`, `majeur`, `critique`, dans cet ordre.
- `list-dir validate "$T/<liste>" --filled` passe sur les trois listes, sans note sur l'ancien
  Marqueur, et signale `source` comme `deprecated` tant qu'une entrée de `technical-debt` le porte.
- `list-dir list "$T/technical-debt" --sort=-severite` classe les entrées de la plus grave à la
  moins grave ; `--sort chantier` les groupe par chantier ; `--sort date` les date.
- `list-dir list "$T/technical-debt" --where pin=true` retrouve les entrées épinglées ; une entrée
  neuve porte `pin = false`.
- Chaque entrée de `technical-debt` porte `severite` (`inconnue` par défaut), et `chantier` valant un
  slug de `done/` ou « Hors chantier » ; son `source` garde son texte d'origine.
- `list-dir contract` de `-solde` et `-ecarte` déclare `source`, `severite`, `chantier`, `pin` et
  `reference` facultatifs.
- L'agent de migration existe sous `agents/`, et les `chantier` et `reference` de `technical-debt`
  ont été remplis par lui.
- Le patron `review.toml` porte `severite` et pas `pin` ; `debt-review` documente qu'elle peut
  remplacer `inconnue` et qu'elle ignore `pin`.

## Hors-périmètre

- L'adaptation de Neovim aux Marqueurs typés et au type `bool` : son propre Chantier (dit, entrée de
  road-map).
- Le traitement des entrées de `technical-debt-solde` et de `technical-debt-ecarte` (dit).
- Toute relecture de fond des entrées de `technical-debt` (dit).
- Tout changement des règles de sortie de `/debt-review`, hors le remplacement de `inconnue` et
  l'ignorance de `pin` (dit).

## Signaux de dérive

- Une entrée de `technical-debt` dont le contenu change au-delà des champs migrés (dit).
- Un `chantier` rempli qui n'est ni un slug de `done/` ni « Hors chantier » (dit).
- `pin` qui protège une entrée dans `/debt-review` (dit).
- Une modification du plugin Neovim (dit).

## Contraintes connues de l'utilisateur

- **Décision** : `severite` est un `enum` aux `values` déclarées dans l'ordre `note`,
  `avertissement`, `majeur`, `critique`, remplie par celui qui crée la dette, non par un script (dit)
- **Décision** : `chantier` porte le nom du Chantier d'où vient la dette, ou « Hors chantier » (dit)
- **Décision** : `reference` porte un `R<n>` du rapport d'audit, ou le lieu du constat (dit)
- **Décision** : `pin` est un `bool` valant `false` par défaut (dit)
- **Décision** : `source` se scinde en passant par `deprecated` — jamais posé dans une entrée neuve,
  signalé tant qu'une entrée le porte —, sans être retiré d'un coup (dit)
- **Décision** : les trois listes `technical-debt`, `-solde` et `-ecarte` sont migrées par `reseed`
  puis `migrate` ; leurs contrats sont des copies détachées de leurs définitions (dit)
- **Décision** : `severite` reçoit une valeur d'énumération de plus, `inconnue`, pour la sévérité
  inconnue, rangée en tête des `values` (`inconnue, note, avertissement, majeur, critique`) : les
  entrées existantes n'ont pas à être relues une à une dans ce Chantier (dit)
- **Décision** : à la migration de `technical-debt`, `severite` vaut `inconnue` par défaut dans
  toute entrée, et `/debt-review` remplace les `inconnue` par la valeur appropriée (dit)
- **Décision** : à la migration de `technical-debt`, `source` passe `deprecated` et garde son texte ;
  `chantier` et `reference` sont remplis par un sous-agent à partir des informations de `source`,
  sans relecture humaine des entrées (dit ; remplace la décision précédente, « Marqueur à remplir au
  fil des revues »)
- **Décision** : le sous-agent de remplissage n'est pas un outil à usage unique, car plusieurs
  registres de dette sont à migrer : la migration des entrées d'une List-dir se confie à un agent
  générique, global, qui reçoit en consigne la liste, le contrat avant et après, et la règle de
  remplissage de chaque champ, et qui sert tout registre de tout projet. Ce Chantier le construit et
  s'en sert pour migrer `technical-debt` (dit)
- **Décision** : pas d'annexe en fichier à part : un `<slug>.brief.annexe.md` serait listé comme un
  Suivi par `impl-list` et non archivé à la clôture (dépôt:
  `skills/implementation-tracker/scripts/impl-list`, constante `ANNEXES`) ; et la semence `brief`
  refuse toute section qu'elle ne déclare pas (dépôt: `gabarit check`). L'agent se décrit dans ces
  puces et dans les incertitudes, le détail se développe au plan (dit pour le principe d'une annexe
  courte)
- **Existant** : `migrate` ne juge pas, il pose les Marqueurs et ne reporte aucune valeur ; l'agent
  prend le relais pour ce jugement sans remplacer `migrate` (dépôt: `skills/list-dir/references/operations.md`,
  « Quand le contrat change »)
- **Existant** : un agent de `agents/` se charge sans suivre les renvois, ses règles s'y écrivent en
  dur, et l'outillage d'un dépôt lui arrive par un mod (dépôt:
  `shadow-skills/skill-convention/references/prose.md`, « Un sous-agent recopie ses règles »)
- **Existant** : les agents du pipeline tournent en isolation, sans pouvoir poser de question : un
  cas non tranché devient une réserve, jamais une supposition (dépôt: `agents/implementation-auditor.md`)
- **Décision** : seules les entrées de `technical-debt` sont traitées (sévérité par défaut,
  remplissage de `chantier` et `reference`) ; celles de `-solde` et `-ecarte` ne le sont pas (dit)
- **Décision** : `/debt-review` peut ajuster la `severite` d'une entrée ; le patron `review.toml` la
  dérive et la reprend telle quelle (dit)
- **Décision** : `/debt-review` ignore `pin` : le patron ne le porte pas, et il ne protège aucune
  entrée d'une sortie par la revue (dit)
- **Décision** : `technical-debt-solde` et `technical-debt-ecarte` portent `source`, `severite`,
  `chantier`, `pin` et `reference` en champs tous facultatifs (dit)

## Incertitudes à lever en plan

- Conception de l'agent de migration, à développer au plan : nom, modèle et jeu d'outils, forme de
  sa consigne (liste, contrat avant et après, règle par champ), garde qui vérifie sa sortie, rapport
  par entrée, reprise sur lot interrompu.
- `migrate` de `-solde` et `-ecarte` : pose-t-il un Marqueur facultatif dans leurs 49 entrées, ou
  les laisse-t-il intactes ? Et `pin` y garde-t-il son défaut `false` ?
- Modèle de l'agent de migration pour `chantier` et `reference` : l'utilisateur suggère Haiku. Le
  texte de `source` est court et régulier (`chantier <slug>, audit R<n>`), mais plusieurs formes
  coexistent ; la sortie est vérifiable (un `chantier` doit être un slug de `done/` ou « Hors
  chantier »).
- Un `source` dont le texte ne dit ni chantier ni référence : que reçoivent `chantier` et
  `reference` ?
