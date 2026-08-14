---
slug: dette-technique
titre: Traçabilité normalisée des dettes techniques
statut: validé
execution: direct
créé: 2026-08-14
---

## Intention

**Symptôme** : « Il faudrait un moyen normalisé pour tracer les dettes pour de futurs
chantiers » (dit). Les constats de dette produits par l'audit finissent dans
`<slug>.audit.md`, archivé en `.claude/implementation/done/` à la clôture — un fichier
que personne ne relit. Les quatre dettes du chantier `audit-integre` clos le 2026-08-14
n'existent nulle part ailleurs (dépôt: .claude/implementation/done/2026-08-14-audit-integre.md).

**But** : un document de dette normalisé, alimenté par le pipeline, sur le modèle de
`/home/Benoit/projects/ebook-translator/docs/TECHNICAL_DEBT.md` (dit).

## Critères de réussite

- `.claude/implementation/todo/technical-debt.md` existe et porte les six dettes connues du
  chantier `audit-integre`, chacune datée, ordonnée de la plus ancienne à la plus récente, avec
  son chantier d'origine.
- La procédure de clôture porte une étape d'alimentation **située après l'audit et avant
  l'archivage** — sinon elle écrit sans connaître le verdict, ou après que les fichiers ont bougé.
- L'auditeur n'a toujours qu'un seul fichier en écriture :
  `grep -c 'audit\.md' agents/implementation-auditor.md` inchangé, et aucune mention de `todo/`
  dans ce fichier.
- L'abandon propose l'alimentation au lieu de l'imposer (`cloture.md`, section Abandon).

## Hors-périmètre

- **Pas de lecture automatique** du répertoire par le pipeline : « seulement l'alimenter. Lu que
  si l'utilisateur demande les dettes disponibles pour un nouveau chantier » (dit). `intent-brief`
  ne consulte pas `todo/` de lui-même au cadrage.
- Pas de `roadmap.md` dans ce chantier — l'emplacement doit seulement pouvoir l'accueillir (dit)

## Signaux de dérive

- **Si le même constat peut être écrit deux fois dans `todo/`, c'est raté** (dit). Un chantier
  subit plusieurs audits — intermédiaire, clôture, puis ré-audit complet après correctif
  (dépôt: skills/implementation-tracker/references/audit.md:80) — et chacun rejuge le diff entier :
  les mêmes constats ressortent par construction. Le rapport encaisse la répétition parce qu'il
  est un journal (dépôt: audit.md:87) ; `todo/` est un état, la répétition y est un doublon.
- Si l'auditeur gagne un droit d'écriture sur `todo/`, s'arrêter : en contexte isolé il ne peut
  ni dédupliquer ni retirer ce qu'un correctif a soldé (dit).

## Contraintes connues de l'utilisateur

- **Modèle imposé** : `docs/TECHNICAL_DEBT.md` d'`ebook-translator` — entrées numérotées
  `## N. Titre`, champs **Constat** / ce qui est **assumé** / **Pourquoi c'est gênant** /
  **Pour solder**, attribution finale `*Identifié par <chantier>, étape N.*`, bloc de citation
  en tête portant `Dernière vérification : <date> (chantier <slug>)` et l'historique des soldes,
  « une entrée soldée est retirée, pas barrée », exclusion explicite des idées d'amélioration
  (renvoyées à `ROADMAP.md`) (dit + dépôt: /home/Benoit/projects/ebook-translator/docs/TECHNICAL_DEBT.md)
- **Le producteur existe déjà** : l'auditeur juge la « dette technique induite »
  (dépôt: agents/implementation-auditor.md:61) et la rapporte en section dédiée
  (dépôt: skills/implementation-tracker/references/audit.md:118)
- **Écriture de l'auditeur bornée à un seul fichier** : `.claude/implementation/<slug>.audit.md`
  (dépôt: agents/implementation-auditor.md, section Interdits)
- **Seule sortie actuelle** : « points laissés de côté » du résumé de clôture, non versionné
  (dépôt: skills/implementation-tracker/references/cloture.md:68)
- **Emplacement** : `.claude/implementation/todo/`, symétrique de `done/`. Un répertoire, pas un
  fichier : « on pourra facilement y ajouter de nouveaux fichiers comme road-map.md plus tard » (dit)
- **Ce qui entre** : « tous les problèmes non résolus » (dit) — pas seulement la section « Dette
  induite » du rapport d'audit. Le hors-périmètre assumé au brief et les constats jamais arbitrés
  y ont leur place au même titre. Filtrage à l'entrée volontairement large : « je peux toujours
  les supprimer plus tard si non pertinente » (dit) — l'élagage est un geste de l'utilisateur.

## Décisions

- **Pas de numérotation des entrées** : « oblige une réindexation à chaque retrait » (dit).
  Identification par **horodatage**, entrées ordonnées **de la plus ancienne à la plus récente**
  (dit) — donc ajout en fin de fichier. Une entrée se référence par son intitulé, comme le fait
  déjà le modèle dans ses blocs de solde.
- **Les dettes soldées partent dans un fichier à part**, « pour éviter le gonflement de dette
  technique » (dit) — l'historique des soldes ne reste pas en tête du fichier de dette, contrairement
  au modèle. Emplacement : `todo/technical-debt-solde.md`, à côté du fichier de dette (dit), pour
  que le répertoire reste le point d'entrée unique du sujet.
- **L'abandon d'un chantier alimente `todo/` à la demande** : le pipeline le propose, l'utilisateur
  tranche au cas par cas (dit). Pas d'alimentation automatique sur abandon.
- **L'orchestrateur écrit, à la clôture, une seule fois** (dit). Il est le seul à avoir vu les
  audits successifs, à savoir lequel fait foi, à connaître les arbitrages de l'utilisateur
  (« clore avec ces réserves ») et donc à pouvoir remplir le champ **Assumé** — qui n'est jamais
  dans le code. Contrepartie assumée : l'auteur du code reporte ses propres dettes. Ce qui la rend
  tenable est que chaque constat du rapport porte son `R<n>` (dépôt: audit.md:130), donc la
  complétude est vérifiable après coup par confrontation rapport ↔ `todo/`.

## Incertitudes à lever en plan

- **Qui constate qu'une entrée est soldée.** Le déplacement vers `technical-debt-solde.md` est un
  geste de l'orchestrateur à la clôture d'un chantier ultérieur — donc, à nouveau, l'auteur du
  travail qui juge son propre solde. L'auditeur pourrait le constater (il a le droit de lire
  `todo/`, seule l'écriture lui est fermée), mais rien ne le lui demande aujourd'hui et le lui
  demander l'oblige à connaître un fichier hors de son mandat. À trancher en plan.
