---
slug: modele-hors-de-settings-json
---

## 2026-10-09 — clôture — `1a2282b`

**Verdict** : RÉSERVES

Brief présent et lu ; suivi, plan (`.claude/plans/compiled-gathering-quokka.md`) et diff
`master...modele-hors-de-settings-json` lus. Le suivi ne s'écarte pas du brief ; il ajoute trois
signaux de dérive venus du plan, jugés ci-dessous.

### Vérifications exécutées

- Étape 1 : `grep -c 'pour la session seulement' skills/implementation-tracker/references/contrat.md skills/implementation-tracker/references/creation.md`
  → `contrat.md:2`, `creation.md:1` (attendu ≥ 1 chacun) : passe.
- Étape 1 : `git diff --stat master -- settings.json` → vide : passe.
- Étape 2 : `grep -n 'settings.local.json' .claude/CLAUDE.md` → lignes 28 et 29 : passe.
- Étape 2 : `git check-ignore -q .claude/settings.local.json && echo IGNORÉ` → `IGNORÉ`
  (`git check-ignore -v` : `~/.config/git/ignore:1:**/.claude/settings.local.json`) : passe.
- Étape 2 : `git diff --stat master -- settings.json settings.local.json` → vide : passe.
- Critères 1 et 3 : `git status --short` (sans filtre rtk, `rtk proxy git status --porcelain`)
  → 0 ligne. Voir R1 : ce résultat ne prouve pas le critère.
- Signaux de dérive : `git diff --name-only master...modele-hors-de-settings-json` → six fichiers
  (`.claude/CLAUDE.md`, brief, suivi, plan, `contrat.md`, `creation.md`) ; aucun `.gitattributes`
  (`ls .gitattributes` : absent) ; `git config --get-regexp '^filter\.'` → aucune entrée (rc 1).
- `scripts/check_pipeline.py` (renvois et ancres, dont le nouveau lien
  `contrat.md#modèle-dimplémentation` de `creation.md`) → « Pipeline conforme. », rc 0.
- `gabarit check .claude/implementation/modele-hors-de-settings-json.md --filled` → conforme, rc 0.
- `uvx rumdl check` sur les trois fichiers modifiés → 1 constat, MD028 dans un bloc cité de
  `contrat.md` (ligne 236). Le même constat sort sur l'arbre de `master` extrait par `git archive`
  (ligne 230) : il existait avant, le Chantier ne l'introduit pas.
- Critère 1 en usage réel (un `/model` pour la session seulement, puis `git status`) → NON
  EXÉCUTÉE : il faut une session interactive de Claude Code et la commande `/model`, ce qu'un
  sous-agent ne peut pas lancer.

### Conformité à l'intention

- Critère « après un changement de modèle […] suivi de la consigne, `git status --short` ne montre
  pas `settings.json` » : invérifiable en l'état (R1).
- Critère « la consigne de choix du modèle (`creation.md` point 10, `contrat.md` « Modèle
  d'implémentation ») ne conduit plus à écrire un fichier versionné » : atteint, vérifié par
  lecture. Les deux passages prescrivent `/model` « pour la session seulement », « sans
  l'enregistrer comme défaut » et « jamais en défaut ». `creation.md` renvoie à `contrat.md` pour le
  motif au lieu de le recopier, comme le plan le demandait. La phrase « ni par Étape, ni par
  session » a été reformulée en « ni d'une Étape à l'autre, ni d'une reprise à l'autre », ce qui
  supprime la contradiction apparente que le plan avait relevée. L'affirmation nouvelle de
  `contrat.md`, « à chaque reprise, implementation-tracker compare le modèle de la session au champ
  `modèle` et signale l'écart », correspond bien à `SKILL.md:130-132`.
- Critère « une création de Chantier et une reprise après Passation passent leur contrôle d'arbre
  propre sans exception pour `settings.json` » : aucune exception pour `settings.json` n'existe dans
  le pipeline (`grep -rn 'settings\.json' skills/` ne renvoie, hors `lexique` et hors sujet, que la
  phrase nouvelle de `contrat.md`). Le passage effectif reste invérifiable (R1).
- Hors-périmètre : respecté. Aucun filtre git, aucun hook, `~/.claude/settings.local.json` absent
  du diff.
- Signaux de dérive :
  - `.gitattributes`, `filter.*` ou hook touchant `settings.json` : aucun.
  - `~/.claude/settings.local.json` modifié : non.
  - le diff touche `settings.json` : non.
  - le diff touche un fichier hors des Étapes : non. Les trois fichiers en plus des Étapes (brief,
    suivi, plan) forment l'état initial `E0`.
  - la consigne fait écrire le modèle par l'agent : non dans la consigne du pipeline. Une réserve
    porte sur la lecture possible de `.claude/CLAUDE.md` (R2).
- Symptôme d'origine : il disparaît si l'utilisateur suit la consigne. Rien ne l'a encore montré
  en usage (R1).

- **R1** — Les critères 1 et 3 n'ont pas été éprouvés, et la Clôture est lancée avant la
  vérification que le Suivi lui-même pose comme préalable. Le plan prévoyait un contrôle de bout en
  bout : Passation, `/model opus` pour la session seulement, reprise sur un arbre propre. Or la
  branche ne porte aucun commit de Passation (`E0`, `E1`, `E2` seulement), et le Suivi est à
  `session = 1`. La « Prochaine action » du Suivi dit : « Vérifier à la prochaine reprise, après un
  `/model` pour la session seulement, que `git status --short` est vide ; puis la Clôture. » L'arbre
  propre constaté aujourd'hui ne prouve rien, parce que `settings.json` porte `"model": "opus"`
  aussi bien sur `master` que sur `HEAD`. Un `/model opus` enregistré comme défaut réécrirait donc
  la même valeur sans laisser de diff. Le critère ne se verra en défaut qu'avec un modèle différent
  de celui que `settings.json` enregistre. L'utilisateur doit choisir entre clore maintenant, en
  reportant l'épreuve au prochain Chantier de la configuration (ce que le plan admet pour la
  consigne réécrite), et faire d'abord la reprise prévue au Suivi.

### Qualité du code

Le diff ne contient que de la prose. Elle suit le style des fichiers voisins : registre, densité,
motif écrit dans le corps du texte, renvoi ancré plutôt que recopie dans `creation.md`. Les lignes
modifiées ne dépassent pas 100 caractères. Les lignes trop longues de `.claude/CLAUDE.md` (43-44)
et de `creation.md` (54-55) existaient avant le Chantier.

- **R2** — `.claude/CLAUDE.md:27-29` : « Le modèle de démarrage se règle dans
  `.claude/settings.local.json` » ne dit pas qui le règle. Un agent à qui l'utilisateur demande
  « passe en Sonnet » peut y lire une invitation à écrire ce fichier. C'est précisément le signal de
  dérive que le plan ajoute (« la consigne fait écrire le modèle par l'agent »). `contrat.md` pose
  ailleurs que seul l'utilisateur change de modèle, mais `.claude/CLAUDE.md` est chargé seul, sans
  ce contexte. Autre point lié, que je ne peux pas trancher : le brief décrit
  `.claude/settings.local.json` comme portant `"model": "sonnet"`, et il porte aujourd'hui
  `"model": "opus"`. Le fichier est ignoré par git, donc absent du diff. Rien ne permet de dire si
  c'est l'utilisateur ou un agent qui l'a changé pendant le Chantier. Si c'est un agent, le signal
  de dérive s'est matérialisé hors du diff.

### Dette induite

- **R3** — Le motif (« `settings.json` est versionné, un `/model` en défaut salit l'arbre, et un
  Chantier ne se crée ni ne se reprend sur un arbre sale ») est écrit deux fois : dans
  `contrat.md`, « Modèle d'implémentation », et dans `.claude/CLAUDE.md`, « Le modèle d'une
  session ». Le plan voulait cette double écriture, et la règle « une règle, un seul endroit » ne
  vise que les fichiers de skill. Le coût : si le pipeline cesse un jour de bloquer sur arbre sale,
  ou si l'option C du brief entre, il faudra corriger deux endroits, et aucune vérification
  (`check_pipeline.py` ne lit pas `.claude/CLAUDE.md`) ne signalera celui qu'on a oublié. Un renvoi
  vers `contrat.md#modèle-dimplémentation` depuis `.claude/CLAUDE.md` l'éviterait. C'est un constat
  léger.

### Pourquoi RÉSERVES et pas DÉFAVORABLE

Aucun critère n'est en échec, aucune commande de vérification n'échoue, et ni le hors-périmètre ni
un signal de dérive ne sont entamés dans le diff. Les critères 1 et 3 sont invérifiables, pas
démentis, et la grille range un critère invérifiable en RÉSERVES. Mais R1 n'est pas une simple
formalité : le Suivi avait lui-même prévu l'épreuve avant la Clôture.

### Bloquants

Aucun.
