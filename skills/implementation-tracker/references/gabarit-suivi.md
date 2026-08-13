# Gabarit du fichier de suivi

Fichier : `.claude/implementation/<slug>.md`

Créé à l'Étape 2 une fois le plan validé, maintenu en continu pendant l'implémentation
(Étape 4), archivé en `done/` à la clôture (Étape 5).

Contraintes de forme :

- **Le slug vient du brief**, jamais réinventé : c'est lui qui apparie les deux fichiers.
- `## Objectif et périmètre` est **repris du brief**, pas reformulé.
- Format d'étape : `- [état] N. Intitulé — <fichier> — vérif: <commande>` (règles de granularité
  et de délégabilité : Étape 2, point 4 du skill).
- Date obtenue par `date +%F`, jamais devinée.

---

```markdown
---
slug: auth-refactor
titre: Refonte de l'authentification
branche: auth-refactor      # branche d'implémentation = <slug>
base: main                  # branche principale, cible de l'aplatissement final (Étape 5)
statut: en-cours            # en-cours | bloqué | terminé
session: 3                  # incrémenté à chaque reprise (Étape 3)
execution: délégué          # délégué | direct — repris du brief, cf. Étape 4
plan: .claude/plans/refonte-auth-lucky-beaver.md
brief: .claude/implementation/auth-refactor.brief.md
créé: 2026-07-12
maj: 2026-07-12
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : … (ce qui était vécu à l'origine — sert à détecter la bonne solution au mauvais problème)
**But** : …
**Critères de réussite** : … (mesurables : tests qui passent, comportement observable)
**Hors-périmètre** : … (explicite — ce qu'on ne fait PAS dans ce chantier)
**Signaux de dérive** : … (déclencheurs d'arrêt pendant l'implémentation, cf. Étape 4)

## Étapes

- [x] 1. Extraire `TokenStore` — `src/auth/token.rs` — vérif: `cargo test auth::token`
- [>] 2. Brancher le middleware — `src/mw/auth.rs` — vérif: `cargo test mw::auth`
- [ ] 3. Migrer les tests — `tests/auth/` — vérif: `cargo test --test auth`
- [!] 4. Rotation des clés — `src/auth/keys.rs` — vérif: `cargo test auth::keys` — BLOQUÉ : attente décision infra

## État courant

**Prochaine action** : …
**Vérification** : `cargo test auth`   (vérification d'ensemble, distincte de celles par étape)
**Notes** : …

## Journal de décisions

- **2026-07-12** — JWT plutôt que sessions serveur. *Pourquoi* : scale horizontal sans état partagé.
  *Rejeté* : sessions Redis (dépendance d'infra supplémentaire).
```

---

## Notes de remplissage

**Symptôme** — c'est lui qui permet, trois sessions plus tard, de voir qu'on a construit la
bonne solution au mauvais problème. Une section `## Objectif et périmètre` sans symptôme a
perdu le lien avec l'intention d'origine.

**Étapes** — l'intitulé seul ne suffit pas à exécuter : c'est le plan (`plan:`) qui décrit
l'étape. Le suivi porte l'état, le plan porte le contenu.

**État courant** — écrit pour la reprise à froid, en début de session suivante. « Prochaine
action » se lit sans avoir à relire le plan.

**Journal** — que ce qui contraint le futur. Les micro-choix n'y entrent pas.
