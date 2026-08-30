"""ListStore : toutes les opérations sur une liste.

C'EST ICI QUE VIT LA LOGIQUE. Les commandes de la CLI se réduisent à un register()
et à un appel d'une méthode d'ici — c'est ce qui garantit qu'un script tiers a
exactement les mêmes moyens que la ligne de commande, et que les deux ne peuvent
pas diverger.

RÈGLE DE LECTURE : tout *.md à la racine est un élément, sans exception. Tout le
reste vit sous .list/. Un README posé à la racine serait compté comme un élément,
et le contrôle de conservation d'une agglomération rendrait un nombre faux sans
broncher.
"""

from __future__ import annotations

import datetime
from collections.abc import Mapping
from pathlib import Path
from typing import final, override

from .contract import (
    CONTRACT,
    LIST_DIR,
    TEMPLATES,
    check_value,
    is_marker,
    load_contract,
    parse_contract,
)
from .gitcmd import git
from .items import (
    SerialiseError,
    dump_value,
    fence_ouverte,
    outside_fences,
    parse_sections,
    read_item,
    write_item,
)
from .types import OPTIONAL, Change, Contract, FieldValue, Item, Result, Violation, fail, ok


@final
class ListStore:
    """Une liste ouverte : son répertoire et son contrat."""

    path: Path
    contract: Contract

    def __init__(self, path: Path, contract: Contract) -> None:
        self.path = path
        self.contract = contract

    @override
    def __repr__(self) -> str:
        return f"<ListStore {self.contract.name} @ {self.path}>"

    # ------------------------------------------------------------------ lecture
    def paths(self) -> list[Path]:
        """Les fichiers d'éléments, triés par nom. Jamais rien de .list/."""
        return sorted(p for p in self.path.glob("*.md") if p.is_file())

    def items(self) -> Result[list[Item]]:
        out: list[Item] = []
        for p in self.paths():
            r = read_item(p)
            if not r:
                return Result(r.status, None, r.message)
            out.append(r.unwrap())
        return ok(out)

    def get(self, item_id: str) -> Result[Item]:
        path = self.path / f"{item_id}.md"
        if not path.is_file():
            return fail(f"{self.path}: élément « {item_id} » introuvable")
        return read_item(path)

    def where(self, **criteria: FieldValue) -> Result[list[Item]]:
        """Filtre sur les champs DÉCLARÉS AU CONTRAT, et rien d'autre.

        Pas de recherche plein texte : grep la fait déjà mieux. Un champ inconnu
        est une erreur, pas un filtre qui ne rend rien — un filtre silencieusement
        vide se lit comme « aucun résultat ».

        LA COMPARAISON EST TEXTUELLE, ET C'EST VOULU : `--where date=2026-08-24`
        doit fonctionner sans que l'appelant ait à connaître le type déclaré, et
        `validate` reste seul juge de la conformité.

        UN CHAMP ABSENT NE VAUT PAS LA CHAÎNE « None ». Il l'a valu, et
        `--where category=None` sélectionnait alors les éléments SANS `category` —
        un comportement utile, découvert par accident, documenté nulle part, et que
        rien ne distinguait d'un élément dont la valeur serait littéralement
        « None ». La forme explicite est le critère VIDE : `--where category=`
        sélectionne les éléments où le champ est absent.
        """
        for name in criteria:
            if name not in self.contract.fields:
                connus = ", ".join(self.contract.fields) or "aucun"
                return fail(
                    f"{self.path}: champ « {name} » non déclaré au contrat ; connus : {connus}"
                )
        r = self.items()
        if not r:
            return r
        return ok(
            [
                it
                for it in r.unwrap()
                if all(_correspond(it.fields.get(k), v) for k, v in criteria.items())
            ]
        )

    # ---------------------------------------------------------------- validation
    def validate(self, filled: bool = False) -> Result[list[Violation]]:
        """Confronte chaque élément au contrat. Liste VIDE = conforme.

        DEUX VERDICTS, et c'est délibéré. Sans `filled`, seule la STRUCTURE est
        jugée : les marqueurs sont légitimes, puisqu'une fiche fraîchement créée
        ou dérivée n'est pas encore remplie. Avec `filled`, plus aucun marqueur
        n'est toléré là où le contrat exige quelque chose — mais les facultatifs
        restés à leur marqueur ne sont JAMAIS réclamés.

        Une liste sans élément est conforme : une liste fraîchement créée est
        légitimement vide.
        """
        r = self.items()
        if not r:
            return Result(r.status, None, r.message)

        out: list[Violation] = []
        for item in r.unwrap():
            out.extend(self.check_item(item, filled))
        return ok(out)

    def check_item(self, item: Item, filled: bool = False) -> list[Violation]:
        """Un élément confronté à CE contrat, qu'il vienne ou non de cette liste.

        Publique parce que `move` en a besoin : après un déplacement, il faut dire
        ce que le contrat d'arrivée exige d'un élément écrit pour le contrat de
        départ. Le déplacement n'en dépend pas — c'est un rappel, jamais un refus.
        """
        return [*self._check_fields(item, filled), *self._check_sections(item, filled)]

    def _check_fields(self, item: Item, filled: bool) -> list[Violation]:
        out: list[Violation] = []
        for name in item.fields:
            if name not in self.contract.fields:
                out.append(Violation(item.path, f"champ « {name} »", "non déclaré au contrat"))

        for name, f in self.contract.fields.items():
            subject = f"champ « {name} »"
            if name not in item.fields:
                if f.required:
                    out.append(Violation(item.path, subject, "manquant"))
                continue
            value = item.fields[name]

            # `id` n'a jamais de marqueur : il vaut le nom du fichier, posé à la
            # création. Le contrôler ici est ce qui empêche un renommage à la main
            # de désolidariser l'identifiant de son support.
            if name == "id":
                if value != item.path.stem:
                    out.append(
                        Violation(
                            item.path, subject, f"vaut « {value} », attendu « {item.path.stem} »"
                        )
                    )
                continue

            reason = check_value(f, value)
            if reason:
                out.append(Violation(item.path, subject, reason))
            elif filled and f.required and is_marker(value):
                out.append(Violation(item.path, subject, "à remplir"))
        return out

    def _check_sections(self, item: Item, filled: bool) -> list[Violation]:
        out: list[Violation] = []
        declared = set(self.contract.sections)
        for title, corps in item.sections.items():
            if title not in declared:
                out.append(Violation(item.path, f"section « {title} »", "non déclarée au contrat"))
            # LA FENCE SE SIGNALE ICI, à sa source. Un bloc jamais refermé absorbe
            # les `## ` suivants : sans ce contrôle, les sections avalées étaient
            # rapportées « manquantes » alors qu'elles sont écrites dans le fichier,
            # et merge annonçait plus loin une perte qui n'existait pas.
            ouverte = fence_ouverte(corps)
            if ouverte is not None:
                out.append(
                    Violation(
                        item.path,
                        f"section « {title} »",
                        f"bloc de code ouvert par « {ouverte} » et jamais refermé — "
                        "les sections suivantes y sont absorbées",
                    )
                )

        for title in self.contract.required_sections:
            subject = f"section « {title} »"
            if title not in item.sections:
                out.append(Violation(item.path, subject, "manquante"))
                continue
            body = item.sections[title].strip()
            if not body:
                out.append(Violation(item.path, subject, "vide"))
            elif filled and is_marker(body):
                out.append(Violation(item.path, subject, "à remplir"))
        return out

    # ------------------------------------------------------------------ écriture
    def create(self, item_id: str, **values: FieldValue) -> Result[Item]:
        """Un élément prérempli de TOUT le contrat : champs et sections, requis et
        facultatifs, chacun portant le marqueur de son statut.

        Poser aussi le facultatif n'est pas de la générosité : ce qu'on ne voit pas
        n'est jamais rempli.
        """
        path = self.path / f"{item_id}.md"
        if path.exists():
            return fail(f"{self.path}: « {item_id} » existe déjà")

        fields: dict[str, FieldValue] = {}
        for name, f in self.contract.fields.items():
            if name in values:
                fields[name] = values[name]
            elif f.type == "slug" and name == "id":
                fields[name] = item_id
            else:
                fields[name] = f.marker
        sections = {t: self.contract.section_marker(t) for t in self.contract.sections}
        return ok(Item(path, fields, sections))

    def write(self, item: Item) -> Result[Path]:
        return write_item(item)

    def migrate(self, *, drop: bool = False, dry_run: bool = False) -> Result[list[Change]]:
        """Remet les éléments en conformité avec le contrat COURANT.

        CE QU'ELLE FAIT — de la structure, rien d'autre : elle pose les champs et
        les sections que le contrat déclare et qui manquent, chacun au marqueur de
        son statut, et remet les uns et les autres dans l'ordre du contrat. Une
        valeur déjà écrite n'est jamais touchée.

        CE QU'ELLE NE FAIT PAS : elle ne renomme rien et ne reporte rien. Décider
        qu'un champ `severite` disparu est devenu `gravite`, c'est juger — et un
        script qui juge est la ligne que ce dispositif ne franchit pas. Un champ
        ou une section que le contrat ne déclare plus est CONSERVÉ et signalé ;
        `drop=True`, demandé explicitement, le retire.

        REJOUABLE : une migration sur une liste déjà conforme ne touche aucun
        fichier et rend une liste de changements vide. C'est ce qui permet de la
        relancer après une écriture interrompue.

        EFFET DE BORD À CONNAÎTRE : un élément modifié voit son front matter
        resérialisé (cf. Item.realigned). D'éventuels commentaires TOML écrits à la
        main y disparaissent — le contrat est l'autorité, pas la mise en page.
        """
        items = self.items()
        if not items:
            return Result(items.status, None, items.message)

        # Tout est calculé avant la moindre écriture, comme pour derive : une
        # migration qui échoue à mi-parcours laisserait la liste dans un état que
        # ni l'ancien contrat ni le nouveau ne décrit.
        plan: list[Item] = []
        changes: list[Change] = []
        for item in items.unwrap():
            aligned, faits = self._realign(item, drop)
            changes.extend(faits)
            # Une remarque seule ne fait rien écrire : réécrire un élément que la
            # migration n'a pas eu à changer lui coûterait son raw_front pour rien.
            if any(c.applied for c in faits):
                plan.append(aligned)

        if dry_run:
            return ok(changes)

        for item in plan:
            written = self.write(item)
            if not written:
                return Result(written.status, None, written.message)
        return ok(changes)

    def _realign(self, item: Item, drop: bool) -> tuple[Item, list[Change]]:
        """L'élément tel que le contrat courant le veut, et ce qu'il a fallu faire.

        Liste de changements vide → l'élément est déjà conforme, et l'appelant ne
        doit PAS le réécrire : le réécrire pour rien perdrait son raw_front.
        """
        changes: list[Change] = []

        fields: dict[str, object] = {}
        for name, f in self.contract.fields.items():
            subject = f"champ « {name} »"
            if name in item.fields:
                fields[name] = item.fields[name]
            elif name == "id":
                # L'identifiant ne prend jamais de marqueur : il vaut le nom du
                # fichier, seul lien entre l'élément et son support.
                fields[name] = item.path.stem
                changes.append(Change(item.path, subject, f"posé à « {item.path.stem} »"))
            else:
                fields[name] = f.marker
                changes.append(Change(item.path, subject, f"ajouté, {f.marker}"))

        for name, value in item.fields.items():
            if name in self.contract.fields:
                continue
            subject = f"champ « {name} »"
            if drop:
                changes.append(Change(item.path, subject, "retiré — non déclaré au contrat"))
            else:
                # Conservé en queue : le retirer d'office détruirait une donnée que
                # personne n'a relue. validate continue de le signaler.
                fields[name] = value
                changes.append(
                    Change(
                        item.path,
                        subject,
                        "conservé — non déclaré au contrat (voir --drop)",
                        applied=False,
                    )
                )

        sections: dict[str, str] = {}
        for title in self.contract.sections:
            subject = f"section « {title} »"
            if title in item.sections:
                sections[title] = item.sections[title]
            else:
                sections[title] = self.contract.section_marker(title)
                changes.append(
                    Change(item.path, subject, f"ajoutée, {self.contract.section_marker(title)}")
                )

        declared = set(self.contract.sections)
        for title, body in item.sections.items():
            if title in declared:
                continue
            subject = f"section « {title} »"
            if drop:
                changes.append(Change(item.path, subject, "retirée — non déclarée au contrat"))
            else:
                sections[title] = body
                changes.append(
                    Change(
                        item.path,
                        subject,
                        "conservée — non déclarée au contrat (voir --drop)",
                        applied=False,
                    )
                )

        changes.extend(
            _reordering(
                item.path,
                "front matter",
                "champs réordonnés selon le contrat",
                item.fields,
                fields,
            )
        )
        changes.extend(
            _reordering(
                item.path,
                "corps",
                "sections réordonnées selon le contrat",
                item.sections,
                sections,
            )
        )

        if not any(c.applied for c in changes):
            return item, changes
        return item.realigned(fields, sections), changes

    def move(self, item_id: str, target: ListStore | Path | str) -> Result[Path]:
        """Déplace un élément vers une autre liste. `git mv`, ET RIEN D'AUTRE.

        LE RENOMMAGE EST PUR, et ce n'est pas un raffinement : Git ne stocke pas
        les renommages, il les DÉDUIT de la similarité des contenus. Réécrire le
        fichier dans le même commit fait tomber cette déduction sous son seuil, et
        l'historique montre alors une suppression suivie d'une création —
        `git log --follow` s'arrête là. Ce qui accompagne un déplacement, la trace
        d'un solde par exemple, va dans un SECOND commit.

        L'état d'un élément est porté par son répertoire, jamais par un champ :
        c'est pourquoi rien n'est écrit ici.
        """
        source = self.path / f"{item_id}.md"
        if not source.is_file():
            return fail(f"{self.path}: élément « {item_id} » introuvable")

        if isinstance(target, ListStore):
            dest_list = target
        else:
            opened = open_list(target)
            if not opened:
                return Result(opened.status, None, opened.message)
            dest_list = opened.unwrap()

        if dest_list.path.resolve() == self.path.resolve():
            return fail(f"{self.path}: « {item_id} » est déjà dans cette liste")

        destination = dest_list.path / source.name
        if destination.exists():
            return fail(f"{dest_list.path}: « {item_id} » existe déjà — rien n'est déplacé")

        # cwd sur la source : git remonte lui-même à la racine du dépôt, et un
        # chemin relatif au répertoire courant du processus appelant serait faux.
        moved = git("mv", str(source.resolve()), str(destination.resolve()), cwd=self.path)
        if not moved:
            return Result(moved.status, None, f"{source} → {destination} : {moved.message}")
        return ok(destination)

    # ---------------------------------------------------------------------- ouverture
    # ------------------------------------------------------- projection et agglomération
    def derive(self, destination: Path | str, template: str) -> Result[ListStore]:
        """Projette la STRUCTURE de cette liste sur une liste neuve.

        CE N'EST PAS UNE COPIE. Chaque élément source engendre un élément de même
        `id`, mais son corps vient du moule `<template>.md`, jamais de la source.
        Une fiche qui porterait la prose de l'élément qu'elle instruit en serait un
        doublon éditable, et la source unique serait perdue. La fiche ne porte que
        du contenu neuf — c'est ce qui la rend légitimement éditable.

        Le seul emprunt est déclaratif : un champ du contrat cible portant `from`
        reçoit la valeur du champ nommé dans la source. Sans `from`, il reçoit le
        marqueur de son propre statut, exactement comme `new`. `derive` ne
        transforme, ne concatène et ne calcule rien — un script qui déciderait quoi
        reporter serait un script qui juge.
        """
        sources = self.items()
        if not sources:
            return Result(sources.status, None, sources.message)
        if not sources.unwrap():
            return fail(f"{self.path}: aucun élément — il n'y a rien à projeter")

        moule = self.template(template)
        if not moule:
            return Result(moule.status, None, moule.message)
        contract_text, gabarit = moule.unwrap()

        target = Path(destination)
        if target.exists():
            # derive ne fusionne ni ne met à jour : deux projections = deux
            # répertoires distincts. Écraser ferait disparaître un travail déjà fait.
            return fail(f"{target}: existe déjà — derive ne fusionne ni ne met à jour")

        # TOUT EST CONSTRUIT EN MÉMOIRE D'ABORD. Un gabarit incohérent découvert
        # après un mkdir laisserait une destination à moitié bâtie, que la tentative
        # suivante refuserait comme « existe déjà » : l'utilisateur serait coincé
        # entre une erreur qu'il a corrigée et un répertoire qu'il n'a pas créé.
        contract_file = target / LIST_DIR / CONTRACT
        parsed = parse_contract(contract_text, contract_file)
        if not parsed:
            return Result(parsed.status, None, parsed.message)
        derived = ListStore(target, parsed.unwrap())

        fiches: list[Item] = []
        for source in sources.unwrap():
            built = self._project(source, derived, gabarit)
            if not built:
                return Result(built.status, None, built.message)
            fiches.append(built.unwrap())

        try:
            contract_file.parent.mkdir(parents=True)
            _ = contract_file.write_text(contract_text, encoding="utf-8")
        except OSError as exc:
            return fail(f"{target}: écriture impossible — {exc.strerror}")

        for fiche in fiches:
            written = derived.write(fiche)
            if not written:
                return Result(written.status, None, written.message)
        return ok(derived)

    def template(self, name: str) -> Result[tuple[str, Mapping[str, str]]]:
        """La paire `<name>.toml` / `<name>.md` de cette liste.

        Les deux sont exigés, et celui qui manque est nommé : un gabarit à moitié
        présent produirait une liste sans contrat ou des fiches sans sections, deux
        états qu'on ne découvrirait qu'à l'usage.
        """
        directory = self.path / LIST_DIR / TEMPLATES
        contrat, gabarit = directory / f"{name}.toml", directory / f"{name}.md"
        for f in (contrat, gabarit):
            if not f.is_file():
                return fail(f"{f}: gabarit « {name} » incomplet — ce fichier manque")
        try:
            texte = contrat.read_text(encoding="utf-8")
            corps = gabarit.read_text(encoding="utf-8")
        except OSError as exc:
            return fail(f"{directory}: gabarit illisible — {exc.strerror}")
        # parse_sections ignore ce qui précède le premier « ## » : le gabarit peut
        # porter un front matter ou n'en porter aucun, seules ses sections comptent.
        # Le front matter d'une fiche est injecté depuis le contrat cible, pour ne
        # pas avoir à tenir la même liste de champs dans le .toml et dans le .md.
        return ok((texte, parse_sections(corps)))

    def _project(
        self, source: Item, derived: ListStore, gabarit: Mapping[str, str]
    ) -> Result[Item]:
        fields: dict[str, object] = {}
        for name, f in derived.contract.fields.items():
            if name == "id":
                # Reporté d'office : c'est le seul lien entre une fiche et l'élément
                # qu'elle instruit.
                fields[name] = source.id
            elif f.source is None:
                fields[name] = f.marker
            elif f.source not in self.contract.fields:
                return fail(
                    f'{derived.path}: champ « {name} » — `from = "{f.source}"` '
                    f"ne nomme aucun champ du contrat de {self.path}"
                )
            else:
                fields[name] = source.fields.get(f.source, f.marker)
        return ok(Item(derived.path / f"{source.id}.md", fields, dict(gabarit)))

    def merge_text(self) -> Result[str]:
        """L'aggloméré, en mémoire. La conservation est vérifiée avant de rendre.

        RENDU FIXÉ, ET IL VAUT POUR TOUTE LISTE : `# ` le préambule, `## ` un
        élément, `### ` ses sections décalées d'un niveau. Le décalage n'est pas
        cosmétique — les sections d'un élément sont des `## ` dans son fichier, et
        sans lui `grep -c '^## '` compterait les sections en plus des éléments,
        vidant de sens le contrôle de conservation.
        """
        attendu = len(self.paths())
        if attendu == 0:
            return fail(f"{self.path}: aucun élément — agglomérer zéro n'est pas un résultat")

        # merge exige --filled : un rapport contenant encore un marqueur se lirait
        # comme instruit alors qu'il ne l'est pas.
        manquements = self.validate(filled=True)
        if not manquements:
            return Result(manquements.status, None, manquements.message)
        restants = manquements.unwrap()
        if restants:
            detail = "\n".join(str(v) for v in restants)
            return fail(f"{detail}\n\n{self.path}: à compléter avant d'agglomérer")

        items = self.items()
        if not items:
            return Result(items.status, None, items.message)

        blocs: list[str] = []
        for item in items.unwrap():
            titre = item.fields.get("title") or item.id
            corps = [f"## {titre}", ""]
            for nom, texte in item.sections.items():
                # Une section restée facultative a joué son rôle — guider — et n'a
                # rien à dire ici. L'y laisser constellerait le rapport de vides.
                if is_marker(texte.strip()):
                    continue
                # Le corps d'une section PEUT contenir un « ## » — dans un bloc de
                # code, où parse_sections n'a pas découpé. Le recomptage plus bas
                # applique la même règle, et c'est la seule raison pour laquelle il
                # ne se trompe pas ici. Le TITRE, lui, est du texte libre lu du
                # front matter : c'est lui que le recomptage attrape.
                corps += [f"### {nom}", "", texte.strip(), ""]
            blocs.append("\n".join(corps).rstrip() + "\n")

        preambule = (
            f"# {self.contract.name}\n\n"
            f"{datetime.date.today().isoformat()} — {len(blocs)} élément(s) aggloméré(s), "
            f"{attendu} fichier(s) dans le répertoire.\n"
        )
        document = preambule + "\n" + "\n".join(blocs)

        # Le compte est refait SUR LE TEXTE RENDU, et non sur la liste qui a servi à
        # l'écrire : compter deux fois la même variable ne prouverait rien.
        #
        # HORS BLOCS DE CODE, par la même règle que parse_sections — un `## ` collé
        # dans une sortie de commande est du contenu. Sans cela le flux de revue
        # échouait sur toute preuve exécutée, en annonçant une perte qui n'existait
        # pas : le pire des deux mondes, un faux positif au message faux.
        rendu = sum(
            1
            for ligne, libre in outside_fences(document)
            if libre and ligne.startswith("## ") and not ligne.startswith("### ")
        )
        if rendu != attendu:
            return fail(
                f"{self.path}: {rendu} élément(s) dans le document pour {attendu} fichier(s) "
                "dans le répertoire — un élément a été perdu ou dédoublé en route"
            )
        return ok(document)

    def merge(self, out: Path | str) -> Result[Path]:
        """L'aggloméré, écrit dans un fichier."""
        text = self.merge_text()
        if not text:
            return Result(text.status, None, text.message)
        target = Path(out)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text.unwrap(), encoding="utf-8")
        except OSError as exc:
            return fail(f"{target}: écriture impossible — {exc.strerror}")
        return ok(target)


def _correspond(valeur: object, critere: FieldValue) -> bool:
    """Un champ vaut-il le critère ? Comparaison textuelle, l'absence exceptée.

    Le front matter vient de TOML, qui n'a pas de valeur nulle : un `None` lu ici
    signifie donc TOUJOURS « le champ n'est pas écrit », jamais « il vaut None ».
    C'est ce qui autorise à réserver le critère vide à l'absence, sans ambiguïté.
    """
    if valeur is None:
        return str(critere) == ""
    return str(valeur) == str(critere)


def _reordering(
    path: Path,
    subject: str,
    action: str,
    avant: Mapping[str, object],
    apres: Mapping[str, object],
) -> list[Change]:
    """Un changement si l'ordre des clés COMMUNES diffère, aucun sinon.

    Les clés communes seulement : un ajout ou un retrait déplace forcément ce qui
    suit, et le signaler deux fois ferait passer une migration banale pour un
    remaniement.
    """
    ordre_avant = [k for k in avant if k in apres]
    ordre_apres = [k for k in apres if k in avant]
    if ordre_avant == ordre_apres:
        return []
    return [Change(path, subject, action)]


def open_list(list_dir: Path | str) -> Result[ListStore]:
    """Ouvre une liste : son contrat est chargé et validé, ou rien n'est rendu."""
    path = Path(list_dir)
    if not path.is_dir():
        return fail(f"{path}: répertoire introuvable")
    r = load_contract(path)
    if not r:
        return Result(r.status, None, r.message)
    return ok(ListStore(path, r.unwrap()))


def _read_definition(definition: Path) -> Result[tuple[str, dict[str, str]]]:
    """Le contrat d'une définition et ses gabarits, LUS ET VALIDÉS EN MÉMOIRE.

    Rien n'est écrit ici, et c'est le point : un contrat de définition invalide
    découvert après un mkdir laisserait une liste à moitié bâtie, que la tentative
    suivante refuserait comme « contrat déjà présent ». L'appelant serait coincé
    entre une erreur qu'il a corrigée et un répertoire qu'il n'a pas créé — c'est
    la raison pour laquelle `derive` construit lui aussi tout en mémoire d'abord.
    """
    contrat = definition / CONTRACT
    if not contrat.is_file():
        return fail(f"{definition}: définition sans contrat — {CONTRACT} attendu")
    try:
        texte = contrat.read_text(encoding="utf-8")
        gabarits = {
            f.name: f.read_text(encoding="utf-8")
            for f in sorted((definition / TEMPLATES).glob("*"))
            if f.is_file()
        }
    except OSError as exc:
        return fail(f"{definition}: définition illisible — {exc.strerror}")

    # Le contrat est jugé ici, pas à la première commande qui ouvrira la liste :
    # une définition fautive doit se dire au moment où on s'en sert, en nommant le
    # fichier de la DÉFINITION, et non plus tard en nommant la copie.
    lu = parse_contract(texte, contrat)
    if not lu:
        return Result(lu.status, None, lu.message)
    return ok((texte, gabarits))


def init_list(
    list_dir: Path | str,
    name: str = "",
    description: str = "",
    definition: Path | str | None = None,
) -> Result[Path]:
    """Crée une liste. Sans `definition`, son contrat squelette. Une liste vide est légitime.

    DEUX SOURCES POSSIBLES POUR LE CONTRAT, et le partage est net :

      - AUCUNE DÉFINITION → LE SQUELETTE, ÉCRIT ICI EN DUR. C'est le seul endroit du
        paquet où un contenu de contrat l'est. Réduit au strict minimum — un `id`,
        un `title`, une section — pour être complété à la main, jamais pour servir
        de modèle à quoi que ce soit.
      - UNE DÉFINITION → SON CONTRAT, COPIÉ TEL QUEL, et ses gabarits avec lui.

    POURQUOI UNE DÉFINITION PEUT CE QU'UN GABARIT NE POUVAIT PAS. Un gabarit vit
    dans le `.list/templates/` d'une liste EXISTANTE, et `init` s'adresse justement
    au cas où aucune liste n'existe : il ne pouvait donc pas en venir. Une définition
    vit hors de tout répertoire-liste (cf. definitions.py) — c'est exactement ce qui
    la rend disponible quand il n'y a encore rien.

    ELLE FAIT AUTORITÉ LE TEMPS DE CET APPEL, ET PAS AU-DELÀ. La liste créée porte
    dès lors son propre contrat, que toute commande relira depuis
    `<liste>/.list/contract.toml`. Rien ne les resynchronise ensuite, et c'est voulu :
    une liste que son projet a délibérément redéfinie ne doit pas se faire rattraper
    par la définition qui l'a semée.

    LES DEUX VALEURS LIBRES PASSENT PAR LE SÉRIALISEUR, jamais par une
    interpolation. Un `--name 'ma "liste"'` interpolé produisait un contrat que
    `tomllib` refuse — et `init` rendait 0 : un échec ouvert, exactement ce que ce
    paquet existe pour supprimer. Le guillemet est un caractère de nom parfaitement
    ordinaire ; c'est l'écriture qui doit le supporter. Elles ne s'appliquent qu'au
    squelette : une définition porte déjà les siennes, et les écraser ferait mentir
    le `diff` qui prouve qu'une semence est bien la copie de son original.
    """
    path = Path(list_dir)
    target = path / LIST_DIR / CONTRACT
    if target.exists():
        return fail(f"{path}: contrat déjà présent — {LIST_DIR}/contract.toml")

    if definition is not None:
        lu = _read_definition(Path(definition))
        if not lu:
            return Result(lu.status, None, lu.message)
        texte, gabarits = lu.unwrap()
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            _ = target.write_text(texte, encoding="utf-8")
            if gabarits:
                (target.parent / TEMPLATES).mkdir(exist_ok=True)
                for nom, corps in gabarits.items():
                    _ = (target.parent / TEMPLATES / nom).write_text(corps, encoding="utf-8")
        except OSError as exc:
            return fail(f"{target}: écriture impossible — {exc.strerror}")
        return ok(target)

    try:
        nom = dump_value(name or path.name, "name")
        desc = dump_value(description or OPTIONAL, "description")
    except SerialiseError as exc:
        return fail(f"{target}: {exc}")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            f"name = {nom}\n"
            f"description = {desc}\n"
            "\n[fields.id]\n"
            'type = "slug"\n'
            "\n[fields.title]\n"
            'type = "text"\n'
            "required = true\n"
            "\n[sections]\n"
            'required = ["Constat"]\n'
            "optional = []\n",
            encoding="utf-8",
        )
    except OSError as exc:
        return fail(f"{target}: écriture impossible — {exc.strerror}")
    return ok(target)
