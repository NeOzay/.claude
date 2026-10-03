# Ce dépôt : la configuration globale de Claude Code

Ce dépôt est `~/.claude`, la configuration globale de Claude Code : ses skills, agents, règles,
hooks et réglages valent pour tous les projets de l'utilisateur.

Deux `CLAUDE.md` y coexistent. Celui de la racine est la mémoire de l'utilisateur, chargée dans
chaque session, quel que soit le projet. Celui-ci n'est chargé que dans une session ouverte sur
ce dépôt. Une règle qui ne vaut que pour travailler sur ce dépôt s'écrit ici, jamais à la racine.

## Conventions

Le skill [`skill-convention`](../skills/skill-convention/SKILL.md) énonce les conventions de ce
dépôt : prose d'une skill, code Python, documents posés depuis une Semence, registres, commandes
fournies à un agent. Le charger avant d'écrire ou de relire un fichier de skill.

## Outillage

[`OUTILLAGE.md`](../OUTILLAGE.md) dit de quoi le dépôt dépend et comment lancer chaque outil :
linters, tests, comparaison à la base, exposition d'un exécutable dans `bin/`. Le lire avant de
lancer l'un de ces outils.

## Neovim, visionneuse de certains skills

Neovim sert de visionneuse à certains skills : on y recherche, liste et affiche leurs données.
Le skill les fournit par sa commande de `bin/` ; la configuration Neovim, dans `~/.config/nvim/`,
hors de ce dépôt, l'appelle par le `PATH` et affiche ce qu'elle rend.

Ce qu'elle appelle forme une interface : la modifier peut casser Neovim sans qu'aucun test de ce
dépôt ne le voie. Avant de changer une sortie ou un format de fichier qu'un skill expose,
chercher son consommateur dans `~/.config/nvim/`.

| Skill | Côté Neovim | Ce qu'il en consomme |
|---|---|---|
| `lexique` | `:Lexique`, `lua/lexique.lua` | les sous-commandes `chemin`, `termes`, `definition`, `definitions` |
| `list-dir` | plugin `listdir`, `plugins/listdir/` | la sortie de `list-dir list`, et `.list/contract.toml`, lu directement |
