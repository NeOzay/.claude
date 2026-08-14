# Audit intègre du pipeline de skills

## Contexte

Le pipeline `intent-brief → plan → implementation-tracker → step-implementer → git-smart-commit`
possède des points de contrôle, mais tous sont confiés au modèle qui vient de produire le travail :
confrontation plan ↔ brief (`intent-brief` Étape 7), bloc `VÉRIFICATION` auto-déclaré par
`step-implementer` (`agents/step-implementer.md:80`), confrontation aux critères de réussite à la
clôture (`skills/implementation-tracker/references/cloture.md:8`). Aucun ne laisse de trace
versionnée : le brief a un fichier, le plan a un fichier, le suivi a un fichier — les verdicts n'ont
rien. Le seul audit outillé, `git-pre-commit-audit`, est un grep de secrets qui ne lit ni le brief ni
les critères.

Résultat attendu : un audit rendu par un sous-agent indépendant qui **rejoue lui-même** les
commandes de vérification au lieu de croire le suivi, dont le rapport est versionné, et dont l'avis
favorable conditionne la clôture.

Brief : `.claude/implementation/audit-integre.brief.md` (validé le 2026-08-14).

## Décisions de cadrage

- Agent + référence du tracker, **pas** de sixième skill — l'audit est un moment du chantier.
- Auditeur en **Opus** : il juge, là où `step-implementer` exécute un plan déjà tranché.
- Blocage par **discipline écrite** dans `cloture.md`, pas de hook.
- Seuil de l'audit intermédiaire : **400 lignes** changées entre `base:` et `<slug>`, avec le
  nombre d'étapes restantes annoncé dans la proposition.
- Rapport dans `.claude/implementation/<slug>.audit.md` ; le suivi ne porte que SHA, verdict, renvoi.
- Verdict défavorable → `statut: bloqué` + journal ; **les étapes ne sont pas touchées**.

## Étapes

### 1. Débrancher `git-pre-commit-audit`

`git mv skills/git-pre-commit-audit archive/git-pre-commit-audit` — hors du répertoire scanné, donc
non appelable par le modèle comme par l'utilisateur, contenu préservé pour le chantier suivant
(reprise des patterns de sécurité). Aucune référence croisée à corriger : le grep sur le dépôt ne
sort que le brief.

### 2. `agents/implementation-auditor.md`

Miroir de `step-implementer`, côté jugement. Frontmatter : `model: opus`, `tools: Read, Grep, Glob,
Bash, Write`.

**Entrée** (transmise par l'appelant) : chemins absolus du suivi et du brief, `base:`, `<slug>`, SHA
de `HEAD` sur la branche, type d'audit (`intermédiaire` | `clôture`). Il lit lui-même le plan via
`plan:` et construit le diff par `git diff <base>...<slug>`.

**Objet du jugement**, dans cet ordre :

1. *Conformité à l'intention* — chaque critère de réussite du brief, le hors-périmètre, les signaux
   de dérive, et la disparition du symptôme d'origine.
2. *Qualité du code produit* — cas limites, gestion d'erreurs, respect du style des fichiers voisins.
3. *Dette technique induite* — duplication, abstraction créée sans nécessité.

**Point d'intégrité** : il **exécute** les commandes de vérification des étapes et les critères de
réussite du brief, et rapporte leur sortie réelle. C'est ce qui le distingue d'une relecture — le
suivi peut affirmer qu'une commande passe, l'auditeur le constate.

**Interdits** — mêmes gardes que `step-implementer`, plus un : aucune commande `git` autre que de
lecture ; **ne corriger aucun code**, même un défaut évident (signal de dérive du brief) ; le seul
fichier qu'il a le droit d'écrire est `.claude/implementation/<slug>.audit.md`, en y **appendant**
son rapport sans effacer les audits antérieurs.

**Sortie** — rapport détaillé dans le fichier, et bloc court en retour de session :

```
VERDICT : FAVORABLE | RÉSERVES | DÉFAVORABLE
COMMIT : <sha>
RAPPORT : .claude/implementation/<slug>.audit.md
VÉRIFICATIONS : <commande → verdict réel, une par ligne>
BLOQUANTS : <ce qui interdit la clôture — sinon "aucun">
```

Écrire le détail dans le fichier plutôt que dans la réponse garde le rapport hors du contexte de la
session, comme la délégation d'étape garde les diffs hors contexte.

### 3. `skills/implementation-tracker/references/audit.md`

La procédure côté appelant, plus le gabarit de `<slug>.audit.md`. Contenu :

- **Quand** : obligatoire avant toute clôture ; proposé — jamais imposé — quand
  `git diff --shortstat <base>..<slug>` dépasse 400 lignes changées, la proposition indiquant le
  nombre d'étapes restantes pour que l'arbitrage soit informé.
- **Quoi transmettre** à l'agent, et rien d'autre (il lit le reste lui-même).
- **Au retour** : inscrire SHA + verdict + renvoi dans le suivi ; `FAVORABLE` → la clôture continue ;
  `RÉSERVES` → restituer les réserves et laisser trancher ; `DÉFAVORABLE` → `statut: bloqué`, verdict
  et SHA au journal, **étapes intactes**, et le traitement se décide avec l'utilisateur.
- **Gabarit du rapport** : frontmatter `slug`, puis une section par audit — date, commit, type,
  verdict, constats par axe, bloquants.
- **Contrôle de l'appelant** : un rapport dont la section `VÉRIFICATIONS` n'a pas de sortie réelle
  n'est pas un audit — relancer.

### 4. `skills/implementation-tracker/SKILL.md`

- Bloc « Emplacement » : ajouter `<slug>.audit.md` et son archivage en `done/`.
- Étape 0 : exclure les `*.audit.md` des listings, comme les `*.brief.md` (deux `grep -v` à étendre).
- Étape 4, tableau des déclencheurs : nouvelle ligne — diff branche/base au-delà de 400 lignes →
  proposer un audit intermédiaire (renvoi vers `references/audit.md`).
- Étape 5 : mentionner que la clôture exige un avis favorable.

### 5. `skills/implementation-tracker/references/cloture.md`

- Insérer l'audit en **point 1**, avant le contrôle des étapes : c'est lui qui rejoue les critères de
  réussite, la confrontation manuelle actuelle (`cloture.md:8`) devient le contrôle du rapport.
- Poser explicitement qu'une clôture sans avis favorable ne va pas au bout.
- Point 3 : ajouter `<slug>.audit.md` à la boucle de déplacement vers `done/` — il rejoint le brief
  et le plan, même repli `mv` + `git add` s'il n'est pas suivi.

### 6. `skills/implementation-tracker/references/gabarit-suivi.md`

- Frontmatter : champ `audit: .claude/implementation/<slug>.audit.md`.
- `## État courant` : ligne `**Dernier audit** : <sha> — <VERDICT> — <date>`.
- Note de remplissage : le suivi porte le verdict, le fichier d'audit porte le raisonnement.

### 7. Rodage sur ce chantier même

Faire tourner `implementation-auditor` sur `audit-integre` avant sa propre clôture. C'est le seul
essai réel possible — un dispositif d'audit qui ne s'applique pas à lui-même n'a jamais été testé.

## Vérification

Pas de suite de tests : le chantier produit du markdown de prompt. Contrôles de bout en bout :

```bash
ls skills/ | grep -c git-pre-commit-audit    # → 0
ls archive/git-pre-commit-audit/SKILL.md     # → présent
```

- Ouvrir une session neuve : `git-pre-commit-audit` n'apparaît plus dans les skills disponibles et
  `/git-pre-commit-audit` n'existe plus.
- Critère décisif — étape 7 : l'audit de `audit-integre` produit un `.audit.md` versionné, un verdict
  dans le suivi, et la clôture s'y subordonne. Si l'auditeur rend un verdict sans avoir exécuté de
  commande, le dispositif a échoué et l'étape 2 est à reprendre.

## Hors-périmètre

Reprise des fonctionnalités de `git-pre-commit-audit` (secrets, patterns de sécurité par langage) :
chantier suivant, pas celui-ci.
