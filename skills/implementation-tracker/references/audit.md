# Audit d'implémentation

L'audit est rendu par le sous-agent `implementation-auditor` (Opus, contexte isolé, lecture seule).
Il juge la conformité à l'intention, la qualité du code et la dette induite — et **exécute lui-même**
les commandes de vérification plutôt que de croire le suivi.

Il est indépendant par construction : il n'a pas écrit le code et n'a pas le droit d'y toucher.
C'est la seule chose que la session de cadrage ne peut pas fournir, quel que soit son sérieux.

---

## Quand auditer

**Avant toute clôture — obligatoire.** Pas de clôture sans avis favorable (voir `cloture.md`).

**En cours de chantier — proposé, jamais imposé.** Quand le diff de la branche dépasse **400 lignes
changées** :

```bash
git diff --shortstat <base>...<slug>
```

Trois points, comme le diff que l'auditeur lira : deux points compteraient aussi ce que `base:` a
bougé pendant le chantier, et le seuil se déclencherait sur des lignes que l'audit ne regarde pas.

Proposer alors un audit intermédiaire, en indiquant **le nombre d'étapes restantes** — c'est ce qui
rend l'arbitrage informé : 400 lignes à deux étapes de la fin ne se traitent pas comme 400 lignes à
mi-chantier.

> Diff de la branche : 612 lignes changées, 3 étapes restantes sur 7.
> Un audit intermédiaire maintenant ? Les remarques sont encore actionnables.

Attendre la réponse. Un refus ne se re-propose pas à chaque étape suivante : n'y revenir qu'une
fois, si le diff a de nouveau doublé.

---

## Lancer l'audit

Transmettre à l'agent, et **rien d'autre** — il lit le plan, le diff et le code lui-même :

- chemins **absolus** du fichier de suivi et du brief,
- **racine du dépôt** (`git rev-parse --show-toplevel`) — c'est par rapport à elle qu'il résoudra
  `plan:` et le chemin d'écriture de son rapport ; sans elle, sur un dépôt où le répertoire courant
  n'est pas la racine, le rapport atterrit à côté,
- `base:` et `<slug>` (nom de la branche de chantier),
- SHA de `HEAD` sur la branche (`git rev-parse HEAD`),
- le type d'audit : `intermédiaire` ou `clôture`.

L'appelant ne recopie ni le diff, ni les critères, ni les étapes : tout est dans les fichiers, et le
recopier reviendrait à lui transmettre sa propre lecture — exactement ce que l'audit existe pour
éviter.

---

## Au retour

**Contrôle préalable** : un rapport dont `VÉRIFICATIONS` ne porte aucune sortie de commande réelle
n'est pas un audit. Relancer l'agent, ou exécuter les commandes soi-même avant de conclure. Un
verdict rendu sans exécution vaut celui qu'on cherchait à remplacer.

Puis, dans tous les cas, **inscrire dans le suivi** :

- `## État courant` → `**Dernier audit** : <sha> — <VERDICT> — <date>`
- frontmatter → `audit: .claude/implementation/<slug>.audit.md`, au premier audit du chantier
- `maj:` actualisé.

Le raisonnement reste dans `<slug>.audit.md` : le suivi porte le verdict, le fichier d'audit porte
le pourquoi.

**Rien ne part dans le registre de dette au retour de l'audit.** Les constats y sont versés à la
clôture, en une seule passe — un audit intermédiaire qui alimenterait le registre ferait écrire deux
fois le même constat, puisque l'audit de clôture rejuge le diff entier depuis le début. Le
raisonnement complet : `dette.md`, « Un état, pas un journal ».

| Verdict | Suite |
|---|---|
| `FAVORABLE` | La clôture continue. |
| `RÉSERVES` | Restituer les réserves à l'utilisateur et **le laisser trancher** entre clore avec, ou traiter d'abord. Ne pas décider à sa place. |
| `DÉFAVORABLE` | `statut: bloqué`, verdict et SHA au journal. **Ne pas toucher aux étapes** : le traitement des remarques se décide au cas par cas avec l'utilisateur. La clôture s'arrête là. |

Un verdict défavorable n'est pas un échec du chantier : c'est l'information qui manquait. Le
corriger en silence, ou requalifier ses constats en détails, annule tout le dispositif.

Après traitement, **relancer un audit complet** — pas une vérification partielle des seuls points
soulevés : le correctif a produit un nouveau diff, qui n'a jamais été jugé.

---

## Gabarit du rapport

Fichier : `.claude/implementation/<slug>.audit.md`. Les audits successifs s'y **appendent**, du plus
ancien au plus récent.

```markdown
---
slug: auth-refactor
---

## 2026-07-20 — clôture — `a1b2c3d`

**Verdict** : RÉSERVES

### Vérifications exécutées

- `cargo test auth` → 47 passés, 0 échec
- `cargo test mw::auth` → 12 passés, 0 échec
- critère « un token expiré renvoie 401 » → NON EXÉCUTÉE : nécessite un serveur lancé

### Conformité à l'intention

- Critère « `cargo test auth` passe » : atteint, vérifié.
- Critère « token expiré → 401 » : invérifiable en l'état — code lu, chemin correct, non exécuté.
- Hors-périmètre : respecté, `legacy/` intact.
- Signaux de dérive : aucun matérialisé.
- Symptôme d'origine : disparu.

### Qualité du code

- **R1** — `src/auth/token.rs:88` — l'erreur de désérialisation est avalée en `None`, un token
  corrompu devient indistinguable d'un token absent.

### Dette induite

- **R2** — `verify_claims()` duplique la validation d'expiration déjà dans `Claims::is_valid()`.

### Bloquants

Aucun.
```

Une section par audit. Un axe sans constat s'écrit « rien à signaler » — une section absente ne se
distingue pas d'un axe oublié.

**Chaque constat porte son numéro `R<n>` là où il est posé**, dans l'ordre du rapport et toutes
sections confondues. Un constat développé sous un titre à lui, sans numéro, mais cité par numéro
ailleurs, est introuvable pour qui lit le rapport.
