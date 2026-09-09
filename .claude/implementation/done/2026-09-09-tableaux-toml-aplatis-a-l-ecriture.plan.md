# Conserver le format des tableaux TOML à la réécriture

Brief : `.claude/implementation/tableaux-toml-aplatis-a-l-ecriture.brief.md` (validé)
Road-map : `tableaux-toml-aplatis-a-l-ecriture`

## Contexte

`dump_value` (`skills/list-dir/scripts/listdir/items.py:191`) sérialise tout tableau sur une seule
ligne, et refuse tout caractère de contrôle (`items.py:176-181`) — donc pas de chaîne multiligne.
Ces deux limites ne se voient qu'à l'écriture, parce qu'un élément lu reconduit son `raw_front` à
l'octet (`items.py:208`). Mais dès qu'un seul champ change, `with_fields` / `realigned` mettent
`raw_front` à `None` (`types.py:316`, `types.py:329`) et **tout** le front matter est resérialisé.

Conséquence vécue : un ajout de champ au contrat fait passer `migrate` sur tous les éléments, et
aplatit d'un coup des tableaux que quelqu'un avait mis en forme à la main — le diff git mélange
alors la vraie migration et un reformatage massif.

L'en-tête d'`items.py` dit pourquoi ce design existe : « tomllib lit mais n'écrit pas, et la stdlib
n'a aucun écrivain TOML ». **tomlkit supprime cette prémisse.** C'est un parseur préservant : il
conserve commentaires, ordre, guillemets, tableaux et chaînes multilignes, et ne réécrit que ce
qu'on a touché.

Résultat visé : un tableau, une chaîne multiligne ou un commentaire écrits à la main ressortent
identiques après une réécriture qui ne portait pas sur eux.

## Le modèle qui change

Aujourd'hui, une frontière binaire : `raw_front` présent → tout reconduit ; `None` → tout
resérialisé. Demain, **un seul chemin de rendu** : le document d'origine est reparsé, on n'y touche
que les champs qui ont réellement changé, et on le redonne.

```python
def dump_front(fields: Mapping[str, object], raw_front: str | None = None) -> str:
    doc = tomlkit.parse(raw_front) if raw_front else tomlkit.document()
    # 1. retirer du document les clés absentes de `fields` (c'est ce que fait --drop)
    # 2. poser celles dont la valeur diffère — les autres ne sont pas touchées,
    #    donc gardent leur mise en forme
    # 3. réordonner les blocs selon l'ordre de `fields`
    return tomlkit.dumps(doc).strip()
```

`raw_front` cesse d'être « le texte à reconduire » pour devenir « le document sur lequel on
reprojette ». `with_fields` et `realigned` n'ont donc plus à l'effacer.

La surface d'écriture est étroite, ce qui rend le changement tenable : trois constructeurs d'`Item`
(`items.py:149` lecture, `store.py:247` create, `store.py:586` derive), un `realigned`
(`store.py:432`), et tout passe par `write_item` → `render_item`.

## Amorçage : venv dédié

`python3` est celui de Linuxbrew (3.14) et porte `EXTERNALLY-MANAGED` ; `pip install` y est refusé.
Le dépôt n'a ni venv, ni `pyproject.toml`, ni pytest installé. Décision prise avec l'utilisateur :
**venv dédié au dépôt de skills, pytest embarqué dedans.**

- `~/.claude/.venv`, créé par `uv venv` (uv est présent).
- `~/.claude/requirements.txt` versionné : `tomlkit`, `pytest`.
- `list-dir.py` se **ré-exécute** dans le venv s'il n'y tourne pas déjà (`os.execv`), juste après la
  garde de version PEP 695 qui est déjà là et documentée. `bin/` et ses liens ne bougent pas — ce
  que `sante_skills` contrôle déjà reste vrai.
- `sante_skills.py` gagne une anomalie « venv absent » / « dépendance manquante », au même endroit
  que `MIN_PYTHON` (`sante_skills.py:76-80`), avec la commande de réparation dans le message.

C'est un élargissement du périmètre par rapport au brief, assumé : sans lui, rien n'est exécutable.

## Étapes

### 1. Amorcer le venv et le rendre obligatoire

Créer `requirements.txt` (`tomlkit`, `pytest`), le venv (`uv venv ~/.claude/.venv` puis
`~/.claude/.venv/bin/python -m pip install -r ~/.claude/requirements.txt`), et le ré-amorçage dans
`list-dir.py`. Renseigner aussi `venvPath`/`venv` dans `skills/list-dir/pyrightconfig.json`, qui est
en `typeCheckingMode: "all"` et ne trouverait pas tomlkit sans ça.

Vérification :
```bash
list-dir help >/dev/null && echo OK
~/.claude/.venv/bin/python -c "import tomlkit, pytest; print(tomlkit.__version__)"
```

### 2. Contrôler la dépendance dans `sante_skills.py`

Anomalie si `.venv` manque ou si un module de `requirements.txt` n'y est pas. Sans subprocess :
tester la présence du répertoire dans `site-packages` du venv.

Vérification :
```bash
python3 ~/.claude/scripts/sante_skills.py; echo "code $?"          # 0, silencieux
~/.claude/.venv/bin/python -m pytest ~/.claude/scripts/tests/test_sante_skills.py
```

### 3. Prouver tomlkit avant d'écrire quoi que ce soit

Script jetable (scratchpad, non versionné) répondant aux quatre incertitudes du brief :

- un `parse` → `dumps` sans modification rend-il l'octet exact ?
- un commentaire sur sa propre ligne est-il un item distinct de `doc.body` ? Comment le regrouper
  avec la clé qui suit — c'est ce qui décide si « le commentaire suit son champ » est tenable ;
- que devient un commentaire **sans champ derrière lui** (fin de front matter) ?
- `tomlkit.string(v, multiline=True)` et les caractères de contrôle : `\r`, `\b`, `\f`, `\x00` —
  échappés proprement, ou faut-il garder une garde ?

Sortie : les réponses, écrites au journal du suivi. **Aucun fichier du paquet touché.**

Vérification — le script porte ses propres assertions et rend un code de sortie :
```bash
~/.claude/.venv/bin/python "$SCRATCHPAD/preuve_tomlkit.py"; echo "code $?"
```

### 4. `toml_value` et `dump_front` reprojetant (sans réordonnancement)

Dans `items.py` : `toml_value(value, key)` rend un item tomlkit — garde `SerialiseError` pour un
type hors contrat (c'est une garantie du paquet, le message nomme le type), pose
`multiline=True` sur une chaîne contenant un saut de ligne, récursivement dans les listes.
`dump_front` prend `raw_front` et reprojette. `render_item` n'a plus de `if`.

Vérification :
```bash
~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/test_items.py
~/.claude/.venv/bin/python -m pyright skills/list-dir 2>/dev/null || npx pyright skills/list-dir
```

### 5. Réordonner les blocs, commentaire compris

Reconstruire le document dans l'ordre de `fields` en déplaçant chaque clé **avec les commentaires
qui la précèdent**. C'est ce que `migrate` fait déjà (`_reordering`, `store.py:410-418`), qui doit
continuer à marcher — mais sans reformater.

Le test qui prouve cette étape (« un commentaire posé au-dessus d'un champ suit ce champ quand le
contrat le réordonne ») est écrit **ici**, pas repoussé à l'étape 7 : sans lui, l'étape passerait au
vert sans avoir démontré ce qu'elle produit.

Vérification :
```bash
~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/test_store_ecriture.py \
    skills/list-dir/scripts/tests/test_items.py
```

### 6. Retirer la frontière et réécrire ce qui la documente

`with_fields` et `realigned` cessent d'effacer `raw_front` (`types.py:316`, `types.py:329`). Puis
les textes qui affirment le contraire, et qui deviendraient faux :

- l'en-tête d'`items.py:1-17` (« DEUX RÈGLES, ET LEUR FRONTIÈRE ») ;
- le docstring d'`Item` (`types.py:291-298`) ;
- l'effet de bord annoncé par `migrate` : « D'éventuels commentaires TOML écrits à la main y
  disparaissent — le contrat est l'autorité, pas la mise en page » (`store.py:269-271`) ;
- `skills/list-dir/references/operations.md:62`.

Vérification :
```bash
~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/
```

### 7. Tests de bout en bout de la préservation

Un test par critère du brief : tableau multiligne intact après un `migrate` qui ajoute un champ ;
entrée contenant un saut de ligne écrite en `"""…"""` ; commentaire qui suit son champ quand le
contrat réordonne.

Vérification :
```bash
~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/
```

## À trancher avant de commencer

**Cinq tests existants deviendront faux, et c'est l'objet du chantier — pas un relâchement.** Le
brief pose « si un test existant est modifié plutôt qu'ajouté, s'arrêter » comme signal de dérive :
il se déclenche dès **l'étape 4**, dont la vérification part au rouge. Aucune étape de 4 à 6 ne peut
donc conclure tant que l'arbitrage n'est pas rendu.

Sur la frontière `raw_front` :
- `tests/test_items.py:172-183` — `test_un_champ_modifie_declenche_la_reserialisation`, dont le
  docstring dit « LA FRONTIÈRE : with_fields met raw_front à None, et c'est le seul commutateur ».
  Ses trois assertions s'inversent, dont `"# un commentaire" not in modifie.render()`.
- `tests/test_items.py:195-205` — `test_realigned_reserialise_et_remplace`, pour son
  `aligne.raw_front is None`. Le reste du test (remplacer, retirer) doit continuer à passer.

Sur le sérialiseur, **si et seulement si `dump_value` est refondu** (cf. « Le sort de `dump_value` »
ci-dessous) :
- `tests/test_items.py:241-244` — `test_echappements_relisibles` attend `dump_value("a\nb", "x")
  == '"a\\nb"'`, l'inverse exact du critère « saut de ligne → `"""…"""` » ;
- `tests/test_items.py:247-252` — `test_caractere_de_controle_refuse_et_nomme` attend
  `SerialiseError` sur `\x00` ;
- `tests/test_items.py:261-262` — `test_dump_front_conserve_l_ordre` appelle `dump_front` avec
  l'ancienne signature.

`tests/test_move.py:103` (`raw_front is not None`) reste vrai, lui.

## Le sort de `dump_value` — non tranché

`dump_value` n'est pas propre au front matter des éléments. Il écrit aussi **le contrat** dans
`init_list` (`store.py:802-803`) et **la semence** (`provenance.py:431`, import en
`provenance.py:45`). Le brief pose ces deux zones en signal de dérive.

Le plan ci-dessus introduit `toml_value` sans dire si `dump_value` survit à côté. Deux issues, et
c'est un arbitrage, pas un détail :

- **le garder intact**, et ne faire passer que `dump_front`/`render_item` par tomlkit. Contrats et
  semences ne bougent pas, les trois tests du sérialiseur restent vrais — mais le paquet porte deux
  écrivains TOML ;
- **le refondre**, et alors le diff touche l'écriture des contrats et `provenance.py` : le signal de
  dérive tombe.

## Risque principal

L'étape 3 peut invalider l'approche : si tomlkit n'attache pas les commentaires autonomes de façon
exploitable, « le commentaire suit son champ » tombe, et il faut revenir vers l'utilisateur — soit
pour renoncer à ce critère, soit pour changer de stratégie de réordonnancement. C'est pour ça
qu'elle vient avant toute écriture dans le paquet.

## Vérification de bout en bout

```bash
~/.claude/.venv/bin/python -m pytest skills/list-dir/scripts/tests/   # tout vert
python3 ~/.claude/scripts/sante_skills.py; echo "code $?"             # 0, silencieux
```

Et la reproduction décrite par l'entrée de road-map, qui doit désormais échouer à reproduire :
créer une liste, y écrire un tableau sur trois lignes avec un commentaire au-dessus, ajouter un
champ au contrat, `list-dir migrate` — le tableau, sa mise en forme et son commentaire sont intacts,
et le diff ne montre que le champ ajouté.
