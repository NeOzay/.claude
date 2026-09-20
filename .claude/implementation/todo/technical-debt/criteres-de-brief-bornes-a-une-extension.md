+++
id = "criteres-de-brief-bornes-a-une-extension"
title = "Les critères d'un brief de renommage bornaient leurs greps à un répertoire et deux extensions"
date = 2026-09-20
source = "chantier `deux-sens-de-gabarit`, audit de clôture R1 et R3 (`ffc2297`)"
reviewed = "<OPTIONNEL>"
category = "<OPTIONNEL>"
+++

## Constat

Le brief de `deux-sens-de-gabarit` portait deux critères de réussite en forme de grep :
`grep -rni 'template' skills/list-dir ...` et `grep -rn 'gabarit' skills/list-dir ...`, tous deux
restreints à `--include=*.md --include=*.py`. Les deux passaient quand l'audit a trouvé, dans des
fichiers qu'ils n'atteignaient pas :

- trois `review.toml` — des `.toml`, donc hors des extensions retenues — dont le commentaire
  employait encore « gabarit » au sens du moule et citait le chemin mort `templates/`, texte
  imprimé par `list-dir contract --def technical-debt --patron review`, que `debt-review` exécute
  à chaque revue ;
- sept entrées vivantes de `.claude/implementation/todo/technical-debt/` — hors du répertoire
  retenu — citant des chemins `templates/` morts.

Établi par : `grep -rn 'templates' skills/implementation-tracker/list-dir .claude/implementation/todo`
le 2026-09-20 → dix occurrences, dont aucune n'était visible par les critères du brief, tous verts
au même instant.

## Pourquoi c'est gênant

Un critère qui passe pendant que le défaut visé subsiste est pire qu'un critère absent : il autorise
la clôture. Ici, seul l'audit a vu l'écart, et il n'a pas d'obligation de chercher là où les
critères ne regardent pas — une prochaine fois, la couverture tiendra au hasard de l'attention d'un
agent. Le coût est double : un renommage déclaré terminé qui ne l'est pas, et un journal de suivi
qui affirme le contraire de l'état réel, comme ce fut le cas ici.

Le mode de défaillance est propre aux chantiers de vocabulaire, où le critère *est* un grep :
chaque restriction de ce grep — répertoire, extension, casse — devient une zone où le mot survit
sans que rien ne le dise.

## Pour solder

Poser la règle, dans `intent-brief` ou dans `skill-convention/references/prose.md` : **un critère de
réussite en forme de grep ne porte ni `--include` ni répertoire plus étroit que le périmètre du
chantier**, ou dit explicitement ce qu'il laisse dehors et pourquoi. Un chantier de renommage
recherche en outre sans distinction de casse — `GABARIT` avait déjà échappé au premier passage.

Vérifier : rejouer le cas de ce chantier sur un dépôt d'essai — un mot renommé dans un `.toml` de
définition doit faire échouer le critère tant qu'il subsiste.

## Assumé

<OPTIONNEL>
