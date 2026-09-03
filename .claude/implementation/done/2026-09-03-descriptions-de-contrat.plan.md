# Rédiger les descriptions des contrats de dette

## Contexte

Les trois registres de dette (`technical-debt`, `technical-debt-solde`, `technical-debt-ecarte`)
sont des répertoires-listes `list-dir`. Leur `contract.toml` est censé déclarer **ce qu'il faut
écrire** dans chaque champ et chaque section — c'est ce que sert `list-dir contract`, et ce que
`contrat-liste.md` définit : « `description` dit ce qu'il faut y écrire ».

Deux défauts l'en empêchent aujourd'hui :

1. **Sections jamais rédigées.** Les 14 sections des trois contrats, plus les 4 du gabarit
   `templates/review.toml`, portent toutes `description = ""`. C'est le hors-périmètre assumé du
   chantier `sections-en-forme-longue` (7e3a122), consigné en dette
   `sections-declarees-sans-description-redigee`.
2. **Descriptions de champ recopiées.** Dans `technical-debt-solde` et `technical-debt-ecarte`,
   les champs `title`, `date`, `source` et `category` portent **la description de la liste**,
   à l'identique sur les quatre (`description = "Dette soldée, avec la commande exécutée qui
   l'établit"`). Origine : d8a06ac, rédaction à la main lors de la création des définitions —
   `prefill.py` ne touche qu'aux valeurs des éléments, aucun code n'est en cause. Ce défaut n'a
   aucune entrée au registre, et il est plus trompeur qu'un vide : la commande a l'air de
   documenter.

Résultat visé : le contrat devient la source de vérité de ce qu'est une dette — son contenu et sa
structure — et `dette.md` renvoie à lui au lieu de le redire, conformément à la ligne de partage
posée au brief (« dette.md explique comment fonctionnent les dettes et comment les manipuler »).

Brief : `.claude/implementation/descriptions-de-contrat.brief.md`

## Principes d'exécution

**Deux exemplaires, une seule rédaction.** Chaque contrat existe en semence
(`skills/implementation-tracker/list-dir/<liste>/contract.toml`) et en copie en vigueur
(`.claude/implementation/todo/<liste>/.list/contract.toml`). Ils sont aujourd'hui **strictement
identiques** (`diff` muet). Rien ne les resynchronise (dette
`semence-et-copie-divergent-sans-controle`), donc : **rédiger dans la semence, copier vers la
copie en vigueur, et prouver par `diff`** — jamais rédiger deux fois.

**Forme d'une description.** Une phrase nominale, sur le modèle déjà en vigueur dans
`contrat-liste.md` (« ce qui a été observé, factuel, sans remède ») et dans les champs de
`technical-debt` (« date du constat, jamais modifiée »). Le contrat déclare, il n'argumente pas :
pas de paragraphe, pas de justification — celles-ci restent dans `dette.md`. Lignes ≤ 100
colonnes (dette `trois-lignes-au-dela-de-100-colonnes`).

## Étapes

### 1. Sections de `technical-debt`

Fichier : `skills/implementation-tracker/list-dir/technical-debt/contract.toml`, puis copie.

Rédiger les 4 `description` de section, en faisant descendre la doctrine de `dette.md`
(« Ce qu'une entrée porte », « Désigner sans numéro de ligne ») :

| Section | Substance de la description |
|---|---|
| `Constat` | ce qui a été observé, factuel et daté, sans remède ; cite un fichier et une phrase, jamais un numéro de ligne |
| `Pourquoi c'est gênant` | le coût réel si rien n'est fait, et le mode de défaillance qu'il ouvre |
| `Pour solder` | ce qu'il faut faire pour que la dette disparaisse, même grossièrement — sans lui, c'est un regret |
| `Assumé` | pourquoi le report a été délibéré, quand il l'a été |

Vérification :

```bash
grep -c 'description = ""' skills/implementation-tracker/list-dir/technical-debt/contract.toml   # 0
diff .claude/implementation/todo/technical-debt/.list/contract.toml \
     skills/implementation-tracker/list-dir/technical-debt/contract.toml
list-dir validate .claude/implementation/todo/technical-debt
```

### 2. `technical-debt-solde` et `technical-debt-ecarte` — champs et sections

Fichiers : les deux semences, puis leurs copies.

**Champs** — remplacer les 4 descriptions recopiées par celles que `technical-debt` porte déjà :
`title` « l'énoncé de la dette, tel qu'il figurait en titre d'entrée », `date` « date du constat,
jamais modifiée », `source` « le chantier qui l'a identifiée et où il l'a écrit, verbatim »,
`category` « verdict de la dernière revue, posé par debt-review » — **sans accents graves**, tel
que `technical-debt/contract.toml:30` l'écrit : les trois contrats doivent rester identiques sur ce
champ. `reviewed` est déjà correct.

**Sections** — reprendre celles de l'étape 1 pour les sections communes, et rédiger les deux
sections de sortie, dont la doctrine est dans `dette.md` (« Solder », « Écarter ») :

| Section | Substance |
|---|---|
| `Soldé le` | date et chantier, puis la commande exécutée avec sa sortie réelle : un solde s'établit, il ne se déclare pas |
| `Écartée le` | date et motif — non pertinent, doublon, pas une dette — puis la preuve exécutée ; pour un doublon, l'`id` de l'entrée conservée |

Les descriptions de `Pourquoi c'est gênant` et `Pour solder`, facultatives dans ces deux listes,
disent qu'elles sont **reprises de l'entrée d'origine si elle les portait** : une entrée sortie du
registre prouve sa sortie, elle ne plaide pas une cause tranchée (`dette.md`, « Ce qu'une entrée
porte »). `Constat` y reste requis, sa description est la même qu'à l'étape 1.

Vérification :

```bash
for l in technical-debt-solde technical-debt-ecarte; do
  grep -c 'description = ""' skills/implementation-tracker/list-dir/$l/contract.toml
  diff .claude/implementation/todo/$l/.list/contract.toml \
       skills/implementation-tracker/list-dir/$l/contract.toml
  list-dir validate .claude/implementation/todo/$l
done
list-dir contract .claude/implementation/todo/technical-debt-solde | grep -c "Dette soldée"   # 1
list-dir contract .claude/implementation/todo/technical-debt-ecarte | grep -c "Sorti du registre"  # 1
```

Les deux comptes valent **5** aujourd'hui : la description de liste, plus les quatre champs qui la
recopient.

### 3. Gabarit `review.toml`

Fichiers : `skills/implementation-tracker/list-dir/technical-debt/templates/review.toml`, puis
`.claude/implementation/todo/technical-debt/.list/templates/review.toml`.

Doctrine dans `skills/debt-review/SKILL.md` (Étape 2, point 4) et
`references/exemple-revue.md` :

| Section | Substance |
|---|---|
| `Vérifié par` | la commande exécutée et sa sortie réelle, rejouable seule — c'est elle qui sera recopiée au registre |
| `Verdict` | ce que la commande établit, et pourquoi cette catégorie plutôt que la voisine |
| `Action` | le `move` à faire et la section de sortie à écrire, ou le maintien au registre |
| `Arbitrage` | ce que l'utilisateur a tranché à l'Étape 4, quand il a corrigé le verdict |

Vérification :

```bash
S=/tmp/claude-1000/-home-debian--claude/309b40cd-53ee-4a65-af63-e3530928cef5/scratchpad
grep -c 'description = ""' \
  skills/implementation-tracker/list-dir/technical-debt/templates/review.toml   # 0
diff .claude/implementation/todo/technical-debt/.list/templates/review.toml \
     skills/implementation-tracker/list-dir/technical-debt/templates/review.toml
rm -rf "$S/revue-test"
list-dir derive .claude/implementation/todo/technical-debt "$S/revue-test" --template review
list-dir contract "$S/revue-test"
rm -rf "$S/revue-test"
```

`derive` exige une destination inexistante et projettera les 40 entrées du registre : la liste est
jetable, sous le scratchpad, et supprimée après lecture.

### 4. Renvoi depuis `dette.md` et `debt-review`

Fichier : `skills/implementation-tracker/references/dette.md`, section « Ce qu'une entrée porte ».

Elle déclare déjà « Le contrat de la liste fait foi » et a retiré son tableau des champs. Il y
reste trois règles qui décrivent le **contenu** d'une section, désormais portées par le contrat :

- la facultativité de `Pourquoi c'est gênant` / `Pour solder` dans les listes de sortie, et
  pourquoi `Constat` y reste requis ;
- « Une entrée sans **Pour solder** est un regret, pas une dette » ;
- « Désigner sans numéro de ligne » (la règle descend dans la description de `Constat`).

Les remplacer par un renvoi à `list-dir contract`, en **gardant** dans `dette.md` ce qui reste de
sa compétence : les *modes de défaillance* (encadrés `> *Mode de défaillance*`), qui expliquent
pourquoi la règle existe, et « L'`id` ne se renomme pas », qui est une règle de manipulation.

**Ne supprimer aucun titre `##`** : `check_pipeline.py` contrôle les ancres des renvois
inter-fichiers.

Côté `skills/debt-review/SKILL.md`, l'Étape 2 point 4 énumère les sections à écrire et *quand* —
c'est de la manipulation, elle reste. Vérifier seulement qu'elle ne redit pas ce que le gabarit
déclare désormais ; si elle le fait, la faire renvoyer.

Vérification : `python3 scripts/check_pipeline.py` (exit 0 aujourd'hui, doit le rester).

### 5. Contrôle d'ensemble

```bash
grep -rn --include='*.toml' 'description = ""' \
  skills/implementation-tracker/list-dir .claude/implementation/todo   # rien
for l in technical-debt technical-debt-solde technical-debt-ecarte; do
  diff -r .claude/implementation/todo/$l/.list skills/implementation-tracker/list-dir/$l
  list-dir validate .claude/implementation/todo/$l
done
list-dir defs
python3 scripts/check_pipeline.py
python3 scripts/sante_skills.py
```

`--include='*.toml'` n'est pas une commodité : sans lui, le grep capte les deux occurrences en
prose de `technical-debt/sections-declarees-sans-description-redigee.md` (lignes 18 et 26), que le
hors-périmètre interdit de retoucher. Le critère du brief se lit donc sur les seuls contrats.

Relire enfin les trois `list-dir contract` en entier : c'est la sortie que le chantier existe pour
rendre lisible, et le seul contrôle qu'aucune commande ne fait.

## Hors-périmètre (rappel du brief)

- aucune modification de code ;
- pas de réécriture des entrées de dette existantes pour les conformer aux descriptions rédigées.

## Signaux de dérive (rappel du brief)

- une `description` qui devient un paragraphe ;
- `dette.md` qui cesse d'expliquer comment fonctionnent les dettes et comment les manipuler ;
- semence et copie qui divergent en fin de passe.

## Reste ouvert

Le second défaut n'a aucune entrée au registre. À la clôture, décider s'il en mérite une
rétroactive ou si le journal du suivi suffit — et ne solder
`sections-declarees-sans-description-redigee` qu'après le verdict de `implementation-auditor`.
