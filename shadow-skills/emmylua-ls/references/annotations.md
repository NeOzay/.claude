# Référence des annotations EmmyLua

EmmyLua utilise des commentaires spéciaux préfixés par `---` (trois tirets) pour enrichir l'analyse statique et le système de types. Ces annotations sont compatibles avec le format EmmyLua et LuaCATS.

## Table des matières

1. [@class](#class)
2. [@field](#field)
3. [@param](#param)
4. [@return](#return)
5. [@type](#type)
6. [@alias](#alias)
7. [@enum](#enum)
8. [@generic](#generic)
9. [@overload](#overload)
10. [@async](#async)
11. [@deprecated](#deprecated)
12. [@private / @protected / @package](#visibilité)
13. [@diagnostic](#diagnostic)
14. [@cast](#cast)
15. [@operator](#operator)
16. [@nodiscard](#nodiscard)
17. [@version](#version)
18. [@see](#see)
19. [@namespace](#namespace)
20. [@using](#using)
21. [@mapping](#mapping)
22. [@source](#source)
23. [@vararg](#vararg)
24. [@meta](#meta)
25. [Formatage des commentaires](#formatage-des-commentaires)

---

## @class

Déclare une classe. Supporte l'héritage simple et multiple, ainsi que les génériques.

### Syntaxe

```
---@class NomClasse [: Parent1, Parent2]
```

### Exemples

```lua
---@class Animal
---@field name string
---@field legs number
local Animal = {}

function Animal:walk()
  print(self.name .. " marche avec " .. self.legs .. " pattes")
end

-- Héritage
---@class Chat : Animal
---@field indoor boolean
local Chat = {}

-- Héritage multiple
---@class ChatDomestique : Animal, Adoptable
local ChatDomestique = {}

-- Classe générique
---@class Container<T>
---@field items T[]
---@field count number
local Container = {}

---@param item T
function Container:add(item)
  table.insert(self.items, item)
  self.count = self.count + 1
end
```

### Notes

- La classe est associée à la variable locale qui suit immédiatement l'annotation.
- Les champs doivent être déclarés via `@field` avant la variable locale.
- L'héritage est spécifié avec `:` suivi des classes parentes séparées par des virgules.
- Les génériques sont déclarés entre `<>` après le nom de la classe.

---

## @field

Déclare un champ sur une classe. Doit être placé entre `@class` et la variable locale.

### Syntaxe

```
---@field [visibilité] nom type [description]
---@field [visibilité] [index_type] type [description]
```

### Visibilités

- `public` (défaut) : accessible partout
- `protected` : accessible dans la classe et ses enfants
- `private` : accessible uniquement dans la classe
- `package` : accessible uniquement dans le fichier

### Exemples

```lua
---@class Personne
---@field name string Le nom complet
---@field age number L'âge en années
---@field private _id number Identifiant interne
---@field protected _cache table Cache interne
---@field [string] any Champs dynamiques string
local Personne = {}

-- Champ optionnel
---@class Config
---@field host string
---@field port? number      -- optionnel (accepte nil)
---@field timeout? number
local Config = {}

-- Champ avec type fonction
---@class EventEmitter
---@field on fun(self: EventEmitter, event: string, callback: fun(...: any))
---@field emit fun(self: EventEmitter, event: string, ...: any)
local EventEmitter = {}

-- Indexeur typé
---@class StringMap
---@field [string] string
local StringMap = {}
```

---

## @param

Déclare le type d'un paramètre de fonction.

### Syntaxe

```
---@param nom type [description]
---@param nom? type [description]   -- paramètre optionnel
```

### Exemples

```lua
---@param name string Le nom de l'utilisateur
---@param age number L'âge
---@param options? table Options facultatives
function createUser(name, age, options) end

-- Paramètre de type fonction
---@param callback fun(result: string, err?: string)
function fetchData(callback) end

-- Paramètre variadic
---@param ... string
function concat(...) end

-- Type union
---@param value string|number|boolean
function serialize(value) end

-- Méthode avec self implicite
---@param target Vector3
function Entity:moveTo(target) end
```

---

## @return

Déclare le type de retour d'une fonction.

### Syntaxe

```
---@return type [nom] [description]
---@return type1, type2   -- retours multiples
```

### Exemples

```lua
---@return string
function getName() end

-- Retours multiples
---@return string nom
---@return number age
function getInfo() end

-- Syntaxe compacte
---@return string, number, boolean
function getMultiple() end

-- Retour optionnel (peut être nil)
---@return string? résultat, string? erreur
function tryParse(input) end

-- Retour variadic
---@return ...string
function getNames() end
```

---

## @type

Attribue un type à une variable.

### Syntaxe

```
---@type type
```

### Exemples

```lua
---@type string
local name = getValue()

---@type number[]
local scores = {}

---@type table<string, boolean>
local flags = {}

---@type fun(a: number, b: number): number
local add

---@type string|nil
local maybeString

-- Cast inline (dans un commentaire)
local x = getData() --[[@as string]]

-- Type littéral
---@type "north"|"south"|"east"|"west"
local direction

-- Type tableau de tuples
---@type [string, number][]
local entries
```

---

## @alias

Crée un alias (synonyme) pour un type, y compris des unions de littéraux.

### Syntaxe

```
---@alias NomAlias type

---@alias NomAlias
---| 'valeur1' # description
---| 'valeur2' # description
```

### Exemples

```lua
---@alias PlayerId number

---@alias Handler fun(request: Request, response: Response)

-- Alias avec littéraux (enum-like sans runtime)
---@alias Direction
---| '"north"' # Vers le nord
---| '"south"' # Vers le sud
---| '"east"'  # Vers l'est
---| '"west"'  # Vers l'ouest

---@param dir Direction
function move(dir) end

-- Alias générique
---@alias Predicate<T> fun(value: T): boolean

-- Alias avec back-ticks (référence à des constantes)
local NORTH = "north"
local SOUTH = "south"
---@alias CardinalDir `NORTH` | `SOUTH`
```

---

## @enum

Déclare un enum qui existe au runtime (contrairement à `@alias` avec littéraux).

### Syntaxe

```
---@enum NomEnum
```

### Exemples

```lua
---@enum Color
local Color = {
  Red = 1,
  Green = 2,
  Blue = 3,
}

---@param c Color
function setColor(c) end

setColor(Color.Red)  -- OK
setColor(1)          -- OK (inlay hint affiche "Color.Red")
setColor(4)          -- Warning: enum-value-mismatch
```

### Attribut key (spécifique à emmylua_ls)

L'attribut `(key)` permet de contrôler le préfixe de complétion. Quand il est utilisé, la complétion propose les chemins internes de l'enum au lieu du nom complet :

```lua
---@enum (key) Bindings
local Bindings = {
  CS = {
    Unity = {
      GameObject = 1,
      Transform = 2,
    }
  }
}

-- Sans (key) : la complétion propose Bindings.CS.Unity.GameObject
-- Avec (key) : la complétion propose CS.Unity.GameObject
```

Cette fonctionnalité est particulièrement utile pour les bindings C# (Unity/XLua) où le nom du conteneur Lua n'est pas pertinent pour l'utilisateur.

### Enum comme clé de table

Les valeurs d'un enum peuvent servir de clés typées dans les tables :

```lua
---@enum Direction
local Direction = { Up = 1, Down = 2, Left = 3, Right = 4 }

---@type table<Direction, string>
local labels = {
  [Direction.Up] = "Haut",
  [Direction.Down] = "Bas",
}
```

---

## @generic

Déclare des types génériques pour une fonction.

### Syntaxe

```
---@generic T [: Contrainte]
---@generic K, V
```

### Exemples

```lua
---@generic T
---@param list T[]
---@return T
function first(list)
  return list[1]
end

---@generic T
---@param list T[]
---@param fn fun(v: T): boolean
---@return T[]
function filter(list, fn)
  local result = {}
  for _, v in ipairs(list) do
    if fn(v) then table.insert(result, v) end
  end
  return result
end

-- Génériques avec contrainte
---@generic T : Animal
---@param pet T
---@return T
function clone(pet) end

-- Génériques multiples
---@generic K, V
---@param tbl table<K, V>
---@return K[]
function keys(tbl) end
```

### Génériques avancés (style TypeScript)

EmmyLua supporte des fonctionnalités avancées de génériques :

```lua
-- keyof : obtenir les clés d'un type
---@generic T
---@param obj T
---@param key keyof T
---@return T[keyof T]
function getField(obj, key) end

-- extends : contrainte conditionnelle
---@generic T : extends string
---@param value T
function processString(value) end

-- infer : inférence dans les conditionnels
-- (fonctionnalité avancée, syntaxe similaire à TypeScript)
```

---

## @overload

Déclare des signatures alternatives pour une fonction.

### Syntaxe

```
---@overload fun(params): returns
```

### Exemples

```lua
---@param x number
---@param y number
---@return number
---@overload fun(vec: Vector2): number
---@overload fun(x: number, y: number, z: number): number
function distance(x, y) end

-- La complétion et le hover afficheront les 3 signatures
```

---

## @async

Marque une fonction comme asynchrone.

### Syntaxe

```
---@async
```

### Exemple

```lua
---@async
---@param url string
---@return string
function fetchUrl(url) end
```

Si une fonction `@async` est appelée dans une fonction non-async, le diagnostic `await-in-sync` sera émis.

---

## @deprecated

Marque un élément comme déprécié.

### Syntaxe

```
---@deprecated [message]
```

### Exemple

```lua
---@deprecated Utiliser newFunction() à la place
function oldFunction() end
```

L'utilisation de `oldFunction` affichera un avertissement et la complétion la montrera barrée.

---

## Visibilité

### @private

Accessible uniquement dans la classe où il est défini.

```lua
---@class Database
local Database = {}

---@private
function Database:_connect() end
```

### @protected

Accessible dans la classe et ses classes enfants.

```lua
---@protected
function Database:_query(sql) end
```

### @package

Accessible uniquement dans le fichier où il est défini.

```lua
---@package
function Database:_internal() end
```

---

## @diagnostic

Contrôle les diagnostics au niveau d'une ligne ou d'une région.

### Syntaxe

```
---@diagnostic disable-next-line: code1, code2
---@diagnostic disable: code
---@diagnostic enable: code
---@diagnostic disable-line: code
```

### Exemples

```lua
---@diagnostic disable-next-line: undefined-global
print(SOME_GLOBAL)

---@diagnostic disable: unused
local x = 1
local y = 2
---@diagnostic enable: unused

-- Désactiver sur la même ligne
local z = GLOBAL ---@diagnostic disable-line: undefined-global
```

---

## @cast

Force un cast de type sur une variable existante.

### Syntaxe

```
---@cast variable type
---@cast variable +type    -- ajouter un type à l'union
---@cast variable -type    -- retirer un type de l'union
```

### Exemples

```lua
local x = getValue()  -- x est `any`

---@cast x string      -- x est maintenant `string`

---@cast x +number     -- x est maintenant `string|number`

---@cast x -nil        -- retire nil du type (narrowing)
```

---

## @operator

Définit les surcharges d'opérateurs pour une classe.

### Syntaxe

```
---@operator opérateur(type_opérande): type_résultat
```

### Opérateurs supportés

`add` (+), `sub` (-), `mul` (*), `div` (/), `mod` (%), `pow` (^), `unm` (- unaire), `concat` (..), `len` (#), `eq` (==), `lt` (<), `le` (<=), `idiv` (//), `band` (&), `bor` (|), `bxor` (~), `bnot` (~ unaire), `shl` (<<), `shr` (>>), `call`

### Exemples

```lua
---@class Vector2
---@field x number
---@field y number
---@operator add(Vector2): Vector2
---@operator mul(number): Vector2
---@operator unm: Vector2
---@operator len: number
local Vector2 = {}

local a = Vector2.new(1, 2)
local b = Vector2.new(3, 4)
local c = a + b     -- type inféré : Vector2
local d = a * 2     -- type inféré : Vector2
local e = -a        -- type inféré : Vector2
local l = #a        -- type inféré : number
```

---

## @nodiscard

Interdit d'ignorer la valeur de retour d'une fonction.

### Syntaxe

```
---@nodiscard
```

### Exemple

```lua
---@nodiscard
---@return string
function generateId() end

generateId()        -- Warning: discard-returns
local id = generateId()  -- OK
```

---

## @version

Spécifie la version Lua requise.

### Syntaxe

```
---@version >5.1, JIT
```

### Versions supportées

`5.1`, `5.2`, `5.3`, `5.4`, `5.5`, `JIT`

### Exemple

```lua
---@version >5.3
function useIntegerDiv()
  return 10 // 3
end
```

---

## @see

Crée une référence croisée vers un autre symbole.

### Syntaxe

```
---@see Symbole
```

### Exemple

```lua
---@see Animal.walk
---@see https://example.com/docs
function move() end
```

---

## @namespace

Déclare un namespace pour organiser les classes et alias. Annotation spécifique à emmylua_ls (absente de lua_ls/LuaLS).

### Syntaxe

```
---@namespace NomNamespace
```

### Exemples

#### Déclaration et référence

```lua
-- fichier ui/button.lua
---@namespace UI

---@class Button
---@field text string
---@field onClick fun()
local Button = {}

-- fichier ui/label.lua
---@namespace UI

---@class Label
---@field text string
local Label = {}
```

Les types sont ensuite accessibles depuis d'autres fichiers via le préfixe du namespace :

```lua
-- fichier app.lua
---@type UI.Button
local btn = createButton()

---@type UI.Label
local lbl = createLabel()
```

#### Réouverture d'un namespace

Un namespace peut être rouvert dans un autre fichier pour accéder à ses types sans préfixe :

```lua
-- fichier components.lua
---@namespace UI  -- Réouvre le namespace UI

---@type Button   -- Résolu comme UI.Button
local btn = createButton()
```

### namespace\<T\> (type spécial)

EmmyLua fournit un type générique spécial `namespace<T : string>` qui référence un namespace dynamiquement. C'est particulièrement utile pour modéliser des bindings vers des langages comme C# :

```lua
CS = {
  ---@type namespace<"UnityEngine">
  UnityEngine = {},
  ---@type namespace<"System">
  System = {},
}

-- CS.UnityEngine.GameObject est résolu comme le type UnityEngine.GameObject
-- CS.System.String est résolu comme System.String
local obj = CS.UnityEngine.GameObject()
```

---

## @using

Importe un namespace, permettant d'utiliser ses types sans le préfixe qualifié. Annotation spécifique à emmylua_ls.

### Syntaxe

```
---@using NomNamespace
```

### Exemple

```lua
---@using UI

---@param btn Button  -- Résolu comme UI.Button
function handleClick(btn) end

---@param lbl Label   -- Résolu comme UI.Label
function updateLabel(lbl) end
```

### Différence avec @namespace

- `---@namespace UI` : Déclare que les types définis ensuite appartiennent au namespace `UI`, ou rouvre le namespace pour y accéder sans préfixe.
- `---@using UI` : Importe le namespace `UI` pour que ses types soient accessibles sans préfixe, sans y ajouter de nouveaux types.

---

## @mapping

Permet de mapper un type vers un autre.

### Syntaxe

```
---@mapping NomMapping
```

Cette annotation est utilisée dans des cas avancés de transformation de types.

---

## @source

Spécifie la source d'un type ou d'une définition.

### Syntaxe

```
---@source chemin/vers/fichier.lua
```

Utile pour les fichiers de définitions qui font référence à des sources externes.

---

## @vararg

(Héritage EmmyLua, préférer `---@param ... type` dans le nouveau format)

Déclare une fonction avec arguments variables.

### Syntaxe

```
---@vararg type
```

### Exemple

```lua
---@vararg string
function print_all(...) end

-- Forme moderne recommandée :
---@param ... string
function print_all_v2(...) end
```

---

## @meta

Marque un fichier comme fichier de métadonnées (définitions uniquement, pas de code exécutable).

### Syntaxe

```
---@meta
```

Placé en début de fichier. Les fichiers meta sont utilisés pour fournir des définitions de types sans code runtime (bibliothèques, stubs, etc.).

---

## Formatage des commentaires

### Description de documentation

Les commentaires `---` supportent le Markdown (par défaut, configurable via `doc.syntax`).

```lua
--- Crée un nouvel utilisateur.
---
--- Cette fonction valide les données et crée l'enregistrement
--- dans la base de données.
---
--- ## Exemple
--- ```lua
--- local user = createUser("Alice", 30)
--- ```
---
---@param name string Le nom de l'utilisateur
---@param age number L'âge (doit être > 0)
---@return User
function createUser(name, age) end
```

### Commentaire inline sur les types

```lua
---@class Config
---@field host string    # L'hôte du serveur
---@field port number    # Le port (défaut: 8080)
```

### Diagnostic inline via commentaire de bloc

```lua
local x = value --[[@as string]]
```
