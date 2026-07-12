# Référence de configuration .emmyrc.json

Ce document décrit toutes les options de configuration du serveur EmmyLua, telles que définies dans le schéma JSON officiel.

Le fichier `.emmyrc.json` (ou `.luarc.json`) doit être placé à la racine du workspace.

## Table des matières

1. [Squelette complet](#squelette-complet)
2. [workspace](#workspace)
3. [runtime](#runtime)
4. [diagnostics](#diagnostics)
5. [completion](#completion)
6. [hint (Inlay Hints)](#hint-inlay-hints)
7. [hover](#hover)
8. [codeLens](#codelens)
9. [references](#references)
10. [semanticTokens](#semantictokens)
11. [signature](#signature)
12. [strict](#strict)
13. [format](#format)
14. [doc](#doc)
15. [resource](#resource)
16. [documentColor](#documentcolor)
17. [inlineValues](#inlinevalues)
18. [codeAction](#codeaction)

---

## Squelette complet

```json
{
  "$schema": "https://raw.githubusercontent.com/EmmyLuaLs/emmylua-analyzer-rust/refs/heads/main/crates/emmylua_code_analysis/resources/schema.json",
  "workspace": {},
  "runtime": {},
  "diagnostics": {},
  "completion": {},
  "hint": {},
  "hover": {},
  "codeLens": {},
  "references": {},
  "semanticTokens": {},
  "signature": {},
  "strict": {},
  "format": {},
  "doc": {},
  "resource": {},
  "documentColor": {},
  "inlineValues": {},
  "codeAction": {}
}
```

---

## workspace

Configuration de l'espace de travail et des bibliothèques.

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `library` | `(string \| LibraryConfig)[]` | `[]` | Chemins de bibliothèques externes à charger. Supporte `$VIMRUNTIME` comme variable. |
| `workspaceRoots` | `string[]` | `[]` | Racines supplémentaires du workspace à analyser. |
| `ignoreDir` | `string[]` | `[]` | Répertoires à ignorer. |
| `ignoreGlobs` | `string[]` | `[]` | Patterns glob à ignorer (ex: `["**/*.generated.lua"]`). |
| `encoding` | `string` | `"utf-8"` | Encodage des fichiers. |
| `moduleMap` | `object[]` | `[]` | Mapping de modules personnalisé. |
| `packageDirs` | `string[]` | `[]` | Répertoires de packages. |
| `preloadFileSize` | `integer` | `0` | Taille max des fichiers à pré-charger (0 = pas de limite). |
| `enableReindex` | `boolean` | `false` | Activer la ré-indexation périodique. |
| `reindexDuration` | `integer` | `5000` | Intervalle de ré-indexation (ms). |

### Format LibraryConfig

Quand une bibliothèque nécessite un filtrage, utiliser un objet :

```json
{
  "workspace": {
    "library": [
      "/chemin/simple",
      {
        "path": "/chemin/vers/lib",
        "ignoreDir": ["tests", "examples"],
        "ignoreGlobs": ["**/*.test.lua"]
      }
    ]
  }
}
```

### Exemple pour Neovim

```json
{
  "workspace": {
    "library": ["$VIMRUNTIME"],
    "workspaceRoots": ["lua"]
  }
}
```

### Format moduleMap

Le `moduleMap` permet de remapper les noms de modules utilisés dans `require` via des expressions régulières. Chaque entrée est un objet avec `pattern` (regex de matching) et `replace` (chaîne de remplacement avec références de groupe `$1`, `$2`, etc.) :

```json
{
  "workspace": {
    "moduleMap": [
      {
        "pattern": "^lib(.*)$",
        "replace": "script$1"
      },
      {
        "pattern": "^myapp%.(.*)$",
        "replace": "src/$1"
      }
    ]
  }
}
```

Avec cette configuration, `require("lib.utils")` est résolu vers le chemin `script/utils.lua`, et `require("myapp.core")` vers `src/core.lua`. Ce mécanisme est utile quand l'arborescence de fichiers ne correspond pas aux noms de modules conventionnels.

---

## runtime

Configuration du runtime Lua.

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `version` | `enum` | `"LuaLatest"` | Version Lua cible. Valeurs : `Lua5.1`, `Lua5.2`, `Lua5.3`, `Lua5.4`, `Lua5.5`, `LuaJIT`, `LuaLatest`. |
| `requirePattern` | `string[]` | `[]` | Patterns de résolution require (ex: `["?.lua", "?/init.lua"]`). |
| `requireLikeFunction` | `string[]` | `[]` | Fonctions traitées comme `require` (ex: `["dofile", "loadfile"]`). |
| `extensions` | `string[]` | `[]` | Extensions de fichiers Lua (ex: `[".lua", ".lua.txt"]`). |
| `special` | `object` | `{}` | Fonctions spéciales avec rôle sémantique. |
| `nonstandardSymbol` | `string[]` | `[]` | Symboles non-standard autorisés. |
| `frameworkVersions` | `string[]` | `[]` | Versions de framework actives. |

### Symboles non-standard supportés

`//`, `/**/`, `` ` ``, `+=`, `-=`, `*=`, `/=`, `%=`, `^=`, `//=`, `|=`, `&=`, `<<=`, `>>=`, `||`, `&&`, `!`, `!=`, `continue`

### Exemples

```json
{
  "runtime": {
    "version": "LuaJIT",
    "requirePattern": ["?.lua", "?/init.lua"],
    "requireLikeFunction": ["import"],
    "nonstandardSymbol": ["+=", "-=", "!=", "continue"]
  }
}
```

---

## diagnostics

Configuration des diagnostics et de l'analyse statique.

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `enable` | `boolean` | `true` | Activer les diagnostics. |
| `disable` | `DiagnosticCode[]` | `[]` | Diagnostics désactivés. |
| `enables` | `DiagnosticCode[]` | `[]` | Diagnostics à forcer activés. |
| `severity` | `object` | `{}` | Sévérité personnalisée par diagnostic. |
| `globals` | `string[]` | `[]` | Variables globales connues (ne lèvent pas `undefined-global`). |
| `globalsRegex` | `string[]` | `[]` | Regex de variables globales connues. |
| `diagnosticInterval` | `integer` | `500` | Délai entre modification et analyse (ms). |

### Codes de diagnostic

| Code | Description | Sévérité par défaut |
|---|---|---|
| `syntax-error` | Erreur de syntaxe Lua | error |
| `doc-syntax-error` | Erreur de syntaxe dans une annotation | error |
| `type-not-found` | Type référencé non trouvé | warning |
| `missing-return` | Return manquant dans une branche | warning |
| `param-type-mismatch` | Type de paramètre incorrect | warning |
| `missing-parameter` | Paramètre obligatoire manquant | warning |
| `redundant-parameter` | Paramètre en trop | warning |
| `unreachable-code` | Code jamais exécuté | hint |
| `unused` | Variable/import non utilisé(e) | hint |
| `undefined-global` | Variable globale non définie | warning |
| `deprecated` | Utilisation d'un élément déprécié | hint |
| `access-invisible` | Accès à un membre privé/protégé | warning |
| `discard-returns` | Valeur de retour @nodiscard ignorée | warning |
| `undefined-field` | Champ non déclaré sur un type | warning |
| `local-const-reassign` | Réassignation d'une constante locale | error |
| `iter-variable-reassign` | Réassignation d'une variable d'itérateur | warning |
| `duplicate-type` | Type déclaré en double | warning |
| `redefined-local` | Variable locale redéfinie | hint |
| `redefined-label` | Label redéfini | warning |
| `code-style-check` | Violation de style de code | hint |
| `need-check-nil` | Valeur possiblement nil non vérifiée | warning |
| `await-in-sync` | Appel async dans une fonction sync | warning |
| `annotation-usage-error` | Annotation mal utilisée | warning |
| `return-type-mismatch` | Type de retour incorrect | warning |
| `missing-return-value` | Valeur de retour manquante | warning |
| `redundant-return-value` | Valeur de retour en trop | warning |
| `undefined-doc-param` | @param pour un paramètre inexistant | warning |
| `duplicate-doc-field` | @field en double | warning |
| `unknown-doc-tag` | Annotation inconnue | warning |
| `missing-fields` | Champs obligatoires manquants | warning |
| `inject-field` | Injection d'un champ non déclaré | warning |
| `circle-doc-class` | Héritage circulaire de @class | error |
| `incomplete-signature-doc` | Documentation de signature incomplète | hint |
| `missing-global-doc` | Documentation manquante pour un global | hint |
| `assign-type-mismatch` | Type d'assignation incorrect | warning |
| `duplicate-require` | require en double | hint |
| `non-literal-expressions-in-assert` | Expression non-littérale dans assert | hint |
| `unbalanced-assignments` | Nombre d'assignations déséquilibré | warning |
| `unnecessary-assert` | Assert inutile | hint |
| `unnecessary-if` | Condition if inutile | hint |
| `duplicate-set-field` | Champ défini en double via assignation | warning |
| `duplicate-index` | Index en double dans une table | warning |
| `generic-constraint-mismatch` | Contrainte générique non respectée | warning |
| `cast-type-mismatch` | Cast de type incompatible | warning |
| `require-module-not-visible` | Module require non visible | warning |
| `enum-value-mismatch` | Valeur enum incorrecte | warning |
| `preferred-local-alias` | Alias local préférable | hint |
| `read-only` | Écriture dans une valeur en lecture seule | error |
| `global-in-non-module` | Global défini hors scope module | warning |
| `attribute-param-type-mismatch` | Type de paramètre d'attribut incorrect | warning |
| `attribute-missing-parameter` | Paramètre d'attribut manquant | warning |
| `attribute-redundant-parameter` | Paramètre d'attribut en trop | warning |
| `invert-if` | If inversable pour simplification | hint |
| `call-non-callable` | Appel d'une valeur non-callable | error |

### Sévérités disponibles

`error`, `warning`, `information`, `hint`

### Exemple

```json
{
  "diagnostics": {
    "disable": ["unused", "undefined-global"],
    "globals": ["vim", "describe", "it", "before_each", "after_each"],
    "globalsRegex": ["^PLUGIN_"],
    "severity": {
      "undefined-field": "hint",
      "need-check-nil": "information"
    },
    "diagnosticInterval": 300
  }
}
```

---

## completion

Configuration de l'auto-complétion.

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `enable` | `boolean` | `true` | Activer l'auto-complétion. |
| `autoRequire` | `boolean` | `true` | Insérer automatiquement `require` pour les modules externes. |
| `autoRequireFunction` | `string` | `"require"` | Fonction utilisée pour l'auto-require. |
| `autoRequireSeparator` | `string` | `"."` | Séparateur dans les chemins d'auto-require. |
| `autoRequireNamingConvention` | `enum` | `"keep"` | Convention de nommage pour l'auto-require. Valeurs : `keep`, `snake-case`, `pascal-case`, `camel-case`, `keep-class`. |
| `callSnippet` | `boolean` | `false` | Insérer un snippet complet lors de la complétion de fonctions. |
| `postfix` | `string` | `"@"` | Symbole déclenchant la complétion postfix. Valeurs : `null`, `"@"`, `"."`, `":"`. |
| `baseFunctionIncludesName` | `boolean` | `true` | Inclure le nom dans la complétion de `function`. |

---

## hint (Inlay Hints)

Configuration des indications inline dans le code.

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `enable` | `boolean` | `true` | Activer les inlay hints. |
| `paramHint` | `boolean` | `true` | Noms des paramètres dans les appels de fonctions. |
| `localHint` | `boolean` | `true` | Types des variables locales. |
| `indexHint` | `boolean` | `true` | Index nommés des tableaux. |
| `overrideHint` | `boolean` | `true` | Indicateur de surcharge de méthode. |
| `metaCallHint` | `boolean` | `true` | Indicateur d'appel via `__call`. |
| `enumParamHint` | `boolean` | `false` | Nom de l'enum quand une valeur littérale est passée. |

---

## hover

Configuration des informations au survol.

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `enable` | `boolean` | `true` | Activer les informations au survol. |
| `customDetail` | `integer \| null` | `null` | Niveau de détail (1-255). `null` = niveau par défaut. |

---

## codeLens

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `enable` | `boolean` | `true` | Activer les code lens. |

---

## references

Configuration de la recherche de références.

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `enable` | `boolean` | `true` | Activer la recherche de références. |
| `fuzzySearch` | `boolean` | `true` | Recherche floue en fallback. |
| `shortStringSearch` | `boolean` | `false` | Rechercher aussi dans les chaînes courtes. |

---

## semanticTokens

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `enable` | `boolean` | `true` | Activer les tokens sémantiques. |
| `renderDocumentationMarkup` | `boolean` | `true` | Rendre le markup dans la documentation. |

---

## signature

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `detailSignatureHelper` | `boolean` | `true` | Afficher les détails dans l'aide de signature. |

---

## strict

Options de mode strict pour renforcer l'analyse.

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `requirePath` | `boolean` | `false` | Mode strict pour les chemins require (doit commencer depuis la racine). |
| `typeCall` | `boolean` | `false` | Mode strict pour les appels de type. |
| `arrayIndex` | `boolean` | `true` | Vérification stricte des index de tableaux. |
| `metaOverrideFileDefine` | `boolean` | `true` | Les fichiers meta peuvent surcharger les définitions. |
| `requireExportGlobal` | `boolean` | `false` | Exiger que les modules exportent uniquement des globaux. |
| `docBaseConstMatchBaseType` | `boolean` | `true` | Les constantes doc doivent correspondre au type de base. |

---

## format

Configuration du formatage de code.

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `useDiff` | `boolean` | `false` | Utiliser l'algorithme diff pour le formatage. |
| `externalTool` | `ExternalTool \| null` | `null` | Outil de formatage externe. |
| `externalToolRangeFormat` | `ExternalTool \| null` | `null` | Outil de formatage externe pour les sélections. |

### Format ExternalTool

```json
{
  "format": {
    "externalTool": {
      "program": "stylua",
      "args": ["--stdin-filepath", "${INPUT}", "-"],
      "timeout": 5000
    }
  }
}
```

---

## doc

Configuration de la documentation.

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `syntax` | `enum` | `"md"` | Syntaxe de la documentation. Valeurs : `none`, `md`, `myst`, `rst`. |
| `knownTags` | `string[]` | `[]` | Tags de documentation personnalisés reconnus (évite `unknown-doc-tag`). |
| `privateName` | `string[]` | `[]` | Patterns de noms traités comme privés (ex: `["m_*"]`). |
| `rstDefaultRole` | `string \| null` | `null` | Rôle par défaut pour RST/MyST. |
| `rstPrimaryDomain` | `string \| null` | `null` | Domaine principal pour RST/MyST. |

---

## resource

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `paths` | `string[]` | `[]` | Chemins de ressources pour la complétion de chemins dans les chaînes. |

---

## documentColor

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `enable` | `boolean` | `true` | Activer la détection et le preview de couleurs dans les chaînes. |

---

## inlineValues

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `enable` | `boolean` | `true` | Afficher les valeurs inline durant le débogage. |

---

## codeAction

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `insertSpace` | `boolean` | `false` | Ajouter un espace après `---` lors de l'insertion de `@diagnostic disable-next-line`. |

---

## Exemple de configuration complète

```json
{
  "$schema": "https://raw.githubusercontent.com/EmmyLuaLs/emmylua-analyzer-rust/refs/heads/main/crates/emmylua_code_analysis/resources/schema.json",
  "workspace": {
    "library": ["$VIMRUNTIME"],
    "workspaceRoots": ["lua"],
    "ignoreGlobs": ["**/*.test.lua"]
  },
  "runtime": {
    "version": "LuaJIT",
    "requirePattern": ["lua/?.lua", "lua/?/init.lua"]
  },
  "diagnostics": {
    "disable": ["unused"],
    "globals": ["vim"],
    "severity": {
      "undefined-global": "error",
      "need-check-nil": "hint"
    }
  },
  "completion": {
    "autoRequire": true,
    "callSnippet": true
  },
  "hint": {
    "enable": true,
    "paramHint": true,
    "localHint": false
  },
  "strict": {
    "requirePath": true,
    "typeCall": true
  },
  "format": {
    "externalTool": {
      "program": "stylua",
      "args": ["--stdin-filepath", "${INPUT}", "-"],
      "timeout": 5000
    }
  },
  "doc": {
    "syntax": "md",
    "privateName": ["m_*", "_*"]
  }
}
```
