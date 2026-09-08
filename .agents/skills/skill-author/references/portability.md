# Portability reference

Read this before writing anything that touches tools, paths, or shell.

## What every harness agrees on

Only two things are universal:

1. A skill is a directory containing `SKILL.md`.
2. That file opens with YAML frontmatter carrying `name` and `description`.

Everything else varies. Build on those two and nothing more.

## Frontmatter that is not portable

| Key | Reality |
| --- | --- |
| `allowed-tools` | Claude Code only. Other hosts ignore it, so it grants no safety anywhere else. |
| `disable-model-invocation` | Claude Code only. |
| `argument-hint` | Claude Code only. |
| `model` | Host-specific and quickly stale. |
| `license` | Read by nobody at load time. Put licensing in a `LICENSE` file. |
| `compatibility` | Free text. No host parses or enforces it. State prerequisites in the body, where the agent will actually read them. |
| `metadata` | Arbitrary. Only `metadata.internal` has defined meaning, and only to the skills CLI. |

A skill that carries these advertises behaviour it will not get. Leave them out.

## Prose that is not portable

- Naming a specific tool. "Use the Grep tool" means nothing to a host whose search tool has another name. Write "search the codebase".
- Assuming a permission or approval model. Some hosts prompt, some sandbox, some do neither.
- Assuming subagents, background tasks, or parallel execution exist.
- Assuming a slash-command syntax, or that the skill is invoked by name at all. Most hosts route on the description.
- Assuming a scratch directory path. Ask for one or use `mktemp`.

State a requirement instead of a mechanism: "confirm before overwriting" travels; "wait for the approval prompt" does not.

## Scripts

Target `#!/bin/sh` and POSIX. The common bashisms to avoid:

| Avoid | Use |
| --- | --- |
| `[[ x == y ]]` | `[ "$x" = "$y" ]` |
| `arr=(a b c)` | positional parameters, or a newline-delimited file |
| `<<< "$var"` | `printf '%s\n' "$var" \|` |
| `function f {` | `f() {` |
| `${var,,}` | `printf '%s' "$var" \| tr 'A-Z' 'a-z'` |
| `$RANDOM`, `$SECONDS` | `mktemp`, `date` |

Also:

- Check for every external binary before calling it: `command -v jq >/dev/null 2>&1 || { ...; }`.
- A variable incremented inside a pipeline runs in a subshell and is lost. Tally to a file.
- `sh -n` on macOS runs bash in POSIX mode and will not catch every bashism. Grep for the constructs above as well.
- Mark scripts executable. A symlinked install preserves the mode from this repository.

## How installing works

The skills CLI discovers `skills/<name>/SKILL.md` in a repository, then installs in two tiers:

1. It **copies** the skill into a canonical store. Globally that is `~/.agents/skills/<name>`, the universal path most agents read directly.
2. It **symlinks** the directories of agents that insist on their own location at that canonical copy, so `~/.claude/skills/<name>` becomes a link to `~/.agents/skills/<name>`.

Two consequences matter when authoring:

- The source repository is never linked into the install. Editing a skill in the repository does not change the installed copy. Re-run the install after every edit.
- Which agents get their own directory rather than sharing the universal store depends on the CLI version and on what it detects. Read the install summary it prints, rather than assuming a path.

Project-scoped installs follow the same split: `.agents/skills/` for most agents, with `.claude/skills/` the common exception.

Run `npx skills add --help` for the current agent ids rather than trusting any copy of the list.

## Contract files

The instruction file a harness reads at startup, which is separate from skills:

| File | Read by |
| --- | --- |
| `AGENTS.md` | Codex, Cursor, opencode, Gemini CLI, Amp |
| `CLAUDE.md` | Claude Code |
| `.github/copilot-instructions.md` | GitHub Copilot |

Claude Code does **not** read `AGENTS.md`, despite the name appearing in its binary. Test it rather than assuming: put a unique fact in a project `AGENTS.md`, ask a fresh session for that fact, and see whether it comes back.

Keep one source and symlink the rest at it, so the rules cannot drift:

```sh
ln -s AGENTS.md CLAUDE.md
```

A pointer file saying "see AGENTS.md" is weaker, because reading it is a hop the agent may not take.

## Changing a skill

- Verify by rule-level diff, old against new, in both directions: rules dropped, and rules invented. Never verify by running anything that writes.
- Stage it. Build, verify, cut over one at a time, then delete the old.
- Show the staged sequence before any of it runs.
- A rename is a move plus a cleanup: `git mv` the directory, update `name` to match, `npx skills remove <old-name>`, then reinstall. Skipping the removal leaves the old name installed and routing.
- A multi-file skill changes as a whole. Editing an installed copy does nothing to the source, and editing the source does nothing to the install until it is re-run.
- After changing a skill, diff the source against the canonical store to confirm what landed. Never report an install you have not verified.
