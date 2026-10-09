+++
gabarit = "suivi"
slug = "messages-du-pipeline"
titre = "Raccourcir les messages que le pipeline rend à l'utilisateur : Brief, commit, contexte, audit"
branche = "messages-du-pipeline"
base = "master"
statut = "terminé"
session = 2
lettre = "A"
"modèle" = "opus"
plan = ".claude/implementation/done/2026-10-09-messages-du-pipeline.plan.md"
brief = ".claude/implementation/done/2026-10-09-messages-du-pipeline.brief.md"
audit = ".claude/implementation/done/2026-10-09-messages-du-pipeline.audit.md"
road-map = "messages-du-pipeline"
skills = ["skill-convention"]
"créé" = 2026-10-09
maj = 2026-10-09
+++

## Objectif et périmètre

**Symptôme** : les messages du pipeline redisent ce que l'utilisateur voit déjà ailleurs — les
fichiers et les diffs dans Neovim, les tokens dans la ligne d'état — : « Ma lecture », « Chemins
stagés », « Voir le diff complet », « Contexte : … sous le seuil », « Le verdict est inscrit au
suivi », « Je ne la lance pas sans votre feu vert ».

**But** : réduire chaque message du pipeline à ce que l'utilisateur ne voit pas déjà ailleurs, et
le cadrage du Brief à des échanges, puis à un fichier que l'utilisateur corrige.

**Critères de réussite** : ceux du Brief, sauf `uvx rumdl fmt --check .`, borné aux fichiers
Markdown du diff du Chantier (journal, 2026-10-09).

**Hors-périmètre** :

- les choix qui terminent un commit d'Étape ou de Retouche, et le déroulement qu'ils entraînent ;
  le nombre de tours d'un Chantier : entrée `enchainement-du-chantier` ;
- le fond de l'audit — verdict, relance, forme du rapport : entrée `refonte-de-l-audit`.

**Signaux de dérive** :

- le diff touche aux choix de fin d'Étape ou au déroulement qu'ils entraînent ;
- le diff touche à l'échelle du verdict, à la relance de l'audit, à la forme du rapport ou à
  `agents/implementation-auditor.md` ;
- un commit, de quelque type, peut partir sans demande d'accord, ou la règle globale de
  `CLAUDE.md` change ;
- intent-brief perd les arbitrages fermés, ou ses questions précèdent la reconnaissance du dépôt ;
- un message du pipeline gagne une formule fixe au lieu d'en perdre.

## Étapes

- [x] 1. Règle des messages, au contrat — `implementation-tracker/references/contrat.md`,
  `scripts/check_pipeline.py`, trois `SKILL.md` — vérif: `python3 scripts/check_pipeline.py`
- [x] 2. Commits : staging et confirmation —
  `git-smart-commit/references/{staging,confirmation}.md`, `git-smart-commit/SKILL.md`, mémoire
  `index-avant-commit` — vérif: `! grep -rn -e "Voir le diff" -e "jamais \`-A\`" skills agents`
- [x] 3. Commits : les trois procédures —
  `git-smart-commit/references/{etape,hors-chantier,aplatissement}.md` — vérif:
  `! grep -rn -e "hemins stagés" -e "chemins à stager" skills agents`
- [x] 4. intent-brief : échanger, écrire, corriger, puis proposer — `intent-brief/SKILL.md`,
  `grille-questions.md`, `gabarit/brief/contract.toml`, `contrat.md` (Slug) — vérif:
  `! grep -rni -e "Ma lecture" -e "question par tour" skills agents`
- [x] 5. Contexte et audit — `implementation-tracker/references/{execution,audit,cloture}.md` —
  vérif: `grep -n "Gravité réelle" skills/implementation-tracker/references/audit.md`

## État courant

**Prochaine action** : Clôture — aplatissement sur `master`.

**Vérification** : la section « Vérification de bout en bout » du Plan.

**Dernier audit** : 617de9f — DÉFAVORABLE — 2026-10-09

**Notes** : l'entrée `enchainement-du-chantier` porte les décisions de fin d'Étape prises au Brief.

## Passation

<OPTIONNEL>

## Journal de décisions

- **2026-10-09** — Critère `rumdl` borné aux fichiers Markdown du diff. *Pourquoi* : six fichiers
  hors Chantier échouent déjà. *Rejeté* : les reformater, Éléments de `todo/` compris.
- **2026-10-09** — Commits d'Étape et de Retouche : deux choix génériques en attendant
  `enchainement-du-chantier`. *Pourquoi* : leurs choix relèvent de cette entrée. *Rejeté* : poser
  ses trois choix dès maintenant.
- **2026-10-09** — MD041 désactivé pour `.claude/implementation/*.md` dans `.rumdl.toml`.
  *Pourquoi* : tout brief et tout suivi posés depuis leur semence l'échouent. *Rejeté* : retirer
  brief et suivi du critère, écart retrouvé au Chantier suivant.
- **2026-10-09** — Forme du commit d'Étape sans « avec le pied d'attribution », seul bloquant (R1)
  de l'audit DÉFAVORABLE sur `617de9f`. *Pourquoi* : la mention venait du commit réel cité en
  exemple au Brief, non de la forme voulue. *Rejeté* : la rétablir.
- **2026-10-09** — Clôture sans nouvel audit après `617de9f`, sur décision de l'utilisateur.
  *Pourquoi* : R1 levé par décision, R4 à R6 corrigés en lignes isolées. *Rejeté* : relancer un
  audit complet.
