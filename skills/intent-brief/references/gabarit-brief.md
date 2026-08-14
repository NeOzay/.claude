# Gabarit du brief

Fichier : `.claude/implementation/<slug>.brief.md`

Créé en `statut: brouillon` dès la fin de l'Étape 2, puis alimenté au fil des réponses : c'est lui
qui sert de **registre des ambiguïtés**. Passe en `statut: validé` quand l'utilisateur valide — il
est alors figé, la suite se journalise dans le fichier de suivi.

Contraintes de forme :

- **Une page maximum.** Au-delà, c'est un plan déguisé — le plan mode fait ce travail après.
- Rédigé **avec les mots de l'utilisateur**. La reformulation est le canal par lequel l'intention
  se perd.
- Marqueurs de source et interdiction de combler par plausibilité : voir « Règle du sourçage »
  du skill. Un axe non abordé s'écrit `— non abordé`.
- Date obtenue par `date +%F` (Étape 0) :
  [Dates et listing](../../implementation-tracker/references/contrat.md#dates-et-listing).
- Champs du frontmatter et valeurs admises :
  [Frontmatter](../../implementation-tracker/references/contrat.md#frontmatter).

---

```markdown
---
slug: auth-refactor
titre: Refonte de l'authentification
statut: brouillon
execution: délégué        # évalué en Étape 5, repris tel quel par le fichier de suivi
créé: 2026-08-10
---

## Intention

**Symptôme** : ce qui est vécu, dans les mots de l'utilisateur.
**But** : ce qu'on veut obtenir. Une ou deux phrases.

## Critères de réussite

Observables et vérifiables. Préférer une commande à une phrase : une commande se rejoue.

- `cargo test auth` passe
- un token expiré renvoie 401 au lieu d'un 500

## Hors-périmètre

Explicite. Ce qu'on ne fait PAS dans ce chantier.

- pas de migration de la base (dit)
- le module `legacy/` n'est pas touché (dit)

## Signaux de dérive

À quoi on reconnaît qu'on part dans la mauvaise direction. Repris dans le fichier de suivi comme
déclencheur d'arrêt pendant l'implémentation.

- si une nouvelle couche d'abstraction apparaît, c'est raté (dit)
- si le diff dépasse trois fichiers, s'arrêter et en reparler (dit)

## Contraintes connues de l'utilisateur

Ce que le dépôt ne dit pas.

- **Historique** : `TokenStore` déjà réécrit en juin, cassait le refresh concurrent (dit)
- **Intouchable** : la signature de `verify()` a des consommateurs hors dépôt (dit)
- **Réutiliser** : `crypto/hash.rs` existe déjà, ne pas recréer (dépôt: src/crypto/hash.rs)
- **Rejeté d'emblée** : pas de dépendance Redis (dit)

## Incertitudes à lever en plan

Registre vivant pendant le cadrage, mission explicite du plan ensuite. Toute ambiguïté y est
appendue dès qu'elle apparaît, dans sa formulation d'origine ; elle en sort quand elle est levée
ou tranchée.

- reste à déterminer si le middleware peut être branché sans casser l'ordre des couches
- « nettoyer le module » — périmètre resté indéfini, à borner avant de toucher au code
```

---

## Notes de remplissage

**Intention** — si le symptôme et le but ne se répondent pas, c'est le premier désalignement.
Le signaler avant d'écrire.

**Signaux de dérive** — section vide = axe non posé. Y revenir : c'est le meilleur rendement de la
grille, et le seul contenu du brief qui reste actif pendant l'implémentation.

**Contraintes** — n'y mettre que du non devinable. Une contrainte lisible dans le code encombre et
dilue le reste.

**Incertitudes** — une section vide n'est crédible que si le registre l'était : un cadrage qui ne
laisse rien d'ouvert a plus probablement effacé ses zones d'ombre que résolu.

**`execution:`** — seul champ du brief qui soit un jugement de l'assistant et non une affirmation
sourcée : la règle du sourçage ne s'y applique pas. Comment le trancher : Étape 5 du skill.
