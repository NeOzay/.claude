# Exploration : ajout d'un onglet "Presets de prétraitement OCR"

Note : tâche d'exploration en lecture seule (pas d'implémentation demandée
pour l'instant). Ce fichier consigne les points clés trouvés pour préparer
un futur plan d'implémentation.

## Fichiers clés
- src/manga_trad/gui/ocr_test_tab.py — UI de composition d'étapes réordonnables
- src/manga_trad/core/ocr/preprocessing.py — classes de préprocesseurs + PRESETS (dict figé)
- src/manga_trad/gui/main_window.py — _prep_combo, _on_prep_changed, _on_ocr_all_requested, _central_tabs, _sync_ocr_test_source
- src/manga_trad/gui/side_panel.py — pattern combo preset traduction (_preset, _load_presets, _on_preset_changed)
- src/manga_trad/db/repository.py + models.py + schema.sql — table `presets` (traduction) avec colonne JSON `glossary`, pattern de sérialisation JSON réutilisable (json.dumps/json.loads) pour tags/ocr_results/glossary

## Constat principal
- PRESETS dans preprocessing.py est un dict Python en dur, non extensible sans redéploiement de code (pas de DB, pas de JSON externe).
- Le système "presets de traduction" (table `presets`, colonne glossary JSON) est un bon modèle de sérialisation DB pour un nouveau système "presets de prétraitement OCR" : nouvelle table avec colonne `steps` JSON (liste ordonnée de {type, params}).
- ocr_test_tab.py construit déjà dynamiquement une pipeline ordonnée de Preprocessor à partir de widgets réordonnables (QVBoxLayout + boutons ▲▼, pas QListWidget) — cette logique de construction/réordonnancement est réutilisable telle quelle pour un futur onglet Presets.

Voir réponse détaillée dans la conversation pour l'analyse complète (numéros de ligne, code, architecture).
