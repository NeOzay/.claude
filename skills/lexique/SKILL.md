---
name: lexique
description: >
  Tient les lexiques qui fixent le sens des mots : le global (`LEXIQUE.md` à la racine de la
  configuration) et le local d'un projet (`.claude/LEXIQUE.md`), deux tableaux
  `Terme | Définition | Lien`. Fournit la commande `lexique` (init, liste, session, sous-agent, chemin,
  termes, definition, definitions). Se déclenche dès qu'il s'agit de proposer, ajouter, modifier ou retirer un terme,
  d'amorcer le lexique local d'un projet, ou de savoir si un terme est déjà réservé. N'écrit aucun
  terme sans l'accord de l'utilisateur.
---

# lexique — tenir un lexique

Les règles d'emploi des termes sont dans [`instructions.md`](instructions.md), que `CLAUDE.md`
charge à chaque session : elles font autorité. Ce fichier dit comment tenir un lexique.

**Partage des rôles** : la commande vérifie le format et les réservations. Le modèle propose les
termes et rédige les définitions ; l'utilisateur tranche.

`chemin`, `termes`, `definition` et `definitions` alimentent la commande `:Lexique` de la
configuration Neovim (`~/.config/nvim/lua/lexique.lua`) ; elles ne servent à rien d'autre.

## Format

Un lexique est un fichier Markdown qui porte **un seul tableau**, avec de la prose autour si
besoin ; un tableau dans un bloc de code est un exemple, et ne compte pas :

```markdown
| Terme | Définition | Lien |
|---|---|---|
| <terme> | <une phrase> | [<élément>](<chemin relatif>) |
```

- **Terme** : un mot, un mot inventé, un mot-valise ou une expression de plusieurs mots, avec une
  majuscule initiale — la règle et son motif sont dans [`instructions.md`](instructions.md). Deux
  termes qui ne diffèrent que par la casse ou les espaces sont le même terme : sinon, deux
  graphies d'un même mot porteraient deux définitions.
- **Définition** : une phrase. Au-delà, c'est une référence, et elle va dans l'élément lié.
- **Lien** : un lien Markdown, relatif au fichier du lexique, vers l'élément qui porte le concept
  — une skill, une référence, une section. Un terme dont on ne sait pas où il vit n'a pas de
  définition vérifiable.

## La commande

```bash
lexique init [--projet DIR]                # pose .claude/LEXIQUE.md, en-tête seul
lexique liste [--projet DIR]               # termes global puis local : niveau, terme, lien
lexique session                            # le lexique local du projet, pour le mod lexique
lexique sous-agent TYPE                    # le lexique d'un sous-agent, pour le mod lexique
lexique chemin [--global] [--projet DIR]   # le chemin du lexique à ouvrir, pour Neovim
lexique termes [--projet DIR]              # un terme par ligne, global puis local, pour Neovim
lexique definition TERME [--projet DIR]    # la définition d'un terme, pour Neovim
lexique definitions [--projet DIR]         # chaque terme et sa définition, pour Neovim
```

`lexique` est un lien de `bin/` vers `scripts/lexique-cli.py`, résolu par le `PATH`.

Sans `--projet`, le projet est la racine du dépôt git du répertoire courant, ou le répertoire
courant hors dépôt : lancée depuis un sous-répertoire, la commande lit quand même le lexique du
projet, au lieu de conclure à son absence. Dans un monodépôt dont un sous-projet porte son propre
lexique, cette racine n'est pas le sous-projet : passer `--projet <sous-projet>`. Quand la racine
git est celle qui porte le lexique global — un HOME versionné par git —, le projet est le répertoire
courant, comme hors dépôt : le global ne se lit pas comme local.

- `init` échoue fermé : **0** lexique posé, son chemin sur stdout ; **1** le fichier existe déjà,
  et rien n'est écrasé.
- `liste` échoue fermé : **0** conforme ; **1** constat — doublon, terme local déjà réservé au
  global — ou lexique malformé, terme sans majuscule compris, un message par ligne sur stderr ;
  **2** erreur d'appel. Un lexique vide ou absent se dit sur stderr, sans changer le code.
- `session` échoue ouvert : **0** quoi qu'il arrive, parce qu'un rappel n'empêche pas une session
  de démarrer. Ses alertes vont dans sa sortie, donc dans le contexte. Le projet est
  `$CLAUDE_PROJECT_DIR` tel quel — le sous-projet ouvert, dans un monodépôt —, ou le répertoire
  courant.
- `sous-agent` échoue ouvert, comme `session` : **0** quoi qu'il arrive, une erreur se dit sur
  stderr — sauf l'argument manquant, **2**, erreur d'appel. Il prend le type de l'agent en argument,
  et rend sur stdout ce que l'agent reçoit, en texte brut comme `session` — ou rien. Le projet se
  résout comme pour `session`.
- `chemin` échoue fermé : **0** le fichier existe, son chemin sur stdout ; **1** aucun global à
  cet endroit, ou local absent, ou local égal au global — pourquoi, sur stderr.
- `termes` échoue fermé : **0** un terme par ligne, global puis local, même sur un lexique non
  conforme — ses constats et ses lignes fautives sortent sur stderr sans changer le code ; **1**
  un niveau illisible (pas en UTF-8, ou inaccessible), l'autre niveau servi quand même.
- `definition TERME` échoue fermé : **0** au moins une correspondance,
  `niveau\tterme\tdéfinition` par ligne, à la casse et aux espaces près (« Signal de dérive » =
  « signal  de dérive ») ; **1** aucune. Constats, fautes et erreurs de lecture vont sur stderr
  dans les deux cas.
- `definitions` échoue fermé, comme `termes` : **0** `niveau\tterme\tdéfinition` par ligne,
  global puis local, même sur un lexique non conforme ; **1** un niveau illisible, l'autre servi
  quand même.

## Proposer, modifier ou retirer un terme

1. `lexique liste` : le terme est-il déjà réservé ? S'il l'est, chercher un autre mot.
2. Choisir le niveau selon la règle du global, dans [`instructions.md`](instructions.md).
3. Présenter la ligne exacte à l'utilisateur et **attendre son accord**. Un accord vaut pour la
   ligne présentée, pas pour la suivante.
4. Écrire la ligne dans le tableau, puis relancer `lexique liste` : **0** attendu.

## Ce que reçoit la session

La session principale reçoit le lexique local par le mod
[`lexique`](hooks/register.ts) : il lance `lexique session` une fois, et ajoute la
sortie au prompt système, en section de session, à chaque composition. Un hook `SessionStart`
plafonne son contexte à 10 000 caractères et n'en garde qu'un aperçu de 2 Ko ; une section du
prompt système n'a pas ce plafond. Sans le mod chargé, la session ne reçoit aucun lexique local, et
aucun hook n'est déclaré dans `settings.json` pour le suppléer.

Le lexique local se lit une fois par processus : le mod garde le texte rendu par la commande, et
ni `/clear` ni `/compact` ne relisent `.claude/LEXIQUE.md`. Une conversation reprise, par
`--resume` ou `--continue`, réutilise en outre le prompt système qu'elle a enregistré jusqu'à sa
prochaine compaction : elle garde le lexique local de son début, ou son absence. Un terme ajouté
ou retiré depuis ne l'atteint pas, et rien ne le signale. Pour avoir le lexique à jour à coup sûr :
relancer Claude Code, dans une nouvelle conversation.

Deux autres voies ne conviennent pas :

- un bloc de `prompt.context` arrive à tous les sous-agents, y compris à ceux que `omitClaudeMd`
  isole ;
- une ligne ajoutée par `$.session.append` au démarrage se perd à `/clear` et à la compaction, et
  se duplique à chaque reprise de la session.

## Ce que reçoit un sous-agent

Un sous-agent ne reçoit pas la section que le mod ajoute au prompt système de la session. Le
mod [`lexique`](hooks/register.ts) lance `lexique sous-agent` à son lancement et
préfixe le `prompt` du sous-agent de ce qu'il rend. La commande lit le **fichier de l'agent** —
d'abord dans `.claude/agents/` du projet, puis dans `agents/` de la configuration globale — et
décide d'après son frontmatter :

| Frontmatter de l'agent | Ce qu'il reçoit par le mod |
|---|---|
| ni `omitClaudeMd` ni `injectLexique` | le lexique local ; le global et les instructions arrivent déjà par `CLAUDE.md` |
| `omitClaudeMd: true` | rien : l'isolation est voulue |
| `omitClaudeMd: true` et `injectLexique: true` | les instructions, le lexique global et le lexique local |

`injectLexique` se lit comme `omitClaudeMd`, comme Claude Code lit le YAML : `true`, `True`, `TRUE`
ou `"true"` vaut oui, et un commentaire de fin de ligne est ignoré. L'auteur de l'agent pose ce
champ à la main ; ni le mod ni ses scripts n'écrivent dans un fichier d'agent. Un agent sans fichier
(`Explore`, `Plan`, general-purpose, agent de plugin) ne reçoit rien.

**Charger le mod** : un mod n'est pas un hook de `settings.json`. Il vit à la racine de ce skill,
dans `.claude-plugin/` et `hooks/`, et chaque session le charge seule : aucun réglage ne le nomme.
Il lance `lexique session` et `lexique sous-agent` par `$.commande`, que le mod
[mod-commun](../mod-commun/SKILL.md) ajoute au moteur, et dont il dépend.
Il passe par le `prompt` et non par un hook `SubagentStart` : un hook plafonne son contexte à
10 000 caractères, au-delà desquels il en garde un aperçu de 2 Ko.

## Amorcer le lexique local d'un projet

`lexique init` pose `.claude/LEXIQUE.md` à la racine du projet, en-tête compris : le modèle n'écrit
que des lignes, par la procédure ci-dessus. Le mod verse le lexique à la
session dès la suivante, et à chaque sous-agent concerné ; aucun import n'est à ajouter au projet.
