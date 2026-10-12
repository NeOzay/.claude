# Plan — affiner-session-dump

## Relecture

```
VERDICT : NON CONFORME
CRITÈRES :
C1 (« `session-dump`, lancé sur ce dépôt, n'écrit aucun dump de session `sdk-cli` ni de session à moins de 2 tours et moins de 10 000 tokens ; sa sortie compte les écartées par motif ») → Étape 3 (motif_d_ecart, Bilan par motif, sortie CLI), Étape 4 (lancement sur le dépôt) — contrôle sur le dépôt incomplet, voir Q3
C2 (« le dump d'une session à sous-agents porte une entrée par lancement et une par famille, chacune avec les champs de `[tokens]` ; le total d'une famille égale la somme de ses lancements ») → Étapes 1 (SousAgent, familles) et 2 (rendu, relu par tomllib)
C3 (« Sur l'ensemble des dumps, le nombre de lancements par famille égale celui des `*.meta.json` qui portent cet `agentType` ») → servi seulement sous une lecture restreinte que le plan ne signale pas (« des sessions dumpées ») ; pris à la lettre, NON SERVI et impossible à tenir avec C1 — voir Q1
C4 (« `SKILL.md`, « Ce qu'elle écrit », décrit les tables des sous-agents et les règles d'écart ») → Étape 4
C5 (« `pytest skills/session-dump/scripts/tests/`, `ruff` et `basedpyright` passent, selon `OUTILLAGE.md` ») → vérif des Étapes 1 à 4, section Vérification
HORS-PÉRIMÈTRE : RESPECTÉ
DÉRIVE : aucun
INCERTITUDES : forme TOML des deux niveaux (noms des tables, clé d'un lancement) → section « Forme du frontmatter », mise en œuvre à l'Étape 2
MODÈLE : sonnet → SOUTENU — travail de code bien délimité, vérifiable par tests, l'unique incertitude tranchée, 4 Étapes, très peu de prose (SKILL.md)
QUALITÉ :
Q1 — C3 réinterprété sans le dire : 4 sessions `sdk-cli` (033ef9ca, be912874, e335c7fb, f070f2ee) portent chacune un sous-agent `lexique-test-isole` qui sera écarté avec elles ; C3 lu à la lettre (tous les `*.meta.json`) est incompatible avec C1. Le plan restreint la comparaison aux « sessions dumpées » sans signaler l'écart au brief — à faire ratifier par l'utilisateur.
Q2 — Étape 3 : la fixture `monde` de `tests/test_cli.py` (l. 29-38) pose des sessions à 1 tour et 0 token, que la nouvelle règle écarte comme « trop-courte » ; cela casse au moins `test_dumper_ecrit_un_dump_par_session_avec_tour` (l. 57, qui attend aussi `ecartes` entier), `test_la_commande_sans_argument_prend_le_repertoire_courant` (l. 185, ancien libellé « sans tour ») et les tests qui comptent sur des dumps écrits. Le plan ne prévoit pas de refaire la fixture.
Q3 — Le contrôle de C1 sur le dépôt ne vérifie que la moitié `sdk-cli` ; aucune commande ne vérifie qu'aucun dump n'a `tours < 2` et `[tokens].total < 10 000`.
Q4 — Le script de contrôle de C2/C3 n'est que décrit (« un script `python3 -I` qui… ») : la session d'exécution devra l'inventer, et rien ne garantit qu'il compare ce qu'il faut.
Q5 — Contrôle de S3 « sur un dump d'avant (sur `master`) et d'après » : le plan ne dit pas comment obtenir le dump d'avant, alors que `remplacer` écrase le répertoire (OUTILLAGE prescrit `git archive <base>`).
Q6 — La vérif de l'Étape 4 ne lance que ruff et basedpyright ; elle omet pytest, le formatage Markdown de `SKILL.md` (`uvx rumdl fmt`, OUTILLAGE) et les contrôles C1–C3 que l'Étape annonce.
Q7 — Étape 1 : `Session` gagne `sous_agents` (puis `entrypoint` à l'Étape 3) sans défaut annoncé ; le helper `session()` de `tests/test_rendu.py` (l. 13-26) construit une `Session` champ par champ et casserait, alors que `test_rendu.py` n'est pas dans les fichiers de l'Étape 1.
Q8 — « `.meta.json` absent ou illisible : … et un illisible compté » ne dit pas si un `.meta.json` absent compte aussi comme illisible, ce qui change `Bilan.illisibles` et le message stderr.
```

**Q1** — Réponse de l'utilisateur : restreindre aux sessions dumpées. C3 se lit sur les
`*.meta.json` des sessions dumpées seulement ; les sous-agents d'une session écartée n'entrent
dans aucun dump.

**Q8** — Réponse de l'utilisateur : non. Un `.meta.json` absent donne `famille = "?"` sans
signalement ; seul un `.meta.json` présent mais illisible est compté en illisible.

**Q2 à Q7** — Défauts de rédaction, corrigés sans arbitrage : fixture `monde` et libellés des
tests à l'Étape 3 (Q2) ; script de contrôle C1–C3 écrit en entier (Q3, Q4) ; procédure du dump
d'avant pour S3 (Q5) ; vérif complète à l'Étape 4 (Q6) ; champs neufs de `Session` avec défaut
(Q7).

## Contexte

Brief : `.claude/implementation/affiner-session-dump.brief.md` (validé). Entrée de road-map :
`session-dump-sous-agents-et-sessions-de-test`.

Mesurer le poids des audits a demandé de relire les transcriptions brutes des sous-agents, et les
sessions lancées par `claude -p` se mêlent aux discussions dans le répertoire de dumps. Le
Chantier ajoute au frontmatter de chaque dump les tokens de ses sous-agents, par lancement et par
famille, et écarte du dump les sessions `claude -p` et les sessions vides.

Rappels du brief :

- **Critères** : C1 (écarts et sortie par motif), C2 (deux niveaux, champs de `[tokens]`, total de
  famille = somme des lancements), C3 (lancements par famille = `*.meta.json`), C4 (`SKILL.md`),
  C5 (pytest, ruff, basedpyright).
- **Hors-périmètre** : analyse des dumps ; dump des transcriptions des sous-agents ; coût par
  sous-agent.
- **Signaux de dérive** : S1 critère d'écart autre ; S2 coût ou table de prix ; S3 `[tokens]` d'une
  session à `cost-state` modifié ; S4 corps du dump modifié ; S5 interprétation du contenu.
- **Incertitude reportée** : la forme TOML des deux niveaux — tranchée ci-dessous, en
  « Forme du frontmatter ».

## Modèle

**Sonnet** : du code Python bien délimité, vérifié par des tests, l'unique incertitude du brief
tranchée ici, quatre Étapes.

## Shadow-skills

`skill-convention` (code Python de la skill, prose de `SKILL.md`).

## Faits relevés

- `skills/session-dump/scripts/session_dump.py` : `analyser_lignes` lit les transcriptions
  `<uuid>/subagents/*.jsonl` seulement sans `cost-state` ; `tokens_transcriptions` dédoublonne par
  `message.id` ; `dumper` écarte les sessions à 0 tour et compte un seul `ecartes`.
- `skills/session-dump/scripts/session-dump-cli.py` affiche `N session(s) sans tour écartée(s)`.
- Chaque `agent-<id>.jsonl` a son `agent-<id>.meta.json` : `agentType`, `description`,
  `spawnDepth` (81 lancements, tous à `spawnDepth` 1, tous dans `<uuid>/subagents/`).
- `entrypoint` est porté par la plupart des lignes d'une session (`"cli"` ou `"sdk-cli"`), pas par
  les premières (`queue-operation`).
- Tests : `skills/session-dump/scripts/tests/` — `test_lecture.py`, `test_rendu.py`,
  `test_cli.py`, fixture `ecrire_jsonl` dans `conftest.py`.
- Aucun consommateur dans `~/.config/nvim/` (`grep -r session-dump` vide).

## Forme du frontmatter

Après `[tokens]` et `[duree]`, seulement si la session a des sous-agents :

```toml
[familles_sous_agents."implementation-auditor"]
lancements = 2
total = 3_400_000
entree = 1_200
sortie = 40_000
cache_lu = 3_200_000
cache_cree = 158_800

[[sous_agents]]
id = "a01b39b9324eec1fe"
famille = "implementation-auditor"
description = "Audit de clôture"
total = 1_700_000
entree = 600
sortie = 20_000
cache_lu = 1_600_000
cache_cree = 79_400
```

- Clé de famille : l'`agentType`, toujours entre guillemets par `chaine_toml` (un type de plugin
  porte `:`). Familles par ordre alphabétique ; lancements par date de leur première ligne, puis
  par `id` — un ordre fixe, aucun classement.
- `id` : le nom du fichier sans `agent-` ni `.jsonl`. `.meta.json` absent, illisible ou sans
  `agentType` : `famille = "?"` (comme `ligne_outil`), pas de `description`. Seul un `.meta.json`
  présent mais illisible compte un illisible (Q8).
- Mêmes noms de champs que `[tokens]`, à plat : `total`, `entree`, `sortie`, `cache_lu`,
  `cache_cree`. Aucun coût (hors-périmètre, S2).

## Étapes

### 1. Lire les sous-agents

Fichiers : `session_dump.py`, `tests/test_lecture.py`.

- `@dataclass(frozen=True) class SousAgent` : `id`, `famille`, `description: str | None`,
  `debut: datetime | None`, `tokens: Tokens`.
- `lire_sous_agents(repertoire: Path) -> tuple[list[SousAgent], int]` : lit chaque
  `agent-*.jsonl` de `repertoire` et son `.meta.json`, réutilise `lire_jsonl`,
  `tokens_transcriptions`, `creation`, `chaine` ; rend aussi les illisibles.
- `Session` gagne `sous_agents: tuple[SousAgent, ...] = ()`, en dernier champ, avec défaut : le
  helper `session()` de `tests/test_rendu.py` reste valide (Q7). `analyser_lignes` appelle
  `lire_sous_agents` une fois ; sans `cost-state`, le total de la session devient
  `tokens_transcriptions(lignes)` + la somme des `SousAgent.tokens` — même résultat qu'avant. Avec
  `cost-state`, `tokens` ne change pas (S3).
- Fonction pure `familles(sous_agents) -> dict[str, tuple[int, Tokens]]` : nombre de lancements et
  somme des tokens par famille.
- Tests : meta présent / absent / illisible ; un message éclaté compté une fois ; total de famille
  = somme ; `[tokens]` d'une session à `cost-state` inchangé quand elle a des sous-agents ;
  `test_analyser_sans_cost_state_somme_les_transcriptions` passe sans modification.

vérif: `~/.claude/.venv/bin/python -m pytest skills/session-dump/scripts/tests/`

### 2. Rendre les sous-agents au frontmatter

Fichiers : `session_dump.py` (`rendre_frontmatter`), `tests/test_rendu.py`.

- Ajoute les tables de « Forme du frontmatter » après `[duree]`, nombres en `{:_}` comme le reste.
  Session sans sous-agent : aucune table, frontmatter identique à aujourd'hui.
- `rendre_corps` n'est pas touché (S4).
- Tests : relu par `tomllib`, deux familles et trois lancements ; une famille à `:` et une
  description à guillemets ; ordre des familles et des lancements ; sans sous-agent, aucune clé
  `sous_agents` ni `familles_sous_agents` ; total de famille = somme des lancements relus.

vérif: `~/.claude/.venv/bin/python -m pytest skills/session-dump/scripts/tests/`

### 3. Écarter par motif

Fichiers : `session_dump.py` (`Session`, `dumper`, `Bilan`), `session-dump-cli.py`,
`tests/test_cli.py`, `tests/test_lecture.py`.

- `Session` gagne `entrypoint: str | None = None`, en dernier champ : la valeur de la première
  ligne qui porte le champ.
- Constantes, définies une seule fois, avec leur motif en commentaire : `ENTREE_SDK = "sdk-cli"`,
  `TOURS_MIN = 2`, `TOKENS_MIN = 10_000`.
- `type Motif = Literal["sans-tour", "claude-p", "trop-courte"]` et fonction pure
  `motif_d_ecart(session) -> Motif | None`, dans cet ordre : 0 tour ; `entrypoint == "sdk-cli"` ;
  `tours < 2 and tokens.total < 10_000` (le total du frontmatter, sous-agents compris). Aucun autre
  critère (S1).
- `Bilan.ecartes` devient un `Mapping[Motif, int]`. La CLI écrit une ligne par motif non nul :
  `session-dump : N session(s) écartée(s) — sans tour` / `— lancée(s) par claude -p` /
  `— moins de 2 tours et de 10 000 tokens`.
- Tests : chaque motif, la limite (2 tours ou 10 000 tokens : gardée), la priorité des motifs, la
  sortie de la commande par motif.
- Tests existants (Q2) : `session_jsonl` de `tests/test_cli.py` pose aujourd'hui des sessions à
  1 tour et 0 token, que la règle écarte. Elle reçoit un second tour, pour que la fixture `monde`
  garde deux sessions dumpées ; `test_dumper_ecrit_un_dump_par_session_avec_tour` attend
  `ecartes == {"sans-tour": 1}` ; `test_la_commande_sans_argument_prend_le_repertoire_courant`
  attend le nouveau libellé.

vérif: `~/.claude/.venv/bin/python -m pytest skills/session-dump/scripts/tests/`

### 4. Documenter et vérifier sur le dépôt

Fichiers : `skills/session-dump/SKILL.md` (« Ce qu'elle écrit »), docstring du module
`session_dump.py` (`PORTÉE`, `TOKENS`).

- `SKILL.md` : les tables des sous-agents (deux niveaux, d'où viennent leurs tokens, pas de coût) ;
  les trois motifs d'écart et la sortie par motif, à la place du paragraphe sur les sessions sans
  tour.
- Docstring : les sous-agents lus dans tous les cas, leurs tokens depuis leurs transcriptions.
- Lancer `session-dump` sur ce dépôt, puis le contrôle C1–C3 et le contrôle S3 (Vérification).

vérif: toute la section Vérification ci-dessous (C1 à C5, S3).

## Vérification

`$S` désigne le scratchpad de la session qui exécute ; tout se lance depuis la racine du dépôt.

- **C5** — `~/.claude/.venv/bin/python -m pytest skills/session-dump/scripts/tests/`, puis, dans
  `skills/session-dump/` : `uvx ruff check .`, `uvx ruff format --check .`,
  `uvx --with pytest basedpyright` ; et `uvx rumdl fmt --check skills/session-dump/SKILL.md`.
- **S3, le dump d'avant** — avant de lancer la commande neuve, dumper avec la version de la Base,
  puis mettre ce dump de côté (`remplacer` écraserait le répertoire) :

  ```bash
  mkdir -p "$S/avant" && git archive master skills/session-dump | tar -x -C "$S/avant"
  python3 "$S/avant/skills/session-dump/scripts/session-dump-cli.py" .
  rm -rf "$S/dumps-avant" && cp -r .claude/session-dump/-home-debian--claude "$S/dumps-avant"
  session-dump
  ```

- **C1, C2, C3** — `python3 -I "$S/controle.py"`, qui sort 0 et écrit
  `C1, C2, C3 : conformes` :

  ```python
  import json, sys, tomllib
  from collections import Counter
  from pathlib import Path

  sessions = Path.home() / ".claude/projects/-home-debian--claude"
  dumps = Path.home() / ".claude/.claude/session-dump/-home-debian--claude"
  CHAMPS = ("total", "entree", "sortie", "cache_lu", "cache_cree")
  erreurs: list[str] = []
  attendu: Counter[str] = Counter()
  vu: Counter[str] = Counter()
  for dump in sorted(dumps.glob("*.md")):
      fm = tomllib.loads(dump.read_text(encoding="utf-8").split("+++")[1])
      uuid = fm["session"]
      if '"entrypoint":"sdk-cli"' in (sessions / f"{uuid}.jsonl").read_text(encoding="utf-8"):
          erreurs.append(f"C1 sdk-cli dumpée : {dump.name}")
      if fm["tours"] < 2 and fm["tokens"]["total"] < 10_000:
          erreurs.append(f"C1 trop courte dumpée : {dump.name}")
      lancements = fm.get("sous_agents", [])
      familles = fm.get("familles_sous_agents", {})
      if {l["famille"] for l in lancements} != set(familles):
          erreurs.append(f"C2 familles et lancements disjoints : {dump.name}")
      for nom, famille in familles.items():
          siens = [l for l in lancements if l["famille"] == nom]
          if famille["lancements"] != len(siens):
              erreurs.append(f"C2 {nom} : lancements faux dans {dump.name}")
          for champ in CHAMPS:
              if famille[champ] != sum(l[champ] for l in siens):
                  erreurs.append(f"C2 {nom}.{champ} : somme fausse dans {dump.name}")
          vu[nom] += famille["lancements"]
      for meta in (sessions / uuid / "subagents").glob("*.meta.json"):
          attendu[json.loads(meta.read_text(encoding="utf-8")).get("agentType") or "?"] += 1
  if vu != attendu:
      erreurs.append(f"C3 : dumps {dict(vu)} != meta.json {dict(attendu)}")
  print("\n".join(erreurs) or "C1, C2, C3 : conformes")
  sys.exit(1 if erreurs else 0)
  ```

  C3 se lit sur les `*.meta.json` des sessions dumpées (Q1). La sortie de `session-dump` compte les
  écartées par motif (C1, à lire).
- **S3** — `python3 -I "$S/s3.py" "$S/dumps-avant"` : pour chaque session présente avant et après,
  `[tokens]` identique ; au plus une différence, la session en cours.

  ```python
  import sys, tomllib
  from pathlib import Path

  def lire(rep: Path) -> dict[str, dict[str, int]]:
      return {
          fm["session"]: fm["tokens"]
          for fm in (
              tomllib.loads(f.read_text(encoding="utf-8").split("+++")[1])
              for f in rep.glob("*.md")
          )
      }

  avant = lire(Path(sys.argv[1]))
  apres = lire(Path.home() / ".claude/.claude/session-dump/-home-debian--claude")
  ecarts = [u for u in avant.keys() & apres.keys() if avant[u] != apres[u]]
  print(f"S3 : {len(ecarts)} écart(s) {ecarts}")
  sys.exit(1 if len(ecarts) > 1 else 0)
  ```

- **C4** — relecture de `SKILL.md`, « Ce qu'elle écrit ».
