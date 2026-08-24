# Réécriture du garde-fou de pipeline en Python

Brief : `.claude/implementation/check-pipeline-python.brief.md` (validé le 2026-08-23).

## Contexte

`scripts/check-pipeline.sh` est le garde-fou mécanique du pipeline de skills : six contrôles,
échec fermé, lancé en tête de chaque clôture de chantier (`cloture.md:14`). Il est en bash, donc
hors de portée du typage statique qui couvre le reste du code du dépôt, et il n'a **aucun test** —
sa fidélité n'a jamais été établie que par des injections manuelles recopiées en prose dans les
rapports d'audit.

Cinq entrées du registre de dette le visent ou le bordent, dont une **aggravée**. Toutes se soldent
par du code, et toutes sont plus faciles à écrire en Python qu'en bash : slugification correcte,
comptage d'occurrences, échappement d'un chemin dans un motif, correspondance empreinte↔section.

L'objectif : réécrire le garde-fou **et** `impl-list.sh` en Python, les couvrir par
`pyrightconfig.json` et par une suite de tests rejouable, et solder les cinq dettes au passage.

## Décisions de conception

**Deux scripts, pas un paquet.** `scripts/check_pipeline.py` et
`skills/implementation-tracker/scripts/impl_list.py`, chacun autonome. Le signal de dérive du brief
est explicite : pas de couches, pas de `Result[T]`, pas de modules par responsabilité — `listdir`
est un précédent de style, pas d'architecture.

**`impl_list.py` reste dans la skill** (arbitré, réserve `Q2` de la relecture) : la skill s'installe
et s'invoque depuis n'importe quel dépôt, elle ne peut pas dépendre d'un `scripts/` qui n'existe que
dans celui-ci. Ses trois lignes d'appel ne changent donc que d'interpréteur, conformément au signal
de dérive.

**Nommage en underscore** (arbitré) : les unitaires importent les fonctions de contrôle, ce qu'un
nom à tiret interdit. Écart assumé à la lettre du brief, à consigner au journal du suivi.

**Collecte / jugement séparés** — c'est ce qui rend chaque contrôle testable :

```python
@dataclass(frozen=True)
class Finding:
    ok: bool
    message: str

def check_anchors(root: Path) -> list[Finding]: ...
```

Chaque contrôle est une fonction **pure** prenant la racine du dépôt en paramètre et rendant des
`Finding`. Aucune ne lit `sys.argv`, aucune n'imprime, aucune n'appelle `exit`. `main()` les
enchaîne, affiche, et somme les `ok=False` en code de sortie. Un unitaire se réduit alors à monter
une arborescence dans `tmp_path` et à appeler la fonction.

**La règle « un contrôle qui n'examine rien échoue » devient structurelle** : chaque contrôle rend
un `Finding(ok=False)` explicite quand sa population d'entrée est vide, jamais une liste vide. `main`
tient l'autre moitié de la garde — un contrôle qui ne rend **aucun** constat est compté rouge.

**Deux points fixés à l'écriture du contrôle 1** (étape 3) :

- `slugify()` garde les lettres accentuées et ne retire que la ponctuation
  (`c.isalnum() or c in " -_"`, puis espaces→tirets) : c'est la règle GitHub, et
  `#format-détape-et-délégabilité` doit continuer de résoudre.
- le motif de renvoi est `\]\(([^)#]*contrat\.md)#([^)]*)\)` — il n'accepte que de **vrais liens
  markdown**, ce qui écarte d'office les citations en prose sans avoir à exclure quoi que ce soit.

**`impl_list.py` est importé, pas sous-processé.** Les contrôles 3 et 5 chargent
`<racine>/skills/implementation-tracker/scripts/impl_list.py` par `importlib` et appellent
`suivis()` — c'est le même code que la CLI, donc les deux ne peuvent pas diverger, et c'est bien la
copie **du dépôt audité** qui est jugée, comme le fait déjà `LISTER` aujourd'hui. Script absent →
contrôle rouge, comme aujourd'hui.

**Les unitaires s'écrivent avec leur contrôle** (arbitré, réserve `Q3`) : chaque étape livre une
fonction de contrôle et ses tests, et sa vérification est donc réellement exécutable au moment où
elle est posée. Il n'y a pas d'étape « tests » séparée, seulement le bout-en-bout final.

## Les sept contrôles et les dettes qu'ils soldent

| # | Contrôle | Ce qui change |
|---|---|---|
| 1 | Renvois vers le contrat | **Portée étendue** : tout le dépôt sauf `agents/`, `.git/`, `plugins/`, `.claude/implementation/` (arbitré : les archives et le registre portent des renvois volontairement morts). L'extension est **invisible sur l'arbre actuel** — 30 renvois avant comme après — donc elle se prouve par un unitaire qui injecte un renvoi mort dans `CLAUDE.md` et dans `hooks/` (réserve `Q4`). **`slugify()` complète** : minuscules, ponctuation retirée, espaces→tirets. **L'auto-citation du contrat ne compte plus** pour « section jamais citée » |
| 2 | Règles définies à un seul endroit | **Comptage d'occurrences**, non de fichiers — deux copies dans un même fichier deviennent rouges. **Table `{ancre-de-section: [empreintes]}`** : une section du contrat sans empreinte est rouge (`## Dépendances` est aujourd'hui dans ce cas, empreinte candidate : « elle ne se suppose pas ») |
| 3 | Filtre de listing | Appelle `impl_list.suivis()` |
| 4 | Indépendance des sous-agents | Inchangé |
| 5 | Chemins du frontmatter des archives | Inchangé |
| 6 | Portabilité des appels de script | **Le garde doit commander l'appel** (`if [ -f X ]; then … X`), pas seulement figurer sur la ligne ; **`re.escape` sur le chemin**, dont les `.` étaient des métacaractères |
| 7 | **Nouveau** — existence des chemins de skill | Chaque `$HOME/.claude/skills/…` cité dans un `.md` désigne un fichier existant. Solde le symptôme de `chemin-skill-code-en-dur` ; la cause reste au registre |

Dettes soldées hors contrôles : `impl-list-extension-gnu-find` (le `find -printf` GNU disparaît avec
bash), `deux-renvois-non-navigables` (en-tête d'`impl_list.py` corrigé en `../references/contrat.md`,
renvoi de `agents/implementation-auditor.md:95` ancré en `#gabarit-du-rapport`).

## Étapes

Chaque étape de contrôle livre **la fonction et ses unitaires ensemble** ; les tests vivent sous
`scripts/tests/`, créés par l'étape 3 avec le premier contrôle.

- [ ] 1. `skills/implementation-tracker/scripts/impl_list.py` — `suivis(dir: Path) -> list[str]`
  + CLI, en-tête repris du `.sh` avec son chemin de renvoi **corrigé** en `../references/contrat.md`
  — vérif: sortie identique à `bash "$HOME/.claude/skills/implementation-tracker/scripts/impl-list.sh" <dir>`
  sur `.claude/implementation/todo`, `.claude/implementation/done`, et sur un répertoire absent
  (message sur stderr, sortie vide, code 0)
- [ ] 2. Squelette de `scripts/check_pipeline.py` — `Finding`, registre des contrôles, `main()`,
  résolution de la racine par `git rev-parse --show-toplevel` — vérif: `python3 scripts/check_pipeline.py`
  s'exécute, annonce 0 contrôle exécuté et sort en code ≠ 0
- [ ] 3. Contrôle 1 + `scripts/tests/` — `slugify()` complète, portée étendue, fin de l'auto-citation
  — vérif: `uvx pytest scripts/tests -q` vert, **dont** un cas qui injecte un renvoi mort dans
  `CLAUDE.md` et dans `hooks/` (preuve de la portée étendue, réserve `Q4`) ; sur le dépôt réel,
  30 renvois résolvent
- [ ] 4. Contrôle 2 — comptage d'occurrences, table `{section: [empreintes]}`, empreinte ajoutée
  pour `## Dépendances` (« elle ne se suppose pas », `contrat.md:238`) — vérif: unitaires verts,
  dont « section sans empreinte → rouge » ; sur le dépôt réel, 8 sections couvertes, aucune
  empreinte à 0 ni ≥ 2
- [ ] 5. Contrôle 3 — chargement d'`impl_list.py` par `importlib` — vérif: unitaires verts, dont
  « listing vide → rouge » et « script absent → rouge »
- [ ] 6. Contrôle 4 — vérif: unitaires verts, dont « répertoire `agents/` absent → rouge »
- [ ] 7. Contrôle 5 — vérif: unitaires verts, dont « champ pointant dans le vide → rouge »
- [ ] 8. Contrôle 6 — garde qui **commande** l'appel, `re.escape` sur le chemin — vérif: les 4 formes
  fautives historiques détectées, les 5 écritures absolues légitimes acceptées, et le faux positif
  `bash x.sh  # [ -f x.sh ]` désormais rouge
- [ ] 9. Contrôle 7 — vérif: un `$HOME/.claude/skills/inexistant.md` injecté dans un `.md` → rouge ;
  sur le dépôt réel, les 5 chemins existants → vert
- [ ] 10. Test bout-en-bout par injection : arborescence-jouet en `tmp_path`, un défaut par contrôle,
  plus un arbre sain — vérif: 7 rouges attendus, 1 vert, code de sortie 1 puis 0
- [ ] 11. Bascule des appels et suppression des deux `.sh` — `cloture.md:14`,
  `implementation-tracker/SKILL.md:42,:75`, `references/contrat.md:202` — vérif: plus aucune mention
  de `check-pipeline.sh` ni d'`impl-list.sh` hors archives ; contrôle 6 vert sur les nouveaux appels
- [ ] 12. `pyrightconfig.json` : `"scripts"` ajouté à `include` — vérif: `uvx basedpyright` → 0 erreur,
  `uvx ruff check scripts skills/implementation-tracker` → clean
- [ ] 13. Dettes annexes : ancrage du renvoi dans `agents/implementation-auditor.md:95`, suppression
  du `scripts/__pycache__/migrate-dette.cpython-314.pyc` orphelin — vérif: contrôle 4 toujours vert
  (le renvoi vise `audit.md`, pas `contrat.md`) **et** `ls scripts/__pycache__` → absent ou vide,
  `git status --short` ne montrant aucun `.pyc` suivi
- [ ] 14. Registre de dette (réserve `Q5`) : les **quatre** entrées entièrement traitées migrent en
  `technical-debt-solde/` ; `chemin-skill-code-en-dur` **reste ouverte**, son constat réécrit pour ne
  garder que la cause — vérif: `list-dir.py validate` vert sur `technical-debt` **et** sur
  `technical-debt-solde`

## Vérification d'ensemble

```bash
python3 scripts/check_pipeline.py        # → Pipeline conforme., 7 contrôles verts, code 0
uvx pytest scripts/tests -q              # → tout vert
uvx basedpyright                         # → 0 erreur
uvx ruff check scripts skills/implementation-tracker       # → clean (listdir est hors-périmètre)
python3 "$HOME/.claude/skills/implementation-tracker/scripts/impl_list.py" \
        .claude/implementation/done                        # → 6 suivis, aucun brief/audit/plan
```

Puis, garde-fou du garde-fou : injecter un défaut par contrôle dans une copie du dépôt et vérifier
que chacun crie — c'est ce que l'étape 9 fige, mais le rejouer une fois à la main sur l'arbre réel
est la seule preuve que les tests testent le bon objet.
