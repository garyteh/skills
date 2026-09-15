.POSIX:
.PHONY: help validate test-hooks pack

help:
	@echo "validate           lint every skill against AGENTS.md"
	@echo "test-hooks         run the hook gates against fixture payloads"
	@echo "pack               zip every skill into build/ for a Cowork upload"
	@echo "pack name=<x>      zip just skills/<x>"

validate:
	@sh scripts/validate.sh

test-hooks:
	@sh scripts/test-hooks.sh

pack:
	@test -z "$(name)" || test -d "skills/$(name)" || \
		{ echo "no skills/$(name)" >&2; exit 1; }
	@if [ -n "$(name)" ]; then sh scripts/pack.sh -s "$(name)"; \
	 else sh scripts/pack.sh; fi
