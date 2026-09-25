# Authoring reference

Read this when writing or revising a skill's description, deciding how to split it, or moving values into config.

## Contents

- Description craft
- Collisions between skills
- Splitting
- Writing the content
- Config
- State

## Description craft

The description is the whole routing mechanism. Everything else in the skill is invisible until it fires.

Budget it for triggers first. A description that spends its length describing capability and none of it on trigger vocabulary will not fire.

**Specific beats broad.** Name the phrases a real person types. "Use when creating a new skill, editing an existing SKILL.md, or checking one for portability" routes; "use for skill-related tasks" does not. Broad wording fails in both directions at once: it misses the specific request whose words it never named, and it grabs requests belonging to a sibling.

**Outcome phrases for hand-off targets.** Where other skills may hand work to this one, name the outcomes they would ask for, such as "make it more personal" or "less AI", not only this skill's own label. A hand-off describes the outcome it wants, so a description that names only its label never matches.

**Third person.** The router reads the description as a statement about the skill, not as an instruction to follow.

**No process.** Describing the workflow gives the agent a summary it can act on instead of reading the body. State the outcome, never the steps.

**No operational values.** Identifiers, paths, thresholds and channel names belong in config. Trigger words may be organisation-specific, because the vocabulary people type is theirs.

**Leave headroom.** The hard limit is 1024 characters. A description written to the limit fails on the next small edit.

**Plain text.** No angle brackets, so the description survives every install path unchanged. Plain prose costs nothing.

## Collisions between skills

Relevant once a family of skills shares vocabulary. A single skill has nothing to collide with.

- Where two skills genuinely share trigger words, one claims the territory and the other names it in an exclusion. Write both sides in the same edit. The failure is silent in both directions: two skills claiming one request, or both excluding it and neither firing.
- Where vocabulary is already disjoint, write no exclusion. It buys nothing and spends budget triggers need.
- Where every skill in a family needs an exclusion against every sibling, the family is one skill. N-1 exclusions each is the signal to merge. A merged skill takes a mode parameter and absorbs the next case in one edit; a family of N needs 2N-1 edits for the same thing, and a half-finished pass leaves exactly the silent misfire the exclusions were meant to prevent.
- Prefer sharpening both descriptions over adding an exclusion. Exclusions are for pairs that have actually collided, not insurance against every pair.

## Splitting

The reason to keep `SKILL.md` tight is dilution, not token cost. Instructions compete for attention, so a long file gives its important rules less weight.

Apply the usage test: where a typical run reads less than half the file, split. Line counts are prompts to apply that test, not thresholds in themselves. Around 500 lines, run it. Past 1,000, suspect two jobs sharing a config.

What never moves:

- Control flow and decision points.
- Rules that shape every path.
- Anything the agent needs before it knows which branch it is on.

Splitting these is how a skill gets half-executed, and the failure is silent.

What moves happily: error tables, schemas, worked examples, long option lists, anything consulted only on one branch.

Keep references exactly one level deep from `SKILL.md`. Every hop is a decision the agent may not make.

Give a reference over 200 lines a contents list, so a reader who stops early still knows what is there.

## Writing the content

- Assume the reader knows its domain. Never explain what any model already knows.
- Be explicit about control flow and decision points even so. Terse on general knowledge, precise on what only this skill knows: that is the resolution of "assume competence" against "write for the weakest model that will run it".
- One term per concept. Never alternate between "field", "box" and "element" for the same thing.
- One default per decision the skill makes, plus a single escape hatch. Not a menu.
- State the rule, then the reason. All-caps imperatives give a rule with no rubric, so the agent follows the letter and misses the cases you did not spell out. Reserve bare imperatives for fragile steps.
- Give any skill with real run history a Known Gotchas section listing concrete failure modes actually seen. On a mature skill this is usually its most valuable content.
- Use a template for output shape and two or three input/output pairs for style. Templates show the skeleton, examples calibrate the voice.
- Mark every template strict or flexible. Go strict only when something downstream parses the output, because strict templates suppress useful variation.

## Config

Indirection has a cost. Every value moved out is a second file to read and a mapping to hold. Move what earns it.

- A value goes to `config.yaml` when it appears in two or more places, or when someone adopting the skill would plausibly change it: identifiers, handles, project keys, URLs, paths, timezone, whitelists.
- A value used once stays inline with its reason attached. A threshold in exactly one instruction is clearer beside that instruction than behind a lookup.
- Once a value is in config, no file restates it. `SKILL.md` and every reference point at config instead.
- One config file per skill. Never ship a second machine-readable copy for scripts, because two files holding the same values drift.
- YAML, for consistency with the ecosystem rather than because it is the better format. It is not: quote any string YAML could misread. Bare `no`, `yes`, `on` and `off` parse as booleans, and bare version numbers parse as floats.

The test for what belongs in config is whether a stranger could use the skill unchanged. If not, the trait is configuration.

Personal and organisational traits that become config: engineering background, language and framework stack, team domain, timezone, board and channel identifiers.

The exception is narrow. A skill whose subject matter *is* one specific person may name them, because removing the person makes the skill meaningless. That covers a personal writing voice or review rubric. It never covers the person who happens to run the skill, and never a job title standing in for an individual. A household name used only as a style reference is not a trait of whoever runs the skill, so it is neither config nor this exception. The repository's `AGENTS.md` says when one may be named.

## State

Config and state are different things and live in different places.

- Config is bundled and read-only. State is mutable and lives outside the bundle, in the workspace the skill operates on.
- State files are hidden dotfiles. They are machinery, not user content, and should not clutter a directory someone browses.
- Document the exact state path in `config.yaml`, so debugging is a lookup rather than a search.
- Choose the format the access pattern wants. A watermark is fine as YAML; an append-only log wants a log format, not a rewritten document.
