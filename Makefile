.POSIX:
.PHONY: help validate test-hooks install uninstall pack new

help:
	@echo "validate           lint every skill against AGENTS.md"
	@echo "test-hooks         run the hook gates against fixture payloads"
	@echo "install            install every skill into every agent in agents.txt"
	@echo "install name=<x>   install just skills/<x>"
	@echo "uninstall          remove every skill this repo defines, from every agent"
	@echo "uninstall name=<x> remove just <x>"
	@echo "pack               zip every skill into build/ for a Cowork upload"
	@echo "pack name=<x>      zip just skills/<x>"
	@echo "new name=<x>       scaffold skills/<x>/SKILL.md"

validate:
	@sh scripts/validate.sh

test-hooks:
	@sh scripts/test-hooks.sh

install:
	@test -z "$(name)" || test -d "skills/$(name)" || \
		{ echo "no skills/$(name)" >&2; exit 1; }
	@if [ -n "$(name)" ]; then sh scripts/install.sh -s "$(name)"; \
	 else sh scripts/install.sh; fi

uninstall:
	@sh scripts/uninstall.sh $(name)

pack:
	@test -z "$(name)" || test -d "skills/$(name)" || \
		{ echo "no skills/$(name)" >&2; exit 1; }
	@if [ -n "$(name)" ]; then sh scripts/pack.sh -s "$(name)"; \
	 else sh scripts/pack.sh; fi

new:
	@test -n "$(name)" || { echo "usage: make new name=my-skill" >&2; exit 1; }
	@echo "$(name)" | grep -qE '^[a-z0-9]+(-[a-z0-9]+)*$$' || \
		{ echo "name must be lowercase alphanumeric and hyphens" >&2; exit 1; }
	@test ! -e "skills/$(name)" || { echo "skills/$(name) already exists" >&2; exit 1; }
	@mkdir -p "skills/$(name)"
	@printf -- '---\nname: %s\ndescription: TODO what it does. Use when TODO.\n---\n\n# %s\n\n## When to use\n\nTODO\n\n## Steps\n\n1. TODO\n' \
		"$(name)" "$(name)" > "skills/$(name)/SKILL.md"
	@echo "created skills/$(name)/SKILL.md"
	@sh scripts/validate.sh || true
