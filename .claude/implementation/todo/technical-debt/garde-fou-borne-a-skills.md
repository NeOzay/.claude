+++
id = "garde-fou-borne-a-skills"
title = "Les contrôles de chemin ne regardent que skills/, alors qu'un point converti vit hors de skills/"
date = 2026-08-29
source = "Identifié par `resolution-chemin-skill`, R2 du rapport d'audit."
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

Les contrôles de chemin de `scripts/check_pipeline.py` s'appliquent tous à
`markdown_files(root, only="skills")` — `check_empreintes`, `check_portabilite`,
`check_chemins_skill` et `check_renvois_skill`. Or la conversion des points d'édition en dur a
touché `.claude/implementation/todo/README.md`, qui vit hors de ce périmètre et qu'aucun contrôle
n'examine. La forme `$HOME/.claude/skills/…` peut y être réintroduite sans qu'un seul rouge
apparaisse.

Établi par : sonde de l'audit de clôture — un chemin ancré sur le `HOME` déposé hors de `skills/`
laisse `check_chemins_skill` et `check_renvois_skill` se déclarer « contrôle sans objet ». Vérifié
le 2026-09-06 : `grep -n 'only="skills"' scripts/check_pipeline.py` rend quatre sites, et
`grep -n "\.claude/implementation" scripts/check_pipeline.py` aucun.

**Les contrôles sont nommés, non numérotés** — ils l'étaient (« 6, 7 et 8 ») jusqu'au 2026-09-06 ;
un contrôle ajouté depuis a décalé les rangs, et `check_empreintes` s'est joint aux trois sans que
l'entrée le voie. Un numéro de contrôle se périme comme un numéro de ligne.

## Pourquoi c'est gênant

Le critère du chantier était « le compte de points d'édition cesse de croître ». Il est tenu
**dans** `skills/`, pas hors de `skills/` — et c'est précisément hors de `skills/` que le registre
et ses README vivent, c'est-à-dire les fichiers qu'un chantier futur éditera le plus souvent. La
garantie est donc plus étroite que ce que le solde de `chemin-skill-code-en-dur` laisse croire.

## Pour solder

Étendre le périmètre de `check_empreintes`, `check_portabilite`, `check_chemins_skill` et
`check_renvois_skill` aux `.md` de `.claude/implementation/` — au minimum aux `README.md` et aux
registres, l'archive `done/` devant rester exclue puisqu'elle relate un état passé et ne se
réécrit pas. Vérifier par une sonde hors `skills/` qui doit devenir rouge.

