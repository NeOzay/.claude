#!/usr/bin/env python3
"""Point d'entrée en ligne de commande des lexiques.

AUCUNE LOGIQUE MÉTIER ICI. Ce fichier parse des arguments, appelle `lexique.py` et traduit
le résultat en code de sortie.

LE NOM PORTE UN TIRET, comme `gabarit-cli.py` : il n'est pas importable, et ne dispute pas son
nom au module `lexique` rangé à côté. La commande s'appelle `lexique` par son lien de `bin/`.

DEUX RÉGIMES D'ÉCHEC POUR TROIS COMMANDES :
- `init` échoue fermé — 0 lexique posé, son chemin sur stdout ; 1 fichier déjà présent ;
- `liste` échoue fermé — 0 conforme, 1 constat ou lexique malformé, 2 erreur d'appel ; un
  lexique vide ou absent se dit sur stderr, sans toucher au code ;
- `session` échoue OUVERT — sortie 0 quoi qu'il arrive : c'est un hook `SessionStart`, et un
  rappel n'a jamais de raison d'empêcher une session de démarrer. Ses alertes vont au contexte.

PAS DE RÉ-EXÉCUTION DANS LE VENV, contrairement à `gabarit-cli.py` : le module n'a que la stdlib
pour horizon, et le hook doit rester rapide.
"""

import sys

# `noqa: UP036` : ruff juge ce bloc mort parce que target-version vaut py312. Il n'existe que
# pour le Python plus ancien qui exécuterait ce fichier — et `session` y reste silencieux.
if sys.version_info < (3, 12):  # noqa: UP036
    if sys.argv[1:2] == ["session"]:  # pyright: ignore[reportUnreachable]
        raise SystemExit(0)
    v = ".".join(str(n) for n in sys.version_info[:3])
    sys.stderr.write(f"lexique exige Python >= 3.12, trouvé {v} ({sys.executable}).\n")
    raise SystemExit(2)

import argparse
import os
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lexique import amorcer, annonce_session, chemin_global, chemin_local, lister, racine_projet


def _init(projet: Path) -> int:
    r = amorcer(chemin_local(projet))
    if r.value is None:
        sys.stderr.write(r.message + "\n")
        return 1
    print(r.value)
    return 0


def _liste(projet: Path) -> int:
    r = lister(chemin_global(), chemin_local(projet))
    if r.value is None:
        sys.stderr.write(r.message + "\n")
        return 1
    for t in r.value.termes:
        print(f"{t.niveau}\t{t.terme}\t{t.lien}")
    # Un avis sort sur stderr sans toucher au code, comme l'avertissement de `gabarit`.
    for a in r.value.avis:
        sys.stderr.write(a + "\n")
    for c in r.value.constats:
        sys.stderr.write(c + "\n")
    return 1 if r.value.constats else 0


def _session() -> int:
    # ÉCHEC OUVERT : une exception ici ne doit jamais bloquer le démarrage d'une session.
    try:
        # `$CLAUDE_PROJECT_DIR` TEL QUEL, sans remonter à la racine git : dans un monodépôt, le
        # sous-projet ouvert porte son propre lexique, et c'est lui que la session doit recevoir.
        projet = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
        sys.stdout.write(annonce_session(chemin_global(), chemin_local(projet), projet))
    except Exception as e:
        sys.stderr.write(f"lexique session : {e}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="lexique", description="Lexiques global et local.")
    sous = parser.add_subparsers(dest="commande", required=True)
    liste = sous.add_parser("liste", help="les termes réservés, leur niveau, leurs conflits")
    liste.add_argument("--projet", type=Path, help="défaut : la racine git d'ici, ou ici")
    init = sous.add_parser("init", help="pose le lexique local d'un projet, en-tête seul")
    init.add_argument("--projet", type=Path, help="défaut : la racine git d'ici, ou ici")
    sous.add_parser("session", help="le lexique local, pour le hook SessionStart")
    args = parser.parse_args()

    if cast("str", args.commande) == "session":
        return _session()
    projet = cast("Path | None", args.projet) or racine_projet(Path.cwd())
    return _init(projet) if cast("str", args.commande) == "init" else _liste(projet)


if __name__ == "__main__":
    raise SystemExit(main())
