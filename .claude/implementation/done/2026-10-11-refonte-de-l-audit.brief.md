+++
gabarit = "brief"
slug = "refonte-de-l-audit"
titre = "Refondre le rapport d'audit : un fichier TOML par audit, le suivi des dettes, un verdict aligné sur leur sévérité"
statut = "validé"
"créé" = 2026-10-10
+++

## Intention

**Symptôme** : « les audits sont empilés dans un fichier .md qui gonfle à chaque audit » ; le
verdict ne conclut presque jamais (74 `RÉSERVES`, 12 `DÉFAVORABLE`, 1 `FAVORABLE` dans les
rapports archivés).

**But** : un rapport par audit, en TOML, qui reprend l'état des dettes de l'audit précédent et
suit leur évolution ; un verdict rendu par l'auditeur selon une échelle de sévérité.

## Critères de réussite

- **C1** — `audit new <slug> --intermediaire` pose `01-<sha>.toml` sur un Chantier sans audit,
  puis `02-<sha>.toml` dont la Dette précédente est la Dette actuelle du `01`, cumuls repris
  (`pytest`).
- **C2** — `audit new` exécute les `vérif:` des Étapes du Suivi et consigne `statut` et `sortie`
  en `[[verification]]` (`pytest`).
- **C3** — `audit check --filled` accepte les deux audits factices et refuse chaque faute de
  l'annexe : dette précédente non rangée, renvoi vers une dette absente, `R<n>` déjà servi,
  verdict non admis, cote d'office non respectée (`pytest`).
- **C4** — `audit range` range une dette précédente sans recopie, vers `ecartee` avec le
  justificatif lu dans `## Dettes écartées` du Suivi ; `audit dette` attribue le `R<n>` suivant
  et `trouvee` (`pytest`).
- **C5** — `grep -rn '\.audit\.md' agents/ skills/` ne rend rien, et
  `git diff --name-only master...refonte-de-l-audit | grep '\.audit\.md$'` non plus.
- **C6** — `grep '^tools:.*Edit' agents/implementation-auditor.md` rend une ligne,
  `gabarit contract suivi | grep 'Dettes écartées'` aussi, et
  `grep -n 'plus sévère' agents/implementation-auditor.md` rien.
- **C7** — `~/.claude/.venv/bin/python -c 'import pydantic'` réussit, Pydantic étant déclaré
  dans `requirements.txt`.
- **C8** — L'audit de Clôture de ce Chantier est écrit au nouveau format, dans
  `refonte-de-l-audit.audit/`, et passe `audit check --filled`.

## Hors-périmètre

- Quand un audit intermédiaire est pertinent : décidé au Plan, en road-map (dit ; dépôt:
  `.claude/implementation/todo/road-map/audit-intermediaire-au-plan.md`).
- Un nombre d'audits borné par Chantier ; un contre-audit borné au diff depuis le SHA audité :
  l'audit reste complet (dit).
- La restitution du verdict en une ligne et un tableau, déjà livrée
  (dépôt: `.claude/implementation/todo/road-map-fait/messages-du-pipeline.md`).
- La correspondance d'une dette de l'audit avec le contrat du Registre, en road-map (dit ; dépôt:
  `.claude/implementation/todo/road-map/dette-d-audit-au-format-du-registre.md`).
- Les rapports `.audit.md` existants, dans `done/` comme `lexique-local-tronque.audit.md` (dit).
- Le Brief et sa semence (dit).

## Signaux de dérive

- **S1** — Une instruction fait recopier une dette à la main par l'auditeur ou l'orchestrateur,
  au lieu d'`audit new`, `audit range` ou `audit dette` (dit).
- **S2** — Une commande ou une instruction lit des audits antérieurs au précédent : le rapport se
  suffit avec un seul précédent (dit).
- **S3** — Le verdict est écrit par une commande et non par l'auditeur ; `audit check` ne fait que
  vérifier qu'il est admis (dit).
- **S4** — Le diff touche la semence `brief`, le contrat du Registre, le seuil de 400 lignes ou un
  `.audit.md` existant (dit).
- **S5** — L'échelle de l'audit change hors décision : `inconnue` revient, ou `bloquant` entre au
  contrat du Registre (dit).

## Contraintes connues de l'utilisateur

- **Décision** : une collection de fichiers TOML, pas une List-dir ; tout l'audit en TOML (dit).
  Le front matter d'un Élément n'admet pas de tableau de tables
  (dépôt: `skills/gabarit/references/format.md:81`).
- **Décision** : `.claude/implementation/<slug>.audit/<NN>-<sha>.toml`, `NN` le rang de l'audit ;
  archivé en `done/` à la Clôture, commité à l'aplatissement (dit).
- **Décision** : les champs du TOML sont ceux des classes Pydantic de l'annexe
  `refonte-de-l-audit.brief.annexe.py`, validés avec le Brief ; le Plan peut les ajuster (dit).
  Notamment :
  - quatre tableaux : Dette précédente (copie de la Dette actuelle du précédent), Dette
    actuelle, Dette corrigée et Dette écartée (cumuls) ; chaque Rx de la précédente est réévalué
    et rangé dans l'un des trois autres ; corrigée et écartée gardent toutes les colonnes de
    l'actuelle, plus la leur ;
  - `R<n>` unique dans le Chantier ; `trouvee` porte le rang et le SHA de l'audit ; `solution`
    obligatoire ; sévérité en dernière colonne ;
  - natures : `alignement` (écart au Brief ou à une décision du Suivi), `qualité` (le code),
    `style` (la documentation et la prose), `dette induite` ;
  - la revue de conformité point par point reste hors tableau ; un point en défaut — critère non
    atteint, hors-périmètre entamé, signal matérialisé, symptôme qui persiste — et une
    vérification échouée sont des dettes ; celle d'une vérification dit comment corriger
    l'erreur, ou la commande si elle est fausse.
- **Décision** : échelle du Registre sans `inconnue`, plus `bloquant`, propre à l'audit ; aucune
  dette `bloquant` n'entre au Registre (dit ; dépôt:
  `skills/implementation-tracker/references/dette.md:138`). Les cas de l'actuel `DÉFAVORABLE` —
  critère non atteint, hors-périmètre entamé, signal matérialisé, vérification en échec,
  résultat inutilisable — sont `bloquant` d'office ; une dette non testable est `majeur` (dit).
- **Décision** : le verdict est rendu par l'auditeur, en dernière section, sur la sévérité réelle
  des dettes. `DÉFAVORABLE` : au moins un `bloquant` ou `critique`. `RÉSERVES` : au moins un
  `majeur` ou `avertissement` — `FAVORABLE` possible, justifié, s'il y a peu d'avertissements.
  `FAVORABLE` sinon. La règle « dans le doute, prends le plus sévère » est supprimée (dit ; dépôt:
  `agents/implementation-auditor.md:118`).
- **Décision** : un critère invérifiable est validé par l'utilisateur ; le Suivi gagne une section
  `## Dettes écartées`, `R<n> — justificatif — date`, d'où l'auditeur range les Rx en Dette
  écartée (dit).
- **Décision** : à la suite du verdict, les dettes restantes partent au Registre par défaut, sans
  arbitrage Rx par Rx (dit).
- **Décision** : cinq commandes (dit) :
  - `audit new <slug> --cloture|--intermediaire` pose le rapport, avec ou sans précédent ; celui
    qui lance le sous-agent la lance. Elle exécute d'avance les vérifications des Étapes,
    extraites du Suivi, et en consigne le résultat : l'auditeur juge, et les rejoue au besoin ;
  - `audit check` valide les sections et les références ;
  - `audit range` déplace une dette d'un tableau à l'autre ;
  - `audit dette <fichier> --nature <nature> --severite <sévérité>` ajoute une dette au Marqueur,
    avec son `R<n>` et `trouvee` ; l'auditeur la remplit par `Edit` ;
  - `audit export` produit l'export, toujours dans un scratchpad, son chemin complet donné à
    l'utilisateur.
- **Décision** : le format se valide par Pydantic, installé dans le dépôt avec uv (dit). Le venv
  ne porte aujourd'hui que `tomlkit` et `pytest` (dépôt: `requirements.txt`).
- **Décision** : `implementation-auditor` reçoit l'outil `Edit` (dit ; dépôt:
  `agents/implementation-auditor.md:5`, qui n'a que `Write`).
- **Réutiliser** : la bibliothèque gabarit plutôt que réinventer — lecture du Suivi et de ses
  sections, Marqueurs, `Result`, écriture TOML par tomlkit (dit ; dépôt:
  `skills/gabarit/scripts/gabarit/items.py`, `contract.py`, `types.py`).
- **Existant** : les auditeurs reprennent déjà les constats antérieurs, sous au moins cinq
  titres différents (dépôt: `.claude/implementation/done/*.audit.md`).

## Incertitudes à lever en plan

- Le format de sortie d'`audit export`, et le nom `audit` : à la discrétion du Plan (dit).
