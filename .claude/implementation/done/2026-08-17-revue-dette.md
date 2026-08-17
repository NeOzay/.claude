---
slug: revue-dette
titre: Skill manuelle de revue du registre de dette
branche: revue-dette
base: master
statut: terminé
session: 2
execution: direct
plan: .claude/implementation/done/2026-08-17-revue-dette.plan.md
brief: .claude/implementation/done/2026-08-17-revue-dette.brief.md
audit: .claude/implementation/done/2026-08-17-revue-dette.audit.md
créé: 2026-08-16
maj: 2026-08-17
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : « Actuellement, il n'y a aucun système pour vérifier si une dette est encore
pertinente. »

**But** : un nouveau skill à déclenchement manuel qui vérifie la pertinence des entrées du
registre — un verdict par entrée, arbitrage de l'utilisateur, puis mise à jour des registres.

**Critères de réussite** :

- chaque entrée du registre reçoit **exactement une** des sept catégories, aucune omise : le compte
  des entrées classées dans le rapport égale `grep -c '^## ' technical-debt.md`

  *Ce critère ne se rejoue plus tel quel après la clôture* (R21) : le registre porte 17 entrées, le
  rapport 14 blocs. L'écart est celui des entrées que **la clôture elle-même** y a versées, après la
  passe. Vérifié strictement additif — `diff` des intitulés entre `69fd11c` et `HEAD` → `14a15,17`,
  aucun des 14 intitulés instruits perdu.
- le script de tri rend les entrées **regroupées par catégorie puis par date**, sans en perdre :
  même compte avant et après
- après arbitrage, `grep -n 'Dernière vérification' technical-debt.md` porte la date du jour
  obtenue par `date +%F`, et aucune entrée arbitrée ne subsiste sans son traitement
- `git status --short` après une passe ne montre que des chemins sous `.claude/implementation/` :
  aucun fichier de code touché

**Élargi le 2026-08-17** (R11 de l'audit de clôture, arbitré par l'utilisateur) : le critère 4
admet une exception — les **fichiers de règle** qu'un arbitrage a explicitement décidé de modifier,
et eux seuls : les trois destinations que l'Étape 3 du skill nomme (`dette.md`, `categories.md`,
`SKILL.md`), pas « tout fichier qu'un arbitrage désigne ».
Le critère écrit au brief faisait de son propre cas nominal une faute : à la première passe réelle,
deux arbitrages sur trois ont produit une règle, donc une écriture dans `skills/`. L'interdit de
fond est inchangé : **aucun fichier de code**, et rien qui n'ait été nommé à l'arbitrage.

**Hors-périmètre** :

- le skill ne corrige aucun code, même trivial : tout correctif passe par `implementation-tracker`
- pas d'invocation automatique : déclenchement manuel uniquement
- le skill n'invente pas de dette : il statue sur les entrées existantes
- `road-map.md`, annoncé par `dette.md:48`, n'est pas créé dans ce chantier

**Signaux de dérive** :

- si le skill se met à écrire dans le code plutôt qu'à instruire un verdict, c'est raté
- si le modèle se met à trier lui-même au lieu d'étiqueter, le script n'a plus de raison d'être
- si une entrée sort du registre sans atterrir ni dans `technical-debt-solde.md` ni dans le fichier
  de trace, la trace est perdue — ce que le dispositif existe pour éviter

## Étapes

- [x] 1. Gabarit du rapport et échantillon — `skills/debt-review/references/gabarit-rapport.md`, `skills/debt-review/references/exemple-revue.md` — vérif: `grep -c '^## ' skills/debt-review/references/exemple-revue.md` → 8 (7 catégories, la pile `pertinent` en portant deux pour couvrir le tri par date)
- [x] 2. Script de tri — `skills/debt-review/scripts/trier-revue.sh` — vérif: `bash skills/debt-review/scripts/trier-revue.sh skills/debt-review/references/exemple-revue.md | grep -c '^# '` → **8** depuis l'étape 9 (7 piles + le titre du préambule, que le
tri conserve désormais ; valait 7 avant), et `| grep -c '^## '` → 8 (conservation)
- [x] 3. Référence des catégories — `skills/debt-review/references/categories.md` — vérif: `grep -cE '^## .+ — \`[a-z-]+\`$' skills/debt-review/references/categories.md` → 7 (ancré sur la forme des sections : un `^## ` nu compterait aussi l'entrée de registre citée en exemple)
- [x] 4. Corps du skill — `skills/debt-review/SKILL.md` — vérif: `bash scripts/check-pipeline.sh`
- [x] 5. Arborescence du contrat — `skills/implementation-tracker/references/contrat.md` — vérif: `bash scripts/check-pipeline.sh`
- [x] 6. Amendements du registre — `skills/implementation-tracker/references/dette.md`, `.claude/implementation/todo/README.md` — vérif: `bash scripts/check-pipeline.sh`
- [x] 7. **Corriger l'exemple travaillé faux** — `skills/debt-review/references/gabarit-rapport.md`, `skills/debt-review/references/exemple-revue.md`, `skills/debt-review/references/categories.md` — vérif: aucun intitulé d'exemple ne figure dans le registre : pour chaque `^## ` de `technical-debt.md`, `grep -F` de son intitulé dans `skills/debt-review/references/` → 0
- [x] 8. **Rendre le tri idempotent** — `skills/debt-review/scripts/trier-revue.sh` — vérif: trois tris enchaînés rendent un document **identique à l'octet** (`diff` muet) — critère plus fort que le comptage des titres, qui valait 7 → 13 → 19 avant correction
- [x] 9. **Combler les trous d'exécution** — `skills/debt-review/SKILL.md`, `skills/debt-review/references/gabarit-rapport.md` — `mkdir -p done/revues`, contrôle du rapport du jour, `## ` réservé aux blocs, comptage en caractères et non en octets, repli quand on ne peut pas demander — vérif: `bash scripts/check-pipeline.sh` et une passe d'écriture réelle du rapport qui n'échoue pas
- [x] 9bis. **Réserves R1, R3, R4 de l'audit `d77f182`** — `skills/debt-review/SKILL.md` — idiome sûr du tri (`> "$R.trie" && mv`), `cd` vers `todo/` retiré, registre absent compté 0 — vérif: le rapport survit au tri **et** à un refus du script (8 blocs conservés, taille inchangée sur `exit 1`) ; contrôle de conservation `rc=0` avec `technical-debt-ecarte.md` absent, TOTAL 20 ; `git status --short` rend des chemins préfixés
- [x] 10. Instruire et trier les 14 entrées — `.claude/implementation/todo/technical-debt.md` (lecture), rapport de revue — vérif: le rapport porte 14 blocs, `bash "$HOME/.claude/skills/debt-review/scripts/trier-revue.sh" <rapport> | grep -c '^## '` → 14
- [x] 11. Écrire les registres après arbitrage et archiver le rapport — `.claude/implementation/todo/*.md`, `.claude/implementation/done/revues/` — vérif: somme des `grep -c '^## '` sur les trois registres → 20, `grep -n 'Dernière vérification' technical-debt.md` porte la sortie de `date +%F`, et `git status --short` ne liste que des chemins sous `.claude/implementation/`
- [x] 12. **Réserves R11 et R13 de l'audit de clôture** — `skills/debt-review/SKILL.md`, `skills/debt-review/scripts/trier-revue.sh` — chemin d'écriture d'une règle issue d'un arbitrage, contrôle de l'Étape 5 amendé, bornes de mois et de quantième dans la validation de date — vérif: `2026-13-45` et `2026-08-00` → `rc=1`, `2026-12-31` → `rc=0` ; `check-pipeline.sh` rc=0 ; tri de l'exemple canonique → 8 piles, 8 blocs ; rapport réel stable à l'octet

## État courant

Chantier **terminé**. Les douze étapes sont cochées ; le détail de chacune est dans le diff du
commit unique et dans le journal ci-dessous.

**Ce qui a été livré** — le skill manuel `debt-review` (corps, sept catégories, gabarit de rapport,
exemple fictif, script de tri à échec fermé), les amendements de `dette.md` qui lui donnent ses
registres (*Écarter*, *Marqueur d'une entrée relue*, *Corriger une entrée*, interdiction des
numéros de ligne), et **une passe réelle** :
`.claude/implementation/done/revues/2026-08-17-revue.md`, 14 blocs pour 14 entrées, arbitrée
puis écrite.

**Ce que la passe réelle a coûté et rapporté** — elle a fait échouer l'étape 7 avant qu'elle ne
commence (8 des 9 exemples du skill étaient de vraies entrées du registre avec des verdicts
fabriqués, dont un qui prescrivait d'écarter une dette vivante), révélé que le tri n'était pas
idempotent, que `done/revues/` n'existait pas, et que l'idiome d'écriture prescrit détruisait le
rapport. **Aucun de ces défauts n'a été trouvé en relisant mon propre travail** : trois viennent
d'une passe en contexte froid, cinq de l'audit intermédiaire, quatre d'une contre-expertise ciblée.

**Verdict de clôture** — `RÉSERVES` sur `69fd11c`, aucun bloquant, quatre critères atteints. R11
(l'arbitrage qui produit une règle n'avait aucun chemin) et R13 (validation de date par la forme
seule) ont été corrigés à l'étape 12. R5 à R8 et R12 sont versées au registre de dette, R14 en
élargit une existante. **R10 n'y est pas** : elle a été traitée par correction de la note fausse,
plus bas dans ce fichier.

**Troisième audit** — `RÉSERVES` sur `be0eadf`, aucun bloquant, demandé avant l'aplatissement parce
que l'étape 12 n'avait été jugée par personne. Il a rendu **fausse** l'entrée de registre qui le
disait : elle est soldée le jour même, avec ce rapport pour preuve. Trois de ses constats sont
traités ici (R16, R17, R20), un part au registre (R19).

**Critère 4 du brief, observation directe** — la passe de revue, vérifiée avant toute correction de
chantier, ne produisait que `?? .claude/implementation/done/revues/`. Les fichiers de `skills/` au
`git status` sont les corrections du chantier et les règles décidées à l'arbitrage, pas l'œuvre de
la passe. Cette observation est désormais **recopiée dans le rapport archivé** (R16) : elle avait
été perdue en compactant cette section, à l'endroit même où le registre venait d'inscrire qu'un
critère doit nommer la pièce persistante qui l'établit.

**Non éprouvé, et il faut le savoir** : quatre catégories sur sept n'ont jamais écrit une ligne —
`technical-debt-ecarte.md` n'existe pas. Le premier écartement réel sera aussi le premier test de
ce chemin.

**Notes** :

- Le contrôle 6 du garde-fou impose que tout appel de script depuis un `.md` de `skills/` soit en
  chemin absolu `$HOME/…` — y compris dans un fichier d'exemple, ce qui a failli passer inaperçu.
- Le contrôle 1 impose que chaque section de `contrat.md` reste citée depuis `skills/` : ne pas
  ajouter de section au contrat sans écrire le renvoi qui y mène.
- **Mesurer l'enroulement en caractères, pas en octets.** `awk length` compte les octets et
  signale une centaine de faux positifs sur du texte accentué. Utiliser `python3` ou `wc -L`.
- **Note corrigée le 2026-08-17** (R10) — elle affirmait qu'après l'étape 6 « la seule ligne > 100
  caractères du corpus » était celle de `dette.md`, ce que la note suivante contredisait déjà. Le
  chiffre réel, établi à l'étape 10 et reproduit par l'auditeur : **133 lignes** sur `master` comme
  sur `HEAD`, dont 14 dans `skills/implementation-tracker/references/`. C'est ce chiffre qui figure
  au registre ; la note d'origine est supprimée plutôt que conservée, une trace fausse survivant
  au chantier valant moins que rien.

## Journal de décisions

- **2026-08-16** — Le modèle étiquette, un script regroupe par catégorie puis par date.
  *Pourquoi* : le regroupement est mécanique et le modèle le fait mal. *Rejeté* : un rapport écrit
  déjà trié par le modèle.
- **2026-08-16** — Rapport archivé en `done/revues/<AAAA-MM-DD>-revue.md`, sous-répertoire.
  *Pourquoi* : `impl-list.sh` est en `-maxdepth 1`, donc les contrôles 3 et 5 du garde-fou restent
  inchangés. *Rejeté* : `done/` à plat avec une exclusion de plus dans `impl-list.sh`.
- **2026-08-16** — Un seul `todo/technical-debt-ecarte.md` pour `non pertinent`, `doublon` et
  `pas une dette`, chaque entrée portant son motif. *Pourquoi* : un registre à relire plutôt que
  trois. *Rejeté* : créer le `road-map.md` annoncé par `dette.md:48`.
- **2026-08-16** — Le rapport de revue s'écrit **directement** dans `done/revues/<date>-revue.md`,
  sans fichier de travail intermédiaire. *Pourquoi* : un archivage en fin de procédure est une étape
  qui s'oublie, et le rapport porte l'arbitrage — il n'a pas d'état « avant archivage » utile.
  *Rejeté* : un `.revue-en-cours.md` dans `todo/`, déplacé après arbitrage.
- **2026-08-16** — `exemple-revue.md` porte **8 blocs pour 7 catégories** : la pile `pertinent` en
  a deux, de dates différentes. *Pourquoi* : avec un bloc par pile, le tri par date à l'intérieur
  d'une pile n'était couvert par aucun test permanent — une régression d'ordonnancement serait
  passée au vert. *Rejeté* : un jeu de test séparé, qui aurait vieilli sans que rien ne le relance.
- **2026-08-16** — Identifiants de catégorie en **ASCII kebab-case** dans l'en-tête du rapport
  (`a-solder`, `aggravee`, `inverifiable`…), libellés accentués réservés à la sortie du script.
  *Pourquoi* : ce sont les seules chaînes que le script compare. *Rejeté* : les libellés accentués
  comme identifiants.
- **2026-08-17** — L'auditeur a exécuté `git checkout -- README.md` pour établir `R3`, hors de son
  mandat en lecture seule. *Constat* : arbre et `HEAD` vérifiés intacts après coup, aucune trace.
  *Pourquoi le noter* : un auditeur qui écrit peut masquer l'état qu'il juge — à verser au registre
  à la clôture, pas ici.
- **2026-08-17** — Le tri **conserve le préambule** du rapport, au lieu de le jeter. *Pourquoi* : la
  procédure y fait consigner la date et le compte des entrées, et le tri s'écrit par-dessus le
  rapport — ce qui n'y survivait pas n'avait aucun endroit où exister. *Rejeté* : réécrire le
  préambule après chaque tri, qui documente le piège au lieu de le supprimer.
- **2026-08-17** — La clause « arbre propre » de l'Étape 0 ne porte que sur ce qui est **hors** de
  `.claude/implementation/`. *Pourquoi* : son seul motif est de garder lisible le `git status` de
  l'Étape 5, qui accepte ces chemins — l'exiger vide rejetait des arbres sains. *Rejeté* : l'arbre
  entièrement propre, comme le tracker l'exige pour une création de chantier.
- **2026-08-17** — `trier-revue.sh` **tolère** un rapport déjà trié : il retire les intitulés de
  pile qu'il reconnaît, au lieu de refuser l'entrée. *Pourquoi* : `SKILL.md:68` et `:107` invitent
  explicitement au re-tri, refuser ferait échouer la procédure sur son propre chemin nominal.
  *Rejeté* : l'échec fermé sur entrée déjà triée.
- **2026-08-17** — Le contrôle de conservation compte aussi les **intitulés de pile**, pas seulement
  les blocs. *Pourquoi* : la duplication laissait les 8 blocs intacts, donc le contrôle restait au
  vert pendant que le document se corrompait. *Rejeté* : ne compter que les blocs, comme avant.
- **2026-08-17** — Tous les exemples de `skills/debt-review/` portent sur un **dépôt fictif**, aucun
  intitulé réel. *Pourquoi* : 8 des 9 exemples reprenaient une vraie entrée du registre avec un
  verdict fabriqué — dont un `non-pertinent` sur une dette vivante, qui poussait à l'écarter.
  *Rejeté* : garder les entrées réelles en corrigeant leurs preuves, qui périment au premier commit.
- **2026-08-17** — Dans `exemple-revue.md`, les deux blocs `pertinent` sont écrits **du plus récent
  au plus ancien**. *Pourquoi* : dans l'ordre croissant, le tri intra-pile passait au vert sans rien
  trier — le test était vide. Ne pas les ranger. *Rejeté* : un troisième bloc `pertinent`.
- **2026-08-17** — `debt-review` est **structurellement non testable par un sous-agent** :
  `disable-model-invocation: true` retire le skill de la liste *et* verrouille le tool `Skill`, dont
  le message d'erreur interdit de reproduire le workflow autrement. *Pourquoi ça compte* : toute
  passe de test future ne peut être que dégradée (lecture du `SKILL.md` comme document).
  *Conséquence assumée* : le skill se teste en session, à la main.
- **2026-08-17** — L'étape 7 est doublée d'une **passe de test par agent froid**, dont le rapport
  (scratchpad, hors dépôt) n'est **pas** autoritaire : la passe directe fait foi. *Pourquoi* :
  l'auteur du `SKILL.md` ne peut pas juger s'il est autosuffisant, il le relit avec son intention en
  tête. *Rejeté* : `execution: délégué` — l'agent est un sujet de test, pas l'exécutant de l'étape.
- **2026-08-17** — La création de `technical-debt-ecarte.md` et la forme de son champ `Écartée le`
  sont définies dans `dette.md` (section *Écarter*), `SKILL.md` s'y renvoyant. *Pourquoi* :
  `dette.md` est l'autorité sur la tenue des registres, et la phrase y était recopiée à l'identique.
  *Rejeté* : la garder dans `SKILL.md`, au plus près du geste.
- **2026-08-17** — **Élargissement du critère 4 du brief** : une passe de revue peut écrire hors de
  `.claude/implementation/`, dans les seuls fichiers de règle nommés à l'arbitrage. *Pourquoi* : le
  critère d'origine faisait de son cas nominal une violation (2 arbitrages sur 3). *Rejeté* : écrire
  les corrections sans la règle qui les autorise.
- **2026-08-17** — Le chemin d'écriture d'une règle est **choisi par ce qu'elle régit** : tenue des
  registres → `dette.md`, classement → `categories.md`, geste de la revue → `SKILL.md`. *Pourquoi* :
  sans destination écrite, la règle atterrit là où l'on tient la plume. *Rejeté* : tout dans le
  skill.
- **2026-08-17** — **Les numéros de ligne sont proscrits du registre de dette** ; une entrée cite un
  fichier, une section, une phrase. *Pourquoi* : un repère périmé ne fait échouer aucune commande et
  fait classer `non-pertinent` une dette vivante. *Rejeté* : un marqueur signalant le repère périmé.
- **2026-08-17** — Une entrée **vraie mais mal écrite** se corrige sur place (`dette.md`, « Corriger
  une entrée »), sans changer de catégorie, de date ni d'intitulé, et avec preuve exécutée.
  *Pourquoi* : 3 entrées sur 14 à la première revue réelle — plus fréquent que les sorties de
  registre. *Rejeté* : une 8ᵉ catégorie, qui aurait fait juger la rédaction et non le fait.
- **2026-08-17** — L'intitulé d'une entrée **reste faux** quand il porte le chiffre erroné, et c'est
  le Constat qui énonce l'écart. *Pourquoi* : l'intitulé est la clé de dédoublonnage d'*Alimenter* ;
  le réécrire ferait revenir l'entrée comme neuve. *Rejeté* : corriger le titre.
- **2026-08-16** — **Amendement au périmètre du brief** : le marqueur des catégories `aggravée` et
  `invérifiable en revue` passe **sous le titre**, forme `(catégorie) date`, au lieu du suffixe
  `(aggravée)` dans l'intitulé écrit au brief. *Pourquoi* : l'intitulé est la clé de référence
  d'une entrée (`dette.md:76-78`) et sert au dédoublonnage de clôture (`dette.md:119`) ; le
  laisser intact évite d'avoir à neutraliser une liste de suffixes qui s'allongerait. *Rejeté* :
  amender le dédoublonnage pour ignorer les suffixes.
