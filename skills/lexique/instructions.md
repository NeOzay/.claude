# Lexique — le sens des mots

Un terme défini dans un lexique n'a qu'un sens : sa définition. Deux lexiques s'appliquent, chargés
à chaque session à la suite de ce fichier :

- **global** — `LEXIQUE.md` à la racine de la configuration : les concepts des skills globales,
  faites pour servir dans n'importe quel projet ;
- **local** — `.claude/LEXIQUE.md` à la racine du projet, versé au contexte au démarrage de la
  session.

## Règles

- **Un terme s'écrit avec une majuscule initiale** — Suivi, Étape, Signal de dérive — quand il est
  employé dans son sens défini. En minuscule, le mot garde son sens courant. Sans cette marque, un
  mot courant réservé ne pourrait plus servir dans son sens ordinaire, et le lecteur ne saurait
  pas lequel des deux sens est en jeu.
- **L'agent n'emploie un terme avec sa majuscule que dans sa définition.** Pour un autre sens, il
  prend un autre mot, ou la minuscule s'il s'agit du sens courant. Un terme employé dans deux sens
  fait lire à chacun ce que l'autre n'a pas écrit, et le malentendu ne se voit qu'au résultat.
- **Quand l'utilisateur emploie un terme avec sa majuscule hors de sa définition, l'agent le lui
  signale** : le terme, sa définition, le sens que la phrase semble lui donner. Il ne reformule
  pas d'office — choisir le mot revient à l'utilisateur.
- **Un terme n'est défini qu'une fois, tous niveaux confondus.** Un terme du global est réservé :
  le local ne le redéfinit pas. Deux définitions d'un même terme lui redonnent deux sens.
- **Aucun terme n'entre, ne change ni ne sort d'un lexique sans l'accord explicite de
  l'utilisateur.** L'agent propose la ligne, selon la procédure de la skill
  [lexique](SKILL.md). Un terme écrit sans accord fixe un sens que l'utilisateur n'a pas choisi.
- **Le global reste le plus petit possible** : n'y entre qu'un concept qu'une skill globale
  emploie, défini en une phrase. Il se charge à chaque session, dans chaque projet.

Termes réservés et conflits : `lexique liste`.
