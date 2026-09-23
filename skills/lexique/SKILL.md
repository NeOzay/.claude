---
name: lexique
description: >
  Tient les lexiques qui fixent le sens des mots : le global (`LEXIQUE.md` à la racine de la
  configuration) et le local d'un projet (`.claude/LEXIQUE.md`), deux tableaux
  `Terme | Définition | Lien`. Fournit la commande `lexique` (init, liste, session). Se déclenche dès
  qu'il s'agit de proposer, ajouter, modifier ou retirer un terme, d'amorcer le lexique local d'un
  projet, ou de savoir si un terme est déjà réservé. N'écrit aucun terme sans l'accord de
  l'utilisateur.
---

# lexique — tenir un lexique

Les règles d'emploi des termes sont dans [`instructions.md`](instructions.md), que `CLAUDE.md`
charge à chaque session : elles font autorité. Ce fichier dit comment tenir un lexique.

**Partage des rôles** : la commande vérifie le format et les réservations. Le modèle propose les
termes et rédige les définitions ; l'utilisateur tranche.

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
lexique init [--projet DIR]    # pose .claude/LEXIQUE.md, en-tête seul
lexique liste [--projet DIR]   # termes global puis local : niveau, terme, lien
lexique session                # le lexique local du projet, pour le hook SessionStart
```

`lexique` est un lien de `bin/` vers `scripts/lexique-cli.py`, résolu par le `PATH`.

Sans `--projet`, le projet est la racine du dépôt git du répertoire courant, ou le répertoire
courant hors dépôt : lancée depuis un sous-répertoire, la commande lit quand même le lexique du
projet, au lieu de conclure à son absence. Dans un monodépôt dont un sous-projet porte son propre
lexique, cette racine n'est pas le sous-projet : passer `--projet <sous-projet>`.

- `init` échoue fermé : **0** lexique posé, son chemin sur stdout ; **1** le fichier existe déjà,
  et rien n'est écrasé.
- `liste` échoue fermé : **0** conforme ; **1** constat — doublon, terme local déjà réservé au
  global — ou lexique malformé, terme sans majuscule compris, un message par ligne sur stderr ;
  **2** erreur d'appel. Un lexique vide ou absent se dit sur stderr, sans changer le code.
- `session` échoue ouvert : **0** quoi qu'il arrive, parce qu'un rappel n'empêche pas une session
  de démarrer. Ses alertes vont dans sa sortie, donc dans le contexte. Le projet est
  `$CLAUDE_PROJECT_DIR` tel quel — le sous-projet ouvert, dans un monodépôt —, ou le répertoire
  courant.

## Proposer, modifier ou retirer un terme

1. `lexique liste` : le terme est-il déjà réservé ? S'il l'est, chercher un autre mot.
2. Choisir le niveau selon la règle du global, dans [`instructions.md`](instructions.md).
3. Présenter la ligne exacte à l'utilisateur et **attendre son accord**. Un accord vaut pour la
   ligne présentée, pas pour la suivante.
4. Écrire la ligne dans le tableau, puis relancer `lexique liste` : **0** attendu.

## Amorcer le lexique local d'un projet

`lexique init` pose `.claude/LEXIQUE.md` à la racine du projet, en-tête compris : le modèle n'écrit
que des lignes, par la procédure ci-dessus. Le hook `SessionStart` verse le lexique au contexte
dès la session suivante ; aucun import n'est à ajouter au projet.
