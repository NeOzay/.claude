"""gabarit — un fichier préstructuré à remplir, créé depuis une semence.

Un gabarit est UN fichier : un front matter TOML, des sections, un contrat qui dit ce
qu'ils doivent contenir. Rien ici ne connaît de répertoire ni de liste — `listdir`
en dépend pour tout ce qui concerne un fichier, jamais l'inverse.

La surface publique est ce que __all__ énumère, et rien d'autre.
"""

__all__: list[str] = []
