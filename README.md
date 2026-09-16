# Agent skills

Portable agent skills. Everything here runs unmodified on Claude Code, Codex, Cursor, opencode, Copilot, Gemini CLI, Amp and the rest.

`AGENTS.md` is the authoring contract. `CLAUDE.md` is a symlink to it, because Claude Code reads that name and not `AGENTS.md`. One source, both discovery paths.

## Layout

```
AGENTS.md                the contract
CLAUDE.md                symlink -> AGENTS.md
Makefile                 validate / pack
scripts/
  validate.sh            the linter
  pack.sh                zips a skill for a Cowork upload
  banned-fail.txt        phrases that fail a build
  banned-warn.txt        phrases that warn
skills/
  <skill-name>/          published, installable from this repository
    SKILL.md             required
    references/          optional, loaded on demand
    scripts/             optional, POSIX shell
    config.yaml          optional, shareable values
    evals.yaml           optional, test cases
.agents/skills/
  <skill-name>/          harness, the skills this repository runs on itself
.claude/skills/
  <skill-name>           symlink -> ../../.agents/skills/<skill-name>
```

A skill is in one tree or the other. Both are source and both are edited by hand; neither is generated from the other, and `make validate` checks both.

Every `SKILL.md` under `.agents/skills/` carries `metadata.internal: true`. An install walks the whole repository tree and reads that directory as a skills container like any other, so the marker is what keeps a harness skill out of the listing. `AGENTS.md` has the rule.

## Create a skill

```sh
cd skills && npx skills init my-skill
```

Then write it, and run `make validate` on what you wrote. `.agents/skills/skill-author/` is the skill that does this properly: point any agent at it and it will follow the contract, ground the content, and iterate against the validator.

## Validate

```sh
make validate
```

It checks both trees: `skills/` published, `.agents/skills/` harness.

Fails on: non-portable frontmatter keys, a harness skill missing `metadata.internal: true` or a published skill carrying it, a `name` that does not match its directory, an over-long description, a description containing angle brackets, an unquoted description containing `": "` or `" #"` (YAML reads a nested mapping or a comment, and the skill either never installs or installs with half its triggers gone), banned phrasing, missing references, a nested `SKILL.md`, malformed `evals.yaml`, and non-POSIX shell.

Warns on: a description over 900 characters, a body over 500 lines, absolute paths, all-caps imperatives, a long reference with no contents list, references more than one level deep, unquoted YAML booleans in config, and a skill with references or scripts but no evals.

FAIL sets a non-zero exit; WARN does not.

To relax or extend the phrase checks, edit `scripts/banned-fail.txt` and `scripts/banned-warn.txt`. The linter reads them at runtime.

To lint a skill outside this repository:

```sh
sh scripts/validate.sh /path/to/some/skills
```

## Install

```sh
npx skills add . -g -y                # every skill
npx skills add . -g -y -s my-skill    # just one
```

Keep `-g` on both. Without it the CLI installs project-scoped, which copies `skills/*` into `.agents/skills/` and writes a `skills-lock.json`, burying the harness tree under the published skills. Nothing in this repository installs project-scoped; the harness tree is maintained by editing it.

The CLI copies each skill into a canonical store, `~/.agents/skills/<name>`, then points every agent directory at that copy — `~/.claude/skills/<name>` becomes a symlink to it. Most agents read the canonical store directly.

**This repository is the source, not the install.** Editing a `SKILL.md` here does not reach the installed copy. Re-run the command after every change; it is idempotent and propagates edits and reverts alike.

With no `-a`, the CLI targets the agents it finds on the machine. Install a new agent later and it holds none of these until this runs again.

`-s` takes a name that exists under `skills/`. Pass one that does not and the CLI exits 1 listing what is available, rather than installing nothing quietly.

## Uninstall

```sh
npx skills remove -g -y $(ls skills)    # every skill this repo defines
npx skills remove -g -y my-skill
```

Names come from `skills/` on disk and are always passed explicitly. Never `npx skills remove --all`: it takes out every skill you have installed, from every source, not only these.

No `-a` flag either, so the CLI cleans the link in every agent directory rather than only the ones you last installed to. An agent you have since stopped using still holds a live copy otherwise.

A name need not still exist under `skills/`. That is the point on a rename: `git mv` the directory, update `name` to match, remove the old name, then install again. Skip the removal and the old name stays installed and keeps routing.

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
