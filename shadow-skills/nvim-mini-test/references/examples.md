# mini.test — Exemples exhaustifs par type de test

This file covers every test pattern supported by mini.test, sourced from the
official TESTING.md and real tests in nvim-mini/mini.nvim.

---

## Table of contents

1. [Basic test set and simple cases](#1-basic-test-set-and-simple-cases)
2. [Hooks — pre/post once and per case](#2-hooks--prepost-once-and-per-case)
3. [Nested sets](#3-nested-sets)
4. [Parametrized tests](#4-parametrized-tests)
5. [All expect assertions](#5-all-expect-assertions)
6. [skip(), add_note(), finally()](#6-skip-add_note-finally)
7. [n_retry — flaky test handling](#7-n_retry--flaky-test-handling)
8. [Child process — basics](#8-child-process--basics)
9. [Child process — lua, lua_get, lua_func](#9-child-process--lua-lua_get-lua_func)
10. [Child process — type_keys](#10-child-process--type_keys)
11. [Child process — option proxies (o, bo, go, wo)](#11-child-process--option-proxies-o-bo-go-wo)
12. [Child process — api, fn, g, b, v proxies](#12-child-process--api-fn-g-b-v-proxies)
13. [Child process — cmd, ensure_normal_mode](#13-child-process--cmd-ensure_normal_mode)
14. [Child process — get_lines, set_lines, get_cursor, set_cursor](#14-child-process--get_lines-set_lines-get_cursor-set_cursor)
15. [Screenshot testing](#15-screenshot-testing)
16. [Async / sleep testing](#16-async--sleep-testing)
17. [Busted-style emulation (describe/it)](#17-busted-style-emulation-describeit)
18. [data field and MiniTest.current](#18-data-field-and-minitest-current)
19. [Custom file collection and case filtering](#19-custom-file-collection-and-case-filtering)
20. [pre_source / post_source hooks](#20-pre_source--post_source-hooks)

---

## 1. Basic test set and simple cases

Every test file must return a `MiniTest.new_set()`. Test cases are functions
assigned as string keys on the set.

```lua
local new_set = MiniTest.new_set
local expect  = MiniTest.expect

local T = new_set()

T["addition works"] = function()
  expect.equality(1 + 1, 2)
end

T["string concatenation"] = function()
  expect.equality("hello" .. " " .. "world", "hello world")
end

T["table comparison"] = function()
  expect.equality({ a = 1, b = { 2, 3 } }, { a = 1, b = { 2, 3 } })
end

return T
```

---

## 2. Hooks — pre/post once and per case

`pre_once` / `post_once` run once for the entire set.
`pre_case` / `post_case` run around every individual test case.

Hooks compose with child sets: parent hooks run outside, child hooks inside.

```lua
local T = new_set({
  hooks = {
    pre_once = function()
      -- Runs once before any case in this set (e.g. start child process)
      _G.shared_state = {}
    end,

    post_once = function()
      -- Runs once after all cases (e.g. stop child process)
      _G.shared_state = nil
    end,

    pre_case = function()
      -- Runs before each individual case (e.g. reset buffer)
      vim.cmd("enew")
      _G.shared_state = {}
    end,

    post_case = function()
      -- Runs after each individual case (e.g. cleanup)
      vim.cmd("%bwipeout!")
    end,
  },
})

T["case sees fresh state"] = function()
  expect.equality(_G.shared_state, {})
end

return T
```

---

## 3. Nested sets

Nested sets group related cases. Each level can define its own hooks, which
compose: parent `pre_case` runs before child `pre_case`.

```lua
local T = new_set()

-- Nested set with its own hooks
T["parse()"] = new_set({
  hooks = {
    pre_case = function()
      vim.cmd("enew")
    end,
  },
})

T["parse()"]["empty string returns empty table"] = function()
  expect.equality(require("my-plugin.parser").parse(""), {})
end

T["parse()"]["valid input returns tokens"] = function()
  expect.equality(require("my-plugin.parser").parse("a b"), { "a", "b" })
end

-- Another nested set — no hooks needed
T["format()"] = new_set()

T["format()"]["adds prefix"] = function()
  expect.equality(require("my-plugin").format("hello"), "[PREFIX] hello")
end

T["format()"]["handles empty string"] = function()
  expect.equality(require("my-plugin").format(""), "[PREFIX] ")
end

return T
```

---

## 4. Parametrized tests

`parametrize` creates one test case per parameter tuple. Each tuple is passed
as arguments to the test function.

```lua
local T = new_set()

-- Simple value parametrization
T["strlen"] = new_set({
  parametrize = {
    { "",      0 },
    { "hello", 5 },
    { "café",  4 },
  },
})

T["strlen"]["returns correct length"] = function(input, expected)
  expect.equality(vim.fn.strcharlen(input), expected)
end

-- Parametrize a whole nested set (all cases inside inherit the args)
T["disable"] = new_set({
  parametrize = { { "g" }, { "b" } },
})

T["disable"]["respects vim.{g,b}.myplugin_disable"] = function(var_type)
  -- var_type is "g" or "b"
  vim[var_type].myplugin_disable = true
  expect.equality(require("my-plugin").is_enabled(), false)
  vim[var_type].myplugin_disable = nil
end

-- Parametrize with tables as arguments
T["setup()"] = new_set({
  parametrize = {
    { {},                      "default" },
    { { prefix = ">>>" },      "custom"  },
    { { prefix = "", silent = true }, "silent"  },
  },
})

T["setup()"]["respects config"] = function(config, label)
  require("my-plugin").setup(config)
  -- label is available for debugging context
  expect.no_error(function()
    require("my-plugin").run()
  end)
end

return T
```

---

## 5. All expect assertions

```lua
local T = new_set()
local expect = MiniTest.expect

-- equality: deep equality (tables compared recursively)
T["expect.equality"] = function()
  expect.equality(1, 1)
  expect.equality("a", "a")
  expect.equality({ 1, 2 }, { 1, 2 })
  expect.equality({ a = { b = 3 } }, { a = { b = 3 } })
end

-- no_equality: values must NOT be equal
T["expect.no_equality"] = function()
  expect.no_equality(1, 2)
  expect.no_equality({ 1 }, { 2 })
end

-- error: function must throw any error
T["expect.error - any"] = function()
  expect.error(function()
    error("boom")
  end)
end

-- error: function must throw error matching a pattern
T["expect.error - pattern"] = function()
  expect.error(function()
    error("invalid argument: expected string")
  end, "invalid argument")
end

-- no_error: function must NOT throw
T["expect.no_error"] = function()
  expect.no_error(function()
    local _ = 1 + 1
  end)
end

-- reference_screenshot: see section 15

return T
```

---

## 6. skip(), add_note(), finally()

```lua
local T = new_set()

-- skip(): stop the case immediately, mark as skipped (not failed)
T["skip() - conditional on Neovim version"] = function()
  if vim.fn.has("nvim-0.10") == 0 then
    MiniTest.skip("Requires Neovim >= 0.10")
  end
  -- only reached on 0.10+
  expect.equality(vim.version().minor >= 10, true)
end

-- skip() in pre_case hook skips ALL cases in the set
T["needs_feature"] = new_set({
  hooks = {
    pre_case = function()
      if not pcall(require, "optional-dep") then
        MiniTest.skip("optional-dep not available")
      end
    end,
  },
})
T["needs_feature"]["case 1"] = function()
  -- skipped if optional-dep is absent
end

-- add_note(): attach a note without changing pass/fail status
T["add_note() - informational"] = function()
  MiniTest.add_note("Running in headless mode, some assertions relaxed.")
  expect.equality(1, 1)
end

-- finally(): register cleanup that always runs, even on error
-- Useful for teardown that must happen regardless of test outcome
T["finally() - guaranteed cleanup"] = function()
  local tmp = vim.fn.tempname()
  vim.fn.writefile({ "data" }, tmp)

  MiniTest.finally(function()
    vim.fn.delete(tmp)  -- always runs
  end)

  -- If this errors, the file is still deleted
  expect.equality(vim.fn.filereadable(tmp), 1)
end

-- finally() - multiple registrations execute in order
T["finally() - multiple"] = function()
  local log = {}

  MiniTest.finally(function() table.insert(log, "first") end)
  MiniTest.finally(function() table.insert(log, "second") end)

  -- both will run after the case; log will be { "first", "second" }
  expect.equality(#log, 0)  -- not yet
end

-- finally() - mark flaky test on failure
T["finally() - flaky marker"] = function()
  MiniTest.finally(function()
    if #MiniTest.current.case.exec.fails > 0 then
      MiniTest.add_note("This test is known to be flaky.")
    end
  end)
  -- Intentionally fragile example:
  expect.equality(math.random(1, 100) > 0, true)
end

return T
```

---

## 7. n_retry — flaky test handling

`n_retry` retries a failing case up to N times. The case passes on the first
success. Useful for timing-sensitive or async tests.

```lua
local T = new_set()

-- Apply n_retry to a whole set
T["flaky_suite"] = new_set({ n_retry = 3 })

T["flaky_suite"]["eventually succeeds"] = function()
  -- Will retry up to 3 times before being marked as failed
  expect.equality(math.random(1, 3) <= 3, true)
end

-- Apply n_retry to a single case via a set wrapper
T["single_retry"] = new_set({ n_retry = 2 })
T["single_retry"]["my flaky case"] = function()
  expect.no_error(function()
    require("my-plugin").unstable_operation()
  end)
end

return T
```

---

## 8. Child process — basics

The child process is an isolated Neovim instance. All meaningful plugin tests
should use it to avoid polluting the test runner's own Neovim state.

```lua
local child = MiniTest.new_child_neovim()

local T = new_set({
  hooks = {
    -- Start fresh child before each case
    pre_case = function()
      child.restart({ "-u", "tests/minimal_init.lua" })
      -- Load the plugin under test into the child
      child.lua([[M = require("my-plugin")]])
    end,
    -- Stop child after all cases in the set
    post_once = child.stop,
  },
})

T["plugin loads without error"] = function()
  expect.no_error(function()
    child.lua([[require("my-plugin").setup({})]])
  end)
end

T["plugin sets global flag"] = function()
  child.lua([[require("my-plugin").setup({})]])
  expect.equality(child.lua_get([[vim.g.my_plugin_loaded]]), true)
end

return T
```

> **Lifecycle methods:**
> - `child.start(args)` — start the process (called once)
> - `child.restart(args)` — stop + start (resets all state, use in `pre_case`)
> - `child.stop()` — terminate the process

---

## 9. Child process — lua, lua_get, lua_func

```lua
local child = MiniTest.new_child_neovim()
local T = new_set({
  hooks = {
    pre_case  = function() child.restart({ "-u", "tests/minimal_init.lua" }) end,
    post_once = child.stop,
  },
})

T["child.lua - execute without return"] = function()
  -- Execute arbitrary Lua in the child; no return value
  child.lua([[vim.g.my_flag = true]])
  expect.equality(child.lua_get([[vim.g.my_flag]]), true)
end

T["child.lua - pass arguments via second parameter"] = function()
  -- Arguments are serialized and available as `...` in the child
  child.lua([[
    local a, b = ...
    vim.g.result = a + b
  ]], { 3, 4 })
  expect.equality(child.lua_get([[vim.g.result]]), 7)
end

T["child.lua_get - return complex value"] = function()
  child.lua([[
    M = require("my-plugin")
    M.setup({ prefix = ">>>" })
  ]])
  -- Returns the value serialized back to the test process
  local config = child.lua_get([[M.config]])
  expect.equality(config.prefix, ">>>")
end

T["child.lua_func - call a function directly"] = function()
  -- lua_func executes a simple function and returns its result
  -- Useful for functions that don't need string-encoded Lua
  local result = child.lua_func(function(x, y) return x * y end, 6, 7)
  expect.equality(result, 42)
end

return T
```

---

## 10. Child process — type_keys

`type_keys` feeds keystrokes to the child as if typed by the user.
It is the primary way to test mappings and interactive behavior.

```lua
local child = MiniTest.new_child_neovim()
local T = new_set({
  hooks = {
    pre_case = function()
      child.restart({ "-u", "tests/minimal_init.lua" })
      child.lua([[require("my-plugin").setup({})]])
      -- Start with a fresh buffer containing known content
      child.api.nvim_buf_set_lines(0, 0, -1, false, { "hello world", "foo bar" })
    end,
    post_once = child.stop,
  },
})

T["mapping works in normal mode"] = function()
  -- Position cursor, send mapping keys
  child.api.nvim_win_set_cursor(0, { 1, 0 })
  child.type_keys("<leader>p")
  -- Check result
  local lines = child.api.nvim_buf_get_lines(0, 0, -1, false)
  expect.equality(lines[1], "[PREFIX] hello world")
end

T["insert mode input"] = function()
  child.type_keys("i", "inserted text", "<Esc>")
  local lines = child.api.nvim_buf_get_lines(0, 0, -1, false)
  expect.equality(lines[1], "inserted texthello world")
end

T["command-line command"] = function()
  child.type_keys(":", "MyPluginCommand", "<CR>")
  expect.equality(child.lua_get([[vim.g.command_ran]]), true)
end

-- type_keys accepts a wait (ms) between keystrokes as second arg
T["mapping with delay"] = function()
  child.type_keys("<leader>", 50, "p")  -- 50ms pause after <leader>
end

return T
```

---

## 11. Child process — option proxies (o, bo, go, wo)

The child exposes Neovim option tables as proxies, mirroring `vim.o`,
`vim.bo`, `vim.go`, `vim.wo`.

```lua
local child = MiniTest.new_child_neovim()
local T = new_set({
  hooks = {
    pre_case  = function() child.restart({ "-u", "tests/minimal_init.lua" }) end,
    post_once = child.stop,
  },
})

T["read and write global options"] = function()
  -- vim.o equivalent
  child.o.lines   = 24
  child.o.columns = 80
  expect.equality(child.o.lines, 24)
end

T["read and write buffer options"] = function()
  -- vim.bo equivalent
  child.bo.filetype = "lua"
  expect.equality(child.bo.filetype, "lua")
end

T["read and write window options"] = function()
  -- vim.wo equivalent
  child.wo.wrap = false
  expect.equality(child.wo.wrap, false)
end

T["read and write global-only options"] = function()
  -- vim.go equivalent
  child.go.encoding = "utf-8"
  expect.equality(child.go.encoding, "utf-8")
end

return T
```

---

## 12. Child process — api, fn, g, b, v proxies

All major Neovim namespaces are proxied on the child object.

```lua
local child = MiniTest.new_child_neovim()
local T = new_set({
  hooks = {
    pre_case  = function() child.restart({ "-u", "tests/minimal_init.lua" }) end,
    post_once = child.stop,
  },
})

T["child.api - nvim API calls"] = function()
  -- Equivalent to vim.api.* inside the child
  local buf = child.api.nvim_get_current_buf()
  expect.no_equality(buf, 0)

  child.api.nvim_buf_set_lines(0, 0, -1, false, { "line 1", "line 2" })
  local lines = child.api.nvim_buf_get_lines(0, 0, -1, false)
  expect.equality(lines, { "line 1", "line 2" })
end

T["child.fn - Vimscript functions"] = function()
  -- Equivalent to vim.fn.* inside the child
  expect.equality(child.fn.has("nvim"), 1)
  expect.equality(child.fn.mode(), "n")

  child.fn.setline(1, "replaced")
  expect.equality(child.fn.getline(1), "replaced")
end

T["child.g - global variables"] = function()
  -- Equivalent to vim.g inside the child
  child.g.my_plugin_option = "test_value"
  expect.equality(child.lua_get([[vim.g.my_plugin_option]]), "test_value")
end

T["child.b - buffer variables"] = function()
  -- Equivalent to vim.b inside the child
  child.b.myplugin_config = { enabled = false }
  expect.equality(child.lua_get([[vim.b.myplugin_config.enabled]]), false)
end

T["child.v - Vim v: variables"] = function()
  -- Read-access to v: namespace
  expect.no_error(function()
    local _ = child.v.version
  end)
end

return T
```

---

## 13. Child process — cmd, ensure_normal_mode

```lua
local child = MiniTest.new_child_neovim()
local T = new_set({
  hooks = {
    pre_case  = function() child.restart({ "-u", "tests/minimal_init.lua" }) end,
    post_once = child.stop,
  },
})

T["child.cmd - execute Ex commands"] = function()
  -- Equivalent to vim.cmd() inside the child
  child.cmd("set filetype=markdown")
  expect.equality(child.bo.filetype, "markdown")
end

T["child.cmd - open a file"] = function()
  child.cmd("edit tests/fixtures/sample.txt")
  expect.equality(child.fn.expand("%:t"), "sample.txt")
end

T["child.ensure_normal_mode"] = function()
  -- Forces the child back to Normal mode regardless of current mode.
  -- Useful after type_keys that might leave child in Insert/Visual mode.
  child.type_keys("i", "some text")
  child.ensure_normal_mode()
  expect.equality(child.fn.mode(), "n")
end

return T
```

---

## 14. Child process — get_lines, set_lines, get_cursor, set_cursor

These are convenience wrappers for the most common buffer/cursor operations.

```lua
local child = MiniTest.new_child_neovim()
local T = new_set({
  hooks = {
    pre_case = function()
      child.restart({ "-u", "tests/minimal_init.lua" })
      child.lua([[require("my-plugin").setup({})]])
    end,
    post_once = child.stop,
  },
})

-- Convenience helpers (mirror common pattern in mini.nvim tests)
local set_lines = function(lines)
  child.api.nvim_buf_set_lines(0, 0, -1, false, lines)
end
local get_lines = function()
  return child.api.nvim_buf_get_lines(0, 0, -1, false)
end
local set_cursor = function(row, col)
  child.api.nvim_win_set_cursor(0, { row, col })
end
local get_cursor = function()
  return child.api.nvim_win_get_cursor(0)
end

T["plugin modifies buffer lines"] = function()
  set_lines({ "hello", "world" })
  set_cursor(1, 0)

  child.lua([[M.transform_current_line()]])

  expect.equality(get_lines(), { "[PREFIX] hello", "world" })
end

T["plugin moves cursor"] = function()
  set_lines({ "aaa", "bbb", "ccc" })
  set_cursor(1, 0)

  child.lua([[M.jump_to_next()]])

  expect.equality(get_cursor(), { 2, 0 })
end

T["buffer operations with parametrize"] = new_set({
  parametrize = {
    { { "one" },             "one",   { "[PREFIX] one" }           },
    { { "one", "two" },      "two",   { "one", "[PREFIX] two" }    },
  },
})
T["buffer operations with parametrize"]["transforms correct line"] =
  function(initial, _, expected)
    set_lines(initial)
    set_cursor(#initial, 0)
    child.lua([[M.transform_current_line()]])
    expect.equality(get_lines(), expected)
  end

return T
```

---

## 15. Screenshot testing

Screenshots capture the full terminal state (text + highlight attributes).
On first run they are written to `tests/screenshots/`. On subsequent runs the
current state is compared against the reference.

```lua
local child = MiniTest.new_child_neovim()
local T = new_set({
  hooks = {
    pre_case = function()
      -- Fixed dimensions are mandatory for reproducible screenshots
      child.restart({ "-u", "tests/minimal_init.lua" })
      child.o.lines   = 20
      child.o.columns = 60
      child.lua([[require("my-plugin").setup({})]])
    end,
    post_once = child.stop,
  },
})

T["renders correctly"] = function()
  child.api.nvim_buf_set_lines(0, 0, -1, false, { "hello", "world" })
  -- Capture and compare (or create) the reference screenshot
  expect.reference_screenshot(child.get_screenshot())
end

-- With explicit path
T["renders with custom path"] = function()
  child.api.nvim_buf_set_lines(0, 0, -1, false, { "custom" })
  expect.reference_screenshot(
    child.get_screenshot(),
    "tests/screenshots/my_custom_name"
  )
end

-- Ignore specific lines (e.g. statusline with dynamic content)
T["renders ignoring statusline"] = function()
  child.api.nvim_buf_set_lines(0, 0, -1, false, { "content" })
  expect.reference_screenshot(child.get_screenshot(), nil, {
    -- Ignore line 20 (bottom statusline) for both text and attributes
    ignore_text = { 20 },
    ignore_attr = { 20 },
  })
end

-- Screenshot + parametrize: each parameter tuple creates a separate
-- named screenshot file automatically
T["parametrized renders"] = new_set({
  parametrize = { { "dark" }, { "light" } },
})
T["parametrized renders"]["colorscheme screenshot"] = function(theme)
  child.cmd("colorscheme " .. theme)
  child.api.nvim_buf_set_lines(0, 0, -1, false, { "sample text" })
  expect.reference_screenshot(child.get_screenshot())
end

return T
```

> **Tips:**
> - Always set `child.o.lines` and `child.o.columns` to fixed values.
> - Delete the reference file to regenerate it on the next run.
> - Keep test case names short — the file name is derived from them and has
>   a 143-byte limit on some filesystems.

---

## 16. Async / sleep testing

For plugins with deferred or timer-based behavior, use `vim.wait()` or the
`sleep()` helper used throughout mini.nvim's own tests.

```lua
local child = MiniTest.new_child_neovim()

-- sleep() helper from mini.nvim's own test suite pattern
local sleep = function(ms)
  vim.loop.sleep(ms)
end

local T = new_set({
  hooks = {
    pre_case  = function()
      child.restart({ "-u", "tests/minimal_init.lua" })
      child.lua([[require("my-plugin").setup({ delay = 50 })]])
    end,
    post_once = child.stop,
  },
})

T["deferred action completes"] = function()
  child.lua([[M.trigger_async()]])
  -- Wait longer than the configured delay
  sleep(100)
  expect.equality(child.lua_get([[_G.async_done]]), true)
end

T["action not yet done before delay"] = function()
  child.lua([[M.trigger_async()]])
  -- Check immediately — should not be done yet
  expect.equality(child.lua_get([[_G.async_done]]), nil)
  sleep(100)
  expect.equality(child.lua_get([[_G.async_done]]), true)
end

-- vim.wait() for event-loop based async (in-process tests)
T["in-process async via vim.wait"] = function()
  local done = false
  vim.defer_fn(function() done = true end, 30)
  vim.wait(200, function() return done end, 5)
  expect.equality(done, true)
end

return T
```

> **Note from mini.nvim CONTRIBUTING.md:** never hardcode sleep durations as
> raw numbers — use named constants that can be scaled per OS:
> ```lua
> local test_times = { action = vim.fn.has("win32") == 1 and 200 or 50 }
> sleep(test_times.action + 10)
> ```

---

## 17. Busted-style emulation (describe/it)

Enable `emulate_busted = true` in `MiniTest.setup()` to use `describe`, `it`,
`before_each`, `after_each`, `setup`, `teardown` as globals.

`scripts/minimal_init.lua` change needed:
```lua
require("mini.test").setup({ collect = { emulate_busted = true } })
```

```lua
-- tests/test_busted_style.lua — no `return T` needed in busted style

describe("my-plugin", function()
  local plugin

  setup(function()
    -- Runs once before all cases in this describe block
    plugin = require("my-plugin")
  end)

  teardown(function()
    -- Runs once after all cases
    package.loaded["my-plugin"] = nil
  end)

  before_each(function()
    -- Runs before each `it`
    plugin.reset()
  end)

  after_each(function()
    -- Runs after each `it`
  end)

  it("returns correct result", function()
    MiniTest.expect.equality(plugin.compute("a"), "Hello a")
  end)

  it("handles nil input", function()
    MiniTest.expect.error(function()
      plugin.compute(nil)
    end)
  end)

  describe("nested group", function()
    it("nested case", function()
      MiniTest.expect.equality(plugin.compute("b"), "Hello b")
    end)
  end)
end)
```

> Use `MiniTest.skip()` instead of busted's `pending()`, and
> `MiniTest.finally()` instead of busted's `finally`.

---

## 18. data field and MiniTest.current

`data` is a free-form table attached to a test set. It is available inside
test cases via `MiniTest.current.case.data` and is deep-merged from parent
sets to child sets.

```lua
local T = new_set({
  data = { plugin = "my-plugin", version = 1 },
})

T["accesses data"] = function()
  local d = MiniTest.current.case.data
  expect.equality(d.plugin, "my-plugin")
end

-- Child set adds its own data — merged with parent
T["sub"] = new_set({
  data = { component = "parser" },
})

T["sub"]["merged data"] = function()
  local d = MiniTest.current.case.data
  expect.equality(d.plugin, "my-plugin")   -- from parent
  expect.equality(d.component, "parser")   -- from child
end

-- MiniTest.current.case holds the current executing case
T["inspect current case"] = function()
  local case = MiniTest.current.case
  -- case.desc is a list of strings: file path + key hierarchy
  expect.no_equality(case.desc, nil)
end

-- MiniTest.current.all_cases is the full collected array (read-only)
T["all_cases available"] = function()
  expect.no_equality(MiniTest.current.all_cases, nil)
end

return T
```

---

## 19. Custom file collection and case filtering

Override `find_files` to test non-standard layouts, or `filter_cases` to
run only a subset.

```lua
-- scripts/minitest.lua (project-specific runner script)
require("mini.test").setup({
  collect = {
    -- Only collect files in tests/unit/, skip tests/integration/
    find_files = function()
      return vim.fn.globpath("tests/unit", "**/test_*.lua", true, true)
    end,

    -- Only run cases whose description contains "smoke"
    filter_cases = function(case)
      return vim.tbl_contains(case.desc, "smoke")
    end,
  },
  execute = {
    stop_on_error = true,  -- abort on first failure
  },
})

MiniTest.run()
```

Run only the test at the cursor position from within Neovim:
```lua
-- Bind to a key in your config:
vim.keymap.set("n", "<leader>tt", MiniTest.run_at_location)
vim.keymap.set("n", "<leader>tf", MiniTest.run_file)
```

---

## 20. pre_source / post_source hooks

`pre_source` and `post_source` run before/after the test file itself is
sourced (i.e. before any `new_set()` is called). They can be `"once"` or
`"case"`. These are advanced hooks used for module-level setup.

```lua
-- In a top-level set definition:
local T = new_set({
  hooks = {
    -- Runs once before the file is sourced by the test runner
    pre_source = "once",   -- value: "once" | "case" | callable

    -- Callable form for actual logic:
    -- pre_source = function() vim.cmd("set rtp+=.") end,
  },
})

-- Typical real-world use: ensure the plugin module is freshly loaded
local T2 = new_set({
  hooks = {
    pre_case = function()
      -- Clear module cache so each case starts from a clean require()
      package.loaded["my-plugin"] = nil
      package.loaded["my-plugin.utils"] = nil
    end,
  },
})

T2["fresh require each time"] = function()
  local p = require("my-plugin")
  expect.no_equality(p, nil)
end

return T2
```
