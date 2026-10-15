+++
id = "solder-sept-dettes-relues-le-2026-10-14"
title = "Solder sept dettes relues le 2026-10-14 : deux de documentation, quatre correctifs, un manque de tests"
date = 2026-10-14
source = "relecture de dettes du 2026-10-14, chacune revérifiée dans le dépôt ce jour-là"
+++

## À faire

Sept dettes relues, toujours vraies, chacune bornée et peu coûteuse. Chaque point dit ce qui a été
décidé à la relecture quand cela s'écarte du « Pour solder » de la dette.

**Documentation**

1. `lexique-depend-du-path-de-la-session` (note) — écrire dans `.claude/CLAUDE.md`, et non dans
   `skills/lexique/SKILL.md` comme le dit la dette, que les commandes de `bin/` s'appellent par
   leur nom et supposent une session lancée d'un shell dont le `PATH` porte `bin/` ; dire ce qui
   manque sans lui : le lexique versé par le mod, et Neovim. La règle vaut pour tous les
   consommateurs de `bin/`.
2. `conversation-reprise-sans-lexique-local-jusqua-compaction` (avertissement) — écrire dans
   `skills/lexique/SKILL.md`, « Ce que reçoit la session », qu'une conversation reprise garde le
   lexique local de son début jusqu'à sa compaction, et le remède : `/compact` ou une nouvelle
   conversation. Corriger les deux formulations qui laissent croire à une recomposition :
   `shadow-skills/claude-code-mods/SKILL.md` (« survit à `/clear`, à `/compact` et à
   `--continue` ») et le commentaire de `prompt.compose` dans `skills/lexique/hooks/register.ts`
   (« survit à la reprise »). La recherche d'un événement de reprise n'est pas de ce chantier.

**Correctifs**

3. `controle-7-lit-shadow-skills-comme-skills` (avertissement) — garde arrière `(?<![\w/.-])` dans
   `CHEMIN_SKILL` de `scripts/check_pipeline.py`. Tests : un lien vers `shadow-skills/<nom>/` passe,
   et le cas homonyme (`skills/x` et `shadow-skills/x` existent tous deux) ne valide plus le mauvais
   fichier. Rétablir le lien vers `claude-code-mods` dans `skills/mod-commun/SKILL.md`. À établir :
   si le contrôle 8 juge l'existence d'un `shadow-skills/…` cité depuis `skills/`, que le contrôle 7
   ne verra plus.
4. `cherche-par-sous-chaine` (note) — `shadow-skill cherche` compare par frontière de mot, avec le
   test « skill » contre « This skill ». Le sous-agent chercheur est une entrée à part.
5. `lexique-home-versionne-par-git` (note) — `racine_projet` retombe sur le répertoire courant quand
   la racine git porte le lexique global, docstring corrigée, test sur un HOME git simulé.
   Compléter d'abord le Constat de la dette : `chemin`, `termes`, `definition` et `definitions`,
   appelées par Neovim, ont le même défaut que `liste` et `init`.
6. `migrate-valeur-multilignes-casse-une-ligne-par-changement` (note) — une seule fonction de
   libellé dans `listdir/store.py`, pour les champs comme pour les sections : première ligne suivie
   de « … » quand la valeur en a plusieurs, valeur d'une ligne inchangée. Le défaut vient aussi
   d'un `text` multi-lignes, pas seulement d'une `command`. Tests : une section multi-lignes donne
   une ligne de `migrate`, une valeur d'une ligne reste telle quelle.

**Tests**

7. `reseed-sans-test-cli` (avertissement) — les quatre cas de bout en bout de la dette dans
   `test_entree_cli.py`, plus un cinquième : une liste sans `origin.def` ni `--def`/`--from`,
   refus qui n'existe que dans la commande.

## Références

- Dettes, dans `.claude/implementation/todo/technical-debt/` : les sept `id` ci-dessus
- `OUTILLAGE.md` : lancer `check_pipeline.py` et les tests
- `.claude/CLAUDE.md`, « Neovim, visionneuse de certains skills » : les consommateurs de `bin/`
  côté Neovim
- `skills/lexique/scripts/lexique.py` : `racine_projet`, `_est_le_global`
- `skills/list-dir/scripts/tests/test_reseed.py` : les montages réutilisables (`semer`, `SEMENCE`)
- Entrées voisines, relues le même jour : `modes-de-defaillance-dans-la-prose`,
  `sous-agent-chercheur-de-shadow-skills`

## Fait le

**2026-10-15, chantier `solder-sept-dettes`** — les sept dettes sont soldées comme l'entrée l'a
décidé, et chacune a sa preuve dans `technical-debt-solde/` : deux par documentation
(`.claude/CLAUDE.md`, `skills/lexique/SKILL.md`), quatre par correctif testé, une par cinq tests
de `reseed` à la ligne de commande. Le retrait du cache du lexique, écarté du chantier, est en
road-map : `lexique-relu-a-chaque-composition`.

Archive du chantier : `.claude/implementation/done/2026-10-15-solder-sept-dettes.md`

Établi par : l'audit de clôture `51fb1a8`, FAVORABLE ;
`grep -l "chantier .solder-sept-dettes." .claude/implementation/todo/technical-debt-solde/*.md | wc -l`
→ `7`.
