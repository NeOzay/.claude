+++
id = "controle-completude-revue-sans-code-sortie"
title = "Le contrôle de complétude d'une revue signale par `echo`, sans code de sortie"
date = 2026-08-23
source = "chantier `format-registres`, R15 des audits de clôture"
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

`skills/debt-review/SKILL.md`, aux deux endroits où le comptage des fiches est confronté au
registre, se termine par `|| echo "ÉCHEC : autant de fiches que d'entrées attendu"`. Le message
part sur stdout et la commande rend **0**.

## Pourquoi c'est gênant

C'est exactement le mode de défaillance que le chantier a passé son temps à supprimer ailleurs :
`hooks/intent-brief-gate.sh` sortait 0 sur `jq` absent, et la règle « échec fermé » a été écrite
pour ça. Ici le contrôle qui garantit qu'aucune entrée n'a été oubliée — le seul, puisque `merge` ne
sait pas voir une fiche disparue — ne peut être remarqué que par un lecteur attentif.

Le reste du dispositif est cohérent : `validate`, `merge` et `move` sortent non nul en nommant la
cause. Ce contrôle-ci est le dernier à ne pas le faire, et c'est le plus important des trois.

## Pour solder

Remplacer l'`echo` par un échec fermé, sur le modèle du garde-fou de pipeline :

    test "$(… list "$R" | wc -l)" -eq "$(… list "$T/technical-debt" | wc -l)" \
      || { echo "ÉCHEC : autant de fiches que d'entrées attendu"; false; }

Vérifier ensuite que le `false` remonte bien — une revue à blanc avec une fiche retirée doit rendre
un code ≠ 0.

## Assumé

<OPTIONNEL>
