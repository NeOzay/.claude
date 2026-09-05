---
slug: decoupe-contrat-liste
titre: Découper et réécrire la référence de list-dir
statut: validé
execution: direct
créé: 2026-09-05
---

## Intention

**Symptôme** : `skills/list-dir/references/contrat-liste.md` « a fortement gonflé » — 828 lignes,
13 sections `##`, accrétées chantier après chantier (dit).
**But** : « couper les responsabilités en plusieurs fichiers », et « en profiter aussi pour
factoriser la documentation, comme réagencer et réécrire les sections » (dit). La gêne principale
est **la dispersion d'un même sujet** — `derive` décrit à trois endroits, le contrat à trois autres
— puis la taille brute (dit).

## Critères de réussite

- `python3 scripts/check_pipeline.py` passe — le contrôle 8 sanctionne tout renvoi inter-skill
  (`../…#ancre`) devenu mort (dépôt: scripts/check_pipeline.py, contrôle 8)
- `skills/list-dir/SKILL.md` référence les nouveaux documents (dit)
- `contrat-liste.md` supprimé, et aucun renvoi résiduel vers lui hors archives
  `.claude/implementation/done/`
- **inventaire des règles** de `contrat-liste.md` figé dans le plan (une ligne par règle
  normative), chacune cochée contre les nouveaux fichiers avant toute suppression (tranché)

## Hors-périmètre

- aucune modification de `contrat-liste.md` pendant le chantier : « c'est le document de
  référence », il sert de source jusqu'à la fin, puis est **supprimé une fois les nouveaux
  fichiers validés** (dit)
- pas de changement de comportement de `list-dir` : ni `scripts/listdir/`, ni les tests
- — non abordé : élargir le contrôle 8 aux renvois voisins/intra-fichier (dette ouverte
  `renvois-sans-prefixe-hors-du-controle-des-ancres`)

## Signaux de dérive

- si une règle change de sens sous couvert de réécriture, s'arrêter : c'est de la doctrine, pas
  de la mise en forme (dit : « c'est le document de référence »)
- si un `> *Mode de défaillance*` disparaît sans être intégré ailleurs, c'est une perte, pas une
  condensation (dit)
- si le chantier touche `scripts/listdir/` ou les tests, il a débordé

### Ce que la réécriture peut faire

- **condenser** deux passages qui disent la même chose sous deux angles (dit)
- **intégrer les « modes de défaillance » aux exemples et à l'utilisation des fonctionnalités**,
  au lieu de les laisser en blocs cités isolés (dit)

## Contraintes connues de l'utilisateur

- **Intouchable jusqu'à la fin** : `contrat-liste.md` est la source de vérité de la réécriture (dit)
- **Point d'entrée** : c'est `SKILL.md` qui référence les nouveaux documents (dit)
- **Un sujet = un fichier = une autorité** : les autres fichiers y renvoient par lien plutôt que
  de redire, comme entre skills (tranché ; dépôt: e9f6a81 « définir chaque règle à un seul endroit »)
- **Consommateurs externes** : `debt-review/SKILL.md` (2 ancres), `implementation-tracker/references/dette.md`
  (6 ancres), `listdir/commands/contract.py:34` (dépôt: grep)
- **Renvois internes non contrôlés** : les 6 `](#ancre)` du fichier deviendront des renvois vers
  fichier voisin, forme qui échappe au contrôle 8 (dépôt: .claude/implementation/todo/technical-debt/renvois-sans-prefixe-hors-du-controle-des-ancres.md)

## Incertitudes à lever en plan

- où passent exactement les coupes, sujet par sujet — l'axe est arrêté (un sujet = un fichier),
  le découpage nominatif reste à établir en plan
- les renvois entre nouveaux fichiers voisins échapperont au contrôle 8 : à vérifier à la main,
  ou à l'occasion solder la dette `renvois-sans-prefixe-hors-du-controle-des-ancres` (à trancher
  en plan)
