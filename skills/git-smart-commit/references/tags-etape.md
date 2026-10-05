# Tags d'étape

Chaque chantier porte une **lettre**, chaque étape livrée un tag `<lettre>E<n>` : `AE0`, `AE1`,
`AE2`…, et chaque Retouche un tag `<lettre>E<n>.<k>` : `AE1.1`, `AE1.2`… Ils rendent les étapes et
leurs Retouches adressables en plage git.

## Lettre

Attribuée à la création du chantier, avant son premier commit, et notée dans `lettre` du
frontmatter du suivi :

```bash
commit-chantier lettre
```

Le script rend la première lettre de A à Z qu'aucun tag d'étape n'occupe, et refuse quand les 26
sont prises. Une lettre se libère quand les tags de son chantier sont supprimés.

## Tags

| Tag | Posé sur |
|---|---|
| `<L>E0` | le premier commit de la branche : état initial (brief, plan, suivi) |
| `<L>E<n>` | le commit qui clôt l'étape n |
| `<L>E<n>.<k>` | la k-ième Retouche de l'étape n, prise avant que l'étape n+1 ne commence |

Le tag d'une Retouche se demande au script, qui refuse si `<L>E<n>` manque ou si `<L>E<n+1>`
existe déjà :

```bash
commit-chantier retouche <L> <n>
```

Les commits de session et de Passation n'en portent pas. Un tag n'est **jamais déplacé** : pas de
`git tag -f`. Un tag déjà présent arrête la procédure, et l'utilisateur tranche.

## Plages

Une plage git **exclut son début** :

| Plage | Contenu |
|---|---|
| `AE0..AE3` | les étapes 1 à 3 |
| `AE2..AE3` | toute l'étape 3, commits de session compris, et les Retouches de l'étape 2 |
| `AE2.<dernier k>..AE3` | l'étape 3 seule — `AE2..AE3` quand l'étape 2 n'a pas de Retouche |
| `AE2..AE2.<dernier k>` | les Retouches de l'étape 2 |
| `AE1..` | tout ce qui suit l'étape 1 |
| `AE1^..AE3` | les étapes 1 à 3, commit de l'étape 1 inclus |

## Suppression

Les tags d'un chantier, d'étape comme de Retouche, sont supprimés **avec sa branche** : à
l'aplatissement, par le script de clôture, et à l'abandon quand la branche est supprimée. Une
branche conservée garde ses tags, et sa lettre reste occupée.

> *Mode de défaillance* — un tag qui survit à sa branche garde en vie des commits que plus rien ne
> référence, et bloque sa lettre : le chantier suivant qui la recevrait se heurterait à un `AE0`
> déjà pris.
