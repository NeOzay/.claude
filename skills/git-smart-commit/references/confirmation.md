# Accord avant d'écrire dans l'historique

**Jamais de commit, squash, rebase ou amend sans accord explicite de l'utilisateur** (règle
globale, `CLAUDE.md`). Proposer, attendre, exécuter.

## Ce qui est présenté

Le message, le tag s'il y en a un, et les exclusions s'il y en a : les fichiers en attente qui ne
partent pas ([`staging.md`](staging.md)). Un aplatissement y ajoute, sur une ligne, ses gestes
irréversibles : branche et tags supprimés. Rien d'autre : les fichiers et le diff, l'utilisateur les
voit dans son éditeur
([Messages à l'utilisateur](../../implementation-tracker/references/contrat.md#messages-à-lutilisateur)).

L'accord couvre toutes les modifications en attente, sauf les exclusions présentées, et les gestes
présentés. Une opération absente de la présentation n'est pas couverte par l'accord.

Un commit mécanique — état initial, session, Passation ([`etape.md`](etape.md)) — se propose sans
son titre : son message est prédéterminé, et l'afficher n'apprend rien. L'accord se demande quand
même, hors l'exception ci-dessous.

Proposer deux réponses :

1. **Valider**, libellé ajusté au contexte — « Committer l'état initial », « Réaliser la
   Clôture » ;
2. **Autre chose** — l'utilisateur dit ce qu'il veut changer, et la proposition modifiée est
   présentée à nouveau.

Un Chantier a ses propres choix pour l'état initial, l'Étape et la Retouche :
[`etape.md`](etape.md), point 4.

## Ce qui compte comme accord

Une réponse de l'utilisateur **à cette proposition-là**. Un accord donné pour un commit ne vaut pas
pour le suivant, même dans la même session et au sein de la même procédure.

Une seule exception : **Valider et faire la Passation (commit inclus)**, au commit d'état initial,
couvre aussi le commit de Passation qui le suit. Rien n'est encore implémenté : la section ne
transmet que ce que la création a établi, dans la session où l'utilisateur vient d'arbitrer le Brief
et le Plan, et la branche ne rejoint la Base qu'aplatie, après audit.

> *Mode de défaillance* — un accord étendu en silence au commit suivant fait entrer dans
> l'historique un contenu que personne n'a regardé. C'est irréversible une fois poussé, et rien ne
> signale qu'il manquait un regard.
