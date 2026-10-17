"""`check` sur une section à labels, en `bold` comme en `title` : fautes et notes.

CE QUE CE FICHIER PROUVE (C2) : une section à labels conforme passe, labels sans `order`
placés n'importe où ; `check` nomme un label requis absent ou vide, un `order` violé, la
prose avant le premier label sans `prefix`, deux labels non séparés d'une ligne vide, un
label en double, la faute d'un motif dans un label ; un label au marqueur passe, et
`--filled` le dit à remplir ; une étiquette non déclarée et un label déprécié sont des
notes, qui ne changent pas le verdict ; une étiquette dans un bloc de code n'en est pas
une ; en `title`, l'imbrication `title` → `title` → `bold` est jugée à chaque niveau.
"""

from __future__ import annotations

from pathlib import Path

from gabarit.check import check_item, notes
from gabarit.contract import parse_contract
from gabarit.types import Contract, Item

BOLD = """name = "essai"
description = ""

[sections."État"]
description = ""
required = true
type = "label"
forme = "bold"

[sections."État".labels."Prochaine action"]
description = "x"
required = true
order = 1

[sections."État".labels."Notes"]
description = "x"

[sections."État".labels."Vérification"]
description = "x"
required = true
order = 2

[sections."État".labels."Critères"]
description = "x"
type = "motif"
motif = "{code}: {texte}"
order = 3

[sections."État".labels."Critères".captures.code]
description = "x"

[sections."État".labels."Critères".captures.texte]
description = "x"

[sections."État".labels."Ancien"]
description = "x"
deprecated = "ne plus l'écrire"
"""

CONFORME = """\
**Prochaine action** : Étape 5.

**Notes** :
libre, sur
plusieurs lignes

**Vérification** : pytest

**Critères** :
- C1: un ;;
- C2: deux ;;
"""

TITLE = """name = "essai"
description = ""

[sections."S"]
description = ""
type = "label"
forme = "title"

[sections."S".labels."Contexte"]
description = "x"
required = true

[sections."S".labels."Détail"]
description = "x"
type = "label"
forme = "title"

[sections."S".labels."Détail".labels."Un"]
description = "x"
required = true

[sections."S".labels."Détail".labels."Deux"]
description = "x"
type = "label"
forme = "bold"

[sections."S".labels."Détail".labels."Deux".labels."Clé"]
description = "x"
required = true
"""

TITRES = """\
### Contexte

du texte
##### un titre plus bas reste du contenu

### Détail

#### Un

texte

#### Deux

**Clé** : valeur
"""


def contrat(tmp_path: Path, texte: str = BOLD) -> Contract:
    return parse_contract(texte, tmp_path / "contract.toml").unwrap()


def item(tmp_path: Path, corps: str, titre: str = "État") -> Item:
    return Item(tmp_path / "essai.md", {}, {titre: corps})


def fautes(
    tmp_path: Path, corps: str, *, texte: str = BOLD, titre: str = "État", filled: bool = False
) -> list[str]:
    it = item(tmp_path, corps, titre)
    return [f"{v.subject} — {v.reason}" for v in check_item(contrat(tmp_path, texte), it, filled)]


def les_notes(tmp_path: Path, corps: str, *, texte: str = BOLD, titre: str = "État") -> list[str]:
    prefixe = f"{tmp_path / 'essai.md'}: "
    return [
        n.removeprefix(prefixe)
        for n in notes(contrat(tmp_path, texte), item(tmp_path, corps, titre))
    ]


# ------------------------------------------------------------------------ bold
def test_une_section_bold_conforme_passe(tmp_path: Path) -> None:
    assert fautes(tmp_path, CONFORME) == []
    assert fautes(tmp_path, CONFORME, filled=True) == []
    assert les_notes(tmp_path, CONFORME) == []


def test_le_corps_peut_suivre_l_etiquette_sans_espace(tmp_path: Path) -> None:
    corps = CONFORME.replace("**Vérification** : pytest", "**Vérification**: pytest")
    assert fautes(tmp_path, corps) == []


def test_label_requis_absent(tmp_path: Path) -> None:
    corps = CONFORME.replace("**Vérification** : pytest\n\n", "")
    assert fautes(tmp_path, corps) == ["section « État », label « Vérification » — manquant"]


def test_label_requis_vide(tmp_path: Path) -> None:
    corps = CONFORME.replace("**Vérification** : pytest", "**Vérification** :")
    assert fautes(tmp_path, corps) == ["section « État », label « Vérification » — vide"]


def test_order_viole(tmp_path: Path) -> None:
    corps = "**Vérification** : pytest\n\n**Prochaine action** : rien\n"
    assert fautes(tmp_path, corps) == [
        "section « État », label « Prochaine action » — « order » 1 placé après "
        "« Vérification » (2)"
    ]


def test_un_label_sans_order_prend_n_importe_quelle_place(tmp_path: Path) -> None:
    corps = "**Notes** : a\n\n**Prochaine action** : b\n\n**Vérification** : c\n"
    assert fautes(tmp_path, corps) == []


def test_prose_avant_le_premier_label_sans_prefix(tmp_path: Path) -> None:
    assert fautes(tmp_path, "Un mot d'intro.\n\n" + CONFORME) == [
        "section « État » — prose avant le premier label : « Un mot d'intro. » — sans "
        "« prefix », la section ne porte que des labels"
    ]


def test_prose_avant_le_premier_label_avec_prefix(tmp_path: Path) -> None:
    texte = BOLD.replace('forme = "bold"\n', 'forme = "bold"\nprefix = "une introduction"\n')
    assert fautes(tmp_path, "Un mot d'intro.\n\n" + CONFORME, texte=texte) == []


def test_labels_non_separes_d_une_ligne_vide(tmp_path: Path) -> None:
    corps = CONFORME.replace("Étape 5.\n\n**Notes**", "Étape 5.\n**Notes**")
    assert fautes(tmp_path, corps) == [
        "section « État », label « Notes » — non séparé de ce qui précède par une ligne vide"
    ]


def test_label_en_double(tmp_path: Path) -> None:
    corps = CONFORME + "\n**Notes** : encore\n"
    assert fautes(tmp_path, corps) == ["section « État », label « Notes » — en double"]


def test_motif_dans_un_label(tmp_path: Path) -> None:
    corps = CONFORME.replace("- C2: deux ;;", "- C2 deux ;;")
    trouvees = fautes(tmp_path, corps)
    assert len(trouvees) == 1
    assert trouvees[0].startswith(
        "section « État », label « Critères », puce 2 — « C2 deux » ne suit pas le motif"
    )


def test_label_au_marqueur_et_filled(tmp_path: Path) -> None:
    corps = CONFORME.replace("**Vérification** : pytest", "**Vérification** : <À REMPLIR>")
    assert fautes(tmp_path, corps) == []
    assert fautes(tmp_path, corps, filled=True) == [
        "section « État », label « Vérification » — à remplir"
    ]


def test_label_a_motif_au_marqueur_de_motif(tmp_path: Path) -> None:
    marqueur = "<OPTIONNEL motif: - {code}: {texte} ;;>"
    corps = CONFORME.replace("- C1: un ;;\n- C2: deux ;;", marqueur)
    assert fautes(tmp_path, corps, filled=True) == []


def test_etiquette_non_declaree_est_une_note(tmp_path: Path) -> None:
    corps = CONFORME + "\n**Inconnu** : quelque chose\n"
    assert fautes(tmp_path, corps) == []
    assert les_notes(tmp_path, corps) == [
        "section « État », label « Inconnu » — étiquette non déclarée au contrat"
    ]


def test_label_deprecie_present_est_une_note(tmp_path: Path) -> None:
    corps = CONFORME + "\n**Ancien** : vieux\n"
    assert fautes(tmp_path, corps) == []
    assert les_notes(tmp_path, corps) == [
        "section « État », label « Ancien » — déprécié : ne plus l'écrire"
    ]


def test_une_etiquette_dans_un_bloc_de_code_n_en_est_pas_une(tmp_path: Path) -> None:
    corps = CONFORME.replace("libre, sur", "```\n**Vérification** : faux\n```")
    assert fautes(tmp_path, corps) == []
    assert les_notes(tmp_path, corps) == []


def test_une_section_au_marqueur_n_a_pas_de_notes(tmp_path: Path) -> None:
    assert les_notes(tmp_path, "<À REMPLIR>") == []


# ----------------------------------------------------------------------- title
def test_une_section_title_imbriquee_conforme_passe(tmp_path: Path) -> None:
    assert fautes(tmp_path, TITRES, texte=TITLE, titre="S") == []
    assert les_notes(tmp_path, TITRES, texte=TITLE, titre="S") == []


def test_title_label_requis_absent_a_chaque_niveau(tmp_path: Path) -> None:
    # « Deux », facultatif, vide : rien à dire ; « Un », requis, absent : manquant.
    corps = TITRES.replace("#### Un\n\ntexte\n\n", "").replace("**Clé** : valeur", "")
    assert fautes(tmp_path, corps, texte=TITLE, titre="S") == [
        "section « S », label « Détail », label « Un » — manquant",
    ]
    sans_contexte = TITRES[TITRES.index("### Détail") :]
    assert fautes(tmp_path, sans_contexte, texte=TITLE, titre="S") == [
        "section « S », label « Contexte » — manquant",
    ]


def test_title_bold_imbrique_juge(tmp_path: Path) -> None:
    corps = TITRES.replace("**Clé** : valeur", "**Autre** : valeur")
    assert fautes(tmp_path, corps, texte=TITLE, titre="S") == [
        "section « S », label « Détail », label « Deux », label « Clé » — manquant"
    ]
    assert les_notes(tmp_path, corps, texte=TITLE, titre="S") == [
        "section « S », label « Détail », label « Deux », label « Autre » — étiquette non "
        "déclarée au contrat"
    ]


def test_title_non_separe_et_non_declare(tmp_path: Path) -> None:
    corps = TITRES.replace("texte\n\n#### Deux", "texte\n#### Deux") + "\n### Autre\n\nx\n"
    assert fautes(tmp_path, corps, texte=TITLE, titre="S") == [
        "section « S », label « Détail », label « Deux » — non séparé de ce qui précède par "
        "une ligne vide"
    ]
    assert les_notes(tmp_path, corps, texte=TITLE, titre="S") == [
        "section « S », label « Autre » — étiquette non déclarée au contrat"
    ]


def test_title_prose_avant_le_premier_label(tmp_path: Path) -> None:
    trouvees = fautes(tmp_path, "intro\n\n" + TITRES, texte=TITLE, titre="S")
    assert trouvees == [
        "section « S » — prose avant le premier label : « intro » — sans « prefix », la "
        "section ne porte que des labels"
    ]
