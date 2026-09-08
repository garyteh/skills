---
name: skill-author
description: Writes, revises and audits portable agent skills that run unmodified on Claude Code, Codex, Cursor, opencode, Copilot and other harnesses. Use when creating a new skill, editing an existing SKILL.md, splitting a skill into references, writing eval cases for one, or checking one for cross-harness portability.
metadata:
  internal: true
---

# Skill author

Build skills that need no per-harness fork. Portability is the product.

## Locate the repository first

Walk up from the working directory for a folder holding both `AGENTS.md` and a `skills/` directory. That is the target repository.

Never derive the target from where this skill is installed. Installed skills are read-only copies, and writing beside them reaches nothing. If no repository is found, ask which one to write into.

Read that repository's `AGENTS.md` before writing. It is the contract; this is the procedure.

## Decide it is a skill

Most things that feel like a skill are not one. A prompt used once is a prompt. Reference material with no procedure is a file. Cadence belongs to whatever schedules the work.

A skill is procedural knowledge plus judgement, reused across runs, that the agent would otherwise get wrong or reinvent. Wrapping an exact script counts, when choosing *when* to run it and *with what* needs judgement.

Say so and stop if the answer is no. A skill that should have been a file is worse than the file.

## Baseline before writing

Run the task with no skill loaded. Record the failures verbatim, in the agent's own words.

This is the step that gets skipped, and skipping it is why skills grow rules nothing backs. "It was vague" is not a finding. The exact wording of the failure tells you which rule to write, and the absence of a failure tells you which rule to leave out.

Then gather the real material: the commands that actually worked, the corrections you had to issue, the shape of raw input and output, and the environment truths that violate a reasonable default assumption. Reject generic advice; "handle errors appropriately" teaches nothing.

Read `references/evaluation.md` before writing cases.

## Choose the level of control

Match prescriptiveness to risk.

| Situation | Approach |
| --- | --- |
| Several valid routes | Give the heuristic and the reason. Leave the route open. |
| Destructive, fragile, or order-dependent | Give the exact command. Forbid deviation. |

Getting this backwards is the common failure. Rigid rules on judgement work produce robotic output; loose prose on fragile work produces a different result every run.

Say **execute** or **read** for every bundled script.

## Write it

Create `skills/<name>/SKILL.md` with exactly two frontmatter keys:

```yaml
---
name: matches the directory name
description: what it does, and the concrete phrases that should trigger it
---
```

Spend the description on triggers, specifically. Name the words a real person types. State the outcome, never the internal steps, because a description that summarises the workflow becomes a shortcut the agent follows instead of reading the body.

Then write the body against the contract:

- Lead with the rule, then give the reason.
- Present tense, second-person imperative, Australian English.
- Name no host agent and no harness-specific tool. Write "search the codebase".
- Keep paths relative to `SKILL.md`.
- Write as though the skill has always been this way. No history, no dates, no cadence.

Read `references/authoring.md` for description craft, splitting, config and state.
Read `references/portability.md` before writing anything touching tools, paths or shell.
Read `references/patterns.md` when the skill has a multi-step, batch or destructive workflow.
Read `references/runtime.md` when the skill writes anywhere, handles time, or fetches external content.

## Split only when the usage test says so

Hosts load `SKILL.md` in full once it fires, so every line competes with every other for attention. A long file gives its important rules less weight.

Where a typical run reads less than half the file, split. Line counts are prompts to run that test, not thresholds in themselves.

Never split the main flow. Control flow, decision points, and the rules shaping every path stay in `SKILL.md` whatever its length. Splitting these is how a skill gets half-executed, and it fails silently.

Keep references exactly one level deep, and give each an explicit trigger naming the condition.

## Validate

Run the repository's validator and iterate until it exits clean:

```sh
make validate
```

1. Fix every failure.
2. Read every warning. Fix it, or be able to say why it stands.
3. Re-run. Do not hand the skill over until the exit status is 0.

The validator enforces the mechanical half of the contract. It cannot check whether the skill is *true*, or whether every rule traces to a failure you actually observed. That part is yours.

## Cut what nothing backs

Re-run the eval cases. Any rule that no observed failure justifies gets deleted.

This is the step that keeps skills small, and it is the only mechanism that does. A skill only ever grows without it.

## Checklist

- [ ] It should be a skill at all
- [ ] Baseline failures recorded verbatim before any prose was written
- [ ] Target repository located by finding `AGENTS.md`, not by the install path
- [ ] Directory name matches `name`
- [ ] Frontmatter carries `name` and `description`, nothing else
- [ ] Description is specific about triggers and reveals no internal process
- [ ] No host agent named, no harness-specific tool named, no absolute paths
- [ ] Main flow in `SKILL.md`; only conditional detail in references
- [ ] Every reference has an explicit trigger and sits one level deep
- [ ] Fetched content treated as data; any write names its verifying read
- [ ] Every shareable trait is a config value
- [ ] Body reads with no history, no dates, no cadence
- [ ] Every remaining rule traces to an observed failure
- [ ] `make validate` exits 0
