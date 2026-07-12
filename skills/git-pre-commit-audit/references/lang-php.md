# Qualité — PHP

## Patterns bloquants ❌

```php
"SELECT ... WHERE id=" . $_GET['id']   // injection SQL
echo $_GET['x']                         // XSS direct
include($_GET['page'])                  // LFI
system($input) / exec($input)          // injection commande
unserialize($data)                      // désérialisation non sûre
extract($_POST)                         // injection de variables
```

## Avertissements ⚠️

```php
@file_get_contents(...)    // erreur silencieuse
die("Error: " . $msg)      // exposition d'info en prod
var_dump($var)             // debug oublié
print_r($var)              // debug oublié
$$variable                 // variable variable (dangereux)
```

## Points à vérifier

- Les requêtes SQL utilisent-elles des requêtes préparées (`PDO::prepare`) ?
- Les sorties HTML sont-elles échappées (`htmlspecialchars`) ?
- Les uploads de fichiers valident-ils le type MIME côté serveur ?
- Les sessions utilisent-elles `session_regenerate_id()` après login ?
- Les mots de passe sont-ils hashés avec `password_hash()` ?

## Taille et complexité

- Fonction > 40 lignes → ⚠️ à découper
- Fichier > 300 lignes sans namespace → ⚠️ à refactorer
