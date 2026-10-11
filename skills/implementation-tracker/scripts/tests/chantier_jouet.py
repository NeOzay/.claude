"""Le Chantier jouet : son slug, que les tests importent.

POURQUOI CE MODULE N'EST PAS `conftest.py` : plusieurs suites de ce dépôt ont leur
`conftest.py`. En mode d'import « prepend », pytest dérive le nom de module du basename : un
`from conftest import …` résout alors vers l'un ou l'autre selon l'ordre de collecte, et une
commande qui lance plusieurs suites échoue à la collecte. Un nom unique supprime l'ambiguïté ;
`conftest.py` ne garde que les fixtures, qui ne s'importent jamais. Même raisonnement que
`scripts/tests/depot_jouet.py`.
"""

SLUG = "contexte-tracker"
