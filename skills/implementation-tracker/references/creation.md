# Phase 2 — Création (nouvelle implémentation)

**Prérequis : arbre de travail propre.** Si `git status --short` (Phase 0) n'est pas vide,
**ne pas créer** de nouvelle implémentation. **Exception : les `*.brief.md`.** Un brief produit par
`intent-brief` avant l'appel au tracker apparaît en `??` sans être une modification étrangère au
chantier — l'ignorer dans ce contrôle. Arrêter et indiquer qu'il ne doit y avoir aucune modification
en cours avant de démarrer un nouveau chantier — sinon les premiers commits de session mélangeraient
des changements étrangers à l'implémentation. Laisser l'utilisateur traiter ces modifications (les
committer ou les mettre de côté) avant de relancer.

1. **Cadrer l'intention avant de planifier** — invoquer le skill `intent-brief`. Il produit
   `.claude/implementation/<slug>.brief.md` : intention réelle, critères de réussite,
   hors-périmètre, contraintes non devinables, signaux de dérive. C'est lui qui pose les
   questions ; ne pas réinventer un questionnaire ici.

   Un brief validé existe déjà pour ce chantier → le lire et passer directement au point 2.

   **Pas de brief** (cadrage jugé inutile, cf. « Quand ne pas cadrer » d'`intent-brief`) →
   `brief` omis. Remplir `## Objectif et périmètre` avec l'utilisateur, en une passe.
2. **Entrer en plan mode** (`EnterPlanMode`), avec le brief comme cadre : rappeler
   explicitement au plan les critères de réussite, le hors-périmètre et les incertitudes à
   lever. Explorer le code et construire le plan normalement — c'est le flux natif qui fait
   le travail.

   **Chercher les Shadow-skills du Chantier** avant de construire le plan : `shadow-skill tags`,
   puis `shadow-skill cherche <mots>` sur les domaines que le plan touche, et
   `shadow-skill charge <nom>` pour ceux dont le `when-to-load` décrit le travail. Retenir leurs
   noms : ils iront dans le champ `skills` du Suivi (point 7).

   **Choisir le modèle de l'implémentation** : le plan porte une section `## Modèle`, le choix —
   Sonnet ou Opus — et sa justification en une phrase. Critères :
   [Modèle d'implémentation](contrat.md#modèle-dimplémentation).

   **C'est ici que le plan se construit, et nulle part ailleurs.** `intent-brief` s'arrête au
   brief validé : il ne planifie pas et ne confronte pas.
3. **Faire relire le plan avant de le présenter.** Le harness assigne un fichier de plan dès
   l'entrée en plan mode et en autorise l'écriture : y écrire le plan, puis lancer le sous-agent
   `plan-reviewer` **avant `ExitPlanMode`**.

   Lui transmettre trois chemins **absolus** — racine du dépôt, fichier de plan, brief — et
   **rien d'autre** : il lit tout lui-même.
   [Contrat des sous-agents](contrat.md#contrat-des-sous-agents).

   **Pas de brief** → le lui dire explicitement : il ne jugera alors que la qualité du plan.

   Pourquoi avant, et non après : celui qui vient d'écrire le plan est le plus mal placé pour juger
   sa propre conformité — il relit son intention, pas son texte. Et un plan approuvé par
   l'utilisateur puis contredit dans la foulée coûte un aller-retour entier. `ExitPlanMode` présente
   donc **le plan et le verdict ensemble**.

   | `VERDICT` | Action |
   |---|---|
   | `CONFORME` | Présenter le plan |
   | `RÉSERVES` | Présenter le plan **avec** les constats — l'utilisateur valide en les connaissant |
   | `NON CONFORME` | Présenter le plan avec le verdict, et laisser l'utilisateur trancher entre corriger le plan et élargir le brief |

   **Ne jamais corriger le plan d'office** sur un verdict, quel qu'il soit. L'écart entre le plan et
   le brief est précisément l'information qu'on paie en lançant l'agent : l'effacer avant que
   l'utilisateur l'ait vue détruit ce qu'on cherchait. Seuls les défauts de rédaction relevés en
   `QUALITÉ` — une citation fausse, une commande de vérification inopérante — se corrigent sans
   arbitrage, et se disent quand même.

   Le plan est persisté dans `.claude/plans/` (voir `plansDirectory`), sous un nom
   **généré par le harness**, sans rapport avec le slug. Son chemin est donné à l'entrée en plan
   mode et confirmé dans la sortie d'`ExitPlanMode` : le prendre là, jamais par `ls -t` — dès qu'un
   second plan existe, la date de modification désigne le mauvais fichier.

   **Le plan doit être versionné.** C'est lui qui porte le contenu des étapes — le suivi n'en a que
   les intitulés, et la session qui exécute une étape y lit sa description. Vérifier qu'il n'est pas
   ignoré :

   ```bash
   git check-ignore -q .claude/plans/<fichier>.md && echo "IGNORÉ — le signaler"
   ```

   S'il est ignoré, le dire à l'utilisateur : sans lui, toute reprise après une Passation perd la
   description des étapes. Sinon, il entre dans le commit de l'état initial (point 9).
4. **Créer la branche d'implémentation** nommée exactement `<slug>`, à partir de la branche
   courante — la **branche principale**, qui ira dans le champ `base` du suivi — et obtenir la
   lettre des tags d'étape, qui ira dans le champ `lettre` :

   ```bash
   git checkout -b <slug>
   commit-chantier lettre
   ```

   La lettre nomme les tags d'étape du chantier
   ([Tags d'étape](../../git-smart-commit/references/tags-etape.md)). Pourquoi le nom de branche est
   exact : [Branche de chantier](../../git-smart-commit/references/branche-chantier.md).
5. **Poser le suivi** depuis sa semence, puis lire ce que chaque champ et chaque section attend :

   ```bash
   gabarit new suivi .claude/implementation/<slug>.md
   gabarit contract suivi
   ```

   **Figer le plan** dans le suivi : ses étapes deviennent la section `Étapes`, et son chemin va
   dans le champ `plan`. Format d'une étape et granularité :
   [Format d'étape](contrat.md#format-détape).

   **C'est ici que les étapes trop grosses se découpent**, pas en cours de route — le renvoi
   ci-dessus dit pourquoi.
6. **Reprendre exactement le slug du brief**, jamais le réinventer — règle et conséquence :
   [Arborescence et nommage](contrat.md#arborescence-et-nommage).
7. **Reprendre l'objectif et le périmètre du brief**, ne pas les réinventer : la semence déclare
   les blocs de cette section, et leur contenu vient du brief tel qu'il a été validé.
   Le champ `brief` en vient aussi ; le champ `modèle` vient de la section `## Modèle` du plan.
   Règles des champs : [Frontmatter](contrat.md#frontmatter).

   **Chantier parti d'une entrée de `road-map/`** → renseigner le champ `road-map` avec son `id`,
   relevé par `intent-brief` à la reconnaissance. C'est la seule chose qui fera sortir l'entrée à
   la clôture ; omis, elle y restera indéfiniment
   ([Road-map](road-map.md#le-champ-road-map)).

   **Le champ `skills`** reçoit les noms des Shadow-skills retenus au point 2, `[]` si aucun ne
   sert : un tableau vide dit qu'on a cherché, un champ absent ne dirait rien.

   Le **symptôme** est ce qui permet, trois sessions plus tard, de voir qu'on a construit la
   bonne solution au mauvais problème. Les **signaux de dérive** deviennent un déclencheur
   d'arrêt pendant l'implémentation (Phase 4). C'est ce point de jonction qui attache le chantier à
   l'intention initiale et empêche le scope creep entre deux discussions.

   Le brief n'est plus modifié ensuite — ce qu'on fait d'une intention qui change en cours de
   route : [Autorité et divergence](contrat.md#autorité-et-divergence).
8. **Vérifier le suivi** contre sa semence :

   ```bash
   gabarit check .claude/implementation/<slug>.md --filled
   ```

   **Un échec arrête la création** : pas de commit de l'état initial, pas d'implémentation. Il
   nomme ce qui reste à remplir ; le compléter, puis relancer. Un suivi incomplet se relit à froid
   trois sessions plus tard, et c'est là que le trou coûte.
9. **Committer l'état initial** — brief, plan et suivi — par `git-smart-commit`, type 2, cas « état
   initial » : [Commit rapide de chantier](../../git-smart-commit/references/etape.md). Le tag
   `<L>E0` qu'il pose est le point de départ des plages d'étapes.
10. **Proposer la Passation**, toujours :
    [Passation](execution.md#passation). Le cadrage, l'exploration et la relecture du plan pèsent
    sur chaque tour suivant sans plus servir à l'implémentation, et la session de création est
    celle qui en sait le plus sans l'avoir écrit.

    La Passation acceptée, dire à l'utilisateur de faire `/model <modèle>` dans la session vierge,
    avant `/implementation-tracker @<suivi>` : c'est là que l'implémentation commence, et rien ne
    change le modèle à sa place.
