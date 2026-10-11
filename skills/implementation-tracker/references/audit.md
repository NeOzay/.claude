# Audit d'implémentation

L'audit est rendu par le sous-agent `implementation-auditor` (Opus, contexte isolé), qui n'écrit
que son rapport. Il juge la conformité à l'intention, la qualité du code et la dette induite — et
**exécute lui-même** les commandes de vérification plutôt que de croire le suivi.

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

Trois points, comme le diff que l'auditeur lira : deux points compteraient aussi ce que `base` a
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

**Poser d'abord le rapport**, depuis la racine du dépôt, sur la branche du chantier :

```bash
audit new <slug> --intermediaire   # ou --cloture
```

La commande écrit `.claude/implementation/<slug>.audit/<NN>-<sha>.toml` et affiche son chemin :
l'en-tête tiré du suivi et de git, la Dette précédente et les cumuls repris du dernier rapport, la
revue posée depuis le brief, et les vérifications des étapes cochées, **exécutées d'avance** avec
leur sortie. Le reste est au Marqueur, pour l'auditeur. Elle sort en 1, en nommant la cause, hors
de la branche du chantier, ou quand le dernier rapport du répertoire n'est pas rempli — un audit
interrompu, à supprimer avant d'en poser un autre.

Transmettre ensuite à l'agent le **chemin absolu du rapport** et la racine du dépôt, et **rien
d'autre** : l'en-tête lui donne le reste, et il lit le plan, le diff et le code lui-même. Règles
générales de l'appel — chemins absolus, racine du dépôt, ce qu'on ne recopie jamais :
[Contrat des sous-agents](contrat.md#contrat-des-sous-agents).

---

## Au retour

**Contrôle préalable**, avant de lire le verdict :

```bash
audit check --filled <rapport>
```

Sortie non nulle → le rapport n'est pas rendu : relancer l'agent sur le même rapport, avec les
fautes nommées. Et un rapport dont `VÉRIFICATIONS` ne porte aucune sortie de commande réelle n'est
pas un audit : relancer l'agent, ou exécuter les commandes soi-même avant de conclure. Un verdict
rendu sans exécution vaut celui qu'on cherchait à remplacer.

Puis, dans tous les cas, **inscrire dans le suivi**, sans l'annoncer :

- `## État courant` → `**Dernier audit** : <sha> — <VERDICT> — <date>`
- frontmatter → `audit = ".claude/implementation/<slug>.audit"`, au premier audit du chantier
- `maj` actualisé.

Le raisonnement reste dans le rapport : le suivi porte le verdict, le rapport porte le pourquoi.

**Exporter le rapport** pour qu'il se lise, dans le scratchpad de la session — jamais dans le
dépôt, où l'export doublerait le rapport :

```bash
audit export <rapport> <scratchpad>
```

La commande nomme l'export `<slug>-<NN>-<sha>.md`, et affiche son chemin complet.

**Restituer** en une ligne — verdict et chemin complet de l'export —, puis, s'il y a des réserves,
le tableau `# | Réserve | Gravité réelle`, avec un commentaire court par réserve : ce qu'elle coûte
vraiment, que le rapport ne pèse pas.

```md
L'audit de clôture rend **RÉSERVES** : `/tmp/…/scratchpad/dump-sessions-02-a1b2c3d.md`.

| # | Réserve | Gravité réelle |
|---|---|---|
| R1 | Le résumé de compaction est compté comme un tour. | Fausse `tours`. |
```

Le reste du rapport, l'utilisateur le lit dans l'export.

**Une dette que l'utilisateur écarte** — un critère invérifiable qu'il valide, une réserve qu'il
renonce à payer — s'écrit, sur son accord et par l'orchestrateur, en `## Dettes écartées` du
suivi : `- R<n> — justificatif — date`. L'audit suivant la range en Dette écartée par
`audit range`, qui lit la ligne ; sans elle, la dette reste actuelle.

**Rien ne part dans le registre de dette au retour de l'audit.** Les constats y sont versés à la
clôture, en une seule passe — un audit intermédiaire qui alimenterait le registre ferait écrire deux
fois le même constat, puisque l'audit de clôture rejuge le diff entier depuis le début. Le
raisonnement complet : `dette.md`, « Un état, pas un journal ».

| Verdict | Suite |
|---|---|
| `FAVORABLE` | La clôture continue. |
| `RÉSERVES` | Restituer les réserves à l'utilisateur et **le laisser trancher** entre clore avec, ou traiter d'abord. Ne pas décider à sa place. |
| `DÉFAVORABLE` | `statut = "bloqué"`, verdict et SHA au journal. **Ne pas toucher aux étapes** : le traitement des remarques se décide au cas par cas avec l'utilisateur. La clôture s'arrête là. |

Un verdict défavorable n'est pas un échec du chantier : c'est l'information qui manquait. Le
corriger en silence, ou requalifier ses constats en détails, annule tout le dispositif.

Après traitement, **relancer un audit complet** — pas une vérification partielle des seuls points
soulevés : le correctif a produit un nouveau diff, qui n'a jamais été jugé.

---

## Le rapport

Un fichier TOML par audit : `.claude/implementation/<slug>.audit/<NN>-<sha>.toml`, `NN` le rang de
l'audit dans le chantier, `sha` le commit audité. Le répertoire n'est commité qu'à l'aplatissement,
archivé en `done/` avec le suivi.

Son format est le modèle de `skills/implementation-tracker/scripts/rapport_audit/modele.py`, et
nulle part ailleurs : l'en-tête, les vérifications exécutées, la revue du brief point par point,
quatre tableaux de dettes, le verdict en dernier.

| Tableau | Ce qu'il porte |
|---|---|
| `dette.precedente` | la Dette actuelle de l'audit d'avant, copiée par `audit new` |
| `dette.actuelle` | ce qui reste à l'heure de l'audit : dettes précédentes rangées là, dettes neuves |
| `dette.corrigee` | cumul : chaque dette dont un audit a constaté la correction, avec sa preuve |
| `dette.ecartee` | cumul : chaque dette que l'utilisateur a écartée, avec son justificatif |

Chaque dette précédente se range dans l'un des trois autres tableaux, et rien ne sort d'un cumul :
**le dernier rapport porte tout l'état du chantier**, et aucun audit n'a à relire les plus anciens.
Un `R<n>` ne désigne qu'une dette dans tout le chantier.

**Le verdict suit la sévérité réelle de la Dette actuelle**, écrit par l'auditeur, vérifié par
`audit check` : `DÉFAVORABLE` dès une dette `bloquant` ou `critique`, `RÉSERVES` dès une `majeur`,
`FAVORABLE` sans rien au-dessus de `note` ; des `avertissement` laissent le choix entre `RÉSERVES`
et `FAVORABLE`, justifié. `bloquant` est propre à l'audit et n'entre jamais au registre de dette.
