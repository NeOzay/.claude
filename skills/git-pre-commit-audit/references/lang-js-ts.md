# Qualité — JavaScript / TypeScript / React

## Patterns bloquants ❌

```js
debugger;                         // breakpoint en production
innerHTML = variable              // XSS potentiel
eval(variable)                    // exécution arbitraire
document.write(variable)          // XSS
dangerouslySetInnerHTML sans sanitize  // XSS React
`SELECT ... WHERE id = ${var}`    // injection SQL
exec('cmd ' + userInput)          // injection commande
rejectUnauthorized: false         // SSL désactivé
```

## Avertissements ⚠️

```js
console.log(...)      // debug oublié
var x = ...           // préférer const/let
function(...: any)    // type TS non justifié
@ts-ignore            // suppression de typage sans explication
as any                // cast dangereux
somePromise()         // Promise sans .catch() ni try/catch
```

## Points à vérifier

- Les fonctions `async` ont-elles un `try/catch` ou `.catch()` ?
- Les fonctions exportées modifiées ont-elles changé de signature ?
- Les imports ajoutés sont-ils tous utilisés ?
- Les magic numbers sont-ils extraits en constantes nommées ?
- Les composants React : les props ont-elles des types définis ?
- `useEffect` : les dépendances du tableau sont-elles correctes ?

## Taille et complexité

- Fonction > 50 lignes → ⚠️ à découper
- Imbrication > 3 niveaux (if/callback/promise) → ⚠️ à refactorer
- Fichier > 300 lignes → ℹ️ envisager une séparation
