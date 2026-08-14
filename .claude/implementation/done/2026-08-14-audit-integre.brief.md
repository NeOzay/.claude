---
slug: audit-integre
titre: Audit intègre du pipeline de skills
statut: validé
execution: direct
créé: 2026-08-14
---

## Intention

**Symptôme** : tous les points de contrôle du pipeline sont confiés au modèle qui vient de
produire le travail — confrontation plan ↔ brief (`intent-brief` Étape 7), bloc `VÉRIFICATION`
auto-déclaré par `step-implementer`, confrontation aux critères à la clôture
(`references/cloture.md:8`). Aucun ne laisse de trace versionnée. Le seul audit outillé,
`git-pre-commit-audit`, ne lit ni le brief ni les critères : c'est un grep de secrets.

**But** : un audit réalisé par un sous-agent indépendant, tracé dans le fichier de suivi, et
dont l'avis favorable conditionne la clôture.

## Critères de réussite

- `git-pre-commit-audit` n'est plus appelable, ni par le modèle ni par l'utilisateur
- un audit tourne systématiquement avant toute clôture d'implémentation
- l'audit est exécuté par un sous-agent, pas par la session de cadrage
- le fichier de suivi porte le commit audité (SHA) et le verdict
- une clôture sans avis favorable ne va pas au bout

## Hors-périmètre

- pas de remplacement de `git-pre-commit-audit` par un équivalent : il est débranché, et la
  reprise de ses fonctionnalités (secrets, patterns de sécurité) fera l'objet d'un prochain
  chantier (dit)

## Signaux de dérive

- si l'auditeur se met à corriger le code au lieu de le juger, c'est raté (dit)
- si le skill d'audit déborde d'une page, c'est raté (dit)
- si le dispositif rallonge la clôture au point qu'on l'esquive, c'est raté (dit)

## Contraintes connues de l'utilisateur

- **Débrancher, pas supprimer** : `git-pre-commit-audit` doit devenir non appelable par le
  modèle et par l'utilisateur (dit)
- **Audit par sous-agent** — l'exécution sort de la session de cadrage (dit)
- **Toujours avant la clôture** (dit)
- **Chantiers de grande envergure** : comparer la branche `<slug>` à `base:` ; au-delà de
  plusieurs centaines de lignes de diff, un audit intermédiaire peut être proposé — avec
  l'accord explicite de l'utilisateur (dit)
- **Traçabilité** : le commit audité est inscrit dans le fichier de suivi (dit)
- **Verdict négatif** : `statut: bloqué` dans le suivi, verdict et SHA au journal ; les étapes
  ne sont pas touchées — le traitement des remarques se décide au cas par cas avec
  l'utilisateur (dit, arbitrage 2026-08-14)
- **Rapport complet** dans un fichier dédié `.claude/implementation/<slug>.audit.md`, versionné
  et archivé en `done/` à la clôture ; le suivi ne porte que le SHA, le verdict et le renvoi.
  Les audits successifs s'y appendent (dit, arbitrage 2026-08-14)
- **La clôture exige un avis favorable** (dit)
- **Objet du jugement** : conformité à l'intention (critères de réussite, hors-périmètre,
  signaux de dérive), qualité du code produit, cas limites, dette technique induite —
  duplication notamment (dit)
- **Emplacement** : `.claude/implementation/` relatif au cwd, soit `~/.claude/.claude/`
  pour ce dépôt-ci, cohérent avec `plansDirectory` (dépôt: settings.json:92) (dit)

## Incertitudes à lever en plan

- « plusieurs centaines de lignes » comme seuil de l'audit intermédiaire — chiffre exact à
  arrêter dans le plan
