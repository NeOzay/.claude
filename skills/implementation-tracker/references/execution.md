# Phase 4 — Maintenir le fichier pendant la session

Le fichier est mis à jour **en continu**, sans que l'utilisateur ait à le demander. Relire le
fichier avant chaque écriture. Toujours actualiser `maj` en même temps que le contenu.

Déclencheurs d'écriture :

| Événement | Action |
|---|---|
| Étape passée en `[>]` | Si `execution = "délégué"` et l'étape est substantielle : déléguer à `step-implementer` (voir ci-dessous) |
| Étape terminée | Cocher `[x]`, passer la suivante en `[>]`, **proposer le commit d'étape**, qui pose le tag `<L>E<n>`, puis **mesurer le contexte** (voir ci-dessous) |
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

## Délégation d'étape

Quand `execution = "délégué"` et que l'étape passée en `[>]` est substantielle, elle **est** confiée
au sous-agent `step-implementer` (Sonnet, contexte isolé). Deux bénéfices distincts : les lectures
de fichiers et les diffs restent dans l'agent au lieu de gonfler la session, et l'exécution sort
du modèle de cadrage.

Lui transmettre : chemins **absolus** du suivi et du brief, numéro et intitulé de l'étape, commande
de vérification de l'étape. **Ne rien recopier d'autre** — il lit lui-même le suivi, le plan (via
`plan`) et le brief : [Contrat des sous-agents](contrat.md#contrat-des-sous-agents).

**Ne pas déléguer** :

- une étape qui tient en un ou deux fichiers évidents — l'amorçage d'un agent froid coûte alors
  plus que le travail lui-même ;
- une étape exploratoire, ou qui dépend d'un arbitrage encore ouvert ;
- une étape **sans commande de vérification** — l'exécutant n'aurait aucun moyen de conclure ;
- une étape **déjà entamée** et interrompue par une fin de session : la terminer en direct
  ([Format d'étape et délégabilité](contrat.md#format-détape-et-délégabilité)).

Dans le doute sur un chantier entier, basculer `execution` à `direct` et le noter au journal.

**L'appelant reste responsable au retour** : relire le fichier de suivi avant d'y écrire.

**Premier réflexe, quel que soit le `RÉSULTAT` : regarder le diff.** Le travail a été produit hors
session — l'utilisateur ne l'a pas vu passer, et le commit d'étape de `git-smart-commit` n'analyse
pas le diff. Afficher `git status --short` et `git diff --stat`, les confronter à `FICHIERS` : un
fichier touché qui n'y figure pas est un écart, pas un oubli. C'est le seul regard porté sur ce
diff, et il vient **avant** toute autre action.

| `RÉSULTAT` | Action |
|---|---|
| `TERMINÉ` | Cocher `[x]`, actualiser `maj`, consigner les `DÉCISIONS`, proposer le commit |
| `ÉCART` | Remonter à l'utilisateur sans rien corriger d'office, comme toute divergence plan/réel |
| `DÉRIVE` | S'arrêter, nommer le signal déclenché, en reparler avant de continuer |
| `BLOQUÉ` | Passer l'étape en `[!]` + raison, `statut = "bloqué"` |

**Sur `ÉCART`, `DÉRIVE` ou `BLOQUÉ`, l'agent a laissé derrière lui un travail inachevé.** Trancher
son sort avec l'utilisateur **avant de faire quoi que ce soit d'autre** : garder en l'état, ou
annuler (`git restore`). Pourquoi c'est voulu, et pourquoi cet arbitrage passe avant tout le
reste : [Contrat des sous-agents](contrat.md#contrat-des-sous-agents).

Dans tous les cas : **`À SIGNALER` non vide se remonte à l'utilisateur**, sans rien corriger
d'office ; si l'anomalie relève du périmètre, elle devient une étape.

Ne jamais cocher une étape sur la seule foi du rapport si `VÉRIFICATION` n'a pas de verdict
réel : relancer la commande soi-même.

**Rendre la main après chaque étape déléguée.** Ne pas enchaîner la suivante sans accord : c'est
le point de contrôle de l'utilisateur sur une exécution qu'il n'a pas vue. Rendre la main n'est pas
couper la session : la Passation suit la mesure du contexte (voir ci-dessous).

## Commits de session

Une étape peut se retrouver **à cheval sur deux sessions** — interruption, ou exécution en `direct`.
Le compteur se cale donc sur la **session**, pas sur l'étape. Commits de session et d'étape,
messages et tags : `git-smart-commit`, type 2 —
[Commit rapide de chantier](../../git-smart-commit/references/etape.md).

Propre à ce skill : pour une étape déléguée, ne stager que les fichiers de `FICHIERS` rapportés par
l'agent et le fichier de suivi — rien d'autre.

## Passation

La Passation fait passer un Chantier d'une session à la suivante. Elle se propose à deux moments,
et à eux seuls : après le commit `<L>E0` de la création, toujours
([Création](creation.md)) ; après un commit d'Étape, quand le contexte dépasse le seuil.

**Après chaque commit d'Étape, mesurer le contexte** de la session :

```bash
contexte
```

| Mesure | Action |
|---|---|
| Au-delà de 300 000 tokens | Demander à l'utilisateur s'il veut la Passation |
| 300 000 tokens ou moins | Rien |
| Indisponible (sortie non nulle) | Le dire, avec le message rendu, et ne rien proposer |

Le seuil laisse à l'Étape suivante la marge qui la tient sous 400 000 tokens. Après un commit
d'Étape, aucun travail n'est en cours et le suivi dit exactement où l'on en est : rien d'inachevé
n'est à décrire. Une mesure indisponible ne se devine pas : une Passation proposée à l'aveugle
serait de trop ou trop tard.

**La Passation acceptée**, dans cet ordre :

1. Réécrire la section `## Passation` du suivi, telle que la semence la décrit
   (`gabarit contract suivi`), bloc `**Écrite** :` compris. Un suivi plus ancien que sa
   semence ne la porte pas : l'ajouter avant `## Journal de décisions`.
2. La committer seule, par `git-smart-commit`, type 2, cas « Passation » :
   [Commit rapide de chantier](../../git-smart-commit/references/etape.md).
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
