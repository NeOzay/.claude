---
slug: contrat-pipeline
titre: Noyau de contrat partagé du pipeline, et garde-fou qui le vérifie
statut: validé
execution: direct
créé: 2026-08-14
---

## Intention

**Symptôme** : « comment peut-on optimiser la taille et l'interopérabilité de tous ces skills ? »
(dit). L'analyse du 2026-08-14 a écarté la taille comme levier — le corpus du pipeline fait
~1830 lignes et sa prose de justification est porteuse — et retenu la **dérive** : une règle du
pipeline est définie en moyenne dans 3,6 fichiers, et deux dérives en sont déjà sorties, toutes
deux au registre de dette (contrats divergents sur la racine du dépôt ; champs `plan:` / `brief:` /
`audit:` morts après archivage).

**But** : ramener chaque règle partagée à un point d'édition unique (P2), et rendre le contrat
vérifiable par un exécutable plutôt que par relecture (C).

## Critères de réussite

- `bash scripts/check-pipeline.sh` sort en **code 0** sur l'arbre du chantier — le garde-fou ne
  laisse aucun rouge derrière lui (cf. hors-périmètre : les dettes qu'il révèle sont soldées ici).
- Chaque règle du tableau des duplications relevé le 2026-08-14 (arborescence, `execution:`,
  `date +%F`, règle du slug, contrat de sous-agent, autorité brief/suivi, format d'étape, filtre de
  listing) n'a **qu'un seul lieu de définition** ; les autres lieux portent un renvoi ancré. Le
  script le vérifie en cherchant les formulations canoniques hors du noyau.
- **Aucune ancre morte** : chaque `contrat.md#…` cité résout vers un titre existant — contrôlé par
  le script.
- Le filtre de listing des suivis actifs **filtre réellement** : il n'a jamais remonté un
  `.brief.md` ni un `.audit.md` (contrôlé par le script, sur le répertoire réel).
- `grep -l 'contrat' agents/*.md` → **aucun résultat** : les agents n'ont pas été rendus dépendants
  du noyau.
- Les quatre entrées de dette visées ne sont plus dans `todo/technical-debt.md` et figurent dans
  `todo/technical-debt-solde.md`, chacune avec la commande exécutée qui l'établit.

## Hors-périmètre

**Dans le périmètre, tranché** : les entrées de dette que le contrat et le script rendent
mécaniquement visibles sont **soldées dans ce chantier** — « On les solde » (dit). Concernées :
le filtre de listing cassé dans ses 3 copies, les champs `plan:` / `brief:` / `audit:` morts après
archivage, l'archive `done/2026-08-14-linked-toasting-graham.md` mal nommée, la divergence
auteur/appelant sur la racine du dépôt. Le script ne doit pas sortir en rouge à sa première
exécution.

- **`git-smart-commit` n'est pas dégraissé** — ses ~150 lignes de rappel générique (tableaux
  `git status` et Conventional Commits, « bonnes pratiques ») et sa `description` de 13 lignes
  restent en l'état : « ce skill est chargé uniquement en fin de session, un gain de taille a peu
  d'impact » (dit). Il n'est touché que si une règle du noyau l'y oblige.
- **Les deux agents ne sont pas dédupliqués** (voir contraintes) — ils sont lus comme référence de
  contrôle, pas modifiés pour pointer vers le noyau.
- **La taille du corpus n'est pas un objectif.** Le chantier vise les points d'édition, pas les
  lignes ; le contrat peut faire grossir le total sans que ce soit un échec.
- `skills/emmylua-ls/` et `skills/nvim-mini-test/` sont hors pipeline — jamais touchés.

## Signaux de dérive

- **Si la même instruction se retrouve dupliquée dans tous les skills, c'est raté** — « le plus
  gênant serait une duplication des instructions dans tous les skills » (dit). C'est le mode
  d'échec du contrat ajouté sans qu'aucune copie ne soit retirée : un fichier de plus, zéro point
  d'édition supprimé.

## Contraintes connues de l'utilisateur

- **P2 et C forment un seul chantier** : « Ok P2 + C » (dit). Un contrat non vérifié dérive comme
  le reste — c'est déjà ce qui est arrivé aux trois copies du filtre de listing (dit, analyse
  acceptée le 2026-08-14).
- **Le noyau porte ce qui est *défini* plusieurs fois, jamais ce qui est *appliqué* plusieurs
  fois** : « hors-périmètre » apparaît dans 9 fichiers et « signaux de dérive » dans 8, mais y sont
  utilisés, pas redéfinis — les déplacer viderait les fichiers de ce qui les rend opérants (dit,
  condition posée avec P2 et acceptée le 2026-08-14).
- **Les deux agents restent auto-suffisants**, leur redondance n'est pas dédupliquée : un
  `agents/*.md` se charge dans sa propre fenêtre et ne coûte rien à la session, et un agent en
  isolation qui ne suit pas un pointeur perd le garde-fou (dit, même acceptation).
- **Une règle déplacée laisse une ligne d'appel portant sa conséquence**, pas un vide (dit, même
  acceptation).
- **Précédent de style pour C** : `hooks/intent-brief-gate.sh` — en-tête `PORTÉE`, politique
  d'échec ouvert documentée, justification en commentaire (dépôt: hooks/intent-brief-gate.sh).
- **Le hook `rtk` ne réécrit que les appels Bash du modèle**, pas les commandes internes à un
  script : `intent-brief-gate.sh:31` exécute un `find -maxdepth -name -mmin` que le modèle ne peut
  pas lancer en ligne (dépôt: hooks/intent-brief-gate.sh:31, vérifié le 2026-08-14).
- **Aucune infrastructure de contrôle n'existe** : pas de `scripts/`, le seul exécutable du dépôt
  est le gate d'`intent-brief` (dépôt: ls racine, 2026-08-14).
- **Les skills du pipeline sont textuellement autonomes** : une seule référence croisée dans tout
  le corpus (dépôt: agents/implementation-auditor.md:95).
- **Les renvois désignent une section du fichier cible, pas seulement le fichier** : « les skills
  sont des fichiers md, donc il est possible d'indiquer une section de ce fichier pour faciliter la
  navigation dans nvim » (dit). Le renvoi doit être exploitable depuis l'éditeur, pas seulement
  compréhensible à la lecture.
- **Règle globale** : jamais de commit sans accord explicite (dépôt: CLAUDE.md).

## Décisions

- **Emplacement du noyau** : `skills/implementation-tracker/references/contrat.md` (tranché
  2026-08-14). Le tracker est l'orchestrateur et porte déjà l'arborescence ; la référence croisée
  depuis une autre skill est déjà pratiquée (dépôt: agents/implementation-auditor.md:95).
  *Rejeté* : `rules/` avec scope `paths:` — rendrait le contrat résident et détournerait un
  répertoire dédié au style de code ; emplacement neutre — orphelin sans propriétaire.
- **Déclenchement du garde-fou** : script lançable à la main **et** appelé depuis
  `references/cloture.md`, à côté de l'audit (tranché 2026-08-14). *Rejeté* : hook sur édition des
  skills — se déclencherait hors chantier ; manuel seul — un contrôle qu'on doit penser à lancer
  ne se lance pas.
- **Renvois** : lien markdown avec ancre, `[Autorité](contrat.md#autorité)` (tranché 2026-08-14).
  Suivable depuis nvim, et une ancre morte devient une erreur détectable par le script — la forme
  du renvoi devient elle-même vérifiable. *Rejeté* : la prose actuelle du dépôt, qui se lit mais
  ne se suit ni ne se vérifie.

## Incertitudes à lever en plan

- **La liste exacte des contrôles du script.** Le tableau des duplications donne les candidats, et
  les critères de réussite en imposent quatre. Reste à arrêter ce qui est vérifiable de façon
  stable : un contrôle qui produit des faux positifs sera désactivé au premier chantier, et le
  garde-fou mourra là.
- **Le sort du renvoi en prose existant** — `agents/implementation-auditor.md:95` pointe vers une
  section en prose. Les agents étant hors-périmètre, ce renvoi reste-t-il tel quel, au prix d'une
  incohérence de forme avec le reste du dépôt ?
