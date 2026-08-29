---
slug: resolution-chemin-skill
titre: Les skills se résolvent entre eux au lieu de se citer en dur
statut: validé
execution: direct
créé: 2026-08-29
---

## Intention

**Symptôme** : « je vois mes skills comme un système interdépendant » (dit) — or chaque skill
localise les autres par une constante `$HOME/.claude/skills/…` recopiée à chaque point d'usage.
Le déclencheur immédiat : `list-dir` s'appelait `python3 <chemin absolu>`, ce qui est verbeux et
fragile.

**But** : qu'un skill trouve un autre skill par résolution, non par constante — et qu'il **fasse
référence aux éléments pertinents de l'autre skill au lieu d'expliquer comment l'utiliser** (dit).
Les dépendances entre skills se déclarent et se vérifient, elles ne se supposent pas.

## Critères de réussite

- **Un skill consommateur ne contient que les commandes nécessaires** : les détails restent
  dans le skill qui propose la commande (dit). La ligne à exécuter demeure chez l'appelant ;
  ce qui disparaît, c'est l'explication du comportement, des options et des garanties — elle
  vit une seule fois, chez le fournisseur, et un renvoi y mène.
- **La ligne de partage est le domaine, pas la commande** : `dette.md` explique le fonctionnement
  des dettes et montre comment employer les commandes de `list-dir` pour cet usage (dit). Ce qui
  reste chez le consommateur : la doctrine du domaine et l'emploi concret des commandes pour ce
  domaine. Ce qui part chez le fournisseur : le comportement générique de la commande — par
  exemple « `--filled` exige qu'aucun marqueur ne subsiste » ou « `migrate` ne renomme rien et
  ne reporte aucune valeur » (dépôt: dette.md:170, dette.md:181).
- La résolution du chemin de skill ne laisse plus de constante recopiée : le compte de points
  d'édition cesse de croître avec chaque skill neuve.

## Hors-périmètre

- **Vider les skills consommateurs de leur doctrine** : `dette.md` garde « un état, pas un
  journal », la règle de solde et les trois registres — il maigrit, il ne se dissout pas (dit)
- Les commandes concrètes appliquées au domaine restent chez le consommateur : le chantier ne
  les remplace pas par des renvois nus (dit)

## Signaux de dérive

- **La duplication d'information ne baisse pas** : si, à la fin d'une étape, la même explication
  se lit encore à deux endroits, l'étape n'a rien soldé (dit)
- **Toutes les étapes sont réexpliquées au lieu de l'essentiel** : un consommateur qui déroule
  la procédure complète au lieu de nommer ce qu'il veut obtenir reproduit le défaut qu'on
  corrige, à un autre endroit (dit)
- **Le mécanisme devient une machinerie** : si écrire un skill neuf exige d'abord de comprendre
  le mécanisme de résolution, il a mangé son propre bénéfice (dit, arbitré 2026-08-29)

## Contraintes connues de l'utilisateur

- **Vision** : les skills forment un système interdépendant, pas des outils isolés (dit)
- **Réutiliser** : le mécanisme `REQUIRES` du chargeur `list-dir` vérifie déjà les outils du
  `PATH` avant d'appeler une commande — précédent de « dépendance déclarée, pas supposée »
  (dépôt: skills/list-dir/scripts/listdir/loader.py, contrat.md#dépendances)
- **État mesuré** : 10 points d'édition `$HOME/.claude/skills/…` à HEAD — 5 vers `list-dir.py`,
  4 vers `impl_list.py`, 1 vers le répertoire `list-dir/` ; plus 6 renvois documentaires en
  chemin relatif `../<skill>/references/…` (dépôt: git grep -o sur HEAD -- skills)
- **Dette ouverte** : `chemin-skill-code-en-dur`, ouverte 2026-08-14, amendée 2026-08-24 —
  « seule une résolution du chemin de skill à la source y mettrait fin », le compte est passé
  de 3 à 8 points depuis l'ouverture
  (dépôt: .claude/implementation/todo/technical-debt/chemin-skill-code-en-dur.md)
- **Le garde-fou impose la forme actuelle** : le contrôle 6 exige un chemin absolu pour tout
  appel de script depuis un `.md` de `skills/`, né de l'audit du 2026-08-14 (127 + stdout vide
  lu comme un résultat). Le contrôle 7 vérifie que ces chemins existent, sans borner leur
  nombre (dépôt: scripts/check_pipeline.py:395-460)
- **Le mode d'emploi de `list-dir` est recopié chez ses consommateurs**, pas seulement son
  chemin : `implementation-tracker/references/dette.md` porte 11 invocations et réexplique
  `--filled`, `migrate` (« ne renomme rien et ne reporte aucune valeur ») et `move` ;
  `cloture.md` recopie la séquence `list`/`new`/`validate --filled` ; `debt-review/SKILL.md` et
  `gabarit-rapport.md` réexpliquent le comportement de `derive` et de `merge`. Tout cela est
  déjà dit dans `list-dir/SKILL.md` et `references/contrat-liste.md`
  (dépôt: grep des commandes sur les quatre fichiers)
- **Précédent de la règle** : le contrat du tracker interdit déjà au brief de déborder sur le
  plan — « deux versions d'une même chose ne peuvent que diverger »
  (dépôt: skills/intent-brief/SKILL.md, section Articulation)
- **Déjà commité** : `31bf551` retire `python3` et pose `~/.local/bin/list-dir` — le lien
  n'est pas versionné et le contrôle 6 est aveugle à un appel nu (dépôt: git show 31bf551)

## Décisions arbitrées

Prises le 2026-08-29, par `AskUserQuestion`.

- **Racine de skills résolue**, et non un lien dans le `PATH` : une définition partagée du type
  `SKILLS="${CLAUDE_SKILLS:-$HOME/.claude/skills}"` donne la racine, chaque skill s'y ancre.
  Un seul point d'édition pour tout le système, **aucun lien hors dépôt**, et le contrôle 6 du
  garde-fou reste valable tel quel.
- **Conséquence sur `31bf551`** : le lien `~/.local/bin/list-dir` n'est pas la voie retenue.
  `list-dir/SKILL.md` revient à un appel par chemin, ancré sur la racine résolue. Le retrait
  de `python3`, lui, est conservé.
- **Les deux mécanismes de liaison sont unifiés** : l'exécutable et le documentaire
  (`../<skill>/references/…`, 6 renvois) obéissent à une même façon de désigner un autre skill.

## Incertitudes à lever en plan

- forme exacte de la résolution documentaire : un renvoi Markdown ne s'évalue pas comme une
  variable de shell — reste à trouver ce qui joue le rôle de `$SKILLS` pour un lien dans un `.md`
- où vit la définition partagée de `SKILLS`, et comment un skill la reprend sans la recopier —
  sous peine de remplacer 10 points d'édition par 10 définitions
- comment les contrôles 6 et 7 du garde-fou évoluent une fois la forme `$HOME/…` remplacée
