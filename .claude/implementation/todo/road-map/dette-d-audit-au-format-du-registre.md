+++
id = "dette-d-audit-au-format-du-registre"
title = "Faire correspondre une dette du rapport d'audit au contrat du Registre de dette"
date = 2026-10-11
source = "Brief du Chantier `refonte-de-l-audit`, qui l'exclut de son périmètre"
+++

## À faire

À la Clôture, les dettes restantes de l'audit entrent au Registre `technical-debt/`, mais une
dette du rapport TOML ne porte pas tout ce que le contrat du Registre exige. Il lui manque un
`id` en slug, un `title` et la section « Pourquoi c'est gênant ». Son `constat` peut citer des
numéros de ligne, que le Registre refuse dans « Constat » ; son `emplacement` n'a pas de champ
d'accueil.

Ce qui correspond déjà : `solution` vers « Pour solder », `severite` (sans `bloquant`, propre à
l'audit), le slug du rapport vers `chantier`, `R<n>` et l'identifiant d'audit vers `reference`,
la date de l'audit de `trouvee` vers `date`.

Une fois les champs alignés, une commande pourrait verser au Registre les dettes restantes sans
recopie.

## Références

- `.claude/implementation/todo/technical-debt/.list/contract.toml` : le contrat du Registre
- `skills/implementation-tracker/references/dette.md` : l'échelle de sévérité et la tenue du
  Registre
- `skills/implementation-tracker/references/cloture.md` : l'alimentation du Registre à la Clôture
- Brief `.claude/implementation/refonte-de-l-audit.brief.md` et son annexe
  `refonte-de-l-audit.brief.annexe.py` : le format d'une dette d'audit
