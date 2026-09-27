---Commande `:Lexique`, à l'essai avant son intégration dans la configuration Neovim.
---
---FICHIER TEMPORAIRE : `:source ~/.claude/skills/lexique/nvim/lexique.lua` déclare la
---commande ; il sera supprimé une fois `:Lexique` intégrée à `~/.config/nvim`.
---
---  :Lexique          ouvre le lexique local du projet
---  :Lexique!         ouvre le lexique global
---  :Lexique <terme>  affiche la définition du terme, à la casse et aux espaces près
---
---Neovim ne sait rien des lexiques : chemins, termes et définitions viennent de la
---commande `lexique` (`chemin`, `termes`, `definition`), lancée dans le cwd de Neovim.
---Aucun fichier n'est lu ici, aucun chemin construit.

local WARN = vim.log.levels.WARN
local ERROR = vim.log.levels.ERROR

---@param msg string
---@param level? integer
local function notify(msg, level)
	vim.notify(msg, level or WARN, { title = "Lexique" })
end

---Lance `lexique <args>` dans le cwd de Neovim, ou nil si la commande est introuvable.
---`quiet` tait l'erreur : la complétion, rappelée à chaque `<Tab>`, rend alors une liste vide.
---@param args string[]
---@param quiet? boolean
---@return vim.SystemCompleted?
local function run(args, quiet)
	local ok, res = pcall(function()
		return vim.system(vim.list_extend({ "lexique" }, args), { text = true, cwd = vim.uv.cwd() }):wait()
	end)
	if not ok then
		if quiet then
			return nil
		end
		notify("commande `lexique` introuvable : " .. tostring(res), ERROR)
		return nil
	end
	return res
end

---@param bang boolean
local function open(bang)
	local res = run(bang and { "chemin", "--global" } or { "chemin" })
	if not res then
		return
	end
	if res.code ~= 0 then
		return notify(vim.trim(res.stderr or ""))
	end
	vim.cmd.edit(vim.fn.fnameescape(vim.trim(res.stdout or "")))
end

---@param terme string
local function define(terme)
	-- `--` : un terme saisi qui commence par `-` n'est pas une option de `lexique`.
	local res = run({ "definition", "--", terme })
	if not res then
		return
	end
	for line in vim.gsplit(res.stdout or "", "\n", { trimempty = true }) do
		local niveau, nom, definition = line:match("^([^\t]*)\t([^\t]*)\t(.*)$")
		if niveau then
			vim.print(("%s (%s) : %s"):format(nom, niveau, definition))
		end
	end
	local err = vim.trim(res.stderr or "")
	if err ~= "" then
		notify(err, res.code == 0 and WARN or ERROR)
	end
end

---@param s string
---@return string[]
local function words(s)
	return vim.split(vim.trim(s), "%s+", { trimempty = true })
end

---@param s string
---@return string
local function normalize(s)
	return table.concat(words(vim.fn.tolower(s)), " ")
end

---Complète un terme, même composé. Neovim ne remplace que le dernier mot (`arglead`) :
---chaque candidat est rendu à partir du rang de ce mot.
---@param arglead string
---@param cmdline string
---@return string[]
local function complete(arglead, cmdline)
	local typed = cmdline:match("^%s*%a+!?%s+(.*)$") or ""
	local res = run({ "termes" }, true)
	if not res then
		return {}
	end
	-- Un espace final est un mot fini : « signal de » ne doit pas proposer « Signal debug ».
	local prefix = normalize(typed)
	if prefix ~= "" and typed:match("%s$") then
		prefix = prefix .. " "
	end
	local before = #words(typed) - (arglead ~= "" and 1 or 0)

	---@type string[]
	local matches = {}
	for terme in vim.gsplit(res.stdout or "", "\n", { trimempty = true }) do
		local rest = table.concat(words(terme), " ", before + 1)
		if rest ~= "" and vim.startswith(normalize(terme) .. " ", prefix) then
			matches[#matches + 1] = rest
		end
	end
	return matches
end

vim.api.nvim_create_user_command("Lexique", function(opts)
	if opts.args == "" then
		return open(opts.bang)
	end
	if opts.bang then
		return notify("`!` ouvre le lexique global et ne prend pas de terme", ERROR)
	end
	define(opts.args)
end, {
	nargs = "?",
	bang = true,
	complete = complete,
	desc = "Ouvrir le lexique local (! : global), ou afficher la définition d'un terme",
})
