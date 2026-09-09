+++
id = "tableaux-toml-aplatis-a-l-ecriture"
title = "Décider si dump_value doit enrouler les tableaux, qu'il aplatit aujourd'hui sur une ligne"
date = 2026-09-08
source = "conception du contrat de fiche d'analyse du projet claude-translator, qui bute dessus"
+++

## À faire

`dump_value` (`skills/list-dir/scripts/listdir/items.py`) sérialise tout tableau sur **une seule
ligne**, sans seuil ni exception :

```python
return "[" + ", ".join(dump_value(v, key) for v in seq) + "]"
```

TOML autorise pourtant les tableaux multilignes, et la lecture les accepte : un élément écrit à la
main sur plusieurs lignes passe `validate --filled`, et `show` le rend verbatim puisqu'il concatène
le fichier. C'est **l'écriture seule** qui aplatit — donc `new`, `migrate`, `move`, `derive`.

Deux conséquences, la seconde plus gênante que la première :

- un champ `list` de quelques entrées un peu longues devient une ligne de plusieurs centaines de
  caractères, difficile à relire et à corriger à la main ;
- **un simple ajout de champ au contrat reformate tous les éléments d'un coup.** L'auteur qui avait
  soigné son tableau multiligne le retrouve aplati après un `migrate` qui ne portait pas sur ce
  champ, et le diff git mélange la vraie migration et un reformatage massif.

La question à trancher : le formatage du frontmatter fait-il partie de ce que `list-dir` garantit,
ou l'élément est-il libre dans sa forme tant qu'il est conforme ?

- **enrouler** → `dump_value` passe à la ligne au-delà d'une longueur donnée, une entrée par ligne,
  virgule finale. Une dizaine de lignes, mais ça fixe un style d'écriture pour tout le monde et ça
  reformate l'existant au premier `migrate` ;
- **ne rien changer** → alors le dire quelque part, parce que la contrainte ne se devine pas depuis
  le contrat : elle impose que les entrées d'un champ `list` restent des **libellés courts**, et
  que toute donnée en phrases aille en section. C'est une règle de conception de contrat, pas un
  détail de sérialisation.

Contrainte connexe à ne pas perdre si le sujet se rouvre : `dump_value` refuse les caractères de
contrôle (« aucune écriture TOML sur une ligne ne le porte »). Une entrée contenant un retour à la
ligne — écrite en chaîne multiligne `"""…"""`, que la lecture accepte — lève une `SerialiseError` à
la première réécriture. La limite « entrées courtes » est donc double : lisibilité, et sérialisation.

## Références

- le sérialiseur : `skills/list-dir/scripts/listdir/items.py`, `dump_value` et `dump_front`
- le type concerné : `skills/list-dir/scripts/listdir/types.py`, `FieldType` — `list` est le seul
  type dont la valeur puisse être longue
- reproduction : créer une liste avec un champ `list`, y écrire un tableau sur trois lignes,
  `validate --filled` passe ; ajouter un champ au contrat, `migrate`, le tableau est sur une ligne
- ce qui a fait remonter le sujet : le contrat des fiches d'analyse de `claude-translator`
  (`docs/ANALYSE.md`, décision D19), où six données de type liste ont été portées du corps vers le
  frontmatter et où la longueur des entrées devient un critère de conception

## Fait le

**2026-09-09, chantier `tableaux-toml-aplatis-a-l-ecriture`** — l'écriture ne resérialise plus le
front matter, elle y reprojette les champs modifiés via tomlkit : un tableau mis en forme à la
main, une chaîne multiligne et un commentaire survivent à une réécriture qui ne portait pas sur
eux. La question posée par l'entrée est tranchée dans le sens « enrouler », mais sans imposer de
style : rien n'est reformaté, c'est ce qui a été écrit qui est conservé.

Archive du chantier : `.claude/implementation/done/2026-09-09-tableaux-toml-aplatis-a-l-ecriture.md`

Établi par : sur une liste neuve portant un tableau écrit sur trois lignes avec un commentaire
au-dessus, l'ajout de deux champs au contrat puis `list-dir migrate` →
`git diff --stat` = `1 file changed, 2 insertions(+)`, tableau et commentaire intacts.
