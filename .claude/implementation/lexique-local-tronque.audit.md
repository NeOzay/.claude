## Audit du 2026-10-06

**Verdict : DÉFAVORABLE.**

Audit de clôture hors Chantier, sur le diff non commité de `master` au-dessus de `5a080c8`
(`git diff HEAD`) : `skills/lexique/mod/hooks/register.ts`, `register.test.ts`, `SKILL.md`,
`scripts/lexique-cli.py`, `settings.json` (le passage de `"model"` à `"sonnet"` est ignoré, il
n'appartient pas à ce travail). Ni Brief, ni Suivi, ni Plan : les sections de cette entrée en
tiennent lieu.

Le symptôme d'origine a disparu : la session principale reçoit le lexique local entier. Mais le bloc
`lexiqueLocal` arrive aussi aux sous-agents, y compris à ceux qui doivent rester isolés : le
correctif casse le contrat du mod établi par le Chantier `lexique-des-sous-agents`, et le texte de
`SKILL.md` affirme l'inverse de ce qui se passe. Une régression constatée à l'exécution sur un
contrat écrit l'emporte sur un critère atteint : verdict le plus sévère.

### Vérifications exécutées

| Commande | Résultat réel |
|---|---|
| `claude plugin test skills/lexique/mod` | 6 pass, 0 fail (base `HEAD` extraite : 4 pass, 0 fail) |
| `claude plugin validate skills/lexique/mod` | passé, avertissements `author` absent et `gating hook without .catch: agent.spawn` — tous deux présents à l'identique sur la base |
| `npx -p typescript@5 tsc -p tsconfig.json --noEmit` (dans `skills/lexique/mod`) | sortie 0, `register.ts` et `register.test.ts` vérifiés (`--listFiles`) ; base : sortie 0 |
| `uvx ruff check .` (dans `skills/lexique`) | `All checks passed!` |
| `uvx ruff format --check .` (dans `skills/lexique`) | `12 files already formatted` |
| `uvx --with pytest basedpyright` (dans `skills/lexique`) | `0 errors, 0 warnings, 0 notes` |
| `~/.claude/.venv/bin/python -m pytest scripts/tests -q` (dans `skills/lexique`) | 90 passed |
| `CLAUDE_PROJECT_DIR=…/claude-translator lexique-cli.py session` | sortie 0, texte brut (pas de JSON), 13 094 caractères |
| `claude -p --model haiku` dans `claude-translator`, sans outil | bloc `lexiqueLocal` présent ; dernière ligne du tableau citée exacte (« Passe typographique ») ; aucune mention d'aperçu ni de fichier de débordement |
| `claude -p --model haiku` dans `claude-translator`, lançant `lexique-test-isole` et `lexique-test-claude-md` | `isole` : lexique local présent, section `lexiqueLocal` présente ; `claude-md` : en-tête « Lexique local de » vu **2 fois** |
| `claude -p --model sonnet --output-format stream-json` dans `claude-translator`, lançant `lexique-test-isole` | lexique local présent, première ligne de la section `# lexiqueLocal` citée mot pour mot ; seuls outils appelés : `Agent` et `SubagentHandback`, aucun `Read` |
| `grep` des hooks `SessionStart` de `settings.json` | reste `python3 $HOME/.claude/scripts/sante_skills.py` seul |
| `list-dir validate` sur le registre, avant cette section | 85 éléments conformes |

### Conformité à l'intention

**R1 — Critère « verser le lexique local à la session par une voie sans plafond » : atteint.** Le
hook `prompt.context` lance `lexique session` et ajoute sa sortie, sans la tronquer, aux blocs du
premier message ; le hook `SessionStart` de `settings.json` est retiré. Vérifié en session neuve
`claude -p` dans `claude-translator` : bloc présent, dernière ligne du tableau restituée exacte, pas
d'aperçu. Réserve : vérifié en mode `-p` seulement, sur un seul essai et avec `haiku`. Une session
interactive, un `/clear` et une compaction (le type dit que le bloc est recalculé à la relecture)
n'ont pas été essayés.

**R2 — Second membre du « Pour solder » : lu comme propre à la seconde option.** « faire dire à
`lexique liste` qu'il dépasse » n'a de sens que si le lexique reste soumis au plafond ; la voie sans
plafond ayant été prise, l'absence de cet avertissement n'est pas retenue comme critère manqué. Si
l'utilisateur entendait les deux membres cumulés, `lexique liste` ne dit toujours rien d'un lexique
de plus de 10 000 caractères. Interprétation, à confirmer.

**R3 — BLOQUANT. Le bloc `lexiqueLocal` atteint les sous-agents isolés.** `lexique-test-isole`
(`omitClaudeMd: true`, sans `injectLexique`), lancé dans `claude-translator`, cite mot pour mot la
première ligne d'une section `# lexiqueLocal` de son contexte, sans avoir appelé aucun outil (trace
`stream-json`). Sur la base, il ne recevait rien : `SessionStart` n'atteint pas les sous-agents, et
`annonce_sous_agent` rend `""` pour cet agent. Le contrat écrit — tableau de `SKILL.md`,
« `omitClaudeMd: true` → rien : l'isolation est voulue » — est rompu. Cause lisible dans le type :
`PromptContextInput` ne porte que `blocks` et `instructionFiles`, aucun `agentId`, et la réponse est
mise en cache pour la conversation ; le hook ne peut pas distinguer la boucle principale et ne le
tente pas. Aucun test du mod ne peut voir ce cas : le banc de `claude plugin test` n'appelle
`prompt.context` qu'à la main.

**R4 — BLOQUANT. Le lexique local arrive deux fois aux sous-agents non isolés.** Pour
`lexique-test-claude-md`, le mod préfixe toujours le `prompt` du lexique local par `agent.spawn`, et
le bloc `lexiqueLocal` s'y ajoute : l'agent compte deux en-têtes « Lexique local de ». Sur
`claude-translator`, c'est environ 13 000 caractères de plus à chaque sous-agent, et deux copies
qui, à la prochaine modification du lexique, se lisent dans deux états si l'une est en cache.
`lexique-test-injecte` n'a pas été essayé ; par le même mécanisme, il reçoit vraisemblablement le
local deux fois aussi (supposition, non vérifiée).

**R5 — Le texte affirme ce que le code ne fait pas.** `SKILL.md`, « Ce que reçoit un sous-agent » :
« Un sous-agent ne reçoit pas le lexique que la session reçoit » — démenti par R3 et R4. Le tableau
qui suit, l'en-tête de `annonce_sous_agent` dans `scripts/lexique.py` (« Sans `omitClaudeMd`, …
il ne manque que le local ») et le docstring de `lexique-cli.py` décrivent tous un partage des rôles
que le nouveau hook a rompu.

**R6 — Sans le mod chargé, plus aucun lexique local, et rien ne le signale.** Le hook
`SessionStart` de secours est retiré sans remplaçant ; `SKILL.md` le déclare (« aucun hook n'est
déclaré dans `settings.json` pour le suppléer »), ce qui en fait une dette assumée par écrit. Mais
rien ne la détecte : `scripts/sante_skills.py` ne contrôle pas que le mod est chargé, et un mod qui
ne se charge pas (`CLAUDE_CODE_PLUGIN_DIRS` ignoré, autre machine, `--plugin-dir` oublié) n'émet pas
la ligne d'état prévue pour les échecs de commande. Le « rien ne le dit » de cette entrée revient
sous une autre forme : là où la base rendait un aperçu tronqué, la session ne reçoit plus rien, en
silence. `claude plugin list` le montre chargé ici (`lexique-sous-agent@inline`, `✔ loaded`).

### Qualité du code

**R7 — Le refactor d'`agent.spawn` préserve le comportement.** `lancer` reprend le `try` à
l'identique ; `tirer` est appelé dans le `try`, si bien qu'un `JSON.parse` en échec reste rattrapé
et dit sur la ligne d'état, comme avant. Les quatre tests antérieurs passent sans retouche. Le style
suit les fichiers voisins : noms français, commentaires qui disent pourquoi, `next(… : e)` en sortie
unique.

**R8 — Commentaires et métadonnées restés à l'ancien état.**

- `skills/lexique/scripts/lexique.py`, ligne 15 : « le hook `SessionStart` lance ce module » — ce
  hook n'existe plus ; c'est le mod qui le lance.
- `skills/lexique/mod/.claude-plugin/plugin.json` : « Verse le lexique à un sous-agent au
  démarrage » — il le verse aussi à la session.
- `register.ts`, commentaire repris dans `lancer` : « Sous Python < 3.12 la CLI sort en 0 sans rien
  rendre, pour `sous-agent` » — c'est vrai aussi pour `session` (`lexique-cli.py`, ligne 33), le
  `pour sous-agent` est désormais trop étroit.
- Le mod garde le nom `lexique-sous-agent` (manifeste, préfixe des messages d'état, citations de
  `SKILL.md`) alors qu'il sert aussi la session : la phrase « La session principale reçoit le
  lexique local par le mod `lexique-sous-agent` » se lit à rebours.
- `lexique-cli.py`, docstring : la puce `session` est réenroulée en une ligne de 24 caractères
  (« composition du premier message, et un ») entre deux lignes pleines, hors de l'enroulement à
  100 colonnes du reste du bloc.

**R9 — Tests : nominal et vide couverts, la séparation session / sous-agent ne l'est pas.** Les deux
tests ajoutés vérifient l'`argv`, le `CLAUDE_PROJECT_DIR` transmis, le nom et le texte du bloc, et
les blocs intacts sur une sortie vide. L'échec de commande sur `prompt.context` n'a pas de test
propre ; il passe par `lancer`, déjà couvert par les tests d'`agent.spawn`, ce qui suffit. Écart de
style mineur : `CONTEXTE` et `blocsVus` sont déclarés au milieu du fichier, quand `SPAWN` et `fond`,
leurs homologues, ouvrent le fichier ; et `blocsVus` ne suit pas le nommage de `fond`.

### Dette induite

**R10 — `Moteur` est tiré du seul `agent.spawn`.**
`type Moteur = Parameters<Hook<'agent.spawn'>>[0]` type aussi le `$` de `prompt.context`. `tsc`
passe, donc les deux `$` sont aujourd'hui compatibles ; mais `lancer` dépend du type d'un événement
qu'elle ne sert qu'à moitié, et une évolution du `$` propre à `agent.spawn` se propagerait au hook
de session sans que rien ne le signale à la lecture.

**R11 — Une autre entrée du Registre décrit désormais un état révolu.**
`technical-debt/hook-sante-chemin-home.md`, paragraphe « Aggravée le 2026-09-23 » et son « Établi
par » : « quatre lignes : deux hooks `SessionStart` (`sante_skills.py`, `lexique-cli.py session`) ».
Le second hook est retiré, il n'en reste que trois. L'entrée n'est pas de ce périmètre et n'a pas
été modifiée : à reprendre à sa prochaine revue.

### Ce qui interdit le solde

- R3 : un agent `omitClaudeMd: true` sans `injectLexique` reçoit le lexique local.
- R4 : un sous-agent non isolé reçoit le lexique local deux fois.
- R5 : `SKILL.md` affirme le contraire de R3 et R4.

### Note sur ce rapport

**R12 — Cette section fait échouer le Registre.** Après son ajout, `list-dir validate` sur
`technical-debt/` rend `1 manquement` : « section « Audit du 2026-10-06 » — non déclarée au
contrat » (85 conformes avant). Elle a été écrite ici sur demande expresse ; ni le contrat ni
l'entrée n'ont été touchés autrement. À trancher : déclarer la section au contrat, ou déplacer ce
rapport.

## Audit du 2026-10-06, second passage

**Verdict : DÉFAVORABLE.**

Audit de clôture hors Chantier, sur le diff non commité de `master` au-dessus de `5a080c8`
(`git diff HEAD`), après les modifications qui suivent le premier passage : `register.ts` (hook
`session.start` + `$.session.append` à la place de `prompt.context`), `register.test.ts`,
`lexique-cli.py`, `lexique.py`, `test_sous_agent.py`, `SKILL.md`, `plugin.json`, et le retrait du
hook `SessionStart` de `settings.json` (le passage de `"model"` à `"sonnet"` est ignoré). Ni Brief,
ni Suivi, ni Plan : le Constat, le « Pourquoi c'est gênant » et le « Pour solder » de l'entrée
`lexique-local-tronque-par-le-hook-session` en tiennent lieu. Les constats du premier passage sont
cités « R3 (1er) » pour ne pas les confondre avec ceux-ci.

Les deux bloquants du premier passage sont levés, constaté à l'exécution : un agent isolé ne
reçoit plus rien, un agent non isolé reçoit le lexique local une seule fois. Mais la nouvelle voie a
son propre défaut : `session.start` ne se déclenche qu'une fois par processus, pas après `/clear` ni
après une compaction. Dans ces deux cas, la session principale ne reçoit plus aucun lexique local,
alors que le hook `SessionStart` retiré repassait (`source=clear`, `source=compact`, constaté). Cela
vaut pour tous les projets, y compris ceux dont le lexique fait moins de 10 000 caractères, qui
fonctionnaient sur la base. On retrouve le tort que l'entrée décrit, « emploie des termes qu'elle
ignore, et rien ne le dit », en pire : plus rien au lieu d'un aperçu. La compaction automatique est
le sort ordinaire d'une longue session. Je retiens donc le verdict le plus sévère.

### Vérifications exécutées

Claude Code 2.1.291. Sessions lancées dans `/home/debian/projects/claude-translator` (lexique local
de 13 338 octets, sortie de `lexique session` de 13 093 caractères). La CLI
`claude -p … < /dev/null` ou `--input-format stream-json`. Chaque comptage est fait
**sur la transcription** (`~/.claude/projects/-home-debian-projects-claude-translator/<id>.jsonl`),
pas sur la seule réponse du modèle : `haiku` a compté une copie là où la transcription en portait
deux.

| Commande | Résultat réel |
|---|---|
| `claude plugin test .` (dans `skills/lexique/mod`) | 5 pass, 0 fail |
| `claude plugin validate .` | passé ; avertissements `author` absent et `gating hook without .catch: agent.spawn`, les deux déjà présents sur la base |
| `npx -p typescript@5 tsc -p tsconfig.json --noEmit` (dans `skills/lexique/mod`) | sortie 0 |
| `uvx ruff check .` (dans `skills/lexique`) | `All checks passed!` |
| `uvx ruff format --check .` (dans `skills/lexique`) | `12 files already formatted` |
| `uvx --with pytest basedpyright` (dans `skills/lexique`) | `0 errors, 0 warnings, 0 notes` |
| `~/.claude/.venv/bin/python -m pytest scripts/tests -q` (dans `skills/lexique`) | 90 passed |
| `uvx rumdl fmt --check skills/lexique/SKILL.md` | `No issues found` |
| `lexique-cli.py sous-agent` sans argument | sortie 2, `the following arguments are required: agent_type`, stdout vide |
| `lexique-cli.py sous-agent <type>` pour `isole` / `claude-md` / `injecte` / `Explore` / `analyste` | 0 / 13 093 / 19 337 / 0 / 13 093 caractères ; « Lexique local de » une fois dans chaque sortie non vide |
| `claude -p --model haiku`, session principale seule | ligne `user` `isMeta` de 13 093 caractères en tête de la transcription ; dernière ligne du tableau (« Passe typographique ») restituée exacte ; aucun aperçu ; aucun outil appelé |
| `claude -p --model haiku`, lançant les trois témoins | `isole` : première ligne `user` = « Fais ton constat. » (17 caractères), réponse « absent » ×3 ; `claude-md` : 13 194 caractères, « Lexique local de » ×1 ; `injecte` : 19 438 caractères, local ×1, global ×1 ; les trois réponses conformes au tableau de `SKILL.md` |
| `claude -p --model sonnet`, lançant `lexique-test-isole` (reprise du test R3 (1er)) | « absent » pour le local, le global, les règles, `lexiqueLocal`, « Passe typographique » et « Orchestrateur » ; seuls outils : `Agent`, `SubagentHandback` |
| `claude -p --resume <id>` puis `claude -p --continue` sur la même session | transcription : **3** lignes `isMeta` « Lexique local de… » de 13 093 caractères chacune (une par processus) |
| `claude -p --settings <hook SessionStart témoin> --input-format stream-json` : question, `/clear`, question | avant `/clear` : lexique présent, témoin `source=startup` ; après : **aucune ligne de lexique** dans la transcription de la nouvelle session, le modèle répond « Non » ; le témoin repasse, `source=clear` |
| même montage avec `--resume`, question, `/compact`, question | à la reprise, une ligne de lexique de plus (et le témoin `source=resume`, s'accumule aussi) ; après `compact_boundary` : le résumé ne porte pas le tableau, **aucune ligne de lexique ré-ajoutée** ; le témoin repasse, `source=compact` |
| sonde sur une **copie** du mod (scratchpad) : `on('session.append', …)` dans un test | non appelé ; le moteur rapporte « session.start hook was skipped: lexique-sous-agent: no implementation for session.append » |
| `list-dir validate technical-debt` | 85 éléments conformes |

Non exécuté : une session **interactive** (TTY) ; un **rechargement** du mod ou une relance du
worker en cours de session, qui demanderait de modifier `register.ts` ; une compaction
**automatique** (seule `/compact` a été essayée, le type les range sous le même événement) ; un
sous-agent `fork`.

### Conformité à l'intention

**R1 — BLOQUANT. Après `/clear` ou une compaction, la session principale n'a plus de lexique
local.** Le type de l'hôte le dit (`'session.start'` : « Fires once per process for each loaded
plugin, before the first prompt, then once per fresh load of one (never `/clear`) »), et les deux
essais le confirment : la nouvelle session ouverte par `/clear` ne porte aucune ligne de lexique, et
le résumé de compaction ne garde pas le tableau. Le hook `SessionStart` retiré repassait dans les
deux cas : le témoin passé par `--settings` est vu avec `source=clear` et avec `source=compact`. Ce
que la base faisait correctement pour un lexique de moins de 10 000 caractères, et en aperçu
au-delà, ne se fait plus du tout, et rien ne le signale. Le contrat écrit est rompu :
`skills/lexique/instructions.md` dit le local « versé au contexte au démarrage de la session », et
une session ouverte par `/clear` (nouvel identifiant) ne le reçoit pas. `SKILL.md` (« Ce que reçoit
la session ») n'en dit rien. Le critère « verser le lexique local à la session par une voie sans
plafond » n'est donc atteint que pour le premier segment d'une session. Pour information, sans que
ce soit une préconisation : les types de l'hôte exposent `session.compact` et `session.end` (motif
`clear`), et rien n'interdit de garder un hook `SessionStart` pour les sources `clear`/`compact`.
Trancher revient à l'auteur.

**R2 — Au démarrage, critère atteint.** Ligne `user` `isMeta` de 13 093 caractères, entière, avant
le premier message ; dernière ligne du tableau restituée exacte ; aucun aperçu ni fichier de
débordement. Vérifié en `-p` seulement (voir R6).

**R3 — Chaque reprise ajoute une copie entière.** `--resume` puis `--continue` sur la même session
donnent trois lignes de 13 093 caractères, soit environ 39 000 caractères de lexique répétés. La
base faisait de même dans son principe : le témoin `SessionStart` s'accumule aussi (`startup`,
`resume`). Mais elle ajoutait un aperçu de 2 Ko par reprise pour un gros lexique, et ici c'est le
lexique entier. Ce n'est pas une régression de comportement, mais le coût change d'échelle, et
`SKILL.md` ne le dit pas.

**R4 — Le second membre du « Pour solder » reste lu comme alternatif.** C'est R2 (1er), inchangé :
`lexique liste` ne dit toujours rien d'un lexique de plus de 10 000 caractères. Je ne le retiens pas
comme un critère manqué, pour la raison donnée au premier passage. Mais R1 redonne du poids à cet
avertissement : après `/clear` ou une compaction, rien ne passe plus, et ce n'est même pas un aperçu
tronqué. Interprétation, à confirmer par l'utilisateur.

**R5 — Hors-périmètre et contrat des sous-agents : respectés.** Le tableau « Ce que reçoit un
sous-agent » de `SKILL.md` est vérifié ligne à ligne par les trois témoins (voir Vérifications). Le
consommateur Neovim (`~/.config/nvim/lua/lexique.lua`) n'appelle ni `session` ni `sous-agent` :
l'interface qu'il consomme n'a pas bougé.

**R6 — Cas non essayés, à tenir pour ouverts.**

- Session interactive : le type dit le premier `session.start` « awaited » avant le premier prompt,
  ce qui laisse attendre le même résultat qu'en `-p`. Supposition non vérifiée.
- Rechargement du mod, relance du worker, activation : le type les liste parmi les déclenchements
  ultérieurs de `session.start` (« A later one runs its hooks alone: an enable, a worker respawn,
  or a reload »). Chacun ajouterait vraisemblablement une copie de plus en cours de conversation.
  Dans ce dépôt, modifier `register.ts` pendant une session est un cas courant. Non vérifié.
- Sous-agent `fork` : il hérite de la conversation, donc vraisemblablement de la ligne ajoutée. La
  phrase de `SKILL.md`, « Un sous-agent ne reçoit pas la ligne que le mod ajoute à la conversation
  principale », serait alors fausse pour lui. Non vérifié.

### Qualité du code

**R7 — Le nominal de `session.start` passe sur un hook qui échoue dans le harnais.** Une sonde sur
une copie du mod montre que le harnais de `claude plugin test` n'a pas d'implémentation de
`session.append`. Dans le test « lance `lexique session` au démarrage », `$.session.append` lève
donc une exception, et le moteur saute le hook (« hook was skipped »). Le test passe quand même :
il n'assertit que l'`argv` et le projet, relevés avant l'ajout. Le commentaire est honnête sur ce
qu'il ne voit pas (« Le test ne voit pas la ligne que le mod ajoute »), mais il annonce aussi « que
`session.start` suit son cours quand l'ajout échoue ». Aucun test ne l'assertit : le second test
couvre une **commande** en échec (sortie 2), donc aucun ajout tenté. Un ajout supprimé, ou appelé
avec de mauvais arguments, laisserait les cinq tests verts. La couverture réelle de l'ajout, ce
sont les sessions témoins, qui ne sont pas rejouables par `claude plugin test`.

**R8 — L'échec de l'ajout ne passe pas par la ligne d'état du mod.** `await $.session.append(…)`
est hors du `try` de `lancer`. Si l'appel lève, le hook est sauté et le moteur « reports by name »
l'échec, mais pas par le message `lexique-sous-agent : …` que le mod promet pour ses erreurs. Une
réponse `{ deny: reason }` (un plugin ou une politique qui refuse l'ajout) est ignorée sans un mot.
Dans les deux cas, la session n'a pas de lexique, comme en R1, et le mod se tait.

**R9 — `lexique sous-agent` : contrat tenu.** Le texte brut, le code 2 sans argument et le 0 sinon
sont vérifiés à l'exécution. Le passage du JSON sur stdin à un argument supprime proprement
`json`/`cast`, et `test_sous_agent.py` suit. Cas limite négligeable : le type est un positionnel
`argparse`, si bien qu'un type commençant par `-` serait lu comme une option
(`lexique-cli.py sous-agent --help` sort en 0 avec l'aide sur stdout, que le mod verserait au
`prompt`). Aucun nom d'agent réel n'a cette forme.

**R10 — Restes de l'ancien texte.**

- `skills/lexique/scripts/lexique-cli.py`, ligne 25 : « le hook doit rester rapide ». Ligne 31 :
  « les hooks y restent silencieux ». C'est désormais le mod qui appelle.
- `skills/lexique/mod/hooks/register.ts`, lignes 11-12 : commentaire enroulé à contretemps (ligne
  courte, puis ligne au-delà de 100 colonnes). Même chose dans `SKILL.md`, dernier paragraphe
  (« Le mod verse le lexique au contexte » seul sur sa ligne). `rumdl` l'accepte.
- `register.test.ts` : `DEMARRAGE` est déclaré au milieu du fichier, alors que `SPAWN`, son
  homologue, ouvre le fichier. C'est l'écart de style déjà noté au R9 (1er), reporté sur la
  nouvelle constante.

### Dette induite

**R11 — `Moteur` est toujours tiré d'`agent.spawn`.** C'est R10 (1er), inchangé :
`type Moteur = Parameters<Hook<'agent.spawn'>>[0]` type maintenant le `$` de `session.start`. `tsc`
passe, mais le couplage décrit au premier passage demeure.

### Suivi des constats du premier passage

| Constat (1er) | État | Constat de ce passage |
|---|---|---|
| R1 — critère atteint, réserve (interactif, `/clear`, compaction non essayés) | **toujours ouvert** : `/clear` et compaction essayés, en échec | R1, R2, R6 |
| R2 — second membre du « Pour solder » | **toujours ouvert** (interprétation à confirmer) | R4 |
| R3 — BLOQUANT, `lexiqueLocal` chez l'isolé | **traité**, vérifié sous `haiku` et `sonnet` | R5 |
| R4 — BLOQUANT, local en double chez le non-isolé | **traité** : une copie pour `claude-md` et pour `injecte`, comptée sur transcription | R5 |
| R5 — texte contraire au code | **traité** pour les sous-agents ; le texte de la session omet `/clear`, la compaction et la reprise | R1, R3 |
| R6 — rien ne signale un mod non chargé | **non traité**, sciemment | — |
| R7 — refactor fidèle | **toujours valable** : `lancer` garde le `try` et la ligne d'état ; plus de `JSON.parse`, donc plus de cas de sortie illisible | — |
| R8 — commentaires et métadonnées | **traité en partie** : `lexique.py` l. 15, `plugin.json`, « pour `sous-agent` » et l'enroulement du docstring sont corrigés ; nom du mod non traité sciemment ; deux « hook » restent dans `lexique-cli.py` | R10 |
| R9 — tests | **toujours ouvert** : la séparation session / sous-agent n'a de couverture qu'en session, et le nominal de `session.start` passe sur un hook sauté | R7 |
| R10 — `Moteur` tiré d'`agent.spawn` | **toujours ouvert** | R11 |
| R11 — `hook-sante-chemin-home.md` révolu | **non traité**, sciemment (lignes 23 et 29 citent toujours `lexique-cli.py session` comme hook) | — |
| R12 — rapport dans le Registre | **traité** : rapport sorti, `list-dir validate technical-debt` donne 85 conformes | — |

### Ce qui interdit le solde

- R1 : après `/clear` ou une compaction, la session principale ne reçoit plus le lexique local,
  alors que la base le versait. La régression vaut pour tous les projets, et rien ne la signale.

## Audit du 2026-10-06, troisième passage

**Verdict : RÉSERVES.**

Audit de clôture hors Chantier, sur `master` à `86b5b7e`. Le travail jugé comprend le diff non
commité (`git diff HEAD`, le passage de `"model"` à `"sonnet"` étant ignoré) et les commits
`bd862b5` et `86b5b7e` (Shadow-skill `claude-code-mods`, tag `mods`). Il n'y a ni Brief, ni Suivi,
ni Plan : le Constat, le « Pourquoi c'est gênant » et le « Pour solder » de l'entrée
`lexique-local-tronque-par-le-hook-session` en tiennent lieu. Les constats des passages précédents
sont cités « R3 (1er) » et « R1 (2e) ».

Le critère est atteint, et vérifié à l'exécution dans tous les cas ordinaires : session neuve,
`/clear`, `/compact`, `--resume`, `--continue`, style de sortie, `--append-system-prompt`. Dans
chacun, la section de 13 093 caractères figure une seule fois dans le prompt système enregistré, et
aucun sous-agent ne la reçoit. Le bloquant du second passage, R1 (2e), est levé.

Restent des constats à connaître, dont aucun ne casse un usage constaté dans l'environnement :

- une régression sous `--system-prompt` (R4) ;
- la reprise d'une conversation commencée sans la section (R5) ;
- plusieurs affirmations du Shadow-skill démenties à l'exécution (R13).

J'ai hésité à rendre DÉFAVORABLE sur R4. Je ne l'ai pas fait parce que cette option n'est employée
par aucun projet de l'utilisateur (recherche faite), alors que le défaut retenu au second passage
touchait le cours ordinaire de toute session.

### Vérifications exécutées

Claude Code 2.1.291, sessions lancées dans `/home/debian/projects/claude-translator` (lexique local
de 13 338 octets). Pour compter les lancements de `lexique-cli.py`, un `python3` journalisant a été
placé en tête du `PATH`. Le comptage se fait dans la transcription : la ligne `prompt_snapshot`
(le prompt système enregistré, découpé en blocs), les lignes `user` et les sous-agents
(`<id>/subagents/*.jsonl`). La réponse du modèle n'a pas servi à compter.

| Commande | Résultat réel |
|---|---|
| `claude plugin test .` (dans `skills/lexique/mod`) | 7 pass, 0 fail ; aucune ligne « engine reported » |
| `claude plugin validate .` | passé ; avertissements `author` absent et `gating hook without .catch: agent.spawn`, les deux déjà présents sur la base ; hooks `prompt.compose`, `agent.spawn` |
| `npx --yes -p typescript@5 tsc -p tsconfig.json --noEmit` (mod) | sortie 0 ; `register.ts` et `register.test.ts` vérifiés (`--listFiles`) |
| `uvx ruff check .` / `uvx ruff format --check .` (dans `skills/lexique`) | `All checks passed!` / `12 files already formatted` |
| `uvx --with pytest basedpyright` (dans `skills/lexique`) | `0 errors, 0 warnings, 0 notes` |
| `~/.claude/.venv/bin/python -m pytest scripts/tests -q` | 90 passed |
| `uvx rumdl fmt --check skills/lexique/SKILL.md` | `No issues found` |
| `uvx rumdl fmt --check shadow-skills/claude-code-mods/SKILL.md` | **1 issue** : MD041, pas de titre de niveau 1 (voir R15) |
| `gabarit check shadow-skills/claude-code-mods/SKILL.md` | conforme à la semence « shadow-skill » |
| `shadow-skill tags` / `shadow-skill cherche mods` | tag `mods` présent ; le Shadow-skill est trouvé |
| `list-dir validate .claude/implementation/todo/technical-debt` | 85 éléments conformes |
| `lexique sous-agent` sans argument | sortie 2, stdout vide, `the following arguments are required: agent_type` |
| `lexique sous-agent <type>` : `isole` / `claude-md` / `injecte` / `Explore` / `analyste` | 0 / 13 094 / 19 338 / 0 / 13 094 caractères, « Lexique local de » au plus une fois ; sortie 0 partout |
| `claude -p --model haiku`, session principale | `prompt_snapshot` : 17 blocs, le 16e est le lexique (13 093 caractères, se termine par la ligne « Passe typographique ») ; réponse « Passe typographique », « pas de troncature » ; `lexique-cli.py session` lancé **une** fois |
| `claude -p --model haiku`, lançant les trois témoins | réponses conformes au tableau de `SKILL.md`. `isole` : premier message « Fais ton constat. » (17 caractères). `claude-md` : 13 194 caractères, local ×1. `injecte` : 19 438 caractères, local ×1. Prompt système de chaque sous-agent : 2 029 caractères, ni « Orchestrateur » ni « Passe typographique » |
| `--input-format stream-json` : question, `/clear`, question, `/compact`, question | trois réponses « Passe typographique ». Après `/clear` (nouvel identifiant) et après `compact_boundary`, chaque `prompt_snapshot` porte le lexique une fois. `lexique-cli.py session` lancé une fois pour tout le processus |
| `--resume <id>` puis `--continue` sur la même session | « Passe typographique » deux fois ; **aucune** ligne de lexique ajoutée à la transcription (le prompt enregistré est réutilisé) ; un lancement de `lexique session` par processus |
| `--settings '{"outputStyle":"Explanatory"}'` | lexique présent, une fois |
| `--append-system-prompt "Sois concis."` | lexique présent, une fois (18 blocs) |
| `--system-prompt "Tu es un assistant concis."` | **absent** : 2 blocs, réponse « absent » (R4) |
| même `--system-prompt`, avec l'ancien hook `SessionStart` passé par `--settings` | attachement `hook_success` du lexique, réponse « Pipeline » (dernier terme de l'aperçu de 2 Ko) : la base versait quelque chose |
| `--resume d6514c38… --fork-session` (conversation du second passage) | prompt enregistré à 09:37 réutilisé, sans section ; réponse « Absent. » (R5) |
| `claude --bare -p` (avec ou sans `--plugin-dir` du mod) | stderr : « lexique-sous-agent: hooks module not loaded: … (--bare) », puis « Not logged in » : session impossible sans clé d'API |
| Agent `subagent_type: "fork"` | « Agent type 'fork' not found » : non essayable dans cette configuration |
| Mod sonde (copie dans le scratchpad, `--plugin-dir`), `prompt.compose` journalisé | 1 composition pour 4 requêtes (`num_turns` 4), avec `--system-prompt-snapshot` à `on` comme à `off` ; 2 dans une session qui lance un sous-agent, toutes deux de la boucle principale (15 sections) |
| Mod sonde : `$.session.append({…, agentId})` après `next(e)` dans `agent.spawn` | **accepté**, en avant-plan comme en arrière-plan : la ligne `isMeta` « SONDE » est dans la transcription du sous-agent, avant son premier `prompt_snapshot` (R13) |
| Mod sonde, banc de test : `on('session.append', …)` + `$.session.append` | le fond n'est pas appelé ; l'appel lève « HooksError: no implementation for session.append » ; le test passe |
| Mod sonde, banc : un compteur au niveau du module, deux tests | le compteur vaut 1 dans chacun : le module est rechargé |
| Copie du mod, `type Moteur = EngineInterface` (importé de `claude-code`) | `tsc` : sortie 0 ; `claude plugin test` : 7 pass (R13, R16) |
| `claude -p "…"` sans `< /dev/null`, stdin non-TTY | « Warning: no stdin data received in 3s » ; 7,1 s contre 4,8 s avec `< /dev/null` |
| `grep` des hooks `SessionStart` de `settings.json` (lecture JSON) | `python3 $HOME/.claude/scripts/sante_skills.py` seul |

Effets de bord : les sessions d'essai ont laissé leurs transcriptions dans
`~/.claude/projects/-home-debian-projects-claude-translator/`, comme aux passages précédents. Les
mods sondes sont dans le scratchpad de la session. Aucun fichier du dépôt n'a été modifié, à part
celui-ci.

Non exécuté : une session **interactive** (TTY) ; une compaction **automatique** ; un sous-agent
`fork` (type refusé ici) ; un coéquipier d'équipe d'agents (`teammate`) ; une session `--bare`
authentifiée (aucune clé d'API).

### Conformité à l'intention

**R1 — Critère « verser le lexique local à la session par une voie sans plafond » : atteint,
vérifié.** La section `lexique-sous-agent:local`, en `scope: 'session'`, figure entière dans le
prompt système de la session principale : 13 093 caractères, la dernière ligne du tableau
comprise, sans aperçu ni fichier de débordement. Le symptôme d'origine a disparu.

**R2 — `/clear`, `/compact`, `--resume`, `--continue` : lexique présent, une seule fois.** R1 (2e)
et R3 (2e) sont levés. Le mécanisme tient à l'enregistrement du prompt système. Claude Code le rend
à la première requête d'une conversation et le consigne (`prompt_snapshot`). Une reprise renvoie ce
qui est consigné. `/clear` et la compaction le rendent à nouveau, et le mod rend chaque fois la même
section, mémorisée. D'où l'absence de duplication. C'est aussi ce qui produit R5.

**R3 — Contrat des sous-agents : respecté.** Le tableau de `SKILL.md` est vérifié ligne à ligne par
les trois témoins, et le prompt système de chaque sous-agent ne porte pas la section. Le mod sonde
montre que `prompt.compose` n'est appelé que pour la boucle principale. R3 et R4 (1er) restent
levés.

**R4 — Sous `--system-prompt`, la session principale n'a plus aucun lexique local.** Avec un
prompt système fourni, la composition du moteur est remplacée et la section du mod disparaît. Le
modèle répond « absent ». La base, elle, versait par `SessionStart` un aperçu au-delà de 10 000
caractères, et le lexique entier en deçà : constaté avec l'ancien hook passé par `--settings`.
C'est une régression pour ce mode, et rien ne la signale ; ni `SKILL.md` ni le Shadow-skill ne la
mentionnent. `--append-system-prompt` n'est pas touché. Je ne la retiens pas comme bloquante :
`--system-prompt`, `system_prompt` et le SDK n'apparaissent dans aucun projet de
`/home/debian/projects`, hormis les clients LLM d'`ebook-translator`, qui n'appellent pas
`claude`. Elle se tient au même rang qu'R6 (1er) : un mode où le lexique manque en silence.

**R5 — Une conversation reprise garde le prompt système qu'elle a enregistré.** Une conversation
commencée sans la section n'en reçoit pas à la reprise, jusqu'à sa prochaine compaction. C'est le
cas d'une conversation antérieure à ce changement, d'une conversation ouverte sans le mod chargé,
ou d'une conversation dont la première requête a vu `lexique session` échouer. Essayé sur une
conversation du second passage : « Absent. ». La base repassait à chaque reprise (`SessionStart`,
`source=resume`). Pour la même raison, une modification de `LEXIQUE.md` n'atteint pas une
conversation reprise avant sa compaction. « Le mod verse le lexique à la session dès la suivante »
(`SKILL.md`, dernier paragraphe) est vrai d'une session neuve, pas d'une reprise. C'est un effet
transitoire pour les anciennes conversations, et durable pour les deux autres cas. Il n'est écrit
nulle part.

**R6 — `--bare` et style de sortie : pas de régression.** Sous `--bare`, le moteur refuse de
charger le module du mod, même passé par `--plugin-dir` (message sur stderr). Les hooks de
`settings.json` y sont aussi sautés (`claude --help`), si bien que la base ne versait rien non plus.
Je n'ai pas pu ouvrir de session `--bare` (« Not logged in ») : le constat repose sur le refus de
chargement et sur l'aide, pas sur une réponse du modèle. Le style `Explanatory` garde la section.

**R7 — Cas non essayés, à tenir pour ouverts.**

- Session interactive : rien dans les types ne distingue sa composition de celle de `-p` (le
  trait `print` mis à part). Supposition non vérifiée.
- Compaction automatique : seule `/compact` a été essayée.
- Sous-agent `fork` : il « hérite du contexte du parent » (type `AgentSpawnInput.fork`), donc
  vraisemblablement du prompt système avec la section. Le mod ne lui ajoute rien (aucun fichier
  d'agent `fork`). Non vérifié : type refusé dans cette configuration.
- Coéquipier (`teammate`) : le trait `teammate` désigne le rendu, par un coéquipier en processus,
  du prompt de son chef. Il recevrait donc la section, et en plus le préfixe d'`agent.spawn` si son
  rôle a un fichier d'agent sans `omitClaudeMd`, soit une copie en double. Supposition tirée des
  types.

**R8 — Second membre du « Pour solder » : toujours lu comme alternatif.** C'est R2 (1er) et R4
(2e), inchangés : `lexique liste` ne dit toujours rien d'un lexique de plus de 10 000 caractères
(stderr vide sur `claude-translator`). La voie sans plafond étant prise, je ne le compte pas comme
un critère manqué. Interprétation, à confirmer par l'utilisateur.

### Qualité du code

**R9 — `register.ts` : juste et lisible ; « une fois » n'est vrai que d'un texte non vide.**
`lancer` factorise l'appel, garde l'échec ouvert et la ligne d'état, et rend `undefined` pour une
sortie vide. La composition appelle `next(e)` d'abord, puis ajoute la section en dernier, ce que
le type exige (une section `shared` après une `session` fait sauter le hook). Mais
`local ??= await lancer(…)` ne mémorise pas `undefined`. Dans un projet sans lexique local, ou
quand la commande échoue, chaque composition relance `python3`, et chaque échec redit son message
d'état. L'effet observé est nul : une composition pour quatre requêtes dans un projet sans lexique.
Mais « Calculé une fois » (commentaire) et « il lance `lexique session` une fois » (`SKILL.md`)
affirment plus que le code ne garantit.

**R10 — « se recompose à chaque requête » n'est pas ce qu'on observe.** Le commentaire de
`register.ts` (l. 38) le dit. Le mod sonde compte une composition pour quatre requêtes, que
`--system-prompt-snapshot` soit à `on` ou à `off`. C'est sans conséquence sur le comportement, mais
le motif donné à la mémorisation est inexact. Le Shadow-skill reprend la même affirmation (R13).

**R11 — Tests du mod : couverture honnête.** Les quatre tests de `prompt.compose` observent ce que
le hook rend : les sections, leur ordre, l'`id`, le texte et le `scope`. Ils n'ont pas le défaut
d'un hook sauté par le banc, R7 (2e) est donc levé. Ils couvrent l'`argv` et le projet transmis, la
mémorisation d'un texte non vide, la sortie vide et l'échec de commande. Ce que le banc ne peut pas
voir (sous-agents, `/clear`, prompt enregistré), aucun test ne prétend le couvrir ; les sessions
réelles ci-dessus le couvrent. Deux manques mineurs :

- la relance sur sortie vide (R9) n'est ni testée ni assumée ;
- le message d'état sur échec n'est vérifié que par le test d'`agent.spawn`, ce qui suffit puisque
  `lancer` est commun.

Le fichier se lit en deux blocs, un par événement, chacun ouvert par ses fixtures. L'écart de style
de R9 (1er) et R10 (2e) ne tient plus. Détail : les tests de composition écrivent `${TEXTE}\n` au
lieu de reprendre `SORTIE`.

**R12 — Restes de texte.**

- `register.ts`, l. 12-13 : commentaire enroulé à contretemps (une ligne courte, puis une ligne
  au-delà de 100 colonnes). Déjà relevé en R10 (2e), toujours présent.
- `SKILL.md`, l. 141-142 : « Le mod verse le lexique à la » coupé à 76 colonnes, suivi d'une ligne
  de 102. `rumdl` l'accepte.
- Le mod garde le nom `lexique-sous-agent` alors qu'il sert aussi la session, et la section en
  hérite (`lexique-sous-agent:local`). Ce choix est fait sciemment. Il rend « La session principale
  reçoit le lexique local par le mod `lexique-sous-agent` » contre-intuitif à la lecture.

### Le Shadow-skill `claude-code-mods`

**R13 — Quatre affirmations ne tiennent pas à l'exécution.** Le fichier s'ouvre sur « chacun a
été établi en exécutant, pas en lisant les types ». Elles sont démenties :

1. « Le `$` d'un hook se type par `Parameters<Hook<'agent.spawn'>>[0]` : le moteur n'exporte pas de
   type nommé pour lui. » C'est faux. `index.d.ts` déclare `export interface EngineInterface`
   (l. 4401), qui est le `$` de tout événement sauf `engine.create` (`Events`, l. 4716). L'en-tête
   des types donne lui-même `import type { Register, On, EngineInterface } from 'claude-code'`.
   Sur une copie du mod, `type Moteur = EngineInterface` passe `tsc` et les 7 tests.
2. « `$.session.append` à `agent.spawn` ou `SubagentStart` : refusé, « no running loop » ». Appelé
   après `next(e)` avec l'`agentId` rendu, il est accepté, et la ligne arrive dans la conversation
   du sous-agent avant sa première requête, en avant-plan comme en arrière-plan. Avant `next`, il
   n'existe pas encore d'`agentId` à nommer. Le constat ne vaut donc que pour ce moment-là, et ne
   le dit pas. Le commentaire de `register.ts` (« refusé à ce moment ») date du Chantier
   `lexique-des-sous-agents` et reste défendable.
3. « `agent.spawn` ne voit que son `prompt` : c'est la seule voie pour verser du contexte à un
   sous-agent ». C'est faux, au vu du point 2.
4. « `prompt.compose` se déclenche à chaque requête ». Ce n'est pas ce qu'on observe (R10).

Ce n'est pas sans effet : ce fichier est fait pour être chargé avant d'écrire un mod, et les
points 2 et 3 y ferment une voie qui existe. L'« Entretenir ce fichier » du Shadow-skill demande
qu'un constat démenti soit remplacé.

**R14 — Le reste se vérifie, et des limites manquent.** Confirmés à l'exécution :

- le chargement par `CLAUDE_CODE_PLUGIN_DIRS` (`claude -p` compris) et par `--plugin-dir` ;
- les trois fichiers d'un mod, et les types écrits à son premier chargement ;
- `tsc` absent, et le recours à `npx` ;
- la survie de la section à `/clear`, `/compact` et `--continue`, sans duplication, sans plafond,
  hors des sous-agents ;
- l'absence de `session.append` dans le banc, et le test vert malgré tout ;
- le module rechargé à chaque test ;
- les 3 s d'attente sans `< /dev/null` ;
- `/clear` et `/compact` envoyés en `stream-json`.

« L'`id` d'un plugin s'écrit `<plugin>:<nom>` » vient des types, et le moteur l'accepte. Manquent
les limites établies ici :

- le prompt enregistré, réutilisé à la reprise jusqu'à la compaction (R5) ;
- la disparition de la section sous `--system-prompt` (R4) ;
- le refus du module sous `--bare`, même avec `--plugin-dir` (R6) ;
- un helper qui reçoit `$` doit être déclaré au niveau du fichier, sinon `validate` et le
  chargement échouent, constaté en écrivant la sonde.

« Non essayé » cite encore `--bare` et le style de sortie, qui ont désormais un résultat.

**R15 — Conformité aux conventions.**

- `gabarit check` le dit conforme, et le tag `mods` est enregistré et trouvé par
  `shadow-skill cherche`.
- `uvx rumdl fmt --check` le refuse (MD041). C'est le seul des quatre Shadow-skills sans titre de
  niveau 1 sous le front matter, et `rumdl fmt` ne sait pas le corriger. Je ne le compte pas comme
  une commande de vérification en échec bloquante : la même commande échoue déjà sur la base
  (`531fa82` : 20 issues dans 12 fichiers). Mais c'est un écart neuf, et propre à ce fichier.
- Sa `description` ne dit pas ce qu'il ne fait pas (« La description dit quoi, quand, et ce que la
  skill ne fait pas »).
- Le raisonnement « `prompt.context` arrive aux sous-agents, `$.session.append` se perd à
  `/clear` » est écrit trois fois : commentaire de `register.ts`, `SKILL.md` (« Deux autres voies
  ne conviennent pas ») et le Shadow-skill. Cela va contre « une règle, un seul endroit ».

### Dette induite

**R16 — `Moteur` est toujours tiré d'`agent.spawn` (R10 (1er), R11 (2e)).** Il y a désormais une
correction directe, établie : `EngineInterface`, exporté (R13, point 1). Le commentaire ajouté,
« Le `$` d'un hook, tel que tous les hooks du mod le reçoivent », décrit exactement ce type.

**R17 — Rien ne signale un mod non chargé (R6 (1er), non traité sciemment).**
`scripts/sante_skills.py` ne contrôle ni le mod ni `CLAUDE_CODE_PLUGIN_DIRS`. Seul `--bare` fait
écrire au moteur un message, sur stderr. Si `CLAUDE_CODE_PLUGIN_DIRS` manque, le mod est inconnu
du moteur, et il ne peut rien en dire. R4 et R5 rangent deux modes de plus parmi ceux où le lexique
manque en silence.

**R18 — `hook-sante-chemin-home.md` décrit un état révolu (R11 (1er), non traité sciemment).**
L'entrée compte toujours « deux hooks `SessionStart` (`sante_skills.py`, `lexique-cli.py session`)
», alors que `settings.json` n'en porte plus qu'un. Elle est à reprendre à sa prochaine revue.

### Suivi des constats des passages précédents

| Constat | État | Ce passage |
|---|---|---|
| R1 (1er) — critère atteint, réserve (interactif, `/clear`, compaction) | **traité** pour `/clear` et `/compact` ; interactif et compaction automatique toujours non essayés | R1, R2, R7 |
| R2 (1er) — second membre du « Pour solder » | **toujours ouvert** (interprétation) | R8 |
| R3 (1er) — `lexiqueLocal` chez l'isolé | **traité**, revérifié | R3 |
| R4 (1er) — local en double chez le non-isolé | **traité**, revérifié (×1 sur transcription) | R3 |
| R5 (1er) — texte contraire au code | **traité** pour les sous-agents ; « une fois » et « dès la suivante » restent trop larges | R5, R9 |
| R6 (1er) — rien ne signale un mod non chargé | **non traité**, sciemment | R17 |
| R7 (1er) — refactor fidèle | **toujours valable** : `lancer` garde le `try` et la ligne d'état | R9 |
| R8 (1er) — commentaires et métadonnées | **traité**, hors nom du mod (sciemment) | R12 |
| R9 (1er) — tests | **traité** : la composition est testée sur ce qu'elle rend | R11 |
| R10 (1er) — `Moteur` tiré d'`agent.spawn` | **toujours ouvert**, correction disponible | R16 |
| R11 (1er) — `hook-sante-chemin-home.md` | **non traité**, sciemment | R18 |
| R12 (1er) — rapport dans le Registre | **traité** : 85 conformes | — |
| R1 (2e) — BLOQUANT, lexique perdu à `/clear` et à la compaction | **traité**, vérifié | R2 |
| R2 (2e) — critère atteint au démarrage | **toujours valable** | R1 |
| R3 (2e) — une copie par reprise | **traité** : aucune ligne ajoutée à `--resume` ni à `--continue` | R2 |
| R4 (2e) — second membre du « Pour solder » | **toujours ouvert** | R8 |
| R5 (2e) — contrat des sous-agents | **toujours valable** | R3 |
| R6 (2e) — cas non essayés | **en partie traité** : rechargement et `session.start` sans objet ; `fork`, interactif, compaction automatique ouverts | R7 |
| R7 (2e) — nominal de `session.start` sur un hook sauté | **traité** : voie abandonnée, tests de composition qui observent | R11 |
| R8 (2e) — ajout hors du `try` | **traité** : plus d'ajout ; `lancer` porte le seul `try` | R9 |
| R9 (2e) — `lexique sous-agent`, type commençant par `-` | **toujours valable**, négligeable | — |
| R10 (2e) — restes de texte | **en partie traité** : « hook » corrigé dans `lexique-cli.py`, `DEMARRAGE` retiré ; enroulements de `register.ts` l. 12-13 et `SKILL.md` l. 141-142 restants | R12 |
| R11 (2e) — `Moteur` | **toujours ouvert** | R16 |

### Ce qui interdit le solde

Aucun bloquant. L'utilisateur doit connaître avant de solder :

- R4 : régression sous `--system-prompt` ;
- R5 : une conversation reprise garde son prompt enregistré, sans lexique s'il n'y était pas ;
- R13 : quatre affirmations du Shadow-skill démenties, dont deux qui ferment une voie existante ;
- R8 : interprétation du « Pour solder » ;
- R17 : aucun signal si le mod ne se charge pas.
