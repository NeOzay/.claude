+++
id = "reprendre-pipeline-v2-au-navigateur"
title = "Reprendre l'étude pipeline-v2 quand les mods dessineront au navigateur"
date = 2026-10-13
source = "Clôture du Chantier pipeline-v2, conclusion mitigée"
+++

## À faire

Reprendre l'exploration de la v2 du pipeline des Chantiers portée par des mods, arrêtée le
2026-10-13 sur un verdict mitigé : panneau et bande s'affichent dans Desktop et au terminal, mais
claude.ai/code par Remote Control ne dessine rien, et c'est là que l'utilisateur travaille.

Déclencheur : une version de Claude Code dont les types ajoutent une surface à `Elements`, ou dont
la documentation (« Where mods run ») fait dessiner Remote Control au navigateur. Vérifier par
`python3 -I pipeline-v2/api/inventaire.py <types> --compare pipeline-v2/api/2.1.296.txt`.

Reprise : relancer `proto-sonde` au navigateur, puis écrire la spécification (Suivi, Étapes,
commits, suivi de l'API) à partir des douze constats.

## Références

- `pipeline-v2/conclusion.md`, `pipeline-v2/constats.md`, prototypes `pipeline-v2/proto-*/`
- `pipeline-v2/api/` : inventaire de l'API 2.1.296 et sa commande
- Chantier archivé : `.claude/implementation/done/2026-10-13-pipeline-v2.md`
- Shadow-skill `claude-code-mods`, sections « Où un mod dessine » et suivantes
