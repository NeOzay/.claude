+++
id = "critere-reussite-faux-dans-sa-lettre"
title = "Un critère de réussite du brief `contrat-pipeline` était faux dans sa lettre"
date = 2026-08-14
source = "Identifié par `contrat-pipeline`, R1 du rapport d'audit ; élargi par `revue-dette`, R14."
reviewed = 2026-09-06
category = "pertinent"
+++

## Constat

le brief exigeait `grep -l 'contrat' agents/*.md` → aucun résultat. Les deux agents
contiennent « contrats en lecture », formulation antérieure au chantier : le critère ne pouvait pas
être atteint tel qu'écrit. Le contrôle 4 du garde-fou cherche `contrat\.md`, ce qui est l'intention
réelle, et passe.

## Pourquoi c'est gênant

un critère de réussite invérifiable dans sa lettre affaiblit le
dispositif qui le porte : l'auditeur doit choisir entre la lettre et l'intention, ce qu'on lui
interdit par ailleurs (« n'invente pas de critère »).

## Pour solder

rien sur ce chantier-ci ; y penser au cadrage suivant, en écrivant les critères
sous la forme exacte de la commande qui les établit.

**Élargi le 2026-08-17 par `revue-dette`** — deuxième occurrence, sous une autre forme : le
critère 4 de ce brief (« `git status --short` après une passe ne montre que des chemins sous
`.claude/implementation/` ») porte sur l'état de l'arbre **pendant** une passe. À la clôture l'arbre
est commité et propre, et le skill n'est pas relançable (`disable-model-invocation`) : l'auditeur
n'a pu établir que ce qui ne le contredit pas, et a dû s'en remettre à la déclaration du suivi pour
l'attribution des fichiers modifiés. Un critère vérifiable aurait exigé que la sortie de l'Étape 5
soit **recopiée dans le rapport archivé** — la seule pièce qui survit à la passe.

**Pour solder, complété** — un critère de réussite doit nommer la pièce **persistante** qui
l'établit, pas un état transitoire de l'arbre de travail. C'est la généralisation des deux cas.

## Assumé

constaté au premier audit, jugé non bloquant, jamais corrigé — le brief est figé après
validation.
