# Qualité — Python

## Patterns bloquants ❌

```python
eval(variable)                  # exécution arbitraire
exec(variable)                  # exécution arbitraire
pickle.loads(data)              # désérialisation non sûre
subprocess.run(..., shell=True) # injection commande
f"SELECT ... WHERE id={var}"   # injection SQL
verify=False                    # SSL désactivé (requests)
render_template_string(input)   # SSTI
```

## Avertissements ⚠️

```python
except:                    # bare except — masque toutes les erreurs
except Exception: pass     # exception silencieuse
def func(data=[]):         # mutable default argument (piège classique)
from module import *       # pollution du namespace
if value == None:          # utiliser `is None`
print(...)                 # debug oublié
```

## Points à vérifier

- Les fonctions publiques ont-elles des type hints (`def func(x: int) -> str`) ?
- Les fonctions publiques ont-elles une docstring ?
- Les ressources (fichiers, connexions) utilisent-elles `with` ?
- Les exceptions levées sont-elles spécifiques (pas `Exception` générique) ?
- Les nouvelles classes héritent-elles correctement ?
- `__all__` est-il défini pour les modules exportés ?

## Taille et complexité

- Fonction > 40 lignes → ⚠️ à découper
- Classe > 200 lignes → ⚠️ envisager une séparation
- Imbrication > 3 niveaux → ⚠️ extraire en sous-fonctions
