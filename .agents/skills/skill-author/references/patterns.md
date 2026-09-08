# Structural patterns

Read this when the skill has a multi-step, batch, or destructive workflow. Copy the shape that fits; do not use all four.

## Gotchas

The highest-value section in a production skill. List the environment truths that violate a reasonable default assumption. Each one prevents a correction the user would otherwise have to issue by hand, every time.

```markdown
## Gotchas

**Soft deletes.** The `users` table never hard-deletes. Every query needs
`WHERE deleted_at IS NULL` or deactivated accounts come back in the results.

**The identifier changes name across services.** It is `user_id` in the
database, `uid` in the auth service, and `accountId` in billing.

**Health is not readiness.** `/health` returns 200 whenever the web server is
up. Use `/ready` to confirm database connectivity.
```

Write one only where you have real ones. An invented gotcha is worse than none.

## Workflow checklist

Use when the task has dependent steps an agent could skip or reorder over a long horizon.

```markdown
## Checklist

- [ ] Analyse the form structure: `scripts/analyse_form.sh input.pdf`
- [ ] Map the fields: edit `fields.json`
- [ ] Validate the mapping: `scripts/validate_fields.sh`
- [ ] Fill the form: `scripts/fill_form.sh`
- [ ] Verify the output: `scripts/verify_output.sh`
```

Each item names the concrete action or command. A checklist of vague intentions buys nothing.

## Validation loop

Use when the work has a machine-checkable definition of done. It converts "try to get this right" into "iterate until the checker passes".

```markdown
## Editing workflow

1. Apply your changes.
2. Run `scripts/validate.sh output/`.
3. If it fails:
   - Read the error output.
   - Correct the files it named.
   - Run it again.
4. Do not deliver until the exit status is 0.
```

The loop only works if the validator gives specific, actionable errors. A checker that prints "invalid" teaches the agent nothing to act on.

## Plan, validate, execute

Use for batch operations and anything destructive. The agent writes its intent to a structured file, a checker verifies that file, and only then does execution run. Mistakes surface before anything is written.

```markdown
## Batch workflow

1. Extract the current state:
   `scripts/analyse.sh input.pdf > form_fields.json`
2. Draft your intended changes in `field_values.json`.
3. Validate the draft against reality:
   `scripts/validate_fields.sh form_fields.json field_values.json`
4. If it reports an error, for example `Field 'signature_date' not found`,
   correct `field_values.json` and validate again.
5. Only once validation passes, execute:
   `scripts/fill.sh input.pdf field_values.json output.pdf`

Do not skip step 3. Step 5 overwrites the target.
```

## Writing errors worth reading

Scripts bundled with a skill talk to an agent, not a human. Make failures actionable.

- Name the parameter that was wrong and show a valid example.
- Never fail silently, and never return an empty result where an error occurred.
- Never dump a raw stack trace as the whole message.
- When truncating output, say so and say what to do about it:

```text
[Output truncated at 25,000 tokens. Showing the first 100 of 4,312 log lines.
 Narrow the time range, add a severity filter, or page with --offset.]
```

## Keeping output cheap

Agents read every byte you return.

- Resolve opaque identifiers into names. `owner: "Sarah Chen"` beats `owner_id: "c82ef910"`.
- Drop fields nothing downstream consumes: MIME types, internal indices, system headers.
- Where an agent sometimes needs identifiers and sometimes needs prose, offer both modes and default to the concise one.
