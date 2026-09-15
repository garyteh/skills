# Agent skills

Portable agent skills. Everything here runs unmodified on Claude Code, Codex, Cursor, opencode, Copilot, Gemini CLI, Amp and the rest.

`AGENTS.md` is the authoring contract. `CLAUDE.md` is a symlink to it, because Claude Code reads that name and not `AGENTS.md`. One source, both discovery paths.

## Layout

```
AGENTS.md                the contract
CLAUDE.md                symlink -> AGENTS.md
agents.txt               install targets, one agent id per line
Makefile                 validate / install / uninstall / new
hooks/
  require-worktree.sh    gate: the primary checkout is not for editing
  require-trunk-landing.sh  gate: land through the documented procedure
.claude/settings.json    hook wiring for Claude Code
.codex/hooks.json        hook wiring for Codex CLI
scripts/
  validate.sh            the linter
  test-hooks.sh          fixture tests for the gates
  install.sh             reads agents.txt, drives the skills CLI
  uninstall.sh           removes this repo's skills from every agent
  pack.sh                zips a skill for a Cowork upload
  banned-fail.txt        phrases that fail a build
  banned-warn.txt        phrases that warn
skills/
  <skill-name>/
    SKILL.md             required
    references/          optional, loaded on demand
    scripts/             optional, POSIX shell
    config.yaml          optional, shareable values
    evals.yaml           optional, test cases
```

## Create a skill

```sh
make new name=my-skill
```

Then write it. `skills/skill-author/` is the skill that does this properly: point any agent at it and it will follow the contract, ground the content, and iterate against the validator.

## Validate

```sh
make validate
```

Fails on: non-portable frontmatter keys, a `name` that does not match its directory, an over-long description, a description containing angle brackets, an unquoted description containing `": "` or `" #"` (YAML reads a nested mapping or a comment, and the skill either never installs or installs with half its triggers gone), banned phrasing, missing references, a nested `SKILL.md`, malformed `evals.yaml`, and non-POSIX shell.

Warns on: a description over 900 characters, a body over 500 lines, absolute paths, all-caps imperatives, a long reference with no contents list, references more than one level deep, unquoted YAML booleans in config, and a skill with references or scripts but no evals.

FAIL sets a non-zero exit; WARN does not.

To relax or extend the phrase checks, edit `scripts/banned-fail.txt` and `scripts/banned-warn.txt`. The linter reads them at runtime.

To lint a skill outside this repository:

```sh
sh scripts/validate.sh /path/to/some/skills
```

## Install

```sh
make install
```

Runs `npx skills add . -g -y` against every agent listed in `agents.txt`.

The CLI copies each skill into a canonical store, `~/.agents/skills/<name>`, then points every agent directory at that copy — `~/.claude/skills/<name>` becomes a symlink to it. Most agents read the canonical store directly.

**This repository is the source, not the install.** Editing a `SKILL.md` here does not reach the installed copy. Re-run `make install` after every change; it is idempotent and propagates edits and reverts alike.

Add or remove targets by editing `agents.txt`. `npx skills add --help` lists the valid agent ids.

To push a single skill:

```sh
make install name=my-skill
```

Same store, same symlinks, one skill. Fails if `skills/my-skill` does not exist, because the CLI would otherwise install nothing and exit 0.

## Hooks

Skills are model-invoked, so a description is a suggestion the router may
decline. Two `PreToolUse` gates make the git workflow non-optional instead.

- `hooks/require-worktree.sh` denies an edit issued from the primary checkout
  and points at the `git-worktree` skill. It gates the edit tools, and only
  where the target lands inside this repository. It allows inside a linked
  worktree, detected by `git rev-parse --git-common-dir`, so it cannot block
  the worktree it just asked for.

  It does not read shell commands. The gate has to catch the first edit rather
  than every write: once a session is working in a worktree, everything it does
  after that is already isolated. Deciding whether a shell command writes means
  parsing shell, which denies ordinary reads every time it is tried.
- `hooks/require-trunk-landing.sh` denies an ad hoc `git commit` or `git push`
  and points at the `git-solo-trunk` skill. It reads the subcommand rather
  than the two words side by side, so a global option in front of the verb
  does not slip past it.

Each denial names its escape: set `WORKTREE_GATE=off` or `TRUNK_GATE=off` in
the environment. Export it before starting the agent, or put it in
`.claude/settings.local.json`, which is gitignored and local to one checkout:

```json
{ "env": { "WORKTREE_GATE": "off" } }
```

The escape is the environment and nothing else. A `PreToolUse` hook runs before
the command, so an assignment written in front of one never reaches the hook's
environment — it arrives as text in the payload. Matching it there meant any
command that merely quoted the words turned the gate off, including a command
that then wrote a file.

So a gate is on or off for a session rather than for one command. An agent
cannot land a change mid-session unless the variable is already set, which is
the point: it hands back to you. These stay speed bumps rather than controls,
and they exist so the skill is the path of least resistance.

The scripts are portable; only the wiring differs. `.claude/settings.json` and
`.codex/hooks.json` carry the same events, matchers and commands, because both
harnesses call the shell tool `Bash`, alias their edit tools to `Edit`/`Write`,
put the command at `.tool_input.command` on stdin, and block on
`permissionDecision: "deny"`. Codex runs project-layer hooks only once the
project is trusted.

Neither skill depends on its gate. Both have to run unmodified where no hooks
exist, so all the coupling lives in the hook — which means a skill rename has
to update the deny message that names it.

```sh
make test-hooks
```

Feeds fixture payloads to each script and asserts the decision. Every case runs
twice, once with `jq` on `PATH` and once without, because the scripts carry a
`sed` fallback and an untested fallback is one that has already broken.

## Uninstall

```sh
make uninstall              # every skill this repo defines
make uninstall name=my-skill
```

Names come from `skills/*/` on disk, never a list in the script, and are always passed explicitly: `npx skills remove --all` would take out every skill you have installed from anywhere, so this tooling does not use it.

No `-a` flag either, so the CLI cleans the link in every agent directory rather than only the agents in `agents.txt`. Drop an agent from that list and its copy is still installed and still routing; a plain `make uninstall` reaches it.

`name=` need not exist in `skills/`. That is the point on a rename: `git mv` the directory, update `name` to match, `make uninstall name=<old>`, then `make install`. Skip the removal and the old name stays installed and keeps routing.

## Package

```sh
make pack                   # every skill
make pack name=my-skill     # just one
```

Writes `build/<name>.zip`. Cowork installs a skill from a zip of its directory, so each archive carries a single top-level folder named for the skill with `SKILL.md` and everything beside it inside — that shape is what the uploader expects. `.DS_Store` is excluded; file modes survive, so a bundled script stays executable.

A multi-file skill changes by repackaging it. Editing an installed copy does nothing, so re-run `make pack` and upload the new archive rather than patching what is already there.

`build/` is gitignored, so archives never land in a commit. Run `make validate` first: packing does not lint.

## Publishing

The remote makes these skills installable anywhere:

```sh
npx skills add garyteh/skills -g
```

Audit for anything internal before making a remote public.
