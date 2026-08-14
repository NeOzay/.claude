# Qualité — Java / Kotlin

## Patterns bloquants ❌

```java
// Java
"SELECT ... WHERE id=" + id           // injection SQL (JDBC)
Runtime.getRuntime().exec(input)      // injection commande
new ObjectInputStream(stream)         // désérialisation non sûre
ALLOW_ALL_HOSTNAME_VERIFIER           // SSL désactivé

// Kotlin
val result = dangerousCall()!!        // null assertion non justifiée
```

## Avertissements ⚠️

```java
// Java
} catch (Exception e) { }            // exception avalée silencieusement
e.printStackTrace()                   // log inapproprié en prod
System.out.println(...)              // debug oublié
if (str == "value")                  // comparaison String par référence

// Kotlin
val x: Any                           // type trop générique
```

## Points à vérifier

**Java :**
- Les requêtes JDBC utilisent-elles `PreparedStatement` ?
- Les `equals()` et `hashCode()` sont-ils cohérents ?
- Les ressources utilisent-elles `try-with-resources` ?
- Les champs sont-ils `private` avec accesseurs si nécessaire ?

**Kotlin :**
- Les `!!` sont-ils tous justifiés ? (chaque occurrence doit être expliquée)
- Les `data class` utilisent-elles `val` (immutabilité) ?
- Les `sealed class` sont-elles préférées aux enum pour les états ?
- Les `coroutines` ont-elles une gestion d'exception (`CoroutineExceptionHandler`) ?

## Taille et complexité

- Méthode > 40 lignes → ⚠️ à découper
- Classe > 300 lignes → ⚠️ envisager séparation
- > 3 niveaux d'imbrication → ⚠️ extraire en méthodes privées
