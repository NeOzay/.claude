# Système de types EmmyLua

Ce document décrit le système de types complet du serveur EmmyLua (emmylua_ls).

## Table des matières

1. [Types primitifs](#types-primitifs)
2. [Types spéciaux](#types-spéciaux)
3. [Types composites](#types-composites)
4. [Types littéraux](#types-littéraux)
5. [Types fonction](#types-fonction)
6. [Types table](#types-table)
7. [Unions et intersections](#unions-et-intersections)
8. [Types optionnels (nullable)](#types-optionnels-nullable)
9. [Tuples](#tuples)
10. [Génériques](#génériques)
11. [Génériques avancés](#génériques-avancés)
12. [Inférence de types](#inférence-de-types)
13. [Narrowing (réduction de type)](#narrowing-réduction-de-type)
14. [Surcharge d'opérateurs](#surcharge-dopérateurs)
15. [Compatibilité et sous-typage](#compatibilité-et-sous-typage)

---

## Types primitifs

Les types Lua de base reconnus par EmmyLua :

| Type | Description |
|---|---|
| `nil` | Valeur nil |
| `boolean` | `true` ou `false` |
| `number` | Nombre flottant (toutes versions Lua) |
| `integer` | Entier (Lua 5.3+, sous-type de `number`) |
| `string` | Chaîne de caractères |
| `table` | Table Lua (sans typage spécifique) |
| `function` | Fonction (sans signature spécifique) |
| `thread` | Coroutine Lua |
| `userdata` | Données C (userdata) |

---

## Types spéciaux

| Type | Description |
|---|---|
| `any` | Accepte n'importe quel type. Désactive la vérification. |
| `unknown` | Type inconnu. Plus sûr que `any` car il force la vérification avant usage. |
| `void` | Pas de valeur de retour (équivalent de ne rien retourner). |
| `never` | Type impossible (branche inatteignable, fonction qui ne retourne jamais). |
| `self` | Référence au type de la classe courante (utile dans les méthodes chaînées). |

### Différence entre `any` et `unknown`

```lua
---@param x any
function useAny(x)
  print(x.field)  -- Pas d'erreur : any désactive la vérification
end

---@param x unknown
function useUnknown(x)
  print(x.field)  -- Erreur : il faut d'abord vérifier le type de x
  if type(x) == "table" then
    -- Après narrowing, x est traité comme table
  end
end
```

### Usage de `self`

```lua
---@class Builder
local Builder = {}

---@param key string
---@return self
function Builder:set(key)
  self[key] = true
  return self
end

-- Permet le chaînage :
-- builder:set("a"):set("b"):set("c")
```

---

## Types composites

### Tableaux typés

```lua
---@type string[]
local names = {"Alice", "Bob"}

---@type number[][]
local matrix = {{1, 2}, {3, 4}}

---@type (string|number)[]
local mixed = {"hello", 42}
```

### Dictionnaires typés

```lua
---@type table<string, number>
local scores = {alice = 100, bob = 85}

---@type table<number, string>
local indexedNames = {[1] = "Alice", [2] = "Bob"}

---@type { [string]: boolean }
local flags = {enabled = true, debug = false}
```

### Tables structurées (littéraux de table)

```lua
---@type {name: string, age: number, active?: boolean}
local user = {name = "Alice", age = 30}

-- Champs optionnels avec ?
---@type {host: string, port?: number}
local config = {host = "localhost"}
```

---

## Types littéraux

Les types littéraux représentent des valeurs exactes :

```lua
---@type "hello"
local greeting = "hello"  -- Seule la valeur "hello" est acceptée

---@type 42
local answer = 42

---@type true
local flag = true

-- Combinaison avec unions pour créer des types enum-like
---@type "north"|"south"|"east"|"west"
local direction = "north"
```

---

## Types fonction

### Syntaxe complète

```
fun(param1: type1, param2: type2, ...): returnType1, returnType2
```

### Exemples

```lua
-- Fonction simple
---@type fun(x: number, y: number): number
local add

-- Fonction sans retour
---@type fun(msg: string)
local log

-- Paramètres optionnels
---@type fun(name: string, age?: number): User
local createUser

-- Varargs
---@type fun(...: string): string
local concat

-- Fonction générique (via callback)
---@type fun(list: any[], fn: fun(v: any): boolean): any[]
local filter

-- Paramètre self explicite
---@type fun(self: MyClass, key: string): any
local method
```

---

## Types table

### Table générique

```lua
---@type table<K, V>
```

### Table avec structure mixte

```lua
---@class MixedTable
---@field name string         -- Champ nommé
---@field [number] string     -- Index numérique → string

-- Utilisation :
---@type MixedTable
local t = {name = "test", "a", "b", "c"}
```

### Table indexée

```lua
-- Table avec clés string arbitraires
---@type {[string]: number}
local counters = {}

-- Table avec clés numériques
---@type {[integer]: string}
local array = {}
```

---

## Unions et intersections

### Unions (OU logique)

```lua
---@type string|number
local value -- accepte string OU number

---@type string|number|boolean|nil
local flexible

-- Avec des classes
---@type Cat|Dog
local pet
```

### Parenthèses pour la priorité

```lua
---@type (string|number)[]
local list  -- tableau de (string ou number)

---@type string|number[]
local ambiguous  -- string OU tableau de number (probablement pas ce qu'on veut)
```

---

## Types optionnels (nullable)

Le suffixe `?` est un raccourci pour `|nil` :

```lua
---@type string?
local maybe  -- équivalent de string|nil

---@param callback? fun()
function register(callback) end  -- callback peut être nil

---@class Config
---@field host string
---@field port? number       -- optionnel
---@field timeout? number    -- optionnel
```

---

## Tuples

Les tuples sont des tableaux à taille fixe avec des types positionnels :

```lua
---@type [string, number]
local pair = {"Alice", 30}

---@type [string, number, boolean]
local triple = {"test", 42, true}

-- Tableau de tuples
---@type [string, number][]
local entries = {{"a", 1}, {"b", 2}}
```

---

## Génériques

### Déclaration basique

```lua
---@generic T
---@param value T
---@return T
function identity(value)
  return value
end

local s = identity("hello")  -- s est inféré comme string
local n = identity(42)       -- n est inféré comme number
```

### Génériques multiples

```lua
---@generic K, V
---@param tbl table<K, V>
---@return K[], V[]
function unzip(tbl) end
```

### Contraintes de type

```lua
---@generic T : number
---@param a T
---@param b T
---@return T
function max(a, b)
  return a > b and a or b
end
```

### Génériques dans les classes

```lua
---@class Stack<T>
---@field private items T[]
---@field private size number
local Stack = {}

---@param item T
function Stack:push(item)
  self.size = self.size + 1
  self.items[self.size] = item
end

---@return T?
function Stack:pop()
  if self.size == 0 then return nil end
  local item = self.items[self.size]
  self.size = self.size - 1
  return item
end

---@type Stack<string>
local stringStack
```

### Inférence par pattern

```lua
---@generic T
---@param list T[]
---@param index number
---@return T
function at(list, index)
  return list[index]
end

local names = {"Alice", "Bob"}
local name = at(names, 1)  -- name est inféré comme string
```

---

## Génériques avancés

EmmyLua supporte des fonctionnalités génériques avancées inspirées de TypeScript.

### keyof

Obtient le type union des clés d'un type :

```lua
---@class Person
---@field name string
---@field age number

---@generic T
---@param obj T
---@param key keyof T
---@return unknown
function get(obj, key) end

---@type Person
local p = {name = "Alice", age = 30}
get(p, "name")  -- OK
get(p, "foo")   -- Erreur : "foo" n'est pas une clé de Person
```

### extends

Contrainte conditionnelle sur un générique :

```lua
---@generic T : extends string
---@param value T
---@return T
function process(value) end
```

### infer

Inférence dans des types conditionnels (fonctionnalité avancée).

### Opérateurs logiques

Dans les contraintes génériques, `and` et `or` remplacent respectivement `?` et `:` de TypeScript. La syntaxe est très similaire au conditionnel TypeScript mais avec cette substitution.

### namespace\<T : string\> (type spécial)

EmmyLua fournit un type générique intégré `namespace<T>` qui permet de référencer dynamiquement un namespace par son nom. C'est particulièrement utile pour modéliser des bindings vers C# (Unity, XLua) :

```lua
CS = {
  ---@type namespace<"UnityEngine">
  UnityEngine = {},
  ---@type namespace<"System">
  System = {},
}

-- CS.UnityEngine.GameObject est reconnu comme le type UnityEngine.GameObject
local go = CS.UnityEngine.GameObject()
local str = CS.System.String.Format("hello %s", "world")
```

Ce mécanisme permet à EmmyLua de résoudre les types à travers des tables de liaison dynamiques, sans avoir à déclarer chaque sous-champ manuellement.

---

## Inférence de types

EmmyLua infère automatiquement les types dans de nombreux cas :

### Variables locales

```lua
local x = 42        -- inféré : number (ou integer selon la version)
local s = "hello"   -- inféré : string
local t = {}        -- inféré : table
local b = true      -- inféré : boolean
```

### Retour de fonctions annotées

```lua
---@return string
function getName() return "Alice" end

local name = getName()  -- name est string
```

### Boucles

```lua
---@type string[]
local names = {"a", "b", "c"}

for i, name in ipairs(names) do
  -- i est inféré comme integer
  -- name est inféré comme string
end
```

### Tables constructeurs

```lua
local config = {
  host = "localhost",  -- string
  port = 8080,         -- number
  debug = false,       -- boolean
}
-- config est inféré comme {host: string, port: number, debug: boolean}
```

---

## Narrowing (réduction de type)

EmmyLua réduit les types dans les branches conditionnelles :

### Via type()

```lua
---@param x string|number
function process(x)
  if type(x) == "string" then
    -- ici x est string
    print(x:upper())
  else
    -- ici x est number
    print(x + 1)
  end
end
```

### Via nil check

```lua
---@param x string?
function greet(x)
  if x then
    -- x est string (nil est éliminé)
    print("Hello " .. x)
  end
end
```

### Via assert

```lua
---@param x string?
function process(x)
  assert(x)
  -- x est maintenant string
end
```

### Via @cast

```lua
---@param x any
function process(x)
  ---@cast x string
  -- x est forcé en string
  print(x:upper())
end
```

---

## Surcharge d'opérateurs

Les métaméthodes Lua peuvent être typées via `@operator` :

```lua
---@class Money
---@field amount number
---@field currency string
---@operator add(Money): Money
---@operator sub(Money): Money
---@operator mul(number): Money
---@operator div(number): Money
---@operator eq(Money): boolean
---@operator lt(Money): boolean
---@operator le(Money): boolean
---@operator unm: Money
---@operator tostring: string
---@operator concat(string): string
---@operator len: number
---@operator call(number): Money
local Money = {}
```

### Opérateurs disponibles

| Annotation | Opérateur Lua | Métaméthode |
|---|---|---|
| `add` | `+` | `__add` |
| `sub` | `-` | `__sub` |
| `mul` | `*` | `__mul` |
| `div` | `/` | `__div` |
| `mod` | `%` | `__mod` |
| `pow` | `^` | `__pow` |
| `unm` | `- (unaire)` | `__unm` |
| `concat` | `..` | `__concat` |
| `len` | `#` | `__len` |
| `eq` | `==` | `__eq` |
| `lt` | `<` | `__lt` |
| `le` | `<=` | `__le` |
| `idiv` | `//` | `__idiv` |
| `band` | `&` | `__band` |
| `bor` | `\|` | `__bor` |
| `bxor` | `~` | `__bxor` |
| `bnot` | `~ (unaire)` | `__bnot` |
| `shl` | `<<` | `__shl` |
| `shr` | `>>` | `__shr` |
| `call` | `()` | `__call` |

---

## Compatibilité et sous-typage

### Règles de sous-typage

- Une classe enfant est un sous-type de sa classe parente.
- `integer` est un sous-type de `number`.
- `never` est un sous-type de tous les types.
- Tous les types sont un sous-type de `any`.
- Les types littéraux (`"hello"`, `42`) sont des sous-types de leur type de base (`string`, `number`).

### Covariance et contravariance

- Les paramètres de type en position de retour sont covariants.
- Les paramètres de type en position de paramètre sont contravariants.

### any vs unknown

| | `any` | `unknown` |
|---|---|---|
| Assignable à | tout type | seulement `any` et `unknown` |
| Peut recevoir | tout type | tout type |
| Accès aux membres | autorisé sans vérification | interdit sans narrowing |
| Usage recommandé | interop, migration | sécurité maximale |

### Types structurels vs nominaux

EmmyLua utilise un système **nominal** pour les classes (deux classes différentes ne sont pas interchangeables même si elles ont les mêmes champs), mais **structurel** pour les tables littérales (une table qui a tous les champs requis est compatible).

```lua
---@class A
---@field x number

---@class B
---@field x number

---@param a A
function takeA(a) end

---@type B
local b = {x = 1}
takeA(b)  -- Erreur : B n'est pas A (nominal)

local c = {x = 1}
takeA(c)  -- OK : table littérale vérifiée structurellement
```
