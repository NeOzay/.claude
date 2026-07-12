# Qualité — Go

## Patterns bloquants ❌

```go
result, _ := func()                          // erreur ignorée
fmt.Sprintf("SELECT ... WHERE id=%s", id)    // injection SQL
InsecureSkipVerify: true                     // SSL désactivé
os/exec avec input utilisateur non validé   // injection commande
```

## Avertissements ⚠️

```go
panic("message")               // dans une lib (utiliser error return)
go func() { ... }()            // goroutine sans context ni WaitGroup
log.Fatal(...)                 // dans du code non-main
time.Sleep(...)                // dans du code de prod (préférer ticker)
```

## Points à vérifier

- Toutes les erreurs sont-elles gérées (pas de `_` sur une erreur) ?
- Les goroutines ont-elles une gestion de leur durée de vie (context, WaitGroup) ?
- Les interfaces sont-elles utilisées plutôt que les types concrets dans les signatures ?
- Les structs exportées ont-elles des commentaires de documentation ?
- Les ressources (fichiers, connexions DB) ont-elles un `defer Close()` ?
- Les tests couvrent-ils les cas d'erreur retournée ?

## Taille et complexité

- Fonction > 40 lignes → ⚠️ à découper
- Fichier > 300 lignes → ⚠️ envisager séparation en packages
- Cyclomatic complexity > 10 → ⚠️ à refactorer
