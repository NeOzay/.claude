---
slug: resolution-chemin-skill
titre: Les skills se résolvent entre eux au lieu de se citer en dur
branche: resolution-chemin-skill
base: master
statut: terminé
session: 1
execution: direct
plan: .claude/implementation/done/2026-08-29-resolution-chemin-skill.plan.md
brief: .claude/implementation/done/2026-08-29-resolution-chemin-skill.brief.md
audit: .claude/implementation/done/2026-08-29-resolution-chemin-skill.audit.md
créé: 2026-08-29
maj: 2026-08-29
---

## Objectif et périmètre

Repris du brief (`brief:`), pas réinventé.

**Symptôme** : « je vois mes skills comme un système interdépendant » — or chaque skill localise
les autres par une constante `$HOME/.claude/skills/…` recopiée à chaque point d'usage, et recopie
en plus le mode d'emploi du skill qu'il appelle.

**But** : qu'un skill trouve un autre skill par résolution, non par constante — et qu'il fasse
référence aux éléments pertinents de l'autre skill au lieu d'expliquer comment l'utiliser. Les
dépendances entre skills se déclarent et se vérifient, elles ne se supposent pas.

**Critères de réussite** :
- un skill consommateur ne contient que les commandes nécessaires ; les détails restent dans le
  skill qui propose la commande ;
- la ligne de partage est le domaine, pas la commande : reste chez le consommateur la doctrine du
  domaine et l'emploi concret des commandes pour ce domaine ; part chez le fournisseur le
  comportement générique (`dette.md:170` sur `--filled`, `dette.md:181` sur `migrate`) ;
- la résolution du chemin de skill ne laisse plus de constante recopiée : le compte de points
  d'édition cesse de croître avec chaque skill neuve.

**Hors-périmètre** :
- vider les skills consommateurs de leur doctrine — `dette.md` maigrit, il ne se dissout pas ;
- remplacer par des renvois nus les commandes concrètes appliquées au domaine.

**Signaux de dérive** :
- la duplication d'information ne baisse pas : la même explication se lit encore à deux endroits ;
- toutes les étapes sont réexpliquées au lieu de l'essentiel ;
- le mécanisme devient une machinerie : écrire un skill neuf exige d'abord de le comprendre.

## Étapes

- [x] 1. Poser `CLAUDE_SKILLS` et vérifier son expansion — `settings.json` — vérif: `python3 -c "import json;print(json.load(open('settings.json'))['env']['CLAUDE_SKILLS'])"` puis, après redémarrage, `test -d "${CLAUDE_SKILLS:?}"`
- [x] 2. Contrôles 6 et 7 acceptent la nouvelle forme — `scripts/check_pipeline.py`, `scripts/tests/` — vérif: `uvx pytest scripts/tests -q` + `python3 scripts/check_pipeline.py`
- [x] 3. Nouveau contrôle : les renvois documentaires inter-skills résolvent — `scripts/check_pipeline.py`, `scripts/tests/` — vérif: un lien faux fait crier le contrôle ; `uvx pytest scripts/tests -q`
- [x] 4. `list-dir` : révoquer le lien, ancrer les appels, aligner `help.py` — `skills/list-dir/SKILL.md`, `skills/list-dir/scripts/listdir/commands/help.py` — vérif: `uvx pytest skills/list-dir/scripts/tests -q` ; `test ! -e ~/.local/bin/list-dir`
- [x] 5. `bin/` versionné, liens relatifs — `bin/` — vérif: `readlink bin/list-dir` relatif ; `test -x bin/list-dir` ; **point d'arrêt** : ligne PATH dans le profil
- [x] 6. Script de santé du système de skills + hook `SessionStart` — `scripts/sante_skills.py`, `settings.json` — vérif: le script crie sur un lien cassé et sur `bin/` absent du PATH
- [x] 7. Contrôles 6, 7 et 8 adaptés à la commande nue — `scripts/check_pipeline.py`, `scripts/tests/` — vérif: `uvx pytest scripts/tests -q` ; une commande citée sans lien dans `bin/` fait crier
- [x] 8. `list-dir/SKILL.md` repasse aux appels nus, `CLAUDE_SKILLS` retirée de `settings.json` — `skills/list-dir/SKILL.md`, `settings.json` — vérif: `python3 scripts/check_pipeline.py` conforme ; `! grep -q CLAUDE_SKILLS settings.json`
- [x] 9. Dégraisser `dette.md` — `skills/implementation-tracker/references/dette.md` — vérif: `python3 scripts/check_pipeline.py` conforme
- [x] 10. Dégraisser `cloture.md` — `skills/implementation-tracker/references/cloture.md` — vérif: `! grep -q '\$HOME/\.claude' skills/implementation-tracker/references/cloture.md`
- [x] 11. Dégraisser `debt-review` — `skills/debt-review/SKILL.md`, `references/gabarit-rapport.md` — vérif: `! git grep -q '\$HOME/\.claude' -- skills/debt-review`
- [x] 12. Convertir les points d'édition restants — `contrat.md`, `implementation-tracker/SKILL.md`, `todo/README.md` — vérif: `! git grep -q '\$HOME/\.claude/skills' -- skills .claude/implementation/todo/README.md`
- [x] 13. Durcir le contrôle 6 et solder la dette — `scripts/check_pipeline.py`, `technical-debt/chemin-skill-code-en-dur.md` — vérif: `python3 scripts/check_pipeline.py` conforme ; `validate` vert sur les trois registres

## État courant

**Prochaine action** : aplatissement sur `master`, puis archivage en `done/`.

Les 13 étapes sont faites. Deux audits : `6a02642` RÉSERVES (R1-R8), `8f5cd52` RÉSERVES
(R9-R11). R3 à R11 sont traitées ; R1 et R2 sont portées au registre de dette sous
`hook-sante-chemin-home` et `garde-fou-borne-a-skills`.

**Pipeline conforme**, 92 tests du garde-fou, 241 de `list-dir`, `sante_skills` à 0, les trois
registres `--filled` conformes (21 / 14 / 0).

**Vérification** : `python3 scripts/check_pipeline.py` conforme, et
`! git grep -q '\$HOME/\.claude/skills' -- skills .claude/implementation/todo/README.md`

**Dernier audit** : `8f5cd52` — RÉSERVES (3, aucun bloquant) — 2026-08-29

**Notes** : l'aplatissement ne casse pas la traçabilité du solde de dette — vérifié sur une
branche jetable avant décision : après `git merge --squash`, `git log --follow` sur
`technical-debt-solde/chemin-skill-code-en-dur.md` remonte toujours à `53eff2d`. La séparation
déplacement / preuve en deux commits reste néanmoins la règle sur la branche, c'est elle qui rend
la similarité lisible.

Le commit `31bf551` (retrait de `python3`, lien `~/.local/bin/list-dir`) précède ce
chantier sur `master`. Le retrait de `python3` est conservé ; le lien est révoqué à l'étape 4.

## Journal de décisions

- **2026-08-29** — Le contrôle d'ancre du contrôle 8 lit **tous** les niveaux de titre
  (`ancres_markdown`), et non la vue `sections()` du contrôle 1, qui ne retient que les `## `.
  *Pourquoi* : un lien vers un `###` légitime était déclaré mort. *Rejeté* : élargir `sections()`,
  qui aurait changé le jugement du contrôle 1 sur les sections jamais citées.
- **2026-08-29** — Le diagnostic de santé part sur **deux flux** : une ligne unique et complète
  sur `stderr`, le détail sur `stdout`. *Pourquoi* : l'hôte n'affiche que la PREMIÈRE ligne du
  `stderr` d'un hook en échec — constaté en session — donc un en-tête qui compte sans nommer perd
  tout ; et `stdout` revient au modèle, premier concerné puisque c'est lui qui lance les commandes.
  *Rejeté* : `stderr` seul, qui ne protégeait ni l'un ni l'autre correctement.
- **2026-08-29** — Il n'existe qu'une forme correcte pour un exécutable de skill invoqué depuis
  un `.md` : la commande de `bin/`. *Pourquoi* : les contrôles 6 et 7 le démontrent ensemble — le
  premier refuse le chemin relatif, le second l'ancrage sur le `HOME`, et il ne reste rien
  d'autre. Découvert en butant sur la contradiction dans le dépôt-jouet du bout-en-bout, puis
  écrit dans `contrat.md#dépendances`.
- **2026-08-29** — L'amorçage de la bibliothèque Python se résout par
  `Path(shutil.which("list-dir")).resolve().parent`. *Pourquoi* : le lien de `bin/` pointe vers
  `scripts/list-dir.py`, donc le résoudre donne le répertoire à insérer — le dernier cas que
  `bin/` ne couvrait pas, un import n'étant ni un appel ni un renvoi. *Rejeté* : laisser
  `os.path.expanduser("~/.claude/…")`, seule constante survivante.
- **2026-08-29 (révision)** — Le contrôle 7 juge la FORME d'appel, pas seulement l'existence :
  citer le chemin d'un script qui a son lien dans `bin/` est rouge, et le constat nomme la
  commande à employer. *Pourquoi* : c'est ce qui empêche le compte de points d'édition de
  repartir à la hausse — la voie de solde que la fiche `chemin-skill-code-en-dur` réclame.
  *Rejeté* : deviner qu'un mot d'un bloc `bash` est une commande de skill — trop fragile ;
  la santé du `PATH` est vérifiée une fois par session, pas par inférence.
- **2026-08-29 (révision)** — `bin/` versionné à la racine du dépôt, portant un lien **relatif**
  par exécutable de skill, et ajouté au `PATH` par le profil. *Pourquoi* : `CLAUDE_SKILLS` devait
  valoir un chemin absolu dans `settings.json`, qui est versionné — une valeur machine-spécifique
  dans un fichier partagé. Un lien relatif se versionne tel quel : plus aucun chemin absolu dans
  le dépôt. *Rejeté* : `CLAUDE_SKILLS` définie depuis le profil (résout le grief, mais ne donne
  pas de point de rendez-vous extensible aux skills suivants).
- **2026-08-29 (révision)** — La santé du système est vérifiée par un script lancé au démarrage
  de session, non par une garde `command -v` répétée dans chaque bloc. *Pourquoi* : une
  vérification unique et bruyante au bon moment, au lieu d'un rituel recopié — c'est le signal de
  dérive « toutes les étapes réexpliquées » appliqué au garde-fou lui-même. *Conséquence* : les
  étapes 1, 2 et 4 sont partiellement défaites ; ce qu'elles ont établi sur l'appel direct sans
  interpréteur et sur le contrôle 8 reste acquis.
- **2026-08-29** — Racine résolue par `CLAUDE_SKILLS` plutôt que par un lien dans le `PATH`.
  *Pourquoi* : une seule définition pour tout le système, aucun artefact hors dépôt, et le
  contrôle 6 du garde-fou reste applicable. *Rejeté* : `~/.local/bin/list-dir` (non versionné,
  et le contrôle 6 est aveugle à un appel nu).
- **2026-08-29** — Garde `${CLAUDE_SKILLS:?}` au premier emploi de chaque bloc, sans variable
  locale ni repli `:-`. *Pourquoi* : échec fermé, et zéro définition recopiée — sinon on
  remplace 10 points d'édition par 10 définitions. *Rejeté* : `${CLAUDE_SKILLS:-$HOME/…}`, qui
  rejoue le mode de défaillance R2 hors `~/.claude`.
- **2026-08-29** — Renvois documentaires inter-skills : chemin relatif, et un contrôle qui
  vérifie qu'ils résolvent. *Pourquoi* : les 8 renvois existants le sont déjà, et les liens
  restent cliquables. *Rejeté* : une notation symbolique `<skills>/…`, non cliquable.
- **2026-08-29** — Le champ `env` de `settings.json` **n'étend pas** `$HOME` : la valeur arrive
  littérale dans l'environnement. *Pourquoi ça compte* : la valeur doit être un chemin absolu
  réel, machine-spécifique, et c'est légitime — la variable est le point de portabilité. À noter
  que `$HOME` fonctionne, lui, dans `hooks` et `statusLine` : l'expansion dépend du champ.
- **2026-08-29** — Le contrôle 6 reconnaît désormais l'**appel direct**, sans interpréteur.
  *Pourquoi* : la forme convertie (`"$CLAUDE_SKILLS/…/y.py" cmd`) n'a plus de `python3` devant ;
  un contrôle resté sur `bash|python3` serait devenu vert en n'examinant plus rien. *Portée* :
  ce motif ne s'applique qu'en tête de commande dans un bloc ```bash, sinon un chemin cité en
  prose deviendrait un appel.
- **2026-08-29** — Écart assumé sur « aucune variable locale » : le bloc des dix commandes de
  `list-dir/SKILL.md` garde un `L="${CLAUDE_SKILLS:?…}/…"`. *Pourquoi* : la décision visait à ne
  pas recopier la RACINE ; ici elle n'apparaît qu'une fois, et écrire dix chemins complets rendrait
  la table illisible. *Portée* : réservé aux blocs de plus de trois commandes ; les consommateurs
  écrivent le chemin en clair.
- **2026-08-29** — Ces trois décisions sont postérieures au figeage du brief : `plan-reviewer` a
  rendu `NON CONFORME` en lisant le plan contre un brief en retard. Le plan suit les arbitrages
  les plus récents ; les défauts de rédaction relevés (Q1, Q3, Q6-Q9) ont été corrigés.
