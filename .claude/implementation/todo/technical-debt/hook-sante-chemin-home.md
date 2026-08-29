+++
id = "hook-sante-chemin-home"
title = "Le hook SessionStart porte la dernière constante ancrée sur le HOME, sans être déclarée comme exception"
date = 2026-08-29
source = "Identifié par `resolution-chemin-skill`, R1 du rapport d'audit."
+++

## Constat

`settings.json` déclare le hook `SessionStart` par
`python3 $HOME/.claude/scripts/sante_skills.py`. C'est la seule constante ancrée sur le `HOME`
qui subsiste après le solde de `chemin-skill-code-en-dur`. Elle est probablement inévitable —
c'est l'amorçage : à cet instant, ni le `PATH` ni `bin/` ne sont encore vérifiés, et rien ne peut
se résoudre — mais aucun contrôle ne la garde et aucun texte ne la déclare comme l'exception
assumée. La fiche `technical-debt-solde/chemin-skill-code-en-dur.md` énumère ce que le solde ne
couvre pas et ne la mentionne pas.

Établi par : `grep -n 'sante_skills' settings.json` → la ligne du hook porte `$HOME/.claude/`.

## Pourquoi c'est gênant

Une exception non écrite ne se distingue pas d'un oubli. Le prochain lecteur qui appliquera la
règle « aucun chemin ancré sur le `HOME` » trouvera cette ligne et ne saura pas si elle est
tolérée ou si elle a échappé à la conversion — et s'il la « corrige », le hook cesse de tourner
sans qu'aucune commande n'échoue, puisque son absence est justement silencieuse.

## Pour solder

Écrire l'exception là où la règle est posée (`contrat.md#dépendances`), en disant pourquoi
l'amorçage ne peut pas se résoudre lui-même, et l'ajouter à la liste « ce que le solde ne couvre
pas » de la fiche `chemin-skill-code-en-dur`. Si un contrôle est ajouté, il doit tolérer cette
ligne nommément plutôt que la forme en général.
