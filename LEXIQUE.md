# Lexique global

Termes réservés dans tous les projets. Règles d'emploi :
[`skills/lexique/instructions.md`](skills/lexique/instructions.md).

| Terme | Définition | Lien |
|---|---|---|
| Gabarit | Fichier Markdown à front matter TOML, posé depuis une Semence et vérifié contre elle. | [gabarit](skills/gabarit/SKILL.md) |
| Semence | Répertoire, résolu par son nom, qui porte le Contrat depuis lequel on pose un Gabarit ou on amorce une List-dir. | [semences](skills/gabarit/references/semences.md), [définitions](skills/list-dir/references/definitions.md) |
| Contrat | Déclaration des champs et des sections qu'un Gabarit ou un Élément doit porter. | [Le contrat](skills/gabarit/references/format.md#le-contrat) |
| Estampille | Champ `gabarit = "<nom>"` en tête d'un fichier posé, qui désigne sa Semence. | [L'estampille](skills/gabarit/SKILL.md#lestampille) |
| Marqueur | Valeur provisoire (`<À REMPLIR>`, `<OPTIONNEL>`) qui dit qu'un champ ou une section reste à écrire. | [Les marqueurs](skills/gabarit/references/format.md#les-marqueurs) |
| List-dir | Répertoire dont chaque `*.md` à la racine est un Élément, et dont `.list/contract.toml` déclare la structure. | [list-dir](skills/list-dir/SKILL.md) |
| Élément | Fichier `*.md` à la racine d'une List-dir, dont le nom est l'`id`. | [Un élément](skills/list-dir/references/format.md#un-élément) |
| Patron | Moule de `derive`, `.list/patrons/<nom>.{toml,md}`, qui projette une List-dir sur une List-dir neuve. | [list-dir](skills/list-dir/SKILL.md) |
| Chantier | Implémentation conduite par implementation-tracker, du Brief à la Clôture, sur la branche `<slug>`. | [implementation-tracker](skills/implementation-tracker/SKILL.md) |
| Brief | Fiche d'intention d'un Chantier (intention, critères, bornes), figée à sa validation. | [intent-brief](skills/intent-brief/SKILL.md) |
| Suivi | Fichier d'un Chantier qui porte son objectif, ses Étapes, son état et ses décisions, tenu à jour en continu. | [implementation-tracker](skills/implementation-tracker/SKILL.md) |
| Étape | Unité de travail d'un Chantier telle que le Suivi la tient, avec ses fichiers et sa commande de vérification ; elle peut s'écarter du Plan initial. | [Format d'étape](skills/implementation-tracker/references/contrat.md#format-détape-et-délégabilité) |
| Signal de dérive | Indice, lisible dans le diff, qu'un Chantier s'écarte de son Brief, et qui arrête l'implémentation. | [implementation-tracker](skills/implementation-tracker/SKILL.md) |
| Registre | List-dir tenue par le pipeline : dette technique ou road-map. | [Registre de dette](skills/implementation-tracker/references/dette.md) |
| Plan | Document qui décrit les Étapes initiales d'un Chantier, relu par plan-reviewer ; le Suivi reprend ces Étapes et les tient à jour. | [implementation-tracker](skills/implementation-tracker/SKILL.md) |
| Hors-périmètre | Exclusion écrite au Brief : ce que le Chantier ne fait pas. | [intent-brief](skills/intent-brief/SKILL.md) |
| Base | Branche principale d'où part un Chantier, et sur laquelle il est aplati à la Clôture. | [Frontmatter](skills/implementation-tracker/references/contrat.md#frontmatter) |
| Clôture | Fin d'un Chantier livré : audit, archivage en `done/`, aplatissement sur la Base. | [implementation-tracker](skills/implementation-tracker/SKILL.md) |
| Abandon | Fin d'un Chantier non livré : archivé avec sa raison, jamais aplati sur la Base. | [implementation-tracker](skills/implementation-tracker/SKILL.md) |
