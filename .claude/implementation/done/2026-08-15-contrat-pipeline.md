---
slug: contrat-pipeline
titre: Noyau de contrat du pipeline, et garde-fou qui le vérifie
branche: contrat-pipeline
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-08-15-contrat-pipeline.plan.md
brief: .claude/implementation/done/2026-08-15-contrat-pipeline.brief.md
audit: .claude/implementation/done/2026-08-15-contrat-pipeline.audit.md
créé: 2026-08-14
maj: 2026-08-15
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : « comment peut-on optimiser la taille et l'interopérabilité de tous ces skills ? ».
L'analyse du 2026-08-14 a écarté la taille comme levier et retenu la **dérive** : une règle du
pipeline est définie en moyenne dans 3,6 fichiers, et deux dérives en sont déjà sorties, toutes
deux au registre de dette (contrats divergents sur la racine du dépôt ; champs `plan:` / `brief:` /
`audit:` morts après archivage).

**But** : ramener chaque règle partagée à un point d'édition unique (P2), et rendre le contrat
vérifiable par un exécutable plutôt que par relecture (C).

**Critères de réussite** :

- `bash scripts/check-pipeline.sh` sort en **code 0** sur l'arbre du chantier.
- Chaque règle du tableau des duplications n'a **qu'un seul lieu de définition** ; les autres lieux
  portent un renvoi ancré. Contrôlé par le script (formulations canoniques hors du noyau).
- **Aucune ancre morte** : chaque `contrat.md#…` cité résout vers un titre existant.
- Le filtre de listing des suivis actifs **filtre réellement** : jamais de `.brief.md` ni
  `.audit.md` remonté.
- `grep -l 'contrat' agents/*.md` → aucun résultat : les agents ne dépendent pas du noyau.
- Les quatre entrées de dette visées sont passées dans `todo/technical-debt-solde.md`, chacune avec
  la commande exécutée qui l'établit.

**Hors-périmètre** :

- `git-smart-commit` n'est pas dégraissé — touché seulement si une règle du noyau l'y oblige.
- Les deux agents ne sont pas dédupliqués ni rendus dépendants du noyau.
- **La taille du corpus n'est pas un objectif** : le contrat peut faire grossir le total sans que
  ce soit un échec.
- `skills/emmylua-ls/` et `skills/nvim-mini-test/` ne sont jamais touchés.

**Signaux de dérive** :

- **Si la même instruction se retrouve dupliquée dans tous les skills, c'est raté.** C'est le mode
  d'échec du contrat ajouté sans qu'aucune copie ne soit retirée : un fichier de plus, zéro point
  d'édition supprimé. → s'arrêter et en reparler.

## Étapes

- [x] 1. Écrire le noyau, sept sections ancrées, sans toucher aux appelants — `skills/implementation-tracker/references/contrat.md` — vérif: `grep -c '^## ' skills/implementation-tracker/references/contrat.md` → 7
- [x] 2. Commande de listing canonique — `skills/implementation-tracker/scripts/impl-list.sh` — vérif: `bash "$HOME/.claude/skills/implementation-tracker/scripts/impl-list.sh" .claude/implementation/done | grep -cE '\.(brief|audit|plan)\.md'` → 0
- [x] 3. Brancher le tracker : Étape 0 et Cas C appellent le script, les règles définies au noyau deviennent des renvois ancrés — `skills/implementation-tracker/SKILL.md` — vérif: `grep -c 'contrat.md#' skills/implementation-tracker/SKILL.md` ≥ 5
- [x] 4. Brancher `intent-brief` : slug, `execution:`, date, « Articulation » réduite à un renvoi — `skills/intent-brief/SKILL.md` — vérif: `grep -c 'contrat.md#' skills/intent-brief/SKILL.md` ≥ 3
- [x] 5. Brancher les gabarits et les références — `gabarit-suivi.md`, `gabarit-brief.md`, `audit.md`, `cloture.md`, `dette.md`, `squash.md` — vérif: `grep -rc 'contrat.md#' skills/*/references/ | grep -v ':0'`
- [x] 6. Écrire le garde-fou et ses cinq contrôles — `scripts/check-pipeline.sh` — vérif: `bash scripts/check-pipeline.sh; echo $?`
- [x] 7. Appeler le garde-fou depuis la procédure de clôture, à côté de l'audit — `skills/implementation-tracker/references/cloture.md` — vérif: `grep -n 'check-pipeline' skills/implementation-tracker/references/cloture.md`
- [x] 8. Solder les dettes révélées : champs `plan:`/`brief:`/`audit:` dans `done/`, renommage de l'archive `2026-08-14-linked-toasting-graham.md`, phrase sur la racine du dépôt dans l'agent — `done/*.md`, `cloture.md`, `agents/implementation-auditor.md` — vérif: `bash scripts/check-pipeline.sh` → code 0
- [x] 9. `R2` — rendre le listing portable : script déplacé dans la skill, appelé par chemin absolu — `skills/implementation-tracker/scripts/impl-list.sh`, `SKILL.md`, `contrat.md`, `scripts/check-pipeline.sh` — vérif: depuis un répertoire hors du dépôt, `bash $HOME/.claude/skills/implementation-tracker/scripts/impl-list.sh .claude/implementation` → code 0
- [x] 10. Réserves `R14`, `R16`, `R12` : vérif morte de l'étape 2, garde-fou pointé sur la copie du dépôt, contrôle 6 élargi aux quatre formes — `contrat-pipeline.md`, `scripts/check-pipeline.sh`, `contrat.md` — vérif: les 4 formes d'appel fautif injectées une à une → détectées ; `bash scripts/check-pipeline.sh` → code 0
- [x] 11. `R21` — le contrôle 6 accepte toutes les écritures de chemin absolu (`~/`, `$HOME/`, `${HOME}/`, `/`) — `scripts/check-pipeline.sh` — vérif: 4 formes fautives → détectées, 5 écritures légitimes → vertes

## État courant

**Chantier terminé**, clos avec les réserves du verdict `0c5a8fe` sur décision de l'utilisateur.

**Vérification** : `bash scripts/check-pipeline.sh` → **code 0**, six contrôles au vert
(2026-08-14).
**Dernier audit** : `0c5a8fe` — RÉSERVES — 2026-08-14 — voir `audit:` (précédents : `a8e3111`
DÉFAVORABLE et `801c9a8` RÉSERVES ; `R2`, `R12`, `R14`, `R16`, `R21` depuis levés)
**Registre de dette** : les 22 constats du rapport ont été repris un par un. Quatre entrées
antérieures soldées avec leur commande d'établissement, une élargie, dix ajoutées — 14 au total.

## Journal de décisions

- **2026-08-14** — Le noyau vit dans `skills/implementation-tracker/references/contrat.md`, cité par
  liens ancrés. *Pourquoi* : le tracker est l'orchestrateur et porte déjà l'arborescence ; une ancre
  morte devient une erreur détectable. *Rejeté* : `rules/` (rendrait le contrat résident), un
  emplacement neutre (orphelin sans propriétaire).
- **2026-08-14** — Le noyau porte ce qui est **défini** plusieurs fois, jamais ce qui est
  **appliqué** plusieurs fois ; une règle déplacée laisse une ligne d'appel portant sa conséquence.
  *Pourquoi* : sans cette borne, le contrat devient une doctrine que plus personne n'ouvre pendant
  que chaque skill réécrit l'essentiel.
- **2026-08-14** — Les deux agents restent auto-suffisants et ne renvoient pas au noyau.
  *Pourquoi* : ils se chargent dans leur propre fenêtre — la redondance n'y coûte rien, et un agent
  isolé qui ne suivrait pas un renvoi perdrait le garde-fou. Le contrôle 4 le vérifie.
- **2026-08-14** — Le contrôle 2 repose sur des **empreintes** : des formulations distinctives du
  corps d'une règle, jamais d'une ligne d'appel, vérifiées à **exactement une occurrence**.
  *Pourquoi* : 0 signale une règle disparue du contrat, ≥2 une règle recopiée. *Conséquence* : toute
  règle ajoutée au contrat doit recevoir son empreinte, sinon elle n'est pas protégée.
- **2026-08-14** — **Un contrôle qui n'examine rien échoue.** *Pourquoi* : un contrôle écrit avec un
  motif faux a affiché « aucun problème » au lieu de « je n'ai rien examiné ». Un garde-fou
  silencieusement vide est pire que pas de garde-fou.
- **2026-08-14** — Un script appelé depuis un skill se référence par chemin absolu ancré dans la
  skill, ou par un appel relatif **gardé sur ce même script**. *Pourquoi* : un skill s'invoque depuis
  n'importe quel dépôt ; un appel relatif nu y renvoie 127 et une sortie vide, que l'appelant lit
  comme un résultat. C'est le défaut qui a rendu le premier audit `DÉFAVORABLE`.
- **2026-08-14** — À l'archivage, un champ `plan:`/`brief:`/`audit:` dont la cible n'existe pas est
  **laissé tel quel**, pas réécrit. *Pourquoi* : le remplacer produirait un autre chemin mort avec
  l'air d'avoir été traité ; laissé en l'état, le garde-fou le signale.
- **2026-08-14** — Le rappel « jamais de commit sans accord » n'est pas réécrit dans les points
  d'application du tracker. *Pourquoi* : il est dans le contrat **et** dans `CLAUDE.md`, résident à
  chaque session. Ne pas le ré-ajouter.
- **2026-08-14** — Trois audits : `a8e3111` DÉFAVORABLE (bloquant `R2`, levé), `801c9a8` RÉSERVES
  (`R12`, `R14`, `R16` traités), `0c5a8fe` RÉSERVES (`R21` traité). Clôture décidée avec les réserves
  restantes ; les 22 constats ont été repris un par un et versés au registre de dette. Le correctif
  `R21` n'a pas été audité — inscrit au registre.
