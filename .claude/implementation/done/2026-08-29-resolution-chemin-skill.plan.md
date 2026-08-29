# Résolution du chemin de skill, et fin de la recopie du mode d'emploi

> **⚠ Ce plan décrit l'intention initiale, pas le chantier exécuté.** Il a été approuvé le
> 2026-08-29 avec 9 étapes et un mécanisme `CLAUDE_SKILLS` posé dans `settings.json`. En cours de
> route, ce mécanisme a été abandonné — `settings.json` est versionné, et la valeur devait y être
> un chemin absolu machine-spécifique. Il a été remplacé par `bin/`, un répertoire versionné de
> liens **relatifs** ajouté au `PATH` par le profil, et le chantier a compté 13 étapes.
>
> **Ce qui fait foi : le fichier de suivi**, `.claude/implementation/resolution-chemin-skill.md` —
> ses étapes réelles et son journal de décisions, qui consigne le virage et ses raisons. Ce plan
> est conservé tel qu'approuvé : le réécrire après coup effacerait l'écart entre ce qui était
> prévu et ce qui a été fait, qui est précisément ce que le dispositif cherche à rendre visible.


## Contexte

Les skills de ce dépôt forment un système interdépendant, mais chacun localise les autres par une
constante `$HOME/.claude/skills/…` recopiée à chaque point d'usage — **10 points d'édition** à
`HEAD` (5 vers `list-dir.py`, 4 vers `impl_list.py`, 1 vers le répertoire `list-dir/`). La dette
`chemin-skill-code-en-dur` (ouverte le 2026-08-14, amendée le 2026-08-24) le dit : le contrôle 7 a
soldé le symptôme, la cause reste, et le compte est passé de 3 à 8 points depuis l'ouverture,
« puisque le contrôle 6 impose cette écriture ».

Le second défaut est plus coûteux que le premier : les consommateurs ne recopient pas seulement le
chemin de `list-dir`, ils recopient son **mode d'emploi**. `dette.md` porte 11 blocs `bash` et
réexplique `--filled`, `migrate` et `move` ; `cloture.md` en porte 7 ; `debt-review/SKILL.md` en
porte 12 et réexplique `derive` et `merge`. Tout cela est déjà écrit dans `list-dir/SKILL.md` et
`references/contrat-liste.md` — deux versions d'une même chose, qui ne peuvent que diverger.

Résultat visé : un skill s'ancre sur une racine résolue au lieu d'une constante, et ne contient
que les commandes nécessaires à son domaine — les détails restent chez le skill qui propose la
commande.

Brief : `.claude/implementation/resolution-chemin-skill.brief.md` (validé, `execution: direct`).

## Décisions déjà arbitrées

- **Racine résolue, échec fermé** : la variable `CLAUDE_SKILLS` est posée dans `settings.json`
  (champ `env`). Un repli `:-` a été écarté : il rejoue le mode de défaillance R2 (127 + `stdout`
  vide, lu comme un résultat) sur une installation hors `~/.claude`.
- **Forme d'emploi : aucune variable locale.** La première occurrence d'un bloc porte la garde,
  les suivantes non :

  ```bash
  "${CLAUDE_SKILLS:?CLAUDE_SKILLS non défini}/list-dir/scripts/list-dir.py" validate "$T/technical-debt"
  "$CLAUDE_SKILLS/list-dir/scripts/list-dir.py" list "$T/technical-debt" --sort date
  ```

  C'est ce qui répond à l'incertitude « sous peine de remplacer 10 points d'édition par 10
  définitions » : il n'y a plus de définition du tout, et le contrôle 6 exige la garde au premier
  emploi de chaque bloc. Le `L="…"` des blocs actuels disparaît.
- **Renvois documentaires : tout en relatif** — `[Titre](../list-dir/references/contrat-liste.md#ancre)`.
  Les **8** renvois inter-skills existants le sont **déjà tous** : il n'y a rien à convertir. Le
  travail se réduit à écrire la règle et à poser le contrôle qui la tient (étape 3).
- **Le lien `~/.local/bin/list-dir` de `31bf551` est supprimé.** Le retrait de `python3` est conservé.
- **Ligne de partage** : reste chez le consommateur la doctrine du domaine et l'emploi concret des
  commandes pour ce domaine ; part chez le fournisseur le comportement générique de la commande.

## Inconnue à lever en premier

`settings.json` étend-il `$HOME` dans le champ `env` ? Si non, la valeur doit être le chemin absolu
réel. Tout le reste en dépend : c'est l'étape 1, et elle exige un redémarrage de session pour être
vérifiée.

## Étapes

1. **Poser `CLAUDE_SKILLS` et vérifier son expansion** — `settings.json` (champ `env`).
   Écrire `"env": { "CLAUDE_SKILLS": "$HOME/.claude/skills" }`, redémarrer la session, constater.
   Si la valeur arrive non étendue, la remplacer par le chemin absolu — la variable **est** le
   point de portabilité, une valeur machine-spécifique y est légitime.

   **Point d'arrêt du chantier.** L'expansion ne s'observe pas depuis la session qui écrit le
   fichier : l'étape se termine en demandant le redémarrage, et le constat est la première
   action de l'étape 2. Ne pas enchaîner avant.
   — vérif, dans le tour courant : `python3 -c "import json;print(json.load(open('settings.json'))['env']['CLAUDE_SKILLS'])"`
   — vérif, après redémarrage : `test -d "${CLAUDE_SKILLS:?}" && echo ok`

2. **Étendre les contrôles du garde-fou pour accepter la nouvelle forme** — `scripts/check_pipeline.py`,
   `scripts/tests/`. Le contrôle 6 (`ABSOLUS`, ligne 411) accepte `$CLAUDE_SKILLS/` et
   `${CLAUDE_SKILLS:?…}/`, et **exige la garde au premier emploi de chaque bloc** ; le contrôle 7
   (`CHEMIN_SKILL`, ligne 470) reconnaît ces formes et résout la cible. L'ancienne forme
   `$HOME/.claude/…` reste tolérée à ce stade — la durcir maintenant rendrait tout rouge avant la
   conversion. Ajouter les cas de test correspondants.
   — vérif : `uvx pytest scripts/tests -q` vert, `python3 scripts/check_pipeline.py` conforme

3. **Nouveau contrôle : les renvois documentaires inter-skills résolvent** — `scripts/check_pipeline.py`,
   `scripts/tests/`. Un lien Markdown `../<skill>/…` depuis un `.md` de `skills/` doit désigner un
   fichier existant. C'est ce qui rend le choix « tout en relatif » sûr face à un renommage.
   — vérif : un lien volontairement faux fait crier le contrôle ; `uvx pytest scripts/tests -q` vert

4. **`list-dir` : révoquer le lien, ancrer les appels, corriger l'usage résiduel** —
   `skills/list-dir/SKILL.md`, `skills/list-dir/scripts/listdir/commands/help.py`.
   `SKILL.md` repasse à `"${CLAUDE_SKILLS:?}/list-dir/scripts/list-dir.py"` (sans `python3`), la section sur le lien
   `~/.local/bin` disparaît. `help.py:30` porte encore `USAGE = "list-dir.py …"` en dur alors que
   `list-dir.py:39` le construit depuis `argv[0]` : l'aligner. Supprimer `~/.local/bin/list-dir`.
   — vérif : `uvx pytest skills/list-dir/scripts/tests -q` vert ; `uvx ruff check skills/list-dir` ;
   `test ! -e ~/.local/bin/list-dir` ; `! grep -q 'local/bin' skills/list-dir/SKILL.md`

5. **Dégraisser `dette.md`** — `skills/implementation-tracker/references/dette.md` (310 lignes,
   11 blocs `bash`). Garder la doctrine — « un état, pas un journal », la règle de solde, les trois
   registres — et les commandes appliquées au domaine dette. Retirer le comportement générique
   (`dette.md:170` sur `--filled`, `dette.md:181` sur `migrate`) au profit d'un renvoi relatif vers
   `../list-dir/references/contrat-liste.md`. Ancrer les appels sur `$CLAUDE_SKILLS`.
   — vérif : `python3 scripts/check_pipeline.py` conforme ; aucun `$HOME/.claude` restant dans le
   fichier ; les renvois résolvent (contrôle de l'étape 3)

6. **Dégraisser `cloture.md`** — `skills/implementation-tracker/references/cloture.md`
   (206 lignes, 7 blocs). La séquence propre à la clôture reste ; ce que `new`, `validate --filled`
   et `move` garantissent part chez `list-dir` par renvoi relatif. Ancrer les appels sur `$CLAUDE_SKILLS`.
   — vérif : `python3 scripts/check_pipeline.py` conforme ;
   `! grep -q '\$HOME/\.claude' skills/implementation-tracker/references/cloture.md`

7. **Dégraisser `debt-review`** — `skills/debt-review/SKILL.md` (344 lignes, 12 blocs),
   `skills/debt-review/references/gabarit-rapport.md`. Même traitement : la conduite d'une revue
   reste, l'explication de ce que `derive` et `merge` garantissent part chez `list-dir`.
   — vérif : `python3 scripts/check_pipeline.py` conforme ;
   `! git grep -q '\$HOME/\.claude' -- skills/debt-review`

8. **Convertir les points d'édition restants** — `skills/implementation-tracker/references/contrat.md`
   (3 points, dont la table des dépendances), `skills/implementation-tracker/SKILL.md` (2 points vers
   `impl_list.py`), `.claude/implementation/todo/README.md` (1 point, hors `skills/` mais même défaut).
   La table `#dépendances` déclare désormais `CLAUDE_SKILLS` comme dépendance à part entière, avec
   son contrôle.
   — vérif : `! git grep -q '\$HOME/\.claude/skills' -- skills .claude/implementation/todo/README.md`

9. **Durcir le garde-fou et solder la dette** — `scripts/check_pipeline.py`, `scripts/tests/`,
   `.claude/implementation/todo/technical-debt/chemin-skill-code-en-dur.md`. Le contrôle 6 refuse
   désormais la forme `$HOME/.claude/skills/…` : c'est ce qui empêche le compte de repartir à la
   hausse, et c'est précisément ce que la fiche demande pour solder. Déplacer la fiche vers
   `technical-debt-solde/` par `move` (git mv, l'historique suit), avec la preuve.
   — vérif : `python3 scripts/check_pipeline.py` conforme ; un `$HOME/.claude/skills` réintroduit
   dans un `.md` de `skills/` fait crier le contrôle 6 ; `"$CLAUDE_SKILLS/list-dir/scripts/list-dir.py" validate`
   vert sur les **trois** registres (`technical-debt/`, `-solde/`, `-ecarte/`)

## Vérification d'ensemble

```bash
python3 scripts/check_pipeline.py                        # 7 contrôles + le nouveau, conformes

uvx pytest scripts/tests -q                              # garde-fou
uvx pytest skills/list-dir/scripts/tests -q              # 241 tests, non régressés
(cd skills/list-dir && uvx ruff check . && uvx --with pytest basedpyright)
# Plus aucune constante dans le code vivant. Les archives de `done/`, la fiche de dette et
# `technical-debt-solde/filtres-listing-hook-rtk.md` en portent 24 : elles relatent un état
# passé et ne se réécrivent pas.
! git grep -q '\$HOME/\.claude/skills' -- skills .claude/implementation/todo/README.md
grep -ril 'dette\|debt' skills/list-dir/                 # rien : l'invariant de 53eff2d tient
```

## Ce que ce chantier ne fait pas

- Il ne vide pas les consommateurs de leur doctrine : `dette.md` maigrit, il ne se dissout pas.
- Il ne remplace pas les commandes concrètes du domaine par des renvois nus.
- Il ne touche pas aux skills hors du pipeline (`nvim-mini-test`, `emmylua-ls`, `git-smart-commit`),
  qui ne citent aucun chemin de skill.

## Points relevés par la relecture, laissés à ton arbitrage

- Le brief a été figé **avant** les trois arbitrages du 2026-08-29 (racine résolue plutôt que lien,
  `:?` plutôt que repli, documentaire en relatif). Le relecteur lit donc le plan comme contredisant
  la décision « les deux mécanismes sont unifiés » et la forme `${CLAUDE_SKILLS:-…}` du brief. Le
  plan suit tes arbitrages les plus récents ; c'est le brief qui est en retard, et le fichier de
  suivi consignera ces trois décisions.

## Signaux d'arrêt

Repris du brief, actifs pendant l'exécution :

- la duplication d'information ne baisse pas — la même explication se lit encore à deux endroits ;
- un consommateur déroule toutes les étapes au lieu de nommer l'essentiel ;
- écrire un skill neuf exige d'abord de comprendre le mécanisme de résolution.
