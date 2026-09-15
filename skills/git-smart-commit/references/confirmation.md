# Accord avant d'écrire dans l'historique

**Jamais de commit, squash, rebase ou amend sans accord explicite de l'utilisateur** (règle
globale, `CLAUDE.md`). Proposer, attendre, exécuter.

## Ce qui est présenté

Tout ce que l'exécution fera, et rien de plus : le message exact, les chemins stagés, et ce qui
s'y ajoute selon la procédure (tag posé, branche supprimée, fichiers déplacés). L'utilisateur
valide ce qu'il a vu — une opération absente de la présentation n'est pas couverte par son accord.

Proposer trois réponses :

1. **Valider** — exécuter tel quel ;
2. **Modifier** — l'utilisateur ajuste, et la proposition modifiée est présentée à nouveau ;
3. **Voir le diff complet** — avant de décider.

## Ce qui compte comme accord

Une réponse de l'utilisateur **à cette proposition-là**. Un accord donné pour un commit ne vaut pas
pour le suivant, même dans la même session et au sein de la même procédure.

> *Mode de défaillance* — un accord étendu en silence au commit suivant fait entrer dans
> l'historique un contenu que personne n'a regardé. C'est irréversible une fois poussé, et rien ne
> signale qu'il manquait un regard.
