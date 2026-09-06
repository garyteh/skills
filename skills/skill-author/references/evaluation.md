# Evaluation reference

Read this when writing `evals.yaml`, or before adding rules to a skill.

## Contents

- The loop
- Case format
- Behaviour and trigger cases
- Which model to run against

## The loop

Evals come before prose. A skill written against observed failures stays small, because there is nothing to write for a gap that does not exist.

1. **Baseline.** Run the task with no skill loaded. Write the failures down verbatim, in the agent's own words. "It was vague" is not a finding; the specific wording is what tells you which rule to write.
2. **Write the cases.** Expected behaviour first, before running anything, so results get recorded rather than judged live against a moving bar.
3. **Write the minimum.** Just enough `SKILL.md` to close the observed gaps. Nothing anticipatory.
4. **Re-run and cut.** Anything still failing earns a new rule. Anything that passes without a rule covering it gets deleted from the skill.

Step 4 is what keeps skills small, and it is the only mechanism that does.

## Case format

`skills/<name>/evals.yaml`. Cases are authored, not generated at run time, so bundling them does not breach the rule against writing to bundled files.

```yaml
cases:
  - query: "the words a real person would type"
    kind: behaviour
    expect_contains: ["a literal string the output must have"]
    expect_absent: ["a literal string it must not"]
    expect: ["a prose assertion needing judgement"]

  - query: "a request that belongs to a different skill"
    kind: trigger
    expect_fires: false
```

At least 3 cases. No upper bound: a skill with more branches earns more cases.

Prefer `expect_contains` and `expect_absent`. They are deterministic and free to check. Reserve `expect` for assertions that genuinely need judgement, because every prose assertion costs a judge call and inherits the judge's own error rate.

## Behaviour and trigger cases

Keep them separate; they test different failures.

**Behaviour** cases check the skill does the right thing once it has fired. Give the query a real person would type and assert on what comes back.

**Trigger** cases check it fires at the right times. The valuable negatives are near-misses that share vocabulary with the skill but belong elsewhere. Obviously unrelated prompts test nothing.

Trigger cases are also how a collision between two skills gets found, rather than guessed at and papered over with a defensive exclusion.

Trigger cases are only meaningful against a real installed set, because routing depends on every sibling description the host can see. Install first, then run them.

## Which model to run against

Run against the weakest model the skill targets, not only the strongest. Writing for a small model and testing only on a large one hides exactly the under-specification that rule exists to catch.

Run against more than one host where the skill claims portability. A skill that works under one agent and not another has failed its central promise, and nothing but running it both ways will show that.
