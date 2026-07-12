---
name: nvim-mini-test
description: >
  Write and manage unit tests for Neovim plugins using mini.test (from mini.nvim).
  Use this skill whenever the user works on a Neovim plugin and mentions tests, testing,
  unit tests, TDD, test coverage, or asks to add/fix/refactor tests. Also trigger when
  the user asks to set up a test infrastructure for a Neovim plugin, create a CI pipeline
  for plugin tests, or bootstrap a new plugin project that needs tests. This skill covers
  mini.test specifically — not plenary.busted, busted, or neotest. If the user explicitly
  asks for plenary or busted, do NOT use this skill.
---

# Neovim Plugin Testing with mini.test

This skill teaches how to write, organize, and run unit tests for Neovim plugins using
mini.test from the mini.nvim ecosystem. mini.test is a modern, zero-dependency test
framework that runs inside a real Neovim instance.

## When to use mini.test

- New Neovim plugin projects that need a test setup
- Adding tests to existing plugins
- Migrating from plenary.busted to mini.test
- Setting up CI for Neovim plugin tests

## Project structure

A well-tested Neovim plugin follows this layout:

```
my-plugin/
├── lua/
│   └── my-plugin/
│       ├── init.lua
│       └── utils.lua
├── tests/
│   ├── minimal_init.lua      -- bootstraps mini.test
│   ├── test_init.lua          -- tests for init.lua
│   └── test_utils.lua         -- tests for utils.lua
├── deps/                      -- local fallback deps (gitignored)
│   └── mini.test/
├── .gitignore                 -- should contain /deps/
├── Makefile                   -- test runner targets
└── .github/
    └── workflows/
        └── tests.yml          -- CI configuration
```

Test files should mirror the source structure with a `test_` prefix.

## Setting up mini.test

### minimal_init.lua

Every test suite needs a bootstrap file. Create `tests/minimal_init.lua`:

```lua
-- Resolve mini.test: check lazy installs first, then fall back to deps/
local lazy_data = vim.fn.stdpath("data") .. "/lazy"
local mini_test_path =
  -- 1. standalone mini.test installed by lazy.nvim
  (vim.uv.fs_stat(lazy_data .. "/mini.test") and lazy_data .. "/mini.test")
  -- 2. full mini.nvim monorepo installed by lazy.nvim (includes mini.test)
  or (vim.uv.fs_stat(lazy_data .. "/mini.nvim") and lazy_data .. "/mini.nvim")

if not mini_test_path then
  -- 3. Fall back to local deps/mini.test (gitignored)
  mini_test_path = vim.fn.getcwd() .. "/deps/mini.test"
  if not vim.uv.fs_stat(mini_test_path) then
    vim.fn.system({
      "git", "clone", "--filter=blob:none",
      "https://github.com/nvim-mini/mini.test",
      mini_test_path,
    })
  end
end

vim.opt.rtp:prepend(mini_test_path)

-- Add the plugin under test to runtimepath
vim.opt.rtp:prepend(vim.fn.getcwd())

-- Setup mini.test
require("mini.test").setup()
```

If the plugin has dependencies, add them to runtimepath in minimal_init.lua before
running tests. Clone them the same way mini.test is cloned above.

> **Note:** If mini.test is cloned into `deps/`, make sure to add `deps/` to your
> `.gitignore` so it isn't committed:
> ```
> /deps/
> ```

### Makefile

```makefile
.PHONY: test test-file

test:
	nvim --headless -u tests/minimal_init.lua -c "lua MiniTest.run()"

test-file:
	nvim --headless -u tests/minimal_init.lua -c "lua MiniTest.run_file('$(FILE)')"
```

## Writing tests

Read `references/mini-test-api.md` for the complete API reference. Here is a summary
of the core patterns.

### Basic test file

Every test file returns a test set:

```lua
local new_set = MiniTest.new_set
local expect = MiniTest.expect

local T = new_set()

T["my_function returns correct value"] = function()
  local result = require("my-plugin").my_function()
  expect.equality(result, 42)
end

T["my_function handles nil input"] = function()
  expect.error(function()
    require("my-plugin").my_function(nil)
  end)
end

return T
```

Key rules:
- Always `return T` at the end of the file
- Test names are string keys on the set — make them descriptive
- Use `MiniTest.expect` for assertions, not raw `assert()`
- Each test function receives no arguments

### Hooks for setup and teardown

```lua
local T = new_set({
  hooks = {
    pre_once = function()
      -- Runs once before all tests in this set
    end,
    pre_case = function()
      -- Runs before each test case
      vim.cmd("enew")  -- fresh buffer for each test
    end,
    post_case = function()
      -- Runs after each test case
      vim.cmd("%bwipeout!")
    end,
    post_once = function()
      -- Runs once after all tests in this set
    end,
  },
})
```

### Nested sets (grouping tests)

```lua
local T = new_set()

T["parse"] = new_set()

T["parse"]["handles empty string"] = function()
  expect.equality(require("my-plugin.parser").parse(""), {})
end

T["parse"]["handles valid input"] = function()
  local result = require("my-plugin.parser").parse("hello")
  expect.equality(result, { "hello" })
end

T["format"] = new_set()

T["format"]["adds prefix"] = function()
  local result = require("my-plugin.formatter").format("test")
  expect.equality(result, "[PREFIX] test")
end

return T
```

Each nested set can have its own hooks — they compose with parent hooks.

### Parametric tests

Since sets are plain Lua tables, generate test cases programmatically:

```lua
local T = new_set()

local cases = {
  { input = "",      expected = 0 },
  { input = "hello", expected = 5 },
  { input = "café",  expected = 4 },
}

for _, case in ipairs(cases) do
  T["strlen('" .. case.input .. "') == " .. case.expected] = function()
    expect.equality(require("my-plugin").strlen(case.input), case.expected)
  end
end

return T
```

### Testing buffer operations

Many Neovim plugins manipulate buffers. Here is the pattern:

```lua
local T = new_set({
  hooks = {
    pre_case = function()
      vim.cmd("enew")
    end,
    post_case = function()
      vim.cmd("%bwipeout!")
    end,
  },
})

T["inserts text at cursor"] = function()
  -- Set buffer content
  vim.api.nvim_buf_set_lines(0, 0, -1, false, { "line 1", "line 2" })
  -- Position cursor
  vim.api.nvim_win_set_cursor(0, { 1, 0 })

  -- Call plugin function
  require("my-plugin").insert_text("inserted")

  -- Assert buffer state
  local lines = vim.api.nvim_buf_get_lines(0, 0, -1, false)
  expect.equality(lines, { "inserted", "line 1", "line 2" })
end

return T
```

### Testing async operations

For plugins with async behavior, use `vim.wait()`:

```lua
T["async operation completes"] = function()
  local done = false
  require("my-plugin").async_action(function()
    done = true
  end)

  -- Wait up to 1 second for completion
  vim.wait(1000, function() return done end, 10)
  expect.equality(done, true)
end
```

### Child process testing (advanced isolation)

For tests that need full isolation (different configs, testing UI), mini.test provides
`MiniTest.new_child_neovim()`. See `references/mini-test-api.md` for details.

```lua
local child = MiniTest.new_child_neovim()

local T = new_set({
  hooks = {
    pre_once = function() child.start() end,
    pre_case = function() child.restart() end,
    post_once = function() child.stop() end,
  },
})

T["plugin loads without errors"] = function()
  child.lua("require('my-plugin').setup({})")
  local result = child.lua_get("vim.g.my_plugin_loaded")
  expect.equality(result, true)
end

return T
```

## Assertions reference (quick)

| Method | Description |
|--------|-------------|
| `expect.equality(a, b)` | Deep equality (tables compared recursively) |
| `expect.no_equality(a, b)` | Not equal |
| `expect.error(fn)` | Function must throw |
| `expect.no_error(fn)` | Function must not throw |
| `expect.reference_screenshot(screenshot)` | Compare screenshot (child process) |

For the full API including screenshot testing and child process methods,
read `references/mini-test-api.md`.

For exhaustive code examples covering every test type (parametrize, child
process, screenshots, async, busted-style, skip/finally, n_retry, data,
custom collection…), read `references/examples.md`.

## CI with GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        nvim-version: ["stable", "nightly"]
    steps:
      - uses: actions/checkout@v4
      - uses: rhysd/action-setup-vim@v1
        with:
          neovim: true
          version: ${{ matrix.nvim-version }}
      - name: Run tests
        run: make test
```

## Common pitfalls

- Forgetting `return T` at the end of a test file — tests silently won't run
- Not cleaning up buffers/state between tests — use `pre_case`/`post_case` hooks
- Using `assert()` instead of `expect` — raw asserts give poor error messages
- Testing module state without re-requiring — Lua caches modules in `package.loaded`,
  so if your module has mutable state, clear it in `pre_case`:
  `package.loaded["my-plugin"] = nil`
- Running tests without `--headless` — omitting this flag opens a visible Neovim window
