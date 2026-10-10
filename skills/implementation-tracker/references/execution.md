# Phase 4 — Maintenir le fichier pendant la session

Le fichier est mis à jour **en continu**, sans que l'utilisateur ait à le demander. Relire le
fichier avant chaque écriture. Toujours actualiser `maj` en même temps que le contenu.

Déclencheurs d'écriture :

| Événement | Action |
|---|---|
| Travail d'une étape commencé | La passer en `[>]` |
| Étape terminée | Cocher `[x]`, **mesurer le contexte** (voir ci-dessous), puis **proposer le commit d'étape**, qui pose le tag `<L>E<n>`, avec ses choix |
| Modification après le commit de l'étape N, N+1 non commencée | Retouche : **mesurer le contexte** (voir ci-dessous), puis **proposer le commit de Retouche**, qui pose le tag `<L>E<N>.<k>`, avec ses choix |
| Blocage | Passer l'étape en `[!]` + raison, `statut = "bloqué"` |
| Déblocage | Repasser en `[>]`, `statut = "en-cours"` |
| Décision d'architecture arrêtée | Ligne dans le journal (voir règle ci-dessous) |
| Le plan ne colle plus au réel | **Modifier les étapes** et le dire. Ne jamais bricoler en silence |
| **Signal de dérive du brief déclenché** | **S'arrêter**, le nommer, en reparler avant de continuer |
| Diff `base`↔`<slug>` au-delà de 400 lignes | **Proposer** un audit intermédiaire, étapes restantes à l'appui (`audit.md`) |
| Demande hors-périmètre | Le signaler, proposer soit d'élargir le périmètre (voir ci-dessous), soit une nouvelle impl |
| Problème constaté hors du périmètre | Le noter au journal — il ira au registre de dette à la clôture (`dette.md`) |

## Quand le périmètre change

Un élargissement accepté par l'utilisateur s'écrit dans `## Objectif et périmètre` du **suivi** —
daté, avec une entrée au journal — et jamais dans le brief. C'est la seule exception au « repris du
brief, pas reformulé » : [Autorité et divergence](contrat.md#autorité-et-divergence).

## Retouche

Entre le commit de l'étape N et le début de N+1, toute modification est une Retouche de l'étape
N, commitée par `git-smart-commit`, type 2, cas « Retouche » :
[Commit rapide de chantier](../../git-smart-commit/references/etape.md). Le suivi ne trace pas les
Retouches : l'étape N reste `[x]`, aucune étape ne s'ajoute, et une décision prise en Retouche va
au journal comme toute autre.

## Commits de session

Une étape peut se retrouver **à cheval sur deux sessions**, quand la session s'interrompt. Le
compteur se cale donc sur la **session**, pas sur l'étape. Commits de session et d'étape,
messages et tags : `git-smart-commit`, type 2 —
[Commit rapide de chantier](../../git-smart-commit/references/etape.md).

## Après un commit d'Étape ou de Retouche

`git-smart-commit` propose le commit avec ses choix ; le choix fait, la suite revient au tracker :

| Choix | Suite |
|---|---|
| Valider et passer à l'Étape suivante | Passer l'Étape suivante en `[>]` et la commencer |
| Valider et attendre | Rendre la main |
| Valider et commencer la Passation | La Passation, ci-dessous |
| Valider et lancer l'audit de Clôture | La Clôture, Phase 5 du `SKILL.md` |

## Passation

La Passation fait passer un Chantier d'une session à la suivante. Elle s'offre comme choix d'un
commit, et de deux seulement : `<L>E0`, toujours ([Création](creation.md)) ; un commit d'Étape ou
de Retouche, quand le contexte dépasse le seuil.

**Avant de proposer un commit d'Étape ou de Retouche, mesurer le contexte** de la session :

```bash
contexte
```

| Mesure | Action |
|---|---|
| Au-delà de 300 000 tokens | Demander à `git-smart-commit` le choix « Valider et commencer la Passation », mesure à l'appui |
| 300 000 tokens ou moins | Rien, et la mesure ne se dit pas |
| Indisponible (sortie non nulle) | Le dire, avec le message rendu, sans ajouter le choix |

Le seuil laisse à l'Étape suivante la marge qui la tient sous 400 000 tokens ; le choix écarté,
l'utilisateur tient seul ce plafond. Le contexte mesuré avant la proposition, la Passation devient
l'un des choix du commit au lieu d'une question de plus après lui. Après le commit, aucun travail
n'est en cours et le suivi dit exactement où l'on en est : rien d'inachevé n'est à décrire. Une
mesure indisponible ne se devine pas : une Passation proposée à l'aveugle serait de trop ou trop
tard.

**La Passation choisie**, dans cet ordre :

1. Réécrire la section `## Passation` du Suivi, telle que la semence la décrit
   (`gabarit contract suivi`), bloc `**Écrite** :` compris. Un suivi plus ancien que sa
   semence ne la porte pas : l'ajouter avant `## Journal de décisions`.
2. La committer seule, par `git-smart-commit`, type 2, cas « Passation » :
   [Commit rapide de chantier](../../git-smart-commit/references/etape.md). Après « Valider et
   faire la Passation (commit inclus) », à `<L>E0`, le commit part sans nouvelle proposition ;
   après « Valider et commencer la Passation », il se propose à son tour
   ([Ce qui compte comme accord](../../git-smart-commit/references/confirmation.md#ce-qui-compte-comme-accord)).
3. Proposer `/clear`, puis `/implementation-tracker @<suivi>`.

La Passation n'appartient à aucune Étape : jointe au commit d'Étape, la section serait écrite avant
que l'utilisateur ait choisi de passer la main, et resterait en place s'il refuse.

## Règle du journal de décisions

N'y consigner que ce qui **contraint le futur** : choix d'architecture, trade-offs, dépendances
retenues. Pas les micro-choix (nommage, style, refacto local).

**Être concis** : une entrée = 2 à 3 lignes maximum. Une phrase pour la décision, une pour le
pourquoi, une pour l'alternative rejetée. Pas de contexte narratif, pas de rappel du code, pas de
paragraphe. Si une entrée déborde, c'est qu'elle contient plusieurs décisions : les séparer, ou
n'en garder que celle qui contraint réellement la suite.

Format : `- **date** — décision. *Pourquoi* : … *Rejeté* : …`
