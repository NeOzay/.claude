"""rapport_audit — le rapport d'un audit de Chantier, un fichier TOML par audit.

PORTÉE : le modèle du rapport et son contrôle (`modele`), la pose d'un rapport et ses
vérifications (`pose`), le rangement et l'ajout des dettes (`dettes`), le rendu en Markdown
(`export`). La commande `audit` les expose ; elle n'y ajoute aucune logique.

LE PAQUET `gabarit` SE TROUVE PAR SON LIEN DE `bin/`, comme dans
`skills/list-dir/scripts/listdir/__init__.py`, qui en donne le raisonnement : le `bin/` du dépôt
d'abord, en remontant, le PATH seulement en repli, et un échec nommé sinon. Ceci vit ici, avant
tout import d'un module du paquet : c'est le seul point par lequel passe chacun d'eux.
"""

import shutil
import sys
from pathlib import Path

if (
    _gabarit := next(
        (
            str(a / "bin" / "gabarit")
            for a in Path(__file__).resolve().parents
            if (a / "bin" / "gabarit").exists()
        ),
        None,
    )
    or shutil.which("gabarit")
) is None:
    raise ImportError(
        "rapport_audit exige le paquet gabarit : aucun bin/gabarit en remontant depuis "
        f"{Path(__file__).resolve().parent}, ni de commande « gabarit » dans le PATH"
    )
if (_scripts := str(Path(_gabarit).resolve().parent)) not in sys.path:
    sys.path.append(_scripts)
