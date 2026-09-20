# Branche de chantier

Un chantier vit sur une branche nommée **exactement `<slug>`**, créée depuis la branche principale,
notée `base` dans le frontmatter du suivi. Tous les commits du chantier s'y font.

- **Livré** → la branche est aplatie en **un seul commit sur `base`**, puis supprimée.
- **Abandonné** → la branche n'est **jamais** aplatie dans `base`.

> *Mode de défaillance* — le nom est la seule chose qui relie la branche au suivi : le script de
> clôture la retrouve par le slug et refuse de s'exécuter depuis une autre. Une branche renommée
> « pour faire plus clair » rend la clôture impossible sans que rien ne l'ait annoncé.
