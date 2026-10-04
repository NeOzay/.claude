# mini.test API Reference

This is the complete API reference for mini.test. Read this when you need details
beyond what SKILL.md covers — child process methods, screenshot testing, custom
reporters, or advanced configuration.

## Table of Contents

1. [MiniTest.setup()](#setup)
2. [MiniTest.new_set()](#new_set)
3. [MiniTest.expect](#expect)
4. [MiniTest.run() / run_file()](#running)
5. [MiniTest.new_child_neovim()](#child-neovim)
6. [Screenshot testing](#screenshots)
7. [Reporters](#reporters)
8. [Filtering and skipping](#filtering)

---

## setup()                                                          <a id="setup"></a>

```lua
MiniTest.setup(config)
```

Call once in `minimal_init.lua`. Config is optional — defaults are sensible.

```lua
MiniTest.setup({
  -- Collection of test cases. See new_set().
  collect = {
    -- Temporarily redefine these globals during collection
    emulate_busted = true,   -- provides describe/it/assert shims (compatibility)
    find_files = function()
      return vim.fn.globpath("tests", "**/test_*.lua", true, true)
    end,
    filter_cases = function(case)
      return true  -- return false to skip
    end,
  },

  -- Execution options
  execute = {
    reporter = nil,      -- nil means default terminal reporter
    stop_on_error = false,
  },

  -- Scripts to run before/after all collected cases
  script_path = nil,
})
```

The `find_files` function controls which files are collected when running
`MiniTest.run()`. By default it globs for `test_*.lua` in `tests/`. Change this
if your test files follow a different naming convention.

---

## new_set()                                                      <a id="new_set"></a>

```lua
local T = MiniTest.new_set(opts)
```

Creates a new test set (a table with special metatable). Options:

```lua
MiniTest.new_set({
  hooks = {
    pre_once  = function() end,  -- before all cases in this set
    pre_case  = function() end,  -- before each case
    post_case = function() end,  -- after each case
    post_once = function() end,  -- after all cases in this set
  },
  parametrize = { { arg1, arg2 }, { arg3, arg4 } },
})
```

### Parametrize

When `parametrize` is provided, every test case in the set is run once for each
parameter set. The parameters are passed as arguments to the test function:

```lua
local T = new_set({
  parametrize = { { "hello", 5 }, { "", 0 }, { "café", 4 } },
})

T["strlen is correct"] = function(input, expected)
  expect.equality(#input, expected)
end
```

This creates 3 test cases automatically. Parametrize tables can be nested across
set levels — they multiply (cartesian product).

### Nesting

Sets can be nested. Child hooks compose with parent hooks:

```lua
local T = new_set({ hooks = { pre_case = parent_setup } })
T["group"] = new_set({ hooks = { pre_case = child_setup } })
T["group"]["test"] = function() ... end
-- Execution order: parent_setup -> child_setup -> test function
```

---

## expect                                                          <a id="expect"></a>

All assertion methods. On failure, they throw an error with a descriptive message
showing expected vs actual values.

### expect.equality(left, right)

Deep equality check. Tables are compared recursively by value.

```lua
expect.equality(1, 1)                          -- pass
expect.equality({ a = 1 }, { a = 1 })          -- pass
expect.equality({ 1, 2 }, { 1, 3 })            -- fail
```

### expect.no_equality(left, right)

Inverse of `equality`.

```lua
expect.no_equality(1, 2)                        -- pass
expect.no_equality({ a = 1 }, { a = 1 })        -- fail
```

### expect.error(fn, pattern)

Asserts that `fn()` throws an error. Optional `pattern` checks the error message
matches (Lua pattern, not regex).

```lua
expect.error(function() error("bad input") end)                  -- pass
expect.error(function() error("bad input") end, "bad")           -- pass
expect.error(function() error("bad input") end, "good")          -- fail
expect.error(function() return 42 end)                           -- fail
```

### expect.no_error(fn)

Asserts that `fn()` does NOT throw.

```lua
expect.no_error(function() return 42 end)                        -- pass
expect.no_error(function() error("oops") end)                    -- fail
```

### expect.reference_screenshot(screenshot)

Used with child process screenshot testing. See [Screenshots](#screenshots).

---

## Running tests                                                  <a id="running"></a>

### MiniTest.run(opts)

Collects and runs all test files matching the configured `find_files` pattern.

```lua
MiniTest.run()          -- run all
MiniTest.run({
  collect = {
    find_files = function()
      return { "tests/test_specific.lua" }
    end,
  },
})
```

### MiniTest.run_file(path, opts)

Run a single test file:

```lua
MiniTest.run_file("tests/test_utils.lua")
```

### MiniTest.run_at_location(opts)

Run test case at current cursor location (useful during development):

```lua
-- In a mapping:
vim.keymap.set("n", "<leader>tt", MiniTest.run_at_location)
```

### Command-line usage

```bash
# Run all tests
nvim --headless -u tests/minimal_init.lua -c "lua MiniTest.run()"

# Run single file
nvim --headless -u tests/minimal_init.lua -c "lua MiniTest.run_file('tests/test_utils.lua')"

# Run and quit (for CI — exit code reflects pass/fail)
nvim --headless -u tests/minimal_init.lua -c "lua MiniTest.run()" -c "qa!"
```

Note: `MiniTest.run()` calls `vim.schedule()` internally, so adding `-c "qa!"` after
it works because the quit happens after tests finish.

---

## Child Neovim                                              <a id="child-neovim"></a>

`MiniTest.new_child_neovim()` spawns a separate Neovim process that you control
from your test. This gives full isolation — separate config, state, and UI.

```lua
local child = MiniTest.new_child_neovim()

local T = new_set({
  hooks = {
    pre_once  = function() child.start({ args = { "-u", "tests/minimal_init.lua" } }) end,
    pre_case  = function() child.restart() end,
    post_once = function() child.stop() end,
  },
})
```

### child methods

| Method | Description |
|--------|-------------|
| `child.start(opts)` | Start child process. `opts.args` = Neovim CLI args |
| `child.stop()` | Kill child process |
| `child.restart()` | Stop + start (resets state between tests) |
| `child.lua(code_string)` | Execute Lua code in child (no return value) |
| `child.lua_get(code_string)` | Execute Lua and return the result |
| `child.lua_func(fn, args)` | Execute a function in child context |
| `child.cmd(vim_command)` | Execute a Vim command (`:cmd`) |
| `child.type_keys(keys)` | Simulate key presses |
| `child.get_screenshot()` | Capture terminal state for screenshot testing |
| `child.set_lines(lines, start, finish)` | Set buffer lines |
| `child.get_lines(start, finish)` | Get buffer lines |
| `child.set_cursor(row, col)` | Set cursor position |
| `child.get_cursor()` | Get cursor position |
| `child.set_size(rows, cols)` | Resize terminal |
| `child.is_running()` | Check if child is alive |
| `child.ensure_started()` | Start if not already running |

### Examples

```lua
T["plugin setup works"] = function()
  child.lua("require('my-plugin').setup({ option = true })")
  local opt = child.lua_get("require('my-plugin').config.option")
  expect.equality(opt, true)
end

T["mapping triggers action"] = function()
  child.lua("require('my-plugin').setup({})")
  child.set_lines({ "hello world" }, 0, -1)
  child.set_cursor(1, 0)
  child.type_keys("<leader>a")  -- trigger plugin mapping
  local lines = child.get_lines(0, -1)
  expect.equality(lines, { "HELLO WORLD" })
end

T["command exists after setup"] = function()
  child.lua("require('my-plugin').setup()")
  local has_cmd = child.lua_get([[
    return vim.fn.exists(':MyPluginCommand') == 2
  ]])
  expect.equality(has_cmd, true)
end
```

---

## Screenshot testing                                        <a id="screenshots"></a>

Screenshot testing captures the visual state of a child Neovim process and compares
it against a reference. Useful for testing UI elements, highlights, floating windows.

### Taking a screenshot

```lua
T["UI renders correctly"] = function()
  child.lua("require('my-plugin').open_float()")
  local screenshot = child.get_screenshot()
  expect.reference_screenshot(screenshot)
end
```

### How it works

1. First run: no reference exists → test creates a reference file in
   `tests/screenshots/` and passes
2. Subsequent runs: compares current screenshot to saved reference
3. If different: test fails and shows the diff
4. To update references: delete the screenshot file and re-run

### Screenshot options

```lua
child.set_size(24, 80)  -- set terminal size before screenshot
local screenshot = child.get_screenshot({
  redraw = true,  -- force redraw before capture (default: true)
})
```

Screenshots capture both text content and highlight groups, so they detect
both content and visual regressions.

---

## Reporters                                                    <a id="reporters"></a>

Reporters control test output format.

### Built-in reporters

```lua
MiniTest.setup({
  execute = {
    reporter = MiniTest.gen_reporter.buffer({ window = { ... } }),
    -- or
    reporter = MiniTest.gen_reporter.stdout({ group_depth = 2 }),
  },
})
```

- `buffer` — shows results in a Neovim buffer (interactive use)
- `stdout` — prints to stdout (headless/CI use, this is the default in headless mode)

### Custom reporter

A reporter is a table with these optional functions:

```lua
{
  start = function(all_cases) end,
  update = function(case_num, case, state) end,  -- state: "pass"/"fail"/"skip"
  finish = function(all_cases) end,
}
```

---

## Filtering and skipping                                      <a id="filtering"></a>

### Skip a test

There is no built-in `skip()`. Instead, conditionally define tests:

```lua
if vim.fn.has("nvim-0.10") == 1 then
  T["uses nvim 0.10 feature"] = function()
    -- ...
  end
end
```

Or use `filter_cases` in setup to skip based on test metadata.

### Run specific tests from CLI

Filter via `find_files` or `filter_cases` overrides:

```lua
-- Run only tests whose name contains "parse"
MiniTest.run({
  collect = {
    filter_cases = function(case)
      return case.desc[#case.desc]:find("parse") ~= nil
    end,
  },
})
```

---

## Tips for writing good tests

- Keep test files focused — one test file per module
- Use descriptive string keys: `T["parse handles UTF-8 input"]` not `T["test1"]`
- Prefer `pre_case` cleanup over relying on test order
- Use child process for integration tests, direct calls for unit tests
- Clear `package.loaded` when testing modules with mutable state
- Set terminal size explicitly in screenshot tests for reproducibility
