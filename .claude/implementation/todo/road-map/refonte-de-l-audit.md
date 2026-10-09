+++
id = "refonte-de-l-audit"
title = "Refondre l'audit d'implémentation : sortir des audits à répétition, borner le rapport"
date = 2026-10-09
source = "analyse des dumps de session du 2026-10-09 ; absorbe l'entrée `rapport-audit-en-liste` du 2026-09-19"
+++

## À faire

Refondre le système d'audit pour qu'un Chantier n'enchaîne plus les audits complets (« audit
hell »), et que `<slug>.audit.md` cesse de gonfler à chaque audit. L'ensemble est à discuter au
Brief : verdict, relance, forme du rapport, restitution.

Constats tirés des dumps et des rapports archivés :

- **Le coût** : 44 lancements d'`implementation-auditor` entre le 2026-09-09 et le 2026-10-09,
  soit environ 153 M de tokens, 17 % des 917 M consommés par les 76 sessions. Un Chantier en
  reçoit 2,3 en moyenne, et 4 pour `pipeline-gabarit`, `contexte-tracker` et
  `git-smart-commit-trois-commits`.
- **Un verdict qui ne conclut presque jamais** : les rapports archivés portent 74 `RÉSERVES`,
  12 `DÉFAVORABLE` et 1 `FAVORABLE`. `RÉSERVES` couvre tout constat, même un cas limite sans
  déclencheur, et l'auditeur doit prendre « le plus sévère » dans le doute. Chaque audit finit
  donc par un arbitrage de l'utilisateur.
- **La boucle** : `audit.md` impose un audit complet après tout traitement de réserve, parce que
  le correctif a produit un diff jamais jugé. L'audit suivant trouve de nouvelles réserves sur
  l'ensemble du diff (`dump-sessions` : R7, nouvelle au second audit). Pour sortir, l'utilisateur
  clôt à la main « sans nouvel audit », 6 fois dans les dumps, et une dette en est née :
  `correctif-passation-e11-non-audite`.
- **Le rapport gonfle** : chaque audit s'appende à `<slug>.audit.md`, que l'auditeur relit puis
  réécrit en entier. Les rapports archivés font de 108 à 1 481 lignes ; celui de
  `mods-a-la-racine-des-skills` en fait 686 pour trois audits.
- **Un périmètre qu'on ne peut pas régler** : l'utilisateur doit le corriger dans sa demande
  (« Indique à l'auditeur de ne pas lire le contenu des dettes », « Indique aussi à l'auditeur de
  lire skill-convention »).

Pistes à confronter au Brief :

- un verdict gradué par la sévérité, sur l'échelle du registre de dette (note, avertissement,
  majeur, critique) : seules les réserves majeures ou critiques bloquent ; les autres partent au
  registre à la Clôture, sans arbitrage une par une ;
- après traitement, un contre-audit borné au diff depuis le SHA audité et aux réserves traitées, à
  la place d'un audit complet ;
- un nombre d'audits par Chantier borné, ou un seuil au-delà duquel la Clôture se décide sans
  nouvel audit ;
- le rapport porté par une List-dir, un Élément par audit, dont le front matter est prérempli
  depuis les audits précédents (idée de l'entrée `rapport-audit-en-liste`), ou un fichier par
  audit : ni l'auditeur ni l'orchestrateur ne relisent alors l'historique entier ;
- l'utilité de l'audit intermédiaire, proposé au-delà de 400 lignes de diff ;
- la restitution du verdict : une ligne et un tableau, objet de l'entrée `messages-du-pipeline`.

## Références

- `skills/implementation-tracker/references/audit.md` : « Quand auditer », « Au retour » (audit
  complet après traitement), « Gabarit du rapport »
- `agents/implementation-auditor.md` : « Écrire le rapport » (lecture et réécriture du fichier
  entier), « Verdict » (règle du plus sévère)
- `skills/implementation-tracker/references/cloture.md`, point 1 ; `dette.md` pour l'échelle de
  sévérité
- rapports archivés : `.claude/implementation/done/*.audit.md` ; rapport hors Chantier en cours :
  `.claude/implementation/lexique-local-tronque.audit.md`
- transcriptions des audits : `projects/-home-debian--claude/<session>/subagents/`, champ
  `agentType` des `*.meta.json`
- dette liée : `correctif-passation-e11-non-audite`
- entrée absorbée : `rapport-audit-en-liste` (sortie vers `road-map-ecarte/`)
- `skills/list-dir/SKILL.md` et `skills/gabarit/SKILL.md` : préremplissage `command` d'un Élément
