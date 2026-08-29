---
slug: resolution-chemin-skill
---

## 2026-08-29 — clôture — `6a02642`

**Verdict** : RÉSERVES

### Vérifications exécutées

- `python3 scripts/check_pipeline.py` → **conforme**, 8 contrôles verts (6 : 27 fichiers, aucun
  appel relatif non gardé ; 7 : 2 chemins cités, tous existent ; 8 : 12 renvois, tous résolvent)
- `uvx pytest scripts/tests -q` → **92 passés**, 0 échec
- `uvx pytest skills/list-dir/scripts/tests -q` → **241 passés**, 0 échec
- `python3 scripts/sante_skills.py` → **code 0**, aucune anomalie
- `python3 $HOME/.claude/scripts/sante_skills.py` (la commande exacte du hook `SessionStart`)
  → **code 0**
- `git grep -q '$HOME/.claude/skills' -- skills .claude/implementation/todo/README.md` → **code 1**,
  aucune occurrence
- `grep -q CLAUDE_SKILLS settings.json` → **code 1** ; `git grep -l CLAUDE_SKILLS` ne remonte que
  le brief, le suivi et le plan
- `readlink bin/list-dir` → `../skills/list-dir/scripts/list-dir.py` (relatif) ;
  `readlink bin/impl-list` → `../skills/implementation-tracker/scripts/impl_list.py` (relatif) ;
  `test -x` vert sur les deux
- `test ! -e ~/.local/bin/list-dir` → **vert**, le lien de `31bf551` est bien révoqué
- `which list-dir impl-list` → `/home/debian/.claude/bin/{list-dir,impl-list}`, `bin/` gagne
  dans le `PATH`
- `list-dir validate <registre> --filled` sur les trois registres → **21 / 14 / 0**, tous conformes
- Effet du hook `SessionStart` sur l'utilisateur (stderr d'une sortie non nulle réellement affiché
  en session) → **NON EXÉCUTÉE** : ne s'observe pas depuis un sous-agent (voir R7)

### Conformité à l'intention

- **Critère « un skill consommateur ne contient que les commandes nécessaires »** : *atteint,
  vérifié*. `dette.md` (310 → 298 l.) rend le comportement générique de `new`, `--filled`,
  `migrate` et `move` ; `debt-review/SKILL.md` rend celui de `derive`. J'ai vérifié que
  l'information n'a pas été *supprimée* mais *déplacée* : `contrat-liste.md:174` (table
  `--filled`), `:222` (« `move` est un renommage pur — `git mv`, et rien d'autre »),
  `:307-324` (« elle ne renomme rien et ne reporte aucune valeur »), `:348` (listes dérivées),
  et `list-dir/SKILL.md:49-63` la portent.
- **Critère « la ligne de partage est le domaine, pas la commande »** : *atteint*. La doctrine
  reste chez le consommateur — `dette.md` garde « Un état, pas un journal » (l. 28), la règle de
  solde (l. 174), les trois registres (l. 6-9) — et les invocations concrètes appliquées au
  domaine sont conservées, non remplacées par des renvois nus.
- **Critère « la résolution ne laisse plus de constante recopiée »** : *atteint*, avec la réserve
  R2 sur la portée du garde-fou. Les 8 points d'édition sont à 0, et le contrôle 7 refuse
  désormais activement la forme (`test_ancrage_sur_le_home_refuse`) au lieu de la seule tester
  pour existence — c'est bien la voie de solde que la fiche de dette réclamait.
- **Hors-périmètre** : *respecté*. `dette.md` maigrit de 12 lignes sans se dissoudre ; aucun bloc
  de commande de domaine n'a été remplacé par un renvoi seul.
- **Signaux de dérive** : *aucun matérialisé au sens fort*. La duplication baisse
  (constatée fichier par fichier, cf. R5 pour un résidu) ; aucun consommateur ne déroule la
  procédure générique ; écrire un skill neuf demande une phrase — poser un lien relatif dans
  `bin/` — écrite en un endroit (`contrat.md#dépendances`), donc la machinerie ne s'est pas
  refermée sur elle-même.
- **Symptôme d'origine** : *disparu*. Un skill localise un autre skill par le `PATH`
  (exécutable), par un chemin relatif à la racine (citation), par un lien relatif (renvoi
  documentaire) ou par `shutil.which` (import) — jamais par une constante.

### Qualité du code

- **R1** — `settings.json`, hook `SessionStart` : `python3 $HOME/.claude/scripts/sante_skills.py`
  est la dernière constante ancrée sur le `HOME` du dépôt. Elle est probablement inévitable
  (c'est l'amorçage : rien n'est encore résolu à ce moment), mais aucun contrôle ne la garde et
  aucun texte ne dit qu'elle est l'exception assumée. La fiche de solde énumère ce que le solde
  ne couvre pas et ne la mentionne pas.
- **R2** — `scripts/check_pipeline.py:125-145` : les contrôles 6, 7 et 8 s'appliquent à
  `markdown_files(root, only="skills")`. Or l'étape 12 a converti
  `.claude/implementation/todo/README.md`, qui était un des 8 points d'édition et qu'aucun
  contrôle n'examine. La forme `$HOME/.claude/skills/…` peut y être réintroduite sans qu'aucun
  rouge n'apparaisse : le critère « le compte cesse de croître » est tenu dans `skills/`, pas
  hors de `skills/`.
- **R3** — `scripts/check_pipeline.py:629` (contrôle 8) ne vérifie que l'existence du **fichier**
  visé, l'ancre étant coupée (`test_ancre_seule_ne_casse_pas_le_chemin`). Un renvoi
  `…/contrat.md#section-renommée` reste vert alors qu'il envoie le lecteur en tête de fichier —
  exactement le mode de défaillance « un renvoi mort se lit comme une section absente » que le
  commentaire du contrôle invoque pour justifier son existence.
- **R4** — Trois renvois créés par ce chantier n'ont pas d'ancre alors que leur libellé nomme une
  section : `dette.md:13` « [Répertoires-listes] », `dette.md:170` « [Migrer] »,
  `debt-review/SKILL.md:113` « [Listes dérivées] ». Les titres cibles existent pourtant dans
  `contrat-liste.md` (`## Structure d'un répertoire-liste`, `## Quand le contrat change`,
  `## Listes dérivées`). Le lecteur atterrit au sommet d'une référence de 400 lignes — le renvoi
  fonctionne, il ne conduit pas.
- **R5** — `skills/list-dir/SKILL.md:81` et `contrat-liste.md:142` :
  `Path(shutil.which("list-dir")).resolve().parent` lève `TypeError: expected str… not NoneType`
  si la commande est absente du `PATH`. L'échec est bruyant, ce qui est le comportement voulu,
  mais le message n'oriente pas vers la cause (`bin/` hors du `PATH`) alors que
  `sante_skills.py` sait la formuler. Constat, pas exigence : personne ne l'a demandé.

### Dette induite

- **R6** — Duplication résiduelle du comportement générique de `move` : `dette.md` a cédé au
  fournisseur la phrase « `move` est un `git mv`, et rien d'autre », mais
  `.claude/implementation/todo/README.md:25` et `skills/debt-review/SKILL.md:270` la réénoncent
  encore. La même chose se lit donc à quatre endroits (`list-dir/SKILL.md:51`,
  `contrat-liste.md:222`, plus ces deux-là). Le brief ne visait nommément que `dette.md` ; le
  signal de dérive « la même explication se lit encore à deux endroits », lui, est général.
- **R7** — Le système entier repose désormais sur deux artefacts hors dépôt : la ligne
  `export PATH="$HOME/.claude/bin:$PATH"` de `~/.zshrc:108`, et le fait que le stderr du hook
  `SessionStart` (sortie 1) parvienne effectivement à l'utilisateur. Le premier n'est documenté
  nulle part dans le dépôt hors du message d'erreur de `sante_skills.py` — il n'existe pas de
  note d'installation. Le second, je n'ai pas pu l'établir : si Claude Code n'expose le stderr
  d'un hook non nul qu'en mode transcript, la seule parade contre le mode de défaillance « 127 +
  stdout vide » est muette au moment où elle compte. C'est le pivot de la conception, et il est
  invérifiable depuis ici.
- **R8** — Le plan `.claude/plans/glittery-kindling-pillow.md` est resté à sa rédaction initiale :
  9 étapes, mécanisme `CLAUDE_SKILLS` dans `settings.json`, forme `"${CLAUDE_SKILLS:?}/…"`. Le
  chantier a exécuté 13 étapes et un mécanisme entièrement différent (`bin/` + `PATH`). Le
  journal du suivi consigne honnêtement le virage et le suivi fait foi — mais le plan versionné
  décrit maintenant un chantier qui n'a pas eu lieu, et il est référencé par le frontmatter du
  suivi comme par le brief. Un lecteur futur qui ouvrira `plan:` lira un état faux.

### Bloquants

Aucun.

---

## 2026-08-29 — clôture — `8f5cd52`

**Verdict** : RÉSERVES

Second audit du même chantier, sur le commit `8f5cd52` (« réserves R3 à R8 de l'audit »). Il porte
sur l'ensemble `master...resolution-chemin-skill`, avec attention particulière au traitement des
réserves du premier audit. Arbre de travail **propre** au moment de l'audit ; le fichier non suivi
`bin/zz-sonde` observé auparavant a disparu.

### Vérifications exécutées

- `python3 scripts/check_pipeline.py` → **conforme**, 8 contrôles verts (6 : 27 fichiers ; 7 :
  2 chemins cités, tous existent ; 8 : 12 renvois, tous résolvent — ancres comprises désormais)
- `uvx pytest scripts/tests -q` → **97 passés**, 0 échec (92 au précédent audit : +5, conformes
  aux tests ajoutés pour R3 et pour les deux flux du diagnostic)
- `uvx pytest skills/list-dir/scripts/tests -q` → **241 passés**, 0 échec
- `python3 scripts/sante_skills.py` → **code 0**, aucune anomalie
- `list-dir validate … --filled` sur les trois registres → `technical-debt` **21**,
  `technical-debt-solde` **14**, `technical-debt-ecarte` **0** — tous conformes
- `git grep -q '$HOME/.claude/skills' -- skills .claude/implementation/todo/README.md` → **code 1**
- `git status --short` → **vide**
- `uvx ruff check scripts/` → **All checks passed**
- Sonde sur le contrôle 8, ancre de niveau `###` (arbre jetable, hors dépôt) → **rouge** (cf. R9)
- Sonde sur le contrôle 8, lien à titre Markdown vers un fichier absent (arbre jetable) →
  **vert**, le renvoi mort n'est pas vu (cf. R10)
- Sonde sur les contrôles 6 et 7 hors de `skills/` (arbre jetable) → « aucun fichier examiné dans
  skills/ — contrôle sans objet » (confirme R2)
- Affichage réel du `stderr` du hook `SessionStart` à l'utilisateur → **NON EXÉCUTÉE** : ne
  s'observe pas depuis un sous-agent (inchangé depuis R7)

### Suite donnée aux réserves du premier audit

- **R3 — traitée.** `RENVOI_INTER_SKILL` capture l'ancre, et le contrôle 8 la compare aux sections
  du fichier cible. Les deux tests qui posaient des ancres bidon sur un fichier sans section ont
  été corrigés au lieu d'être laissés verts par accident ; `test_ancre_morte` et
  `test_renvoi_sans_ancre_reste_licite` couvrent les deux cas. Correction réelle, pas cosmétique —
  mais elle introduit R9 et R10.
- **R4 — traitée.** Les trois renvois portent leur ancre, et le libellé « Migrer » devient
  « Quand le contrat change », qui est le titre réel. Vérifié par le contrôle 8 lui-même, qui
  refuserait désormais une ancre inventée.
- **R5 — traitée.** `shutil.which` nul lève un `SystemExit` qui nomme la cause, aux trois endroits
  où l'amorçage est écrit (`list-dir/SKILL.md`, `contrat-liste.md`, `listdir/__init__.py`).
- **R6 — traitée.** « `move` est un `git mv` » retiré de `todo/README.md` et de
  `debt-review/SKILL.md`. Les occurrences restantes que j'ai relevées sont chez le fournisseur
  (`list-dir/SKILL.md`, `contrat-liste.md`, code et tests de `listdir`) ou désignent un vrai
  `git mv` de procédure (`cloture.md`) : la duplication visée a bien disparu.
- **R7 — partiellement traitée.** `contrat.md#dépendances` porte désormais le geste
  d'installation (`export PATH="$HOME/.claude/bin:$PATH"`) et le mode de défaillance du `stderr`
  tronqué ; le diagnostic part sur deux flux, avec trois tests dont un qui **impose** que le
  `stderr` tienne sur une seule ligne auto-suffisante. Ce qui reste hors de portée : l'affichage
  effectif de ce `stderr` à l'utilisateur, toujours invérifiable depuis un sous-agent.
- **R8 — traitée.** Le plan porte un avertissement en tête et n'est pas réécrit. Le choix est
  motivé dans le fichier même.
- **R1 — non traitée**, conformément à ce que l'appelant annonce. Le hook `SessionStart` de
  `settings.json` porte toujours `python3 $HOME/.claude/scripts/sante_skills.py`. Je maintiens le
  constat : ce n'est pas la constante qui gêne — l'amorçage n'a rien d'autre — c'est qu'aucun
  texte ne la déclare exception assumée, et que la fiche de solde
  `technical-debt-solde/chemin-skill-code-en-dur.md` énumère « ce que le solde ne couvre pas »
  sans la mentionner.
- **R2 — non traitée**, et re-vérifiée par sonde ci-dessus. Les contrôles 6, 7 et 8 s'appliquent à
  `markdown_files(root, only="skills")`. Un appel `python3 "$HOME/.claude/skills/…/y.py"` déposé
  dans `.claude/implementation/todo/README.md` — qui était l'un des 8 points d'édition convertis
  par l'étape 12 — ne produit aucun rouge. Le critère « le compte cesse de croître » est tenu
  dans `skills/`, pas hors de `skills/`. La fiche de solde ne le dit pas non plus.

### Constats nouveaux

- **R9** — `scripts/check_pipeline.py:626-653` (contrôle 8) compare l'ancre aux seules sections
  produites par `sections()`, qui ne connaît que les titres `## `. Une ancre légitime vers un
  titre de niveau 3 est donc déclarée morte. Établi sur arbre jetable : un renvoi
  `…/contrat.md#sous-section` vers un `### Sous-section` existant produit
  « ancre morte : … — le renvoi fonctionne, il ne conduit pas ». Aucun renvoi du dépôt n'est
  aujourd'hui dans ce cas, d'où le vert ; le défaut est latent et son message affirme le
  contraire de la réalité, ce qui pousse à « corriger » un lien juste. Le contrôle 2, lui, se sert
  de `sections()` pour un usage où le niveau 2 est le bon grain — la fonction est réutilisée hors
  de son domaine, sans le dire.
- **R10** — Même correctif, effet de bord inverse : le motif est passé de
  `\]\((\.\./[^)#\s]+)` à `\]\((\.\./[^)#\s]+)(#[^)\s]+)?\)`, qui exige la parenthèse fermante
  immédiatement après le chemin ou l'ancre. Un lien à titre Markdown —
  `[X](../cible/disparu.md "titre")` — n'est plus reconnu **du tout** : sonde sur arbre jetable,
  un renvoi mort de cette forme sort **vert**. Avant `8f5cd52`, il était détecté. Aucun lien de
  cette forme n'existe aujourd'hui dans `skills/` ; la couverture a néanmoins reculé pendant que
  le contrôle se durcissait, et rien ne le signale.
- **R11** — À `8f5cd52`, R1 et R2 ne sont consignées nulle part : ni fiche au registre
  `technical-debt`, ni mention dans `technical-debt-solde/chemin-skill-code-en-dur.md`. Le suivi
  annonce « Restent R1 et R2, à porter au registre de dette » comme action de clôture, ce qui est
  cohérent avec un chantier non clos — mais tant que ce geste n'est pas fait, la seule trace de
  ces deux angles morts est ce fichier d'audit, qui partira en `done/` avec le chantier. C'est le
  mode de défaillance que le registre existe pour éviter.
- **R12** — `scripts/check_pipeline.py:645`, `cast("str", ancre)` est redondant : `ancre` est déjà
  restreint à `str` par le `continue` de la ligne précédente. Détail de style, dans un fichier qui
  par ailleurs commente abondamment le *pourquoi* et n'a pas d'autre `cast` défensif de ce type.

### Conformité à l'intention

Inchangée par rapport au premier audit, et re-vérifiée :

- **Critère « le consommateur ne contient que les commandes nécessaires »** : *atteint, vérifié*.
- **Critère « la ligne de partage est le domaine, pas la commande »** : *atteint, vérifié* —
  R6 traitée renforce ce point, la duplication de `move` ne subsiste plus que chez le fournisseur.
- **Critère « la résolution ne laisse plus de constante recopiée »** : *atteint*, sous la réserve
  R2 (portée du garde-fou) et R1 (constante d'amorçage non déclarée).
- **Hors-périmètre** : *respecté*. Le diff `6a02642..HEAD` ne touche à la doctrine d'aucun
  consommateur et ne remplace aucune commande de domaine par un renvoi nu.
- **Signaux de dérive** : *aucun matérialisé*. Le geste d'installation unique est écrit en un seul
  endroit — écrire un skill neuf n'exige pas de comprendre un mécanisme.
- **Symptôme d'origine** : *disparu*.

### Bloquants

Aucun. R9 et R10 portent sur un contrôle du garde-fou qui reste plus strict qu'avant le chantier ;
R1, R2 et R11 sont des angles morts connus, à porter au registre plutôt qu'à corriger ici.
