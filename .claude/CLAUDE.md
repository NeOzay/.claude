# Ce dépôt : la configuration globale de Claude Code

Ce dépôt est `~/.claude`, la configuration globale de Claude Code : ses skills, agents, règles,
hooks et réglages valent pour tous les projets de l'utilisateur.

Deux `CLAUDE.md` y coexistent. Celui de la racine est la mémoire de l'utilisateur, chargée dans
chaque session, quel que soit le projet. Celui-ci n'est chargé que dans une session ouverte sur
ce dépôt. Une règle qui ne vaut que pour travailler sur ce dépôt s'écrit ici, jamais à la racine.

## Conventions

Le Shadow-skill [`skill-convention`](../shadow-skills/skill-convention/SKILL.md) énonce les
conventions de ce dépôt : prose d'une skill, code Python, documents posés depuis une Semence,
registres, commandes fournies à un agent. Le charger par `shadow-skill charge skill-convention`
avant d'écrire ou de relire un fichier de skill.

## Outillage

[`OUTILLAGE.md`](../OUTILLAGE.md) dit de quoi le dépôt dépend et comment lancer chaque outil :
linters, tests, comparaison à la base, exposition d'un exécutable dans `bin/`. Le lire avant de
lancer l'un de ces outils.

Les commandes de `bin/` s'appellent par leur nom : elles supposent une session lancée depuis un
shell dont le `PATH` porte `bin/`. Une session ouverte autrement, depuis un lanceur graphique ou
un IDE, perd le lexique local que verse le mod `lexique`, et l'échec ne se lit que sur la ligne
d'état. Neovim, lancé de même, ne trouve plus les commandes qu'il appelle. La ligne à ajouter au
profil du shell : [Ce dont le dépôt dépend](../OUTILLAGE.md#ce-dont-le-dépôt-dépend).

## Le modèle d'une session

Ce dépôt versionne `settings.json`, où `/model` enregistre le modèle choisi comme défaut : un
`/model` en défaut salit l'arbre, et un Chantier ne se crée ni ne se reprend sur un arbre sale.
Dans une session ouverte ici, `/model` se fait donc **pour la session seulement**. L'utilisateur
règle le modèle de démarrage dans `.claude/settings.local.json`, ignoré par git, qui l'emporte sur
`settings.json` ; un agent n'écrit jamais ce fichier, rien ne change le modèle à la place de
l'utilisateur. Le `settings.local.json` de la racine, versionné, ne sert pas à cela.

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
